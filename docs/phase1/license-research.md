# 付録：データソース ライセンス調査（一次情報の確認記録）

- 調査日：2026年7月16日
- 方法：各ソースの公式ライセンス原文・FAQ・ガイドラインをWeb上で直接確認（根拠URLを併記）
- 前提：社内DBに統合し商用AIの提案根拠として利用。DB自体の再配布はしないが、データに基づくAI出力（提案文）は顧客に表示される
- 本文：[data-source-survey.md](data-source-survey.md) の判断根拠となる詳細記録

---

## 1. Foursquare OS Places

| 項目 | 内容 |
|---|---|
| ライセンス | **Apache License 2.0**（公式ドキュメントに明記。Hugging Faceのデータセットページでも "Apache 2.0 license" と宣言） |
| 商用利用 | **可**（Apache 2.0は商用利用・改変・再配布を許容） |
| 帰属表示 | Apache 2.0の標準義務（再配布時にライセンス文・NOTICEの保持）。CC BYのような「画面上の目立つクレジット表示」義務はなし。※Hugging Face経由のダウンロードにはゲート条件があり「利用企業名・ロゴをFoursquareがパートナー紹介・マーケティングに使うことへの同意」を求められる点に注意 |
| 再配布・加工 | 可（ライセンス文保持が条件） |
| 組み合わせ制約 | なし（share-alikeなし。OSM等と混ぜてもApache 2.0側からの汚染はない） |
| 費用 | 無料 |
| 取得方法 | Places Portal（Icebergカタログ、要無料トークン）／Hugging Face `foursquare/fsq-os-places`／Snowflake Marketplace／S3（PMTiles: `s3://fsq-os-places-us-east-1/...`） |
| 更新頻度 | **月次リリース**（公式リリースノートに「monthly releases will still be available on Snowflake and Hugging Face」。HF上の最新リリース2026-07-09を確認） |
| 根拠URL | [docs.foursquare.com/data-products/docs/access-fsq-os-places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) ／ [huggingface.co/datasets/foursquare/fsq-os-places](https://huggingface.co/datasets/foursquare/fsq-os-places) ／ [リリースノート](https://docs.foursquare.com/data-products/docs/fsq-os-places-release-notes) |

## 2. OpenStreetMap（ODbL 1.0）

| 項目 | 内容 |
|---|---|
| ライセンス | **Open Database License (ODbL) 1.0** |
| 商用利用 | 可（「free to copy, distribute, transmit and adapt our data」） |
| 帰属表示 | 「OpenStreetMap」への帰属＋ODbLであることの明示（openstreetmap.org/copyright へのリンクで充足）。推奨文言: **「© OpenStreetMap contributors」** |
| share-alike | 派生DBを**公に(Publicly)利用・配布する場合のみ**発動 |
| 根拠URL | [openstreetmap.org/copyright](https://www.openstreetmap.org/copyright) ／ [ODbL原文](https://opendatacommons.org/licenses/odbl/1-0/) ／ [OSMFコミュニティガイドライン](https://osmfoundation.org/wiki/Licence/Community_Guidelines) ／ [帰属ガイドライン](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines) |

### 本プロジェクトに直結する論点（一次情報で確認済み）

**(a)(b) 派生DB vs 寄せ集めDB — Collective Database Guideline（OSMF公認）**
- 「あるデータ型（プロパティ）について、同一リージョナルカット内で**全てOSM由来か、全て非OSM由来か**のどちらかであれば、両データセットは独立とみなされ、Derivative DatabaseではなくCollective Databaseになる」
- 条件: (1) OSMデータと非OSMデータが**相互参照しない**こと（「参照はDBキーでも、特定要素を識別する他の方法でも成立する」）、(2) 非OSMデータがある型を完全置換または新規追加していること
- **含意**: 都市テーブルにOSM由来カラム（例: POI座標）とWikidata由来カラム（例: 人口）を「同一実世界オブジェクトのレコード」として並置しても、**カラム（プロパティ）単位でソースが分離**されていればCollective扱いが主張できる。ただしOSM IDと他ソースIDの相互参照・マッチング補完（OSMの欠損をFoursquareで埋める等の混合）をすると Derivative になり得る
- 根拠: [Collective Database Guideline](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Collective_Database_Guideline_Guideline)

**(c) 社内DBのshare-alike範囲 — ODbL原文 §4.5(c)**
- 「**Use of a Derivative Database internally within an organisation is not to the public** and therefore does not fall under the requirements of Section 4.4.」（組織内部利用はshare-alike対象外）
- 「Publicly」の定義: 本人または50%超所有・支配下にない者への利用。→ **JTB社内DBに留める限り、仮にDerivative Databaseになってもshare-alike公開義務は発生しない**
- ただし §4.6: Derivative Databaseから作ったProduced Workを**公に利用**した場合、派生DB全体（または差分ファイル）の機械可読コピーの提供義務が発生
- 根拠: [ODbL 1.0原文](https://opendatacommons.org/licenses/odbl/1-0/)

**(d) Produced Work**
- 定義: 「コンテンツの全部または実質的部分を利用した結果生じる著作物（画像、視聴覚資料、**テキスト**、音声など）」。判定基準は意図: 「公開物が元データの抽出を意図するものならDBであり、そうでなければProduced Work」
- **AIの提案文はテキストであり、データ抽出を意図しないためProduced Workに該当する可能性が高い**（ガイドラインはAI出力を明示していないため断定は不可）。Produced Work自体にshare-alikeは及ばないが、それが「Derivative Databaseから」作られた場合は§4.6の基礎DB提供義務が発生し得る
- 参考: 帰属ガイドラインは「ジオコーディング結果や経路案内のテキスト出力は、派生DBを構成しない限り個々の結果に帰属表示を付け続ける必要はない」とし、ML項では「予測結果はOSMデータを実質的に再現しない限り帰属不要（学習データの帰属はREADME等で）」としている — AI提案文への類推が可能
- 根拠: [Produced Work Guideline](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline)

**(e) 帰属表示**
- DBとして保持する場合: READMEなどに「OpenStreetMapへの帰属＋ODbL全文またはリンク」を含める。ユーザー向け画面に地図を出す場合はマップ隅等に表示（5秒後の折り畳み可）

## 3. Wikidata

| 項目 | 内容 |
|---|---|
| ライセンス | **CC0 1.0（パブリックドメイン）** — 「All structured data in the main, property and lexeme namespaces is made available under the Creative Commons CC0 License」を公式ページで確認 |
| 商用利用 | 可（無制限） |
| 帰属表示 | 法的義務なし（礼儀としての出典記載は任意） |
| 再配布・加工・組み合わせ | 制約なし。**混ぜても他データを汚染しない安全なソース** |
| 注意 | 構造化データ以外の名前空間のテキストはCC BY-SA 4.0 |
| 費用／更新 | 無料／リアルタイム（ダンプは定期） |
| 根拠URL | [wikidata.org/wiki/Wikidata:Licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) |

## 4. Wikimedia Pageviews API（Analytics API / AQS）

| 項目 | 内容 |
|---|---|
| データライセンス | **CC0 1.0** — アクセスポリシーに「Data provided by the API is available under the CC0 1.0 license」と明記 |
| 商用利用 | 可（CC0＋ポリシー上の明示的制限なし） |
| 帰属表示 | 不要（CC0） |
| 利用条件 | **User-Agentヘッダ必須**（「User-Agentヘッダなしのリクエストは予告なくブロックされ得る」。推奨形式: `<client name>/<version> (<contact info>)`）。逐次リクエスト推奨 |
| レート制限 | 「クライアントの識別状況とアクセスレベルに依存」とのみ記載。Wikimedia APIs全般の新制限（2026年導入、変更可能性あり）は匿名IPのみ10req/分、適正User-Agent付き200req/分、認証済み200〜2000req/分。**AQS固有の数値は未確認**（一般APIのレート制限ページはAnalytics APIを対象外と明記） |
| 費用 | 無料。バルクは dumps.wikimedia.org でも取得可 |
| 根拠URL | [アクセスポリシー](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html) ／ [Wikimedia APIs Rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits) |

## 5. UNESCO World Heritage List（whc.unesco.org）

| 項目 | 内容 |
|---|---|
| ライセンス | 独自規約（オープンライセンスではない）。「Copyright © 1992 - [年] UNESCO/World Heritage Centre. All rights reserved.」 |
| 商用利用 | **原則不可（事前の書面許諾＋有償ライセンスが必要）**。公式FAQ: 「素材をシンジケートしたい個人・組織はUNESCO/WHCから特定のXMLサブスクリプションとライセンスを取得しなければならず、**料金が発生する**」。無償なのは個人・非商用目的の書面許可のみ |
| 再配布・加工 | 「いかなるUNESCO/WHCデータの再公開もオンライン・他形式を問わず事前の書面許可が必要」「コンテンツの改変不可（書体・サイズ・色・改行のみ変更可）」「販売・ライセンス・譲渡不可」 |
| 帰属表示 | シンジケート利用ごとにwhc.unesco.orgトップと当該アイテムページへのリンク＋上記コピーライト表記 |
| 更新頻度 | 年次（世界遺産委員会後）— 規約とは別の一般知識であり公式記載は未確認 |
| 根拠URL | [whc.unesco.org/en/syndication/](https://whc.unesco.org/en/syndication/) ／ [FAQ 126](https://whc.unesco.org/en/faq/126)（※両ページとも直接取得はCloudflareにより拒否されたため、引用文は検索エンジン経由で取得した同ページの本文抜粋。**契約前に法務がブラウザで原文再確認を推奨**） |
| **代替案の妥当性** | **Wikidata経由が妥当**。世界遺産登録の事実（登録年・件名・座標等）はWikidataにCC0で構造化されており（プロパティP1435「heritage designation」等）、事実データ自体は著作権の対象外。UNESCOサイトの**記述文をコピーしない**限り、Wikidata経由の取得で規約リスクを回避できる。UNESCO DataHub（data.unesco.org whc001）も存在するが、ライセンス表記はwhc.unesco.orgのシンジケーション規約へのリンクのみで独立したオープンライセンスは確認できず（[DataHub](https://data.unesco.org/explore/dataset/whc001/?flg=en-us)） |

## 6. Copernicus ERA5（CDS）＋ Open-Meteo

**ERA5 / Licence to Use Copernicus Products**

| 項目 | 内容 |
|---|---|
| ライセンス | Licence to Use Copernicus Products（独自だが極めて寛容） |
| 商用利用 | **可**（「for any purpose in so far as it is lawful」— 複製・頒布・公衆送信・改変・他データとの結合を明示的に許可） |
| 帰属表示 | 必須。原文どおり: **「Generated using Copernicus Climate Change Service information [年]」**、改変時は **「Contains modified Copernicus Climate Change Service information [年]」**。加えて「欧州委員会もECMWFも利用結果に責任を負わない」旨の記載義務 |
| 再配布・加工 | 可（帰属表示が条件）。改変により生じた新規知財は作成者に帰属 |
| 費用／更新 | 無料（CDS登録要）／ERA5は約5日遅れで日次更新（更新頻度の公式記載はこのページでは未確認） |
| 根拠URL | [apps.ecmwf.int/datasets/licences/copernicus/](https://apps.ecmwf.int/datasets/licences/copernicus/) |

**Open-Meteo API**

| 項目 | 内容 |
|---|---|
| 無料枠 | **非商用限定を確認**。規約原文: 「You may only use the free API services for **non-commercial purposes**」→ **JTBの商用サービスでは無料枠は使えない** |
| データライセンス | CC BY 4.0（規約で「You accept to the CC-BY 4.0 licence」） |
| 商用プラン | **Standard: $29/月（100万コール）、Professional: $99/月（500万コール、Historical Weather API含む）**、Enterprise: >5,000万コール（要問い合わせ）。全プラン商用利用可、固定月額・超過課金なし |
| 根拠URL | [open-meteo.com/en/terms](https://open-meteo.com/en/terms) ／ [open-meteo.com/en/pricing](https://open-meteo.com/en/pricing)（価格数値は公式ブログ [openmeteo.substack.com](https://openmeteo.substack.com/p/api-subscriptions-for-commercial) で確認。pricingページ本体はStripe経由表示のため要最終確認） |
| 備考 | 気候平年値を一度計算して社内DBに保存する用途なら、ERA5をCDSから直接取得（無料・商用可）する方がライセンス・費用とも単純 |

## 7. OurAirports

| 項目 | 内容 |
|---|---|
| ライセンス | **パブリックドメイン**。原文: 「All data is released to the Public Domain, and comes with no guarantee of accuracy or fitness for use.」 |
| 商用利用／再配布／組み合わせ | すべて無制限（帰属は任意の推奨のみ） |
| 費用／更新 | 無料／**毎晩更新** |
| 根拠URL | [ourairports.com/data/](https://ourairports.com/data/) |

## 8. Eurostat（観光統計）

| 項目 | 内容 |
|---|---|
| ライセンス | **CC BY 4.0**（統計データ・メタデータ・刊行物） |
| 商用利用 | 可。「Reuse ... for commercial or non-commercial purposes is authorised provided the source is acknowledged」 |
| 帰属表示 | データセット: 「Source: [DOI], [取得日]」形式。変更を加えた場合はその旨の明示が必要 |
| **重要な例外** | (1) 第三者著作物（写真等）は対象外、(2) **非EU/EFTA諸国由来データ、他機関との共同刊行物、スイス・オーストリアの一部貿易データは商用再利用不可** → 欧州154都市の観光統計（tour_occ系）はEU/EFTA域内が中心なので概ね問題ないが、非EU都市を含める場合は当該系列の出所を要確認 |
| 費用／更新 | 無料（API/バルクあり）／系列による（月次〜年次） |
| 根拠URL | [ec.europa.eu/eurostat/web/main/help/copyright-notice](https://ec.europa.eu/eurostat/web/main/help/copyright-notice) |

## 9. 外務省 海外安全ホームページ

| 項目 | 内容 |
|---|---|
| ライセンス | 海外安全HP本体（anzen.mofa.go.jp）: **公共データ利用規約（第1.0版）（PDL1.0）**を確認。オープンデータサイト（ezairyu.mofa.go.jp/html/opendata/）: **政府標準利用規約（第2.0版）準拠、CC BY 4.0互換を明記**（「本利用規約は、クリエイティブ・コモンズ・ライセンス表示4.0国際…と互換性があり、本利用規約が適用されるコンテンツは、CC BYに従うことでも利用できます」） |
| 商用利用 | **可**。オープンデータ規約原文: 「複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます。**商用利用も可能です**」。なお「数値データ、簡単な表・グラフ等は著作権の対象ではないため規約適用外で自由利用可」 |
| 帰属表示（文言例・原文） | 「出典：外務省 海外安全情報オープンデータ（当該ページのURL）」／海外安全HP: 「出典：外務省 海外安全ホームページ（当該ページのURL）」 |
| 編集・加工時 | 出典とは別に加工した旨を記載。例: 「『○○危険情報』（外務省 海外安全情報オープンデータ）（URL）をもとに○○株式会社作成」。**国が作成したかのような態様での公表は禁止** — AI提案文に危険情報を織り込む際は「外務省情報を加工」である旨の表示設計が必要 |
| API/オープンデータ | **あり**。ezairyu.mofa.go.jp配下に「海外安全情報オープンデータ」サイトが存在（危険情報等の機械可読提供、国別XML）。※配信形式の詳細ページは今回未確認 |
| 費用／更新 | 無料／随時（危険情報発出時） |
| 根拠URL | [海外安全HP 法的事項](https://www.anzen.mofa.go.jp/c_info/legalmatters.html) ／ [オープンデータ利用規約](https://www.ezairyu.mofa.go.jp/html/opendata/support/terms.html) |

## 10. GeoNames（補欠候補）

| 項目 | 内容 |
|---|---|
| ライセンス | **CC BY 4.0**。原文: 「The GeoNames geographical database is available for download free of charge under a creative commons attribution license」 |
| 商用利用 | 可（CC BY 4.0） |
| 帰属表示 | GeoNamesへのクレジット必須（CC BY標準: 出典名＋ライセンスへのリンク＋改変の明示） |
| 再配布・加工・組み合わせ | 可。share-alikeなし（混合安全） |
| 費用／更新 | ダンプ無料・**日次エクスポート**。無料Web APIはクレジット制（時間/日次上限）、商用高頻度利用は有償premium web serviceあり（詳細価格は未確認） |
| 根拠URL | [geonames.org/about.html](https://www.geonames.org/about.html) |

---

## リスク順ランキング（本プロジェクト観点）

| 順位 | ソース | リスク | 理由 |
|---|---|---|---|
| 1 | **UNESCO whc.unesco.org** | 高 | 商用利用は有償ライセンス＋書面許可必須、再公開全面禁止。**公式データの直接取り込みは避け、Wikidata（CC0）経由に切り替えるべき**。事実情報のみ使い、UNESCOの記述文は転載しない |
| 2 | **OpenStreetMap (ODbL)** | 中 | 商用利用自体は問題ないが、share-alike設計（下記法務論点）とDB混合方法の設計規律が必要。設計を誤ると§4.6の派生DB提供義務が理論上発生 |
| 3 | **Open-Meteo無料枠** | 中 | 無料APIは非商用限定と明文化。**商用プラン契約（$29〜99/月）かERA5直接取得への切替が必須**。無料枠のまま商用投入すると明確な規約違反 |
| 4 | **Eurostat** | 低〜中 | 基本CC BY 4.0だが、非EU/EFTA由来データの商用再利用禁止例外あり。使用系列ごとの出所確認が必要 |
| 5 | **外務省** | 低 | 商用可を明文確認。ただし「国が作成したかのような態様」禁止のため、AI出力での出典・加工表示のUI設計が必要 |
| 6 | **GeoNames** | 低 | CC BYの帰属表示を実装すれば問題なし（無料APIの上限のみ注意） |
| 7 | **Foursquare OS Places** | 低 | Apache 2.0で自由度高。HFゲートの「社名・ロゴのマーケティング利用同意」だけ広報・法務に事前共有推奨（Portal/S3経由なら回避可能か要確認） |
| 8 | **Wikimedia Pageviews** | 極低 | CC0。User-Agent設定と取得ペース配慮のみ |
| 9 | **Wikidata** | 極低 | CC0 |
| 10 | **OurAirports** | 極低 | パブリックドメイン |

## OSM ODbL 法務確認が必要な論点の要約

1. **社内DBの位置づけ（最重要・好材料）**: ODbL §4.5(c)が「組織内部での派生DB利用はpublicではなくshare-alike（§4.4）の対象外」と明文で規定。JTB社内DBに留める限り公開義務なし。ただし「Publicly」の定義は「50%超所有・支配下にない者への利用」— **グループ会社・委託先ベンダー・クラウド上の提供形態がこの範囲に収まるか**の確認が必要。
2. **AI提案文の法的性質**: 顧客に表示される提案文は「Produced Work（テキスト）」に該当する可能性が高い。もし社内DBが「Derivative Database」と認定されると、§4.6により**Produced Workの公的利用時に派生DB全体の機械可読コピー提供義務**が発生し得る。→ 社内DBをDerivativeにしない設計（論点3）が防波堤になる。なおOSMF帰属ガイドラインのジオコーディング/ML項は「結果テキストへの個別帰属は不要」との類推材料を提供。
3. **Collective Database設計の遵守**: OSMF公認ガイドラインに従い、(a) OSM由来と他ソース由来のデータを**プロパティ（カラム）単位で完全分離**する（同一プロパティ内でOSM値と他ソース値を混在・相互補完しない）、(b) OSM IDと他データの**レコード間相互参照を作らない**（「参照はいかなる識別方法でも成立」との文言に注意——都市IDでの単純並置が「参照」に当たらない設計かの確認）、(c) データリネージを記録すること。これが守られれば社内DBはCollective Databaseであり、そもそもshare-alike対象外。
4. **帰属表示の実装**: 最低限、DB内README等に「© OpenStreetMap contributors, ODbL」＋ライセンスリンク。顧客向けUIに地図やOSM由来情報を目に見える形で出す場合の表示位置・文言を帰属ガイドラインに沿って決定。
5. **未確定領域の認識**: Produced WorkガイドラインはAI/LLM出力を明示的に扱っておらず、「AI提案文がOSMデータを実質的(Substantial)に再現する場合」の扱いは公式解釈が存在しない。OSMF Community Guidelinesは法的拘束力ある解釈ではなくOSMFの見解である点も含め、法務見解を取得すべき。

## 未確認事項（推測で埋めていない項目）

- UNESCO公式ページ2点はCloudflareにより直接取得不可（引用は検索エンジン経由の同ページ本文。原文再確認推奨）
- Wikimedia Pageviews API（AQS）固有のレート数値、ERA5の更新頻度の公式記載、GeoNames有償Web APIの価格、Foursquare Portal経由取得時の追加条件有無、外務省オープンデータの配信形式詳細
