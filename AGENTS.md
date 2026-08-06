# AGENTS.md — PenchantManufacture ImageAssets 共通エージェント指示書

このファイルは **Codex**、**Claude Code**、**GitHub Copilot** が共有する
PenchantManufacture リポジトリ固有指示の **唯一の正（SSOT）** です。
`CLAUDE.md` は `@AGENTS.md` の参照入口であり、詳細指示を重複記載しません。

姉妹プロジェクト **Secvier_ImageAssets** と同じ設計思想・命名規則・ビルドフローを踏襲します。

---

## プロジェクト概要

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、
**RadianN_kswg / ラジアン（柏木主税）による独自フォント PenchantManufacture** と
**Claude による Agent 機能** によって制作するカスタム画像アセット／グリフ素材リポジトリです。

現時点では **フォントグリフを起点とした画像アセット生成パイプラインの初期設定** を収録します。
フォント（`assets/fonts/PenchantManufacture.otf`）から各グリフをアウトライン化SVGとして抽出し、
透過PNGへ変換するまでの土台を提供します。

**著作権者**: RadianN_kswg / ラジアン（柏木主税） / **ライセンス**: CC BY 4.0

---

## 収録グリフ（PenchantManufacture v3.2-beta）

`_original-fonts/penchant-manufacture_v3.2-beta/収録グリフ.txt` に記載の作者公式グリフ:

```
ASCII可視記号・数字・英大文字・英小文字 : U+0021–U+007E（94字）
ギリシャ大文字                         : Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω（24字）
ギリシャ小文字                         : α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω（25字）
曲がり引用符                           : ' ' " "（U+2018 U+2019 U+201C U+201D）
上付き                                 : ⁰¹²³⁴⁵⁶⁷⁸⁹ ⁱ ⁿ ⁺ ⁻ ⁼ ⁽ ⁾（17字）
下付き                                 : ₀₁₂₃₄₅₆₇₈₉ ₙ ₊ ₋ ₌ ₍ ₎（16字）
キリル大文字                           : А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я（33字）
キリル小文字                           : а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я（33字）
ラテン拡張 大文字                      : À Á Â Ã Ä Å Ç È É Ê Ë Ì Í Î Ï Ñ Ò Ó Ô Õ Ö Ø Ù Ú Û Ü Ý Ÿ Ā Ē Ī Ō Ū（33字）
ラテン拡張 小文字                      : à á â ã ä å ç è é ê ë ì í î ï ñ ò ó ô õ ö ø ù ú û ü ý ÿ ā ē ī ō ū（33字）
合字・特殊                             : Æ æ Œ œ ẞ ß ı（7字）
算術記号                               : × ÷（2字）
```

v3.0-release（Version 1.005）で **ギリシャ小文字 α–ω と ß が新規追加**され、
v3.1-release（Version 1.007）で **上付き17字・下付き16字・キリル66字が追加**、
α の字形が修正された。
v3.2-beta で **アクセント付きラテン66字・合字系7字・`×` `÷` の計74グリフが追加**され、
`ß` の字形が変更された。英小文字 a–z は独立グリフとして x-height・アセンダ・
ディセンダ（g/j/p/q/y は base line 下 ~101/1000 まで伸びる）を持つ。

### アクセント記号対応（v3.2-beta）

v3.1 以前は cmap にアクセント付きラテン 56 コードポイントが登録されていたが、
**すべて無印の基底グリフへ再マップ**されていた（`café` が `cafe` と表示される状態）。
v3.2-beta でこの 56 字すべてに実アウトラインが与えられ、さらに `Œ œ Ā–Ū ā–ū Æ æ ẞ ı`
が新規 cmap として追加された。**`glyph_aliases.json` の異体字エイリアスは 0 件**になった。

対応言語: 英語（米・英）／ドイツ語／フランス語／イタリア語／日本語ローマ字（ヘボン式長音
`ā ē ī ō ū`・訓令式 `â ê î ô û`）に加え、スペイン語・ポルトガル語・北欧語の大半。
詳細は [docs/DIACRITIC_EXTENSION_PLAN.md] 参照。**ギリシャ文字のアクセント（モノトニック
20字）は未着手**。

**分音記号の配置帯**（既存の縦バンドを侵さないための規格。作字時に順守すること）

