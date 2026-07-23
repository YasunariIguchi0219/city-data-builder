#!/usr/bin/env python3
"""フェーズ3: 全地点のWikipedia年間閲覧数（ja/en・2025年）を取得する。
- 入力: data/raw/wikidata/sitelinks.json（記事タイトル）
- 出力: data/raw/pageviews/views_2025.json （QID → {ja, en}）
- 途中保存あり（再実行時は未取得分のみ照会）。約300リクエスト・毎秒1件ペース。
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITELINKS = ROOT / "data/raw/wikidata/sitelinks.json"
OUT = ROOT / "data/raw/pageviews/views_2025.json"
UA = {"User-Agent": "city-data-builder/0.1 (fetch; batch, sequential)"}
START, END, YEAR = "20250101", "20251231", "2025"


def yearly_views(project: str, title: str):
    """(年間合計, 月別12要素) を返す。月別は認知度の季節性（例: クリスマスマーケット都市の12月）に使う。
    注意: monthly粒度はAPI側に欠損がある（例: ウィーン×user×2025のみ404）ため、
    daily粒度で取得して自前で月次集計する（1記事1リクエストのまま）。"""
    t = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"{project}/all-access/user/{t}/daily/{START}/{END}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                monthly = [0] * 12
                for i in json.load(r)["items"]:
                    monthly[int(i["timestamp"][4:6]) - 1] += i["views"]
                return sum(monthly), monthly
        except urllib.error.HTTPError as e:
            if e.code == 404:  # 記事はあるが期間内の閲覧データなし
                return 0, [0] * 12
            time.sleep(5 * (attempt + 1))
        except Exception:  # noqa: BLE001
            time.sleep(5)
    return None, None


def main():
    sitelinks = json.loads(SITELINKS.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    views = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    for i, (qid, sl) in enumerate(sitelinks.items(), 1):
        cur = views.get(qid, {})
        changed = False
        for lang, key in (("ja", "jawiki"), ("en", "enwiki")):
            title = sl.get(key)
            # 取得成功済み（または記事なし確定）のみスキップ。None（一時的な失敗）は再試行する
            done = f"{lang}_monthly" in cur and (cur[f"{lang}_monthly"] is not None or not title)
            if done:
                continue
            if title:
                total, monthly = yearly_views(f"{lang}.wikipedia", title)
            else:
                total, monthly = None, None
            cur[lang], cur[f"{lang}_monthly"] = total, monthly
            changed = True
            time.sleep(1.0)
        views[qid] = cur
        if changed:
            OUT.write_text(json.dumps(views, ensure_ascii=False, indent=1), encoding="utf-8")
        if i % 20 == 0 or i == len(sitelinks):
            print(f"{i}/{len(sitelinks)}", flush=True)

    ja = sum(1 for v in views.values() if v.get("ja") is not None)
    en = sum(1 for v in views.values() if v.get("en") is not None)
    print(f"閲覧数取得: ja {ja}件 / en {en}件 -> {OUT}")


if __name__ == "__main__":
    main()
