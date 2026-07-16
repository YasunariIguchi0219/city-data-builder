#!/usr/bin/env python3
"""フェーズ3: OSM Overpass APIで全地点のPOI・自然地物の件数を取得する（低速・再開可能）。

- 方式: 1地点=1リクエストに全カテゴリのcount文をまとめ、地点間に間隔を空けて逐次照会。
  国別ファイル(Geofabrik, 20GB超)のダウンロードを避けるための選択（共有ストレージ事情）。
- ライセンス: ODbL。このデータは poi._meta.source="osm" / osm_features として分離管理する
  （docs/phase1/data-source-survey.md §2.7 の決定に従う）。
- 出力: data/raw/osm/poi_counts.json（地点id → カテゴリ→件数。取得済みはスキップ）
- 帰属: © OpenStreetMap contributors
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/osm/poi_counts.json"
UA = {"User-Agent": "city-data-builder/0.1 (fetch; sequential, ~6 req/min)"}
ENDPOINTS = ["https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter"]
SLEEP_BETWEEN_PLACES = 10  # 秒。公開サーバーへの負荷配慮

# (キー, Overpass文テンプレート)。1リクエストに全て入れ、out count の出現順で対応付ける
QUERIES = [
    # poiブロック相当
    ("dining_5km",    'nwr["amenity"~"^(restaurant|cafe|bar|fast_food|pub)$"](around:5000,{lat},{lon})'),
    ("culture_5km",   'nwr["tourism"~"^(museum|gallery)$"](around:5000,{lat},{lon});'
                      'nwr["amenity"~"^(theatre|arts_centre)$"](around:5000,{lat},{lon})'),
    ("nightlife_5km", 'nwr["amenity"~"^(bar|pub|nightclub)$"](around:5000,{lat},{lon})'),
    ("shopping_5km",  'nwr["shop"](around:5000,{lat},{lon});'
                      'nwr["amenity"="marketplace"](around:5000,{lat},{lon})'),
    ("wellness_5km",  'nwr["leisure"~"^(spa|sauna)$"](around:5000,{lat},{lon});'
                      'nwr["amenity"="public_bath"](around:5000,{lat},{lon})'),
    ("lodging_5km",   'nwr["tourism"~"^(hotel|guest_house|hostel|apartment|motel)$"](around:5000,{lat},{lon})'),
    ("dining_1km",    'nwr["amenity"~"^(restaurant|cafe|bar|fast_food|pub)$"](around:1000,{lat},{lon})'),
    ("culture_1km",   'nwr["tourism"~"^(museum|gallery)$"](around:1000,{lat},{lon});'
                      'nwr["amenity"~"^(theatre|arts_centre)$"](around:1000,{lat},{lon})'),
    ("shopping_1km",  'nwr["shop"](around:1000,{lat},{lon})'),
    # osm_featuresブロック相当
    ("viewpoints_5km",       'nwr["tourism"="viewpoint"](around:5000,{lat},{lon})'),
    ("peaks_10km",           'nwr["natural"="peak"](around:10000,{lat},{lon})'),
    ("lakes_10km",           'nwr["natural"="water"]["water"~"^(lake|lagoon|reservoir)$"](around:10000,{lat},{lon})'),
    ("coastline_10km",       'way["natural"="coastline"](around:10000,{lat},{lon})'),
    ("protected_areas_10km", 'nwr["boundary"="protected_area"](around:10000,{lat},{lon});'
                             'nwr["leisure"="nature_reserve"](around:10000,{lat},{lon})'),
    ("hiking_routes_10km",   'relation["route"="hiking"](around:10000,{lat},{lon})'),
    ("ski_marina_10km",      'nwr["piste:type"](around:10000,{lat},{lon});'
                             'nwr["leisure"="marina"](around:10000,{lat},{lon})'),
    ("parks_gardens_5km",    'nwr["leisure"~"^(park|garden)$"](around:5000,{lat},{lon})'),
    ("pedestrian_area_1km",  'way["highway"="pedestrian"](around:1000,{lat},{lon})'),
]


def build_query(lat: float, lon: float) -> str:
    parts = ["[out:json][timeout:180];"]
    for _, stmt in QUERIES:
        parts.append(f"({stmt.format(lat=lat, lon=lon)};); out count;")
    return "\n".join(parts)


def run_query(lat: float, lon: float):
    data = urllib.parse.urlencode({"data": build_query(lat, lon)}).encode()
    for ep in ENDPOINTS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(ep, data=data, headers=UA)
                d = json.load(urllib.request.urlopen(req, timeout=200))
                counts = [int(e["tags"]["total"]) for e in d["elements"]
                          if e.get("type") == "count"]
                if len(counts) != len(QUERIES):
                    raise ValueError(f"count数不一致: {len(counts)} != {len(QUERIES)}")
                return dict(zip((k for k, _ in QUERIES), counts))
            except Exception as e:  # noqa: BLE001
                print(f"    ({ep.split('/')[2]} attempt{attempt + 1}: {e})", flush=True)
                time.sleep(20)
    return None


def main():
    places = json.loads((ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
    targets = [p for p in places if p.get("lat")]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    todo = [p for p in targets if p["id"] not in results]
    print(f"対象 {len(targets)}地点（取得済み {len(results)}、残り {len(todo)}）")
    for i, p in enumerate(todo, 1):
        counts = run_query(p["lat"], p["lon"])
        if counts is None:
            print(f"[{i}/{len(todo)}] {p['name_ja']}: 失敗（次回再実行で再試行）", flush=True)
        else:
            results[p["id"]] = counts
            OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[{i}/{len(todo)}] {p['name_ja']}: 飲食{counts['dining_5km']} "
                  f"文化{counts['culture_5km']} 展望{counts['viewpoints_5km']}", flush=True)
        time.sleep(SLEEP_BETWEEN_PLACES)

    print(f"\n完了: {len(results)}/{len(targets)} -> {OUT}")


if __name__ == "__main__":
    main()
