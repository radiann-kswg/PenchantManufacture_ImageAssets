# AGENTS.md — PenchantManufacture ImageAssets 共通エージェント指示書

このファイルは **Codex**、**Claude Code**、**GitHub Copilot** が共有する
PenchantManufacture リポジトリ固有指示の **唯一の正（SSOT）** です。
`CLAUDE.md` は `@AGENTS.md` の参照入口であり、詳細指示を重複記載しません。

姉妹プロジェクト **Secvier_ImageAssets** と同じ設計思想・命名規則・ビルドフローを踏襲します。

---

## プロジェクト概要

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、
**RadianN_kswg / ラジアン（柏木主税）による独自フォント PenchantManufacture** と
**Claude による Agent 機能** によって制作するカスタム画像アセット／グリフ素材リポジトリです。

現時点では **フォントグリフを起点とした画像アセット生成パイプラインの初期設定** を収録します。
フォント（`assets/fonts/PenchantManufacture.otf`）から各グリフをアウトライン化SVGとして抽出し、
透過PNGへ変換するまでの土台を提供します。

**著作権者**: RadianN_kswg / ラジアン（柏木主税） / **ライセンス**: CC BY 4.0

---

## 作字・フォントアセット制作のコンセプト

拡張計画（[docs/GLYPH_EXTENSION_PLAN.md]）の収録判断を貫く原則。新カテゴリの
提案・取捨選択・保留判断はすべてこの基準に照らして行うこと。

1. **工業デカールとしての実用性** — 型番・仕様・単位・図面注記・数式・論理式など、
   技術コミュニケーションをカスタム絵文字で「組版」するための文字体系。
   装飾ではなく短縮入力の実装であり、チャットで実際に打てる・検索できることが価値。
2. **文字（字形）であること** — 収録対象は文字であって図形ではない。
   線幅・縦帯（OS/2 win 帯契約）・サイドベアリングという**字形契約**の恩恵を
   受けるものを優先する。図形・ピクトグラム的な記号（チェック・幾何図形・
   安全標識・キーボード記号・電気記号 = Z 保留枠）は、汎用図版でも代替でき、
   作字の必要性・容易性がコストに釣り合わないため凍結する。
3. **文字体系ごとの完結性** — ラテン（アクセント込み）→ギリシャ→キリル→
   数式・単位→論理と、技術文書に現れる字種を**体系単位**で揃える。
   中途半端な虫食い収録より、1 体系を作り切ることを優先する。
4. **同形は作らない** — 字面が一致する字は別名運用（エイリアス）と描画一致統合で
   吸収し、絵文字点数を増やさない（µ⇔μ、Å⇔Å、∅⇔Ø、⊥ の垂直/falsum 兼用など）。
5. **半角系／全角系の分業** — 本家はプロポーショナル半角系。全角メトリクスが
   前提の和文（括弧・約物・かな）は **PenchantManufacture-CJK**（等幅・全角、
   有料頒布予定）で扱い、本家には収録しない。
6. **メトリクス契約の維持** — 「フォント登録メトリクス（win 帯・advance 幅）を
   そのまま信頼してビルドできる」よう作字側で調整する。ビルドは配置を動かさない
   （「配置の基準」参照）。win 帯の変更は Discord 全点再登録を招くため避ける。
7. **命名・検索性** — トークン・別名の規則は [docs/EMOJI_TECHCODE_SPEC.md] が SSOT。
   保留・移管したカテゴリのトークンも予約済みとして凍結し、再利用しない。

---

## 収録グリフ（PenchantManufacture v3.4-release）

`_original-fonts/penchant-manufacture_v3.4-release/収録グリフ.txt` に記載の作者公式グリフ:

