#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_previews.py — README 冒頭用のプレビュー画像を生成する。

  docs/previews/hero.png … 工業デカール全バリアントの横長バナー
                           （各行がバリアント名を自身のデカールで綴る）

入力は `dist/glyphs_decal/{バリアント}/` の生成済み PNG。依存: Pillow
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist" / "glyphs_decal"
OUT = ROOT / "docs" / "previews"

BG = (28, 28, 30)
VARIANTS = ["hazard", "nickel", "patina", "rust", "sumi"]


def glyph(variant: str, ch: str, height: int) -> Image.Image | None:
    """デカール PNG を高さ height に縮小して返す（無ければ None）。"""
    p = DIST / variant / f"char_{ch}_{ord(ch):04X}_512.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    return im.resize((max(1, round(im.width * height / im.height)), height),
                     Image.LANCZOS)


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


if __name__ == "__main__":
    build_hero()
