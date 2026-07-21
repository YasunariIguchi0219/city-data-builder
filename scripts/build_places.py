#!/usr/bin/env python3
"""フェーズ3: 全154件の統一フォーマットデータ data/output/places.json を組み立てる。

入力（フェッチ済みの生データ。欠けているソースはそのブロックがnullになる）:
- data/master/places_master.json            … identity/geography基礎（フェーズ0）
- data/raw/wikidata/extras.json             … 標高（fetch/wikidata_extras.py）
- data/raw/airports/nearest.json     … 空港（fetch/airports.py）
- data/raw/wikidata/whs_europe.json  … 世界遺産（fetch/unesco_whs.py）
- data/raw/pageviews/views_2025.json        … 閲覧数（fetch/pageviews.py）
- data/raw/wikidata/sitelinks.json  … sitelinks数
- data/raw/mofa/risk_levels.json            … 危険情報（fetch/mofa_safety.py）
- data/raw/osm/poi_counts.json              … POI・自然地物（fetch/osm_poi.py、ODbL）
- data/raw/era5/climate_monthly.json        … 月別気候（fetch/climate_era5.py）
- data/raw/nager/holidays.json              … 祝日（fetch/holidays.py、国単位）
- data/raw/eurostat/pli.json                … 物価水準（fetch/price_levels.py、国単位）
- data/raw/wikidata/countries.json          … 公用語（fetch/country_wikidata.py、国単位）
- data/raw/wikidata/jp_missions.json        … 日本の在外公館（fetch/country_wikidata.py）
- 日照時間（daylight）は座標からの天文計算（取得不要）

検証: schema/place.schema.json（JSON Schema 2020-12）に全件適合しなければ失敗する。
指標の定義: docs/phase2/schema-design.md §4
"""
import json
import math
import urllib.parse
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/output/places.json"
TODAY = "2026-07-16"
SCHEMA_VERSION = "0.2.0-draft"

OSM_ATTR = "© OpenStreetMap contributors"
ERA5_ATTR = "Generated using Copernicus Climate Change Service information 2026"
COMFORT = dict(t_lo=8, t_hi=27, w_temp=0.5, w_precip=0.3, w_sun=0.2)  # 設計書§4.2（仮置き係数）


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(a))


def meta(source, license_, attribution=None):
    return {"source": source, "license": license_, "attribution": attribution,
            "retrieved_at": TODAY}


def load(rel, default=None):
    p = ROOT / rel
    if not p.exists():
        print(f"  (入力なし: {rel} → 該当ブロックはnull)")
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def percentile_map(values: dict) -> dict:
    """id→数値 の辞書を、id→パーセンタイル(0-100) に変換（null除外）。"""
    items = [(k, v) for k, v in values.items() if v is not None]
    if not items:
        return {}
    items.sort(key=lambda x: x[1])
    n = len(items)
    return {k: round(100 * i / (n - 1)) if n > 1 else 50 for i, (k, _) in enumerate(items)}


def seasonal_comfort(monthly):
    """月別快適度0-100。設計書§4.2の式（係数は仮置き）。"""
    scores = []
    for m in monthly:
        t = m["temp_mean_c"]
        if t is None:
            scores.append(None)
            continue
        t_score = max(0.0, min(1.0, 1 - max(COMFORT["t_lo"] - t, t - COMFORT["t_hi"], 0) / 10))
        p_score = max(0.0, 1 - (m["precip_mm"] or 0) / 150)
        s_score = min(1.0, (m["sunshine_h"] or 0) / 250)
        scores.append(round(100 * (COMFORT["w_temp"] * t_score
                                   + COMFORT["w_precip"] * p_score
                                   + COMFORT["w_sun"] * s_score)))
    return scores


def indicator(value, depends_on, formula, cohort=None):
    return {"value": value, "cohort": cohort, "depends_on": depends_on, "formula": formula}


def daylight_hours(lat_deg: float, month: int) -> float:
    """各月15日時点の昼の長さ（時間）。太陽赤緯の近似式による天文計算（座標のみから求まる）。"""
    day_of_year = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349][month - 1]
    decl = math.radians(23.44) * math.sin(2 * math.pi * (284 + day_of_year) / 365)
    x = -math.tan(math.radians(lat_deg)) * math.tan(decl)
    x = max(-1.0, min(1.0, x))  # 白夜/極夜のクランプ
    return round(math.degrees(math.acos(x)) / 15 * 2, 1)


