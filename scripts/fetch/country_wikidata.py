#!/usr/bin/env python3
"""データ拡張: Wikidata(CC0)から (1)対象21カ国の公用語 (2)日本の在外公館（大使館・領事館）を取得する。
出力:
- data/raw/wikidata/countries.json … ISO → {qid, official_languages_ja[]}
- data/raw/wikidata/jp_missions.json … [{label_ja, label_en, country, lat, lon}]
  （在外公館は「外交使節団クラス配下 かつ 英語ラベルに 'of Japan' を含む」で抽出。座標つきのみ）
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "city-data-builder/0.1 (fetch)"}
OUT_COUNTRIES = ROOT / "data/raw/wikidata/countries.json"
OUT_MISSIONS = ROOT / "data/raw/wikidata/jp_missions.json"

# P137(運営者)=日本 が未登録でクエリに掛からない公館のピン留め（実在確認済み）。
# 値は国コード（P17が「オランダ王国」等の別QIDを指す場合のフォールバック）
PINNED_MISSIONS = {
    "Q69522954": "DK",  # 在デンマーク日本国大使館（コペンハーゲン）
    "Q17386935": "NL",  # 在オランダ日本国大使館（ハーグ）
}


def sparql(query: str):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
        {"query": query, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=120))["results"]["bindings"]


def main():
    isos = sorted({p["country"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("country")})
    values = " ".join(f'"{c}"' for c in isos)

    # (1) 公用語（P37）
    rows = sparql(f"""
    SELECT ?iso ?country ?langLabel WHERE {{
      VALUES ?iso {{ {values} }}
      ?country wdt:P297 ?iso .
      OPTIONAL {{ ?country wdt:P37 ?lang }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ja,en". }}
    }}""")
    countries = {}
    for r in rows:
        iso = r["iso"]["value"]
        c = countries.setdefault(iso, {
            "qid": r["country"]["value"].rsplit("/", 1)[-1], "official_languages_ja": []})
        lang = r.get("langLabel", {}).get("value")
        if lang and lang not in c["official_languages_ja"]:
            c["official_languages_ja"].append(lang)
    OUT_COUNTRIES.write_text(json.dumps(countries, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"公用語: {len(countries)}カ国 -> {OUT_COUNTRIES}")

    # (2) 日本の在外公館。運営者(P137)=日本(Q17) で特定（ラベル検索より軽く確実）。
    #     国はISO文字列の逆引きではなくQID直指定（逆引きはWDQSで504になるため）。
    #     座標(P625)は未登録の公館があるため任意。所在都市(P131)も取得
    qid_to_iso = {v["qid"]: iso for iso, v in countries.items()}
    host_values = " ".join(f"wd:{q}" for q in qid_to_iso)
    rows = sparql(f"""
    SELECT ?e ?eLabel ?host ?lat ?lon ?cityLabel WHERE {{
      ?e wdt:P137 wd:Q17 .
      VALUES ?cls {{ wd:Q3917681 wd:Q1155502 wd:Q7843791 }}
      ?e wdt:P31 ?cls .
      VALUES ?host {{ {host_values} }}
      ?e wdt:P17 ?host .
      OPTIONAL {{ ?e p:P625/psv:P625 ?c .
                  ?c wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon }}
      OPTIONAL {{ ?e wdt:P131 ?city }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ja,en". }}
    }}""")
    pinned = " ".join(f"wd:{q}" for q in PINNED_MISSIONS)
    rows += sparql(f"""
    SELECT ?e ?eLabel ?host ?lat ?lon ?cityLabel WHERE {{
      VALUES ?e {{ {pinned} }}
      ?e wdt:P17 ?host .
      OPTIONAL {{ ?e p:P625/psv:P625 ?c .
                  ?c wikibase:geoLatitude ?lat ; wikibase:geoLongitude ?lon }}
      OPTIONAL {{ ?e wdt:P131 ?city }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ja,en". }}
    }}""")
    seen, missions = set(), []
    for r in rows:
        qid = r["e"]["value"].rsplit("/", 1)[-1]
        if qid in seen:
            continue
        seen.add(qid)
        missions.append({
            "qid": qid,
            "label": r.get("eLabel", {}).get("value"),
            "country": qid_to_iso.get(r["host"]["value"].rsplit("/", 1)[-1],
                                      PINNED_MISSIONS.get(qid)),
            "city": r.get("cityLabel", {}).get("value"),
            "lat": float(r["lat"]["value"]) if "lat" in r else None,
            "lon": float(r["lon"]["value"]) if "lon" in r else None,
        })
    OUT_MISSIONS.write_text(json.dumps(missions, ensure_ascii=False, indent=1), encoding="utf-8")
    cc = sorted({m["country"] for m in missions})
    print(f"日本の在外公館（座標つき）: {len(missions)}件 / {len(cc)}カ国 {cc} -> {OUT_MISSIONS}")


if __name__ == "__main__":
    main()
