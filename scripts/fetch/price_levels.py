#!/usr/bin/env python3
"""データ拡張: 対象21カ国の物価水準指数（Eurostat PLI, EU27=100）を取得する。
- データセット: prc_ppp_ind / na_item=PLI_EU27_2020（CC BY 4.0・年次更新）
- カテゴリ: A01=実質個人消費（総合の定番） / A0111=外食・宿泊（旅行者の体感物価に近い）
- 年は最新から遡って値のある年を採用（国によって欠損年があるため。英国はEU離脱後に欠損の可能性）
- 出力: data/raw/eurostat/pli.json （ISO国コード → {pli_total, pli_restaurants_hotels, year}）
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/eurostat/pli.json"
UA = {"User-Agent": "city-data-builder/0.1 (fetch)"}
YEARS = ["2024", "2023", "2022"]  # 新しい順に探す
CATS = {"A01": "pli_total", "A0111": "pli_restaurants_hotels"}
# Eurostatの地域コードは概ねISOと同じだが英国・ギリシャ等に独自コードがある
GEO_ALIAS = {"GB": "UK"}


def fetch(geo: str, cat: str):
    """最新の値と年を返す（なければ (None, None)）。"""
    params = urllib.parse.urlencode({
        "format": "JSON", "lang": "EN", "na_item": "PLI_EU27_2020",
        "ppp_cat": cat, "geo": geo}) + "".join(f"&time={y}" for y in YEARS)
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_ppp_ind?" + params
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
    time_idx = d["dimension"]["time"]["category"]["index"]
    values = d.get("value", {})
    for year in YEARS:  # 新しい順
        i = time_idx.get(year)
        if i is not None and str(i) in values:
            return values[str(i)], year
    return None, None


def main():
    countries = sorted({p["country"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("country")})
    result = {}
    for cc in countries:
        geo = GEO_ALIAS.get(cc, cc)
        entry = {"pli_total": None, "pli_restaurants_hotels": None, "year": None}
        for cat, key in CATS.items():
            v, y = fetch(geo, cat)
            entry[key] = v
            entry["year"] = entry["year"] or y
        result[cc] = entry
        print(f"  {cc}: 総合={entry['pli_total']} 外食宿泊={entry['pli_restaurants_hotels']} ({entry['year']})", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"retrieved_at": "2026-07-21", "base": "EU27_2020=100",
                               "countries": result}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    n = sum(1 for v in result.values() if v["pli_total"] is not None)
    print(f"wrote {OUT} ({n}/{len(result)}カ国で値あり)")


if __name__ == "__main__":
    main()
