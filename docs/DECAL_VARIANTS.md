# 工業デカール バリアント仕様（PenchantManufacture）

`scripts/generate_decal.py` が生成する図柄アセットの仕様書。姉妹プロジェクト
**Secvier**（宝石・陶磁の素材名バリアント）とは **別コンセプト** で、
PenchantManufacture のグリフに工業的・スチームパンク・電脳のクロスオーバー質感を与える。

> 最終更新: 2026-09-08（v3.3 のメトリクス基準クロップへの追随、グリフ数を v4.0-beta へ更新）

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

### トリミング（配置フレームに従った余白除去）— **v3.3 で刷新**

**v3.3-beta 以降、クロップはインク実測ではなく「フォント登録メトリクス」で決まる。**
`extract_glyphs.py` が各 SVG の先頭に `<!-- frame x=X0,X1 y=Y0,Y1 -->` として配置フレームを
埋め込み、`generate_decal.frame_box()` がそれを読んでクロップ矩形を決める
（[AGENTS.md] 「配置の基準」参照）。

- **横幅**：**advance 幅 ∪ インク**。正のサイドベアリングによる字間は絵文字の余白として
  保持され、負のサイドベアリング（`√ ∛ ∜` の笠の右超過、`j` の尾など）のインクも
  切り落とさない。**キャンバス境界へクランプしない**ため、advance が viewBox を超える
  幅広グリフ（`Ⅷ` = 1036 units ≈ 1.04 em）も PIL crop の透明パディングで
  登録メトリクスどおりの余白を保つ。
- **高さ**：**OS/2 win 帯 `[−198, 793]` を全グリフ共通の固定バンド**として使う
  （v3.1–v3.2 のインク実測による動的算出 `compute_vertical_fit` は廃止）。
  全グリフのクロップ高さが揃うので、高さ基準のリサイズ後もベースラインが常に同じ
  出力行に来る（**ベースライン整合**）。帯を逸脱するインクは `extract_glyphs.py` が
  WARN で検出する。
  - 実測（upm=1000, win 帯 991 ≤ 1000 → scale = 512/1000）: クロップ高は全グリフ **533px**、
    512 出力でのベースラインは上端から **402.5px**、win 帯下端は **499.9px**
    （ベースライン下のディセンダ余地 97.4px）。
- **出力形状**：正方形ではなく「**高さ = SIZES（512 / 128 px）／幅 = 可変**」の透過PNG。
  幅は `round(cw × size / ch)` で、**量子化・スナップは行わない**
  （512 出力の実測で 92〜534px の 86 通り）。グリッドへの量子化を行わない判断の経緯は
  [GLYPH_EXTENSION_PLAN.md] §0-2。
- **ハローの逃げ**：作業キャンバスは `WORK = 512 + 2×PAD`（`PAD=18px`）。字面がSVGキャンバス
  上端等に接していても外縁取りが切れないよう、外周に余白を確保してからSDF合成する。
  クロップ側も `CROP_MARGIN = W_HALO + 3 = 13px` を各辺に足してハローを残す。

> **削除済みの旧機構**: v3.2 以前にあった境界キャッシュ `.build_cache/decal_bounds.json`
> （`BOUNDS_VERSION` で無効化）、インク判定しきい値 `INK_THRESH`、高さバンドの基準グリフ
> 判定 `_is_primary()` は **v3.3 で全廃**され、現行 `generate_decal.py` に存在しない。
> 配置がフォントメトリクス由来になりキャッシュする境界が無くなったため。

---

## パイプライン

