"""PenchantManufacture フォントのグリフ情報を検査し、docs/glyph_map.txt に出力する。

Secvier ImageAssets の inspect_font.py を PenchantManufacture 向けに移植したもの。
cmap（Unicode → グリフ名）と全グリフ名を一覧化し、利用可能グリフを把握するための
一次資料として `docs/glyph_map.txt` を生成する。

使い方:
    python scripts/inspect_font.py
"""
from __future__ import annotations

from pathlib import Path

from fontTools import agl, ttLib

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "PenchantManufacture.otf"
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "glyph_map.txt"

FONT_TITLE = "PenchantManufacture"


def inspect_font(font_path: Path = FONT_PATH, output: Path = OUTPUT_PATH) -> None:
    """フォントを読み込み、グリフ名・Unicodeマッピングを出力する。

    Args:
        font_path: OTFフォントファイルのパス
        output: 出力テキストファイルのパス
    """
    tt = ttLib.TTFont(str(font_path))

    cmap = tt.getBestCmap()
    glyph_set = tt.getGlyphSet()
    upm: int = tt["head"].unitsPerEm

    lines: list[str] = [
        f"# {FONT_TITLE} Glyph Map",
        f"# Font: {font_path.name}",
        f"# Units per em: {upm}",
        f"# Total glyphs: {len(glyph_set)}",
        f"# Unicode mapped glyphs: {len(cmap) if cmap else 0}",
        "",
        "## Unicode -> Glyph Name (AGL name)",
        "",
    ]

    if cmap:
        for codepoint in sorted(cmap.keys()):
            glyph_name = cmap[codepoint]
            char = chr(codepoint)
            printable = char if char.isprintable() else "."
            agl_name = agl.UV2AGL.get(codepoint, "-")
            lines.append(
                f"U+{codepoint:04X}  {printable!r:5}  glyph={glyph_name:<16}  agl={agl_name}"
            )

    lines += [
        "",
        "## All Glyph Names",
        "",
    ]
    for name in sorted(glyph_set.keys()):
        lines.append(f"  {name}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Glyph map written to: {output}")
    print(f"  Total glyphs: {len(glyph_set)}")
    if cmap:
        print(f"  Unicode mapped: {len(cmap)}")


if __name__ == "__main__":
    inspect_font()
