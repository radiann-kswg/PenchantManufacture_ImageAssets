"""字体トークン／後置タグ 命名様式の単一の正（SSOT）。

``docs/EMOJI_TECHCODE_SPEC.md`` で確定した命名様式を実装する共通モジュール。
``build_misskey_zip.py`` および将来の ``text_to_emoji.py`` から参照する。

命名: ``{字体トークン}{後置タグ}``
- 字体トークン: 数字 ``n``＋値 / 英小文字 ``l``＋値 / 英大文字 ``u``＋値 /
  ギリシャ小文字は AGL / ギリシャ大文字は ``c``＋AGL / ASCII記号は2字略号。
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
        字体トークン（例 'ua' / 'n2' / 'hy' / 'alpha' / 'cdelta'）。
    """
    if len(char) == 1 and char.isascii():
        if char.isdigit():
            return f"n{char}"
        if "a" <= char <= "z":
            return f"l{char}"
        if "A" <= char <= "Z":
            return f"u{char.lower()}"
    if agl in SYMBOL_TOKENS:
        return SYMBOL_TOKENS[agl]
    if agl in _GREEK_UPPER_AGL:
        return "c" + _greek_canon_lower(agl)
    if agl in _GREEK_LOWER_AGL:
        return _greek_canon_lower(agl)
    # フォールバック: AGL を小文字化し [a-z0-9_] 以外を除去
    safe = "".join(ch for ch in agl.lower() if ch.isalnum() or ch == "_")
    return safe or "x"


def emoji_name(char: str, agl: str, variant: str) -> str:
    """絵文字名 ``{トークン}{後置タグ}`` を返す。"""
    return glyph_token(char, agl) + VARIANT_SUFFIX[variant]
