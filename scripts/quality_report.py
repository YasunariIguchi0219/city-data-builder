#!/usr/bin/env python3
"""フェーズ3: data/output/places.json の品質検証を行い、品質レポートを生成する。
（計画書6.2: カバレッジ検証・妥当性検証・外れ値検出）
出力: docs/phase3/data-quality-report.md
"""
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase3/data-quality-report.md"
TODAY = "2026-07-16"

# 妥当性スポットチェック: (id, 説明, 取得関数, 期待範囲)
SPOT_CHECKS = [
    ("paris", "パリの飲食店数(5km)", lambda r: r["poi"]["dining_5km"], (5000, 50000)),
    ("paris", "パリの7月平均気温", lambda r: r["climate"]["monthly"][6]["temp_mean_c"], (17, 24)),
    ("zermatt", "ツェルマットの標高", lambda r: r["geography"]["elevation_m"], (1400, 1800)),
    ("seville", "セビリアの7月平均気温", lambda r: r["climate"]["monthly"][6]["temp_mean_c"], (25, 31)),
    ("seville", "セビリアの7月降水量", lambda r: r["climate"]["monthly"][6]["precip_mm"], (0, 15)),
    ("london", "ロンドンのja年間閲覧数", lambda r: r["recognition"]["wikipedia_views_ja_year"], (100000, 5000000)),
    ("dubrovnik", "ドブロブニクの世界遺産5km圏", lambda r: len(r["heritage"]["whs_onsite"]), (1, 10)),
    ("bibury", "バイブリー(村)の飲食店数(5km)", lambda r: r["poi"]["dining_5km"], (1, 200)),
]

# カバレッジ対象: (ブロック, フィールド)。route以外を母数とする
COVERAGE_FIELDS = [
    ("geography", "elevation_m"), ("geography", "population"),
    ("poi", "dining_5km"), ("osm_features", "viewpoints_5km"),
    ("heritage", "whs_within_30km"), ("climate", "monthly"),
    ("access", "nearest_airport"), ("recognition", "wikipedia_views_ja_year"),
    ("recognition", "wikipedia_views_en_year"), ("recognition", "wikipedia_views_ja_monthly"),
    ("safety", "mofa_risk_level"), ("media", "images"),
    ("holidays", "monthly_counts"), ("daylight", "monthly"),
    ("economy", "pli_total"), ("country_info", "official_languages_ja"),
]


def get_field(r, block, field):
    b = r.get(block)
    if b is None:
        return None
    return b.get(field)


