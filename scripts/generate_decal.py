"""工業／スチームパンク「機械デカール」バリアント生成スクリプト.

姉妹プロジェクト Secvier の宝石・陶磁バリアント（generate_dualmode.py）とは
別コンセプトで、PenchantManufacture のグリフに **工業的・スチームパンク・電脳**
のクロスオーバー質感を与える。ステンシルのブリッジ痕（掠れ）・機械デカール印字・
彫刻溝に流し込んだ燐光トレースをベクター起点のSDFで合成する。

対象は **フォントグリフのみ**。ダイス・トランプ・麻雀牌などの遊戯アイコンは
本スクリプトの対象外（別途、独自図柄として制作する）。

パイプライン:
    src/glyphs/char_*.svg （extract_glyphs.py 出力・アウトライン化済み）
        │  cairosvg で白背景マスク化（黒字被覆率を抽出）
        ▼
    SDF（符号付き距離場）で 外ハロー＋キーライン＋ボディ を二重縁取り
        │  finish 別の質感処理:
        │    stencil … スプレーの掠れ（グレイン）＋ハザード斜線
        │    circuit … ブラシド金属ボディ＋燐光回路トレース（彫刻溝の発光）
        ▼
    dist/glyphs_decal/{variant}/{stem}_{size}.png         幅可変（Misskey 向け・マスター）
    dist/glyphs_decal_square/{variant}/{stem}_{size}.png  正方形パディング（Discord 向け）
        （いずれも 512 / 128 の透過PNG）

5スキーム（既定の墨 ＋ 2バリアント × 各2配色）:
    C 二画面モノクロ（既定）
        sumi   … 墨       近黒ボディ＋オフホワイト縁取り（ダーク/ライト両対応）
    A 酸化ステンシル（物理寄り）
        rust   … A-1 酸鉄   ガンメタル地＋酸化オレンジの縁＋ボーン文字
        hazard … A-2 警戒   暗鋼地＋安全標識イエロー＋黒斜線ハザード
    B 真鍮回路（物理×電脳・蝕刻＋燐光の折衷）
        patina … B-1 緑青真鍮 真鍮ボディ＋燐光シアンの回路トレース
        nickel … B-2 白銅燐光 白銅ボディ＋燐光マゼンタの回路トレース

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0

使い方:
    python scripts/generate_decal.py                      # 全4スキーム × 全グリフ
    python scripts/generate_decal.py --variant rust       # 1スキームのみ
    python scripts/generate_decal.py --limit 5            # 先頭5グリフで試写
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import NamedTuple

import cairosvg
import click
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, uniform_filter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "glyphs"
# 幅可変版（高さ基準・幅はインク幅に応じて可変）。Misskey 向け＆マスター。
DIST = ROOT / "dist" / "glyphs_decal"
# 正方形パディング版（中央寄せ・余白透過）。Discord のスクエア絵文字枠向け。
DIST_SQUARE = ROOT / "dist" / "glyphs_decal_square"
# 描画結果が完全一致するグリフの統合表（絵文字ビルダーがエイリアス化に使用）。
MERGES_PATH = ROOT / "docs" / "glyph_render_merges.json"
ALIASES_PATH = ROOT / "docs" / "glyph_aliases.json"

RES = 512                 # SVGラスタライズ解像度（グリフ本体のマスク基準）
PAD = 18                  # 作業キャンバスの外周余白（ハローの逃げ, px）
WORK = RES + 2 * PAD      # 実際の作業解像度（縁取りがキャンバス外で切れないように）
SIZES = (512, 128)        # 出力サイズ（＝高さ基準の px。幅はトリミングで可変）
W_HALO = 10               # 外ハロー幅（px, 512基準）
W_KEY = 6                 # 内キーライン幅（px, 512基準）
AA = 1.1                  # 境界アンチエイリアス幅

# ── トリミング（文字形状に合わせた余白除去） ──
# 横幅はグリフごとにタイト、高さは全グリフ共通の固定バンドで揃える。
#   - 縦: 全グリフのインク union から算出した「単一の固定バンド」を、全グリフに
#         同一の top/bottom で適用する。全グリフのクロップ高さが揃うため、高さ基準の
#         リサイズ後もベースラインが常に同じ出力行に来る（＝ベースライン整合）。
#         小文字の下ぶくれ（g/j/p/q/y のディセンダ）やアクセント付き文字の頭も、
#         union バンドが端から端まで含むためクリップされない。
#   - 横: 各グリフ自身のインク幅で個別クロップ（左右の余白を除去）
# 出力は正方形ではなく「高さ=SIZES / 幅=可変」の透過PNGになる。
# NOTE: 以前は主要グリフ(A–Z/0–9)基準のバンドをグリフごとに上下拡張していたため、
#       ディセンダを持つ小文字だけスケールが縮みベースライン行がずれていた。v2.2 で
#       小文字が実装されたのに合わせ、全グリフ一律の固定バンドへ変更した。
INK_THRESH = 0.05         # インクとみなす被覆率しきい値
CROP_MARGIN = W_HALO + 3  # クロップ余白（ハロー＋αを切り落とさないための保険, px）
BOUNDS_CACHE = ROOT / ".build_cache" / "decal_bounds.json"
BOUNDS_VERSION = "4"      # 境界算出ロジックのバージョン（変更でキャッシュ無効化）


class Scheme(NamedTuple):
    """工業デカールの仕上げ定義（RGBは全て 0-255）。"""

    label: str                      # 和名ラベル
    finish: str                     # "stencil" | "circuit"
    body_top: tuple[int, int, int]  # ボディ上端色（縦グラデ）
    body_bottom: tuple[int, int, int]
    keyline: tuple[int, int, int]   # 内キーライン（彫り込み陰）
    halo: tuple[int, int, int]      # 外ハロー（両モード視認用リング）
    accent: tuple[int, int, int]    # ハザード斜線 / 燐光トレース色
    grain: float                    # スプレー掠れの強さ（0=無し .. 1=激しい）
    stripes: bool = False           # True でハザード斜線を重畳


# ── 5スキーム（既定の墨 ＋ 2バリアント × 各2配色） ──
SCHEMES: dict[str, Scheme] = {
    # C 二画面モノクロ（既定・技術テキスト本文向け）
    #    近黒ボディをオフホワイトの縁取り（キーライン＋外ハロー）で囲む。
    #    ライト地では黒ボディが、ダーク地では白縁が効き、両モードで視認できる。
    "sumi":   Scheme("墨",     "mono",
                     (22, 24, 28),   (11, 12, 14),
                     (232, 228, 216), (232, 228, 216), (232, 228, 216), grain=0.10),
    # A 酸化ステンシル（物理寄り）
    "rust":   Scheme("酸鉄",   "stencil",
                     (223, 216, 202), (198, 190, 175),
                     (20, 22, 26),   (181, 83, 42),  (120, 58, 30), grain=0.55),
    "hazard": Scheme("警戒",   "stencil",
                     (232, 180, 48), (205, 150, 28),
                     (22, 24, 28),   (232, 228, 216), (18, 18, 20), grain=0.42,
                     stripes=True),
    # B 真鍮回路（物理×電脳）
    "patina": Scheme("緑青真鍮", "circuit",
                     (200, 156, 78), (140, 106, 46),
                     (38, 28, 12),   (214, 196, 150), (51, 224, 208), grain=0.12),
    "nickel": Scheme("白銅燐光", "circuit",
                     (202, 206, 214), (150, 156, 166),
                     (40, 44, 50),   (224, 228, 234), (255, 77, 157), grain=0.12),
}

# ── バリアント → スキームキー（ドキュメント／CLI補助用） ──
VARIANT_GROUPS: dict[str, list[str]] = {
    "C_mono": ["sumi"],
    "A_stencil": ["rust", "hazard"],
    "B_circuit": ["patina", "nickel"],
}


# ────────────────────────────────────────────────────────────────
# マスク・SDF ユーティリティ
# ────────────────────────────────────────────────────────────────
def load_mask(svg_path: Path) -> np.ndarray:
    """アウトラインSVG → グリフ被覆率 [0,1]（WORK×WORK, 外周にPAD余白）。

    白背景に合成して黒字被覆を抽出し、外周に PAD の空き（被覆0）を確保した
    WORK×WORK 配列で返す。これによりキャンバス上端等に接する字面でも、
    ハロー（外縁取り）がキャンバス外で切れない。
    """
    png = cairosvg.svg2png(
        bytestring=svg_path.read_bytes(),
        output_width=RES,
        output_height=RES,
        background_color="white",
    )
    im = Image.open(BytesIO(png)).convert("L")
    core = 1.0 - np.asarray(im, dtype=np.float32) / 255.0
    mask = np.zeros((WORK, WORK), dtype=np.float32)
    mask[PAD:PAD + RES, PAD:PAD + RES] = core
    return mask


def signed_distance(mask: np.ndarray) -> np.ndarray:
    """符号付き距離場：グリフ外で正、内で負（px）。"""
    solid = mask >= 0.5
    return distance_transform_edt(~solid) - distance_transform_edt(solid)


def region_alpha(sdf: np.ndarray, t: float) -> np.ndarray:
    """{sdf <= t} 領域のアンチエイリアス被覆率 [0,1]。"""
    return np.clip((t - sdf) / AA + 0.5, 0.0, 1.0)


def vertical_gradient(top: tuple, bottom: tuple, mask: np.ndarray) -> np.ndarray:
    """グリフbbox範囲で上→下の縦グラデRGB（H,W,3）。金属の面陰影に使う。"""
    ys = np.where(mask.max(axis=1) > 0.05)[0]
    y0, y1 = (int(ys.min()), int(ys.max())) if len(ys) else (0, WORK - 1)
    t = np.clip((np.arange(WORK) - y0) / max(1, (y1 - y0)), 0.0, 1.0)
    rgb = np.array(top)[None, :] * (1 - t)[:, None] + np.array(bottom)[None, :] * t[:, None]
    return np.repeat(rgb[:, None, :], WORK, axis=1)


def _over(dst: np.ndarray, color: np.ndarray, alpha: np.ndarray) -> None:
    """dst(RGBA float, RGB 0-255 / A 0-1) に color を alpha 合成（in-place）。"""
    a = alpha[..., None]
    dst[..., :3] = color * a + dst[..., :3] * (1 - a)
    dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)


# ────────────────────────────────────────────────────────────────
# 質感フィールド（ステンシル掠れ・ハザード斜線・回路トレース）
# ────────────────────────────────────────────────────────────────
def grain_field(seed: int, strength: float) -> np.ndarray:
    """スプレー掠れの被覆率倍率 [1-strength, 1]（ブロッチ状のノイズ）。

    seed 固定でリビルド時も同一結果になる（決定論的）。
    """
    if strength <= 0:
        return np.ones((WORK, WORK), dtype=np.float32)
    rng = np.random.default_rng(seed)
    n = rng.random((WORK, WORK)).astype(np.float32)
    n = uniform_filter(n, size=11, mode="reflect")     # 塗りムラ状に均す
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    mult = 1.0 - strength * (1.0 - n)                  # 高ノイズ域を残し、低域を痩せさせる
    mult = np.where(n < 0.10 * strength, mult * 0.25, mult)  # まれにピンホール
    return mult.astype(np.float32)


def stripe_field(period: int = 58) -> np.ndarray:
    """左上→右下の斜めハザード縞（0/1）。"""
    xx, yy = np.meshgrid(np.arange(WORK), np.arange(WORK))
    return ((xx + yy) % period < period * 0.5).astype(np.float32)


def _trace_fields() -> tuple[np.ndarray, np.ndarray]:
    """機械デカール共通の回路トレース（core=芯線, glow=滲み）を返す。

    全グリフ共通のグリッド状トレース。ボディ被覆でマスクするため、
    実際にはストロークと交差した箇所だけが「彫刻溝の発光」として現れる。
    """
    xx, yy = np.meshgrid(np.arange(WORK), np.arange(WORK))
    core = np.zeros((WORK, WORK), dtype=np.float32)
    glow = np.zeros((WORK, WORK), dtype=np.float32)

    lines = [
        (("h", 0.44), 2, 6),
        (("h", 0.68), 2, 6),
        (("v", 0.30), 2, 6),
        (("v", 0.72), 2, 6),
    ]
    for (axis, frac), tc, tg in lines:
        pos = frac * WORK
        d = np.abs((yy if axis == "h" else xx) - pos)
        core = np.maximum(core, (d <= tc).astype(np.float32))
        glow = np.maximum(glow, (d <= tg).astype(np.float32))

    for px, py in [(0.30, 0.44), (0.72, 0.68), (0.30, 0.68), (0.72, 0.44)]:
        r2 = (xx - px * WORK) ** 2 + (yy - py * WORK) ** 2
        core = np.maximum(core, (r2 <= 9 ** 2).astype(np.float32))
        glow = np.maximum(glow, (r2 <= 15 ** 2).astype(np.float32))

    return core, glow


_TRACE_CORE, _TRACE_GLOW = _trace_fields()
_STRIPE = stripe_field()


# ────────────────────────────────────────────────────────────────
# トリミング境界（横=グリフ個別 / 縦=全グリフ一律の固定バンド）
# ────────────────────────────────────────────────────────────────
def ink_bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    """マスクのインク境界 (x0, y0, x1, y1) を返す。空なら None。"""
    cols = np.where(mask.max(axis=0) > INK_THRESH)[0]
    rows = np.where(mask.max(axis=1) > INK_THRESH)[0]
    if len(cols) == 0 or len(rows) == 0:
        return None
    return int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1


def compute_bounds(sources: list[Path]) -> tuple[dict[str, list[int]], tuple[int, int]]:
    """全ソースのインク境界と、全グリフ共通の縦バンド (top, bottom) を算出する。

    縦バンドは全グリフのインク union（最上端〜最下端）とする。文字セット中で
    最も背の高い字面（アクセント付き大文字の頭）から最も低い字面（小文字の
    ディセンダ）までを 1 本の帯に含めるため、全グリフをこの同一 top/bottom で
    クロップしてもインクがクリップされない。かつ全グリフのクロップ高さが揃うので、
    高さ基準リサイズ後のベースライン行が全グリフで一致する（ベースライン整合）。
    """
    bounds: dict[str, list[int]] = {}
    tops: list[int] = []
    bottoms: list[int] = []
    for svg in sources:
        bb = ink_bbox(load_mask(svg))
        if bb is None:
            continue
        bounds[svg.stem] = list(bb)
        tops.append(bb[1])
        bottoms.append(bb[3])
    vband = (min(tops), max(bottoms)) if tops else (0, RES)
    return bounds, vband


def _sig(sources: list[Path]) -> str:
    """ソース集合の署名（ファイル名＋サイズ）。変化時にキャッシュを無効化する。"""
    h = hashlib.md5()
    h.update(BOUNDS_VERSION.encode("utf-8"))
    for svg in sources:
        h.update(svg.name.encode("utf-8"))
        h.update(str(svg.stat().st_size).encode("utf-8"))
    return h.hexdigest()


def ensure_bounds(sources: list[Path]) -> tuple[dict[str, list[int]], tuple[int, int]]:
    """トリミング境界をキャッシュ経由で取得（無ければ算出して保存）。"""
    sig = _sig(sources)
    if BOUNDS_CACHE.exists():
        try:
            data = json.loads(BOUNDS_CACHE.read_text(encoding="utf-8"))
            if data.get("sig") == sig:
                return data["bounds"], tuple(data["vband"])
        except (json.JSONDecodeError, KeyError):
            pass
    print("  トリミング境界を算出中（全グリフをスキャン）...")
    bounds, vband = compute_bounds(sources)
    BOUNDS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    BOUNDS_CACHE.write_text(
        json.dumps({"sig": sig, "vband": list(vband), "bounds": bounds}),
        encoding="utf-8",
    )
    return bounds, vband


def crop_box_for(stem: str, bounds: dict[str, list[int]], vband: tuple[int, int]) -> tuple[int, int, int, int]:
    """グリフのクロップ矩形 (left, top, right, bottom) を返す。

    横 = 当該グリフのインク幅（左右余白を除去）。
    縦 = 全グリフ共通の固定バンド（vband）。当該グリフの背丈に依らず top/bottom は
    常に同じなので、全グリフのクロップ高さが一致し、高さ基準リサイズ後もベースライン
    行が全グリフで揃う。union バンドなのでディセンダ・アクセントもクリップされない。
    いずれも CROP_MARGIN 分を外側に確保し、ハローや燐光の滲みを切り落とさない。
    """
    x0, _y0, x1, _y1 = bounds[stem]
    left = max(0, x0 - CROP_MARGIN)
    right = min(WORK, x1 + CROP_MARGIN)
    t = max(0, vband[0] - CROP_MARGIN)
    b = min(WORK, vband[1] + CROP_MARGIN)
    return left, t, right, b


# ────────────────────────────────────────────────────────────────
# レンダリング
# ────────────────────────────────────────────────────────────────
def render(mask: np.ndarray, s: Scheme, seed: int) -> Image.Image:
    """1グリフを指定スキームの工業デカールとして透過RGBAで描画する。"""
    sdf = signed_distance(mask)
    canvas = np.zeros((WORK, WORK, 4), dtype=np.float32)

    a_halo = region_alpha(sdf, float(W_HALO))
    a_key = region_alpha(sdf, 0.0)
    a_body = region_alpha(sdf, float(-W_KEY))

    if s.finish == "stencil":
        g = grain_field(seed, s.grain)
        a_body = a_body * g
        a_key = a_key * (0.4 + 0.6 * g)   # 縁も worn に
    elif s.finish == "mono":
        # 掠れはボディのみへ控えめに適用する。縁取り（キーライン／外ハロー）は
        # 二画面視認の要であり、削ると明地・暗地どちらかで輪郭が沈むため温存する。
        a_body = a_body * grain_field(seed, s.grain)

    # 二重縁取り（外ハロー → キーライン → ボディ）
    _over(canvas, np.array(s.halo, dtype=np.float32), a_halo)
    _over(canvas, np.array(s.keyline, dtype=np.float32), a_key)
    body = vertical_gradient(s.body_top, s.body_bottom, mask)
    _over(canvas, body, a_body)

    if s.finish == "stencil" and s.stripes:
        # ボディ上に黒斜線を重ねてハザード表現（ボディ被覆内のみ）
        _over(canvas, np.array(s.accent, dtype=np.float32), a_body * _STRIPE * 0.85)

    if s.finish == "circuit":
        accent = np.array(s.accent, dtype=np.float32)
        _over(canvas, accent, a_body * _TRACE_GLOW * 0.30)   # 滲み（発光の裾）
        _over(canvas, accent, a_body * _TRACE_CORE * 0.95)   # 芯線

    out = np.empty_like(canvas)
    out[..., :3] = canvas[..., :3]
    out[..., 3] = canvas[..., 3] * 255.0
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def _save_all_sizes(
    img: Image.Image,
    out_dir: Path,
    stem: str,
    box: tuple[int, int, int, int],
    square_dir: Path | None = None,
) -> None:
    """クロップ後、2形状で各サイズに保存する。

    - **幅可変版**（``out_dir``）: 高さを SIZES に固定し、幅はアスペクト維持で可変。
      Misskey は非正方形の絵文字をそのまま表示できるため、字面本来の比率を保つ。
    - **正方形版**（``square_dir``、指定時のみ）: 幅可変クロップを一辺 ``max(幅,高さ)`` の
      透過キャンバスへ中央寄せでパディングしてから SIZES 正方形へ縮小。Discord は
      絵文字を正方形スロットで表示するため、字面が歪まないようパディングで正方形化する。
      いずれも同一クロップ（＝同一ベースライン整合）から生成する。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cropped = img.crop(box)
    cw, ch = cropped.size

    # 幅可変版（高さ基準）
    for sz in SIZES:
        w = max(1, round(cw * sz / ch))
        cropped.resize((w, sz), Image.LANCZOS).save(out_dir / f"{stem}_{sz}.png")

    # 正方形版（中央寄せパディング）
    if square_dir is not None:
        square_dir.mkdir(parents=True, exist_ok=True)
        side = max(cw, ch)
        square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        square.paste(cropped, ((side - cw) // 2, (side - ch) // 2), cropped)
        for sz in SIZES:
            square.resize((sz, sz), Image.LANCZOS).save(square_dir / f"{stem}_{sz}.png")


def _seed_for(key: str) -> int:
    """文字列から決定論的な乱数シードを作る（掠れの再現性確保）。

    Python の hash() は実行ごとに変わる（PYTHONHASHSEED）ため使わず、
    バイト列から安定なシードを算出してリビルド時の同一性を保証する。
    """
    return int.from_bytes(key.encode("utf-8"), "little") % (2 ** 31)


def dedupe_renders(square: bool = True) -> dict[str, list[str]]:
    """描画結果が**完全一致**するグリフを統合し、非正規側のPNGを削除する。

    フォント上は別グリフ（別パス）でも、絵文字サイズでは同形になる字がある
    （例: ラテン A と ギリシャ Α（Alpha）、B と Β、E と Ε、O と Ο、o と ο）。
    これらは「同一画像が別名で登録される」状態になるため、絵文字成果物としては
    1 枚に統合する。ソースSVG（src/glyphs, ギリシャ文字セットの独立グリフ）は温存し、
    ここでは **出力PNGのみ** を対象に、全スキーム×全サイズで**バイト完全一致**する
    グリフだけを統合対象とする（1スキームでも差があれば統合しない＝安全側）。

    正規グリフはステム辞書順で最小のもの（ラテン < ギリシャ）を採用する。
    統合結果は ``MERGES_PATH`` に保存し、絵文字ビルダーがエイリアス付与に用いる。

    Returns:
        {正規ステム: [統合された非正規ステム, ...]} の辞書
    """
    variants = list(SCHEMES)
    ref_dir = DIST / variants[0]
    if not ref_dir.exists():
        return {}
    stems = sorted(p.name[: -len(f"_{SIZES[0]}.png")]
                   for p in ref_dir.glob(f"char_*_{SIZES[0]}.png"))

    # 各グリフの署名 = 全スキーム×全サイズ（幅可変）の出力バイトを連結ハッシュ
    signatures: dict[str, str] = {}
    for stem in stems:
        h = hashlib.md5()
        ok = True
        for v in variants:
            for sz in SIZES:
                f = DIST / v / f"{stem}_{sz}.png"
                if not f.exists():
                    ok = False
                    break
                h.update(f.read_bytes())
            if not ok:
                break
        if ok:
            signatures[stem] = h.hexdigest()

    seen: dict[str, str] = {}
    merges: dict[str, list[str]] = {}
    for stem in stems:                       # 辞書順（ラテンが先＝正規）
        sig = signatures.get(stem)
        if sig is None:
            continue
        if sig in seen:
            merges.setdefault(seen[sig], []).append(stem)
        else:
            seen[sig] = stem

    # 非正規PNGを全ディレクトリから削除
    removed = 0
    for dups in merges.values():
        for d in dups:
            for v in variants:
                for sz in SIZES:
                    for base in ((DIST, DIST_SQUARE) if square else (DIST,)):
                        p = base / v / f"{d}_{sz}.png"
                        try:
                            p.unlink()
                            removed += 1
                        except FileNotFoundError:
                            pass
                        except OSError as exc:
                            print(f"  WARN: 削除できません {p}: {exc}")

    # 統合表を保存（glyph_aliases.json のグリフ情報を付与）
    glyph_info: dict[str, dict] = {}
    if ALIASES_PATH.exists():
        glyph_info = json.loads(ALIASES_PATH.read_text(encoding="utf-8")).get("glyphs", {})

    def _info(stem: str) -> dict:
        gi = glyph_info.get(stem, {})
        return {"stem": stem, "glyph": gi.get("glyph", ""),
                "char": gi.get("char", ""), "agl": gi.get("agl", "")}

    doc = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("絵文字サイズで描画が完全一致する別グリフの統合表。ソースSVGは温存し、"
                 "出力PNGは正規側1枚に統合、非正規側は絵文字のエイリアスとして扱う。"),
        "merge_count": sum(len(v) for v in merges.values()),
        "merges": {
            canon: {"canonical": _info(canon),
                    "merged": [_info(d) for d in dups]}
            for canon, dups in sorted(merges.items())
        },
    }
    MERGES_PATH.parent.mkdir(parents=True, exist_ok=True)
    MERGES_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    if merges:
        pairs = ", ".join(
            f"{glyph_info.get(c, {}).get('char', c)}<={'/'.join(glyph_info.get(d, {}).get('char', d) for d in ds)}"
            for c, ds in sorted(merges.items())
        )
        print(f"  描画一致の統合: {sum(len(v) for v in merges.values())}件 "
              f"({removed} PNG削除)  {pairs}")
    return merges


def build(variant: str | None = None, limit: int | None = None, square: bool = True,
          dedupe: bool = True) -> int:
    """全スキーム（または指定スキーム）で src/glyphs を工業デカール化する。

    幅可変版（Misskey 向け）を dist/glyphs_decal/{variant}/ に、正方形版（Discord 向け）を
    dist/glyphs_decal_square/{variant}/ に出力する。

    Args:
        variant: スキームキー（rust/hazard/patina/nickel）。None なら全4種。
        limit:   先頭 N グリフのみ処理（試写用）。None なら全グリフ。
        square:  True で正方形版（Discord 向け）も併せて生成する。
        dedupe:  True かつ全スキーム生成時、描画完全一致グリフを統合する
                 （dedupe_renders）。単一スキーム/limit 指定時はスキップ。

    Returns:
        生成した (グリフ×スキーム) の件数
    """
    sources = sorted(SRC.glob("char_*.svg"))
    if not sources:
        print(f"WARN: {SRC} にSVGがありません。先に extract_glyphs.py を実行してください。")
        return 0

    # トリミング境界は全グリフから算出する（--limit でも共通バンドは全体基準）。
    bounds, vband = ensure_bounds(sources)

    if limit:
        sources = sources[:limit]

    targets = {variant: SCHEMES[variant]} if variant else SCHEMES
    count = 0
    for key, scheme in targets.items():
        out_dir = DIST / key
        sq_dir = (DIST_SQUARE / key) if square else None
        arrow = f"{out_dir}" + (f" + {sq_dir}" if square else "")
        print(f"[{key}] {scheme.label}（{scheme.finish}）→ {arrow}")
        for svg in sources:
            if svg.stem not in bounds:   # 空インク（通常発生しない）
                continue
            mask = load_mask(svg)
            img = render(mask, scheme, _seed_for(svg.stem + key))
            _save_all_sizes(img, out_dir, svg.stem, crop_box_for(svg.stem, bounds, vband),
                            square_dir=sq_dir)
            count += 1

    # 描画完全一致グリフの統合は全スキーム分が揃っている時のみ実施
    if dedupe and variant is None and not limit:
        dedupe_renders(square=square)

    return count


@click.command()
@click.option("--variant", "-v", type=click.Choice(list(SCHEMES.keys())),
              default=None, help="単一スキームのみ生成（未指定なら全4種）")
@click.option("--limit", "-n", type=int, default=None,
              help="先頭Nグリフのみ処理（試写用）")
@click.option("--no-square", is_flag=True, help="正方形版（Discord向け）を生成しない")
def main(variant: str | None, limit: int | None, no_square: bool) -> None:
    """PenchantManufacture グリフを工業デカール4スキームで生成します。"""
    print(f"入力    : {SRC}")
    print(f"出力(幅可変): {DIST}   … Misskey 向け")
    print(f"出力(正方形): {DIST_SQUARE if not no_square else '（生成しない）'}   … Discord 向け")
    print(f"対象    : {variant or '全4スキーム (' + ', '.join(SCHEMES) + ')'}")
    print(f"サイズ  : {SIZES}")
    print()
    n = build(variant=variant, limit=limit, square=not no_square)
    shapes = "幅可変" + ("＋正方形" if not no_square else "")
    print(f"\n完了: {n} 件（グリフ×スキーム）を生成しました（{shapes} × {len(SIZES)} サイズ）")


if __name__ == "__main__":
    main()
