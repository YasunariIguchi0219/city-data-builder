#!/usr/bin/env python3
"""フェーズ1調査: 世界遺産データをWikidata(CC0)から取得し、154地点との近傍マッチングを実測する。
UNESCO公式(whc.unesco.org)は商用有償＋機械取得不可のため不採用 → Wikidata経由を代替採用
（経緯: docs/phase1/data-source-survey.md §2.5）。
出力: data/raw/survey/unesco_whs_wikidata.json（欧州域内の世界遺産・構成資産、座標付き）
"""
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/survey/unesco_whs_wikidata.json"

SPARQL = """
SELECT ?site ?siteLabel ?lat ?lon ?countryLabel WHERE {
  ?site wdt:P1435 wd:Q9259 .
  ?site p:P625/psv:P625 ?c .
  ?c wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon .
  FILTER(?lat > 35 && ?lat < 72 && ?lon > -11 && ?lon < 30)
  OPTIONAL { ?site wdt:P17 ?country }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
"""


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(a))


def main():
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
        {"query": SPARQL, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "city-data-builder/0.1 (survey)"})
    rows = json.load(urllib.request.urlopen(req, timeout=120))["results"]["bindings"]
    sites = [{"qid": r["site"]["value"].rsplit("/", 1)[-1],
              "label": r["siteLabel"]["value"],
              "lat": float(r["lat"]["value"]), "lon": float(r["lon"]["value"]),
              "country": r.get("countryLabel", {}).get("value")} for r in rows]
    OUT.write_text(json.dumps(sites, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"欧州域内の世界遺産（構成資産含む・座標付き）: {len(sites)}件 -> {OUT}")

    places = json.loads((ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
    targets = [p for p in places if p.get("lat")]
    for radius in (5, 15, 30):
        hit = sum(1 for p in targets
                  if any(haversine_km(p["lat"], p["lon"], s["lat"], s["lon"]) <= radius for s in sites))
        print(f"半径{radius}km以内に世界遺産あり: {hit}/{len(targets)} ({hit / len(targets):.0%})")


if __name__ == "__main__":
    main()