| 帯 | y 範囲 | 高さ | 用途 |
| --- | --- | --- | --- |
| 上帯（大文字用） | 660.5 – **792.5** | 132 | `Ä Ö Ü À É Î Ā` 等。上端は `Ё Й` と同一 |
| 中帯（小文字用） | 462.3 – **594.4** | 132 | `ä ö ü à é î ā` 等。上端は `ё й` と同一 |
| 下帯（下付き用） | **−198.1** – 0 | 198 | `Ç ç` のセディーユ |

上帯と中帯は高さが等しく、**記号パーツを 198.2 units 平行移動しただけ**の関係にある。
`ì î ï í ī` は `ı`（dotlessi, U+0131）を土台とし、i のドットを除去してある。

上付き・下付きは当初「合成」で作る計画だったが、**作者が実グリフとして作字した**ため
`generate_decal.py` に合成処理は不要（既存グリフと同じ経路でそのまま処理される）。

### 縦方向の配置（v3.1 で変更・既存絵文字の見た目に影響）

`Ё`(U+0401) と `Й`(U+0419) の分音記号は **y=792.5** まで伸び、アセンダー 660 を
大きく超える。旧実装は SVG のベースラインをアセンダー固定で置いていたため、
この 2 字は**頭が viewBox の外に出て切り落とされ、`Е`/`И` と 1px も違わない画像**に
なっていた。`compute_vertical_fit` で **実インクの上端**を基準に全グリフ一律で
ベースラインを 67.9px 下げ、確実に収まるようにした。

その結果、全グリフ共通の固定縦バンドが 440px → 508px（+15.5%）に広がり、
**既存の全グリフが従来比 86.6% のサイズで描画される**。字面どうしの縦位置関係は
正しく保たれるが、v3.0 以前にビルドした絵文字とは見た目が変わる。

> **既存絵文字の入れ替えが必要**
> - Misskey: 一括インポート zip で全点が置換されるため追加作業は不要
> - Discord: 個別アップロードのため、登録済みの絵文字は手動で再アップロードが必要

スケールは `viewbox / upm` を維持しており、字面の総高が em を超える場合にのみ
自動縮小する。メトリクス値（`sTypoDescender` 等）は基準に使わない
（v3.1 の descender は −400 だが実インクは −198 までしか無く、
メトリクスを基準にすると不要な縮小が入るため）。

**v3.2-beta では縦バンドは変化していない。** 全グリフのインクは `−198.2 … 792.5`
（990.7 / 1000 upm）に収まり、v3.1 と 1 unit も違わない。追加した 74 グリフの分音記号が
既存の `Ё Й` の天井 792.5 と `g p y` の底 −198.2 を侵さないよう設計されているため。
既存グリフで出力 PNG が変わったのは **`ß` の 1 字のみ**（作者による字形変更）。

> **フォント更新時に必ず確認すること**
> 新しいグリフのインクが `y > 792.5` または `y < −198.2` に出ると、
> `compute_vertical_fit` が全グリフを再スケールし、**Discord 登録済み絵文字の全点
> 手動再アップロード**が発生する（v3.1 で実際に起きた）。逸脱チェックは
> [docs/DIACRITIC_EXTENSION_PLAN.md §2.3] のスニペットで機械的に行える。

### 制作途中グリフの除外

作者が調整中の字は、絵文字として公開すると差し替え時に登録済み絵文字を作り直す羽目に
なるため、`extract_glyphs.py` の `PENDING_RANGES` に挙げた範囲を **既定でスキップ** する。
`--include-pending` で一時的に含められる。

**現在 `PENDING_RANGES` は空**（v3.1-release でキリル全66字が確定し除外を解除）。
今後グリフが作字中の状態で追加された場合は、この表に範囲を足すだけでビルド対象外にできる
（他スクリプトの変更は不要）。

### 別バージョンのフォントでビルドする

フォントを読むのは inspect / extract の 2 ステップだけなので、`--font` を渡せば
`assets/fonts/` を差し替えずに任意の OTF でビルドできる。開発版フォントの試写に使う。

```bash
python scripts/build.py --font "_original-fonts/.develop/penchant-manufacture_vX.Y-develop/PenchantManufacture.otf"
```

> `_original-fonts/` は `.gitignore` 対象のため、開発版でのビルドは**そのフォントを持つ
> 環境でのみ**再現できる。release になったら `assets/fonts/` を差し替え、
> `--font` 指定なしの通常ビルドへ戻すこと（差し替えはコミット履歴を残す）。

### 重複排除の方針（同一画像を二重生成しない）

