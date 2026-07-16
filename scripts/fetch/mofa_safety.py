#!/usr/bin/env python3
"""フェーズ3: 外務省 海外安全情報オープンデータから対象21カ国の危険情報レベルを取得する。

- 国コード一覧: html/opendata/support/country.xlsx（公式・取得済み data/raw/mofa/country_codes.xlsx）
- 実データ: https://www.ezairyu.mofa.go.jp/opendata/country/<国コード>.xml
  （riskLevel1〜4 のフラグ＝国内のどこかにそのレベルの地域がある、を示す）
- 格納値: mofa_risk_level = フラグが立っている最大レベル（なければ0）
  ※「国内最悪値」であり都市自体のレベルではない（granularity=country）。
- ライセンス: 政府標準利用規約2.0（CC BY 4.0互換）。商用可・出典表示要
- 出力: data/raw/mofa/risk_levels.json
"""
import json
import re
import time
import urllib.request
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/mofa"
XLSX = RAW / "country_codes.xlsx"
OUT = RAW / "risk_levels.json"
DATA_URL = "https://www.ezairyu.mofa.go.jp/opendata/country/{code}.xml"
UA = {"User-Agent": "city-data-builder/0.1 (fetch)"}
TODAY = "2026-07-16"

# master の country_ja → 公式一覧の国名表記（部分一致で対応）
NAME_ALIASES = {"イギリス": "英国"}


def official_codes() -> dict:
    """公式xlsxから 国名 → 国コード の辞書を作る。"""
    wb = openpyxl.load_workbook(XLSX)
    codes = {}
    for row in wb.active.iter_rows(values_only=True):
        if row[2] is None or not row[3]:
            continue
        codes[str(row[4])] = str(row[3])
    return codes


def fetch_xml(code: str) -> str:
    p = RAW / f"{code}.xml"
    if not p.exists():
        req = urllib.request.Request(DATA_URL.format(code=code), headers=UA)
        p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(1)
    return p.read_text(encoding="utf-8", errors="replace")


def risk_level(xml_text: str):
    """riskLevel4〜1 のフラグから最大レベルを返す（すべて0なら0）。"""
    for n in (4, 3, 2, 1):
        m = re.search(rf"<riskLevel{n}>\s*(\d)\s*</riskLevel{n}>", xml_text)
        if m and m.group(1) == "1":
            return n
    return 0


def main():
    codes = official_codes()
    ja_by_iso = {p["country"]: p["country_ja"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("country")}

    levels = {}
    for iso, ja in sorted(ja_by_iso.items()):
        key = NAME_ALIASES.get(ja, ja)
        code = next((c for name, c in codes.items() if key in name), None)
        if code is None:
            print(f"  {ja}({iso}): 国コード未発見 → 手動確認")
            levels[iso] = {"country_ja": ja, "mofa_code": None, "risk_level": None}
            continue
        xml_text = fetch_xml(code)
        lv = risk_level(xml_text)
        levels[iso] = {"country_ja": ja, "mofa_code": code, "risk_level": lv}
        print(f"  {ja}({iso}): code={code} level={lv}")

    OUT.write_text(json.dumps(
        {"retrieved_at": TODAY, "source": DATA_URL.format(code="<code>"),
         "semantics": "国内に存在する危険情報の最大レベル（0=発出なし）。粒度は国単位",
         "levels": levels}, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for v in levels.values() if v["risk_level"] is not None)
    print(f"wrote {OUT} ({n}/{len(levels)}カ国)")


if __name__ == "__main__":
    main()
