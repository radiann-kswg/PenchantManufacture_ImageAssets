# PenchantManufacture ImageAssets

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、**RadianN_kswg / ラジアン（柏木主税）による独自フォント PenchantManufacture** と **Claude による Agent 機能** によって制作するカスタム画像アセット／グリフ素材集です。

姉妹プロジェクト **Secvier_ImageAssets** と同じ設計思想・命名規則・ビルドフローを踏襲しています。本リポジトリは現時点では、フォントグリフを起点とした画像アセット生成パイプラインの **初期設定** を収録しています。

> **著作権者**: RadianN_kswg / ラジアン（柏木主税）
> **ライセンス**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)

---

## フォント収録グリフ

`_original-fonts/penchant-manufacture_v3.0-release/収録グリフ.txt` に記載の作者公式グリフ:

| カテゴリ           | 内容                                                          | 字数 |
| ------------------ | ------------------------------------------------------------- | ---- |
| ASCII可視記号ほか  | `U+0021`–`U+007E`（記号・数字・英大文字・英小文字）           | 94   |
| ギリシャ大文字     | Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω             | 24   |
| ギリシャ小文字     | α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω             | 25   |
| 曲がり引用符ほか   | ' ' " "（U+2018 U+2019 U+201C U+201D）、ß（U+00DF）           | 5    |

| 項目              | 値                                   |
| ----------------- | ------------------------------------ |
| フォント名        | PenchantManufacture (Regular)        |
| バージョン        | Version 1.005 (Fontself Maker 3.6.12) |
| Units per em      | 1000                                 |
| cmap マッピング数 | 210                                  |
| 実グリフ数        | 155                                  |

> **v3.0-release（Version 1.005）での変更**: ギリシャ小文字（α–ω）と ß が新規に
> 追加され、一部グリフの形状が修正されました。英小文字（a–z）は独立グリフとして
> x-height・アセンダ・ディセンダ（g/j/p/q/y）を持つため、デカール生成のトリミングは
> 全グリフ一律の固定縦バンドでベースラインを揃えています（後述）。

抽出スクリプトは cmap 全コードポイント（210）を走査しますが、**同一グリフへ再マップ
されたコードポイントを 1 枚に統合**します。アクセント付きラテン 56 字（À Á … ÿ Ÿ）は
基底グリフ（A/E/I/O/U/Y/C/N とその小文字）への再マップのため、正規グリフ **148 字**のみを
SVG 化し、統合した異体字は `docs/glyph_aliases.json` に検索エイリアスとして記録します。
さらに工業デカール生成では、絵文字サイズで描画が完全一致するギリシャ同形 5 組
（A=Α, B=Β, E=Ε, O=Ο, o=ο）を出力 PNG 上で統合し、**絵文字は正味 143 字**になります
（統合表 `docs/glyph_render_merges.json`。ソース SVG の 148 字は温存）。この 2 段の
重複排除により、**同一画像が別名で二重登録されることを防ぎます**。

---

## ディレクトリ構成

姉妹プロジェクト **Secvier** のビルド構成（`dist/{カテゴリ}/{バリアント}/` ＋
`_exported-dist/` の Misskey 一括インポート zip）に揃えています。

```
PenchantManufacture_ImageAssets/
├── assets/
│   └── fonts/
│       └── PenchantManufacture.otf   # ビルドで参照するフォント
├── src/
│   └── glyphs/                       # グリフ SVG 148字（アウトライン化済み）
├── dist/
│   ├── glyphs/                       # グリフ透過PNG（72px / 512px、装飾なし）
│   ├── glyphs_decal/{variant}/       # 工業デカール 幅可変PNG（Misskey向け・マスター）
│   └── glyphs_decal_square/{variant}/ # 工業デカール 正方形PNG（Discord向け）
├── svg2png/
│   └── glyphs/                       # SVG の単純PNG変換（装飾なし）
├── scripts/
│   ├── inspect_font.py               # フォントグリフ検査
│   ├── extract_glyphs.py             # フォント → SVGアウトライン抽出（重複排除）
│   ├── export_png.py                 # SVG → PNG 変換
│   ├── generate_decal.py             # 工業デカール生成（幅可変＋正方形／描画一致統合）
│   ├── build_misskey_zip.py          # Misskey一括インポートzip生成
│   └── build.py                      # 全ステップ一括ビルド
├── docs/
│   ├── glyph_map.txt                 # inspect_font.py が自動生成
│   ├── glyph_aliases.json            # 異体字→正規グリフ 対応表
│   ├── glyph_render_merges.json      # 描画一致グリフ 統合表
│   └── DECAL_VARIANTS.md             # 工業デカール バリアント仕様
├── _original-fonts/                  # 原本フォント（読み取り専用・.gitignore対象）
├── _exported-dist/                   # エクスポートzip格納（.gitignore対象）
├── requirements.txt
├── .gitattributes
├── LICENSE
├── AGENTS.md                         # エージェント共通指示書
└── CLAUDE.md                         # Claude 向け補足
```

