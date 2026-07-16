#!/usr/bin/env python3
"""フェーズ2: 設計レビュー用サンプル3件（パリ・オビドス・シヨン城）を実データで生成する。
- 出力: data/output/samples/<id>.json（schema/place.schema.json で検証済み）
- 未取得ブロック（poi / osm_features / safety）はフェーズ3で取得するため null＋notesに明記
- 気候はOpen-Meteoアーカイブ(2024年単年・調査目的)。本番はERA5直接取得・平年値に置換予定
"""
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

import jsonschema

from build_master import ROOT, api_get

SAMPLES = ["paris", "obidos", "chillon-castle"]
TODAY = "2026-07-16"
OUT_DIR = ROOT / "data/output/samples"
SCHEMA = json.loads((ROOT / "schema/place.schema.json").read_text(encoding="utf-8"))
UA = {"User-Agent": "city-data-builder/0.1 (phase2 samples)"}

COMFORT = dict(t_lo=8, t_hi=27, w_temp=0.5, w_precip=0.3, w_sun=0.2)  # 設計書§4.2（仮置き係数）


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(a))


def meta(source, license_, attribution=None, retrieved=TODAY):
    return {"source": source, "license": license_, "attribution": attribution, "retrieved_at": retrieved}


def fetch_elevations(qids):
    ents = api_get({"action": "wbgetentities", "ids": "|".join(qids), "props": "claims"})["entities"]
    out = {}
    for qid, ent in ents.items():
        elev = None
        for c in ent.get("claims", {}).get("P2044", []):
            if c["mainsnak"].get("snaktype") == "value":
                elev = float(c["mainsnak"]["datavalue"]["value"]["amount"])
                break
        out[qid] = elev
    return out


def fetch_monthly_climate(lat, lon, year=2024):
    params = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon,
        "start_date": f"{year}-01-01", "end_date": f"{year}-12-31",
        "daily": "temperature_2m_mean,precipitation_sum,sunshine_duration,relative_humidity_2m_mean",
        "timezone": "UTC"})
    url = "https://archive-api.open-meteo.com/v1/archive?" + params
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))["daily"]
    monthly = []
    for m in range(1, 13):
        idx = [i for i, t in enumerate(d["time"]) if int(t[5:7]) == m]
        monthly.append({
            "month": m,
            "temp_mean_c": round(sum(d["temperature_2m_mean"][i] for i in idx) / len(idx), 1),
            "precip_mm": round(sum(d["precipitation_sum"][i] for i in idx), 1),
            "sunshine_h": round(sum(d["sunshine_duration"][i] for i in idx) / 3600, 1),
            "humidity_pct": round(sum(d["relative_humidity_2m_mean"][i] for i in idx) / len(idx), 1),
        })
    return monthly


def fetch_pageviews(project, title, start="2025010100", end="2025123100"):
    t = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"{project}/all-access/user/{t}/monthly/{start}/{end}")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return sum(i["views"] for i in json.load(r)["items"])
    except Exception:  # noqa: BLE001
        return None


def seasonal_comfort(monthly):
    """月別快適度0-100。気温は快適帯(8-27℃)の台形、降水は少ないほど高、日照は多いほど高。"""
    scores = []
    for m in monthly:
        t = m["temp_mean_c"]
        if t is None:
            scores.append(None)
            continue
        lo, hi = COMFORT["t_lo"], COMFORT["t_hi"]
        t_score = max(0.0, min(1.0, 1 - max(lo - t, t - hi, 0) / 10))
        p_score = max(0.0, 1 - (m["precip_mm"] or 0) / 150)
        s_score = min(1.0, (m["sunshine_h"] or 0) / 250)
        scores.append(round(100 * (COMFORT["w_temp"] * t_score
                                   + COMFORT["w_precip"] * p_score
                                   + COMFORT["w_sun"] * s_score)))
    return scores


