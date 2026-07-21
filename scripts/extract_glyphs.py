"""PenchantManufacture フォントのグリフをアウトライン化SVGとして抽出する。

fontTools の SVGPathPen を使い、フォントに依存しない純粋なSVGパス（<path d="...">）を
src/glyphs/ に出力する。生成SVGは外部フォント参照を一切持たない。

対象グリフ:
    デフォルトでは cmap にマッピングされた **全コードポイント** を対象とする
    （ASCII記号・数字・英大文字、ギリシャ文字、アクセント付きラテン、曲がり引用符など）。
    空パスのグリフ（スペース・NBSP・制御文字）は自動的にスキップされる。

ファイル名（case-insensitive な Windows でも衝突しない安全命名）:
    char_{AGL名}_{コードポイント16進}.svg
    例: char_A_0041.svg / char_a_0061.svg / char_zero_0030.svg
        char_exclam_0021.svg / char_Alpha_0391.svg / char_quoteleft_2018.svg

使い方:
    python scripts/extract_glyphs.py
    python scripts/extract_glyphs.py --viewbox 256
    python scripts/extract_glyphs.py --out-dir src/glyphs
    python scripts/extract_glyphs.py --dry-run
"""
from __future__ import annotations

import re
from pathlib import Path

import click
from fontTools import agl, ttLib
from fontTools.pens.svgPathPen import SVGPathPen

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "PenchantManufacture.otf"
OUT_DIR = Path(__file__).parent.parent / "src" / "glyphs"
VIEWBOX = 512

FONT_TITLE = "PenchantManufacture"

_SAFE_RE = re.compile(r"[^A-Za-z0-9]+")


def char_to_stem(codepoint: int, glyph_name: str) -> str:
    """コードポイントとフォントグリフ名から安全なファイル名ステムを生成する。

    AGL（Adobe Glyph List）名を優先し、無ければフォントのグリフ名、
    それも不適なら ``uniXXXX`` にフォールバックする。末尾にコードポイントを
    付与することで、case-insensitive なファイルシステム（Windows）でも
    大文字/小文字グリフ（A vs a, Alpha vs alpha）が衝突しないようにする。

    Args:
        codepoint: Unicode コードポイント
        glyph_name: フォント内グリフ名

    Returns:
        ``char_{base}_{CP:04X}`` 形式のファイル名ステム
    """
    base = agl.UV2AGL.get(codepoint)
    if not base:
        base = glyph_name or f"uni{codepoint:04X}"
    base = _SAFE_RE.sub("_", base).strip("_")
    if not base:
        base = f"uni{codepoint:04X}"
    return f"char_{base}_{codepoint:04X}"


def extract_glyph_svg(
    glyph_name: str,
    glyph_set: object,
    hmtx_metrics: dict[str, tuple[int, int]],
    ascender: int,
    upm: int,
    viewbox: int,
    title: str,
) -> str | None:
    """1グリフのアウトライン化SVG文字列を生成する。

    Args:
        glyph_name: フォント内グリフ名（例: 'A', 'zero', 'Alpha'）
        glyph_set:  fontTools glyphSet オブジェクト
        hmtx_metrics: {グリフ名: (advanceWidth, lsb)} のマップ
        ascender:   フォントのアセンダー高さ（フォントユニット）
        upm:        Units Per Em
        viewbox:    出力SVGのviewBoxサイズ（正方形）
        title:      SVG <title> 要素のテキスト

    Returns:
        SVG文字列、またはパスデータが空の場合は None
    """
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    path_data: str = pen.getCommands()

    if not path_data.strip():
        return None  # space / nbsp / 制御文字 等の空グリフはスキップ

    advance_width, _ = hmtx_metrics.get(glyph_name, (upm, 0))

    # フォント座標系（Y上方向）→ SVG座標系（Y下方向）の変換
    # 変換行列: matrix(sx, 0, 0, -sx, tx, ty)
    #   sx = viewbox / upm  （スケール）
    #   ty = ascender * sx  （ベースライン位置をY軸に反映）
    #   tx = グリフを水平中央揃えするオフセット
    scale = viewbox / upm
    glyph_width_px = advance_width * scale
    tx = (viewbox - glyph_width_px) / 2
    ty = ascender * scale

    transform = f"matrix({scale:.6f},0,0,{-scale:.6f},{tx:.3f},{ty:.3f})"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {viewbox} {viewbox}"\n'
        f'     width="{viewbox}" height="{viewbox}">\n'
        f"  <title>{title}</title>\n"
        f'  <g transform="{transform}">\n'
        f'    <path d="{path_data}" fill="#000000"/>\n'
        "  </g>\n"
        "</svg>\n"
    )


