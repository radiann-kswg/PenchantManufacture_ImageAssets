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

制作途中グリフの除外:
    フォントに収録済みでも**作者がまだ調整中**の字は、絵文字として公開すると
    差し替え時に登録済み絵文字を作り直す羽目になる。``PENDING_RANGES`` に挙げた
    コードポイント範囲は既定でスキップし、``--include-pending`` で明示的に含める。
    現在の対象はキリル文字（U+0400–U+04FF、v3.1.0-develop で大文字27字が着手済み・
    残り39字は未着手）。完成したら ``PENDING_RANGES`` から外すだけで通常ビルドに乗る。

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
    python scripts/extract_glyphs.py --font "_original-fonts/.develop/penchant-manufacture_v3.1.0-develop/PenchantManufacture.otf"
    python scripts/extract_glyphs.py --include-pending   # 制作途中グリフも抽出
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
from xml.sax.saxutils import escape

import click
from fontTools import agl, ttLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

from glyph_tokens import GLYPH_NAME_OVERRIDES

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "PenchantManufacture.otf"
OUT_DIR = Path(__file__).parent.parent / "src" / "glyphs"
ALIASES_PATH = Path(__file__).parent.parent / "docs" / "glyph_aliases.json"
VIEWBOX = 512

FONT_TITLE = "PenchantManufacture"

# ── 制作途中グリフ（既定で抽出対象外） ──
# (開始CP, 終了CP, 説明) の閉区間。作者が調整中で絵文字化を保留する字を挙げる。
# 完成したらこの表から外すだけで通常ビルドに乗る（他スクリプトの変更は不要）。
# キリル U+0400–U+04FF は v3.1-release で全66字が確定したため除外を解除した。
PENDING_RANGES: tuple[tuple[int, int, str], ...] = ()

_SAFE_RE = re.compile(r"[^A-Za-z0-9]+")


def is_pending(codepoint: int, ranges: tuple[tuple[int, int, str], ...] = PENDING_RANGES) -> str | None:
    """制作途中の範囲に含まれるなら、その説明文を返す（含まれなければ None）。"""
    for start, end, label in ranges:
        if start <= codepoint <= end:
            return label
    return None


def _agl_name(codepoint: int, glyph_name: str) -> str:
    """コードポイントの表示名（可読名 → AGL 名 → グリフ名 → uniXXXX）を返す。"""
    base = GLYPH_NAME_OVERRIDES.get(codepoint) or agl.UV2AGL.get(codepoint)
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


class VerticalFit(NamedTuple):
    """全グリフ共通の縦方向配置（スケールとベースライン位置）。

    Attributes:
        scale:  フォントユニット → px のスケール
        ty:     SVG 座標でのベースライン Y 位置（px）
        top:    字面上端に使ったフォント座標 Y（＝この値が SVG の y=0 に来る）
        bottom: 字面下端に使ったフォント座標 Y
    """

    scale: float
    ty: float
    top: float
    bottom: float


def metrics_fit(os2: object, upm: int, viewbox: int) -> VerticalFit:
    """フォント登録メトリクス（OS/2 win 帯）による固定の縦配置を返す。

    v3.2 以前はインク実測からベースラインを動的に算出していたが、v3.3-beta で
    作者が **usWinAscent / usWinDescent をインク帯に一致するよう登録**し、
    「登録されている上下位置のままビルドしてよい」契約になった。以後ビルド側では
    グリフの上下位置を動かさない（フォント更新で実測が変わっても配置が揺れない）。
    帯を逸脱するインクは抽出時に WARN で検出する（``extract_glyph_svg``）。

    Args:
        os2:     fontTools の OS/2 テーブル
        upm:     Units Per Em
        viewbox: 出力SVGのviewBoxサイズ（正方形）

    Returns:
        全グリフ共通の ``VerticalFit``（win 帯上端が SVG の y=0 に来る）。
    """
    top = float(os2.usWinAscent)
    bottom = -float(os2.usWinDescent)
    scale = viewbox / upm
    if top - bottom > upm:
        # 万一 win 帯が em を超えて登録されたら一律に縮めて収める（現行 991 < 1000）
        scale = viewbox / (top - bottom)
    return VerticalFit(scale=scale, ty=top * scale, top=top, bottom=bottom)


