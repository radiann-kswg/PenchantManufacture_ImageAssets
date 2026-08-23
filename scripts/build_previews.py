#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_previews.py — README 冒頭用のプレビュー画像を生成する。

  docs/previews/hero.png     … 工業デカール全バリアントの横長バナー
                               （各行がバリアント名を自身のデカールで綴る）
  docs/previews/glyphset.png … 収録グリフ一覧（Unicodeブロック別・ブロック毎に
                               バリアントを巡回させ、収録範囲と作風を同時に見せる）

入力は `dist/glyphs_decal/{バリアント}/` と `dist/glyphs_roman/{バリアント}/` の
生成済み PNG。依存: Pillow
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist" / "glyphs_decal"
ROMAN = ROOT / "dist" / "glyphs_roman"
OUT = ROOT / "docs" / "previews"

BG = (28, 28, 30)
TXT = (200, 200, 205)
SUB = (130, 130, 138)
VARIANTS = ["hazard", "nickel", "patina", "rust", "sumi"]

# ラベル, コードポイント範囲（Unicodeブロック単位のざっくり分類。範囲は重複させない）
BLOCKS: list[tuple[str, list[tuple[int, int]]]] = [
    ("Basic Latin  U+0021-007E", [(0x0021, 0x007E)]),
    ("Latin-1 Supplement  U+00A1-00FF", [(0x00A0, 0x00FF)]),
    ("Latin Extended  U+0100-024F, U+1E00-1EFF", [(0x0100, 0x024F), (0x1E00, 0x1EFF)]),
    ("Greek  U+0370-03FF", [(0x0370, 0x03FF)]),
    ("Cyrillic  U+0400-04FF", [(0x0400, 0x04FF)]),
    ("Punctuation  U+2000-206F", [(0x2000, 0x206F)]),
    ("Super / Subscripts  U+2070-209F", [(0x2070, 0x209F)]),
    ("Currency  U+20A0-20BF", [(0x20A0, 0x20BF)]),
    ("Letterlike  U+2100-214F", [(0x2100, 0x214F)]),
    ("Roman Numerals  U+2160-217F", [(0x2150, 0x218F)]),
    ("Math Operators  U+2200-22FF", [(0x2200, 0x22FF)]),
]


def load(path: Path, height: int) -> Image.Image:
    """PNG を高さ height に縮小して返す（アスペクト比維持）。"""
    im = Image.open(path).convert("RGBA")
    return im.resize((max(1, round(im.width * height / im.height)), height),
                     Image.LANCZOS)


def glyph(variant: str, ch: str, height: int) -> Image.Image | None:
    """1 文字ぶんのデカール PNG（無ければ None）。"""
    p = DIST / variant / f"char_{ch}_{ord(ch):04X}_512.png"
    return load(p, height) if p.exists() else None


def build_hero(cell: int = 110, pad: int = 20, gap: int = 8, space: int = 44) -> None:
    """各バリアント名を、そのバリアント自身のデカールで綴った 1 行バナー。"""
    words = [[g for ch in v.upper() if (g := glyph(v, ch, cell))] for v in VARIANTS]
    words = [w for w in words if w]
    if not words:
        raise SystemExit("dist/glyphs_decal/ が空です。先に build.py を実行してください。")
    W = pad * 2 + sum(sum(g.width for g in w) + gap * (len(w) - 1) for w in words) \
        + space * (len(words) - 1)
    s = Image.new("RGB", (W, pad * 2 + cell), BG)
    x = pad
    for w in words:
        for g in w:
            s.paste(g, (x, pad), g)
            x += g.width + gap
        x += space - gap
    OUT.mkdir(parents=True, exist_ok=True)
    s.save(OUT / "hero.png")
    print("hero ->", OUT / "hero.png", s.size)


