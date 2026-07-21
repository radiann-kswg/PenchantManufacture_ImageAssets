@AGENTS.md

---

## Claude Code 固有の作業指針

### 優先確認事項

1. 作業開始前に `docs/glyph_map.txt` を確認し、利用可能グリフを把握すること。
   未生成の場合は `python scripts/inspect_font.py` を実行して生成する。
2. グリフSVGを起点にする場合は `scripts/extract_glyphs.py` で生成された
   アウトライン済みSVG（`src/glyphs/char_*.svg`）を利用すること。
3. フォント本体は `assets/fonts/PenchantManufacture.otf` を参照する
   （`_original-fonts/` は読み取り専用・.gitignore対象）。

### 現行スクリプト

| スクリプト                     | 対象                                        | 出力先                                   |
| ------------------------------ | ------------------------------------------- | ---------------------------------------- |
| `scripts/inspect_font.py`      | フォントグリフ検査                          | `docs/glyph_map.txt`                     |
| `scripts/extract_glyphs.py`    | cmap全グリフのアウトライン化SVG抽出         | `src/glyphs/char_*.svg`                  |
| `scripts/export_png.py`        | SVG → PNG変換（2サイズ + 単純変換）         | `dist/glyphs/`, `svg2png/glyphs/`        |
| `scripts/build.py`             | 検査→抽出→PNGの全ステップ一括ビルド         | 上記すべて                               |

### スクリプト実行順序

```bash
# 初回セットアップ
pip install -r requirements.txt

# フォント検査（グリフ確認）→ docs/glyph_map.txt
python scripts/inspect_font.py

# グリフSVG抽出 → src/glyphs/
python scripts/extract_glyphs.py --dry-run   # まず対象確認
python scripts/extract_glyphs.py             # 書き出し

# PNG変換 → dist/glyphs/, svg2png/glyphs/
python scripts/export_png.py

# 全ステップ一括（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py
```

### ディレクトリ補足

- `src/glyphs/` — `extract_glyphs.py` が生成するアウトライン化済みグリフSVG。
  ファイル名は `char_{AGL名}_{コードポイント}.svg`（case-safe 命名）。
- `dist/glyphs/` — 絵文字出力用の透過PNG（72px / 512px）。直接配置禁止。
- `svg2png/glyphs/` — 装飾なしの単純PNG変換。スタイル付き出力（`dist/`）とは別管理。
- `docs/glyph_map.txt` — `inspect_font.py` の自動生成物。手動編集しないこと。

### メモリ・コンテキスト管理

- Python依存を追加した場合は `requirements.txt` を必ず更新すること
- 新カテゴリや新仕様を追加する場合は `docs/` に仕様書を作成すること
- コミットは `feat` / `fix` / `build` / `docs` / `chore` / `style` プレフィックスで行うこと
