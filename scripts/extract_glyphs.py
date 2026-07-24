"""PenchantManufacture フォントのグリフをアウトライン化SVGとして抽出する。

fontTools の SVGPathPen を使い、フォントに依存しない純粋なSVGパス（<path d="...">）を
src/glyphs/ に出力する。生成SVGは外部フォント参照を一切持たない。

対象グリフ（重複排除つき）:
    cmap にマッピングされた全コードポイント（210）を走査するが、**同一グリフ（同一
    アウトライン）へ再マップされたコードポイントは 1 枚に統合** する。PenchantManufacture の
    cmap はアクセント付きラテン（À Á Â … ø ù … Ÿ など計56点）を基底グリフ（A/E/I/O/U/Y/C/N
    とその小文字）へ再マップしているため、素朴に全コードポイントを書き出すと**視覚的に同一の
    SVG が別名で二重生成される**（例: char_A_0041.svg と char_Aacute_00C1.svg が同一画像）。
    これを避け、グリフ名（＝アウトライン同一性）でユニーク化した **148 字のみ** を出力する。
    空パスのグリフ（スペース・NBSP・制御文字）は従来どおり自動スキップ。

異体字は削除せず、正規グリフへの**エイリアス**として ``docs/glyph_aliases.json`` に記録する。
Misskey/Discord の絵文字ビルダー（build_misskey_zip.py 等）がこの対応表を読み、
基底グリフの絵文字にアクセント付き文字の検索エイリアスを付与する。

ファイル名（case-insensitive な Windows でも衝突しない安全命名）:
    char_{AGL名}_{コードポイント16進}.svg
    例: char_A_0041.svg / char_a_0061.svg / char_zero_0030.svg
        char_exclam_0021.svg / char_Alpha_0391.svg / char_quoteleft_2018.svg
    ステム末尾のコードポイントは各グリフの**正規（最小）コードポイント**を用いる。

使い方:
    python scripts/extract_glyphs.py
    python scripts/extract_glyphs.py --viewbox 256
    python scripts/extract_glyphs.py --out-dir src/glyphs
    python scripts/extract_glyphs.py --dry-run
    python scripts/extract_glyphs.py --no-prune   # 旧SVGを削除しない
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import click
from fontTools import agl, ttLib
from fontTools.pens.svgPathPen import SVGPathPen

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "PenchantManufacture.otf"
OUT_DIR = Path(__file__).parent.parent / "src" / "glyphs"
ALIASES_PATH = Path(__file__).parent.parent / "docs" / "glyph_aliases.json"
VIEWBOX = 512

FONT_TITLE = "PenchantManufacture"

_SAFE_RE = re.compile(r"[^A-Za-z0-9]+")


def _agl_name(codepoint: int, glyph_name: str) -> str:
    """コードポイントの AGL 名（無ければグリフ名 / uniXXXX）を返す。"""
    base = agl.UV2AGL.get(codepoint)
    if not base:
        base = glyph_name or f"uni{codepoint:04X}"
    base = _SAFE_RE.sub("_", base).strip("_")
    return base or f"uni{codepoint:04X}"


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
    return f"char_{_agl_name(codepoint, glyph_name)}_{codepoint:04X}"


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
        f"  <title>{escape(title)}</title>\n"
        f'  <g transform="{transform}">\n'
        f'    <path d="{path_data}" fill="#000000"/>\n'
        "  </g>\n"
        "</svg>\n"
    )


def _printable(codepoint: int) -> str:
    """表示可能な文字、または U+XXXX 表記を返す。"""
    ch = chr(codepoint)
    return ch if ch.isprintable() else f"U+{codepoint:04X}"


def extract_all(
    font_path: Path = FONT_PATH,
    out_dir: Path = OUT_DIR,
    viewbox: int = VIEWBOX,
    dry_run: bool = False,
    prune: bool = True,
    aliases_path: Path = ALIASES_PATH,
) -> list[Path]:
    """cmap を走査し、**グリフ単位で重複排除した** アウトライン化SVGを出力する。

    同一グリフ名へ再マップされた複数コードポイント（アクセント付きラテン等）は、
    最小コードポイント側を「正規グリフ」として 1 枚だけ書き出し、残りは
    エイリアスとして ``aliases_path`` に記録する。

    Args:
        font_path:   PenchantManufacture OTFファイルのパス
        out_dir:     出力ディレクトリ
        viewbox:     SVG viewBoxサイズ（px）
        dry_run:     True の場合はファイルを書き出さず対象のみ表示する
        prune:       True の場合、今回生成対象でない既存 char_*.svg を削除する
                     （旧・重複SVGの掃除）
        aliases_path: 異体字→正規グリフ対応表(JSON)の出力先

    Returns:
        生成した（または dry-run で生成予定の）正規SVGファイルのパスリスト
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
    # glyph_name -> 正規グリフ情報 { "stem", "codepoint", "char", "agl", "aliases": [...] }
    canonical: dict[str, dict] = {}
    seen_stems: set[str] = set()

    for codepoint in sorted(cmap.keys()):
        glyph_name = cmap[codepoint]
        agl_name = _agl_name(codepoint, glyph_name)

        if glyph_name in canonical:
            # 既出グリフへの再マップ = 異体字。エイリアスとして記録し、SVGは作らない。
            canonical[glyph_name]["aliases"].append(
                {"codepoint": f"U+{codepoint:04X}", "char": _printable(codepoint), "agl": agl_name}
            )
            continue

        title = f"{FONT_TITLE} {_printable(codepoint)}"
        svg = extract_glyph_svg(
            glyph_name, glyph_set, hmtx_metrics,
            ascender, upm, viewbox, title,
        )
        if svg is None:
            skipped_empty += 1
            continue

        stem = char_to_stem(codepoint, glyph_name)
        seen_stems.add(stem)
        canonical[glyph_name] = {
            "stem": stem,
            "glyph": glyph_name,
            "codepoint": f"U+{codepoint:04X}",
            "char": _printable(codepoint),
            "agl": agl_name,
            "aliases": [],
        }

        out_path = out_dir / f"{stem}.svg"
        produced.append(out_path)
        if dry_run:
            print(f"  DRY-RUN: {out_path.name}  (glyph={glyph_name!r}, U+{codepoint:04X})")
        else:
            out_path.write_text(svg, encoding="utf-8")
            print(f"  OK: {out_path.name}  (glyph={glyph_name!r})")

    # ── 旧・重複SVGの掃除 ──
    pruned: list[str] = []
    failed: list[str] = []
    if prune:
        for existing in sorted(out_dir.glob("char_*.svg")):
            if existing.stem not in seen_stems:
                if dry_run:
                    pruned.append(existing.name)
                    continue
                try:
                    existing.unlink()
                    pruned.append(existing.name)
                except OSError as exc:  # 一部環境（読み取り専用マウント等）で削除不可
                    failed.append(existing.name)
                    print(f"  WARN: 削除できませんでした {existing.name}: {exc}")
        if pruned:
            verb = "削除予定" if dry_run else "削除"
            print(f"\n  重複/旧SVGを{verb}: {len(pruned)}件  例: {', '.join(pruned[:6])}"
                  + (" ..." if len(pruned) > 6 else ""))
        if failed:
            print(f"  ※ {len(failed)}件は削除できませんでした（手動削除が必要）")

    # ── エイリアス対応表 JSON ──
    alias_total = sum(len(v["aliases"]) for v in canonical.values())
    aliases_doc = {
        "font": FONT_TITLE,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unique_glyphs": len(canonical),
        "cmap_mappings": len(cmap),
        "alias_count": alias_total,
        "note": (
            "異体字（アクセント付きラテン等）は基底グリフと同一アウトラインのため画像は "
            "統合し、ここに検索エイリアスとして記録する。絵文字ビルダーが参照する。"
        ),
        "glyphs": {
            info["stem"]: {
                "glyph": info["glyph"],
                "codepoint": info["codepoint"],
                "char": info["char"],
                "agl": info["agl"],
                "aliases": info["aliases"],
            }
            for info in sorted(canonical.values(), key=lambda d: d["stem"])
        },
    }
    if not dry_run:
        aliases_path.parent.mkdir(parents=True, exist_ok=True)
        aliases_path.write_text(
            json.dumps(aliases_doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  エイリアス表: {aliases_path}  （{alias_total}件の異体字を{len(canonical)}正規グリフへ）")

    print(f"\n正規グリフ {len(produced)} 字 / 異体字統合 {alias_total} 件 / 空グリフ {skipped_empty} 件スキップ")
    return produced


@click.command()
@click.option("--font", "font_path", default=str(FONT_PATH), show_default=True,
              help="PenchantManufacture OTFファイルのパス")
@click.option("--out-dir", default=str(OUT_DIR), show_default=True,
              help="SVG出力ディレクトリ")
@click.option("--viewbox", default=VIEWBOX, show_default=True,
              help="SVG viewBoxサイズ（px、正方形）")
@click.option("--no-prune", is_flag=True, help="今回生成対象でない既存SVGを削除しない")
@click.option("--dry-run", is_flag=True, help="ファイルを生成せず対象を表示")
def main(font_path: str, out_dir: str, viewbox: int, no_prune: bool, dry_run: bool) -> None:
    """PenchantManufacture フォントの cmap をグリフ単位で重複排除してSVG化します。"""
    fp = Path(font_path)
    od = Path(out_dir)

    print(f"フォント : {fp}")
    print(f"出力先   : {od}")
    print(f"viewBox  : {viewbox}x{viewbox}")
    print(f"モード   : {'DRY-RUN' if dry_run else '書き出し'} / prune={'OFF' if no_prune else 'ON'}")
    print()

    paths = extract_all(fp, od, viewbox, dry_run=dry_run, prune=not no_prune)

    verb = "生成予定" if dry_run else "生成"
    print(f"\n完了: {len(paths)} 正規グリフを{verb}しました")


if __name__ == "__main__":
    main()