```
ASCII可視記号・数字・英大文字・英小文字 : U+0021–U+007E（94字）
ギリシャ大文字                         : Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω（24字）
ギリシャ小文字                         : α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω（25字）
曲がり引用符                           : ' ' " "（U+2018 U+2019 U+201C U+201D）
上付き                                 : ⁰¹²³⁴⁵⁶⁷⁸⁹ ⁱ ⁿ ⁺ ⁻ ⁼ ⁽ ⁾（17字）
下付き                                 : ₀₁₂₃₄₅₆₇₈₉ ₙ ₊ ₋ ₌ ₍ ₎（16字）
キリル大文字                           : А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я（33字）
キリル小文字                           : а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я（33字）
ラテン拡張 大文字                      : À Á Â Ã Ä Å Ç È É Ê Ë Ì Í Î Ï Ñ Ò Ó Ô Õ Ö Ø Ù Ú Û Ü Ý Ÿ Ā Ē Ī Ō Ū（33字）
ラテン拡張 小文字                      : à á â ã ä å ç è é ê ë ì í î ï ñ ò ó ô õ ö ø ù ú û ü ý ÿ ā ē ī ō ū（33字）
合字・特殊                             : Æ æ Œ œ ẞ ß ı（7字）
算術記号                               : × ÷（2字）
科学・数式記号                         : ± ∓ ℓ ℧ ℏ ℮ √ ∛ ∜ ≈ ≠ ≤ ≥（13字）
数式演算子（v3.4追加）                 : ∞ ∂ ∇ ∈ ∉ ∋ ⊂ ⊃ ⊆ ⊇ ∩ ∪ ∴ ∵ ∝ ≡ ≅ ∅（18字）
論理・証明記号（v3.4追加）             : ∀ ∃ ∄ ¬ ∧ ∨ ⊻ ⊤ ⊢ ⊨ ∎（11字）
参照・校正記号（v3.4追加）             : © ® ※ ¶ § № † ‡ ™（9字）
通貨（v3.4追加）                       : ¥ € £ ¢ ₩ ₽ ¤（7字）
可読補助（v3.4追加）                   : · … ‰ ‱ – —（6字）
```

v3.0-release（Version 1.005）で **ギリシャ小文字 α–ω と ß が新規追加**され、
v3.1-release（Version 1.007）で **上付き17字・下付き16字・キリル66字が追加**、
α の字形が修正された。
v3.2-beta で **アクセント付きラテン66字・合字系7字・`×` `÷` の計74グリフが追加**され、
`ß` の字形が変更された。英小文字 a–z は独立グリフとして x-height・アセンダ・
ディセンダ（g/j/p/q/y は base line 下 ~101/1000 まで伸びる）を持つ。
v3.3-beta（Version 1.008）で **科学・数式記号13字が追加**され、
`+ - < = > ^ ~ i j r s t ν × ÷ ² ³ ¹` と上付き17字・`₋` の計33字の字形が改善された。
トークン・サブカテゴリは `glyph_tokens.py` の `SCIENCE_SYMBOL_TOKENS` /
`GLYPH_NAME_OVERRIDES`（`uni210f`→`hbar` 等の可読名）で定義し、サブカテゴリ
**「数式記号」** に v3.2 の `×` `÷` も併合した（Misskey は一括インポートで
カテゴリごと更新されるため移動コストは無い）。
v3.4-release（Version 1.009）で **拡張記号51字が追加**された:
数式演算子の残り17字＋`∅`（B1。`∅` は Ø の別名運用から独立作字へ格上げ）、
論理・証明記号11字（B15）、参照・校正記号9字（B4）、通貨7字（B6）、可読補助6字（B7）。
`* / %` などのグリフも変更・改善された。トークンは `glyph_tokens.py` の
`MATH_EXT_TOKENS` / `LOGIC_SYMBOL_TOKENS` / `REF_SYMBOL_TOKENS` / `CURRENCY_TOKENS` /
`READABILITY_TOKENS`（すべて文字キー）で定義し、サブカテゴリ **「論理記号」「参照記号」
「通貨」** を新設（数式演算子は「数式記号」へ、可読補助は「記号ほか」へ併合）。
win 帯（793/198）は不変のため、既存絵文字の再登録は不要。

### アクセント記号対応（v3.2-beta）

