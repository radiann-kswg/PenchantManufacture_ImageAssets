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

# ── キリル文字（SPEC §4 C1 / v3.1-release で 66字すべて作字） ──
# トークンは `y`（Cyrillic）＋ `u`/`l`（大小）＋ BGN/PCGN 準拠の簡易翻字。
# ラテン・ギリシャと違い AGL 名（Acyrillic 等）は一貫しているが、上付き／下付きと
# 同じく **文字キー** に統一してグリフ名の揺れから独立させる。
_CYRILLIC_TRANSLIT: tuple[tuple[str, str, str], ...] = (
    # (大文字, 小文字, 翻字)
    ("А", "а", "a"), ("Б", "б", "b"), ("В", "в", "v"), ("Г", "г", "g"),
    ("Д", "д", "d"), ("Е", "е", "e"), ("Ё", "ё", "yo"), ("Ж", "ж", "zh"),
    ("З", "з", "z"), ("И", "и", "i"), ("Й", "й", "j"), ("К", "к", "k"),
    ("Л", "л", "l"), ("М", "м", "m"), ("Н", "н", "n"), ("О", "о", "o"),
    ("П", "п", "p"), ("Р", "р", "r"), ("С", "с", "s"), ("Т", "т", "t"),
    ("У", "у", "u"), ("Ф", "ф", "f"), ("Х", "х", "kh"), ("Ц", "ц", "ts"),
    ("Ч", "ч", "ch"), ("Ш", "ш", "sh"), ("Щ", "щ", "shch"), ("Ъ", "ъ", "hard"),
    ("Ы", "ы", "y"), ("Ь", "ь", "soft"), ("Э", "э", "eh"), ("Ю", "ю", "yu"),
    ("Я", "я", "ya"),
)

CYRILLIC_UPPER_TOKENS: dict[str, str] = {
    up: f"yu{tr}" for up, _lo, tr in _CYRILLIC_TRANSLIT
}
CYRILLIC_LOWER_TOKENS: dict[str, str] = {
    lo: f"yl{tr}" for _up, lo, tr in _CYRILLIC_TRANSLIT
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
    0x1E9E: "Germandbls",      # ẞ  font: uni1e9e（AGL 名なし。ß=germandbls と対にする）
}

# ── ラテン拡張（アクセント付き・合字）→ 字体トークン ──
# [SPEC §2.3] の `u`/`l` マーカー方式を分音記号付き字へ拡張する。
#
#     {u|l}{基底ラテン字}{記号2字コード}   → 固定 4 字（例 Ä=uadi / ä=ladi）
#
# **AGL 名フォールバックは使えない**。フォールバックは AGL を小文字化するため
# `Adieresis`(Ä) と `adieresis`(ä) が同一トークンへ潰れ、絵文字名が衝突する
# （v3.2-beta 追加分で 35 組が該当した）。マーカーで大小を分けて回避する。
ACCENT_CODES: dict[str, str] = {
    "grave": "gr", "acute": "ac", "circumflex": "cf", "dieresis": "di",
    "tilde": "tl", "macron": "mc", "ring": "rg", "cedilla": "cd",
    "slash": "sk",   # `sl`（solidus/slash 記号）と衝突するため sk
}

# (大文字, 小文字, 基底ラテン字, 記号名)
_LATIN_EXT_SPEC: tuple[tuple[str, str, str, str], ...] = (
    ("À", "à", "a", "grave"),      ("Á", "á", "a", "acute"),
    ("Â", "â", "a", "circumflex"), ("Ã", "ã", "a", "tilde"),
    ("Ä", "ä", "a", "dieresis"),   ("Å", "å", "a", "ring"),
    ("Ā", "ā", "a", "macron"),
    ("Ç", "ç", "c", "cedilla"),
    ("È", "è", "e", "grave"),      ("É", "é", "e", "acute"),
    ("Ê", "ê", "e", "circumflex"), ("Ë", "ë", "e", "dieresis"),
    ("Ē", "ē", "e", "macron"),
    ("Ì", "ì", "i", "grave"),      ("Í", "í", "i", "acute"),
    ("Î", "î", "i", "circumflex"), ("Ï", "ï", "i", "dieresis"),
    ("Ī", "ī", "i", "macron"),
    ("Ñ", "ñ", "n", "tilde"),
    ("Ò", "ò", "o", "grave"),      ("Ó", "ó", "o", "acute"),
    ("Ô", "ô", "o", "circumflex"), ("Õ", "õ", "o", "tilde"),
    ("Ö", "ö", "o", "dieresis"),   ("Ø", "ø", "o", "slash"),
    ("Ō", "ō", "o", "macron"),
    ("Ù", "ù", "u", "grave"),      ("Ú", "ú", "u", "acute"),
    ("Û", "û", "u", "circumflex"), ("Ü", "ü", "u", "dieresis"),
    ("Ū", "ū", "u", "macron"),
    ("Ý", "ý", "y", "acute"),      ("Ÿ", "ÿ", "y", "dieresis"),
)

