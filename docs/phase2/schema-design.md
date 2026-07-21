# フェーズ2 データ構造設計書

- 作成日：2026年7月16日
- ステータス：**承認済み（2026-07-16）**。§7の残論点（4〜6）はフェーズ3の中で扱う
- 形式定義：[schema/place.schema.json](../../schema/place.schema.json)
- サンプル：フェーズ3完了に伴い全件データ（`data/output/places.json`）へ置き換え済み（設計時は パリ・オビドス・シヨン城 の3件で検証した）
- 前提：フェーズ1調査の採用判定（[phase1/data-source-survey.md](../phase1/data-source-survey.md)）に従う

## 1. 設計原則

1. **提案体験からの逆算**：お客様の回答（旅の醍醐味・スタイル・時期・経験・自由記述）から必要な指標を定義し、指標から必要な事実データを定義する（§4のマッピング表が本設計の中核）。
2. **事実と指標の2層分離**：Layer 1（事実：実測値そのもの）と Layer 2（指標：提案ロジック用の比較値）を分け、指標は必ず事実から再計算可能にする。「初心者向き」のような主観ラベルは持たない。
3. **出所リネージ**：すべてのデータブロックに `_meta`（ソース・取得日・ライセンス・帰属表示文）を、すべての指標に `depends_on`（依存ソース）を付ける。
4. **ソース分離（ODbL対応）**：OSM由来データは専用ブロック `osm_features` に物理隔離し、他ソースと同一項目内で混合しない。OSMがNGになった場合は `osm_features` と、`depends_on` に `osm` を含む指標だけを無効化・再計算すれば済む。
5. **null規約**：`null` =「該当なし・未取得」（0とは区別する）。`type` により適用外のブロックはブロックごと `null`（§6の適用マトリクス参照）。

## 2. レコード構造（place）

1地点 = 1レコード。ブロック単位でソースが揃うよう構成する。

```
place
├── identity        # 名寄せマスタ由来（フェーズ0で整備済み）
├── geography       # 人口・標高・地形       ← Wikidata (CC0)
├── poi             # カテゴリ別POI数        ← Foursquare OS Places (Apache 2.0)
├── osm_features    # 展望地点・自然・歩行者エリア ← OpenStreetMap (ODbL) ※物理隔離
├── heritage        # 世界遺産               ← Wikidata (CC0)
├── climate         # 月別気候（12ヶ月×4指標） ← Copernicus ERA5
├── access          # 空港・都市間距離        ← OurAirports (PD) + 自前計算
├── recognition     # 認知度                 ← Wikimedia Pageviews (CC0) + Eurostat (CC BY)
├── safety          # 渡航安全情報            ← 外務省オープンデータ
├── holidays        # 祝日（月別・国単位）    ← Nager.Date (MIT)
├── daylight        # 昼の長さ（月別）        ← 座標からの天文計算
├── economy         # 物価水準（国単位・年次） ← Eurostat PLI (CC BY)
├── country_info    # 公用語・日本の在外公館   ← Wikidata (CC0)
├── media           # 画像群（表示用）        ← Wikidata画像プロパティ経由のWikimedia Commons
├── indicators      # Layer 2 派生指標（§5）
└── meta            # レコード全体のメタ（スキーマ版・生成日時）
```

### 2.1 ブロック別フィールド定義（Layer 1：事実）

**identity**（フェーズ0マスタ。詳細は [phase0/data-dictionary.md](../phase0/data-dictionary.md)）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| id / name_ja / name_en / qid / country / type / lat / lon | — | マスタから転記 |
| base_place_id | string?null | **single_poi・natural_feature用**：最寄りの拠点都市のid（例：シヨン城→montreux ※154件外も可、その場合はnullで名称のみnoteに） |

**geography**（Wikidata）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| population | int?null | 人口（P1082、preferredランク優先） |
| population_date | string?null | 人口の時点 |
| elevation_m | number?null | 標高（P2044） |
| coastal | bool?null | 海岸線から10km以内（座標から計算） |

**poi**（Foursquare OS Places。**半径固定の件数**として持つ——面積データ不要で全typeを比較可能にするため）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| radius_km | number | 集計半径（既定5km。徒歩圏系は1km） |
| dining_5km | int?null | 飲食店（restaurant/cafe/bar等） |
| dining_categories_5km | int?null | 飲食のユニークカテゴリ数（食の多様性） |
| culture_5km | int?null | 美術館・ギャラリー・劇場・コンサートホール |
| nightlife_5km | int?null | ナイトライフ施設 |
| shopping_5km | int?null | 商業施設・市場 |
| wellness_5km | int?null | スパ・温泉 |
| lodging_5km | int?null | 宿泊施設 |
| dining_1km / culture_1km / shopping_1km | int?null | 徒歩圏（散策性の材料） |

