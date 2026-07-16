# フェーズ0 レビュー：154件の同定結果一覧

`scripts/build_master.py` により生成。マスタ本体は `data/master/places_master.json`。

> **レビュー結果（2026-07-16）：全件暫定承認。** リストの出所に正解を持つ者がいないため、曖昧エントリ（ディナン=仏Dinan、ランス=Reims 等）は本一覧の同定のまま採用する。将来ツアー文脈等で正解が判明した場合は `seed_places.json` のQID指定を修正して再生成する。

- 件数：154件（city: 76件、natural_feature: 3件、route: 2件、single_poi: 9件、town_village: 64件）
- 種別：city（人口10万以上）／town_village（それ未満・不明）／single_poi（城・遺跡等の単体スポット）／natural_feature（自然地物）／route（航路）
- 「Wikidata日本語ラベル」列は同定の妥当性確認用。原本の日本語名と一致・近似していれば同定は概ね正しい。

## ⚠️ 要確認エントリ（同定に曖昧さがあるもの）

| 日本語名（原本） | 同定結果（英語名） | 国 | 種別 | Wikidata | 人口 | Wikidata日本語ラベル | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ウィンザー | Windsor | イギリス | town_village | [Q464955](https://www.wikidata.org/wiki/Q464955) | 32,184 | ウィンザー | 同名地が多数（カナダ等）。英国バークシャーの町と同定（検索ではウィンザー城を誤取得するためQID固定） |
| カーン | Caen | フランス | city | [Q41185](https://www.wikidata.org/wiki/Q41185) | 109,400 | カーン | Caen（ノルマンディー）と同定。カンヌ(Cannes)ではない前提 |
| クリスチャンサン | Kristiansand | ノルウェー | city | [Q2415](https://www.wikidata.org/wiki/Q2415) | 119,287 | クリスチャンサン | Kristiansand（南部）と同定。Kristiansund（西部）の可能性もあり |
| コルドバ | Córdoba | スペイン | city | [Q5818](https://www.wikidata.org/wiki/Q5818) | 323,262 | コルドバ | アルゼンチン等にも同名地。スペイン・アンダルシアと同定 |
| シャンボール | Château de Chambord | フランス | single_poi | [Q205367](https://www.wikidata.org/wiki/Q205367) | — | シャンボール城 | 城として同定（村Chambordではなく） |
| シュノンソー | Château de Chenonceau | フランス | single_poi | [Q193215](https://www.wikidata.org/wiki/Q193215) | — | シュノンソー城 | 城として同定（村Chenonceauxではなく） |
| ストックホルム―トゥルク | Stockholm–Turku ferry | — | route | — | — | — | バルト海クルーズフェリー航路（Viking Line / Tallink Silja）。旅行先ではなく航路 |
| ダラム | Durham | イギリス | town_village | [Q179815](https://www.wikidata.org/wiki/Q179815) | 48,069 | ダラム | 米国にも同名地多数。英国イングランド北東部と同定 |
| ディナン | Dinan | フランス | town_village | [Q201311](https://www.wikidata.org/wiki/Q201311) | 14,764 | ディナン | 【要確認】仏ブルターニュのDinanと同定したが、ベルギーのDinant（ディナン）の可能性あり。ツアー文脈で確認要 |
| デンマーク/ノルウェー間フェリー | Copenhagen–Oslo ferry | — | route | — | — | — | DFDSのオーバーナイトフェリー航路と想定。旅行先ではなく航路 |
| ナザレ | Nazaré | ポルトガル | town_village | [Q497179](https://www.wikidata.org/wiki/Q497179) | 15,158 | ナザレ | イスラエルのナザレではなく、ポルトガルの海岸の町と同定 |
| ビトリア | Vitoria-Gasteiz | スペイン | city | [Q14318](https://www.wikidata.org/wiki/Q14318) | 260,699 | ビトリア＝ガステイス | ブラジルのVitóriaではなく、バスク州都Vitoria-Gasteizと同定 |
| ビランドリー | Château de Villandry | フランス | single_poi | [Q477613](https://www.wikidata.org/wiki/Q477613) | — | ヴィランドリー城 | 庭園で有名な城として同定（村Villandryではなく） |
| ベルゲン | Bergen | ノルウェー | city | [Q26793](https://www.wikidata.org/wiki/Q26793) | 291,189 | ベルゲン | 独・蘭にも同名地。ノルウェーと同定 |
| ポンペイ | Pompeii | イタリア | single_poi | [Q43332](https://www.wikidata.org/wiki/Q43332) | — | ポンペイ | 古代遺跡として同定。現代都市Pompeiの選択肢もあり |
| メリダ | Mérida | スペイン | town_village | [Q14323](https://www.wikidata.org/wiki/Q14323) | 60,225 | メリダ | メキシコ・ベネズエラにも同名地。ローマ遺跡のあるスペイン・エストレマドゥーラと同定 |
| モンセラット | Santa Maria de Montserrat | スペイン | single_poi | [Q771935](https://www.wikidata.org/wiki/Q771935) | — | サンタ・マリア・ダ・ムンサラート大修道院付属大聖堂 | モンセラット修道院(Santa Maria de Montserrat)と同定。検索ではバレンシア県の同名の町を誤取得するためQID固定。山と修道院どちらを主とするか要確認 |
| ランカスター | Lancaster | イギリス | city | [Q168052](https://www.wikidata.org/wiki/Q168052) | 144,246 | シティ・オブ・ランカスター | 米国に同名地多数。英国イングランド北西部と同定 |
| ランス | Reims | フランス | city | [Q41876](https://www.wikidata.org/wiki/Q41876) | 177,674 | ランス | 【要確認】大聖堂のあるReimsと同定したが、ルーヴル別館のあるLens（ランス）の可能性もあり |
| リッチフィールド | Lichfield | イギリス | city | [Q1823259](https://www.wikidata.org/wiki/Q1823259) | 108,352 | リッチフィールド・ディストリクト | 大聖堂のある英スタッフォードシャーLichfieldと同定 |
| レバント | Levanto | イタリア | town_village | [Q254139](https://www.wikidata.org/wiki/Q254139) | 5,140 | レヴァント | 【要確認】チンクエテッレ近郊のLevanto（リグーリア）と同定。ヴェルナッツァが同リストにあることが傍証 |
| ローテンブルク | Rothenburg ob der Tauber | ドイツ | town_village | [Q153494](https://www.wikidata.org/wiki/Q153494) | 11,385 | ローテンブルク・オプ・デア・タウバー | ロマンチック街道のRothenburg ob der Tauberと同定（他のRothenburgではなく） |

## 全件一覧（上記以外）

| 日本語名（原本） | 同定結果（英語名） | 国 | 種別 | Wikidata | 人口 | Wikidata日本語ラベル | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| アインジーデルン | Einsiedeln | スイス | town_village | [Q68950](https://www.wikidata.org/wiki/Q68950) | 15,550 | アインジーデルン |  |
| アッシジ | Assisi | イタリア | town_village | [Q20103](https://www.wikidata.org/wiki/Q20103) | 27,605 | アッシジ |  |
| アニック | Alnwick | イギリス | town_village | [Q1002826](https://www.wikidata.org/wiki/Q1002826) | 8,583 | アニック | アニック城の城下町として同定 |
| アベイロ | Aveiro | ポルトガル | town_village | [Q485581](https://www.wikidata.org/wiki/Q485581) | 78,450 | アヴェイロ |  |
| アムステルダム | Amsterdam | オランダ | city | [Q727](https://www.wikidata.org/wiki/Q727) | 921,468 | アムステルダム |  |
| アルベロベッロ | Alberobello | イタリア | town_village | [Q51812](https://www.wikidata.org/wiki/Q51812) | 10,177 | アルベロベッロ |  |
| アロマンシュ | Arromanches-les-Bains | フランス | town_village | [Q212620](https://www.wikidata.org/wiki/Q212620) | 413 | アロマンシュ＝レ＝バン | ノルマンディー上陸作戦の海岸の町 |
| アンジェ | Angers | フランス | city | [Q38380](https://www.wikidata.org/wiki/Q38380) | 159,022 | アンジェ |  |
| アンボワーズ | Amboise | フランス | town_village | [Q205116](https://www.wikidata.org/wiki/Q205116) | 12,937 | アンボワーズ |  |
| インバネス | Inverness | イギリス | town_village | [Q160493](https://www.wikidata.org/wiki/Q160493) | 47,380 | インヴァネス |  |
| ウィーン | Vienna | オーストリア | city | [Q1741](https://www.wikidata.org/wiki/Q1741) | 2,028,289 | ウィーン |  |
| エディンバラ | Edinburgh | イギリス | city | [Q23436](https://www.wikidata.org/wiki/Q23436) | 488,050 | エディンバラ |  |
| エボラ | Évora | ポルトガル | town_village | [Q179948](https://www.wikidata.org/wiki/Q179948) | 53,577 | エヴォラ |  |
| オスロ | Oslo | ノルウェー | city | [Q585](https://www.wikidata.org/wiki/Q585) | 717,710 | オスロ |  |
| オックスフォード | Oxford | イギリス | city | [Q34217](https://www.wikidata.org/wiki/Q34217) | 147,500 | オックスフォード | 検索ではオックスフォード大学を誤取得するためQID固定 |
| オパティア | Opatija | クロアチア | town_village | [Q223353](https://www.wikidata.org/wiki/Q223353) | 10,619 | オパティヤ |  |
| オビドス | Óbidos | ポルトガル | town_village | [Q275862](https://www.wikidata.org/wiki/Q275862) | 11,689 | オビドゥシュ | ブラジルにも同名地あり。ポルトガルと同定 |
| オルタ・サン・ジュリオ | Orta San Giulio | イタリア | town_village | [Q22536](https://www.wikidata.org/wiki/Q22536) | 1,047 | オルタ・サン・ジューリオ |  |
| オレブロ | Örebro | スウェーデン | city | [Q25732](https://www.wikidata.org/wiki/Q25732) | 128,658 | エレブルー |  |
| オーデンセ | Odense | デンマーク | city | [Q25331](https://www.wikidata.org/wiki/Q25331) | 185,480 | オーデンセ |  |
| オーフス | Aarhus | デンマーク | city | [Q25319](https://www.wikidata.org/wiki/Q25319) | 290,598 | オーフス |  |
| カレー | Calais | フランス | town_village | [Q6454](https://www.wikidata.org/wiki/Q6454) | 67,571 | カレー |  |
| カンバードス | Cambados | スペイン | town_village | [Q24013870](https://www.wikidata.org/wiki/Q24013870) | 6,789 | — | ガリシア州の漁村 |
| グラスゴー | Glasgow | イギリス | city | [Q4093](https://www.wikidata.org/wiki/Q4093) | 626,410 | グラスゴー |  |
| グラナダ | Granada | スペイン | city | [Q8810](https://www.wikidata.org/wiki/Q8810) | 233,975 | グラナダ | ニカラグア等にも同名地。スペインと同定 |
| グリュイエール | Gruyères | スイス | town_village | [Q69600](https://www.wikidata.org/wiki/Q69600) | 2,199 | グリュイエール |  |
| ケルン | Cologne | ドイツ | city | [Q365](https://www.wikidata.org/wiki/Q365) | 1,087,353 | ケルン |  |
| コインブラ | Coimbra | ポルトガル | city | [Q45412](https://www.wikidata.org/wiki/Q45412) | 140,816 | コインブラ |  |
| コペンハーゲン | Copenhagen | デンマーク | city | [Q1748](https://www.wikidata.org/wiki/Q1748) | 667,099 | コペンハーゲン |  |
| コンスエグラ | Consuegra | スペイン | town_village | [Q919046](https://www.wikidata.org/wiki/Q919046) | 9,767 | コンスエグラ | 風車の町 |
| サラエボ | Sarajevo | ボスニア・ヘルツェゴビナ | city | [Q11194](https://www.wikidata.org/wiki/Q11194) | 275,524 | サラエヴォ |  |
| サラゴサ | Zaragoza | スペイン | city | [Q10305](https://www.wikidata.org/wiki/Q10305) | 693,091 | サラゴサ |  |
| サンジミニャーノ | San Gimignano | イタリア | town_village | [Q91413](https://www.wikidata.org/wiki/Q91413) | 7,480 | サン・ジミニャーノ |  |
| サンセバスチャン | San Sebastián | スペイン | city | [Q10313](https://www.wikidata.org/wiki/Q10313) | 189,866 | サン・セバスティアン |  |
| サンチャゴ・デ・コンポステーラ | Santiago de Compostela | スペイン | city | [Q14314](https://www.wikidata.org/wiki/Q14314) | 100,965 | サンティアゴ・デ・コンポステーラ |  |
| サンマロ | Saint-Malo | フランス | town_village | [Q163108](https://www.wikidata.org/wiki/Q163108) | 47,439 | サン・マロ |  |
| ザグレブ | Zagreb | クロアチア | city | [Q1435](https://www.wikidata.org/wiki/Q1435) | 767,131 | ザグレブ |  |
| ザルツブルク | Salzburg | オーストリア | city | [Q34713](https://www.wikidata.org/wiki/Q34713) | 155,021 | ザルツブルク |  |
| ザンクトゴア | Sankt Goar | ドイツ | town_village | [Q186037](https://www.wikidata.org/wiki/Q186037) | 2,913 | ザンクト・ゴアー | ライン川中流域（ローレライ付近） |
| ザーンスカンス | Zaanse Schans | オランダ | single_poi | [Q136661](https://www.wikidata.org/wiki/Q136661) | 100 | ザーンセ・スカンス | 風車の野外保存地区。所在都市はザーンダム |
| シャモニー | Chamonix-Mont-Blanc | フランス | town_village | [Q83236](https://www.wikidata.org/wiki/Q83236) | 8,705 | シャモニー＝モン＝ブラン |  |
| シャルトル | Chartres | フランス | town_village | [Q130272](https://www.wikidata.org/wiki/Q130272) | 38,324 | シャルトル |  |
| シヨン城 | Chillon Castle | スイス | single_poi | [Q372647](https://www.wikidata.org/wiki/Q372647) | — | シヨン城 | レマン湖畔。最寄り都市はモントルー |
| シルミオーネ | Sirmione | イタリア | town_village | [Q112019](https://www.wikidata.org/wiki/Q112019) | 8,248 | シルミオーネ | ガルダ湖畔 |
| ジュネーブ | Geneva | スイス | city | [Q71](https://www.wikidata.org/wiki/Q71) | 209,061 | ジュネーヴ |  |
| スタバンゲル | Stavanger | ノルウェー | city | [Q26772333](https://www.wikidata.org/wiki/Q26772333) | 129,300 | — |  |
| ストウ・オン・ザ・ウォルド | Stow-on-the-Wold | イギリス | town_village | [Q33125737](https://www.wikidata.org/wiki/Q33125737) | 1,901 | — | コッツウォルズ |
| ストックホルム | Stockholm | スウェーデン | city | [Q1754](https://www.wikidata.org/wiki/Q1754) | 984,748 | ストックホルム |  |
| ストラスブール | Strasbourg | フランス | city | [Q6602](https://www.wikidata.org/wiki/Q6602) | 293,771 | ストラスブール |  |
| ストラットフォード·アポン·エイボン | Stratford-upon-Avon | イギリス | town_village | [Q189288](https://www.wikidata.org/wiki/Q189288) | 30,495 | ストラトフォード＝アポン＝エイヴォン |  |
| ストレーザ | Stresa | イタリア | town_village | [Q23700](https://www.wikidata.org/wiki/Q23700) | 4,599 | ストレーザ | マッジョーレ湖畔 |
| ストン | Ston Municipality | クロアチア | town_village | [Q428227](https://www.wikidata.org/wiki/Q428227) | 2,491 | ストン | 城壁と牡蠣で知られる町 |
| ストーンヘンジ | Stonehenge | イギリス | single_poi | [Q39671](https://www.wikidata.org/wiki/Q39671) | — | ストーンヘンジ | 最寄り都市はソールズベリー |
| スプリット | Split | クロアチア | city | [Q1663](https://www.wikidata.org/wiki/Q1663) | 160,577 | スプリト |  |
| セビリア | Seville | スペイン | city | [Q8717](https://www.wikidata.org/wiki/Q8717) | 689,423 | セビリア |  |
| ソグネフィヨルド | Sognefjord | ノルウェー | natural_feature | [Q208495](https://www.wikidata.org/wiki/Q208495) | — | ソグネ・フィヨルド |  |
| ソールズベリー | Salisbury | イギリス | town_village | [Q160642](https://www.wikidata.org/wiki/Q160642) | 45,477 | ソールズベリー |  |
| チェスキー・クルムロフ | Český Krumlov | チェコ | town_village | [Q188082](https://www.wikidata.org/wiki/Q188082) | 12,797 | チェスキー・クルムロフ |  |
| チューリッヒ | Zurich | スイス | city | [Q72](https://www.wikidata.org/wiki/Q72) | 452,421 | チューリッヒ |  |
| ツェルマット | Zermatt | スイス | town_village | [Q27494](https://www.wikidata.org/wiki/Q27494) | 6,023 | ツェルマット |  |
| トゥール | Tours | フランス | city | [Q288](https://www.wikidata.org/wiki/Q288) | 139,259 | トゥール |  |
| トラー二 | Trani | イタリア | town_village | [Q13495](https://www.wikidata.org/wiki/Q13495) | 54,941 | トラーニ | 原本の表記は漢数字の「二」（トラー二）。プーリア州Traniと同定 |
| ドブロブニク | Dubrovnik | クロアチア | town_village | [Q1722](https://www.wikidata.org/wiki/Q1722) | 41,562 | ドゥブロヴニク |  |
| ドモドッソラ | Domodossola | イタリア | town_village | [Q23325](https://www.wikidata.org/wiki/Q23325) | 17,709 | ドモドッソラ |  |
| ナポリ | Naples | イタリア | city | [Q2634](https://www.wikidata.org/wiki/Q2634) | 913,462 | ナポリ |  |
| ナーンタリ | Naantali | フィンランド | town_village | [Q503862](https://www.wikidata.org/wiki/Q503862) | 19,999 | ナーンタリ | ムーミンワールドのある町 |
| ニュルンベルク | Nuremberg | ドイツ | city | [Q2090](https://www.wikidata.org/wiki/Q2090) | 529,508 | ニュルンベルク |  |
| ネス湖 | Loch Ness | イギリス | natural_feature | [Q49650](https://www.wikidata.org/wiki/Q49650) | — | ネス湖 |  |
| ネルハ | Nerja | スペイン | town_village | [Q13149](https://www.wikidata.org/wiki/Q13149) | 22,132 | ネルハ |  |
| ノッティンガム | Nottingham | イギリス | city | [Q41262](https://www.wikidata.org/wiki/Q41262) | 289,301 | ノッティンガム |  |
| ハイデルベルク | Heidelberg | ドイツ | city | [Q2966](https://www.wikidata.org/wiki/Q2966) | 162,960 | ハイデルベルク |  |
| バイブリー | Bibury | イギリス | town_village | [Q856722](https://www.wikidata.org/wiki/Q856722) | 581 | バイブリー | コッツウォルズ |
| バイヨンヌ | Bayonne | フランス | town_village | [Q134674](https://www.wikidata.org/wiki/Q134674) | 54,306 | バイヨンヌ | 米NJ州にも同名地。仏バスクと同定 |
| バターリャ | Batalha | ポルトガル | town_village | [Q810715](https://www.wikidata.org/wiki/Q810715) | 15,805 | バターリャ | バターリャ修道院の町 |
| バニャルカ | Banja Luka | ボスニア・ヘルツェゴビナ | city | [Q131127](https://www.wikidata.org/wiki/Q131127) | 185,042 | バニャ・ルカ |  |
| バルセロナ | Barcelona | スペイン | city | [Q1492](https://www.wikidata.org/wiki/Q1492) | 1,731,649 | バルセロナ |  |
| バレンシア | Valencia | スペイン | city | [Q8818](https://www.wikidata.org/wiki/Q8818) | 840,792 | バレンシア |  |
| バース | Bath | イギリス | town_village | [Q22889](https://www.wikidata.org/wiki/Q22889) | 94,092 | バース |  |
| バーミンガム | Birmingham | イギリス | city | [Q2256](https://www.wikidata.org/wiki/Q2256) | 1,137,100 | バーミンガム | 米アラバマ州にも同名地。英国と同定 |
| パリ | Paris | フランス | city | [Q90](https://www.wikidata.org/wiki/Q90) | 2,103,778 | パリ |  |
| パンプローナ | Pamplona | スペイン | city | [Q10282](https://www.wikidata.org/wiki/Q10282) | 209,094 | パンプローナ |  |
| ビュルツブルク | Würzburg | ドイツ | city | [Q2999](https://www.wikidata.org/wiki/Q2999) | 132,215 | ヴュルツブルク |  |
| ビルバオ | Bilbao | スペイン | city | [Q8692](https://www.wikidata.org/wiki/Q8692) | 351,124 | ビルバオ |  |
| ピサ | Pisa | イタリア | town_village | [Q13375](https://www.wikidata.org/wiki/Q13375) | 88,737 | ピサ |  |
| フィレンツェ | Florence | イタリア | city | [Q2044](https://www.wikidata.org/wiki/Q2044) | 360,930 | フィレンツェ |  |
| フォート・オーガスタス | Fort Augustus | イギリス | town_village | [Q1012033](https://www.wikidata.org/wiki/Q1012033) | 660 | フォート・オーガスタス | ネス湖南端の村 |
| フジェール | Fougères | フランス | town_village | [Q4043](https://www.wikidata.org/wiki/Q4043) | 20,307 | フージェール |  |
| フランクフルト | Frankfurt am Main | ドイツ | city | [Q1794](https://www.wikidata.org/wiki/Q1794) | 775,790 | フランクフルト・アム・マイン | マイン川沿いと同定（オーダー川沿いのフランクフルトではなく） |
| ブイヨン | Bouillon | ベルギー | town_village | [Q217216](https://www.wikidata.org/wiki/Q217216) | 5,353 | ブイヨン | ブイヨン城の町。検索では地区(section)エンティティを誤取得するためQID固定 |
| ブダペスト | Budapest | ハンガリー | city | [Q1781](https://www.wikidata.org/wiki/Q1781) | 1,685,209 | ブダペスト |  |
| ブラガ | Braga | ポルトガル | city | [Q83247](https://www.wikidata.org/wiki/Q83247) | 193,324 | ブラガ |  |
| ブラチスラバ | Bratislava | スロバキア | city | [Q1780](https://www.wikidata.org/wiki/Q1780) | 480,902 | ブラチスラヴァ |  |
| ブリュッセル | Brussels | ベルギー | city | [Q239](https://www.wikidata.org/wiki/Q239) | 195,546 | ブリュッセル市 |  |
| ブリーク | Brig-Glis | スイス | town_village | [Q15583](https://www.wikidata.org/wiki/Q15583) | 13,109 | ブリーク | ブリーク=Brig。自治体名はBrig-Glis |
| ブルゴス | Burgos | スペイン | city | [Q9580](https://www.wikidata.org/wiki/Q9580) | 177,402 | ブルゴス |  |
| ブルージュ | Bruges | ベルギー | city | [Q12994](https://www.wikidata.org/wiki/Q12994) | 118,509 | ブルッヘ |  |
| ブレッド | Bled | スロベニア | town_village | [Q202852](https://www.wikidata.org/wiki/Q202852) | 4,969 | ブレッド | ブレッド湖畔の町 |
| プラハ | Prague | チェコ | city | [Q1085](https://www.wikidata.org/wiki/Q1085) | 1,397,880 | プラハ |  |
| プリトビチェ | Plitvice Lakes National Park | クロアチア | natural_feature | [Q189849](https://www.wikidata.org/wiki/Q189849) | — | プリトヴィツェ湖群国立公園 |  |
| ヘルシンキ | Helsinki | フィンランド | city | [Q1757](https://www.wikidata.org/wiki/Q1757) | 694,392 | ヘルシンキ |  |
| ヘルシンゲル | Helsingør | デンマーク | town_village | [Q26881](https://www.wikidata.org/wiki/Q26881) | 47,364 | ヘルシンゲル | クロンボー城の町 |
| ベネチア | Venice | イタリア | city | [Q641](https://www.wikidata.org/wiki/Q641) | 250,369 | ヴェネツィア |  |
| ベネベント | Benevento | イタリア | town_village | [Q13437](https://www.wikidata.org/wiki/Q13437) | 56,201 | ベネヴェント |  |
| ベルン | Bern | スイス | city | [Q70](https://www.wikidata.org/wiki/Q70) | 136,988 | ベルン |  |
| ベローナ | Verona | イタリア | city | [Q2028](https://www.wikidata.org/wiki/Q2028) | 255,588 | ヴェローナ |  |
| ペニスコラ | Peníscola | スペイン | town_village | [Q845424](https://www.wikidata.org/wiki/Q845424) | 8,774 | ペニスコラ |  |
| ホークスヘッド | Hawkshead | イギリス | town_village | [Q691544](https://www.wikidata.org/wiki/Q691544) | 508 | ホークスヘッド | 湖水地方の村 |
| ポストイナ | Postojna | スロベニア | town_village | [Q15901](https://www.wikidata.org/wiki/Q15901) | 9,605 | ポストイナ | ポストイナ鍾乳洞の町。町として同定（鍾乳洞単体ではなく） |
| ポルト | Porto | ポルトガル | city | [Q36433](https://www.wikidata.org/wiki/Q36433) | 231,800 | ポルト |  |
| マテーラ | Matera | イタリア | town_village | [Q13616](https://www.wikidata.org/wiki/Q13616) | 59,685 | マテーラ |  |
| マドリード | Madrid | スペイン | city | [Q2807](https://www.wikidata.org/wiki/Q2807) | 3,506,730 | マドリード |  |
| マラガ | Málaga | スペイン | city | [Q8851](https://www.wikidata.org/wiki/Q8851) | 599,063 | マラガ |  |
| マリボル | Maribor | スロベニア | city | [Q1010](https://www.wikidata.org/wiki/Q1010) | 114,301 | マリボル |  |
| マルティニ | Martigny | スイス | town_village | [Q68956](https://www.wikidata.org/wiki/Q68956) | 18,301 | マルティニー |  |
| ミュンヘン | Munich | ドイツ | city | [Q1726](https://www.wikidata.org/wiki/Q1726) | 1,510,378 | ミュンヘン |  |
| ミラノ | Milan | イタリア | city | [Q490](https://www.wikidata.org/wiki/Q490) | 1,354,196 | ミラノ |  |
| モスタル | Mostar | ボスニア・ヘルツェゴビナ | city | [Q93347](https://www.wikidata.org/wiki/Q93347) | 105,448 | モスタル |  |
| モンサンミッシェル | Le Mont Saint-Michel | フランス | single_poi | [Q20892](https://www.wikidata.org/wiki/Q20892) | 23 | ル・モン＝サン＝ミシェル | 修道院のある島（コミューンでもある）。single_poiとして扱う |
| ヤイツェ | Jajce | ボスニア・ヘルツェゴビナ | town_village | [Q258429](https://www.wikidata.org/wiki/Q258429) | 12,000 | ヤイツェ | 滝のある歴史都市 |
| ヨーク | York | イギリス | city | [Q42462](https://www.wikidata.org/wiki/Q42462) | 208,400 | ヨーク |  |
| リスボン | Lisbon | ポルトガル | city | [Q597](https://www.wikidata.org/wiki/Q597) | 545,796 | リスボン |  |
| リュブリアナ | Ljubljana | スロベニア | city | [Q437](https://www.wikidata.org/wiki/Q437) | 284,293 | リュブリャナ |  |
| リューデスハイム | Rüdesheim am Rhein | ドイツ | town_village | [Q628118](https://www.wikidata.org/wiki/Q628118) | 10,180 | リューデスハイム・アム・ライン |  |
| ルガーノ | Lugano | スイス | town_village | [Q7024](https://www.wikidata.org/wiki/Q7024) | 63,495 | ルガーノ |  |
| ルクセンブルク | Luxembourg | ルクセンブルク | city | [Q1842](https://www.wikidata.org/wiki/Q1842) | 137,696 | ルクセンブルク市 | 国ではなくルクセンブルク市と同定 |
| ルーアン | Rouen | フランス | city | [Q30974](https://www.wikidata.org/wiki/Q30974) | 117,662 | ルーアン |  |
| レンヌ | Rennes | フランス | city | [Q647](https://www.wikidata.org/wiki/Q647) | 230,890 | レンヌ |  |
| ロンセスバジェス | Orreaga-Roncesvalles | スペイン | town_village | [Q917891](https://www.wikidata.org/wiki/Q917891) | 25 | ロンセスバーリェス | サンティアゴ巡礼路の起点の村 |
| ロンダ | Ronda | スペイン | town_village | [Q13153](https://www.wikidata.org/wiki/Q13153) | 33,671 | ロンダ |  |
| ロンドン | London | イギリス | city | [Q84](https://www.wikidata.org/wiki/Q84) | 8,799,728 | ロンドン |  |
| ローマ | Rome | イタリア | city | [Q220](https://www.wikidata.org/wiki/Q220) | 2,748,109 | ローマ |  |
| ヴェルナッツァ | Vernazza | イタリア | town_village | [Q270328](https://www.wikidata.org/wiki/Q270328) | 729 | ヴェルナッツァ | チンクエテッレの村 |
