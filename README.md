# city-data-builder

接客AI（β版）の旅行先提案ロジックで使う、**154件の欧州都市・観光地の客観的事実データ**を調査・設計・作成するプロジェクト。

- 依頼内容（原本）：[docs/note.md](docs/note.md) ／ 計画書：[docs/plan.md](docs/plan.md)
- 連携先リポジトリ：`global-bm`

## 成果物（まずここから）

| 何を見たい | どこ |
| --- | --- |
| **最終データ（154件・統一フォーマット）** | [data/output/places.json](data/output/places.json) |
| **データを画面で眺める** | `uv run python scripts/serve_viewer.py` を実行（ブラウザが自動で開く。**他メンバーへの共有は `--share` 付きで実行**し表示される共有URLを配布。検索／フィルタ／指標バー／気候チャート／**画像カルーセル・地図**。出所チップ・計算方法の解説・JSONパス表示つき。画像と地図の表示には閲覧側の外部接続が必要） |
| データの形式定義 | [schema/place.schema.json](schema/place.schema.json)＋設計書 [docs/phase2/schema-design.md](docs/phase2/schema-design.md) |
| 品質・既知の制約 | [docs/phase3/data-quality-report.md](docs/phase3/data-quality-report.md) |

## 進行状況

| フェーズ | 内容 | 状態 | 成果物 |
| --- | --- | --- | --- |
| 0. 名寄せ | 154件にQID・座標・種別を付与 | ✅ 完了（全件暫定承認） | [docs/phase0/](docs/phase0/)、`data/master/places_master.json` |
| 1. 調査 | データソースの取得可否・カバー率・ライセンス | ✅ 完了 | [docs/phase1/](docs/phase1/) |
| 2. 設計 | スキーマ＋質問回答→指標マッピング | ✅ 完了（承認済み） | [docs/phase2/](docs/phase2/)、[schema/](schema/) |
| 3. 作成 | 154件の統一フォーマットデータ | ✅ 一次完成（POI=OSM版） | [docs/phase3/](docs/phase3/)、[data/output/](data/output/) |

### 残課題

一覧と詳細は **[docs/phase1/data-source-survey.md §4](docs/phase1/data-source-survey.md)**（提出物側に記載）。
要点：**本データは将来一般サービスとして公開される可能性があるため、公開判断の前にOSM ODbLの法務確認が必須**（優先度・高）。
ほかにFoursquare Portal登録の判断、指標の重み調整、Eurostat NUTS2対応表など。

## セットアップ

```bash
uv sync                 # Python環境の構築（3.13固定・依存はuv.lockで再現）
cp .env.example .env    # 気候データ(ERA5)を再取得する場合のみ: CDSのトークンを記入
```

## データの再生成（パイプライン）

```
scripts/fetch/ ──→ data/raw/（ソース別生データ） ──→ build_places.py ──→ data/output/places.json ←─参照── viewer/index.html
```

```bash
# 1) 取得（必要なものだけ。生データはdata/raw/に保存され、再実行は差分のみ）
uv run python scripts/build_master.py           # 名寄せマスタ（Wikidata。キャッシュあり）
uv run python scripts/fetch/wikidata_extras.py  # 標高
uv run python scripts/fetch/sitelinks.py        # Wikipedia記事タイトル（閲覧数取得の前提）
uv run python scripts/fetch/pageviews.py        # Wikipedia閲覧数（約10分・中断再開可）
uv run python scripts/fetch/mofa_safety.py      # 外務省 危険情報（21カ国）
uv run python scripts/fetch/osm_poi.py          # OSM POI・自然地物（1〜2時間・中断再開可）
uv run python scripts/fetch/climate_era5.py fetch && uv run python scripts/fetch/climate_era5.py extract  # 気候（要.env）
uv run python scripts/fetch/airports.py         # 最寄り空港（CSVは自動ダウンロード）
uv run python scripts/fetch/unesco_whs.py       # 世界遺産（Wikidata SPARQL）

# 2) 組み立て・検証・可視化
uv run python scripts/build_places.py           # 全154件を統合し JSON Schema で検証
uv run python scripts/quality_report.py         # 品質レポート再生成（妥当性・外れ値チェック）
```

## フォルダ構成

```
├── docs/
│   ├── note.md / plan.md               # 依頼原本・計画書
│   ├── phase0/                         # 名寄せ（同定レビュー・データ辞書）
│   ├── phase1/                         # データソース調査・ライセンス調査（根拠URL付き）
│   ├── phase2/schema-design.md         # スキーマ設計書（指標の定義・算出式はここ）
│   └── phase3/data-quality-report.md   # 品質レポート（既知の制約もここ）
├── schema/place.schema.json            # JSON Schema（形式定義）
├── data/
│   ├── cities.json                     # 原本（154件・日本語名のみ・編集しない）
│   ├── master/
│   │   ├── seed_places.json            # 同定シード（人手管理。同定修正はここにQIDを指定）
│   │   └── places_master.json          # 名寄せマスタ（生成物）
│   ├── raw/                            # ソース別生データ（airports/ era5/ mofa/ osm/ pageviews/ wikidata/）
│   └── output/places.json              # ★最終データ
├── viewer/index.html                   # ★ビュワー（ソース。places.jsonを参照して表示）
└── scripts/
    ├── build_master.py                 # フェーズ0: 名寄せマスタ生成
    ├── fetch/                          # 本番の取得スクリプト（すべて再実行・中断再開可）
    ├── survey/                         # フェーズ1調査時の取得テスト（probe_*。本番では未使用）
    ├── build_places.py                 # 統合＋スキーマ検証 → places.json
    ├── quality_report.py               # 品質検証 → 品質レポート
    ├── serve_viewer.py                 # ビュワーをローカルHTTPで開く（file://はfetch不可のため）
    └── envfile.py                      # .env ローダー
```

## 運用ルール

- **生成物は手で編集しない**（`places_master.json` / `places.json` / `docs/phase0/review.md`。修正はシードやスクリプトに入れて再生成。`viewer/index.html` はソースなので直接編集してよい）
- **data/raw/ のgit管理ポリシー**：スクリプトで再取得できる大容量ダウンロード（ERA5生データ・外務省XML・空港CSV）は管理外＆抽出後にディスクからも削除可。小さな抽出結果・取得に時間のかかる成果（OSMの`poi_counts.json`等）は管理する
- **シークレット**：`.env`（CDSトークン）はコミット禁止（gitignore済み）。雛形は `.env.example`
- **ライセンス**：OSM由来データは `poi` / `osm_features` ブロックに分離し `_meta.source="osm"` を明記（ODbL対応。詳細は [docs/phase1/data-source-survey.md](docs/phase1/data-source-survey.md) §2.7）。外部表示時の帰属表示文は各ブロックの `_meta.attribution` にある

## データの決めごと（要点）

- 154件は同一スキーマ＋`type` 属性（city / town_village / single_poi / natural_feature / route）。都市向け項目が該当しない種別は null
- 外部データとの結合キーは **Wikidata QID＋座標**
- **事実（Layer 1）と指標（Layer 2）を分離**。指標は「同種の地点内のパーセンタイル 0〜100」で、算出式を `indicators.*.formula`、依存ソースを `depends_on` としてデータ内に保持（OSMがNGになった場合は依存指標だけ機械的に再計算できる）
