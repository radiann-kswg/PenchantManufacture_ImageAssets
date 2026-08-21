"""PenchantManufacture ImageAssets 一括ビルドスクリプト。

初期設定（グリフパイプライン）の一括実行を担う。フォント検査 → グリフSVG抽出 →
PNG変換（dist/ と svg2png/）を順に行う。

ステップ: inspect → extract（重複排除）→ png → svg2png → decal（幅可変＋正方形）
→ roman（合成ローマ数字 13〜39。カーニング適用の専用ビルド）
→ spacer（バリアント非依存の透過スペーサ）→ misskey_zip（一括インポートzip）

フォントを読むのは inspect / extract / roman の3ステップだけなので、``--font`` を渡せば
``assets/fonts/`` を差し替えずに別バージョン（例: ``_original-fonts/.develop/`` の
開発版）でビルドできる。制作途中グリフは ``extract_glyphs.PENDING_RANGES`` により
既定で除外される（``--include-pending`` で解除）。

使い方:
  python scripts/build.py                 # 全ステップ実行
  python scripts/build.py --dry-run       # 実行内容の確認のみ（生成なし）
  python scripts/build.py --step extract  # 特定ステップのみ
                                          # inspect/extract/png/svg2png/decal/spacer/misskey_zip
  python scripts/build.py --font "_original-fonts/.develop/penchant-manufacture_v3.1.0-develop/PenchantManufacture.otf"
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

# scriptsディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from build_misskey_zip import build_zip as build_misskey_zip
from export_png import export_category, svg2png_category
from extract_glyphs import FONT_PATH as DEFAULT_FONT
from extract_glyphs import extract_all
from generate_decal import SCHEMES as DECAL_SCHEMES
from generate_decal import build as build_decal
from generate_roman import build as build_roman
from generate_spacers import build as build_spacers
from inspect_font import inspect_font

STEPS = ["inspect", "extract", "png", "svg2png", "decal", "roman", "spacer", "misskey_zip"]


def run_step(step: str, dry_run: bool, font_path: Path = DEFAULT_FONT,
             include_pending: bool = False) -> None:
    """指定ステップを実行する。

    Args:
        step:            実行するステップ名（``STEPS`` のいずれか）。
        dry_run:         True なら生成せず内容表示のみ。
        font_path:       参照する OTF（inspect / extract のみ使用）。
        include_pending: True なら制作途中グリフも抽出する（extract のみ使用）。
    """
    print(f"\n=== [{step}] ===")
    if step == "inspect":
        if dry_run:
            print("  DRY-RUN: docs/glyph_map.txt を生成予定")
        else:
            inspect_font(font_path)
    elif step == "extract":
        extract_all(font_path, dry_run=dry_run, include_pending=include_pending)
    elif step == "png":
        if dry_run:
            print("  DRY-RUN: dist/glyphs/*_72.png / *_512.png を生成予定")
        else:
            export_category("glyphs")
    elif step == "svg2png":
        if dry_run:
            print("  DRY-RUN: svg2png/glyphs/*.png を生成予定")
        else:
            svg2png_category("glyphs")
    elif step == "decal":
        if dry_run:
            keys = ", ".join(DECAL_SCHEMES)
            print(f"  DRY-RUN: dist/glyphs_decal/{{{keys}}}/ (幅可変・Misskey) と "
                  f"dist/glyphs_decal_square/{{{keys}}}/ (正方形・Discord) に *_512/*_128.png を生成予定")
        else:
            build_decal()
    elif step == "roman":
        # 合成ローマ数字（13〜39）はフォントのカーニングを読むため font_path を使う
        build_roman(font_path=font_path, dry_run=dry_run)
    elif step == "spacer":
        build_spacers(dry_run=dry_run)
    elif step == "misskey_zip":
        if dry_run:
            print("  DRY-RUN: _exported-dist/penchant-misskey-{timestamp}.zip を生成予定")
        else:
            build_misskey_zip()


@click.command()
@click.option(
    "--step", "-s",
    type=click.Choice(STEPS + ["all"]),
    default="all",
    show_default=True,
    help="実行するステップ",
)
@click.option("--font", "font_path", default=str(DEFAULT_FONT), show_default=False,
              help="参照する OTF（既定: assets/fonts/PenchantManufacture.otf）")
@click.option("--include-pending", is_flag=True,
              help="制作途中グリフ（キリル等）も抽出対象に含める")
@click.option("--dry-run", is_flag=True, help="実際には生成せず内容を表示")
def main(step: str, font_path: str, include_pending: bool, dry_run: bool) -> None:
    """PenchantManufacture グリフアセットをビルドします。"""
    fp = Path(font_path)
    if not fp.exists():
        raise click.BadParameter(f"フォントが見つかりません: {fp}", param_hint="--font")
    if fp != DEFAULT_FONT:
        print(f"フォント: {fp}  （assets/fonts/ ではなく明示指定）")

    targets = STEPS if step == "all" else [step]
    for st in targets:
        run_step(st, dry_run=dry_run, font_path=fp, include_pending=include_pending)

    if dry_run:
        print("\n（dry-runモード：ファイルは生成されていません）")
    else:
        print("\n✓ ビルド完了")


if __name__ == "__main__":
    main()
