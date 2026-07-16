# city-data-builder

接客AI（β版）の旅行先提案ロジックで使う、**154件の欧州都市・観光地の客観的事実データ**を調査・設計・作成するプロジェクト。

- 依頼内容（原本）：[docs/note.md](docs/note.md)
- 計画書：[docs/plan.md](docs/plan.md)
- 連携先リポジトリ：`global-bm`

## 進行状況

| フェーズ | 内容 | 状態 | 成果物 |
| --- | --- | --- | --- |
| 0. 名寄せ | 154件にQID・座標・種別を付与 | ✅ 完了（全件暫定承認） | [docs/phase0/](docs/phase0/)、`data/master/places_master.json` |
| 1. 調査 | データソースの取得可否・カバー率・ライセンス | ✅ 完了（承認待ち） | [docs/phase1/](docs/phase1/) |
| 2. 設計 | スキーマ＋質問回答→指標マッピング | ✅ 完了（承認済み） | [docs/phase2/](docs/phase2/)、[schema/](schema/)、`data/output/samples/` |
| 3. 作成 | 154件の統一フォーマットデータ | 🔄 進行中 | docs/phase3/、data/output/ |

## フォルダ構成

```
├── docs/
│   ├── note.md                     # 依頼内容（原本・編集しない）
│   ├── plan.md                     # 計画書（全体）
│   ├── phase0/
│   │   ├── review.md               # 同定結果レビュー一覧（build_master.py が生成）
│   │   └── data-dictionary.md      # マスタのデータ辞書（暫定版。フェーズ2で正式化）
│   ├── phase1/
│   │   ├── data-source-survey.md   # データソース調査レポート（採用判定）
│   │   └── license-research.md     # ライセンス一次情報の確認記録（根拠URL付き）
│   ├── phase2/                     # （今後）スキーマ設計書
│   └── phase3/                     # （今後）データ品質レポート
├── data/
│   ├── cities.json                 # 原本（154件・日本語名のみ・編集しない）
│   ├── master/
│   │   ├── seed_places.json        # 同定案シード（人手管理。修正はここに）
│   │   └── places_master.json      # 名寄せマスタ（生成物。直接編集しない）
│   ├── raw/
│   │   ├── wikidata/cache.json     # Wikidata APIキャッシュ（生成物）
│   │   └── survey/                 # フェーズ1実測の根拠データ
│   └── output/                     # （今後）最終データ
└── scripts/
    ├── build_master.py             # シード検証→マスタ＋レビュー一覧を生成
    └── survey/                     # フェーズ1の実測・取得テスト（すべて再実行可能）
        ├── wikipedia.py            # Wikipedia記事カバー率（ja 92% / en 98%）
        ├── airports.py             # 最寄り空港計算（OurAirports、100%）
        ├── unesco_whs.py           # 世界遺産取得（Wikidata経由）＋近傍マッチング
        ├── probe_pageviews.py      # 閲覧数APIテスト
        ├── probe_climate.py        # 気候データテスト（⚠️本番はERA5直接取得）
        ├── probe_overpass.py       # OSM POI数テスト（本番はGeofabrik推奨）
        └── probe_eurostat_mofa.py  # 観光統計・外務省オープンデータのテスト
```

## 使い方

```bash
uv sync                                   # 環境構築（Python 3.13固定）
uv run python scripts/build_master.py     # マスタ再生成（APIキャッシュにより差分のみ照会）
uv run python scripts/survey/airports.py  # 例: 最寄り空港の再計算
```

- 同定の修正：`data/master/seed_places.json` の該当エントリに `qid` を直接指定 → `build_master.py` を再実行
- 生成物（`places_master.json`、`docs/phase0/review.md`、`data/raw/wikidata/cache.json`）は手で編集しない

## データの決めごと（要点）

- 154件は同一スキーマ＋`type` 属性（city / town_village / single_poi / natural_feature / route）。定義は [docs/phase0/data-dictionary.md](docs/phase0/data-dictionary.md)
- 外部データはWikidata QIDと座標をキーに結合する
- ライセンス上の扱い（UNESCO不採用・OSM分離設計など）は [docs/phase1/data-source-survey.md](docs/phase1/data-source-survey.md) の採用判定に従う
