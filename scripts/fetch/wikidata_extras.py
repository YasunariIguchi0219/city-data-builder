#!/usr/bin/env python3
"""フェーズ3: マスタ全QIDの追加属性（標高 P2044・画像群）をWikidataから一括取得する。
出力: data/raw/wikidata/extras.json （QID → {elevation_m, images: [{kind, file}]}）

画像は種類が明確なプロパティのみ採用（Commonsカテゴリの無選別取得はしない）:
  P18=代表 / P4291=パノラマ / P3451=夜景 / P8592=空撮 / P5252=冬景色 / P2716=コラージュ
ファイル名はWikimedia Commonsのもの。URL化は build_places.py 側で行う。
注意: 画像ファイル自体のライセンスは画像ごとに異なる（CC BY-SA等）。表示時は出典ページへ必ずリンクする。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_master import ROOT, api_get

OUT = ROOT / "data/raw/wikidata/extras.json"

IMAGE_PROPS = [  # (プロパティ, 種別キー)。この順で表示される
    ("P18", "main"), ("P4291", "panorama"), ("P3451", "night"),
    ("P8592", "aerial"), ("P5252", "winter"), ("P2716", "collage"),
]


def all_values(ent: dict, prop: str):
    return [c["mainsnak"]["datavalue"]["value"]
            for c in ent.get("claims", {}).get(prop, [])
            if c["mainsnak"].get("snaktype") == "value"]


def main():
    qids = [p["qid"] for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("qid")]
    extras = {}
    for i in range(0, len(qids), 50):
        ents = api_get({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
                        "props": "claims"})["entities"]
        for qid, ent in ents.items():
            elev = all_values(ent, "P2044")
            images, seen = [], set()
            for prop, kind in IMAGE_PROPS:
                for f in all_values(ent, prop):
                    if f not in seen:
                        seen.add(f)
                        images.append({"kind": kind, "file": f})
            extras[qid] = {"elevation_m": float(elev[0]["amount"]) if elev else None,
                           "images": images}
        print(f"fetched {min(i + 50, len(qids))}/{len(qids)}", flush=True)

    OUT.write_text(json.dumps(extras, ensure_ascii=False, indent=1), encoding="utf-8")
    n_elev = sum(1 for v in extras.values() if v["elevation_m"] is not None)
    n_img = sum(1 for v in extras.values() if v["images"])
    n_multi = sum(1 for v in extras.values() if len(v["images"]) > 1)
    total = sum(len(v["images"]) for v in extras.values())
    print(f"標高: {n_elev}/{len(extras)}, 画像あり: {n_img}/{len(extras)} "
          f"(計{total}枚, 2枚以上: {n_multi}件) -> {OUT}")


if __name__ == "__main__":
    main()
