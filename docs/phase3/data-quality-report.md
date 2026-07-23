# フェーズ3 データ品質レポート

- 生成日：2026-07-16 ／ 対象：`data/output/places.json`（154件、スキーマ検証済み） ／ 生成: `scripts/quality_report.py`

## 1. カバレッジ（充足率）

母数はroute除く152件。nullは「該当なし・未取得」。

| ブロック.フィールド | 充足 | 率 |
| --- | --- | --- |
| geography.elevation_m | 123/152 | 81% |
| geography.population | 140/152 | 92% |
| poi.dining_5km | 152/152 | 100% |
| osm_features.viewpoints_5km | 152/152 | 100% |
| heritage.whs_within_30km | 152/152 | 100% |
| climate.monthly | 152/152 | 100% |
| access.nearest_airport | 152/152 | 100% |
| recognition.wikipedia_views_ja_year | 140/152 | 92% |
| recognition.wikipedia_views_en_year | 149/152 | 98% |
| recognition.wikipedia_views_ja_monthly | 140/152 | 92% |
| safety.mofa_risk_level | 152/152 | 100% |
| media.images | 150/152 | 99% |
| holidays.monthly_counts | 152/152 | 100% |
| daylight.monthly | 152/152 | 100% |
| economy.pli_total | 152/152 | 100% |
| country_info.official_languages_ja | 152/152 | 100% |

## 2. 妥当性スポットチェック（既知の事実との突合）

| 項目 | 値 | 期待範囲 | 判定 |
| --- | --- | --- | --- |
| パリの飲食店数(5km) | 34446 | 5000〜50000 | ✅ |
| パリの7月平均気温 | 20.5 | 17〜24 | ✅ |
| ツェルマットの標高 | 1624.0 | 1400〜1800 | ✅ |
| セビリアの7月平均気温 | 28.1 | 25〜31 | ✅ |
| セビリアの7月降水量 | 1.4 | 0〜15 | ✅ |
| ロンドンのja年間閲覧数 | 164237 | 100000〜5000000 | ✅ |
| ドブロブニクの世界遺産5km圏 | 1 | 1〜10 | ✅ |
| バイブリー(村)の飲食店数(5km) | 20 | 1〜200 | ✅ |

## 3. 外れ値検出（settlementコホート）

- 検出なし

## 4. 既知の制約

1. **山岳部の気温**：ERA5はグリッド（約25km四方）平均のため、山岳の町では実際より低温に出る（例：ツェルマット1月）。都市間比較には使えるが絶対値表示は注意。
2. **日照時間は近似値**：日射量(ssrd)からの換算のため、晴天の多い地域で過大になる場合がある。
3. **POIはFoursquare OS Places由来**（2026-07-09版・閉店除外済み）。OSMは自然地物・展望地点・歩行者エリア（osm_features）のみで、同ブロックには登録密度の地域差（小さな町で過少）が残る。Foursquareの月次更新への追随は再取得経路の確認が前提（調査レポート§4）。
4. **安全情報は国単位**：都市固有のレベルではない（granularity=countryを明示済み）。
5. **Eurostat宿泊統計（nights_spent_nuts2）は未整備**（NUTS2対応表が必要。設計書§7）。
6. **coastal（海岸判定）は未実装**（osm_features.coastline_10kmで代替可能）。
7. **scenic_natureの重みは要調整**：湖沼カウントが小さな池も拾い、都市部の展望台が山岳景観と同列に効くため、上位に都市が混ざる（例：アベイロ・プラハ）。事実データは正しく、式の重み（設計書§4.2）の調整で対応可能。旅行知見でのチューニングを推奨。
8. **画像（media.images）はライセンスが画像ごとに異なる**：Wikidata経由のWikimedia Commons画像はCC0ではない（CC BY-SA等）。表示時は image_source_url（出典ページ）へのリンクを必ず併記する（ビュワーは対応済み）。また画像・地図の表示には閲覧側ブラウザの外部接続が必要。
9. **国単位ブロック（holidays / economy / country_info の公用語）は同一国内で同じ値**：生データは国単位で保持し、ビルド時に各地点へ展開している（granularity で明示）。祝日は全国区＋その地点の州・地域の祝日（Wikidata行政区分チェーンでISO 3166-2に紐付けて判定）。物価水準（PLI）は年次・EU27=100の相対値で変動は小さく年1回の更新で十分。日照時間は各月15日時点の天文計算値。

## 5. 判定

- スキーマ検証：全154件通過
- 妥当性チェック：8/8 通過
- 外れ値：0件（上記参照）
