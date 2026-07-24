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

## 収録グリフ（PenchantManufacture v3.0-release）

`_original-fonts/penchant-manufacture_v3.0-release/収録グリフ.txt` に記載の作者公式グリフ:

```
ASCII可視記号・数字・英大文字・英小文字 : U+0021–U+007E（94字）
ギリシャ大文字                         : Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω（24字）
ギリシャ小文字                         : α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω（25字）
曲がり引用符・その他                   : ' ' " "（U+2018 U+2019 U+201C U+201D）、ß（U+00DF）
```

v3.0-release（Version 1.005）で **ギリシャ小文字 α–ω と ß が新規追加**され、
一部グリフの形状が修正された。英小文字 a–z は独立グリフとして x-height・アセンダ・
ディセンダ（g/j/p/q/y は base line 下 ~101/1000 まで伸びる）を持つ。cmap には
アクセント付きラテンのマッピングも含まれる（多くは大文字／小文字グリフへの再マップ）。

### 重複排除の方針（同一画像を二重生成しない）

cmap は 210 コードポイントだが、**同一グリフ（同一アウトライン）へ再マップされた
コードポイントを含む**ため、素朴に全コードポイントを書き出すと同じ画像が別名で二重
生成される。SNS カスタム絵文字（Discord・Misskey）向けには同一画像の重複登録を避けたい。
本パイプラインは 2 段でこれを排除する:

1. **cmap 再マップの統合（`extract_glyphs.py`）** — アクセント付きラテン 56 字
   （À Á Â … ø ù … Ÿ など）は基底グリフ（A/E/I/O/U/Y/C/N とその小文字）への再マップ。
   グリフ名でユニーク化し、**正規グリフ 148 字のみ** SVG 化する。統合した異体字は
   `docs/glyph_aliases.json` に検索エイリアスとして記録する。
2. **描画一致の統合（`generate_decal.py` → `dedupe_renders`）** — フォント上は別グリフ
   でも絵文字サイズで描画が完全一致する字（ラテンとギリシャの同形: A=Α, B=Β, E=Ε,
   O=Ο, o=ο の 5 組）は、出力 PNG を正規側 1 枚に統合。**絵文字は正味 143 字**となる。
   統合表は `docs/glyph_render_merges.json`。**ソース SVG（`src/glyphs/`）は 148 字を
   温存**し、ギリシャ文字セットの独立性を保つ（統合は出力 PNG と絵文字登録のみ）。

| 段階                       | 対象         | 結果         |
| -------------------------- | ------------ | ------------ |
| cmap マッピング            | —            | 210          |
| 実グリフ                   | —            | 155          |
| SVG ソース（cmap再マップ統合後） | src/glyphs   | **148**      |
| 絵文字 PNG（描画一致統合後）     | dist/glyphs_decal | **143** |

| 項目                 | 値                                        |
| -------------------- | ----------------------------------------- |
| フォント名           | PenchantManufacture (Regular)             |
| バージョン           | Version 1.005 (Fontself Maker 3.6.12)     |
| Units per em         | 1000                                      |
| cmap マッピング数    | 210                                       |
| 実グリフ数           | 155                                       |

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
│   └── glyphs/                 ← グリフ SVGソース 148字（アウトライン化済み、extract_glyphs.py 出力）
├── dist/
│   ├── glyphs/                 ← グリフ透過PNG（72px / 512px、装飾なし、export_png.py 出力）
│   ├── glyphs_decal/{variant}/       ← 工業デカール 幅可変PNG（Misskey向け・マスター）
│   └── glyphs_decal_square/{variant}/ ← 工業デカール 正方形PNG（Discord向け）
│                                   variant = rust / hazard / patina / nickel
├── svg2png/
│   └── glyphs/                 ← SVG の単純PNG変換（装飾なし、ユーティリティ用途）
├── scripts/
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/glyphs/ SVG（重複排除＋エイリアス表）
│   ├── export_png.py           ← SVG → PNG変換（dist/glyphs, svg2png/）
│   ├── generate_decal.py       ← 工業デカール生成（幅可変＋正方形、描画一致統合）
│   ├── build_misskey_zip.py    ← Misskey一括インポートzip生成 → _exported-dist/
│   └── build.py                ← 全ステップ一括ビルド
├── docs/
│   ├── glyph_map.txt           ← inspect_font.py が自動生成
│   ├── glyph_aliases.json      ← 異体字→正規グリフ 対応表（extract_glyphs.py 生成）
│   ├── glyph_render_merges.json ← 描画一致グリフ 統合表（generate_decal.py 生成）
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
  ├─ [グリフ アウトライン抽出＋重複排除] scripts/extract_glyphs.py
  │         ├─ src/glyphs/char_*.svg  （正規148字、fontToolsのSVGPathPenで純粋パス）
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
  └─ [Misskey zip] scripts/build_misskey_zip.py
            └─ _exported-dist/penchant-misskey-{timestamp}.zip（meta.json付き）
```

一括実行は `python scripts/build.py`（全ステップ）。`--step` で個別指定。
ステップ順: inspect → extract → png → svg2png → decal → misskey_zip。

### ビルドコマンド早見表

```bash
pip install -r requirements.txt          # 初回セットアップ（numpy / scipy 含む）
python scripts/inspect_font.py           # フォント検査 → docs/glyph_map.txt
python scripts/extract_glyphs.py --dry-run   # 抽出対象の確認（生成なし）
python scripts/extract_glyphs.py         # グリフSVG抽出（重複排除）→ src/glyphs/, glyph_aliases.json
python scripts/export_png.py             # src/glyphs/*.svg → dist/glyphs/, svg2png/
python scripts/generate_decal.py         # 工業デカール（幅可変＋正方形）＋描画一致統合
python scripts/generate_decal.py -v rust # 単一スキームのみ（統合はスキップ）
python scripts/build_misskey_zip.py      # Misskey一括インポートzip → _exported-dist/
python scripts/build.py                  # 全ステップ一括
python scripts/build.py --dry-run        # 実行確認（ファイル生成なし）
python scripts/build.py --step decal     # 特定ステップのみ
```

### SNS カスタム絵文字 登録の前提

- **Misskey**: `_exported-dist/penchant-misskey-*.zip` を管理画面から一括インポート。
  非正方形の絵文字をそのまま扱えるため **幅可変版**（字面本来の比率）を収録する。
  meta.json のカテゴリは `PenchantManufacture/工業デカール_{和名}/{字種}`、
  各絵文字に基底文字・異体字（アクセント付き／ギリシャ同形）・バリアント名を alias 付与。
- **Discord**: 絵文字は正方形スロットで表示されるため **正方形版**
  （`dist/glyphs_decal_square/{variant}/*_128.png`）を個別アップロードする。
  1 ファイル 256KB 以下（本出力は全て充足）。

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