def group_by_block(variant: str) -> list[tuple[str, list[Path]]]:
    """1 バリアントの収録 512px PNG を Unicode ブロック別に仕分けする。"""
    entries: list[tuple[int, Path]] = []
    for p in (DIST / variant).glob("char_*_512.png"):
        m = re.search(r"_([0-9A-F]{4})_512\.png$", p.name)
        if m:
            entries.append((int(m.group(1), 16), p))
    groups = []
    for label, ranges in BLOCKS:
        paths = [p for cp, p in sorted(entries)
                 if any(lo <= cp <= hi for lo, hi in ranges)]
        if paths:
            groups.append((label, paths))
    assert sum(len(p) for _, p in groups) == len(entries), \
        "BLOCKS の範囲が重複しているか、未分類のコードポイントがあります"
    return groups


def flow(draw: ImageDraw.ImageDraw, sheet: Image.Image | None, paths: list[Path],
         x0: int, y0: int, width: int, cell: int, gap: int) -> int:
    """paths を左→右に流し込み、width で折り返す。消費した高さを返す。

    sheet=None のときは描画せず高さ計算のみ（2 パス用）。
    """
    x, y = x0, y0
    for p in paths:
        im = load(p, cell)
        if x > x0 and x + im.width > x0 + width:
            x, y = x0, y + cell + gap
        if sheet is not None:
            sheet.paste(im, (x, y + (cell - im.height) // 2), im)
        x += im.width + gap
    return y + cell - y0


def build_glyphset(cell: int = 52, pad: int = 24, gap: int = 7, width: int = 1240) -> None:
    """収録グリフ一覧シート。ブロック毎にバリアントを巡回して作風も見せる。"""
    blocks = group_by_block(VARIANTS[-1])
    if not blocks:
        raise SystemExit("dist/glyphs_decal/ が空です。先に build.py を実行してください。")
    roman_all = sorted((ROMAN / VARIANTS[0]).glob("roman_*_512.png"))
    romans = [p for kind in ("u", "l")
              for p in sorted((ROMAN / VARIANTS[0]).glob(f"roman_{kind}*_512.png"),
                              key=lambda p: int(re.search(r"\d+", p.stem).group()))[:12]]
    title_f, head_f, note_f = (ImageFont.load_default(size=s) for s in (34, 20, 15))
    head_h, sec_gap = 34, 26

    def render(sheet: Image.Image | None) -> int:
        draw = ImageDraw.Draw(sheet) if sheet else ImageDraw.Draw(Image.new("RGB", (1, 1)))
        y = pad
        if sheet:
            draw.text((pad, y), "PenchantManufacture  /  industrial decal glyph set",
                      font=title_f, fill=TXT)
            draw.text((pad, y + 42),
                      f"{sum(len(p) for _, p in blocks)} glyphs  x  "
                      f"{len(VARIANTS)} variants ({', '.join(VARIANTS)})",
                      font=note_f, fill=SUB)
        y += 74
        for i, (label, paths) in enumerate(blocks):
            variant = VARIANTS[i % len(VARIANTS)]
            paths = [DIST / variant / p.name for p in paths]
            paths = [p for p in paths if p.exists()]
            if sheet:
                draw.text((pad, y), f"{label}   [{variant}]  {len(paths)}",
                          font=head_f, fill=SUB)
            y += head_h + flow(draw, sheet, paths, pad, y + head_h, width, cell, gap)
            y += sec_gap
        if romans:
            if sheet:
                draw.text((pad, y),
                          f"Composed Roman Numerals 13-39 (upper / lower)   "
                          f"[{VARIANTS[0]}]  {len(roman_all)}  -  13-24 shown",
                          font=head_f, fill=SUB)
            y += head_h + flow(draw, sheet, romans, pad, y + head_h, width, cell, gap)
        return y + pad

    height = render(None)
    sheet = Image.new("RGB", (width + pad * 2, height), BG)
    render(sheet)
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "glyphset.png")
    print("glyphset ->", OUT / "glyphset.png", sheet.size)


if __name__ == "__main__":
    build_hero()
    build_glyphset()