**osm_features**（OpenStreetMap。ODbL隔離ブロック——poiと項目を重複させない）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| viewpoints_5km | int?null | 展望地点 |
| peaks_10km / lakes_10km / coastline_10km | int?null／bool?null | 山頂・湖・海岸線の近接 |
| protected_areas_10km | int?null | 自然保護地域 |
| hiking_routes_10km | int?null | ハイキングコース |
| ski_marina_10km | int?null | スキー場・マリーナ |
| parks_gardens_5km | int?null | 公園・庭園 |
| pedestrian_area_1km | bool?null | 歩行者エリア・旧市街の有無 |

**heritage**（Wikidata経由。UNESCO公式は不採用）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| whs_onsite | array | 地点自体・5km以内の世界遺産（qid・名称・距離km） |
| whs_within_30km | int?null | 30km以内の世界遺産数（日帰り圏） |

**climate**（ERA5。12要素の配列、1月〜12月）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| monthly[] | array(12) | { month, temp_mean_c, precip_mm, sunshine_h, humidity_pct } |
| reference_period | string | 平年値の参照期間（例 "2015-2024"）。※サンプルは暫定で単年 |

**access**（OurAirports＋自前計算）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| nearest_airport | object?null | { iata, name, type, distance_km } |
| nearest_large_airport | object?null | 同上（large_airportに限定） |
| nearest_hub_place_id | string?null | 154件中の最寄り大都市（city）のid と距離（周遊・拠点判定用） |

**recognition**（Pageviews＋sitelinks＋Eurostat）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| wikipedia_views_ja_year | int?null | ja記事の年間閲覧数（**日本人の認知度**） |
| wikipedia_views_en_year | int?null | en記事の年間閲覧数（国際的認知度） |
| wikipedia_sitelinks | int?null | 記事のある言語版数 |
| views_year | string?null | 集計対象年 |
| nights_spent_nuts2 | int?null | 所属NUTS2地域の年間宿泊数（Eurostat。**地域粒度**であることに注意） |

**safety**（外務省）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| mofa_risk_level | int?null | 危険情報レベル 0〜4（**国・地域単位の値を割り当て**） |
| granularity | string | "country"（粒度の明示） |

**holidays**（Nager.Date。全国区＋**その地点の州・地域に適用される地域祝日**）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| reference_year | int | 参照年（祝日は年ごとに日付が変わるが月別分布はほぼ安定） |
| monthly_counts[12] | array | 月別の祝日数。全国区に加え、地点の地域コード（Wikidata P131→P300で取得したISO 3166-2）に合致する地域祝日を含む（例：ミュンヘンはバイエルン州祝日込み） |
| total / granularity | int / enum | 年間合計／"region"（地域込みで判定）または "country"（地域コードが取れなかった地点） |

**daylight**（座標からの天文計算。ソース分離の原則によりclimate（ERA5）とは別ブロック）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| monthly[12] | array | { month, daylight_h }。各月15日時点の昼の長さ（時間）。冬の欧州の観光可能時間の判断材料 |

**economy**（Eurostat PLI。**国単位・年次**。相対値のため変動小・年1回更新で十分）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| pli_total | number?null | 物価水準指数・総合（実質個人消費、EU27=100） |
| pli_restaurants_hotels | number?null | 同・外食＋宿泊（旅行者の体感物価に近い） |
| pli_base / pli_year / granularity | string | 基準（EU27_2020=100）／データ年／"country" |

**country_info**（Wikidata。公用語は国単位、最寄り公館の距離のみ地点単位）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| official_languages_ja[] | array | 公用語（日本語表記） |
| jp_missions_in_country[] | array | 国内にある日本の在外公館の名称 |
| nearest_jp_mission | object?null | 最寄りの日本公館 { label, city, country, distance_km（直線距離） }。国境を跨ぐ場合あり。**Wikidataに座標登録のある公館のみが距離計算の対象**（例：サラエボの日本大使館は座標未登録のため、jp_missions_in_country には載るが nearest には出ない） |

**media**（Wikidataの画像プロパティ経由のWikimedia Commons画像。**表示用であり指標には使わない**）

| フィールド | 型 | 内容 |
| --- | --- | --- |
| images[] | array | { kind, commons_file, image_url, image_source_url }。kindは main（代表）/ panorama / night / aerial / winter / collage |
| — | — | ⚠️ **画像ファイル自体のライセンスはCC0ではなく画像ごとに異なる**（CC BY-SA等）。表示時は image_source_url（Commonsの出典ページ）へのリンクを必ず併記する |

**\_meta（全ブロック共通）**