v3.1 以前は cmap にアクセント付きラテン 56 コードポイントが登録されていたが、
**すべて無印の基底グリフへ再マップ**されていた（`café` が `cafe` と表示される状態）。
v3.2-beta でこの 56 字すべてに実アウトラインが与えられ、さらに `Œ œ Ā–Ū ā–ū Æ æ ẞ ı`
が新規 cmap として追加された。**`glyph_aliases.json` の異体字エイリアスは 0 件**になった。

対応言語: 英語（米・英）／ドイツ語／フランス語／イタリア語／日本語ローマ字（ヘボン式長音
`ā ē ī ō ū`・訓令式 `â ê î ô û`）に加え、スペイン語・ポルトガル語・北欧語の大半。
詳細は [docs/DIACRITIC_EXTENSION_PLAN.md] 参照。**ギリシャ文字のアクセント（モノトニック
20字）は未着手**。

**分音記号の配置帯**（既存の縦バンドを侵さないための規格。作字時に順守すること）

| 帯 | y 範囲 | 高さ | 用途 |
| --- | --- | --- | --- |
| 上帯（大文字用） | 660.5 – **792.5** | 132 | `Ä Ö Ü À É Î Ā` 等。上端は `Ё Й` と同一 |
| 中帯（小文字用） | 462.3 – **594.4** | 132 | `ä ö ü à é î ā` 等。上端は `ё й` と同一 |
| 下帯（下付き用） | **−198.1** – 0 | 198 | `Ç ç` のセディーユ |

上帯と中帯は高さが等しく、**記号パーツを 198.2 units 平行移動しただけ**の関係にある。
`ì î ï í ī` は `ı`（dotlessi, U+0131）を土台とし、i のドットを除去してある。

上付き・下付きは当初「合成」で作る計画だったが、**作者が実グリフとして作字した**ため
`generate_decal.py` に合成処理は不要（既存グリフと同じ経路でそのまま処理される）。

### 配置の基準（v3.3 で「フォント登録メトリクスをそのまま信頼」へ変更）

**v3.3-beta 以降、グリフの配置はビルド側で一切動かさない。** 作者が
`usWinAscent=793 / usWinDescent=198` をインク帯に一致するよう登録し、
「登録されている横幅・上下位置のままカスタム絵文字へビルドできる」よう
作字側で調整した（大型算術記号・アクセント記号を含む全グリフがこの契約に収まる）。
これを受けてパイプラインは:

- **縦**: `extract_glyphs.metrics_fit` が **OS/2 win 帯 [−198, 793]** を全グリフ共通の
  固定バンドとして使う（`compute_vertical_fit` によるインク実測の動的算出は廃止）。
  スケールは `viewbox / upm`（win 帯が em を超えた場合のみ縮小）。
- **横**: デカールのクロップは **advance 幅 ∪ インク**（`extract_glyphs` が SVG に
  埋め込む配置フレームを `generate_decal.frame_box` が読む）。正のサイドベアリングに
  よる字間は絵文字の余白として保持され、負のサイドベアリング（`√ ∛ ∜` の笠の
  右超過、`j` の尾など 24 字）のインクも切り落とさない。
- 帯を逸脱するインクは `extract_glyphs.py` が **WARN** で検出する（現行 v3.4 は逸脱ゼロ）。

利点: フォント更新でインク実測が変わっても配置・出力が揺れない（v3.1→v3.3 で起きた
全点サブピクセルシフトや描画一致統合の入れ替わりが再発しない）。作字側で意図した
字間・上下位置（上付き数字と `∛ ∜` の頭揃えなど）がそのまま絵文字組版に現れる。

> **歴史**: v3.0 以前はベースラインをアセンダー固定で置き、`Ё Й` の頭が切れていた。
> v3.1–v3.2 はインク実測からベースラインを動的算出（縦バンド 440px → 508px、
> 既存グリフ 86.6% 縮小）。v3.3 で上記のメトリクス契約に置き換え、実測依存を廃止した。

