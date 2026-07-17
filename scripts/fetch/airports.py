#!/usr/bin/env python3
"""フェーズ1調査: OurAirports データで全地点の最寄り空港を計算する。
- 入力: data/raw/airports/ourairports.csv（https://davidmegginson.github.io/ourairports-data/airports.csv）
- 対象: 定期便のある large_airport / medium_airport
- 出力: data/raw/airports/nearest.json と距離分布のサマリ表示
"""
import csv
import json
import math
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data/raw/airports/ourairports.csv"
OUT = ROOT / "data/raw/airports/nearest.json"
CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"  # パブリックドメイン・毎晩更新


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def main():
    if not CSV.exists():
        print(f"downloading {CSV_URL} ...")
        CSV.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(CSV_URL, headers={"User-Agent": "city-data-builder/0.1 (survey)"})
        CSV.write_bytes(urllib.request.urlopen(req, timeout=120).read())

    airports = []
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row["type"] in ("large_airport", "medium_airport")
                    and row["scheduled_service"] == "yes"
                    and row["continent"] == "EU"):
                airports.append({
                    "ident": row["ident"], "iata": row["iata_code"],
                    "name": row["name"], "type": row["type"],
                    "country": row["iso_country"],
                    "lat": float(row["latitude_deg"]), "lon": float(row["longitude_deg"]),
                })
    print(f"欧州の定期便あり空港: {len(airports)}件 "
          f"(large={sum(1 for a in airports if a['type'] == 'large_airport')}, "
          f"medium={sum(1 for a in airports if a['type'] == 'medium_airport')})")

    master = json.loads((ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))
    results = {}
    for p in master["places"]:
        if not p.get("lat"):
            continue
        best = min(airports, key=lambda a: haversine_km(p["lat"], p["lon"], a["lat"], a["lon"]))
        best_large = min((a for a in airports if a["type"] == "large_airport"),
                         key=lambda a: haversine_km(p["lat"], p["lon"], a["lat"], a["lon"]))
        results[p["id"]] = {
            "name_ja": p["name_ja"],
            "nearest": {**{k: best[k] for k in ("iata", "name", "type", "country")},
                        "distance_km": round(haversine_km(p["lat"], p["lon"], best["lat"], best["lon"]), 1)},
            "nearest_large": {**{k: best_large[k] for k in ("iata", "name", "country")},
                              "distance_km": round(haversine_km(p["lat"], p["lon"], best_large["lat"], best_large["lon"]), 1)},
        }

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    dists = sorted(r["nearest"]["distance_km"] for r in results.values())
    n = len(dists)
    print(f"対象: {n}地点 / 最寄り空港距離 中央値 {dists[n // 2]}km, 最大 {dists[-1]}km")
    far = [(r["name_ja"], r["nearest"]["distance_km"], r["nearest"]["iata"]) for r in results.values()
           if r["nearest"]["distance_km"] > 100]
    print(f"最寄り空港まで100km超: {len(far)}件")
    for name, d, iata in sorted(far, key=lambda x: -x[1])[:10]:
        print(f"  {name}: {d}km ({iata})")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
