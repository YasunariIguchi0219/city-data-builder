#!/usr/bin/env python3
"""フェーズ1調査: Wikipedia記事カバー率の実測。
マスタの全QIDについて Wikidata sitelinks から ja/en 版Wikipedia記事の有無を取得し、
data/raw/survey/wikipedia_sitelinks.json に保存、カバー率を表示する。
（記事タイトルは後続の Pageviews API 調査（認知度データ）の入力になる）
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/ を import パスに追加
from build_master import ROOT, api_get

OUT = ROOT / "data/raw/survey/wikipedia_sitelinks.json"


def main():
    master = json.loads((ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))
    qids = [p["qid"] for p in master["places"] if p.get("qid")]

    sitelinks = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        r = api_get({"action": "wbgetentities", "ids": "|".join(chunk),
                     "props": "sitelinks"})
        for qid, ent in r.get("entities", {}).items():
            sl = ent.get("sitelinks", {})
            sitelinks[qid] = {
                "jawiki": sl.get("jawiki", {}).get("title"),
                "enwiki": sl.get("enwiki", {}).get("title"),
                "n_sitelinks": len(sl),  # 全言語版の記事数（認知度の参考指標）
            }
        print(f"fetched {min(i + 50, len(qids))}/{len(qids)}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sitelinks, ensure_ascii=False, indent=1), encoding="utf-8")

    n = len(qids)
    ja = sum(1 for v in sitelinks.values() if v["jawiki"])
    en = sum(1 for v in sitelinks.values() if v["enwiki"])
    print(f"\n対象: {n}件（route除く）")
    print(f"日本語版Wikipedia記事あり: {ja}件 ({ja / n:.1%})")
    print(f"英語版Wikipedia記事あり:   {en}件 ({en / n:.1%})")
    missing_ja = [q for q, v in sitelinks.items() if not v["jawiki"]]
    if missing_ja:
        names = {p["qid"]: p["name_ja"] for p in master["places"]}
        print("ja記事なし:", ", ".join(names[q] for q in missing_ja))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
