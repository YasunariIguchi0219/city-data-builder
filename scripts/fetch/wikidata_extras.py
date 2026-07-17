#!/usr/bin/env python3
"""フェーズ3: マスタ全QIDの追加属性（標高 P2044・代表画像 P18）をWikidataから一括取得する。
出力: data/raw/wikidata/extras.json （QID → {elevation_m, image}）
- image は Wikimedia Commons のファイル名。URL化は build_places.py 側で行う
- 注意: 画像ファイル自体のライセンスはCC0ではなく画像ごとに異なる（CC BY-SA等）。
  表示時は出典ページへのリンクで帰属をたどれるようにする
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_master import ROOT, api_get

OUT = ROOT / "data/raw/wikidata/extras.json"


def first_value(ent: dict, prop: str):
    for c in ent.get("claims", {}).get(prop, []):
        if c["mainsnak"].get("snaktype") == "value":
            return c["mainsnak"]["datavalue"]["value"]
    return None


def main():
    qids = [p["qid"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("qid")]
    extras = {}
    for i in range(0, len(qids), 50):
        ents = api_get({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
                        "props": "claims"})["entities"]
        for qid, ent in ents.items():
            elev = first_value(ent, "P2044")
            extras[qid] = {
                "elevation_m": float(elev["amount"]) if elev else None,
                "image": first_value(ent, "P18"),  # Commonsのファイル名（例 "Tour Eiffel....jpg"）
            }
        print(f"fetched {min(i + 50, len(qids))}/{len(qids)}", flush=True)

    OUT.write_text(json.dumps(extras, ensure_ascii=False, indent=1), encoding="utf-8")
    n_elev = sum(1 for v in extras.values() if v["elevation_m"] is not None)
    n_img = sum(1 for v in extras.values() if v["image"])
    print(f"標高あり: {n_elev}/{len(extras)}, 画像あり: {n_img}/{len(extras)} -> {OUT}")


if __name__ == "__main__":
    main()