> **フォント更新時に必ず確認すること**
> `extract_glyphs.py` の WARN（win 帯逸脱）が出たら、そのグリフは頭や尾が
> クリップされる。作者に「win 帯内に収める」か「win メトリクスの更新」を依頼する。
> win 帯自体が変わると全グリフの縦位置・サイズが変わり、**Discord 登録済み絵文字の
> 全点手動再アップロード**が必要になるため、帯の変更は避けるのが望ましい。

### 制作途中グリフの除外

作者が調整中の字は、絵文字として公開すると差し替え時に登録済み絵文字を作り直す羽目に
なるため、`extract_glyphs.py` の `PENDING_RANGES` に挙げた範囲を **既定でスキップ** する。
`--include-pending` で一時的に含められる。

**現在 `PENDING_RANGES` は空**（v3.1-release でキリル全66字が確定し除外を解除）。
今後グリフが作字中の状態で追加された場合は、この表に範囲を足すだけでビルド対象外にできる
（他スクリプトの変更は不要）。

### 別バージョンのフォントでビルドする

フォントを読むのは inspect / extract の 2 ステップだけなので、`--font` を渡せば
`assets/fonts/` を差し替えずに任意の OTF でビルドできる。開発版フォントの試写に使う。

```bash
python scripts/build.py --font "_original-fonts/.develop/penchant-manufacture_vX.Y-develop/PenchantManufacture.otf"
```

> `_original-fonts/` は `.gitignore` 対象のため、開発版でのビルドは**そのフォントを持つ
> 環境でのみ**再現できる。release になったら `assets/fonts/` を差し替え、
> `--font` 指定なしの通常ビルドへ戻すこと（差し替えはコミット履歴を残す）。

### 重複排除の方針（同一画像を二重生成しない）

cmap は 327 コードポイントだが、フォント上は別グリフでも**絵文字サイズで描画が一致する字**
を含むため、素朴に全コードポイントを書き出すと同じ画像が別名で二重生成される。
SNS カスタム絵文字（Discord・Misskey）向けには同一画像の重複登録を避けたい。
本パイプラインは 2 段でこれを排除する:

1. **cmap 再マップの統合（`extract_glyphs.py`）** — 異なるコードポイントが同一グリフを
   指す場合、グリフ名でユニーク化して 1 枚だけ SVG 化し、統合した異体字は
   `docs/glyph_aliases.json` に検索エイリアスとして記録する。
   v3.1 以前はアクセント付きラテン 56 字（À Á Â … ø ù … Ÿ）が基底グリフ
   （A/E/I/O/U/Y/C/N とその小文字）への再マップだったためここで 56 件が統合されていたが、
   **v3.2-beta で全 56 字に実アウトラインが与えられ、統合件数は 0 になった**。
   現在の正規グリフは **321 字**（機構自体は将来の再マップに備えて残す）。
2. **描画一致の統合（`generate_decal.py` → `dedupe_renders`）** — フォント上は別グリフ
   でも絵文字サイズで描画が完全一致する字は、出力 PNG を正規側 1 枚に統合する。
   **13 字が 9 グループへ統合され、絵文字は正味 321 字**となる。全スキーム×全サイズで
   バイト完全一致する場合のみ統合する安全側の判定。統合表は
   `docs/glyph_render_merges.json`。**ソース SVG（`src/glyphs/`）は 334 字を温存**し、
   各文字セットの独立性を保つ（統合は出力 PNG と絵文字登録のみ）。
   v3.3 のメトリクス基準クロップでは **advance 幅が異なる同形字は統合されない**
   （`C/С` `T/Т` `c/с` `x/х` `о` は幅が僅かに違い独立。字間まで含めた
   フォント設計に忠実な判定であり、配置が実測に依存しないため今後は安定する）。

   | 正規 | 統合される字 |
   | --- | --- |
   | `A` | `А`(キリル) `Α`(ギリシャ) |
   | `B` | `Β` `В` |
   | `E` | `Ε` `Е` |
   | `O` | `О` `Ο` |
   | `o` | `ο` |
   | `К`(キリル) | `Κ`(ギリシャ) |
   | `М`(キリル) | `Μ` |
   | `Н`(キリル) | `Η` |
   | `Χ`(ギリシャ) | `Х`(キリル) |

   キリルの同形字はラテン／ギリシャ側へ統合されるが、**トークン（`yua` など）と
   リテラル字（`А`）は正規側の検索エイリアスに残る**ため、型番検索での引きやすさは失われない。

