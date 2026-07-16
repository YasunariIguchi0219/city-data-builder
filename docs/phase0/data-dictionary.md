# 名寄せマスタ データ辞書（暫定版）

- 対象ファイル：`data/master/places_master.json`
- ステータス：**暫定（フェーズ0時点）**。フェーズ2「データ構造設計」（`docs/phase2/schema-design.md`）で正式版に置き換える。
- 生成方法：`uv run python scripts/build_master.py`（シード `data/master/seed_places.json` を Wikidata API で検証して生成。再実行可能）
- 作成日：2026年7月16日

## 1. ファイルの位置づけ

154件の都市・観光地（原本：`data/cities.json`、日本語名のみ）を、外部データソースと突合できる共通キー（Wikidata QID・座標）に変換する**名寄せマスタ**。以降の全工程（データソース調査のカバー率実測、データ作成）はこのマスタをキーに行う。

## 2. トップレベル構造

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `generated_by` | string | 生成スクリプトのパス |
| `source_seed` | string | シードファイルのパス |
| `count` | number | レコード件数（154） |
| `places` | array | 地点レコードの配列（原本 `cities.json` と同順） |

## 3. 地点レコードのフィールド定義

| フィールド | 型 | null | 説明 |
| --- | --- | --- | --- |
| `id` | string | 不可 | プロジェクト内の安定ID。英語名のslug（例：`amsterdam`、`chateau-de-chambord`）。**以降の全データファイルはこのIDで結合する** |
| `name_ja` | string | 不可 | 日本語名。原本 `cities.json` の表記そのまま（表記ゆれも保持） |
| `name_en` | string | 不可 | 英語名。Wikidataの英語ラベル（なければ検索語） |
| `wikidata_label_ja` | string | 可 | Wikidata側の日本語ラベル。**同定の妥当性確認用**（原本名と近ければ同定は概ね正しい）。routeにはない |
| `qid` | string | 可 | Wikidata QID（例：`Q727`）。**外部ソースとの結合主キー**。route 2件のみnull |
| `country` | string | 可 | 国コード（ISO 3166-1 alpha-2）。routeのみnull |
| `country_ja` | string | 可 | 国名（日本語） |
| `type` | string | 不可 | 種別（§4参照）。**プロジェクト独自分類**（Wikidataの分類ではない） |
| `lat` / `lon` | number | 可 | 緯度・経度（WGS84、小数5桁）。Wikidata P625由来。routeのみnull |
| `population` | number | 可 | 人口。Wikidata P1082の現行値（preferredランク優先→時点が最新のもの、deprecated除外）。城・自然地物等は原則null |
| `population_date` | string | 可 | 上記人口の時点（`YYYY-MM-DD`。Wikidata上で日が不明な場合 `YYYY-00-00` 形式あり） |
| `description_en` | string | 可 | Wikidataの英語説明文。同定確認用の参考情報 |
| `instance_of` | array | 可 | Wikidata P31（instance of）のQID列（最大6件）。Wikidata側の分類。参考・将来の細分類用 |
| `endpoints` | array | — | **routeのみ**。航路の両端（日本語名） |
| `note` | string | 可 | 同定に関する人手の補足（シード由来） |
| `review` | boolean | 不可 | 人によるレビューが必要なエントリはtrue（`docs/phase0/review.md` の要確認一覧に対応） |

## 4. 種別（`type`）の定義 【暫定・フェーズ2で見直し】

| 値 | 定義 | 判定方法 | 件数 |
| --- | --- | --- | --- |
| `city` | 都市 | シードで settlement 指定かつ **人口10万以上**（機械判定） | 76 |
| `town_village` | 町・村 | シードで settlement 指定かつ人口10万未満または不明（機械判定） | 64 |
| `single_poi` | 単体スポット（城・遺跡・修道院など） | シードで人手指定 | 9 |
| `natural_feature` | 自然地物（湖・フィヨルド・国立公園） | シードで人手指定 | 3 |
| `route` | 航路（旅行先ではなく移動手段） | シードで人手指定 | 2 |

### 暫定的な決めごと（フェーズ2でレビューする論点）

- **人口10万の閾値は仮置き**。人口の生値を保持しているため、閾値変更・多段階化・「分類せず人口を直接指標に使う」への変更はいつでも可能。
- `single_poi` / `natural_feature` には、将来「最寄り拠点都市への参照」を持たせる想定（未実装）。
- `route` はQID・座標を持たない。POI数など都市向け項目はすべてnullとする方針。
- 都市向け項目が該当しない種別は**null許容**（0ではなくnull＝「該当なし／未取得」）。

## 5. 生成・検証の仕組み（再現性）

1. `data/master/seed_places.json` … 人手作成の同定案（154件）。検索語・想定国・種別・レビューフラグを持つ。誤同定が判明した場合は `qid` フィールドでWikidata IDを直接指定（ピン留め）できる。
2. `scripts/build_master.py` … シードをWikidata APIで検証（想定国と一致し座標を持つ候補を採用）。API応答は `data/raw/wikidata/cache.json` にキャッシュされ、再実行時は差分のみ照会。
3. 出力は本マスタと `docs/phase0/review.md`（レビュー用一覧）。

### 既知の注意点

- Wikidataの人口には歴史値（紀元前含む）が混在するため、preferredランク優先＋年の数値比較で現行値を選んでいる。
- 検索ベースの同定は誤ヒットしうる（例：オックスフォード→大学を誤取得）。原本名とWikidata日本語ラベルの突き合わせで検出し、QIDピン留めで修正する運用。