variant = `rust`（酸鉄）/ `hazard`（警戒）/ `patina`（緑青真鍮）/ `nickel`（白銅燐光）

---

## セットアップ

### 必要環境

- Python 3.11+
- 依存ライブラリ（`requirements.txt` 参照）

```bash
pip install -r requirements.txt
```

### グリフアセットの生成

```bash
# フォント検査 → docs/glyph_map.txt
python scripts/inspect_font.py

# グリフSVG抽出（重複排除。まず対象確認 → 書き出し） → src/glyphs/, docs/glyph_aliases.json
python scripts/extract_glyphs.py --dry-run
python scripts/extract_glyphs.py

# SVG → PNG変換 → dist/glyphs/, svg2png/glyphs/
python scripts/export_png.py

# 工業デカール生成（幅可変＋正方形／描画一致統合） → dist/glyphs_decal[_square]/
python scripts/generate_decal.py

# Misskey一括インポートzip → _exported-dist/
python scripts/build_misskey_zip.py

# 全ステップ一括ビルド（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py
```

### SNS カスタム絵文字の登録

- **Misskey**: `_exported-dist/penchant-misskey-*.zip` を管理画面から一括インポート
  （非正方形をそのまま扱えるため幅可変版を収録。カテゴリ・エイリアス付き）。
- **Discord**: `dist/glyphs_decal_square/{variant}/*_128.png` を個別アップロード
  （正方形スロット向け。1ファイル 256KB 以下）。

---

## 出力仕様

| 項目               | 仕様                                                       |
| ------------------ | ---------------------------------------------------------- |
| フォーマット       | PNG（RGBA）                                                 |
| グリフ SVG         | viewBox `0 0 512 512`、アウトライン化                       |
| グリフ PNG（装飾なし） | 72 × 72 px / 512 × 512 px                               |
| デカール（Misskey） | 高さ 512 / 128 px・**幅可変**（字面比率を維持）            |
| デカール（Discord） | 512 / 128 px の**正方形**（中央寄せパディング）           |
| 背景               | 透過（alpha）                                              |
| カラーモード       | sRGB                                                       |

ファイル命名: `char_{AGL名}_{コードポイント}.svg`（例: `char_A_0041.svg`, `char_Alpha_0391.svg`）。
末尾のコードポイントにより、case-insensitive なファイルシステムでも大文字/小文字グリフが衝突しません。

---

## クレジット

### フォント

**PenchantManufacture** — RadianN_kswg / ラジアン（柏木主税）による独自作字フォント。
本リポジトリの画像アセットはこのフォントのグリフをベースに制作されています。

### 生成ツール

**Claude（Anthropic）** — Agent 機能を使用してアセットの設計・スクリプト生成を行っています。
本プロジェクトの制作は Claude Cowork による自律エージェント作業によって実施されました。

---

## ライセンス

本アセット群（PenchantManufacture フォントグリフ派生部分および独自デザイン部分）は
**CC BY 4.0** で公開されています。

**[Creative Commons 表示 4.0 国際](https://creativecommons.org/licenses/by/4.0/deed.ja)**

著作者：RadianN_kswg / ラジアン（柏木主税）

利用時のクレジット表記例:

```
PenchantManufacture image assets by RadianN_kswg / ラジアン（柏木主税）
CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
```