cmap は 327 コードポイントだが、フォント上は別グリフでも**絵文字サイズで描画が一致する字**
を含むため、素朴に全コードポイントを書き出すと同じ画像が別名で二重生成される。
SNS カスタム絵文字（Discord・Misskey）向けには同一画像の重複登録を避けたい。
本パイプラインは 2 段でこれを排除する:

1. **cmap 再マップの統合（`extract_glyphs.py`）** — 異なるコードポイントが同一グリフを
   指す場合、グリフ名でユニーク化して 1 枚だけ SVG 化し、統合した異体字は
   `docs/glyph_aliases.json` に検索エイリアスとして記録する。
   v3.1 以前はアクセント付きラテン 56 字（À Á Â … ø ù … Ÿ）が基底グリフ
   （A/E/I/O/U/Y/C/N とその小文字）への再マップだったためここで 56 件が統合されていたが、
   **v3.2-beta で全 56 字に実アウトラインが与えられ、統合件数は 0 になった**。
   現在の正規グリフは **321 字**（機構自体は将来の再マップに備えて残す）。
2. **描画一致の統合（`generate_decal.py` → `dedupe_renders`）** — フォント上は別グリフ
   でも絵文字サイズで描画が完全一致する字は、出力 PNG を正規側 1 枚に統合する。
   **17 字が 12 グループへ統合され、絵文字は正味 304 字**となる。全スキーム×全サイズで
   バイト完全一致する場合のみ統合する安全側の判定。統合表は
   `docs/glyph_render_merges.json`。**ソース SVG（`src/glyphs/`）は 321 字を温存**し、
   各文字セットの独立性を保つ（統合は出力 PNG と絵文字登録のみ）。
   統合対象は v3.1 と同一で、**v3.2-beta の追加 74 字はいずれも統合されない**
   （`Ë` と `Ё` は同一字面に見えるが、輪郭構成が異なりバイト一致しない）。

   | 正規 | 統合される字 |
   | --- | --- |
   | `A` | `А`(キリル) `Α`(ギリシャ) |
   | `B` | `Β` `В` |
   | `C` | `С` |
   | `E` | `Ε` `Е` |
   | `O` | `О` `Ο` |
   | `T` | `Т` |
   | `c` | `с` |
   | `o` | `о` `ο` |
   | `Η`(ギリシャ) | `Н` |
   | `Κ`(ギリシャ) | `К` |
   | `Μ`(ギリシャ) | `М` |
   | `Χ`(ギリシャ) | `Х` |

   キリルの同形字はラテン／ギリシャ側へ統合されるが、**トークン（`yua` など）と
   リテラル字（`А`）は正規側の検索エイリアスに残る**ため、型番検索での引きやすさは失われない。

| 段階                       | 対象         | v3.0-release | v3.1-release | v3.2-beta |
| -------------------------- | ------------ | ------------ | ------------ | --------- |
| cmap マッピング            | —            | 210          | 309          | 327       |
| 実グリフ                   | —            | 155          | 253          | 328       |
| SVG ソース（cmap再マップ統合後） | src/glyphs   | **148**      | **247**      | **321**   |
| 絵文字 PNG（描画一致統合後）     | dist/glyphs_decal | **143** | **230**      | **304**   |

| 項目                 | 値                                        |
| -------------------- | ----------------------------------------- |
| フォント名           | PenchantManufacture (Regular)             |
| リリース             | v3.2-beta (2026-08-06)                    |
| バージョン文字列     | Version 1.007 (Fontself Maker 3.6.12)     |
| Units per em         | 1000                                      |
| cap height / x-height | 661 / 462                                |
| 実インク上端 / 下端  | 792.5 / −198.2（帯 990.7 = 99.1% em）     |
| cmap マッピング数    | 327                                       |
| 実グリフ数           | 328                                       |

> **既知の不整合**: v3.2-beta の `name` テーブル（nameID 3/5）と `head.fontRevision` は
> v3.1-release と同一の `1.007` / `1.0` のまま更新されていない。次の release 化の際に
> 作者へ版数の繰り上げ（1.008）を依頼すること。パイプラインは版数を参照しないため
> ビルドには影響しない。

> フォントが更新されたら `python scripts/inspect_font.py` を再実行し、
> `docs/glyph_map.txt` で差分を確認すること。

---

## 権限・ライセンス（最優先）

- **著作権者**：RadianN_kswg / ラジアン（柏木主税）
- **ライセンス**：CC BY 4.0
- PenchantManufacture フォントのグリフは著作者の独自創作物。
  第三者フォント・商用グリフのグリフパスを流用することを **絶対に行わないこと**。