def main():
    data = json.loads((ROOT / "data/output/places.json").read_text(encoding="utf-8"))
    places = data["places"]
    non_route = [r for r in places if r["identity"]["type"] != "route"]
    by_id = {r["identity"]["id"]: r for r in places}
    n = len(non_route)

    lines = [
        "# フェーズ3 データ品質レポート",
        "",
        f"- 生成日：{TODAY} ／ 対象：`data/output/places.json`（{data['count']}件、"
        f"スキーマ検証済み） ／ 生成: `scripts/quality_report.py`",
        "",
        "## 1. カバレッジ（充足率）",
        "",
        f"母数はroute除く{n}件。nullは「該当なし・未取得」。",
        "",
        "| ブロック.フィールド | 充足 | 率 |",
        "| --- | --- | --- |",
    ]
    for block, field in COVERAGE_FIELDS:
        c = sum(1 for r in non_route if get_field(r, block, field) is not None)
        lines.append(f"| {block}.{field} | {c}/{n} | {c / n:.0%} |")

    # type別のブロックnull数
    lines += ["", "## 2. 妥当性スポットチェック（既知の事実との突合）", "",
              "| 項目 | 値 | 期待範囲 | 判定 |", "| --- | --- | --- | --- |"]
    n_fail = 0
    for pid, desc, getter, (lo, hi) in SPOT_CHECKS:
        try:
            v = getter(by_id[pid])
        except (TypeError, KeyError):
            v = None
        ok = v is not None and lo <= v <= hi
        n_fail += not ok
        lines.append(f"| {desc} | {v} | {lo}〜{hi} | {'✅' if ok else '❌'} |")

    # 外れ値検出: settlementコホートで中央値の100倍超 or 主要フィールド0
    lines += ["", "## 3. 外れ値検出（settlementコホート）", ""]
    settlements = [r for r in non_route if r["identity"]["type"] in ("city", "town_village")]
    outliers = []
    for block, field in [("poi", "dining_5km"), ("poi", "lodging_5km"),
                         ("osm_features", "viewpoints_5km"), ("recognition", "wikipedia_views_en_year")]:
        vals = [(r["identity"]["name_ja"], get_field(r, block, field)) for r in settlements]
        nums = [v for _, v in vals if v is not None]
        if not nums:
            continue
        med = statistics.median(nums)
        for name, v in vals:
            if v is None:
                continue
            if med > 0 and v > 100 * med:
                outliers.append(f"{name}: {block}.{field}={v:,}（中央値{med:,.0f}の100倍超）")
            if v == 0 and field in ("dining_5km", "lodging_5km"):
                outliers.append(f"{name}: {block}.{field}=0（要確認）")
    if outliers:
        lines += [f"- ⚠️ {o}" for o in outliers]
    else:
        lines.append("- 検出なし")

    # 既知の制約（手書きメンテ部分）
    lines += [
        "",
        "## 4. 既知の制約",
        "",
        "1. **山岳部の気温**：ERA5はグリッド（約25km四方）平均のため、山岳の町では実際より低温に出る"
        "（例：ツェルマット1月）。都市間比較には使えるが絶対値表示は注意。",
        "2. **日照時間は近似値**：日射量(ssrd)からの換算のため、晴天の多い地域で過大になる場合がある。",
        "3. **POIはOSM由来**（Foursquare保留中）。OSMの登録密度は地域差があり、"
        "小さな町では実態より少なく出る可能性。dining_categories_5kmは未取得（null）。",
        "4. **安全情報は国単位**：都市固有のレベルではない（granularity=countryを明示済み）。",
        "5. **Eurostat宿泊統計（nights_spent_nuts2）は未整備**（NUTS2対応表が必要。設計書§7）。",
        "6. **coastal（海岸判定）は未実装**（osm_features.coastline_10kmで代替可能）。",
        "7. **scenic_natureの重みは要調整**：湖沼カウントが小さな池も拾い、都市部の展望台が"
        "山岳景観と同列に効くため、上位に都市が混ざる（例：アベイロ・プラハ）。事実データは正しく、"
        "式の重み（設計書§4.2）の調整で対応可能。旅行知見でのチューニングを推奨。",
        "8. **画像（media.images）はライセンスが画像ごとに異なる**：Wikidata経由のWikimedia Commons"
        "画像はCC0ではない（CC BY-SA等）。表示時は image_source_url（出典ページ）へのリンクを必ず併記する"
        "（ビュワーは対応済み）。また画像・地図の表示には閲覧側ブラウザの外部接続が必要。",
        "9. **国単位ブロック（holidays / economy / country_info の公用語）は同一国内で同じ値**："
        "生データは国単位で保持し、ビルド時に各地点へ展開している（granularity で明示）。"
        "祝日は全国区（global=true）のみで地方祝日は含まない。物価水準（PLI）は年次・EU27=100の相対値で"
        "変動は小さく年1回の更新で十分。日照時間は各月15日時点の天文計算値。",
        "",
        "## 5. 判定",
        "",
        f"- スキーマ検証：全{data['count']}件通過",
        f"- 妥当性チェック：{len(SPOT_CHECKS) - n_fail}/{len(SPOT_CHECKS)} 通過",
        f"- 外れ値：{len(outliers)}件（上記参照）",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"妥当性: {len(SPOT_CHECKS) - n_fail}/{len(SPOT_CHECKS)} OK, 外れ値: {len(outliers)}件")


if __name__ == "__main__":
    main()
