"""Misskey 文字列コンバーター（AiScript）の対応表を再生成する。

``aiscript/penchant-string-converter.is`` の **データ部だけ** を、ビルド成果物と
命名様式の SSOT（``glyph_tokens.py`` / ``dist/glyphs_decal/`` / ``docs/*.json``）から
再生成する。UI・変換ロジックは書き換えないので、手で編集してよい。

再生成する範囲（`let <名前> = ... ` の1ブロックずつ、行単位で差し替え）:

- ``character_map``  : 1文字 → 字体トークン（後置タグ無し）
- ``neutral_tokens`` : バリアント非依存トークン（スペーサ。常に ``{token}p``）
- ``roman_ligatures``: ローマ数字の並び → 合成トークン（``rom13``〜``lrom39``）
- ``roman_max_length``: 上記キーの最大長
- ``variants``       : バリアント選択肢（``VARIANT_JP`` / ``VARIANT_SUFFIX``）

グリフを追加したら ``python scripts/build.py``（または ``--step aiscript``）を実行し、
生成された ``.is`` をコミットすること。

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent))

from build_misskey_zip import (  # noqa: E402
    _load_aliases,
    _load_render_merges,
    _merged_stems,
    _parse_stem,
)
from glyph_tokens import (  # noqa: E402
    VARIANT_JP,
    VARIANT_SUFFIX,
    glyph_token,
    roman_token,
)

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT / "aiscript" / "penchant-string-converter.is"
DECAL_DIST = ROOT / "dist" / "glyphs_decal"
SPACERS_PATH = ROOT / "docs" / "glyph_spacers.json"
ROMANS_PATH = ROOT / "docs" / "glyph_romans.json"

# 対応表の基準バリアント（どのバリアントでも収録字は同じ）
REFERENCE_VARIANT = "sumi"
SIZE = 128

# スペーサ token → 対応する文字（docs/glyph_spacers.json の name/token に対応）
SPACER_CHARS: dict[str, str] = {"gap": " ", "spc": "　"}

# 単独グリフとして収録済みのローマ数字（1〜12）。合成の分割単位でもある。
ROMAN_UNITS: tuple[str, ...] = (
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
)
ROMAN_CHARS = {"upper": "ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ", "lower": "ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ"}

# Misskey のカスタム絵文字名（後置タグ付与後も満たす必要がある）
_NAME_RE = re.compile(r"[a-z0-9_]+")


def _roman_ascii(value: int) -> str:
    """1〜39 を ASCII のローマ数字表記にする。"""
    out = ""
    for num, sym in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while value >= num:
            out += sym
            value -= num
    return out


def _segmentations(text: str) -> list[list[int]]:
    """ASCII ローマ数字を、単独収録字（1〜12）の並びへ分割する全パターン。"""
    if not text:
        return [[]]
    out: list[list[int]] = []
    for value, unit in enumerate(ROMAN_UNITS, 1):
        if text.startswith(unit):
            out.extend([value, *rest] for rest in _segmentations(text[len(unit):]))
    return out


def character_map() -> dict[str, str]:
    """1文字 → 字体トークン（後置タグ無し）の対応表を作る。

    収録の正は ``dist/glyphs_decal/{REFERENCE_VARIANT}/`` の実ファイル。描画一致で
    統合されたグリフ（``glyph_render_merges.json``）と cmap 再マップ異体字
    （``glyph_aliases.json``）は、統合先トークンへ向けたエイリアスとして展開する。
    """
    src_dir = DECAL_DIST / REFERENCE_VARIANT
    if not src_dir.exists():
        raise click.ClickException(
            f"{src_dir} がありません（先に generate_decal.py を実行してください）"
        )
    aliases_map = _load_aliases()
    render_merges = _load_render_merges()
    skip_stems = _merged_stems(render_merges)

    table: dict[str, str] = {}

    def put(char: str, token: str) -> None:
        # 1文字・印字可能のみ（合字などの複数コードポイントは対象外）
        if len(char) == 1 and char.isprintable():
            table.setdefault(char, token)

    for png in sorted(src_dir.glob(f"char_*_{SIZE}.png")):
        stem = png.stem[: -(len(str(SIZE)) + 1)]
        if stem in skip_stems:
            continue
        agl, _cp, char = _parse_stem(stem)
        token = glyph_token(char, agl)
        put(char, token)
        for al in aliases_map.get(stem, {}).get("aliases", []):
            put(al.get("char", ""), token)
        for mg in render_merges.get(stem, []):
            put(mg.get("char", ""), token)

    for sp in json.loads(SPACERS_PATH.read_text(encoding="utf-8")).get("spacers", []):
        char = SPACER_CHARS.get(sp["token"])
        if char:
            table[char] = sp["token"]

    # Misskey の絵文字名規則（^[a-z0-9_]+$）を満たさないトークンは登録できない
    bad = sorted({t for t in table.values() if not _NAME_RE.fullmatch(t)})
    if bad:
        raise click.ClickException(f"不正な字体トークン: {bad}（glyph_tokens.py を確認）")
    return table


def neutral_tokens() -> list[str]:
    """バリアント非依存トークン（登録名は常に ``{token}p``）。"""
    spacers = json.loads(SPACERS_PATH.read_text(encoding="utf-8")).get("spacers", [])
    return [sp["token"] for sp in spacers if sp["token"] in SPACER_CHARS]


def roman_ligatures() -> dict[str, str]:
    """ローマ数字の並び → 合成トークン（13〜39、大小）。

    ``ⅩⅢ`` だけでなく ``ⅩⅡⅠ`` ``ⅫⅠ`` のような等価な打ち方も同じ合成へ寄せる。
    生成対象の値は ``docs/glyph_romans.json``（generate_roman.py の出力）が正。
    """
    romans = json.loads(ROMANS_PATH.read_text(encoding="utf-8")).get("romans", [])
    table: dict[str, str] = {}
    for rm in romans:
        chars = ROMAN_CHARS[rm["case"]]
        token = roman_token(rm["value"], upper=rm["case"] == "upper")
        for seg in _segmentations(_roman_ascii(rm["value"])):
            if len(seg) >= 2:                      # 1字で足りるものは character_map 側
                table["".join(chars[v - 1] for v in seg)] = token
        # 正規表記（glyph_romans.json の chars）は必ず引けること
        if table.get(rm["chars"]) != token:
            raise click.ClickException(
                f"合成ローマ数字 {rm['chars']}({token}) の分割に失敗しました"
            )
    return table


def _escape(text: str) -> str:
    """AiScript の二重引用符文字列としてエスケープする。"""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _obj(entries: dict[str, str]) -> list[str]:
    items = list(entries.items())
    return [
        f'\t"{_escape(k)}": "{v}"' + ("," if i < len(items) - 1 else "")
        for i, (k, v) in enumerate(items)
    ]


def _render_blocks() -> dict[str, list[str]]:
    """`let <名前> = ...` に流し込む本文（開始行・終了行を含む）。"""
    chars = character_map()
    romans = roman_ligatures()
    variants = [
        f'\t{{text: "{VARIANT_JP[v]}", value: "{VARIANT_SUFFIX[v]}"}}'
        for v in VARIANT_JP
    ]
    return {
        "character_map": ["let character_map = {", *_obj(chars), "}"],
        "neutral_tokens": [
            "let neutral_tokens = ["
            + ", ".join(f'"{t}"' for t in neutral_tokens())
            + "]"
        ],
        "roman_ligatures": ["let roman_ligatures = {", *_obj(romans), "}"],
        "roman_max_length": [
            f"let roman_max_length = {max((len(k) for k in romans), default=1)}"
        ],
        "variants": ["let variants = [", *variants, "]"],
    }


def _replace_block(lines: list[str], name: str, body: list[str]) -> list[str]:
    """`let {name} = ` の1ブロック（単一行 or 閉じ括弧まで）を body で置き換える。"""
    head = f"let {name} = "
    start = next((i for i, ln in enumerate(lines) if ln.startswith(head)), None)
    if start is None:
        raise click.ClickException(f"{SCRIPT_PATH.name} に `{head}...` が見つかりません")
    opener = lines[start].rstrip()[-1]
    if opener in "{[":
        closer = "}" if opener == "{" else "]"
        end = next(i for i in range(start + 1, len(lines)) if lines[i] == closer)
    else:
        end = start
    return lines[:start] + body + lines[end + 1:]


def build(dry_run: bool = False) -> None:
    """`.is` のデータ部を再生成する（UI・変換ロジックには触れない）。"""
    original = SCRIPT_PATH.read_text(encoding="utf-8")
    lines = original.replace("\r\n", "\n").split("\n")
    blocks = _render_blocks()
    for name, body in blocks.items():
        lines = _replace_block(lines, name, body)
    updated = "\n".join(lines)

    counts = ", ".join(f"{n}={len(b) - 2 if len(b) > 2 else 1}" for n, b in blocks.items())
    if dry_run:
        state = "変更なし" if updated == original else "更新予定"
        print(f"  DRY-RUN: {SCRIPT_PATH.relative_to(ROOT)} を再生成（{state}） {counts}")
        return
    if updated == original:
        print(f"  {SCRIPT_PATH.relative_to(ROOT)}: 変更なし  {counts}")
        return
    SCRIPT_PATH.write_text(updated, encoding="utf-8")
    print(f"  ✓ {SCRIPT_PATH.relative_to(ROOT)} を再生成  {counts}")


@click.command()
@click.option("--dry-run", is_flag=True, help="実際には書き換えず内容を表示")
def main(dry_run: bool) -> None:
    """AiScript コンバーターの対応表を再生成します。"""
    build(dry_run=dry_run)


if __name__ == "__main__":
    main()