| 段階                       | 対象         | v3.1-release | v3.2-beta | v3.3-beta | v3.4-release |
| -------------------------- | ------------ | ------------ | --------- | --------- | ------------ |
| cmap マッピング            | —            | 309          | 327       | 340       | 391          |
| 実グリフ                   | —            | 253          | 328       | 341       | 392          |
| SVG ソース（cmap再マップ統合後） | src/glyphs   | **247**      | **321**   | **334**   | **385**      |
| 絵文字 PNG（描画一致統合後）     | dist/glyphs_decal | **230** | **304**   | **321**   | **372**      |

| 項目                 | 値                                        |
| -------------------- | ----------------------------------------- |
| フォント名           | PenchantManufacture (Regular)             |
| リリース             | v3.4-release (2026-08-18)                 |
| バージョン文字列     | Version 1.009 (Fontself Maker 3.6.12)     |
| Units per em         | 1000                                      |
| cap height / x-height | 661 / 462                                |
| 実インク上端 / 下端  | 793.0 / −198.2（帯 991.2 = 99.1% em）     |
| cmap マッピング数    | 391                                       |
| 実グリフ数           | 392                                       |

> v3.2-beta で懸案だった `name` テーブルの版数据え置きは v3.3-beta 以降
> 適切に繰り上げられている（v3.4-release は 1.009。`head.fontRevision` は
> 1.0 のままだが、パイプラインは版数を参照しないためビルドには影響しない）。

> フォントが更新されたら `python scripts/inspect_font.py` を再実行し、
> `docs/glyph_map.txt` で差分を確認すること。

---

## 権限・ライセンス（最優先）

- **著作権者**：RadianN_kswg / ラジアン（柏木主税）
- **ライセンス**：CC BY 4.0
- PenchantManufacture フォントのグリフは著作者の独自創作物。
  第三者フォント・商用グリフのグリフパスを流用することを **絶対に行わないこと**。
- すべての出力ファイルにクレジット属性を保持すること。
- `_original-fonts/` 内のファイルは **読み取り専用**。ビルドスクリプトから変更・削除禁止。

---

## ディレクトリ構成

姉妹プロジェクト **Secvier** のビルド構成（`dist/{カテゴリ}/{バリアント}/` ＋
`_exported-dist/` への Misskey 一括インポート zip）に揃えている。