def extract_all(
    font_path: Path = FONT_PATH,
    out_dir: Path = OUT_DIR,
    viewbox: int = VIEWBOX,
    dry_run: bool = False,
) -> list[Path]:
    """cmap 全コードポイントのアウトライン化SVGを out_dir に出力する。

    Args:
        font_path: PenchantManufacture OTFファイルのパス
        out_dir:   出力ディレクトリ
        viewbox:   SVG viewBoxサイズ（px）
        dry_run:   True の場合はファイルを書き出さず対象のみ表示する

    Returns:
        生成した（または dry-run で生成予定の）SVGファイルのパスリスト
    """
    tt = ttLib.TTFont(str(font_path))
    glyph_set = tt.getGlyphSet()
    cmap = tt.getBestCmap()
    hmtx_metrics: dict[str, tuple[int, int]] = tt["hmtx"].metrics
    upm: int = tt["head"].unitsPerEm

    # アセンダー取得（OS/2 優先、なければ hhea）
    try:
        ascender: int = tt["OS/2"].sTypoAscender
    except (KeyError, AttributeError):
        ascender = tt["hhea"].ascender

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    produced: list[Path] = []
    skipped_empty = 0

    for codepoint in sorted(cmap.keys()):
        glyph_name = cmap[codepoint]
        stem = char_to_stem(codepoint, glyph_name)
        char = chr(codepoint)
        printable = char if char.isprintable() else f"U+{codepoint:04X}"
        title = f"{FONT_TITLE} {printable}"

        svg = extract_glyph_svg(
            glyph_name, glyph_set, hmtx_metrics,
            ascender, upm, viewbox, title,
        )
        if svg is None:
            skipped_empty += 1
            continue

        out_path = out_dir / f"{stem}.svg"
        produced.append(out_path)
        if dry_run:
            print(f"  DRY-RUN: {out_path.name}  (glyph={glyph_name!r}, U+{codepoint:04X})")
        else:
            out_path.write_text(svg, encoding="utf-8")
            print(f"  OK: {out_path.name}  (glyph={glyph_name!r})")

    print(f"\n対象 {len(produced)} グリフ / 空グリフ {skipped_empty} 件スキップ")
    return produced


@click.command()
@click.option("--font", "font_path", default=str(FONT_PATH), show_default=True,
              help="PenchantManufacture OTFファイルのパス")
@click.option("--out-dir", default=str(OUT_DIR), show_default=True,
              help="SVG出力ディレクトリ")
@click.option("--viewbox", default=VIEWBOX, show_default=True,
              help="SVG viewBoxサイズ（px、正方形）")
@click.option("--dry-run", is_flag=True, help="ファイルを生成せず対象を表示")
def main(font_path: str, out_dir: str, viewbox: int, dry_run: bool) -> None:
    """PenchantManufacture フォントの cmap 全グリフをアウトライン化SVGに変換します。"""
    fp = Path(font_path)
    od = Path(out_dir)

    print(f"フォント : {fp}")
    print(f"出力先   : {od}")
    print(f"viewBox  : {viewbox}x{viewbox}")
    print(f"モード   : {'DRY-RUN' if dry_run else '書き出し'}")
    print()

    paths = extract_all(fp, od, viewbox, dry_run=dry_run)

    verb = "生成予定" if dry_run else "生成"
    print(f"\n完了: {len(paths)} グリフを{verb}しました")


if __name__ == "__main__":
    main()
