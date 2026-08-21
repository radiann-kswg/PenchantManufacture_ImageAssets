"""合成ローマ数字（XIII〜XXXIX）専用ビルドスクリプト。

PenchantManufacture v4.0-beta のローマ数字は、通常グリフと**コンセプトが異なる**:

- 字幅が「構成文字数分の advance」を持つ（例 Ⅷ は約 1 em 超）。
- 「Ⅹ」「ⅹ」の**直後に来るローマ数字**へ GPOS カーニング（字詰め）が定義されており、
  Ⅹ を連結すると XIII〜XXXIX（13〜39）を 1 つの字面として組める設計になっている。

単独グリフは Ⅰ–Ⅻ / ⅰ–ⅻ の 24 字のみで、これらは通常パイプライン
（extract_glyphs → generate_decal）がそのまま処理する。一方、カスタム絵文字は
1 枚ずつ独立した画像のため、**絵文字を並べてもカーニングは働かない**。
そこで本スクリプトが 13〜39（大小 54 点）を、フォントのカーニングを適用した
**合成SVG → 合成デカール** として事前生成する。

構成規則（フォントのカーニングペア実装と一致。Ⅹ＋Ⅰ／Ⅹ＋Ⅱ のペアは存在せず、
21・22 は Ⅺ・Ⅻ グリフを使う）:

    13〜19 = Ⅹ＋Ⅲ〜Ⅸ    20 = Ⅹ＋Ⅹ    21 = Ⅹ＋Ⅺ    22 = Ⅹ＋Ⅻ
    23〜29 = Ⅹ＋Ⅹ＋Ⅲ〜Ⅸ  30 = Ⅹ＋Ⅹ＋Ⅹ  31 = Ⅹ＋Ⅹ＋Ⅺ  …  39 = Ⅹ＋Ⅹ＋Ⅹ＋Ⅸ

出力:
    src/glyphs_roman/roman_{u|l}{13..39}.svg              合成ソース（横長 viewBox）
    dist/glyphs_roman/{variant}/roman_*_{512,128}.png       幅可変（**Misskey 専用**）
    docs/glyph_romans.json                                絵文字ビルダー用対応表

合成 13〜39 は **Misskey 専用**。Discord は絵文字を正方形スロットで表示するため、
横長の合成字（XXXVIII 等）は正方形パディングでは字が小さくなりすぎる。
Discord へはローマ数字の単独グリフ 24 字（dist/glyphs_decal_square/ の正方形版）のみ
登録する運用とし、本スクリプトは正方形版を生成しない。

デカール描画は generate_decal.py の実装（SDF・5スキーム・シード）を共用し、
質感・縁取り・配置契約（win 帯）を単独グリフと完全に揃える。

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0

使い方:
    python scripts/generate_roman.py                 # SVG合成＋全5スキーム描画
    python scripts/generate_roman.py --variant sumi  # 単一スキームのみ
    python scripts/generate_roman.py --dry-run       # 対象の確認のみ
    python scripts/generate_roman.py --font "_original-fonts/.develop/..../PenchantManufacture.otf"
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import click
from fontTools import ttLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

from extract_glyphs import FONT_PATH, FONT_TITLE, VIEWBOX, metrics_fit
from generate_decal import (
    SCHEMES,
    _save_all_sizes,
    _seed_for,
    frame_box,
    load_mask,
    render,
)
from glyph_tokens import roman_reading, roman_token

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "glyphs_roman"
DIST = ROOT / "dist" / "glyphs_roman"
ROMANS_PATH = ROOT / "docs" / "glyph_romans.json"

VALUES = range(13, 40)          # 合成対象（13〜39）。1〜12 は単独グリフが通常経路で処理
MARGIN_PX = 30.0                # SVG 左右余白（クロップはフレーム基準のため装飾値）


def component_values(value: int) -> list[int]:
    """13〜39 を単独グリフ値（1〜12）の連結列へ分解する。

    フォントのカーニングペア（Ⅹ＋Ⅲ〜Ⅻ のみ定義）と同じ構成規則を使う。
    末尾 1・2 は Ⅹ＋Ⅰ ではなく Ⅺ・Ⅻ グリフで表す。
    """
    tens, unit = divmod(value, 10)
    if unit in (1, 2):          # 21→Ⅹ＋Ⅺ / 22→Ⅹ＋Ⅻ（Ⅹ＋Ⅰのペアは無い）
        tens -= 1
        unit += 10
    return [10] * tens + ([unit] if unit else [])


def roman_codepoint(value: int, upper: bool) -> int:
    """単独ローマ数字グリフ（1〜12）のコードポイントを返す。"""
    return (0x2160 if upper else 0x2170) + value - 1


def load_kern_pairs(tt: ttLib.TTFont) -> dict[tuple[str, str], int]:
    """GPOS の PairPos（Format 1 / 2）から水平カーニング {(左, 右): XAdvance} を読む。"""
    pairs: dict[tuple[str, str], int] = {}
    if "GPOS" not in tt:
        return pairs
    glyph_order = tt.getGlyphOrder()
    for lookup in tt["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            st = getattr(sub, "ExtSubTable", sub)
            if getattr(st, "Coverage", None) is None:
                continue
            if hasattr(st, "PairSet"):          # Format 1（グリフペア）
                for g1, ps in zip(st.Coverage.glyphs, st.PairSet):
                    for rec in ps.PairValueRecord:
                        x = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                        if x:
                            pairs[(g1, rec.SecondGlyph)] = x
            elif hasattr(st, "ClassDef1"):      # Format 2（クラスペア）
                c1, c2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                by_c1: dict[int, list[str]] = {}
                for g in st.Coverage.glyphs:
                    by_c1.setdefault(c1.get(g, 0), []).append(g)
                by_c2: dict[int, list[str]] = {}
                for g in glyph_order:
                    if g in c2:
                        by_c2.setdefault(c2[g], []).append(g)
                for i, cr in enumerate(st.Class1Record):
                    for j, rec in enumerate(cr.Class2Record):
                        x = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                        if not x:
                            continue
                        for ga in by_c1.get(i, []):
                            for gb in by_c2.get(j, []):
                                pairs[(ga, gb)] = x
    return pairs


def compose_svg(
    value: int,
    upper: bool,
    tt: ttLib.TTFont,
    kern: dict[tuple[str, str], int],
) -> tuple[str, dict]:
    """1つの合成ローマ数字の SVG 文字列と対応表エントリを生成する。

    縦配置は extract_glyphs.metrics_fit（OS/2 win 帯）を単独グリフと共用し、
    横は「advance の累積＋カーニング」で連結する（配置契約は通常グリフと同一）。

    Returns:
        (SVG文字列, glyph_romans.json 用エントリ辞書)
    """
    cmap = tt.getBestCmap()
    glyph_set = tt.getGlyphSet()
    hmtx = tt["hmtx"].metrics
    upm: int = tt["head"].unitsPerEm
    fit = metrics_fit(tt["OS/2"], upm, VIEWBOX)
    scale = fit.scale

    comps = component_values(value)
    glyphs = [cmap[roman_codepoint(v, upper)] for v in comps]

    # 横位置（フォント units）: advance 累積＋直前ペアのカーニング
    xs: list[float] = []
    x = 0.0
    kerns_used: list[int] = []
    for i, g in enumerate(glyphs):
        if i > 0:
            k = kern.get((glyphs[i - 1], g), 0)
            if k == 0:
                print(f"  WARN: カーニングペア ({glyphs[i-1]}, {g}) がフォントにありません")
            kerns_used.append(k)
            x += k
        xs.append(x)
        x += hmtx[g][0]
    total_advance = x

    # パスとインク境界
    paths: list[str] = []
    ink_x0 = ink_x1 = None
    for g, gx in zip(glyphs, xs):
        pen = SVGPathPen(glyph_set)
        glyph_set[g].draw(pen)
        paths.append(f'    <path transform="translate({gx:.1f},0)" '
                     f'd="{pen.getCommands()}" fill="#000000"/>')
        bpen = BoundsPen(glyph_set)
        glyph_set[g].draw(bpen)
        bx0, _by0, bx1, _by1 = bpen.bounds
        ink_x0 = bx0 + gx if ink_x0 is None else min(ink_x0, bx0 + gx)
        ink_x1 = bx1 + gx if ink_x1 is None else max(ink_x1, bx1 + gx)

    # 配置フレーム（generate_decal.frame_box が読む。通常グリフと同じ規約:
    # 横 = advance 幅 ∪ インク / 縦 = win 帯）
    tx = MARGIN_PX
    fx0 = min(0.0, ink_x0) * scale + tx
    fx1 = max(total_advance, ink_x1) * scale + tx
    fy1 = (fit.top - fit.bottom) * scale
    vb_w = round(fx1 + MARGIN_PX)

    chars = "".join(chr(roman_codepoint(v, upper)) for v in comps)
    title = f"{FONT_TITLE} {chars} ({value})"
    transform = f"matrix({scale:.6f},0,0,{-scale:.6f},{tx:.3f},{fit.ty:.3f})"
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {vb_w} {VIEWBOX}"\n'
        f'     width="{vb_w}" height="{VIEWBOX}">\n'
        f"  <title>{escape(title)}</title>\n"
        f"  <!-- frame x={fx0:.3f},{fx1:.3f} y=0.000,{fy1:.3f} -->\n"
        f'  <g transform="{transform}">\n'
        + "\n".join(paths) + "\n"
        "  </g>\n"
        "</svg>\n"
    )

    case = "upper" if upper else "lower"
    token = roman_token(value, upper)
    reading = roman_reading(value)
    entry = {
        "stem": f"roman_{'u' if upper else 'l'}{value}",
        "value": value,
        "case": case,
        "token": token,
        "chars": chars,                      # 合成に使った単独グリフ列（例 ⅩⅢ）
        "reading": reading if not upper else reading.upper(),
        "components": glyphs,
        "kerns": kerns_used,
        "aliases": [
            "roman", "ローマ数字", str(value),
            reading, chars,
        ],
    }
    return svg, entry


def build_svgs(font_path: Path = FONT_PATH, dry_run: bool = False) -> list[dict]:
    """13〜39 × 大小の合成SVGを生成し、対応表エントリのリストを返す。"""
    tt = ttLib.TTFont(str(font_path))
    kern = load_kern_pairs(tt)
    n_roman_kerns = sum(1 for (a, _b) in kern if a.lower() == "tenroman")
    print(f"  カーニング: 全 {len(kern)} ペア（うち Ⅹ/ⅹ 起点 {n_roman_kerns} ペア）")

    if not dry_run:
        SRC.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for upper in (True, False):
        for value in VALUES:
            svg, entry = compose_svg(value, upper, tt, kern)
            entries.append(entry)
            out = SRC / f"{entry['stem']}.svg"
            if dry_run:
                print(f"  DRY-RUN: {out.name}  ({entry['chars']} = {value})")
            else:
                out.write_text(svg, encoding="utf-8")
    if not dry_run:
        print(f"  合成SVG: {len(entries)} 点 → {SRC}")
    return entries


def write_romans_json(entries: list[dict]) -> None:
    """docs/glyph_romans.json（絵文字ビルダー用対応表）を書き出す。"""
    doc = {
        "font": FONT_TITLE,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": (
            "合成ローマ数字（13〜39）の対応表。単独グリフに無い値を、フォントの "
            "GPOS カーニング（Ⅹ/ⅹ 直後の字詰め）を適用した連結字面として事前生成する。"
            "build_misskey_zip.py が絵文字エントリ化に使う。"
        ),
        "count": len(entries),
        "romans": entries,
    }
    ROMANS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ROMANS_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    print(f"  対応表: {ROMANS_PATH}")


def build_decals(variant: str | None = None) -> int:
    """src/glyphs_roman の合成SVGを工業デカール化する（generate_decal と同一質感）。

    幅可変版のみ生成する（Misskey 専用。正方形版は作らない — モジュール docstring 参照）。
    """
    sources = sorted(SRC.glob("roman_*.svg"))
    if not sources:
        print(f"WARN: {SRC} にSVGがありません。先に SVG 合成を実行してください。")
        return 0
    targets = {variant: SCHEMES[variant]} if variant else SCHEMES
    count = 0
    for key, scheme in targets.items():
        out_dir = DIST / key
        print(f"[{key}] {scheme.label}（{scheme.finish}）→ {out_dir}")
        for svg in sources:
            mask = load_mask(svg)
            img = render(mask, scheme, _seed_for(svg.stem + key))
            _save_all_sizes(img, out_dir, svg.stem, frame_box(svg))
            count += 1
    return count


def build(font_path: Path = FONT_PATH, variant: str | None = None,
          dry_run: bool = False) -> int:
    """SVG合成 → 対応表 → デカール描画 を一括実行する。"""
    entries = build_svgs(font_path, dry_run=dry_run)
    if dry_run:
        print(f"  DRY-RUN: {DIST}/ に {len(entries)} 点 × スキーム × 2サイズを生成予定"
              "（幅可変のみ・Misskey 専用）")
        return 0
    write_romans_json(entries)
    return build_decals(variant=variant)


@click.command()
@click.option("--font", "font_path", default=str(FONT_PATH), show_default=True,
              help="PenchantManufacture OTFファイルのパス")
@click.option("--variant", "-v", type=click.Choice(list(SCHEMES.keys())),
              default=None, help="単一スキームのみ生成（未指定なら全5種）")
@click.option("--dry-run", is_flag=True, help="ファイルを生成せず対象を表示")
def main(font_path: str, variant: str | None, dry_run: bool) -> None:
    """合成ローマ数字（XIII〜XXXIX）をカーニング適用で組版し、工業デカール化します。"""
    print(f"フォント : {font_path}")
    print(f"出力(SVG): {SRC}")
    print(f"出力(幅可変): {DIST}   … Misskey 専用（Discord は単独24字のみ登録）")
    print()
    n = build(Path(font_path), variant=variant, dry_run=dry_run)
    if not dry_run:
        print(f"\n完了: {n} 件（合成字×スキーム）を生成しました")


if __name__ == "__main__":
    main()