| フィールド | 型 | 内容 |
| --- | --- | --- |
| source | string | ソース識別子（wikidata / fsq_os_places / osm / era5 / ourairports / wikimedia_pageviews / eurostat / mofa / computed） |
| license | string | ライセンス（CC0 / Apache-2.0 / ODbL-1.0 / …） |
| attribution | string?null | 帰属表示文（例 "© OpenStreetMap contributors"） |
| retrieved_at | string | 取得日（ISO 8601） |

## 3. 質問回答 → 指標マッピング表（提案体験からの逆算）

### 3.1 旅の醍醐味

| お客様の回答 | 使用する指標（Layer 2） | 使用する事実（Layer 1） | ソース |
| --- | --- | --- | --- |
| 絶品グルメを味わう | food_scene | poi.dining_5km, dining_categories_5km | fsq |
| 感性を揺さぶる体験 | culture_scene | poi.culture_5km | fsq |
| 絶景に息をのむ | scenic_nature | osm_features.viewpoints/peaks/lakes/coastline, geography.elevation_m | osm, wikidata |
| 最高の景色を写真に | scenic_nature ＋ historic_depth | 上記＋heritage, osm_features.pedestrian_area | osm, wikidata |
| 思いっきり体を動かす | outdoor_activity | osm_features.hiking/ski_marina/parks, climate.monthly（季節適合） | osm, era5 |
| 非日常にどっぷり浸る | （検討中※1） | climate・geography・recognition の組合せ | 複合 |
| 歴史を肌で感じる | historic_depth | heritage.whs_*, poi.culture_5km | wikidata, fsq |
| 街を自由に散策 | walkability | poi.*_1km, osm_features.pedestrian_area_1km | fsq, osm |

※1 「非日常」は日本の日常環境との差の定義が必要（気候差・地形差・認知度の低さ等）。フェーズ2レビューの論点。

### 3.2 旅のスタイル

| お客様の回答 | 指標 | 事実 | ソース |
| --- | --- | --- | --- |
| ワイワイ | vibrancy | poi.nightlife_5km, dining_5km | fsq |
| ロマンチック | （複合※2） | osm_features.viewpoints/lakes/coastline/parks_gardens, pedestrian_area | osm |
| リラックス | tranquility | poi.wellness_5km, osm_features.parks/protected_areas, poi密度の低さ | fsq, osm |
| ディスカバリー | hidden_gem | recognition（低）×充実度（高）（§5.3） | 複合 |
| ディープ | （検討中※2） | 特定カテゴリの特化度（poiカテゴリ分布の偏り） | fsq |

※2 「ロマンチック」「ディープ」は事実の組合せ方に主観が入りやすい。まず構成要素（Layer 1）を揃え、合成はLLM側の判断に委ねる案もある（§7論点）。

### 3.3 旅の時期

| お客様の回答 | 指標 | 事実 | ソース |
| --- | --- | --- | --- |
| 春・夏・秋・冬 | seasonal_comfort[12] | climate.monthly（4指標） | era5 |
| おまかせ | best_months | seasonal_comfort の上位月 | era5 |
| （時期の補助材料） | — 事実のみ提供 | holidays.monthly_counts（現地連休の混雑・休業）、daylight.monthly（観光可能時間）、recognition.wikipedia_views_*_monthly（関心の季節性：クリスマスマーケット等） | nager_date, computed, pageviews |

### 3.4 旅行経験

| お客様の回答 | 指標 | 事実 | ソース |
| --- | --- | --- | --- |
| ビギナー寄り | ease_of_access（事実の束※3） | access.nearest_airport距離, recognition, poi.lodging_5km, safety, country_info（公用語・最寄り日本公館距離） | ourairports, pageviews, fsq, mofa, wikidata |
| ベテラン寄り | 同上（逆向きに使う） | 同上＋access.nearest_hub距離 | 同上 |

※3 note.mdの指示どおり「初心者向き」ラベルは付与せず、確認可能な事実（空港距離・宿泊施設数・認知度・安全情報）を並べて提供し、判断はロジック/LLM側で行う。

### 3.5 自由記述

| 記述例 | 使用するデータ |
| --- | --- |
| パリには行きたい | identity（名称・国） |
| 治安のよい街がいい | safety.mofa_risk_level |
| 予算を抑えたい／物価が心配 | economy.pli_total, pli_restaurants_hotels（国単位） |
| 移動は少なめにしたい | access.nearest_airport / nearest_hub、都市間距離行列（§7） |
| 有名すぎない穴場 | hidden_gem（§5.3） |
| 特になし | 追加データなし |

## 4. Layer 2：指標の定義

### 4.1 正規化の方式

- 生の件数は都市規模で桁が違うため、**同一コホート内のパーセンタイル順位（0〜100）**に正規化する。
- コホートは `type` で分ける：city / town_village は共通コホート「settlement」、single_poi・natural_feature は原則対象外（構成要素の事実のみ提供）、route は全指標対象外。
- 元の実数値は常にLayer 1に残っているため、正規化方式の変更はいつでも再計算可能。

