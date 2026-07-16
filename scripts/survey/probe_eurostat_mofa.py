#!/usr/bin/env python3
"""フェーズ1調査: Eurostat観光統計APIと外務省オープンデータの取得テスト（再現用）。
- Eurostat: NUTS2地域単位の宿泊者数(tour_occ_nin2)がREST APIで取れることを確認
- 外務省: 海外安全情報オープンデータ（国別XML）の存在確認
"""
import json
import urllib.request

UA = {"User-Agent": "city-data-builder/0.1 (survey)"}


def eurostat_test():
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_occ_nin2"
           "?format=JSON&lang=EN&time=2023&geo=ES61&geo=FR10&unit=NR&c_resid=TOTAL&nace_r2=I551-I553")
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
    print("Eurostat tour_occ_nin2 (2023, 宿泊数):")
    print(" 地域:", d["dimension"]["geo"]["category"]["label"], "値:", d.get("value"))


def mofa_test():
    url = "https://www.ezairyu.mofa.go.jp/html/opendata/index.html"
    html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace")
    n_xml = html.count(".xml")
    print(f"外務省オープンデータ: index取得OK、XMLリンク {n_xml}件を確認")


if __name__ == "__main__":
    eurostat_test()
    mofa_test()