LATIN_EXT_TOKENS: dict[str, str] = {}
LATIN_EXT_ACCENT: dict[str, str] = {}   # 字 → 記号名（エイリアス用）
for _up, _lo, _base, _mark in _LATIN_EXT_SPEC:
    _code = ACCENT_CODES[_mark]
    LATIN_EXT_TOKENS[_up] = f"u{_base}{_code}"
    LATIN_EXT_TOKENS[_lo] = f"l{_base}{_code}"
    LATIN_EXT_ACCENT[_up] = _mark
    LATIN_EXT_ACCENT[_lo] = _mark

# 合字・特殊字（分音記号ではないラテン拡張）。同じく大小をマーカーで分ける。
# `ß` は v3.0 以来 AGL 名フォールバックで `germandbls` だったが、大文字 `ẞ` の追加に
# 伴い `lss`/`uss` の対へ揃える。v3.2-beta で `ß` の字形自体が変わり再登録が必要な
# ため、改名の追加コストは発生しない（旧名は検索エイリアスに残す）。
LATIN_LIGATURE_TOKENS: dict[str, str] = {
    "Œ": "uoe", "œ": "loe",
    "Æ": "uae", "æ": "lae",
    "ẞ": "uss", "ß": "lss",
    "ı": "lidl",   # dotless i
}

# 算術記号（[GLYPH_EXTENSION_PLAN] B1）。AGL 名キー。
MATH_SYMBOL_TOKENS: dict[str, str] = {
    "multiply": "times",
    "divide": "div",
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
    if char in CYRILLIC_UPPER_TOKENS:
        return CYRILLIC_UPPER_TOKENS[char]
    if char in CYRILLIC_LOWER_TOKENS:
        return CYRILLIC_LOWER_TOKENS[char]
    # ラテン拡張は AGL 判定より先に置く。AGL フォールバックでは大小が潰れる。
    if char in LATIN_EXT_TOKENS:
        return LATIN_EXT_TOKENS[char]
    if char in LATIN_LIGATURE_TOKENS:
        return LATIN_LIGATURE_TOKENS[char]
    if agl in MATH_SYMBOL_TOKENS:
        return MATH_SYMBOL_TOKENS[agl]
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
    if char in CYRILLIC_UPPER_TOKENS:
        return "キリル大文字"
    if char in CYRILLIC_LOWER_TOKENS:
        return "キリル小文字"
    if char in LATIN_EXT_TOKENS or char in LATIN_LIGATURE_TOKENS:
        return ("ラテン拡張大文字"
                if glyph_token(char, agl).startswith("u") else "ラテン拡張小文字")
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
    # キリルは翻字（yuzh の zh）を単独でも引けるようにする。型番検索で有効。
    token = CYRILLIC_UPPER_TOKENS.get(char)
    if token:
        return ["cyrillic", "キリル", token[len("yu"):]]
    token = CYRILLIC_LOWER_TOKENS.get(char)
    if token:
        return ["cyrillic", "キリル", token[len("yl"):]]
    # ラテン拡張は「基底字＋記号名」で引けるようにする。café の é を `acute` や
    # `e_acute` で探せるほうが、AGL 名 `eacute` を覚えているより実用的。
    mark = LATIN_EXT_ACCENT.get(char)
    if mark:
        base = LATIN_EXT_TOKENS[char][1]
        return ["latin", "ラテン拡張", mark, f"{base}_{mark}"]
    if char in LATIN_LIGATURE_TOKENS:
        extra = ["latin", "ラテン拡張"]
        if char in ("Œ", "œ", "Æ", "æ"):
            extra += ["ligature", "合字"]
        if char in ("ẞ", "ß"):
            extra += ["germandbls", "eszett", "sharps"]   # 旧名 germandbls を温存
        if char == "ı":
            extra += ["dotlessi", "dotless"]
        return extra
    return []


def emoji_name(char: str, agl: str, variant: str) -> str:
    """絵文字名 ``{トークン}{後置タグ}`` を返す。"""
    return glyph_token(char, agl) + VARIANT_SUFFIX[variant]
