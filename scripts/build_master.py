#!/usr/bin/env python3
"""フェーズ0: seed_places.json の同定案を Wikidata API で検証し、
places_master.json（名寄せマスタ）と docs/phase0/review.md（レビュー用一覧）を生成する。

- 検索: wbsearchentities（英語ラベル）で候補を取得
- 検証: 候補の P17（国）がシードの想定国と一致し、P625（座標）を持つ最初の候補を採用
- 取得: QID / 英語・日本語・現地語ラベル / 座標 / 人口(P1082) / P31(instance of)
- 分類: settlement は人口10万以上→city、未満・不明→town_village
- キャッシュ: data/raw/wikidata/cache.json（再実行時はAPIを叩かない）
"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data/master/seed_places.json"
CACHE = ROOT / "data/raw/wikidata/cache.json"
MASTER = ROOT / "data/master/places_master.json"
REVIEW = ROOT / "docs/phase0/review.md"

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "city-data-builder/0.1 (phase0 master build; internal research)"}

COUNTRY_QID = {
    "FR": "Q142", "ES": "Q29", "IT": "Q38", "GB": "Q145", "DE": "Q183",
    "CH": "Q39", "AT": "Q40", "PT": "Q45", "NL": "Q55", "BE": "Q31",
    "LU": "Q32", "DK": "Q35", "NO": "Q20", "SE": "Q34", "FI": "Q33",
    "CZ": "Q213", "HU": "Q28", "SK": "Q214", "SI": "Q215", "HR": "Q224",
    "BA": "Q225",
}
COUNTRY_JA = {
    "FR": "フランス", "ES": "スペイン", "IT": "イタリア", "GB": "イギリス",
    "DE": "ドイツ", "CH": "スイス", "AT": "オーストリア", "PT": "ポルトガル",
    "NL": "オランダ", "BE": "ベルギー", "LU": "ルクセンブルク", "DK": "デンマーク",
    "NO": "ノルウェー", "SE": "スウェーデン", "FI": "フィンランド", "CZ": "チェコ",
    "HU": "ハンガリー", "SK": "スロバキア", "SI": "スロベニア", "HR": "クロアチア",
    "BA": "ボスニア・ヘルツェゴビナ",
}
DISAMBIGUATION = "Q4167410"
CITY_POP_THRESHOLD = 100_000


MIN_INTERVAL = 1.5  # 秒。Wikidataのレート制限(429)対策
_last_request = [0.0]


def api_get(params: dict) -> dict:
    params = {**params, "format": "json"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    last_err = None
    for attempt in range(6):
        wait = MIN_INTERVAL - (time.monotonic() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        try:
            _last_request[0] = time.monotonic()
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                time.sleep(int(retry_after) if retry_after and retry_after.isdigit()
                           else 15 * (attempt + 1))
            else:
                time.sleep(3)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(3)
    raise RuntimeError(f"API failed: {url}: {last_err}")


def search_candidates(term: str) -> list[str]:
    r = api_get({"action": "wbsearchentities", "search": term,
                 "language": "en", "type": "item", "limit": "10"})
    return [c["id"] for c in r.get("search", [])]


def get_entities(ids: list[str]) -> dict:
    out = {}
    for i in range(0, len(ids), 50):
        r = api_get({"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]),
                     "props": "claims|labels|descriptions"})
        out.update(r.get("entities", {}))
    return out


def claim_item_ids(ent: dict, prop: str) -> list[str]:
    ids = []
    for c in ent.get("claims", {}).get(prop, []):
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") == "value":
            ids.append(snak["datavalue"]["value"]["id"])
    return ids


def coordinates(ent: dict):
    for c in ent.get("claims", {}).get("P625", []):
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") == "value":
            v = snak["datavalue"]["value"]
            return round(v["latitude"], 5), round(v["longitude"], 5)
    return None


def population(ent: dict):
    """人口(P1082)の現行値を返す。preferredランク優先、次に時点(P585)の新しさ。
    紀元前(-0550-…)の歴史人口を「最新」と誤認しないよう、年は符号込みの数値で比較する。
    deprecatedランクは除外。"""
    best = None  # (is_preferred, year, amount, date_str)
    for c in ent.get("claims", {}).get("P1082", []):
        if c.get("rank") == "deprecated":
            continue
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        amount = int(float(snak["datavalue"]["value"]["amount"]))
        year, date_str = -(10 ** 9), None
        for q in c.get("qualifiers", {}).get("P585", []):
            if q.get("snaktype") == "value":
                t = q["datavalue"]["value"]["time"]  # 例 "+2023-01-01T00:00:00Z" / "-0550-01-01…"
                m = re.match(r"^([+-])(\d+)", t)
                if m:
                    year = int(m.group(1) + m.group(2))
                    date_str = t[:11].lstrip("+")
        key = (1 if c.get("rank") == "preferred" else 0, year)
        if best is None or key > best[0]:
            best = (key, amount, date_str)
    return (best[1], best[2]) if best else (None, None)


def label(ent: dict, lang: str):
    return ent.get("labels", {}).get(lang, {}).get("value")


def description(ent: dict, lang: str = "en"):
    return ent.get("descriptions", {}).get(lang, {}).get("value")


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()


def entity_to_result(qid: str, ent: dict) -> dict:
    coord = coordinates(ent)
    pop, pop_date = population(ent)
    return {
        "qid": qid,
        "label_en": label(ent, "en"),
        "label_ja": label(ent, "ja"),
        "label_local": None,
        "description_en": description(ent),
        "lat": coord[0] if coord else None,
        "lon": coord[1] if coord else None,
        "population": pop, "population_date": pop_date,
        "instance_of": claim_item_ids(ent, "P31")[:6],
    }


def resolve(seed: dict, cache: dict) -> dict:
    """1件のシードをWikidataで解決する。結果dictを返す。
    seedに qid があれば検索せず直接そのエンティティを採用（誤同定のピン留め修正用）。"""
    pinned = seed.get("qid")
    key = f"qid:{pinned}" if pinned else f"{seed['search']}|{seed['country']}"
    if key in cache:
        return cache[key]

    if pinned:
        result = entity_to_result(pinned, get_entities([pinned])[pinned])
    else:
        expected_country = COUNTRY_QID[seed["country"]]
        candidates = search_candidates(seed["search"])
        if not candidates:
            result = {"qid": None, "reason": "no_candidates"}
        else:
            entities = get_entities(candidates)
            chosen = None
            for cid in candidates:
                ent = entities.get(cid, {})
                p31 = claim_item_ids(ent, "P31")
                if DISAMBIGUATION in p31:
                    continue
                if expected_country not in claim_item_ids(ent, "P17"):
                    continue
                if coordinates(ent) is None:
                    continue
                chosen = cid
                break
            if chosen is None:
                result = {"qid": None, "reason": "no_country_match",
                          "candidates": candidates[:5]}
            else:
                result = entity_to_result(chosen, entities[chosen])

    cache[key] = result
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return result


def main():
    seeds = json.loads(SEED.read_text(encoding="utf-8"))["places"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    records, unresolved = [], []
    for i, seed in enumerate(seeds, 1):
        if seed["type"] == "route":
            records.append({
                "id": slugify(seed["name_en"]),
                "name_ja": seed["ja"], "name_en": seed["name_en"],
                "qid": None, "country": None, "type": "route",
                "lat": None, "lon": None, "population": None,
                "endpoints": seed["endpoints"],
                "note": seed.get("note"), "review": seed.get("review", False),
            })
            continue

        r = resolve(seed, cache)
        if r.get("qid") is None:
            unresolved.append((seed, r))
            records.append({
                "id": slugify(seed["search"]),
                "name_ja": seed["ja"], "name_en": seed["search"],
                "qid": None, "country": seed["country"], "type": seed["type"],
                "lat": None, "lon": None, "population": None,
                "note": (seed.get("note") or "") + f" 【未解決: {r['reason']}】",
                "review": True,
            })
            print(f"[{i:3}/154] UNRESOLVED {seed['ja']} ({seed['search']}): {r['reason']}", flush=True)
            continue

        ptype = seed["type"]
        if ptype == "settlement":
            ptype = "city" if (r["population"] or 0) >= CITY_POP_THRESHOLD else "town_village"

        records.append({
            "id": slugify(seed["search"]),
            "name_ja": seed["ja"],
            "name_en": r["label_en"] or seed["search"],
            "wikidata_label_ja": r["label_ja"],
            "qid": r["qid"],
            "country": seed["country"],
            "country_ja": COUNTRY_JA[seed["country"]],
            "type": ptype,
            "lat": r["lat"], "lon": r["lon"],
            "population": r["population"], "population_date": r["population_date"],
            "description_en": r["description_en"],
            "instance_of": r["instance_of"],
            "note": seed.get("note"),
            "review": seed.get("review", False),
        })
        print(f"[{i:3}/154] {seed['ja']} -> {r['qid']} {r['label_en']} pop={r['population']}", flush=True)

    MASTER.write_text(json.dumps(
        {"generated_by": "scripts/build_master.py", "source_seed": "data/master/seed_places.json",
         "count": len(records), "places": records},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {MASTER} ({len(records)} records, {len(unresolved)} unresolved)")

    write_review(records)
    print(f"wrote {REVIEW}")


def write_review(records: list[dict]):
    def row(r):
        qid = f"[{r['qid']}](https://www.wikidata.org/wiki/{r['qid']})" if r.get("qid") else "—"
        pop = f"{r['population']:,}" if r.get("population") else "—"
        wl = r.get("wikidata_label_ja") or "—"
        country = r.get("country_ja") or ("—" if r.get("country") is None else r["country"])
        note = (r.get("note") or "").replace("|", "／")
        return f"| {r['name_ja']} | {r['name_en']} | {country} | {r['type']} | {qid} | {pop} | {wl} | {note} |"

    header = ("| 日本語名（原本） | 同定結果（英語名） | 国 | 種別 | Wikidata | 人口 | Wikidata日本語ラベル | 備考 |\n"
              "| --- | --- | --- | --- | --- | --- | --- | --- |")

    flagged = [r for r in records if r.get("review")]
    normal = [r for r in records if not r.get("review")]

    type_counts = {}
    for r in records:
        type_counts[r["type"]] = type_counts.get(r["type"], 0) + 1
    counts = "、".join(f"{k}: {v}件" for k, v in sorted(type_counts.items()))

    lines = [
        "# フェーズ0 レビュー：154件の同定結果一覧",
        "",
        "`scripts/build_master.py` により生成。マスタ本体は `data/master/places_master.json`。",
        "",
        "> **レビュー結果（2026-07-16）：全件暫定承認。** リストの出所に正解を持つ者がいないため、"
        "曖昧エントリ（ディナン=仏Dinan、ランス=Reims 等）は本一覧の同定のまま採用する。"
        "将来ツアー文脈等で正解が判明した場合は `seed_places.json` のQID指定を修正して再生成する。",
        "",
        f"- 件数：{len(records)}件（{counts}）",
        "- 種別：city（人口10万以上）／town_village（それ未満・不明）／single_poi（城・遺跡等の単体スポット）／natural_feature（自然地物）／route（航路）",
        "- 「Wikidata日本語ラベル」列は同定の妥当性確認用。原本の日本語名と一致・近似していれば同定は概ね正しい。",
        "",
        "## ⚠️ 要確認エントリ（同定に曖昧さがあるもの）",
        "",
        header,
        *[row(r) for r in flagged],
        "",
        "## 全件一覧（上記以外）",
        "",
        header,
        *[row(r) for r in normal],
        "",
    ]
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