def main():
    places = {p["id"]: p for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]}
    airports = json.loads((ROOT / "data/raw/survey/nearest_airports.json").read_text(encoding="utf-8"))
    whs = json.loads((ROOT / "data/raw/survey/unesco_whs_wikidata.json").read_text(encoding="utf-8"))
    sitelinks = json.loads((ROOT / "data/raw/survey/wikipedia_sitelinks.json").read_text(encoding="utf-8"))

    elevations = fetch_elevations([places[s]["qid"] for s in SAMPLES])
    cities = [p for p in places.values() if p["type"] == "city" and p.get("lat")]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    validator = jsonschema.Draft202012Validator(SCHEMA)

    for sid in SAMPLES:
        p = places[sid]
        sl = sitelinks.get(p["qid"], {})

        near = sorted(((s, haversine_km(p["lat"], p["lon"], s["lat"], s["lon"])) for s in whs),
                      key=lambda x: x[1])
        onsite = [{"qid": s["qid"], "label": s["label"], "distance_km": round(d, 1)}
                  for s, d in near if d <= 5]
        seen = {o["qid"] for o in onsite}
        onsite = [o for o in onsite if not (o["qid"] in seen and seen.discard(o["qid"]))]  # qid重複除去

        hubs = sorted(((c, haversine_km(p["lat"], p["lon"], c["lat"], c["lon"]))
                       for c in cities if c["id"] != sid), key=lambda x: x[1])
        monthly = fetch_monthly_climate(p["lat"], p["lon"])
        ap = airports[sid]

        views_ja = fetch_pageviews("ja.wikipedia", sl["jawiki"]) if sl.get("jawiki") else None
        views_en = fetch_pageviews("en.wikipedia", sl["enwiki"]) if sl.get("enwiki") else None

        record = {
            "identity": {
                "id": sid, "name_ja": p["name_ja"], "name_en": p["name_en"],
                "qid": p["qid"], "country": p["country"], "country_ja": p.get("country_ja"),
                "type": p["type"], "lat": p["lat"], "lon": p["lon"],
                "base_place_id": None, "endpoints": None, "note": p.get("note"),
            },
            "geography": {
                "population": p.get("population"), "population_date": p.get("population_date"),
                "elevation_m": elevations.get(p["qid"]), "coastal": None,
                "_meta": meta("wikidata", "CC0-1.0"),
            },
            "poi": None,
            "osm_features": None,
            "heritage": {
                "whs_onsite": onsite,
                "whs_within_30km": len({s["qid"] for s, d in near if d <= 30}),
                "_meta": meta("wikidata", "CC0-1.0"),
            },
            "climate": {
                "monthly": monthly, "reference_period": "2024",
                "_meta": meta("era5", "Copernicus-Products-Licence",
                              "Generated using Copernicus Climate Change Service information 2026"),
            },
            "access": {
                "nearest_airport": {**ap["nearest"]},
                "nearest_large_airport": {**ap["nearest_large"], "type": "large_airport"},
                "nearest_hub_place_id": hubs[0][0]["id"],
                "nearest_hub_distance_km": round(hubs[0][1], 1),
                "_meta": meta("ourairports", "Public-Domain"),
            },
            "recognition": {
                "wikipedia_views_ja_year": views_ja,
                "wikipedia_views_en_year": views_en,
                "wikipedia_sitelinks": sl.get("n_sitelinks"),
                "views_year": "2025",
                "nights_spent_nuts2": None,
                "_meta": meta("wikimedia_pageviews", "CC0-1.0"),
            },
            "safety": None,
            "indicators": {
                "seasonal_comfort": {
                    "value": seasonal_comfort(monthly),
                    "cohort": None,
                    "depends_on": ["era5"],
                    "formula": "月別: 0.5*快適帯(8-27C台形) + 0.3*(1-降水/150mm) + 0.2*min(日照/250h,1)",
                },
            },
            "meta": {
                "schema_version": "0.2.0-draft",
                "generated_at": TODAY,
                "notes": "フェーズ2設計レビュー用サンプル。poi/osm_features/safetyはフェーズ3で取得（null）。"
                         "気候は2024年単年の暫定値（本番はERA5平年値に置換）。"
                         "コホート正規化が必要な指標（food_scene等）は全件データ作成後に算出。",
            },
        }

        errors = list(validator.iter_errors(record))
        if errors:
            for e in errors[:5]:
                print(f"  SCHEMA ERROR [{sid}] {'/'.join(map(str, e.path))}: {e.message}")
            raise SystemExit(1)

        out = OUT_DIR / f"{sid}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        best = max(range(12), key=lambda i: record["indicators"]["seasonal_comfort"]["value"][i])
        print(f"{p['name_ja']}: schema OK, 世界遺産5km圏 {len(onsite)}件/30km圏 "
              f"{record['heritage']['whs_within_30km']}件, 認知度 ja={views_ja} en={views_en}, "
              f"ベストシーズン {best + 1}月 -> {out.name}")


if __name__ == "__main__":
    main()