- すべての出力ファイルにクレジット属性を保持すること。
- `_original-fonts/` 内のファイルは **読み取り専用**。ビルドスクリプトから変更・削除禁止。

---

## ディレクトリ構成

姉妹プロジェクト **Secvier** のビルド構成（`dist/{カテゴリ}/{バリアント}/` ＋
`_exported-dist/` への Misskey 一括インポート zip）に揃えている。

```
PenchantManufacture_ImageAssets/
├── AGENTS.md                   ← 本ファイル（エージェント共通指示書）
├── CLAUDE.md                   ← Claude Code 互換入口（@AGENTS.md のみ）
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot 向け補足
├── assets/
│   └── fonts/
│       └── PenchantManufacture.otf ← ビルド参照フォント（_original-fontsのコピー）
├── src/
│   └── glyphs/                 ← グリフ SVGソース 321字（アウトライン化済み、extract_glyphs.py 出力）
├── dist/
│   ├── glyphs/                 ← グリフ透過PNG（72px / 512px、装飾なし、export_png.py 出力）
│   ├── glyphs_decal/{variant}/       ← 工業デカール 幅可変PNG（Misskey向け・マスター）
│   ├── glyphs_decal_square/{variant}/ ← 工業デカール 正方形PNG（Discord向け）
│   │                               variant = sumi（既定）/ rust / hazard / patina / nickel
│   └── glyphs_spacer/                ← スペーサ 完全透過PNG（バリアント非依存・Misskey専用）
├── svg2png/
│   └── glyphs/                 ← SVG の単純PNG変換（装飾なし、ユーティリティ用途）
├── scripts/
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/glyphs/ SVG（重複排除＋制作途中グリフ除外）
│   ├── export_png.py           ← SVG → PNG変換（dist/glyphs, svg2png/）
│   ├── generate_decal.py       ← 工業デカール生成（幅可変＋正方形、描画一致統合）
│   ├── generate_spacers.py     ← スペーサ透過PNG生成（バリアント非依存、Pillowのみ）
│   ├── glyph_tokens.py         ← 字体トークン／後置タグ／サブカテゴリ 命名様式のSSOT
│   ├── build_misskey_zip.py    ← Misskey一括インポートzip生成 → _exported-dist/
│   └── build.py                ← 全ステップ一括ビルド
├── docs/
│   ├── glyph_map.txt           ← inspect_font.py が自動生成
│   ├── glyph_aliases.json      ← 異体字→正規グリフ 対応表（extract_glyphs.py 生成）
│   ├── glyph_render_merges.json ← 描画一致グリフ 統合表（generate_decal.py 生成）
│   ├── glyph_spacers.json      ← スペーサ対応表（generate_spacers.py 生成）
│   ├── EMOJI_TECHCODE_SPEC.md   ← 絵文字 命名様式（確定）
│   ├── GLYPH_EXTENSION_PLAN.md  ← 追加グリフ計画
│   ├── DIACRITIC_EXTENSION_PLAN.md ← アクセント記号 収録計画・配置帯規格
│   └── DECAL_VARIANTS.md        ← 工業デカール バリアント仕様
├── _original-fonts/            ← 原本（読み取り専用、.gitignore対象）
├── _exported-dist/             ← エクスポートzip格納（.gitignore対象）
├── requirements.txt
├── .gitattributes
└── LICENSE
```

---

## ファイル命名規則

| 対象                        | 命名パターン                          | 例                                |
| --------------------------- | ------------------------------------- | --------------------------------- |
| グリフ SVG（src/glyphs）    | `char_{AGL名}_{コードポイント}.svg`   | `char_A_0041.svg`, `char_Alpha_0391.svg` |
| PNG出力（dist/glyphs）      | `{stem}_72.png` / `{stem}_512.png`    | `char_A_0041_512.png`             |
| 単純PNG変換（svg2png）      | `{stem}.png`                          | `char_A_0041.png`                 |

### 命名の要点

- ステムは `char_{AGL名}_{コードポイント16進4桁}` 形式。
- **AGL名**（Adobe Glyph List）を優先（`A`, `zero`, `exclam`, `Alpha`, `quoteleft` など）。
  AGL に無い場合はフォントのグリフ名、それも不適なら `uniXXXX` にフォールバック。
  AGL 名を持たない字は `glyph_tokens.GLYPH_NAME_OVERRIDES` で読める名に揃える
  （例 U+1E9E `ẞ` はフォント側 `uni1e9e` → `Germandbls`）。