### 4.2 指標カタログ

| 指標 | 算出式（要旨） | depends_on | 状態 |
| --- | --- | --- | --- |
| food_scene | pct(dining_5km) と pct(dining_categories_5km) の平均 | fsq | 確定案 |
| culture_scene | pct(culture_5km) | fsq | 確定案 |
| scenic_nature | pct(viewpoints_5km + peaks/lakes/coastline/protected近接の重み和) | **osm**, wikidata | 確定案 |
| outdoor_activity | pct(hiking+ski_marina+parks) ※季節はclimateと併用 | **osm**, era5 | 確定案 |
| historic_depth | pct(whs_onsite×2 + whs_within_30km) | wikidata | 確定案 |
| walkability | pct(dining_1km+culture_1km+shopping_1km) + pedestrian_areaボーナス | fsq, **osm** | 確定案 |
| vibrancy | pct(nightlife_5km) | fsq | 確定案 |
| tranquility | pct(wellness+parks+protected) − pct(dining_5km)の混雑補正 | fsq, **osm** | 要検討 |
| recognition_jp | pct(wikipedia_views_ja_year)（ja記事なしはen×補正で代替） | pageviews | 確定案 |
| hidden_gem | §5.3 | 複合 | 確定案 |
| seasonal_comfort[12] | 月別：気温の快適帯（8〜27℃で台形スコア）×0.5 ＋ 低降水×0.3 ＋ 日照×0.2 | era5 | 確定案（係数は要調整） |
| ease系（事実の束） | 指標化せず事実をそのまま提供 | 複合 | 確定（方針） |

**太字（osm）を含む指標は、OSM無効化時に自動で再計算対象になる**（§1原則4）。

### 4.3 hidden_gem（穴場）の定義

note.mdの「認知度は低い＋希望との一致度が高い＋一定以上の充実度」を分解し、**前段の2条件だけ**をデータ側で持つ：

```
hidden_gem = (100 − recognition_jp) × 充実度ゲート
充実度ゲート = 1 if（dining_5km・lodging_5km・culture_5km または scenic_nature が
                settlement コホート下位25%を上回る）else 0
```

「希望との一致度」は提案時にお客様の回答と掛け合わせる部分なので、データではなく提案ロジック側の責務とする。

## 5. type別 適用マトリクス

| ブロック | city / town_village | single_poi | natural_feature | route |
| --- | --- | --- | --- | --- |
| identity | ✅ | ✅（＋base_place_id） | ✅（＋base_place_id） | ✅（＋endpoints） |
| geography | ✅ | 一部（標高のみ） | 一部（標高のみ） | null |
| poi / osm_features | ✅ | ✅（周辺5kmとして） | ✅（同左） | null |
| heritage | ✅ | ✅ | ✅ | null |
| climate | ✅ | ✅ | ✅ | null |
| access | ✅ | ✅ | ✅ | null |
| recognition | ✅ | ✅（Eurostatはnull） | 同左 | null |
| safety | ✅ | ✅ | ✅ | null |
| holidays / economy / country_info | ✅（国単位の値を展開） | ✅（同左） | ✅（同左） | null |
| daylight | ✅ | ✅ | ✅ | null |
| media | ✅ | ✅ | ✅ | null |
| indicators | ✅ | 事実のみ・指標はnull | 同左 | null |

## 6. 検証（フェーズ3で使用）

- **形式検証**：`schema/place.schema.json`（JSON Schema 2020-12）に全レコードが適合すること
- **null規約検証**：type別マトリクスに反するnull/非nullがないこと
- **妥当性検証・外れ値検出**：計画書6.2のとおり（品質レポートに記載）

## 7. 設計レビューの論点（未決事項）

1. ~~**「非日常」「ロマンチック」「ディープ」の扱い**~~ → **決定（2026-07-16）：合成指標は作らず、構成要素の事実（Layer 1）のみ提供し、組合せの判断はLLM側に委ねる**（合成式の主観性を避け、note.mdの「事実に接地」方針に沿う）
2. ~~**POI集計半径**~~ → **決定（2026-07-16）：5km固定＋徒歩圏1kmの仮置きで進める**。フェーズ3パイロットで半径3/5/10kmの順位逆転を検証し、問題があれば補正を検討
3. **seasonal_comfortの係数**（快適帯8〜27℃、重み0.5/0.3/0.2）は仮置き。旅行商品の知見での調整余地
4. **base_place_id**：単体スポットの拠点都市が154件外の場合の扱い（例：シヨン城→モントルー）
5. **Eurostat宿泊数**：NUTS2粒度のまま載せるか、参考値として指標から外すか
6. **気候平年値の参照期間**：直近10年（2015-2024）を提案。サンプルは暫定で2024年単年