```
PenchantManufacture_ImageAssets/
├── AGENTS.md                   ← 本ファイル（エージェント共通指示書）
├── CLAUDE.md                   ← Claude Code 互換入口（@AGENTS.md のみ）
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot 向け補足
├── assets/
│   └── fonts/
│       └── PenchantManufacture.otf ← ビルド参照フォント（_original-fontsのコピー）
├── src/
│   └── glyphs/                 ← グリフ SVGソース 321字（アウトライン化済み、extract_glyphs.py 出力）
├── dist/
│   ├── glyphs/                 ← グリフ透過PNG（72px / 512px、装飾なし、export_png.py 出力）
│   ├── glyphs_decal/{variant}/       ← 工業デカール 幅可変PNG（Misskey向け・マスター）
│   ├── glyphs_decal_square/{variant}/ ← 工業デカール 正方形PNG（Discord向け）
│   │                               variant = sumi（既定）/ rust / hazard / patina / nickel
│   └── glyphs_spacer/                ← スペーサ 完全透過PNG（バリアント非依存・Misskey専用）
├── svg2png/
│   └── glyphs/                 ← SVG の単純PNG変換（装飾なし、ユーティリティ用途）
├── scripts/
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/glyphs/ SVG（重複排除＋制作途中グリフ除外）
│   ├── export_png.py           ← SVG → PNG変換（dist/glyphs, svg2png/）
│   ├── generate_decal.py       ← 工業デカール生成（幅可変＋正方形、描画一致統合）
│   ├── generate_spacers.py     ← スペーサ透過PNG生成（バリアント非依存、Pillowのみ）
│   ├── glyph_tokens.py         ← 字体トークン／後置タグ／サブカテゴリ 命名様式のSSOT
│   ├── build_misskey_zip.py    ← Misskey一括インポートzip生成 → _exported-dist/
│   └── build.py                ← 全ステップ一括ビルド
├── docs/
│   ├── glyph_map.txt           ← inspect_font.py が自動生成
│   ├── glyph_aliases.json      ← 異体字→正規グリフ 対応表（extract_glyphs.py 生成）
│   ├── glyph_render_merges.json ← 描画一致グリフ 統合表（generate_decal.py 生成）
│   ├── glyph_spacers.json      ← スペーサ対応表（generate_spacers.py 生成）
│   ├── EMOJI_TECHCODE_SPEC.md   ← 絵文字 命名様式（確定）
│   ├── GLYPH_EXTENSION_PLAN.md  ← 追加グリフ計画
│   ├── DIACRITIC_EXTENSION_PLAN.md ← アクセント記号 収録計画・配置帯規格
│   └── DECAL_VARIANTS.md        ← 工業デカール バリアント仕様
├── _original-fonts/            ← 原本（読み取り専用、.gitignore対象）
├── _exported-dist/             ← エクスポートzip格納（.gitignore対象）
├── requirements.txt
├── .gitattributes
└── LICENSE
```

---

## ファイル命名規則

| 対象                        | 命名パターン                          | 例                                |
| --------------------------- | ------------------------------------- | --------------------------------- |
| グリフ SVG（src/glyphs）    | `char_{AGL名}_{コードポイント}.svg`   | `char_A_0041.svg`, `char_Alpha_0391.svg` |
| PNG出力（dist/glyphs）      | `{stem}_72.png` / `{stem}_512.png`    | `char_A_0041_512.png`             |
| 単純PNG変換（svg2png）      | `{stem}.png`                          | `char_A_0041.png`                 |

### 命名の要点

- ステムは `char_{AGL名}_{コードポイント16進4桁}` 形式。
- **AGL名**（Adobe Glyph List）を優先（`A`, `zero`, `exclam`, `Alpha`, `quoteleft` など）。
  AGL に無い場合はフォントのグリフ名、それも不適なら `uniXXXX` にフォールバック。
  AGL 名を持たない字は `glyph_tokens.GLYPH_NAME_OVERRIDES` で読める名に揃える
  （例 U+1E9E `ẞ` はフォント側 `uni1e9e` → `Germandbls`）。
- 末尾のコードポイントにより、case-insensitive な Windows でも大文字/小文字グリフ
  （例: `A` U+0041 と `a` U+0061、`Alpha` U+0391 と `alpha` U+03B1、
  `Germandbls` U+1E9E と `germandbls` U+00DF）が衝突しない。

> **絵文字名（`glyph_token`）は AGL 名フォールバックに頼らないこと。**
> フォールバックは AGL を小文字化するため、`Adieresis`(Ä) と `adieresis`(ä) が
> 同一トークンへ潰れ、Misskey の絵文字名が衝突する。ラテン拡張は
> `{u|l}{基底字}{記号2字}` の固定 4 字（`uadi` / `ladi`）で大小を分ける。
> 新しい字種を追加するときは `scripts/glyph_tokens.py` に必ずトークン定義を足す。

---

## 技術スタック

- **言語**: Python 3.11+
- **主要ライブラリ**:
  - `fontTools` — フォントグリフ解析・アウトライン抽出（`SVGPathPen`）、AGL名解決
  - `cairosvg` — SVG→PNG変換
  - `Pillow` — PNG後処理・保存
  - `click` — CLIインターフェース
  - `svgwrite` — SVGファイル生成補助（将来の合成SVG用）
