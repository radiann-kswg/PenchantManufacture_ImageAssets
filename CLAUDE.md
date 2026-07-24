@AGENTS.md

---

## Claude Code 固有の作業指針

### 優先確認事項

1. 作業開始前に `docs/glyph_map.txt` を確認し、利用可能グリフを把握すること。
   未生成の場合は `python scripts/inspect_font.py` を実行して生成する。
2. グリフSVGを起点にする場合は `scripts/extract_glyphs.py` で生成された
   アウトライン済みSVG（`src/glyphs/char_*.svg`、重複排除後 148字）を利用すること。
3. フォント本体は `assets/fonts/PenchantManufacture.otf` を参照する
   （`_original-fonts/` は読み取り専用・.gitignore対象）。
4. **同一画像を二重生成しないこと。** cmap 再マップ（アクセント付き）とギリシャ同形は
   重複排除され、異体字は `glyph_aliases.json` / `glyph_render_merges.json` に
   エイリアスとして記録される。詳細は AGENTS.md「重複排除の方針」を参照。

### 現行スクリプト

| スクリプト                     | 対象                                                    | 出力先                                            |
| ------------------------------ | ------------------------------------------------------- | ------------------------------------------------- |
| `scripts/inspect_font.py`      | フォントグリフ検査                                      | `docs/glyph_map.txt`                              |
| `scripts/extract_glyphs.py`    | cmap走査＋グリフ単位の重複排除 → アウトライン化SVG抽出   | `src/glyphs/char_*.svg`（148）, `docs/glyph_aliases.json` |
| `scripts/export_png.py`        | SVG → PNG変換（2サイズ + 単純変換）                     | `dist/glyphs/`, `svg2png/glyphs/`                 |
| `scripts/generate_decal.py`    | 工業デカール生成（幅可変＋正方形）＋描画一致統合         | `dist/glyphs_decal/{v}/`, `dist/glyphs_decal_square/{v}/`, `docs/glyph_render_merges.json` |
| `scripts/build_misskey_zip.py` | Misskey一括インポートzip生成（幅可変版・エイリアス付与） | `_exported-dist/penchant-misskey-{ts}.zip`        |
| `scripts/build.py`             | inspect→extract→png→svg2png→decal→misskey_zip 一括      | 上記すべて                                        |

### スクリプト実行順序

```bash
# 初回セットアップ（numpy / scipy / cairosvg 含む）
pip install -r requirements.txt

# フォント検査（グリフ確認）→ docs/glyph_map.txt
python scripts/inspect_font.py

# グリフSVG抽出（重複排除）→ src/glyphs/, docs/glyph_aliases.json
python scripts/extract_glyphs.py --dry-run   # まず対象確認
python scripts/extract_glyphs.py             # 書き出し（旧・重複SVGは prune される）

# 単純PNG変換 → dist/glyphs/, svg2png/glyphs/
python scripts/export_png.py

# 工業デカール生成（幅可変＋正方形）＋描画一致統合 → dist/glyphs_decal[_square]/
python scripts/generate_decal.py

# Misskey一括インポートzip → _exported-dist/
python scripts/build_misskey_zip.py

# 全ステップ一括（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py
```

### ディレクトリ補足

- `src/glyphs/` — `extract_glyphs.py` が生成するアウトライン化済みグリフSVG（正規148字）。
  ファイル名は `char_{AGL名}_{コードポイント}.svg`（case-safe 命名）。ギリシャ文字を含む
  独立グリフを温存し、絵文字向けの描画一致統合はここでは行わない。
- `dist/glyphs/` — 装飾なしの絵文字用透過PNG（72px / 512px）。直接配置禁止。
- `dist/glyphs_decal/{variant}/` — 工業デカール **幅可変**PNG（512/128、Misskey向け・マスター）。
- `dist/glyphs_decal_square/{variant}/` — 工業デカール **正方形**PNG（512/128、Discord向け）。
  variant は rust / hazard / patina / nickel。直接配置禁止（`generate_decal.py` 経由）。
- `svg2png/glyphs/` — 装飾なしの単純PNG変換。スタイル付き出力（`dist/`）とは別管理。
- `docs/glyph_map.txt` / `glyph_aliases.json` / `glyph_render_merges.json`
  — いずれもスクリプトの自動生成物。**手動編集しないこと**。
- `_exported-dist/` — `build_misskey_zip.py` の出力先（`.gitignore` 対象）。

### メモリ・コンテキスト管理

- Python依存を追加した場合は `requirements.txt` を必ず更新すること
- 新カテゴリや新仕様を追加する場合は `docs/` に仕様書を作成すること
- コミットは `feat` / `fix` / `build` / `docs` / `chore` / `style` プレフィックスで行うこと