- 末尾のコードポイントにより、case-insensitive な Windows でも大文字/小文字グリフ
  （例: `A` U+0041 と `a` U+0061、`Alpha` U+0391 と `alpha` U+03B1、
  `Germandbls` U+1E9E と `germandbls` U+00DF）が衝突しない。

> **絵文字名（`glyph_token`）は AGL 名フォールバックに頼らないこと。**
> フォールバックは AGL を小文字化するため、`Adieresis`(Ä) と `adieresis`(ä) が
> 同一トークンへ潰れ、Misskey の絵文字名が衝突する。ラテン拡張は
> `{u|l}{基底字}{記号2字}` の固定 4 字（`uadi` / `ladi`）で大小を分ける。
> 新しい字種を追加するときは `scripts/glyph_tokens.py` に必ずトークン定義を足す。

---

## 技術スタック

- **言語**: Python 3.11+
- **主要ライブラリ**:
  - `fontTools` — フォントグリフ解析・アウトライン抽出（`SVGPathPen`）、AGL名解決
  - `cairosvg` — SVG→PNG変換
  - `Pillow` — PNG後処理・保存
  - `click` — CLIインターフェース
  - `svgwrite` — SVGファイル生成補助（将来の合成SVG用）
- **フォントファイル**: `assets/fonts/PenchantManufacture.otf`

---

## ビルドフロー

```
PenchantManufacture.otf
  │
  ├─ [検査] scripts/inspect_font.py
  │         └─ docs/glyph_map.txt
  │
  ├─ [グリフ アウトライン抽出＋重複排除] scripts/extract_glyphs.py
  │         ├─ src/glyphs/char_*.svg  （正規321字、fontToolsのSVGPathPenで純粋パス）
  │         └─ docs/glyph_aliases.json（異体字→正規グリフ 対応表）
  │
  ├─ [単純PNG変換] scripts/export_png.py
  │         ├─ dist/glyphs/{stem}_72.png / {stem}_512.png
  │         └─ svg2png/glyphs/{stem}.png
  │
  ├─ [工業デカール生成＋描画一致統合] scripts/generate_decal.py
  │         ├─ dist/glyphs_decal/{variant}/{stem}_{512,128}.png        （幅可変・Misskey）
  │         ├─ dist/glyphs_decal_square/{variant}/{stem}_{512,128}.png （正方形・Discord）
  │         └─ docs/glyph_render_merges.json（描画一致グリフ 統合表）
  │
  ├─ [スペーサ生成] scripts/generate_spacers.py  ※ decal の出力寸法を実測するため decal の後
  │         ├─ dist/glyphs_spacer/spacer_{spc,gap}_{512,128}.png（完全透過・バリアント非依存）
  │         └─ docs/glyph_spacers.json（スペーサ対応表）
  │
  └─ [Misskey zip] scripts/build_misskey_zip.py
            └─ _exported-dist/penchant-misskey-{timestamp}.zip（meta.json付き）
```

一括実行は `python scripts/build.py`（全ステップ）。`--step` で個別指定。
ステップ順: inspect → extract → png → svg2png → decal → spacer → misskey_zip。

### ビルドコマンド早見表

```bash
pip install -r requirements.txt          # 初回セットアップ（numpy / scipy 含む）
python scripts/inspect_font.py           # フォント検査 → docs/glyph_map.txt
python scripts/extract_glyphs.py --dry-run   # 抽出対象の確認（生成なし）
python scripts/extract_glyphs.py         # グリフSVG抽出（重複排除＋制作途中グリフ除外）
python scripts/extract_glyphs.py --include-pending  # 制作途中グリフ（キリル）も抽出
python scripts/export_png.py             # src/glyphs/*.svg → dist/glyphs/, svg2png/
python scripts/generate_decal.py         # 工業デカール（幅可変＋正方形）＋描画一致統合
python scripts/generate_decal.py -v rust # 単一スキームのみ（統合はスキップ）
python scripts/generate_spacers.py       # スペーサ透過PNG（decal の後に実行）
python scripts/build_misskey_zip.py      # Misskey一括インポートzip → _exported-dist/
python scripts/build.py                  # 全ステップ一括
python scripts/build.py --dry-run        # 実行確認（ファイル生成なし）
python scripts/build.py --step decal     # 特定ステップのみ
python scripts/build.py --font "_original-fonts/.develop/penchant-manufacture_v3.1.0-develop/PenchantManufacture.otf"
```

