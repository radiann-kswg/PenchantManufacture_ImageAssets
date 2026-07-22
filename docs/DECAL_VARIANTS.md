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

## バリアントと配色（2バリアント × 各2配色 = 4スキーム）

| キー | バリアント | finish | 位置づけ | ボディ | キーライン | ハロー | アクセント |
| ------ | ------------ | ------- | ------------ | -------- | ---------- | -------- | ---------- |
| `rust`   | A-1 酸鉄     | stencil | 物理寄り     | ボーン `#DFD8CA→#C6BEAF` | ガンメタル `#14161A` | 酸化オレンジ `#B5532A` | 暗錆 `#783A1E` |
| `hazard` | A-2 警戒     | stencil | 物理寄り     | 標識イエロー `#E8B430→#CD961C` | 暗鋼 `#16181C` | オフホワイト `#E8E4D8` | 黒斜線 `#121214` |
| `patina` | B-1 緑青真鍮 | circuit | 物理×電脳   | 真鍮 `#C89C4E→#8C6A2E` | 暗銅 `#261C0C` | 淡真鍮 `#D6C496` | 燐光シアン `#33E0D0` |
| `nickel` | B-2 白銅燐光 | circuit | 物理×電脳   | 白銅 `#CACED6→#969CA6` | スレート `#282C32` | 淡白 `#E0E4EA` | 燐光マゼンタ `#FF4D9D` |

### finish 別の質感処理

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
- **高さ**：主要グリフ（A–Z / 0–9）のインク union を共通バンドとして採用し、
  文字セットとしての高さ・ベースライン整合を維持。バンドより背高（例: `!`・アクセント）／
  背低（例: `,`）なグリフは、その分だけバンドを拡張して**クリップしない**。
- **出力形状**：正方形ではなく「**高さ = SIZES（512 / 128 px）／幅 = 可変**」の透過PNG。
- **ハローの逃げ**：作業キャンバスは `WORK = 512 + 2×PAD`（`PAD=18px`）。字面がSVGキャンバス
  上端等に接していても外縁取りが切れないよう、外周に余白を確保してからSDF合成する。
- **境界キャッシュ**：全グリフ走査で得た境界を `.build_cache/decal_bounds.json` に保存し、
  4スキーム間で再利用（`BOUNDS_VERSION` 変更で自動無効化）。

---

## パイプライン

```
assets/fonts/PenchantManufacture.otf
    │ inspect_font.py     → docs/glyph_map.txt
    │ extract_glyphs.py   → src/glyphs/char_*.svg（アウトライン化・XMLエスケープ済み）
    ▼
src/glyphs/char_*.svg
    │ generate_decal.py   ← cairosvg で白背景マスク化 → SDF＋質感合成
    ▼
dist/glyphs_decal/{variant}/{stem}_{size}.png   （512 / 128 の透過PNG）
```

## 出力ディレクトリ構成

```
dist/glyphs_decal/
├── rust/    char_A_0041_512.png / char_A_0041_128.png ...
├── hazard/  ...
├── patina/  ...
└── nickel/  ...
```

各バリアントに 202 グリフ × 2 サイズ。合計 4 × 202 × 2 = 1,616 PNG。
サフィックス `_512` / `_128` は**高さ** px（幅はトリミングで可変）。

---

## 実行

```bash
pip install -r requirements.txt          # numpy / scipy を含む

python scripts/generate_decal.py                 # 全4スキーム × 全グリフ
python scripts/generate_decal.py --variant rust  # 単一スキームのみ
python scripts/generate_decal.py --limit 5       # 先頭5グリフで試写

# 一括ビルド（inspect→extract→png→svg2png→decal）
python scripts/build.py --dry-run
python scripts/build.py
```

## パラメータ調整の勘所（`scripts/generate_decal.py`）

- 配色：`SCHEMES` の各 `Scheme`（body_top/bottom・keyline・halo・accent）。
- 掠れ：`Scheme.grain`（0=無し .. 1=激しい）。
- ハザード斜線：`stripe_field(period=…)` の周期。
- 回路トレース：`_trace_fields()` の線位置・太さ・パッド位置。
- 縁取り幅：`W_HALO` / `W_KEY`、アンチエイリアス `AA`。
- トリミング：`CROP_MARGIN`（外側の保険余白）、`PAD`（ハローの逃げ）、
  `INK_THRESH`（インク判定しきい値）、`_is_primary()`（高さバンドの基準グリフ）。
