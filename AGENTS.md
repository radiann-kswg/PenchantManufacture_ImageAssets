# AGENTS.md — PenchantManufacture ImageAssets 共通エージェント指示書

このファイルは **GitHub Copilot** および **Claude Code** の両エージェントが参照する
統合ワークスペース指示書です。ツール固有の補足は末尾のセクションを参照してください。

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

## 収録グリフ（PenchantManufacture v2.1-beta）

`_original-fonts/penchant-manufacture_v2.1-beta/収録グリフ.txt` に記載の作者公式グリフ:

```
ASCII可視記号・数字・英大文字 : U+0021–U+007E（94字）
ギリシャ大文字               : Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω（24字）
曲がり引用符                 : ' ' " "（U+2018 U+2019 U+201C U+201D）
```

フォント内部の cmap には上記に加え、小文字ラテン・アクセント付きラテン・ギリシャ小文字などの
マッピングも含まれる（多くは大文字グリフ等への再マップ）。

| 項目                 | 値                                        |
| -------------------- | ----------------------------------------- |
| フォント名           | PenchantManufacture (Regular)             |
| バージョン           | Version 1.003 (Fontself Maker 3.6.12)     |
| Units per em         | 1000                                      |
| cmap マッピング数    | 208                                       |
| 実グリフ数           | 103                                       |

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

```
PenchantManufacture_ImageAssets/
├── AGENTS.md                   ← 本ファイル（エージェント共通指示書）
├── CLAUDE.md                   ← Claude Code 向け補足（AGENTS.mdをインポート）
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot 向け補足
├── assets/
│   └── fonts/
│       └── PenchantManufacture.otf ← ビルド参照フォント（_original-fontsのコピー）
├── src/
│   └── glyphs/                 ← グリフ SVGソース（アウトライン化済み、extract_glyphs.py 出力）
├── dist/
│   └── glyphs/                 ← グリフ透過PNG（72px / 512px、export_png.py 出力）
├── svg2png/
│   └── glyphs/                 ← SVG の単純PNG変換（装飾なし、ユーティリティ用途）
├── scripts/
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/glyphs/ SVG
│   ├── export_png.py           ← SVG → PNG変換（dist/ と svg2png/）
│   └── build.py                ← 全ステップ一括ビルド
├── docs/
│   └── glyph_map.txt           ← inspect_font.py が自動生成
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
- 末尾のコードポイントにより、case-insensitive な Windows でも大文字/小文字グリフ
  （例: `A` U+0041 と `a` U+0061、`Alpha` U+0391 と `alpha` U+03B1）が衝突しない。

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
  ├─ [グリフ アウトライン抽出] scripts/extract_glyphs.py
  │         └─ src/glyphs/char_*.svg  （fontToolsのSVGPathPenで純粋パス出力）
  │
  └─ [PNG変換] scripts/export_png.py
            ├─ dist/glyphs/{stem}_72.png / {stem}_512.png  （絵文字出力）
            └─ svg2png/glyphs/{stem}.png                    （単純変換）
```

一括実行は `python scripts/build.py`（全ステップ）。`--step` で個別指定。

### ビルドコマンド早見表

```bash
pip install -r requirements.txt          # 初回セットアップ
python scripts/inspect_font.py           # フォント検査 → docs/glyph_map.txt
python scripts/extract_glyphs.py         # グリフSVG抽出 → src/glyphs/
python scripts/extract_glyphs.py --dry-run   # 抽出対象の確認（生成なし）
python scripts/export_png.py             # src/glyphs/*.svg → dist/glyphs/*.png
python scripts/build.py                  # 全ステップ一括
python scripts/build.py --dry-run        # 実行確認（ファイル生成なし）
python scripts/build.py --step extract   # 特定ステップのみ
```

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

## [Claude Code 向け補足]

- `docs/glyph_map.txt` を読んで利用可能グリフを把握してから作業すること
  （未生成の場合は `python scripts/inspect_font.py` を実行）
- Python依存の追加は `requirements.txt` に記録し、インストール手順も更新すること
- テスト実行: `python scripts/build.py --dry-run`

---

## [GitHub Copilot 向け補足]

- 補完提案はこのAGENTS.mdの命名規則・ディレクトリ規則に従うこと
- SVGの `viewBox` は常に `0 0 512 512`
- フォント参照は `assets/fonts/PenchantManufacture.otf` への相対パス、または
  アウトライン化（パス埋め込み）を使用すること
- 新規スクリプトは `scripts/` に配置し、`from __future__ import annotations` を先頭に記述すること