> `generate_decal.py` の描画一致統合は、統合先グリフの PNG を**削除**して重複を消す。
> 読み取り専用マウント等で削除に失敗すると WARN が出るが、`build_misskey_zip.py` は
> `docs/glyph_render_merges.json` を見て消し残りを除外するため zip は正しく作られる。
> 消し残った PNG は次回の `generate_decal.py` 実行時に削除される。

### SNS カスタム絵文字 登録の前提

- **Misskey**: `_exported-dist/penchant-misskey-*.zip` を管理画面から一括インポート。
  非正方形の絵文字をそのまま扱えるため **幅可変版**（字面本来の比率）を収録する。
  meta.json のカテゴリは `PenchantManufacture/工業デカール_{和名}/{字種}`、
  各絵文字に基底文字・異体字（ギリシャ同形など）・バリアント名を alias 付与。
  収録点数は **304字 × 5バリアント ＋ スペーサ2 = 1522点**（v3.2-beta ビルド時）。
  字種サブカテゴリに v3.2-beta で **ラテン拡張大文字 / ラテン拡張小文字** を追加。
- **Discord**: 絵文字は正方形スロットで表示されるため **正方形版**
  （`dist/glyphs_decal_square/{variant}/*_128.png`）を個別アップロードする。
  1 ファイル 256KB 以下（本出力は全て充足）。
- **スペーサ（`spcp` 全角 / `gapp` 半角）は Misskey 専用**。バリアント非依存の完全透過PNGで、
  幅可変表示が効く Misskey でのみ余白幅の差が意味を持つ。Discord は正方形パディングで
  両者が同一画像に潰れるため対象外（正方形版を生成しない）。詳細は
  [GLYPH_EXTENSION_PLAN.md](docs/GLYPH_EXTENSION_PLAN.md) §3。

---

## SVG制作仕様

- **viewBox**: `0 0 512 512`（正方形）
- **背景**: 透過（alpha）
- **カラーモード**: sRGB
- **フォント依存の排除**:
  - `src/glyphs/` の SVG は `extract_glyphs.py` が生成するアウトライン化済みパス。
    外部フォント参照を一切持たない（`<path d="...">` のみ）。
- **PNG出力サイズ**: 72px（標準絵文字）/ 512px（高解像度）
- 出力は `scripts/build.py` / `scripts/export_png.py` 経由で `dist/` `svg2png/` に配置すること。

---

## Pythonコーディング規則

- スタイル: PEP 8 準拠
- 型ヒント: 全関数に付与（`from __future__ import annotations`）
- docstring: Google スタイル（日本語可）
- エラーハンドリング: フォント読み込み・SVG変換は必要に応じて `try/except` でラップ

```python
from __future__ import annotations
from pathlib import Path

def render_glyph(char: str, output: Path, size: int = 512) -> None:
    """指定文字のグリフをPNGとして書き出す。

    Args:
        char: レンダリングする文字（PenchantManufacture フォントのグリフ）
        output: 出力PNGパス
        size: 出力サイズ（px）
    """
    ...
```

---

## コミットメッセージ規約

```
<type>(<scope>): <subject>
```

- **type**: `feat` `fix` `build` `docs` `chore` `style`
- **scope**: `glyphs` `scripts` `assets` `docs`
- **言語**: 日本語・英語いずれも可（混在可）

例:

```
feat(glyphs): add outlined SVG extraction for full cmap
build(scripts): add extract_glyphs.py with AGL-based safe naming
docs: add AGENTS.md / CLAUDE.md for PenchantManufacture setup
```

---

## 絶対に行わないこと（全エージェント共通）

- `_original-fonts/` 内ファイルの変更・削除
- PenchantManufacture 以外の商用フォント・第三者フォントのグリフパス流用
- `dist/` `svg2png/` への直接ファイル配置（スクリプト経由のみ）
- ライセンス表記（CC BY 4.0 / 著作者名）の削除・改ざん
- `assets/fonts/PenchantManufacture.otf` の上書き（差し替えはコミット履歴を残すこと）

---

## 作業開始時の共通チェック

- `docs/glyph_map.txt` を読んで利用可能グリフを把握してから作業すること
  （未生成の場合は `python scripts/inspect_font.py` を実行）
- Python依存の追加は `requirements.txt` に記録し、インストール手順も更新すること
- テスト実行: `python scripts/build.py --dry-run`
