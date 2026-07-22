"""PenchantManufacture ImageAssets 一括ビルドスクリプト。

初期設定（グリフパイプライン）の一括実行を担う。フォント検査 → グリフSVG抽出 →
PNG変換（dist/ と svg2png/）を順に行う。

使い方:
  python scripts/build.py                 # 全ステップ実行（glyphs）
  python scripts/build.py --dry-run       # 実行内容の確認のみ（生成なし）
  python scripts/build.py --step extract  # 特定ステップのみ（inspect/extract/png/svg2png）
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

# scriptsディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from export_png import export_category, svg2png_category
from extract_glyphs import extract_all
from generate_decal import SCHEMES as DECAL_SCHEMES
from generate_decal import build as build_decal
from inspect_font import inspect_font

STEPS = ["inspect", "extract", "png", "svg2png", "decal"]


def run_step(step: str, dry_run: bool) -> None:
    """指定ステップを実行する。"""
    print(f"\n=== [{step}] ===")
    if step == "inspect":
        if dry_run:
            print("  DRY-RUN: docs/glyph_map.txt を生成予定")
        else:
            inspect_font()
    elif step == "extract":
        extract_all(dry_run=dry_run)
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
            print(f"  DRY-RUN: dist/glyphs_decal/{{{keys}}}/*_512.png / *_128.png を生成予定")
        else:
            build_decal()


@click.command()
@click.option(
    "--step", "-s",
    type=click.Choice(STEPS + ["all"]),
    default="all",
    show_default=True,
    help="実行するステップ",
)
@click.option("--dry-run", is_flag=True, help="実際には生成せず内容を表示")
def main(step: str, dry_run: bool) -> None:
    """PenchantManufacture グリフアセットをビルドします。"""
    targets = STEPS if step == "all" else [step]
    for st in targets:
        run_step(st, dry_run=dry_run)

    if dry_run:
        print("\n（dry-runモード：ファイルは生成されていません）")
    else:
        print("\n✓ ビルド完了")


if __name__ == "__main__":
    main()
