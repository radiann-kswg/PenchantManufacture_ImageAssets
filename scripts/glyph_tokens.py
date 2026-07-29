"""字体トークン／後置タグ 命名様式の単一の正（SSOT）。

``docs/EMOJI_TECHCODE_SPEC.md`` で確定した命名様式を実装する共通モジュール。
``build_misskey_zip.py`` および将来の ``text_to_emoji.py`` から参照する。

命名: ``{字体トークン}{後置タグ}``
- 字体トークン: 数字 ``n``＋値 / 英小文字 ``l``＋値 / 英大文字 ``u``＋値 /
  ギリシャ小文字は AGL / ギリシャ大文字は ``c``＋AGL / ASCII記号は2字略号 /
  上付きは ``sup``＋値 / 下付きは ``sub``＋値。
- 後置タグ: プロジェクト印 ``p`` ＋バリアント記号。
  既定 ``sumi``（墨・二画面）= ``p``。工業4種 = ``pr``/``ph``/``pt``/``pn``。

いずれも英小文字・数字のみ／2字以上で、Misskey（``^[a-z0-9_]+$``）と
Discord（2字以上）の双方の命名規則を同時に満たす。

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0
"""
from __future__ import annotations

# ── 後置タグ（プロジェクト印 p ＋バリアント記号） ──
# 既定 sumi(墨) は `p`。sumi 未実装の間、工業4種は pr/ph/pt/pn を用いる。
VARIANT_SUFFIX: dict[str, str] = {
    "sumi": "p",
    "rust": "pr",
    "hazard": "ph",
    "patina": "pt",
    "nickel": "pn",
}

VARIANT_JP: dict[str, str] = {
    "sumi": "墨",
    "rust": "酸鉄",
    "hazard": "警戒",
    "patina": "緑青真鍮",
    "nickel": "白銅燐光",
}

# ── バリアント非依存アセットの後置タグ ──
# スペーサ（完全透過の余白絵文字）のように 5 バリアントで見た目が変わらないアセットは
# 1 組のみ生成し、後置タグは **プロジェクト印 `p` のみ**（バリアント記号を持たない）。
# 既定 sumi の後置タグと同形になるが、既定字と混在させても `:upp::ump::spcp::n3p:` と
# 打鍵リズムが崩れない利点を優先する（SPEC §2.4 注記）。
NEUTRAL_SUFFIX = "p"

# ── ASCII 記号 → 2字略号（AGL名キー。SPEC §2.3 と一致） ──
SYMBOL_TOKENS: dict[str, str] = {
    "hyphen": "hy", "period": "dt", "colon": "co", "slash": "sl",
    "underscore": "sb", "plus": "pl", "equal": "eq", "asterisk": "as",
    "numbersign": "hs", "at": "at", "percent": "pc", "ampersand": "am",
    "parenleft": "ro", "parenright": "rc", "bracketleft": "bo", "bracketright": "bx",
    "braceleft": "wo", "braceright": "wx", "less": "sm", "greater": "bg",
    "exclam": "ex", "question": "qm", "comma": "cm", "semicolon": "sc",
    "quotesingle": "sq", "quotedbl": "dq", "backslash": "bk", "grave": "gv",
    "asciitilde": "td", "asciicircum": "ht", "bar": "vb", "dollar": "dl",
    # 曲がり引用符（フォント収録の拡張記号）
    "quoteleft": "ql", "quoteright": "qr",
    "quotedblleft": "dql", "quotedblright": "dqr",
}

# ── 上付き／下付き（SPEC §4.1 A1 / A2） ──
# v3.1.0 で作者が **実グリフとして作字** した（当初計画の「合成」ではない）。
# フォントのグリフ名は `zerosuperior` / `uni207b` / `twoinferior` のように命名規則が
# 揺れているため、トークン表は **文字そのものをキー** にしてグリフ名の揺れから独立させる。
SUPERSCRIPT_TOKENS: dict[str, str] = {
    "⁰": "sup0", "¹": "sup1", "²": "sup2", "³": "sup3", "⁴": "sup4",
    "⁵": "sup5", "⁶": "sup6", "⁷": "sup7", "⁸": "sup8", "⁹": "sup9",
    "⁺": "supplus", "⁻": "supminus", "⁼": "supeq",
    "⁽": "suplp", "⁾": "suprp",
    "ⁿ": "supn", "ⁱ": "supi",
}

SUBSCRIPT_TOKENS: dict[str, str] = {
    "₀": "sub0", "₁": "sub1", "₂": "sub2", "₃": "sub3", "₄": "sub4",
    "₅": "sub5", "₆": "sub6", "₇": "sub7", "₈": "sub8", "₉": "sub9",
    "₊": "subplus", "₋": "subminus", "₌": "subeq",
    "₍": "sublp", "₎": "subrp",
    "ₙ": "subn",
}

# ── グリフ名の可読化オーバーライド（コードポイント → 表示名） ──
# フォント側が `uni207b` のような機械名を持つグリフだけ、他の上付き／下付きと同じ
# `{値}{superior|inferior}` 様式に揃える。SVG/PNG のステム（``char_{名}_{CP}``）が
# 一貫し、フォント側でグリフ名が変わってもファイル名が動かない。
GLYPH_NAME_OVERRIDES: dict[int, str] = {
    0x2071: "isuperior",       # ⁱ  font: uni2071
    0x207B: "minussuperior",   # ⁻  font: uni207b
    0x208A: "plusinferior",    # ₊  font: uni208a
    0x208B: "minusinferior",   # ₋  font: uni208b
    0x208C: "equalinferior",   # ₌  font: uni208c
    0x2099: "ninferior",       # ₙ  font: uni2099
}

