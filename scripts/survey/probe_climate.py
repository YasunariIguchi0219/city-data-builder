#!/usr/bin/env python3
"""フェーズ1調査: 気候データ（ERA5系）の取得テスト（再現用）。
note.md要求の4指標（気温・降水量・日照時間・湿度）が月別に集計できることを確認する。

⚠️ このテストは Open-Meteo アーカイブAPI（ERA5ベース）を使うが、
   Open-Meteo の無料枠は【非商用限定】。本番のデータ作成では
   Copernicus CDS から ERA5 を直接取得する（無料・商用可・要帰属表示）。
   詳細: docs/phase1/license-research.md §6
"""
import json
import urllib.parse
import urllib.request

UA = {"User-Agent": "city-data-builder/0.1 (survey)"}


def monthly_climate(name: str, lat: float, lon: float, year=2024):
    params = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon,
        "start_date": f"{year}-01-01", "end_date": f"{year}-12-31",
        "daily": "temperature_2m_mean,precipitation_sum,sunshine_duration,relative_humidity_2m_mean",
        "timezone": "UTC"})
    url = "https://archive-api.open-meteo.com/v1/archive?" + params
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        d = json.load(r)["daily"]
    for month in ("01", "07"):
        idx = [i for i, t in enumerate(d["time"]) if t[5:7] == month]
        temp = sum(d["temperature_2m_mean"][i] for i in idx) / len(idx)
        prec = sum(d["precipitation_sum"][i] for i in idx)
        sun = sum(d["sunshine_duration"][i] for i in idx) / 3600
        hum = sum(d["relative_humidity_2m_mean"][i] for i in idx) / len(idx)
        print(f"{name} {int(month)}月: 平均気温 {temp:.1f}C, 降水 {prec:.0f}mm, "
              f"日照 {sun:.0f}h, 湿度 {hum:.0f}%")


if __name__ == "__main__":
    monthly_climate("パリ", 48.85661, 2.35222)
    monthly_climate("ツェルマット", 46.01958, 7.74611)
