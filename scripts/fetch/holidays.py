#!/usr/bin/env python3
"""データ拡張: 対象21カ国の祝日（Nager.Date API）を取得し、月別の祝日数に集計する。
- 入手元: https://date.nager.at/api/v3/PublicHolidays/{year}/{cc} （無料・キー不要・MIT）
- 全国一斉の祝日（global=true）のみ数える（州・県単位の地方祝日はノイズになるため除外）
- 出力: data/raw/nager/holidays.json （ISO国コード → {reference_year, monthly_counts[12], total}）
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
        monthly = [0] * 12
        for h in holidays:
            if h.get("global"):
                monthly[int(h["date"][5:7]) - 1] += 1
        result[cc] = {"reference_year": YEAR, "monthly_counts": monthly, "total": sum(monthly)}
        print(f"  {cc}: 年間{sum(monthly)}日（全国区のみ）", flush=True)
        time.sleep(0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"retrieved_at": "2026-07-21", "source": "date.nager.at",
                               "countries": result}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"wrote {OUT} ({len(result)}カ国)")


if __name__ == "__main__":
    main()
