# 工業デカール バリアント仕様（PenchantManufacture）

`scripts/generate_decal.py` が生成する図柄アセットの仕様書。姉妹プロジェクト
**Secvier**（宝石・陶磁の素材名バリアント）とは **別コンセプト** で、
PenchantManufacture のグリフに工業的・スチームパンク・電脳のクロスオーバー質感を与える。

- **著作権者**：RadianN_kswg / ラジアン（柏木主税）
- **ライセンス**：CC BY 4.0
- **対象**：フォントグリフのみ（`src/glyphs/char_*.svg`）
- **対象外**：ダイス・トランプ・麻雀牌などの遊戯アイコンは本パイプラインでは扱わない
  （別途、独自図柄として制作する）

---

## コンセプト

- 工業的／スチームパンクなデザイン
- そこはかとなくステンシルな質感（掠れ・ブリッジ痕）
- 機械的なデカールとしての印字を主軸
- 物理的でもあり電脳的でもある、クロスオーバーな色合い

ベクター（SVG アウトライン）を起点に SDF（符号付き距離場）で縁取り・質感を合成するため、
生成ノイズは最小限に抑えられる。

---

## バリアントと配色（既定の墨 ＋ 2バリアント × 各2配色 = 5スキーム）

| キー | バリアント | finish | 位置づけ | ボディ | キーライン | ハロー | アクセント |
| ------ | ------------ | ------- | ------------ | -------- | ---------- | -------- | ---------- |
| `sumi`   | C **既定** 墨 | mono | 二画面・技術テキスト本文 | 近黒 `#16181C→#0B0C0E` | オフホワイト `#E8E4D8` | オフホワイト `#E8E4D8` | （未使用） |
| `rust`   | A-1 酸鉄     | stencil | 物理寄り     | ボーン `#DFD8CA→#C6BEAF` | ガンメタル `#14161A` | 酸化オレンジ `#B5532A` | 暗錆 `#783A1E` |
| `hazard` | A-2 警戒     | stencil | 物理寄り     | 標識イエロー `#E8B430→#CD961C` | 暗鋼 `#16181C` | オフホワイト `#E8E4D8` | 黒斜線 `#121214` |
| `patina` | B-1 緑青真鍮 | circuit | 物理×電脳   | 真鍮 `#C89C4E→#8C6A2E` | 暗銅 `#261C0C` | 淡真鍮 `#D6C496` | 燐光シアン `#33E0D0` |
| `nickel` | B-2 白銅燐光 | circuit | 物理×電脳   | 白銅 `#CACED6→#969CA6` | スレート `#282C32` | 淡白 `#E0E4EA` | 燐光マゼンタ `#FF4D9D` |

### finish 別の質感処理

- **mono**（`sumi`・既定）
  - 近黒ボディをオフホワイトの縁取り（キーライン＋外ハロー）で囲む二画面設計。
    ライト地では黒ボディが、ダーク地では白縁が silhouette を担い、両モードで視認できる。
  - 掠れ（グレイン `0.10`）は **ボディのみ** に控えめに適用する。縁取りは両モード視認の
    要であり、削ると明地・暗地のいずれかで輪郭が沈むため温存する。
  - 技術テキスト（日付・型番・数式・コード）の本文用として最も中立。命名様式では
    最短の後置タグ `p` を占有する（`docs/EMOJI_TECHCODE_SPEC.md` §2.4）。
- **stencil**（`rust` / `hazard`）
  - スプレーの掠れ（グレイン）を SDF ボディ被覆へ乗算。`grain` 係数で強度制御。
    シードはファイル名から決定論的に算出し、リビルド時も同一結果になる。
  - `hazard` はさらにボディ内に斜め縞（ハザードストライプ）を重畳。
- **circuit**（`patina` / `nickel`）
  - ブラシド金属の縦グラデをボディに適用。
  - 全グリフ共通のグリッド状「回路トレース」を **ボディ被覆でマスク** して合成。
    ストロークと交差した箇所だけが「彫刻溝に流れる燐光トレース」として現れる。
  - 芯線（core）＋滲み（glow）の二層で淡い発光感を出す。

### 二重縁取り（両モード視認）

いずれも 外ハロー → キーライン → ボディ の順で SDF 合成し、背景を持たない単体グリフでも
ライト／ダーク両モードで視認できるようにしている（`W_HALO=10px` / `W_KEY=6px`, 512基準）。

### トリミング（文字形状に合わせた余白除去）

フォントメトリクスそのままだと左右・下に大きな余白が出るため、以下方針でトリミングする。

- **横幅**：各グリフ自身のインク幅で個別クロップ（左右余白を除去）。
- **高さ**：**全グリフのインク union から求めた単一の固定縦バンド**を、全グリフに
  **同一の top/bottom で適用**する。全グリフのクロップ高さが揃うので、高さ基準の
  リサイズ後もベースラインが常に同じ出力行に来る（**ベースライン整合**）。union
  バンドは文字セット中で最も背の高い字面（アクセント付き大文字の頭）から最も低い
  字面（小文字 g/j/p/q/y の**ディセンダ**）までを含むため、どのグリフもクリップされない。
  - ※ v2.2 で英小文字が実装され、x-height・アセンダ・ディセンダが混在するようになった。
    旧ロジック（A–Z/0–9 基準バンドをグリフごとに上下拡張）ではディセンダを持つ小文字だけ
    スケールが縮みベースライン行がずれていたため、全グリフ一律の固定バンドへ変更した。
