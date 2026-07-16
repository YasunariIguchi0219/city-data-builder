#!/usr/bin/env python3
"""フェーズ1調査: Wikimedia Pageviews API の取得テスト（再現用）。
記事別・月別の閲覧数が取得できること、都市の知名度差が数値に表れることを確認する。
データはCC0。User-Agentヘッダ必須。
"""
import json
import urllib.parse
import urllib.request

UA = {"User-Agent": "city-data-builder/0.1 (survey)"}


def yearly_views(project: str, title: str, start="2025010100", end="2025123100"):
    t = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"{project}/all-access/user/{t}/monthly/{start}/{end}")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        items = json.load(r)["items"]
    return sum(i["views"] for i in items), len(items)


if __name__ == "__main__":
    tests = [("ja.wikipedia", "パリ"), ("en.wikipedia", "Paris"),
             ("ja.wikipedia", "ヴェルナッツァ"), ("en.wikipedia", "Vernazza"),
             ("ja.wikipedia", "ローテンブルク・オプ・デア・タウバー"),
             ("en.wikipedia", "Stow-on-the-Wold")]
    for proj, title in tests:
        total, months = yearly_views(proj, title)
        print(f"{proj} / {title}: 2025年計 {total:,} views ({months}ヶ月分)")
