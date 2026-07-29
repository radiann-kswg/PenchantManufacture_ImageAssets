"""バリアント非依存スペーサ絵文字（完全透過PNG）生成スクリプト。

工業デカール（``generate_decal.py``）が「高さ固定・幅可変」で出力するのに合わせ、
**既存グリフのデカールPNGと同一寸法の完全透過PNG** を生成する。新規作字は不要で、
寸法は参照グリフの出力PNGを実測して決めるため、フォント更新でデカールを作り直せば
スペーサ幅も自動で追従する（本ステップは decal ステップの後に実行する）。

2トークン（いずれもバリアント差分なし＝全スキーム共通の1組のみ生成）:

    spc … 全角スペース  参照 ``m``(U+006D) … 全グリフ中の最大幅（em 幅）
    gap … 半角スペース  参照 ``I``(U+0049) … ``m`` の約 48.6%（≒半角）

Misskey は非正方形の絵文字をそのまま表示するため、幅の差がそのまま余白量の差になる。
一方 Discord は絵文字を正方形スロットで表示し、正方形パディング後は ``spc`` と ``gap``
が完全透過の同一画像に潰れて区別できない。よって **本スペーサは Misskey 専用** とし、
正方形版（``dist/glyphs_decal_square`` 相当）は生成しない。

パイプライン:
    dist/glyphs_decal/{variant}/char_m_006D_{size}.png （decal ステップ出力）
        │  参照グリフPNGの寸法を実測（幅はスキームに依らず同一）
        ▼
    dist/glyphs_spacer/spacer_{token}_{size}.png  （完全透過・幅可変）
    docs/glyph_spacers.json                       （絵文字名・寸法・参照グリフの対応表）

依存は Pillow のみ（cairosvg / numpy / scipy を必要としない）。

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0

使い方:
    python scripts/generate_spacers.py
    python scripts/generate_spacers.py --dry-run   # 実測結果の表示のみ
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import click
from PIL import Image

from glyph_tokens import NEUTRAL_SUFFIX

ROOT = Path(__file__).resolve().parent.parent
DECAL = ROOT / "dist" / "glyphs_decal"          # 幅可変版デカール（寸法の実測元）
DIST = ROOT / "dist" / "glyphs_spacer"
MANIFEST_PATH = ROOT / "docs" / "glyph_spacers.json"

# 寸法はスキームに依らず同一なので既定バリアントを実測元にする（無ければ他を使う）。
REF_VARIANT = "sumi"
# グリフSVG/PNG（char_*）の glob と衝突しないよう別接頭辞を使う。
STEM_PREFIX = "spacer_"


class Spacer(NamedTuple):
    """スペーサ 1 種の定義。"""

    token: str                  # 字体トークン（後置タグを除く）
    ref_stem: str               # 寸法の基準にする既存グリフのステム
    label: str                  # 和名ラベル
    aliases: tuple[str, ...]    # Misskey 検索エイリアス（token は自動付与）


SPACERS: tuple[Spacer, ...] = (
    Spacer("spc", "char_m_006D", "全角スペース",
           ("space", "emsp", "zenkaku", "全角", "スペース", "spacer")),
    Spacer("gap", "char_I_0049", "半角スペース",
           ("ensp", "halfspace", "hankaku", "半角", "スペース", "spacer")),
)


def _ref_char(stem: str) -> str:
    """``char_{AGL}_{CP}`` 形式のステムから参照文字を復元する。"""
    try:
        return chr(int(stem.rsplit("_", 1)[1], 16))
    except (IndexError, ValueError):
        return ""


def reference_dir() -> Path:
    """参照デカールPNGのディレクトリを返す。

    幅は各グリフのクロップ矩形だけで決まりスキームに依存しないため、既定バリアント
    （``sumi``）を使う。未生成なら生成済みの他バリアントへフォールバックする。

    Raises:
        FileNotFoundError: デカールPNGが 1 つも見つからない場合
    """
    preferred = DECAL / REF_VARIANT
    if preferred.exists() and any(preferred.glob("char_*.png")):
        return preferred
    for alt in sorted(p for p in DECAL.glob("*") if p.is_dir()):
        if any(alt.glob("char_*.png")):
            return alt
    raise FileNotFoundError(
        f"{DECAL} にデカールPNGがありません。先に generate_decal.py を実行してください。"
    )


def measure(ref_dir: Path) -> dict[str, dict[int, tuple[int, int]]]:
    """参照グリフのデカールPNGを実測し、各スペーサの出力寸法を決める。

    出力サイズの一覧も実測から得るため、``generate_decal.SIZES`` を変更しても
    定数を二重管理せずに追従する。

    Args:
        ref_dir: 参照バリアントのデカールPNGディレクトリ

    Returns:
        {token: {size: (幅, 高さ)}} の辞書

    Raises:
        FileNotFoundError: 参照グリフのPNGが見つからない場合
    """
    dims: dict[str, dict[int, tuple[int, int]]] = {}
    for sp in SPACERS:
        found: dict[int, tuple[int, int]] = {}
        for png in sorted(ref_dir.glob(f"{sp.ref_stem}_*.png")):
            try:
                size = int(png.stem.rsplit("_", 1)[1])
            except (IndexError, ValueError):
                continue
            with Image.open(png) as im:
                found[size] = im.size
        if not found:
            raise FileNotFoundError(
                f"参照グリフ {sp.ref_stem} のデカールPNGが {ref_dir} にありません。"
                " generate_decal.py を先に実行してください。"
            )
        dims[sp.token] = found
    return dims


def _write_manifest(dims: dict[str, dict[int, tuple[int, int]]], ref_dir: Path) -> None:
    """絵文字名・寸法・参照グリフの対応表を ``docs/glyph_spacers.json`` へ書き出す。

    ``build_misskey_zip.py`` はこの表を読んでスペーサをzipへ収録する。
    """
    doc = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("バリアント非依存の完全透過スペーサ。後置タグはプロジェクト印 p のみで、"
                 "5バリアント共通の1組を Misskey 専用に登録する（Discord は正方形パディングで"
                 "全スペーサが同一画像に潰れるため対象外）。"),
        "suffix": NEUTRAL_SUFFIX,
        "reference_variant": ref_dir.name,
        "spacers": [
            {
                "name": f"{sp.token}{NEUTRAL_SUFFIX}",
                "token": sp.token,
                "label": sp.label,
                "reference": {"stem": sp.ref_stem, "char": _ref_char(sp.ref_stem)},
                "aliases": list(sp.aliases),
                "sizes": {
                    str(size): {
                        "file": f"{STEM_PREFIX}{sp.token}_{size}.png",
                        "width": w,
                        "height": h,
                    }
                    for size, (w, h) in sorted(dims[sp.token].items(), reverse=True)
                },
            }
            for sp in SPACERS
        ],
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def build(dry_run: bool = False) -> int:
    """スペーサの透過PNGと対応表を生成する。

    Args:
        dry_run: True なら実測結果を表示するだけでファイルを生成しない。

    Returns:
        生成した PNG の件数（dry-run 時は生成予定件数）。
    """
    try:
        ref_dir = reference_dir()
        dims = measure(ref_dir)
    except FileNotFoundError as exc:
        print(f"WARN: {exc}")
        return 0

    print(f"  実測元: {ref_dir.relative_to(ROOT)}")
    count = 0
    for sp in SPACERS:
        sizes = sorted(dims[sp.token].items(), reverse=True)
        ref = _ref_char(sp.ref_stem) or sp.ref_stem
        shape = "  ".join(f"{w}x{h}" for _size, (w, h) in sizes)
        name = f"{sp.token}{NEUTRAL_SUFFIX}"
        print(f"  {name:<6} {sp.label}  基準 '{ref}'  → {shape}")
        if dry_run:
            count += len(sizes)
            continue
        DIST.mkdir(parents=True, exist_ok=True)
        for size, (w, h) in sizes:
            Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(
                DIST / f"{STEM_PREFIX}{sp.token}_{size}.png"
            )
            count += 1

    if not dry_run:
        _write_manifest(dims, ref_dir)
        print(f"  対応表: {MANIFEST_PATH.relative_to(ROOT)}")
    return count


@click.command()
@click.option("--dry-run", is_flag=True, help="実測結果のみ表示（ファイル生成なし）")
def main(dry_run: bool) -> None:
    """バリアント非依存のスペーサ絵文字（完全透過PNG）を生成します。"""
    print(f"出力    : {DIST}   … Misskey 向け（幅可変・バリアント共通）")
    print()
    n = build(dry_run=dry_run)
    if dry_run:
        print(f"\n（dry-runモード：{n} 件を生成予定）")
    else:
        print(f"\n完了: {n} 件の透過PNGを生成しました")


if __name__ == "__main__":
    main()