```
assets/fonts/PenchantManufacture.otf
    │ inspect_font.py     → docs/glyph_map.txt
    │ extract_glyphs.py   → src/glyphs/char_*.svg（重複排除・正規409字）+ docs/glyph_aliases.json
    │                     ← 各SVGに配置フレーム <!-- frame x=..,.. y=..,.. --> を埋め込む
    ▼
src/glyphs/char_*.svg
    │ generate_decal.py   ← cairosvg で白背景マスク化 → SDF＋質感合成
    │                     ← frame_box() が配置フレームを読んでクロップ（advance∪ink / win帯）
    │                     ← 幅可変版（Misskey）＋正方形版（Discord）を出力
    │                     ← dedupe_renders: 描画完全一致グリフを統合 → docs/glyph_render_merges.json
    ▼
dist/glyphs_decal/{variant}/{stem}_{size}.png         （幅可変・Misskey向け）
dist/glyphs_decal_square/{variant}/{stem}_{size}.png  （正方形・Discord向け）
    │ build_misskey_zip.py → _exported-dist/penchant-misskey-{ts}.zip（meta.json付き）
```

## 重複排除（同一画像を二重生成しない）

工業デカールの対象は、`extract_glyphs.py` が cmap 再マップを統合した **正規409字**
（v4.0-beta。アクセント付き56字は v3.2-beta で実アウトラインが与えられ、cmap 統合は 0 件）。
さらに `generate_decal.py` の `dedupe_renders` が、絵文字サイズで描画が **完全一致** する字を
全スキーム×全サイズのバイト一致で検出し、出力PNGを正規側1枚へ統合する
（**13字 → 9グループ、絵文字は正味396字**）。統合表は `docs/glyph_render_merges.json`。
統合された異体字は Misskey の meta.json に検索エイリアスとして付与される。
ソースSVG（`src/glyphs/` 409字）は温存し、各文字セットの独立性を保つ。

> v3.3 のメトリクス基準クロップでは **advance 幅が異なる同形字は統合されない**
> （`C/С` `T/Т` `c/с` `x/х` `о` は幅が僅かに違い独立）。統合の内訳は [AGENTS.md] の表を参照。
>
> 統合先グリフの PNG は `dedupe_renders` が**削除**して重複を消すが、読み取り専用マウント等で
> 削除に失敗すると消し残りが出る。`build_misskey_zip.py` は `glyph_render_merges.json` を見て
> 除外するので zip は正しく作られる（消し残りは次回実行時に削除される）。
> このため `dist/` のファイル数は 409×5×2×2 = 8,180 になることがあり、正味は
> **396×5×2×2 = 7,920**。

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

各バリアントに 396 グリフ × 2 サイズ × 2 形状（幅可変／正方形）。
合計 5 × 396 × 2 × 2 = **7,920 PNG**（v4.0-beta）。サフィックス `_512` / `_128` は**高さ** px
（幅可変版は幅がトリミングで可変、正方形版は幅＝高さ）。

**本仕様書の対象外の出力**（`generate_decal.py` 以外のスクリプトが生成する）:

| ディレクトリ | 内容 | 生成元 |
| --- | --- | --- |
| `dist/glyphs_roman/{variant}/` | 合成ローマ数字 13〜39（大小54点・幅可変・**Misskey 専用**） | `generate_roman.py`（デカール描画は本仕様書の実装を共用） |
| `dist/glyphs_spacer/` | スペーサ `spcp` / `gapp`（完全透過・**バリアント非依存**） | `generate_spacers.py` |

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
- 縁取り幅：`W_HALO`（既定 10px）/ `W_KEY`（既定 6px）、アンチエイリアス `AA`（1.1）。
- トリミング：`CROP_MARGIN`（= `W_HALO + 3` = 13px。外側の保険余白）、`PAD`（18px・ハローの逃げ）。
  **クロップ位置そのものは `frame_box()` が SVG の配置フレームから読むので、
  ここを触ってもグリフの相対位置は動かない**（動かしたい場合は作字側 or `extract_glyphs.py`）。

> **触ってはいけないもの**: `W_HALO` / `W_KEY` / `PAD` / `CROP_MARGIN` の変更は全グリフの
> 出力寸法を変える。Misskey は zip 再インポートで済むが、**Discord は登録済み絵文字の
> 全点手動再アップロード**が必要になる。OS/2 win 帯（793/198）の変更も同様（[AGENTS.md]）。