def main():
    places = load("data/master/places_master.json")["places"]
    extras = load("data/raw/wikidata/extras.json", {})
    airports = load("data/raw/airports/nearest.json", {})
    whs = load("data/raw/wikidata/whs_europe.json", [])
    views = load("data/raw/pageviews/views_2025.json", {})
    sitelinks = load("data/raw/wikidata/sitelinks.json", {})
    mofa = (load("data/raw/mofa/risk_levels.json") or {}).get("levels", {})
    osm = load("data/raw/osm/poi_counts.json", {})
    holidays = (load("data/raw/nager/holidays.json") or {}).get("countries", {})
    place_regions = load("data/raw/wikidata/place_regions.json", {})
    pli = (load("data/raw/eurostat/pli.json") or {}).get("countries", {})
    country_langs = load("data/raw/wikidata/countries.json", {})
    jp_missions = load("data/raw/wikidata/jp_missions.json", [])
    climate_all = (load("data/raw/era5/climate_monthly.json") or {})
    climate_by_id = climate_all.get("monthly", {})
    climate_period = climate_all.get("reference_period", "n/a")

    settlements = [p for p in places if p["type"] in ("city", "town_village")]
    cities = [p for p in places if p["type"] == "city" and p.get("lat")]
    cohort_ids = {p["id"] for p in settlements}

    # ---- コホート正規化用の元値を全地点分先に計算 ----
    heritage_detail, raw = {}, {k: {} for k in (
        "heritage", "ja", "en", "dining", "culture", "nightlife", "walk", "scenic",
        "outdoor", "lodging", "dining_pc", "lodging_pc")}
    for p in places:
        if not p.get("lat"):
            continue
        pid = p["id"]
        near = [(s, haversine_km(p["lat"], p["lon"], s["lat"], s["lon"])) for s in whs]
        onsite_qids, onsite = set(), []
        for s, d in sorted(near, key=lambda x: x[1]):
            if d <= 5 and s["qid"] not in onsite_qids:
                onsite_qids.add(s["qid"])
                onsite.append({"qid": s["qid"], "label": s["label"], "distance_km": round(d, 1)})
        heritage_detail[pid] = {"onsite": onsite,
                                "within30": len({s["qid"] for s, d in near if d <= 30})}
        raw["heritage"][pid] = 2 * len(onsite) + heritage_detail[pid]["within30"]
        v = views.get(p["qid"], {})
        raw["ja"][pid], raw["en"][pid] = v.get("ja"), v.get("en")
        o = osm.get(pid)
        if o:
            raw["dining"][pid] = o["dining_5km"]
            raw["culture"][pid] = o["culture_5km"]
            raw["nightlife"][pid] = o["nightlife_5km"]
            raw["lodging"][pid] = o["lodging_5km"]
            pop = p.get("population")
            if pop:
                # 人口あたり（充実度ゲート用）: 小規模観光地が絶対数のみだと過小評価されるため
                raw["dining_pc"][pid] = o["dining_5km"] / pop
                raw["lodging_pc"][pid] = o["lodging_5km"] / pop
            raw["walk"][pid] = o["dining_1km"] + o["culture_1km"] + o["shopping_1km"]
            raw["scenic"][pid] = (o["viewpoints_5km"] + 0.5 * o["peaks_10km"]
                                  + 0.5 * o["lakes_10km"] + (5 if o["coastline_10km"] else 0)
                                  + 0.3 * o["protected_areas_10km"])
            raw["outdoor"][pid] = (o["hiking_routes_10km"] + o["ski_marina_10km"]
                                   + o["parks_gardens_5km"])

    pct = {k: percentile_map({i: v for i, v in vals.items() if i in cohort_ids})
           for k, vals in raw.items()}

    # ---- レコード組み立て ----
    records = []
    stats = {"poi": 0, "climate": 0, "views_ja": 0, "safety": 0, "elev": 0, "whs": 0}
    for p in places:
        pid = p["id"]
        is_route = p["type"] == "route"
        is_settlement = p["type"] in ("city", "town_village")

        base = None
        if p["type"] in ("single_poi", "natural_feature") and p.get("lat"):
            cand = min(((s, haversine_km(p["lat"], p["lon"], s["lat"], s["lon"]))
                        for s in settlements if s.get("lat")), key=lambda x: x[1])
            base = cand[0]["id"]

        record = {"identity": {
            "id": pid, "name_ja": p["name_ja"], "name_en": p["name_en"],
            "qid": p.get("qid"), "country": p.get("country"), "country_ja": p.get("country_ja"),
            "type": p["type"], "lat": p.get("lat"), "lon": p.get("lon"),
            "base_place_id": base, "endpoints": p.get("endpoints"), "note": p.get("note"),
        }}

        if is_route:
            for b in ("geography", "poi", "osm_features", "heritage", "climate",
                      "access", "recognition", "safety", "holidays", "daylight",
                      "economy", "country_info", "media", "indicators"):
                record[b] = None
        else:
            elev = (extras.get(p["qid"]) or {}).get("elevation_m")
            record["geography"] = {
                "population": p.get("population") if is_settlement else None,
                "population_date": p.get("population_date") if is_settlement else None,
                "elevation_m": elev, "coastal": None,
                "_meta": meta("wikidata", "CC0-1.0"),
            }
            hd = heritage_detail[pid]
            record["heritage"] = {"whs_onsite": hd["onsite"], "whs_within_30km": hd["within30"],
                                  "_meta": meta("wikidata", "CC0-1.0")}

            # 画像群（Wikidataの画像プロパティ → Wikimedia Commons。画像自体のライセンスは画像ごとに異なる）
            imgs = (extras.get(p["qid"]) or {}).get("images") or []
            if imgs:
                items = []
                for im in imgs:
                    fn = urllib.parse.quote(im["file"].replace(" ", "_"))
                    items.append({
                        "kind": im["kind"],
                        "commons_file": im["file"],
                        "image_url": f"https://commons.wikimedia.org/wiki/Special:FilePath/{fn}?width=800",
                        "image_source_url": f"https://commons.wikimedia.org/wiki/File:{fn}",
                    })
                record["media"] = {
                    "images": items,
                    "_meta": meta("wikidata", "per-image (Wikimedia Commons)",
                                  "画像: Wikimedia Commons（ライセンス・作者は各出典ページを参照）"),
                }
            else:
                record["media"] = None

            o = osm.get(pid)
            if o:
                record["poi"] = {
                    "radius_km": 5,
                    "dining_5km": o["dining_5km"], "dining_categories_5km": None,
                    "culture_5km": o["culture_5km"], "nightlife_5km": o["nightlife_5km"],
                    "shopping_5km": o["shopping_5km"], "wellness_5km": o["wellness_5km"],
                    "lodging_5km": o["lodging_5km"],
                    "dining_1km": o["dining_1km"], "culture_1km": o["culture_1km"],
                    "shopping_1km": o["shopping_1km"],
                    "_meta": meta("osm", "ODbL-1.0", OSM_ATTR),
                }
                record["osm_features"] = {
                    "viewpoints_5km": o["viewpoints_5km"], "peaks_10km": o["peaks_10km"],
                    "lakes_10km": o["lakes_10km"],
                    "coastline_10km": o["coastline_10km"] > 0,
                    "protected_areas_10km": o["protected_areas_10km"],
                    "hiking_routes_10km": o["hiking_routes_10km"],
                    "ski_marina_10km": o["ski_marina_10km"],
                    "parks_gardens_5km": o["parks_gardens_5km"],
                    "pedestrian_area_1km": o["pedestrian_area_1km"] > 0,
                    "_meta": meta("osm", "ODbL-1.0", OSM_ATTR),
                }
            else:
                record["poi"] = None
                record["osm_features"] = None

            monthly = climate_by_id.get(pid)
            record["climate"] = {
                "monthly": monthly, "reference_period": climate_period,
                "_meta": meta("era5", "Copernicus-Products-Licence", ERA5_ATTR),
            } if monthly else None

            ap = airports.get(pid)
            hubs = sorted(((c, haversine_km(p["lat"], p["lon"], c["lat"], c["lon"]))
                           for c in cities if c["id"] != pid), key=lambda x: x[1])
            record["access"] = {
                "nearest_airport": dict(ap["nearest"]) if ap else None,
                "nearest_large_airport": {**ap["nearest_large"], "type": "large_airport"} if ap else None,
                "nearest_hub_place_id": hubs[0][0]["id"] if hubs else None,
                "nearest_hub_distance_km": round(hubs[0][1], 1) if hubs else None,
                "_meta": meta("ourairports", "Public-Domain"),
            }
            sl = sitelinks.get(p["qid"], {})
            v = views.get(p["qid"], {})
            record["recognition"] = {
                "wikipedia_views_ja_year": raw["ja"].get(pid),
                "wikipedia_views_en_year": raw["en"].get(pid),
                "wikipedia_views_ja_monthly": v.get("ja_monthly"),
                "wikipedia_views_en_monthly": v.get("en_monthly"),
                "wikipedia_sitelinks": sl.get("n_sitelinks"),
                "views_year": "2025", "nights_spent_nuts2": None,
                "_meta": meta("wikimedia_pageviews", "CC0-1.0"),
            }
            lv = mofa.get(p.get("country"), {}).get("risk_level") if mofa else None
            record["safety"] = {
                "mofa_risk_level": lv, "granularity": "country",
                "_meta": meta("mofa", "govt-standard-terms-2.0(CC-BY-4.0互換)",
                              "出典：外務省 海外安全情報オープンデータ（https://www.ezairyu.mofa.go.jp/html/opendata/）"),
            } if mofa else None

            cc = p.get("country")

            # 祝日: 全国区＋この地点の州・地域に適用される地域祝日（place_regionsと突合）
            h_cc = holidays.get(cc)
            if h_cc:
                region_codes = set(place_regions.get(pid, []))
                counts = [0] * 12
                for h in h_cc["holidays"]:
                    applies = h["global"] or (h["counties"] and region_codes.intersection(h["counties"]))
                    if applies:
                        counts[int(h["date"][5:7]) - 1] += 1
                record["holidays"] = {
                    "reference_year": h_cc["reference_year"],
                    "monthly_counts": counts, "total": sum(counts),
                    "granularity": "region" if region_codes else "country",
                    "_meta": meta("nager_date", "MIT"),
                }
            else:
                record["holidays"] = None

            # 日照時間（座標からの天文計算。ソース分離のためclimateとは別ブロック）
            record["daylight"] = {
                "monthly": [{"month": m, "daylight_h": daylight_hours(p["lat"], m)}
                            for m in range(1, 13)],
                "_meta": meta("computed", "n/a（座標からの天文計算）"),
            } if p.get("lat") is not None else None

            # 物価水準（Eurostat PLI・国単位・年次）
            e_cc = pli.get(cc)
            record["economy"] = {
                "pli_total": e_cc["pli_total"],
                "pli_restaurants_hotels": e_cc["pli_restaurants_hotels"],
                "pli_base": "EU27_2020=100", "pli_year": e_cc["year"],
                "granularity": "country",
                "_meta": meta("eurostat", "CC-BY-4.0",
                              "Source: Eurostat, Purchasing power parities (prc_ppp_ind)"),
            } if e_cc else None

            # 公用語（国単位）＋日本の在外公館（最寄りは地点単位の直線距離）
            langs = (country_langs.get(cc) or {}).get("official_languages_ja", [])
            in_country = [m["label"] for m in jp_missions if m["country"] == cc and m["label"]]
            nearest = None
            if p.get("lat") is not None:
                cands = [(m, haversine_km(p["lat"], p["lon"], m["lat"], m["lon"]))
                         for m in jp_missions if m.get("lat") is not None]
                if cands:
                    m, d = min(cands, key=lambda x: x[1])
                    nearest = {"label": m["label"], "city": m.get("city"),
                               "country": m.get("country"), "distance_km": round(d, 1)}
            record["country_info"] = {
                "official_languages_ja": langs,
                "jp_missions_in_country": in_country,
                "nearest_jp_mission": nearest,
                "_meta": meta("wikidata", "CC0-1.0"),
            } if (langs or in_country or nearest) else None

            # ---- Layer 2 指標（settlementコホートのみ。式は設計書§4） ----
            if is_settlement:
                ind = {
                    "historic_depth": indicator(
                        pct["heritage"].get(pid), ["wikidata"],
                        "pct(2*whs_onsite件数 + whs_within_30km)", "settlement"),
                    "recognition_jp": indicator(
                        pct["ja"].get(pid, pct["en"].get(pid)),
                        ["wikimedia_pageviews"],
                        "pct(ja年間閲覧数)。ja記事なしはpct(en閲覧数)で代替", "settlement"),
                }
                if o:
                    ped_bonus = 10 if o["pedestrian_area_1km"] > 0 else 0
                    walk = pct["walk"].get(pid)
                    ind.update({
                        "food_scene": indicator(
                            pct["dining"].get(pid), ["osm"],
                            "pct(dining_5km)（OSM版。カテゴリ多様性はFoursquare導入後に追加）",
                            "settlement"),
                        "lodging_scene": indicator(
                            pct["lodging"].get(pid), ["osm"], "pct(lodging_5km)", "settlement"),
                        "culture_scene": indicator(
                            pct["culture"].get(pid), ["osm"], "pct(culture_5km)", "settlement"),
                        "vibrancy": indicator(
                            pct["nightlife"].get(pid), ["osm"], "pct(nightlife_5km)", "settlement"),
                        "walkability": indicator(
                            min(100, walk + ped_bonus) if walk is not None else None, ["osm"],
                            "pct(dining_1km+culture_1km+shopping_1km) + 歩行者エリアなら+10（上限100）",
                            "settlement"),
                        "scenic_nature": indicator(
                            pct["scenic"].get(pid), ["osm"],
                            "pct(viewpoints_5km + 0.5*peaks + 0.5*lakes + 海岸+5 + 0.3*保護区)",
                            "settlement"),
                        "outdoor_activity": indicator(
                            pct["outdoor"].get(pid), ["osm"],
                            "pct(hiking_routes + ski_marina + parks_gardens)", "settlement"),
                    })
                    # 穴場: 認知度が低く、かつ最低限の充実度がある（設計書§4.3）
                    # 飲食・宿泊は絶対数と人口あたりの高い方のパーセンタイルで判定
                    rec = ind["recognition_jp"]["value"]
                    dine = max(pct["dining"].get(pid, 0), pct["dining_pc"].get(pid, 0))
                    lodge = max(pct["lodging"].get(pid, 0), pct["lodging_pc"].get(pid, 0))
                    gate = (min(dine, lodge) > 25
                            and max(pct["culture"].get(pid, 0), pct["scenic"].get(pid, 0)) > 25)
                    ind["hidden_gem"] = indicator(
                        round((100 - rec) * (1 if gate else 0)) if rec is not None else None,
                        ["wikimedia_pageviews", "osm", "wikidata"],
                        "(100 - recognition_jp) × 充実度ゲート(飲食・宿泊が絶対数or人口あたりでP25超"
                        " かつ 文化or自然>P25)",
                        "settlement")
                if monthly:
                    ind["seasonal_comfort"] = indicator(
                        seasonal_comfort(monthly), ["era5"],
                        "月別: 0.5*快適帯(8-27C台形) + 0.3*(1-降水/150mm) + 0.2*min(日照/250h,1)")
                record["indicators"] = ind
            else:
                record["indicators"] = None

        pending = [b for b in ("poi", "climate") if not is_route and record.get(b) is None]
        record["meta"] = {
            "schema_version": SCHEMA_VERSION, "generated_at": TODAY,
            "notes": (f"未取得: {', '.join(pending)}（取得後に再生成）" if pending else None),
        }
        records.append(record)

        if not is_route:
            stats["poi"] += record["poi"] is not None
            stats["climate"] += record["climate"] is not None
            stats["views_ja"] += raw["ja"].get(pid) is not None
            stats["safety"] += bool(record.get("safety") and record["safety"]["mofa_risk_level"] is not None)
            stats["elev"] += (extras.get(p["qid"]) or {}).get("elevation_m") is not None
            stats["whs"] += bool(heritage_detail[pid]["onsite"])

    # ---- スキーマ検証 ----
    schema = json.loads((ROOT / "schema/place.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    n_err = 0
    for r in records:
        for e in validator.iter_errors(r):
            n_err += 1
            print(f"SCHEMA ERROR [{r['identity']['id']}] {'/'.join(map(str, e.path))}: {e.message}")
    if n_err:
        raise SystemExit(f"schema errors: {n_err}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"schema_version": SCHEMA_VERSION, "generated_at": TODAY, "count": len(records),
         "places": records}, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(records) - 2  # route除く
    print(f"\nwrote {OUT} ({len(records)}件, schema OK)")
    print(f"充足: POI {stats['poi']}/{n}, 気候 {stats['climate']}/{n}, "
          f"標高 {stats['elev']}/{n}, 世界遺産5km圏 {stats['whs']}/{n}, "
          f"ja閲覧数 {stats['views_ja']}/{n}, 安全情報 {stats['safety']}/{n}")


if __name__ == "__main__":
    main()