- **フォントファイル**: `assets/fonts/PenchantManufacture.otf`

---

## ビルドフロー

```
PenchantManufacture.otf
  │
  ├─ [検査] scripts/inspect_font.py
  │         └─ docs/glyph_map.txt
  │
  ├─ [グリフ アウトライン抽出＋重複排除] scripts/extract_glyphs.py
  │         ├─ src/glyphs/char_*.svg  （正規321字、fontToolsのSVGPathPenで純粋パス）
  │         └─ docs/glyph_aliases.json（異体字→正規グリフ 対応表）
  │
  ├─ [単純PNG変換] scripts/export_png.py
  │         ├─ dist/glyphs/{stem}_72.png / {stem}_512.png
  │         └─ svg2png/glyphs/{stem}.png
  │
  ├─ [工業デカール生成＋描画一致統合] scripts/generate_decal.py
  │         ├─ dist/glyphs_decal/{variant}/{stem}_{512,128}.png        （幅可変・Misskey）
  │         ├─ dist/glyphs_decal_square/{variant}/{stem}_{512,128}.png （正方形・Discord）
  │         └─ docs/glyph_render_merges.json（描画一致グリフ 統合表）
  │
  ├─ [スペーサ生成] scripts/generate_spacers.py  ※ decal の出力寸法を実測するため decal の後
  │         ├─ dist/glyphs_spacer/spacer_{spc,gap}_{512,128}.png（完全透過・バリアント非依存）
  │         └─ docs/glyph_spacers.json（スペーサ対応表）
  │
  └─ [Misskey zip] scripts/build_misskey_zip.py
            └─ _exported-dist/penchant-misskey-{timestamp}.zip（meta.json付き）
```

一括実行は `python scripts/build.py`（全ステップ）。`--step` で個別指定。
ステップ順: inspect → extract → png → svg2png → decal → spacer → misskey_zip。

### ビルドコマンド早見表

```bash
pip install -r requirements.txt          # 初回セットアップ（numpy / scipy 含む）
python scripts/inspect_font.py           # フォント検査 → docs/glyph_map.txt
python scripts/extract_glyphs.py --dry-run   # 抽出対象の確認（生成なし）
python scripts/extract_glyphs.py         # グリフSVG抽出（重複排除＋制作途中グリフ除外）
python scripts/extract_glyphs.py --include-pending  # 制作途中グリフ（キリル）も抽出
python scripts/export_png.py             # src/glyphs/*.svg → dist/glyphs/, svg2png/
python scripts/generate_decal.py         # 工業デカール（幅可変＋正方形）＋描画一致統合
python scripts/generate_decal.py -v rust # 単一スキームのみ（統合はスキップ）
python scripts/generate_spacers.py       # スペーサ透過PNG（decal の後に実行）
python scripts/build_misskey_zip.py      # Misskey一括インポートzip → _exported-dist/
python scripts/build.py                  # 全ステップ一括
python scripts/build.py --dry-run        # 実行確認（ファイル生成なし）
python scripts/build.py --step decal     # 特定ステップのみ
python scripts/build.py --font "_original-fonts/.develop/penchant-manufacture_v3.1.0-develop/PenchantManufacture.otf"
```

> `generate_decal.py` の描画一致統合は、統合先グリフの PNG を**削除**して重複を消す。
> 読み取り専用マウント等で削除に失敗すると WARN が出るが、`build_misskey_zip.py` は
> `docs/glyph_render_merges.json` を見て消し残りを除外するため zip は正しく作られる。
> 消し残った PNG は次回の `generate_decal.py` 実行時に削除される。

### SNS カスタム絵文字 登録の前提

