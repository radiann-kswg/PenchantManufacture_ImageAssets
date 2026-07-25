"""Misskey一括インポート用zipファイルを生成するスクリプト。

姉妹プロジェクト Secvier の ``build_misskey_zip.py`` に倣い、工業デカール5スキームの
**幅可変版** PNG（``dist/glyphs_decal/{variant}/*_128.png``）から Misskey 互換の
meta.json 付き zip アーカイブを作成する。Misskey は非正方形の絵文字をそのまま
表示できるため、幅可変版（字面本来の比率）を採用する。

重複排除で統合したアクセント付き等の異体字は、``docs/glyph_aliases.json`` を参照して
**基底グリフ絵文字の検索エイリアス**として付与する（é で検索すると e のデカールが出る）。
これにより「同一画像を別名で二重登録しない」まま、異体字からの検索性を確保する。

Discord 向けには正方形版（``dist/glyphs_decal_square/{variant}/``）の PNG を
個別アップロードする運用のため、本スクリプトの一括zipは Misskey 専用。

出力: _exported-dist/penchant-misskey-{timestamp}.zip

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0

使い方:
    python scripts/build_misskey_zip.py
    python scripts/build_misskey_zip.py --variant rust   # 単一スキームのみ
    python scripts/build_misskey_zip.py --size 128       # 取り込むPNGサイズ（既定128）
"""
from __future__ import annotations

import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import click

from glyph_tokens import glyph_token, VARIANT_JP, VARIANT_SUFFIX

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist" / "glyphs_decal"          # 幅可変版（Misskey向け）
ALIASES_PATH = ROOT / "docs" / "glyph_aliases.json"        # 異体字（cmap再マップ）統合表
MERGES_PATH = ROOT / "docs" / "glyph_render_merges.json"   # 描画一致グリフ統合表
OUTPUT_DIR = ROOT / "_exported-dist"

HOST = "radiann6631.net"

# ── ライセンス（フォントグリフのみ・外部素材なし） ──
_LICENSE = (
    "https://github.com/radiann-kswg/PenchantManufacture_ImageAssets/\n"
    "PenchantManufacture emoji assets by RadianN_kswg / ラジアン（柏木主税）\n"
    "CC BY 4.0 https://creativecommons.org/licenses/by/4.0/"
)

# スキーム → 和名ラベルは glyph_tokens.VARIANT_JP（命名様式のSSOT）を参照する。
# 既定は sumi（墨・二画面）＝後置タグ p。工業4種は pr / ph / pt / pn。

# ギリシャ大文字/小文字 AGL 名（カテゴリ分類・エイリアス用）
_GREEK_UPPER = {
    "Alpha", "Beta", "Gamma", "Delta", "Deltagreek", "Epsilon", "Zeta", "Eta",
    "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
    "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega", "Omegagreek",
}
_GREEK_LOWER = {
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota",
    "kappa", "lambda", "mu", "mugreek", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "sigma1", "sigmafinal", "tau", "upsilon", "phi", "chi", "psi", "omega",
}


def _load_aliases() -> dict[str, dict]:
    """docs/glyph_aliases.json の glyphs 辞書（stem -> 情報）を返す。"""
    if not ALIASES_PATH.exists():
        print(f"WARN: {ALIASES_PATH} がありません。extract_glyphs.py を先に実行してください。")
        return {}
    return json.loads(ALIASES_PATH.read_text(encoding="utf-8")).get("glyphs", {})


def _load_render_merges() -> dict[str, list[dict]]:
    """docs/glyph_render_merges.json を読み、{正規stem: [統合グリフ情報, ...]} を返す。

    描画完全一致で統合された非正規グリフ（例: A に統合された Α(Alpha)）を、
    正規絵文字の検索エイリアスとして展開するために用いる。
    """
    if not MERGES_PATH.exists():
        return {}
    doc = json.loads(MERGES_PATH.read_text(encoding="utf-8")).get("merges", {})
    return {canon: entry.get("merged", []) for canon, entry in doc.items()}


def _parse_stem(stem: str) -> tuple[str, str, str]:
    """char_{agl}_{CP} を (agl, cp_hex, char) に分解する。"""
    # 末尾の 16進コードポイントを切り出す（agl 名にアンダースコアは無い前提）
    body = stem[len("char_"):]
    agl, cp = body.rsplit("_", 1)
    try:
        char = chr(int(cp, 16))
    except ValueError:
        char = ""
    return agl, cp, char


def _subcategory(agl: str, char: str) -> str:
    """グリフ種別のサブカテゴリ名を返す。"""
    if len(char) == 1 and char.isascii():
        if char.isdigit():
            return "数字"
        if "A" <= char <= "Z":
            return "英大文字"
        if "a" <= char <= "z":
            return "英小文字"
    if agl in _GREEK_UPPER:
        return "ギリシャ大文字"
    if agl in _GREEK_LOWER:
        return "ギリシャ小文字"
    return "記号ほか"


