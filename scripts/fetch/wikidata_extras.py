#!/usr/bin/env python3
"""フェーズ3: マスタ全QIDの追加属性（標高 P2044）をWikidataから一括取得する。
出力: data/raw/wikidata/extras.json （QID → {elevation_m}）
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_master import ROOT, api_get

OUT = ROOT / "data/raw/wikidata/extras.json"


def main():
    qids = [p["qid"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("qid")]
    extras = {}
    for i in range(0, len(qids), 50):
        ents = api_get({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
                        "props": "claims"})["entities"]
        for qid, ent in ents.items():
            elev = None
            for c in ent.get("claims", {}).get("P2044", []):
                if c["mainsnak"].get("snaktype") == "value":
                    elev = float(c["mainsnak"]["datavalue"]["value"]["amount"])
                    break
            extras[qid] = {"elevation_m": elev}
        print(f"fetched {min(i + 50, len(qids))}/{len(qids)}", flush=True)

    OUT.write_text(json.dumps(extras, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for v in extras.values() if v["elevation_m"] is not None)
    print(f"標高あり: {n}/{len(extras)} ({n / len(extras):.0%}) -> {OUT}")


if __name__ == "__main__":
    main()
