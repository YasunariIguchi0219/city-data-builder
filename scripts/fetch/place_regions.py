#!/usr/bin/env python3
"""データ拡張: 各地点の行政区分コード（ISO 3166-2、例: DE-BY, GB-ENG）をWikidataから取得する。
地点QIDから P131（上位行政区）を国レベルまで遡り、途中の区分が持つ P300（ISO 3166-2）を集める。
祝日の地域判定（州祝日がその地点に適用されるか）に使う。
出力: data/raw/wikidata/place_regions.json （place_id → [コード…]）
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_master import ROOT, api_get

OUT = ROOT / "data/raw/wikidata/place_regions.json"
MAX_DEPTH = 8


def claims_first(ent, prop):
    for c in ent.get("claims", {}).get(prop, []):
        if c["mainsnak"].get("snaktype") == "value":
            return c["mainsnak"]["datavalue"]["value"]
    return None


def claims_all(ent, prop):
    return [c["mainsnak"]["datavalue"]["value"]
            for c in ent.get("claims", {}).get(prop, [])
            if c["mainsnak"].get("snaktype") == "value"]


def main():
    places = [p for p in json.loads(
        (ROOT / "data/master/places_master.json").read_text(encoding="utf-8"))["places"]
        if p.get("qid")]
    codes = {p["id"]: set() for p in places}
    current = {p["id"]: {p["qid"]} for p in places}   # 次に調べるエンティティ群（P131は複数親がありうるため全て辿る）
    visited = {p["id"]: {p["qid"]} for p in places}   # ループ防止

    for depth in range(MAX_DEPTH):
        qids = sorted({q for qs in current.values() for q in qs})
        if not qids:
            break
        ents = {}
        for i in range(0, len(qids), 50):
            ents.update(api_get({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
                                 "props": "claims"})["entities"])
        nxt = {}
        for pid, qs in current.items():
            parents = set()
            for qid in qs:
                ent = ents.get(qid, {})
                for code in claims_all(ent, "P300"):
                    codes[pid].add(code)
                for parent in claims_all(ent, "P131"):
                    if parent["id"] not in visited[pid]:
                        visited[pid].add(parent["id"])
                        parents.add(parent["id"])
            if parents:
                nxt[pid] = parents
        current = nxt
        print(f"depth {depth + 1}: 残り{len(current)}地点を遡り中（対象エンティティ{len(qids)}件）", flush=True)

    OUT.write_text(json.dumps({pid: sorted(c) for pid, c in codes.items()},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for c in codes.values() if c)
    print(f"地域コードあり: {n}/{len(codes)} -> {OUT}")


if __name__ == "__main__":
    main()