def _dedupe(seq: list[str]) -> list[str]:
    """順序を保って重複と空文字を除去する。"""
    out: list[str] = []
    seen: set[str] = set()
    for s in seq:
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _make_entry(file_name: str, name: str, category: str, aliases: list[str]) -> dict:
    """meta.json 用の絵文字エントリを生成する。"""
    return {
        "fileName": file_name,
        "downloaded": True,
        "emoji": {
            "id": uuid.uuid4().hex[:16],
            "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "name": name,
            "host": None,
            "category": category,
            "originalUrl": "",
            "publicUrl": "",
            "uri": None,
            "type": "image/png",
            "aliases": aliases,
            "license": _LICENSE,
            "localOnly": False,
            "isSensitive": False,
            "roleIdsThatCanBeUsedThisEmojiAsReaction": [],
        },
    }


def collect(variant: str | None, size: int) -> list[tuple[Path, str, dict]]:
    """dist/glyphs_decal/{variant}/*_{size}.png のエントリを収集する。

    重複排除で統合された 2 系統の異体字を検索エイリアスとして展開する:
      - cmap 再マップ異体字（アクセント付き等）… glyph_aliases.json
      - 描画完全一致グリフ（ギリシャ同形など）… glyph_render_merges.json
    統合された非正規グリフの PNG は生成されないため、エントリ自体は正規グリフのみ。
    """
    aliases_map = _load_aliases()
    render_merges = _load_render_merges()
    variants = [variant] if variant else list(VARIANT_JP.keys())
    entries: list[tuple[Path, str, dict]] = []

    for var in variants:
        var_dir = DIST / var
        if not var_dir.exists():
            print(f"  skip: {var_dir} がありません")
            continue
        vjp = VARIANT_JP.get(var, var)

        for png in sorted(var_dir.glob(f"char_*_{size}.png")):
            stem = png.stem[: -(len(str(size)) + 1)]  # char_A_0041_128 -> char_A_0041
            agl, _cp, char = _parse_stem(stem)
            token = glyph_token(char, agl)          # 字体トークン（例 ua / n2 / hy / cdelta）
            suffix = VARIANT_SUFFIX[var]            # 後置タグ（pr / ph / pt / pn、既定sumiはp）

            emoji_name = f"{token}{suffix}"         # 確定様式: {字体トークン}{後置タグ}
            zip_name = f"{emoji_name}.png"
            category = f"PenchantManufacture/工業デカール_{vjp}/{_subcategory(agl, char)}"

            # 名前は打鍵用に最短、エイリアスは検索・可読用に多めに（SPEC §2.6）
            aliases = [token, agl, agl.lower(), var, vjp]
            if char and char.isprintable() and len(char) == 1:
                aliases.append(char)               # リテラル字（Misskeyは大文字/非ASCIIも別名可）
            # 統合した異体字（アクセント付き等）を検索エイリアスとして展開
            info = aliases_map.get(stem)
            if info:
                for al in info.get("aliases", []):
                    aliases.append(al.get("agl", ""))
                    aliases.append(al.get("agl", "").lower())
                    alc = al.get("char", "")
                    if alc and alc.isprintable() and len(alc) == 1:
                        aliases.append(alc)
            # 描画一致で統合したグリフ（ギリシャ同形など）もエイリアス化
            for mg in render_merges.get(stem, []):
                m_agl = mg.get("agl", "")
                mc = mg.get("char", "")
                aliases.append(m_agl)
                aliases.append(m_agl.lower())
                if m_agl:
                    aliases.append(glyph_token(mc, m_agl))  # 統合グリフの字体トークンも別名に
                if mc and mc.isprintable() and len(mc) == 1:
                    aliases.append(mc)

            entries.append(
                (png, zip_name, _make_entry(zip_name, emoji_name, category, _dedupe(aliases)))
            )

    return entries


def build_zip(variant: str | None = None, size: int = 128) -> Path | None:
    """工業デカールPNGから Misskey 一括インポート用 zip を生成する。

    Args:
        variant: スキームキー（未指定なら全5種）。
        size:    収録するPNGサイズ（高さpx）。

    Returns:
        生成した zip のパス。収録対象が無ければ None。
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    entries = collect(variant, size)
    if not entries:
        print("収録対象がありません。generate_decal.py を先に実行してください。")
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    zip_path = OUTPUT_DIR / f"penchant-misskey-{timestamp}.zip"
    now_jst = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT+0900 (JST)")
    meta = {
        "metaVersion": 2,
        "host": HOST,
        "exportedAt": now_jst,
        "emojis": [entry for _, _, entry in entries],
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for src_path, zip_name, _ in entries:
            zf.write(src_path, zip_name)
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"Created: {zip_path.name}")
    print(f"Total: {len(entries)} emojis")
    by_cat: dict[str, int] = {}
    for _, _, e in entries:
        cat = e["emoji"]["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1
    for cat in sorted(by_cat):
        print(f"  {cat}: {by_cat[cat]}")
    return zip_path


@click.command()
@click.option("--variant", "-v", type=click.Choice(list(VARIANT_JP.keys())),
              default=None, help="単一スキームのみ収録（未指定なら全5種）")
@click.option("--size", type=int, default=128, show_default=True,
              help="収録するPNGサイズ（高さpx）")
def main(variant: str | None, size: int) -> None:
    """工業デカールPNGから Misskey 一括インポート用 zip を生成します。"""
    build_zip(variant=variant, size=size)


if __name__ == "__main__":
    main()
