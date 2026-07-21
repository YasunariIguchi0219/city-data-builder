#!/usr/bin/env python3
"""データ拡張: 対象21カ国の祝日（Nager.Date API）を取得する。
- 入手元: https://date.nager.at/api/v3/PublicHolidays/{year}/{cc} （無料・キー不要・MIT）
- 全国区（global）と地域限定（counties=ISO 3166-2コード）を両方保存し、
  地点への適用判定（その町の州の祝日か）は build_places.py 側で place_regions と突合して行う
- 出力: data/raw/nager/holidays.json （ISO国コード → {reference_year, holidays[]}）
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/nager/holidays.json"
UA = {"User-Agent": "city-data-builder/0.1 (fetch)"}
YEAR = 2026


def main():
    countries = sorted({p["country"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("country")})
    result = {}
    for cc in countries:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{YEAR}/{cc}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            holidays = json.load(r)
        items = [{"date": h["date"], "global": bool(h.get("global")),
                  "counties": h.get("counties")} for h in holidays]
        n_global = sum(1 for h in items if h["global"])
        result[cc] = {"reference_year": YEAR, "holidays": items}
        print(f"  {cc}: 全国区{n_global}日 / 地域限定含め{len(items)}日", flush=True)
        time.sleep(0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"retrieved_at": "2026-07-21", "source": "date.nager.at",
                               "countries": result}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"wrote {OUT} ({len(result)}カ国)")


if __name__ == "__main__":
    main()