- **出力形状**：正方形ではなく「**高さ = SIZES（512 / 128 px）／幅 = 可変**」の透過PNG。
- **ハローの逃げ**：作業キャンバスは `WORK = 512 + 2×PAD`（`PAD=18px`）。字面がSVGキャンバス
  上端等に接していても外縁取りが切れないよう、外周に余白を確保してからSDF合成する。
- **境界キャッシュ**：全グリフ走査で得た境界を `.build_cache/decal_bounds.json` に保存し、
  5スキーム間で再利用（`BOUNDS_VERSION` 変更で自動無効化）。

---

## パイプライン

```
assets/fonts/PenchantManufacture.otf
    │ inspect_font.py     → docs/glyph_map.txt
    │ extract_glyphs.py   → src/glyphs/char_*.svg（重複排除・正規148字）+ docs/glyph_aliases.json
    ▼
src/glyphs/char_*.svg
    │ generate_decal.py   ← cairosvg で白背景マスク化 → SDF＋質感合成
    │                     ← 幅可変版（Misskey）＋正方形版（Discord）を出力
    │                     ← dedupe_renders: 描画完全一致グリフを統合 → docs/glyph_render_merges.json
    ▼
dist/glyphs_decal/{variant}/{stem}_{size}.png         （幅可変・Misskey向け）
dist/glyphs_decal_square/{variant}/{stem}_{size}.png  （正方形・Discord向け）
    │ build_misskey_zip.py → _exported-dist/penchant-misskey-{ts}.zip（meta.json付き）
```

## 重複排除（同一画像を二重生成しない）

工業デカールの対象は、`extract_glyphs.py` が cmap 再マップ（アクセント付き56字）を統合した
**正規148字**。さらに `generate_decal.py` の `dedupe_renders` が、絵文字サイズで描画が
**完全一致**するギリシャ同形5組（A=Α, B=Β, E=Ε, O=Ο, o=ο）を全スキーム×全サイズの
バイト一致で検出し、出力PNGを正規側1枚へ統合する（**絵文字は正味143字**）。統合された
異体字は Misskey の meta.json に検索エイリアスとして付与される。ソースSVG（`src/glyphs/`
148字、ギリシャ文字セットを含む独立グリフ）は温存する。

## 出力ディレクトリ構成

```
dist/glyphs_decal/          幅可変（高さ基準／Misskey向け・マスター）
├── sumi/    char_A_0041_512.png / char_A_0041_128.png ...  ← 既定（墨・二画面）
├── rust/    ...
├── hazard/  ...
├── patina/  ...
└── nickel/  ...
dist/glyphs_decal_square/   正方形（中央寄せパディング／Discord向け）
├── sumi/ ... └── nickel/ ...
```

各バリアントに 143 グリフ × 2 サイズ × 2 形状（幅可変／正方形）。
合計 5 × 143 × 2 × 2 = 2,860 PNG。サフィックス `_512` / `_128` は**高さ** px
（幅可変版は幅がトリミングで可変、正方形版は幅＝高さ）。

---

## 実行

```bash
pip install -r requirements.txt          # numpy / scipy を含む

python scripts/generate_decal.py                 # 全5スキーム × 全グリフ（幅可変＋正方形＋統合）
python scripts/generate_decal.py --variant sumi  # 単一スキームのみ（描画一致統合はスキップ）
python scripts/generate_decal.py --no-square     # 正方形版を生成しない（幅可変のみ）
python scripts/generate_decal.py --limit 5       # 先頭5グリフで試写

python scripts/build_misskey_zip.py              # Misskey一括インポートzip → _exported-dist/

# 一括ビルド（inspect→extract→png→svg2png→decal→misskey_zip）
python scripts/build.py --dry-run
python scripts/build.py
```

> **注**: 描画一致統合（`dedupe_renders`）は全5スキームが揃った全量ビルド時のみ実施する。
> `--variant` や `--limit` を付けた部分ビルドではスキップされる（統合判定に全スキームの
> 出力が必要なため）。単一スキームで試した後は、最終的に全量ビルドで統合を確定させること。

## パラメータ調整の勘所（`scripts/generate_decal.py`）

- 配色：`SCHEMES` の各 `Scheme`（body_top/bottom・keyline・halo・accent）。
- 掠れ：`Scheme.grain`（0=無し .. 1=激しい）。
- ハザード斜線：`stripe_field(period=…)` の周期。
- 回路トレース：`_trace_fields()` の線位置・太さ・パッド位置。
- 縁取り幅：`W_HALO` / `W_KEY`、アンチエイリアス `AA`。
- トリミング：`CROP_MARGIN`（外側の保険余白）、`PAD`（ハローの逃げ）、
  `INK_THRESH`（インク判定しきい値）、`_is_primary()`（高さバンドの基準グリフ）。