- **Misskey**: `_exported-dist/penchant-misskey-*.zip` を管理画面から一括インポート。
  非正方形の絵文字をそのまま扱えるため **幅可変版**（字面本来の比率）を収録する。
  meta.json のカテゴリは `PenchantManufacture/工業デカール_{和名}/{字種}`、
  各絵文字に基底文字・異体字（ギリシャ同形など）・バリアント名を alias 付与。
  収録点数は **372字 × 5バリアント ＋ スペーサ2 = 1862点**（v3.4-release ビルド時）。
  字種サブカテゴリに v3.2-beta で **ラテン拡張大文字 / ラテン拡張小文字**、
  v3.3-beta で **数式記号**（科学・数式13字＋`×` `÷`）、
  v3.4-release で **論理記号 / 参照記号 / 通貨** を追加
  （数式演算子18字は既存の「数式記号」へ、可読補助6字は「記号ほか」へ併合）。
- **Discord**: 絵文字は正方形スロットで表示されるため **正方形版**
  （`dist/glyphs_decal_square/{variant}/*_128.png`）を個別アップロードする。
  1 ファイル 256KB 以下（本出力は全て充足）。
- **スペーサ（`spcp` 全角 / `gapp` 半角）は Misskey 専用**。バリアント非依存の完全透過PNGで、
  幅可変表示が効く Misskey でのみ余白幅の差が意味を持つ。Discord は正方形パディングで
  両者が同一画像に潰れるため対象外（正方形版を生成しない）。詳細は
  [GLYPH_EXTENSION_PLAN.md](docs/GLYPH_EXTENSION_PLAN.md) §3。

---

## SVG制作仕様

- **viewBox**: `0 0 512 512`（正方形）
- **背景**: 透過（alpha）
- **カラーモード**: sRGB
- **フォント依存の排除**:
  - `src/glyphs/` の SVG は `extract_glyphs.py` が生成するアウトライン化済みパス。
    外部フォント参照を一切持たない（`<path d="...">` のみ）。
- **PNG出力サイズ**: 72px（標準絵文字）/ 512px（高解像度）
- 出力は `scripts/build.py` / `scripts/export_png.py` 経由で `dist/` `svg2png/` に配置すること。

---

## Pythonコーディング規則

- スタイル: PEP 8 準拠
- 型ヒント: 全関数に付与（`from __future__ import annotations`）
- docstring: Google スタイル（日本語可）
- エラーハンドリング: フォント読み込み・SVG変換は必要に応じて `try/except` でラップ

```python
from __future__ import annotations
from pathlib import Path

def render_glyph(char: str, output: Path, size: int = 512) -> None:
    """指定文字のグリフをPNGとして書き出す。

    Args:
        char: レンダリングする文字（PenchantManufacture フォントのグリフ）
        output: 出力PNGパス
        size: 出力サイズ（px）
    """
    ...
```

---

## コミットメッセージ規約

```
<type>(<scope>): <subject>
```

- **type**: `feat` `fix` `build` `docs` `chore` `style`
- **scope**: `glyphs` `scripts` `assets` `docs`
- **言語**: 日本語・英語いずれも可（混在可）

例:

```
feat(glyphs): add outlined SVG extraction for full cmap
build(scripts): add extract_glyphs.py with AGL-based safe naming
docs: add AGENTS.md / CLAUDE.md for PenchantManufacture setup
```

---

## 絶対に行わないこと（全エージェント共通）

- `_original-fonts/` 内ファイルの変更・削除
- PenchantManufacture 以外の商用フォント・第三者フォントのグリフパス流用
- `dist/` `svg2png/` への直接ファイル配置（スクリプト経由のみ）
- ライセンス表記（CC BY 4.0 / 著作者名）の削除・改ざん
- `assets/fonts/PenchantManufacture.otf` の上書き（差し替えはコミット履歴を残すこと）

---

## 作業開始時の共通チェック

- `docs/glyph_map.txt` を読んで利用可能グリフを把握してから作業すること
  （未生成の場合は `python scripts/inspect_font.py` を実行）
- Python依存の追加は `requirements.txt` に記録し、インストール手順も更新すること
- テスト実行: `python scripts/build.py --dry-run`
