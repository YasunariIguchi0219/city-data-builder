#!/usr/bin/env python3
"""フェーズ1調査: OpenStreetMap Overpass API のPOI数取得テスト（再現用）。
座標×半径でカテゴリ別POI件数が取れることを確認する。

調査結果メモ: 方式は機能する（パリ半径5km 飲食店15,676件を取得成功）が、
公開Overpassサーバーは過負荷が常態（504多発）。152地点×多カテゴリの
本番取得は Geofabrik 地域抽出ファイル(PBF)のローカル処理を推奨。
ライセンスはODbL — 取り扱いは docs/phase1/data-source-survey.md §2.7 参照。
"""
import json
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "city-data-builder/0.1 (survey)"}
ENDPOINTS = ["https://overpass-api.de/api/interpreter",
             "https://overpass.kumi.systems/api/interpreter"]

CATEGORIES = {
    "飲食店": 'nwr["amenity"~"^(restaurant|cafe|bar|fast_food)$"](around:{r},{lat},{lon})',
    "美術館・博物館": 'nwr["tourism"~"^(museum|gallery)$"](around:{r},{lat},{lon})',
    "展望地点": 'nwr["tourism"="viewpoint"](around:{r},{lat},{lon})',
}


def count(lat: float, lon: float, radius: int, stmt: str):
    q = f'[out:json][timeout:120];({stmt.format(lat=lat, lon=lon, r=radius)};);out count;'
    data = urllib.parse.urlencode({"data": q}).encode()
    for ep in ENDPOINTS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(ep, data=data, headers=UA)
                d = json.load(urllib.request.urlopen(req, timeout=130))
                return int(d["elements"][0]["tags"]["total"])
            except Exception as e:  # noqa: BLE001
                print(f"  ({ep.split('/')[2]} attempt{attempt + 1}: {e})", flush=True)
                time.sleep(5)
    return None


if __name__ == "__main__":
    for name, lat, lon in [("パリ", 48.85661, 2.35222), ("バイブリー", 51.76168, -1.83552)]:
        for cat, stmt in CATEGORIES.items():
            print(f"{name} 半径5km {cat}: {count(lat, lon, 5000, stmt)}", flush=True)
            time.sleep(3)
