# PenchantManufacture ImageAssets

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、**RadianN_kswg / ラジアン（柏木主税）による独自フォント PenchantManufacture** と **Claude による Agent 機能** によって制作するカスタム画像アセット／グリフ素材集です。

姉妹プロジェクト **Secvier_ImageAssets** と同じ設計思想・命名規則・ビルドフローを踏襲しています。本リポジトリは現時点では、フォントグリフを起点とした画像アセット生成パイプラインの **初期設定** を収録しています。

> **著作権者**: RadianN_kswg / ラジアン（柏木主税）
> **ライセンス**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)

---

## フォント収録グリフ

`_original-fonts/penchant-manufacture_v2.2-alpha/収録グリフ.txt` に記載の作者公式グリフ:

| カテゴリ           | 内容                                                          | 字数 |
| ------------------ | ------------------------------------------------------------- | ---- |
| ASCII可視記号ほか  | `U+0021`–`U+007E`（記号・数字・英大文字・英小文字）           | 94   |
| ギリシャ大文字     | Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω             | 24   |
| 曲がり引用符       | ' ' " "（U+2018 U+2019 U+201C U+201D）                        | 4    |

| 項目              | 値                                   |
| ----------------- | ------------------------------------ |
| フォント名        | PenchantManufacture (Regular)        |
| バージョン        | Version 1.004 (Fontself Maker 3.6.12) |
| Units per em      | 1000                                 |
| cmap マッピング数 | 184                                  |
| 実グリフ数        | 129                                  |

> **v2.2-alpha（Version 1.004）での変更**: 英小文字（a–z）が独立グリフとして
> **実装**されました（従来は大文字への再マップ）。小文字は x-height・アセンダ・
> ディセンダ（g/j/p/q/y）を持つため、デカール生成のトリミングは全グリフ一律の
> 固定縦バンドでベースラインを揃えています（後述）。一方で **ギリシャ小文字は
> 収録対象外**となりました。

抽出スクリプトは cmap 全コードポイント（184）を対象とし、空パスのグリフ
（スペース・NBSP・制御文字など）は自動でスキップして 129 の実グリフを書き出します。

---

## ディレクトリ構成

```
PenchantManufacture_ImageAssets/
├── assets/
│   └── fonts/
│       └── PenchantManufacture.otf   # ビルドで参照するフォント
├── src/
│   └── glyphs/                       # グリフ SVG（アウトライン化済み）
├── dist/
│   └── glyphs/                       # グリフ透過PNG（72px / 512px）
├── svg2png/
│   └── glyphs/                       # SVG の単純PNG変換（装飾なし）
├── scripts/
│   ├── inspect_font.py               # フォントグリフ検査
│   ├── extract_glyphs.py             # フォント → SVGアウトライン抽出
│   ├── export_png.py                 # SVG → PNG 変換
│   └── build.py                      # 全ステップ一括ビルド
├── docs/
│   └── glyph_map.txt                 # inspect_font.py が自動生成
├── _original-fonts/                  # 原本フォント（読み取り専用・.gitignore対象）
├── requirements.txt
├── .gitattributes
├── LICENSE
├── AGENTS.md                         # エージェント共通指示書
└── CLAUDE.md                         # Claude 向け補足
```

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

# グリフSVG抽出（まず対象確認 → 書き出し） → src/glyphs/
python scripts/extract_glyphs.py --dry-run
python scripts/extract_glyphs.py

# SVG → PNG変換 → dist/glyphs/, svg2png/glyphs/
python scripts/export_png.py

# 全ステップ一括ビルド（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py
```

---

## 出力仕様

| 項目             | 仕様                                  |
| ---------------- | ------------------------------------- |
| フォーマット     | PNG（RGBA）                           |
| グリフ SVG       | viewBox `0 0 512 512`、アウトライン化 |
| グリフ PNG       | 72 × 72 px / 512 × 512 px             |
| 背景             | 透過（alpha）                         |
| カラーモード     | sRGB                                  |

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