def extract_glyph_svg(
    glyph_name: str,
    glyph_set: object,
    hmtx_metrics: dict[str, tuple[int, int]],
    fit: VerticalFit,
    upm: int,
    viewbox: int,
    title: str,
) -> str | None:
    """1グリフのアウトライン化SVG文字列を生成する。

    Args:
        glyph_name: フォント内グリフ名（例: 'A', 'zero', 'Alpha'）
        glyph_set:  fontTools glyphSet オブジェクト
        hmtx_metrics: {グリフ名: (advanceWidth, lsb)} のマップ
        fit:        全グリフ共通の縦方向配置（``compute_vertical_fit``）
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

    # インク境界（win 帯逸脱の警告と、配置フレームの横方向 union に使う）
    bpen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(bpen)
    ink_x0, ink_y0, ink_x1, ink_y1 = bpen.bounds
    if ink_y1 > fit.top + 0.5 or ink_y0 < fit.bottom - 0.5:
        print(f"  WARN: {glyph_name} のインク y[{ink_y0:.1f}, {ink_y1:.1f}] が "
              f"win 帯 [{fit.bottom:.0f}, {fit.top:.0f}] を逸脱（クリップの恐れ。作者へ確認）")

    # フォント座標系（Y上方向）→ SVG座標系（Y下方向）の変換
    # 変換行列: matrix(sx, 0, 0, -sx, tx, ty)
    #   sx = fit.scale  （全グリフ共通のスケール）
    #   ty = fit.ty     （ベースライン位置。字面上端が y=0 に来るよう決めてある）
    #   tx = グリフを水平中央揃えするオフセット
    scale = fit.scale
    glyph_width_px = advance_width * scale
    tx = (viewbox - glyph_width_px) / 2
    ty = fit.ty

    transform = f"matrix({scale:.6f},0,0,{-scale:.6f},{tx:.3f},{ty:.3f})"

    # 配置フレーム（generate_decal.py がクロップに使う）:
    #   x = advance 幅 ∪ インク（SVG px）。正のサイドベアリングは保持し、
    #       負のサイドベアリング（√ の笠、j の尾など）のインクは切らない。
    #   y = win 帯（全グリフ共通。上端が y=0）。
    fx0 = min(0.0, ink_x0) * scale + tx
    fx1 = max(float(advance_width), ink_x1) * scale + tx
    fy1 = (fit.top - fit.bottom) * scale
    frame = f"  <!-- frame x={fx0:.3f},{fx1:.3f} y=0.000,{fy1:.3f} -->\n"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {viewbox} {viewbox}"\n'
        f'     width="{viewbox}" height="{viewbox}">\n'
        f"  <title>{escape(title)}</title>\n"
        f"{frame}"
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
    include_pending: bool = False,
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
        include_pending: True の場合、``PENDING_RANGES``（制作途中グリフ）も抽出する

    Returns:
        生成した（または dry-run で生成予定の）正規SVGファイルのパスリスト
    """
    tt = ttLib.TTFont(str(font_path))
    glyph_set = tt.getGlyphSet()
    cmap = tt.getBestCmap()
    hmtx_metrics: dict[str, tuple[int, int]] = tt["hmtx"].metrics
    upm: int = tt["head"].unitsPerEm

    # 縦配置はフォント登録メトリクス（OS/2 win 帯）を全グリフ共通で使う。
    # ビルド側でインク実測から配置をやり直さない（作字側の契約を信頼する）。
    fit = metrics_fit(tt["OS/2"], upm, viewbox)
    print(f"  縦配置: win 帯 [{fit.bottom:.0f}, {fit.top:.0f}]"
          f"（{fit.top - fit.bottom:.0f} units）をそのまま使用")

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    produced: list[Path] = []
    skipped_empty = 0
    # glyph_name -> 正規グリフ情報 { "stem", "codepoint", "char", "agl", "aliases": [...] }
    canonical: dict[str, dict] = {}
    seen_stems: set[str] = set()
    pending_skipped: dict[str, list[str]] = {}

    for codepoint in sorted(cmap.keys()):
        glyph_name = cmap[codepoint]
        agl_name = _agl_name(codepoint, glyph_name)

        if not include_pending:
            label = is_pending(codepoint)
            if label:
                # 制作途中。異体字エイリアスにも載せない（正規グリフが存在しないため）。
                pending_skipped.setdefault(label, []).append(_printable(codepoint))
                continue

        if glyph_name in canonical:
            # 既出グリフへの再マップ = 異体字。エイリアスとして記録し、SVGは作らない。
            canonical[glyph_name]["aliases"].append(
                {"codepoint": f"U+{codepoint:04X}", "char": _printable(codepoint), "agl": agl_name}
            )
            continue

        title = f"{FONT_TITLE} {_printable(codepoint)}"
        svg = extract_glyph_svg(
            glyph_name, glyph_set, hmtx_metrics,
            fit, upm, viewbox, title,
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

    if pending_skipped:
        print()
        for label, chars in pending_skipped.items():
            print(f"  制作途中のためスキップ: {label}  {len(chars)}字  "
                  f"{''.join(chars[:40])}{' ...' if len(chars) > 40 else ''}")
        print("  （--include-pending で抽出対象に含められます）")

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
        "pending_skipped": {
            label: {"count": len(chars), "chars": "".join(chars)}
            for label, chars in pending_skipped.items()
        },
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
@click.option("--include-pending", is_flag=True,
              help="制作途中グリフ（PENDING_RANGES）も抽出対象に含める")
@click.option("--dry-run", is_flag=True, help="ファイルを生成せず対象を表示")
def main(font_path: str, out_dir: str, viewbox: int, no_prune: bool,
         include_pending: bool, dry_run: bool) -> None:
    """PenchantManufacture フォントの cmap をグリフ単位で重複排除してSVG化します。"""
    fp = Path(font_path)
    od = Path(out_dir)
    pending = ", ".join(label for _s, _e, label in PENDING_RANGES) or "なし"

    print(f"フォント : {fp}")
    print(f"出力先   : {od}")
    print(f"viewBox  : {viewbox}x{viewbox}")
    print(f"モード   : {'DRY-RUN' if dry_run else '書き出し'} / prune={'OFF' if no_prune else 'ON'}")
    print(f"制作途中 : {pending} … {'含める' if include_pending else '除外'}")
    print()

    paths = extract_all(fp, od, viewbox, dry_run=dry_run, prune=not no_prune,
                        include_pending=include_pending)

    verb = "生成予定" if dry_run else "生成"
    print(f"\n完了: {len(paths)} 正規グリフを{verb}しました")


if __name__ == "__main__":
    main()
