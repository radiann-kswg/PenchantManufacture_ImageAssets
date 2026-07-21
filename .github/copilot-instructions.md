# GitHub Copilot ワークスペース指示書 — PenchantManufacture ImageAssets

> 共通仕様の詳細は **[AGENTS.md](../AGENTS.md)** を参照してください。
> このファイルはCopilot固有の補足事項のみを記載します。

---

## プロジェクト概要

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、
**RadianN_kswg / ラジアン（柏木主税）による独自フォント PenchantManufacture** と
**Claude による Agent 機能** によって制作するカスタム画像アセット／グリフ素材リポジトリ。

**著作権者**: RadianN_kswg / ラジアン（柏木主税） / **ライセンス**: CC BY 4.0

---

## 補完規則

### Python補完

- `from __future__ import annotations` を全スクリプトの先頭に記述
- 型ヒントは全引数・戻り値に付与（`Path`, `str`, `int`, `list[Path]` 等）
- docstringはGoogle スタイル（日本語記述可）
- フォントパスは常に
  `FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "PenchantManufacture.otf"`
  パターンを踏襲

### SVG補完

- `viewBox="0 0 512 512"` 固定
- `width` / `height` も `512` に統一
- フォント参照はアウトライン化（パス埋め込み）を基本とする
- `fill` のデフォルト色: `#000000`（透過背景）

### ファイル配置

```
src/glyphs/char_{AGL名}_{CP}.svg    ← extract_glyphs.py 出力（case-safe 命名）
dist/glyphs/char_*_72.png           ← export_png.py 出力（72px）
dist/glyphs/char_*_512.png          ← export_png.py 出力（512px）
svg2png/glyphs/char_*.png           ← SVG の単純PNG変換（装飾なし）
docs/glyph_map.txt                  ← inspect_font.py 自動生成
_exported-dist/*.zip                ← エクスポートzip（.gitignore対象）
```

`dist/` `svg2png/` への直接配置は禁止（スクリプト経由のみ）。
`_exported-dist/` は `.gitignore` 対象のため git 管理外。

---

## 禁止事項

- `_original-fonts/` 内ファイルの変更・削除
- 第三者フォントのグリフパス使用
- `dist/` `svg2png/` への直接ファイル配置
- ライセンス表記の削除・改ざん

---

## コミットメッセージ

```
<type>(<scope>): <subject>
```

| type    | 用途                         |
| ------- | ---------------------------- |
| `feat`  | 新機能・新アセット追加       |
| `fix`   | バグ修正                     |
| `build` | ビルドスクリプト変更         |
| `docs`  | ドキュメント更新             |
| `chore` | 設定ファイル・メタデータ変更 |
| `style` | SVGスタイル・見た目の調整    |

例: `feat(glyphs): add outlined SVGs for full cmap`
