#!/usr/bin/env python3
"""フェーズ3: Copernicus CDS から ERA5 月平均データを取得し、全地点の月別気候値を作る。

- 認証: プロジェクト直下の .env（CDSAPI_URL / CDSAPI_KEY）。scripts/envfile.py が読み込む
- ライセンス: Licence to Use Copernicus Products（商用可・帰属表示必須）
  帰属: "Generated using Copernicus Climate Change Service information 2026"
- 方式: 欧州範囲のグリッド（0.25度）を1リクエストで取得（約50MB・抽出後は削除可）し、
  各地点の最寄りグリッドセルから月別平年値（2015-2024平均）を作る
- 使い方:
    uv run python scripts/fetch/climate_era5.py test     # トークン確認（小さなリクエスト）
    uv run python scripts/fetch/climate_era5.py fetch    # 本取得（CDSのキュー待ちあり）
    uv run python scripts/fetch/climate_era5.py extract  # netCDF→ climate_monthly.json
- 出力: data/raw/era5/era5_monthly_europe.nc, climate_monthly.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import envfile

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/era5"
NC = RAW / "era5_monthly_europe.nc"
OUT = RAW / "climate_monthly.json"

YEARS = [str(y) for y in range(2015, 2025)]
AREA = [72, -11, 35, 30]  # N, W, S, E（欧州）
VARIABLES = [
    "2m_temperature",            # 気温
    "total_precipitation",       # 降水量（m/日 平均）
    "2m_dewpoint_temperature",   # 露点（相対湿度の計算用）
    "surface_solar_radiation_downwards",  # 日射（日照時間の代理指標）
]
DATASET = "reanalysis-era5-single-levels-monthly-means"


def client():
    envfile.require("CDSAPI_URL", "CDSAPI_KEY")
    import cdsapi
    return cdsapi.Client()


def cmd_test():
    RAW.mkdir(parents=True, exist_ok=True)
    client().retrieve(DATASET, {
        "product_type": "monthly_averaged_reanalysis",
        "variable": ["2m_temperature"],
        "year": ["2024"], "month": ["07"], "time": "00:00",
        "area": [49, 2, 48, 3], "format": "netcdf",
    }, str(RAW / "_test.nc"))
    print("CDS接続テスト成功（トークン有効）:", RAW / "_test.nc")


def cmd_fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    client().retrieve(DATASET, {
        "product_type": "monthly_averaged_reanalysis",
        "variable": VARIABLES,
        "year": YEARS, "month": [f"{m:02d}" for m in range(1, 13)],
        "time": "00:00", "area": AREA, "format": "netcdf",
    }, str(NC))
    print("wrote", NC)


def relative_humidity(t_k: float, td_k: float) -> float:
    """気温・露点(K)から相対湿度(%)を計算（Magnus式）。"""
    import math
    t, td = t_k - 273.15, td_k - 273.15
    es = 6.112 * math.exp(17.62 * t / (243.12 + t))
    e = 6.112 * math.exp(17.62 * td / (243.12 + td))
    return 100.0 * e / es


def open_datasets():
    """CDSの応答はnetCDF単体または複数netCDFを含むZIP。両対応で全Datasetを返す。"""
    import zipfile

    import netCDF4

    if zipfile.is_zipfile(NC):
        unzip_dir = RAW / "unzipped"
        unzip_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(NC) as z:
            z.extractall(unzip_dir)
        paths = sorted(unzip_dir.glob("*.nc"))
    else:
        paths = [NC]
    return [netCDF4.Dataset(p) for p in paths]


def cmd_extract():
    import calendar

    import numpy as np

    datasets = open_datasets()
    names = {}  # 変数名(小文字) → variableオブジェクト（複数ファイルを横断）
    for ds in datasets:
        for v in ds.variables:
            names.setdefault(v.lower(), ds.variables[v])

    def var(*cands):
        for c in cands:
            if c in names:
                return names[c]
        raise KeyError(f"変数が見つからない: {cands} / 実際: {list(names)}")

    lats = var("latitude", "lat")[:]
    lons = var("longitude", "lon")[:]
    t2m, d2m = var("t2m")[:], var("d2m")[:]
    tp, ssrd = var("tp")[:], var("ssrd")[:]
    # 時間軸: YEARS×12ヶ月。(time, lat, lon) を想定（余剰次元はsqueeze）
    t2m, d2m, tp, ssrd = (np.squeeze(a) for a in (t2m, d2m, tp, ssrd))
    n_time = t2m.shape[0]
    assert n_time == len(YEARS) * 12, f"時間軸が想定外: {n_time}"

    places = json.loads((ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
    result = {}
    for p in places:
        if not p.get("lat"):
            continue
        iy = int(np.abs(lats - p["lat"]).argmin())
        ix = int(np.abs(lons - p["lon"]).argmin())
        monthly = []
        for m in range(12):
            idx = [y * 12 + m for y in range(len(YEARS))]
            days = sum(calendar.monthrange(int(y), m + 1)[1] for y in YEARS) / len(YEARS)
            t_k = float(np.mean([t2m[i, iy, ix] for i in idx]))
            td_k = float(np.mean([d2m[i, iy, ix] for i in idx]))
            tp_m_day = float(np.mean([tp[i, iy, ix] for i in idx]))      # m/日
            ssrd_j_day = float(np.mean([ssrd[i, iy, ix] for i in idx]))  # J/m2/日
            monthly.append({
                "month": m + 1,
                "temp_mean_c": round(t_k - 273.15, 1),
                "precip_mm": round(tp_m_day * 1000 * days, 1),
                # 日照時間の近似: 日射量を晴天時代表フラックス(約500W/m2)で除して時間換算
                "sunshine_h": round(ssrd_j_day / (500 * 3600) * days, 1),
                "humidity_pct": round(relative_humidity(t_k, td_k), 1),
            })
        result[p["id"]] = monthly

    OUT.write_text(json.dumps(
        {"reference_period": f"{YEARS[0]}-{YEARS[-1]}",
         "attribution": "Generated using Copernicus Climate Change Service information 2026",
         "note": "sunshine_hはssrd(日射量)からの近似値",
         "monthly": result}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT} ({len(result)}地点)")


if __name__ == "__main__":
    {"test": cmd_test, "fetch": cmd_fetch, "extract": cmd_extract}[
        sys.argv[1] if len(sys.argv) > 1 else "test"]()