# ── ギリシャ AGL 名の集合（stem 実測に一致） ──
_GREEK_UPPER_AGL = {
    "Alpha", "Beta", "Gamma", "Delta", "Deltagreek", "Epsilon", "Zeta", "Eta",
    "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
    "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega", "Omegagreek",
}
_GREEK_LOWER_AGL = {
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota",
    "kappa", "lambda", "mu", "mugreek", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "sigma1", "sigmafinal", "tau", "upsilon", "phi", "chi", "psi", "omega",
}

# ギリシャ小文字 AGL → 正規トークン（特殊名の正規化）
_GREEK_LOWER_TOKEN_FIX = {"mugreek": "mu", "sigma1": "sigmaf", "sigmafinal": "sigmaf"}


def _greek_canon_lower(agl: str) -> str:
    """ギリシャ AGL 名を小文字の正規名へ（'greek' 接尾辞・特殊名を吸収）。"""
    base = agl.lower()
    if base.endswith("greek"):
        base = base[: -len("greek")]
    return _GREEK_LOWER_TOKEN_FIX.get(agl, base)


def glyph_token(char: str, agl: str) -> str:
    """1グリフの字体トークンを返す（後置タグは含まない）。

    Args:
        char: グリフの文字（例 'A' / '2' / '-' / 'α'）。空文字可（記号のみ AGL 判定）。
        agl:  グリフの AGL 名（例 'A' / 'two' / 'hyphen' / 'alpha' / 'Deltagreek'）。

    Returns:
        字体トークン（例 'ua' / 'n2' / 'hy' / 'alpha' / 'cdelta' / 'sup2' / 'subn'）。
    """
    if len(char) == 1 and char.isascii():
        if char.isdigit():
            return f"n{char}"
        if "a" <= char <= "z":
            return f"l{char}"
        if "A" <= char <= "Z":
            return f"u{char.lower()}"
    # 上付き／下付きは非ASCII。'²'.isdigit() は True なので数字判定より後に置く必要は
    # ないが、ASCII 分岐で弾かれるため誤って n2 にはならない。
    if char in SUPERSCRIPT_TOKENS:
        return SUPERSCRIPT_TOKENS[char]
    if char in SUBSCRIPT_TOKENS:
        return SUBSCRIPT_TOKENS[char]
    if agl in SYMBOL_TOKENS:
        return SYMBOL_TOKENS[agl]
    if agl in _GREEK_UPPER_AGL:
        return "c" + _greek_canon_lower(agl)
    if agl in _GREEK_LOWER_AGL:
        return _greek_canon_lower(agl)
    # フォールバック: AGL を小文字化し [a-z0-9_] 以外を除去
    safe = "".join(ch for ch in agl.lower() if ch.isalnum() or ch == "_")
    return safe or "x"


def glyph_subcategory(char: str, agl: str) -> str:
    """グリフ種別のサブカテゴリ名を返す（Misskey のカテゴリ末尾に使う）。

    Args:
        char: グリフの文字（例 'A' / '²' / 'α'）。
        agl:  グリフの AGL 名（例 'A' / 'twosuperior' / 'alpha'）。

    Returns:
        '数字' / '英大文字' / '英小文字' / 'ギリシャ大文字' / 'ギリシャ小文字' /
        '上付き' / '下付き' / '記号ほか' のいずれか。
    """
    if len(char) == 1 and char.isascii():
        if char.isdigit():
            return "数字"
        if "A" <= char <= "Z":
            return "英大文字"
        if "a" <= char <= "z":
            return "英小文字"
    if char in SUPERSCRIPT_TOKENS:
        return "上付き"
    if char in SUBSCRIPT_TOKENS:
        return "下付き"
    if agl in _GREEK_UPPER_AGL:
        return "ギリシャ大文字"
    if agl in _GREEK_LOWER_AGL:
        return "ギリシャ小文字"
    return "記号ほか"


def glyph_extra_aliases(char: str, agl: str) -> list[str]:
    """字種に応じた追加検索エイリアスを返す（SPEC §4.1 / §2.6）。

    上付き・下付きは字面が小さく、ピッカーのサムネイルでは数字・記号の判別が
    難しい。字種名（``superscript`` / ``上付き``）と読み下し（``sup_2``）を
    足しておくと、名前を覚えていなくても絞り込める。

    Args:
        char: グリフの文字。
        agl:  グリフの AGL 名。

    Returns:
        追加エイリアスのリスト（該当しない字種では空）。
    """
    token = SUPERSCRIPT_TOKENS.get(char)
    if token:
        return ["superscript", "上付き", f"sup_{token[len('sup'):]}"]
    token = SUBSCRIPT_TOKENS.get(char)
    if token:
        return ["subscript", "下付き", f"sub_{token[len('sub'):]}"]
    return []


def emoji_name(char: str, agl: str, variant: str) -> str:
    """絵文字名 ``{トークン}{後置タグ}`` を返す。"""
    return glyph_token(char, agl) + VARIANT_SUFFIX[variant]
