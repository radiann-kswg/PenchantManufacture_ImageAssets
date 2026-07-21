"""SVGファイルをPNGに変換して dist/ または svg2png/ に出力する。

- ``export_category()``  : src/{category}/*.svg -> dist/{category}/{stem}_{size}.png
                           （72px / 512px の2サイズ、絵文字出力用）
- ``svg2png_category()`` : src/{category}/*.svg -> svg2png/{category}/{stem}.png
                           （装飾なしの単純PNG変換、ユーティリティ用途）

使い方:
    python scripts/export_png.py                 # glyphs を dist/ へ変換（動作確認）
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "src"
DIST_DIR = ROOT / "dist"
SVG2PNG_DIR = ROOT / "svg2png"

SIZES = {
    "72": 72,
    "512": 512,
}


def _render(svg_data: bytes, px: int, out_path: Path) -> None:
    """SVGバイト列を px 正方形の PNG として out_path に保存する。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    png_data = cairosvg.svg2png(bytestring=svg_data, output_width=px, output_height=px)
    img = Image.open(BytesIO(png_data)).convert("RGBA")
    img.save(str(out_path), "PNG", optimize=True)


def svg_to_png(
    svg_path: Path,
    category: str,
    filename_stem: str,
    sizes: dict[str, int] = SIZES,
) -> list[Path]:
    """SVGを指定サイズのPNGに変換し dist/{category}/ に出力する。

    Args:
        svg_path: 変換元SVGファイル
        category: 出力カテゴリ（例: glyphs）
        filename_stem: ファイル名（拡張子・サイズサフィックスなし）
        sizes: {サフィックス: ピクセル数} の辞書

    Returns:
        生成したPNGファイルのパスリスト
    """
    svg_data = svg_path.read_bytes()
    outputs: list[Path] = []
    for suffix, px in sizes.items():
        out_path = DIST_DIR / category / f"{filename_stem}_{suffix}.png"
        _render(svg_data, px, out_path)
        outputs.append(out_path)
        print(f"  Exported: {out_path} ({px}px)")
    return outputs


def export_category(category: str = "glyphs", sizes: dict[str, int] = SIZES) -> None:
    """src/{category}/ 内の全SVGを dist/{category}/ にPNG変換する。

    Args:
        category: カテゴリ名（例: glyphs）
        sizes: {サフィックス: ピクセル数} の辞書
    """
    src_dir = SRC_DIR / category
    if not src_dir.exists():
        print(f"Warning: {src_dir} が存在しません")
        return
    svgs = sorted(src_dir.glob("*.svg"))
    print(f"[{category}] {len(svgs)}件のSVGを dist/ に変換中...")
    for svg in svgs:
        svg_to_png(svg, category, svg.stem, sizes=sizes)
    print(f"[{category}] 完了")


def svg2png_category(category: str = "glyphs", px: int = 512) -> None:
    """src/{category}/ 内の全SVGを svg2png/{category}/ に単純PNG変換する。

    Args:
        category: カテゴリ名（例: glyphs）
        px: 出力ピクセル数（正方形）
    """
    src_dir = SRC_DIR / category
    if not src_dir.exists():
        print(f"Warning: {src_dir} が存在しません")
        return
    svgs = sorted(src_dir.glob("*.svg"))
    print(f"[{category}] {len(svgs)}件のSVGを svg2png/ に単純変換中...")
    for svg in svgs:
        out_path = SVG2PNG_DIR / category / f"{svg.stem}.png"
        _render(svg.read_bytes(), px, out_path)
        print(f"  Exported: {out_path} ({px}px)")
    print(f"[{category}] 完了")


if __name__ == "__main__":
    export_category("glyphs")
