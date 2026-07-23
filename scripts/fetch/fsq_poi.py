#!/usr/bin/env python3
"""データ拡張: Foursquare OS Places（ローカルparquet・Apache 2.0）から全地点のPOI数を集計する。
- 入力: data/raw/fsq-os-places/release/dt=*/places/parquet/*.parquet（gitignore対象・約11GB）
- 方式: DuckDBで1パス。国の一致＋境界ボックスで結合し、大圏距離で5km/1km円に絞る。閉店（date_closed）除外
- カテゴリ対応（FSQ分類ラベルの前方/部分一致。設計根拠は docs/phase1/data-source-survey.md §2.6）:
    dining   = 'Dining and Drinking' 全体（レストラン・カフェ・バー等）
    culture  = Museum / Art Gallery / Performing Arts
    nightlife= Bar / Night Club / Nightlife Spot
    shopping = Retail 全体 + Marketplace
    wellness = Spa / Sauna / Hot Spring / Bathhouse（'Space'への誤一致を避けるため末尾一致）
    lodging  = Travel and Transportation > Lodging 配下
    dining_categories = Dining and Drinking 配下のユニーク分類数（食の多様性）
- 出力: data/raw/fsq/poi_counts.json（place_id → 各件数）
"""
import glob
import json
import math
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/fsq/poi_counts.json"
RELEASES = sorted(glob.glob(str(ROOT / "data/raw/fsq-os-places/release/dt=*")))

CATS = {
    "dining": "l LIKE 'Dining and Drinking%'",
    "culture": "(l LIKE '%> Museum%' OR l LIKE '%Art Gallery%' OR l LIKE '%Performing Arts%')",
    "nightlife": "(l LIKE 'Dining and Drinking > Bar%' OR l LIKE '%Night Club%' OR l LIKE 'Nightlife Spot%')",
    "shopping": "(l LIKE 'Retail%' OR l LIKE '%Marketplace%')",
    "wellness": "(l LIKE '%> Spa' OR l LIKE '%> Sauna' OR l LIKE '%Hot Spring%' OR l LIKE '%Bathhouse%')",
    "lodging": "l LIKE 'Travel and Transportation > Lodging%'",
}
FIELDS_5KM = ["dining", "culture", "nightlife", "shopping", "wellness", "lodging"]
FIELDS_1KM = ["dining", "culture", "shopping"]


def has(key: str) -> str:
    """行のカテゴリ配列に該当ラベルが1つでもあるかの条件式。"""
    return f"len(list_filter(labels, l -> {CATS[key]})) > 0"


def main():
    assert RELEASES, "Foursquareデータが data/raw/fsq-os-places/release/ にありません"
    base = RELEASES[-1]  # 最新リリースを使用
    print(f"使用リリース: {Path(base).name}")

    places = [p for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("lat")]
    con = duckdb.connect()
    con.execute("""CREATE TEMP TABLE centers (
        id VARCHAR, country VARCHAR, clat DOUBLE, clon DOUBLE,
        lat_min DOUBLE, lat_max DOUBLE, lon_min DOUBLE, lon_max DOUBLE)""")
    con.executemany("INSERT INTO centers VALUES (?,?,?,?,?,?,?,?)", [
        (p["id"], p["country"], p["lat"], p["lon"],
         p["lat"] - 5 / 111.0, p["lat"] + 5 / 111.0,
         p["lon"] - 5 / (111.0 * math.cos(math.radians(p["lat"]))),
         p["lon"] + 5 / (111.0 * math.cos(math.radians(p["lat"]))))
        for p in places])

    # 1パス目: 各地点の5km境界ボックス内の行を距離つきで抽出（列参照同士の演算なので負数リテラルの罠はない）
    print("parquetを走査中（数分かかります）…", flush=True)
    con.execute(f"""CREATE TEMP TABLE hits AS
      SELECT c.id,
        2*6371*asin(sqrt(pow(sin(radians(p.latitude - c.clat)/2), 2)
          + cos(radians(c.clat)) * cos(radians(p.latitude))
          * pow(sin(radians(p.longitude - c.clon)/2), 2))) AS d,
        p.fsq_category_labels AS labels
      FROM read_parquet('{base}/places/parquet/*.parquet') p
      JOIN centers c
        ON p.country = c.country
       AND p.latitude  BETWEEN c.lat_min AND c.lat_max
       AND p.longitude BETWEEN c.lon_min AND c.lon_max
      WHERE p.date_closed IS NULL""")
    print("抽出行数:", con.execute("SELECT count(*) FROM hits").fetchone()[0])

    # 2パス目: 件数集計
    agg_5 = ", ".join(f"count(*) FILTER (WHERE d<=5 AND {has(k)}) AS {k}_5km" for k in FIELDS_5KM)
    agg_1 = ", ".join(f"count(*) FILTER (WHERE d<=1 AND {has(k)}) AS {k}_1km" for k in FIELDS_1KM)
    rows = con.execute(f"SELECT id, {agg_5}, {agg_1} FROM hits GROUP BY id").fetchall()
    cols = [c[0] for c in con.description]

    # 食の多様性: 5km円内の Dining and Drinking 配下ユニーク分類数
    cats = dict(con.execute("""
      SELECT id, count(DISTINCT l) FROM
        (SELECT id, unnest(labels) AS l FROM hits WHERE d <= 5)
      WHERE l LIKE 'Dining and Drinking%' GROUP BY id""").fetchall())

    result = {}
    for row in rows:
        rec = dict(zip(cols, row))
        pid = rec.pop("id")
        rec["dining_categories_5km"] = cats.get(pid, 0)
        result[pid] = rec
    for p in places:  # 円内に1件もない地点もゼロ埋めで出力
        result.setdefault(p["id"], {f"{k}_5km": 0 for k in FIELDS_5KM}
                          | {f"{k}_1km": 0 for k in FIELDS_1KM} | {"dining_categories_5km": 0})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"release": Path(base).name, "retrieved_at": "2026-07-23",
                               "places": result}, ensure_ascii=False, indent=1), encoding="utf-8")
    md = sorted(result.items(), key=lambda x: -x[1]["dining_5km"])
    print(f"wrote {OUT} ({len(result)}地点)")
    print("dining_5km 上位:", [(k, v['dining_5km']) for k, v in md[:3]],
          "下位:", [(k, v['dining_5km']) for k, v in md[-3:]])


if __name__ == "__main__":
    main()
