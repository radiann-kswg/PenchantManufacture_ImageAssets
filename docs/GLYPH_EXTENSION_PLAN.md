# グリフ拡張計画（OTF実装対象・コードポイント／トークン／エイリアス）

> 状態: **計画ドラフト**。`docs/EMOJI_TECHCODE_SPEC.md`（命名様式・確定）を前提に、
> フォント（OTF）への追加グリフ、および既存拡張グリフ（ギリシャ等）の推敲をまとめる。
> UTF-8 列は各コードポイントの UTF-8 バイト列（hex）。名前は既定バリアント **`sumi`（墨）** の
> 後置タグ `p` を付けた形。他バリアントは `pr`/`ph`/`pt`/`pn`（[SPEC §2.4] 参照）。
>
> 著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0

---

## 1. 実装経路の区分

| 経路 | 意味 | 対象 | 前提 |
| --- | --- | --- | --- |
| **合成**（pipeline） | 既存グリフの縮小・配置・合字で `generate_decal.py` が生成 | A1 上付き / A2 下付き / スペーサ / 単位・型番合字 | 新規作字ほぼ不要 |
| **作字**（font） | 作者がフォントに新規グリフを描き、`_original-fonts/` 更新 → `assets/fonts/*.otf` 差し替え | C1 キリル / C2 大型演算子 / C3 科学単位 / B1–B9 | 作者作業が前提 |
| **別名のみ**（alias） | 既存グリフと同一字面 → 新規画像を作らず検索エイリアスに展開 | ギリシャ⇔ラテン同形、µ⇔μ、Ω⇔Ω、∆⇔Δ、Å⇔Å(Aring) | 描画一致統合の踏襲 |

### トークン導出規則（[SPEC §2.3] の非ASCII拡張）

- 数字/ラテン: `n`/`l`/`u` ＋値（確定済み）。
- ギリシャ小文字: **AGL 名**（`alpha`…、終シグマ ς は `sigmaf`）。
- ギリシャ大文字: **`c`＋AGL 小文字**（`calpha`… / Δ=`cdelta` / Σ=`csigma`）。
- キリル: **`y`（Cyrillic）＋ `u`/`l`（大小）＋翻字**（例 Ж=`yuzh` / ж=`ylzh`）。
- 数式・記号・矢印・単位: **HTMLエンティティ風の短い語トークン**（`sum` `int` `neq` `rarr` `deg` `ohm` 等）。
  先頭が `n`+数字 / `l`・`u`+1字 の2字パターンと衝突しないよう選定済み。
- 上付き/下付き: `sup`/`sub` ＋値（`sup2` `sub2` `supn` `subplus` 等）。

---

## 2. 既存拡張グリフの推敲（ギリシャ）

**現状**: フォントは α–ω（終シグマ ς 含む）と Α–Ω を独立グリフとして収録。うち描画一致で
**A=Α, B=Β, E=Ε, O=Ο, o=ο** の 5 組が [glyph_render_merges.json] で統合され、ギリシャ側は
ラテン絵文字の**別名**（`calpha`→`uap` 等）として扱われ、独自 PNG を持たない。

**推敲ポイント**

1. **終シグマ ς** は `sigma`(σ) と別字。トークン `sigmaf` を与え衝突回避（現行 AGL は `sigma1`/`sigmafinal`）。
   エイリアスに `sigma1` `sigmafinal` も併設。
2. **µ(マイクロ U+00B5)・Ω(オーム 記号)・∆(増分)** は数式・単位側の需要が大きいが、字面は
   ギリシャ `mu`/`comega`/`cdelta` と同一。→ **新規作字せず**、C3（単位）側トークン `micro`/`ohm` を
   ギリシャ絵文字の**別名**として付与（描画一致統合の対象に追加）。
3. 統合済みギリシャ大文字（Α/Β/Ε/Ο）と ο は、Discord ではラテンで代替（別名不可のため）。Misskey は
   `calpha` 等で検索可能。この非対称は仕様として明記する。
4. ギリシャ小文字は数式本文で頻用のため、既定（墨）だけでなく全バリアントで生成継続を推奨。

### 既存 ギリシャ小文字（推敲）
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 統合先 | 主なエイリアス |
| --- | --- | --- | --- | --- | --- | --- |
| `α` | U+03B1 | CE B1 | `alpha` | `alphap` | — | α, greek, alpha |
| `β` | U+03B2 | CE B2 | `beta` | `betap` | — | β, greek, beta |
| `γ` | U+03B3 | CE B3 | `gamma` | `gammap` | — | γ, greek, gamma |
| `δ` | U+03B4 | CE B4 | `delta` | `deltap` | — | δ, greek, delta |
| `ε` | U+03B5 | CE B5 | `epsilon` | `epsilonp` | — | ε, greek, epsilon |
| `ζ` | U+03B6 | CE B6 | `zeta` | `zetap` | — | ζ, greek, zeta |
| `η` | U+03B7 | CE B7 | `eta` | `etap` | — | η, greek, eta |
| `θ` | U+03B8 | CE B8 | `theta` | `thetap` | — | θ, greek, theta |
| `ι` | U+03B9 | CE B9 | `iota` | `iotap` | — | ι, greek, iota |
| `κ` | U+03BA | CE BA | `kappa` | `kappap` | — | κ, greek, kappa |
| `λ` | U+03BB | CE BB | `lambda` | `lambdap` | — | λ, greek, lambda |
| `μ` | U+03BC | CE BC | `mu` | `mup` | — | μ, greek, mu, micro(別名) |
| `ν` | U+03BD | CE BD | `nu` | `nup` | — | ν, greek, nu |
| `ξ` | U+03BE | CE BE | `xi` | `xip` | — | ξ, greek, xi |
| `ο` | U+03BF | CE BF | `omicron` | `omicronp` | o(lop) | ο, greek, omicron |
| `π` | U+03C0 | CF 80 | `pi` | `pip` | — | π, greek, pi |
| `ρ` | U+03C1 | CF 81 | `rho` | `rhop` | — | ρ, greek, rho |
| `ς` | U+03C2 | CF 82 | `sigmaf` | `sigmafp` | — | ς, greek, sigma1, sigmafinal |
| `σ` | U+03C3 | CF 83 | `sigma` | `sigmap` | — | σ, greek, sigma |
| `τ` | U+03C4 | CF 84 | `tau` | `taup` | — | τ, greek, tau |
| `υ` | U+03C5 | CF 85 | `upsilon` | `upsilonp` | — | υ, greek, upsilon |
| `φ` | U+03C6 | CF 86 | `phi` | `phip` | — | φ, greek, phi |
| `χ` | U+03C7 | CF 87 | `chi` | `chip` | — | χ, greek, chi |
| `ψ` | U+03C8 | CF 88 | `psi` | `psip` | — | ψ, greek, psi |
| `ω` | U+03C9 | CF 89 | `omega` | `omegap` | — | ω, greek, omega |

### 既存 ギリシャ大文字（推敲）
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 統合先 | 主なエイリアス |
| --- | --- | --- | --- | --- | --- | --- |
| `Α` | U+0391 | CE 91 | `calpha` | `calphap` | A(uap) | Α, greek, cap_alpha |
| `Β` | U+0392 | CE 92 | `cbeta` | `cbetap` | B(ubp) | Β, greek, cap_beta |
| `Γ` | U+0393 | CE 93 | `cgamma` | `cgammap` | — | Γ, greek, cap_gamma |
| `Δ` | U+0394 | CE 94 | `cdelta` | `cdeltap` | — | Δ, greek, cap_delta, increment(別名) |
| `Ε` | U+0395 | CE 95 | `cepsilon` | `cepsilonp` | E(uep) | Ε, greek, cap_epsilon |
| `Ζ` | U+0396 | CE 96 | `czeta` | `czetap` | — | Ζ, greek, cap_zeta |
| `Η` | U+0397 | CE 97 | `ceta` | `cetap` | — | Η, greek, cap_eta |
| `Θ` | U+0398 | CE 98 | `ctheta` | `cthetap` | — | Θ, greek, cap_theta |
| `Ι` | U+0399 | CE 99 | `ciota` | `ciotap` | — | Ι, greek, cap_iota |
| `Κ` | U+039A | CE 9A | `ckappa` | `ckappap` | — | Κ, greek, cap_kappa |
| `Λ` | U+039B | CE 9B | `clambda` | `clambdap` | — | Λ, greek, cap_lambda |
| `Μ` | U+039C | CE 9C | `cmu` | `cmup` | — | Μ, greek, cap_mu |
| `Ν` | U+039D | CE 9D | `cnu` | `cnup` | — | Ν, greek, cap_nu |
| `Ξ` | U+039E | CE 9E | `cxi` | `cxip` | — | Ξ, greek, cap_xi |
| `Ο` | U+039F | CE 9F | `comicron` | `comicronp` | O(uop) | Ο, greek, cap_omicron |
| `Π` | U+03A0 | CE A0 | `cpi` | `cpip` | — | Π, greek, cap_pi |
| `Ρ` | U+03A1 | CE A1 | `crho` | `crhop` | — | Ρ, greek, cap_rho |
| `Σ` | U+03A3 | CE A3 | `csigma` | `csigmap` | — | Σ, greek, cap_sigma |
| `Τ` | U+03A4 | CE A4 | `ctau` | `ctaup` | — | Τ, greek, cap_tau |
| `Υ` | U+03A5 | CE A5 | `cupsilon` | `cupsilonp` | — | Υ, greek, cap_upsilon |
| `Φ` | U+03A6 | CE A6 | `cphi` | `cphip` | — | Φ, greek, cap_phi |
| `Χ` | U+03A7 | CE A7 | `cchi` | `cchip` | — | Χ, greek, cap_chi |
| `Ψ` | U+03A8 | CE A8 | `cpsi` | `cpsip` | — | Ψ, greek, cap_psi |
| `Ω` | U+03A9 | CE A9 | `comega` | `comegap` | — | Ω, greek, cap_omega, ohm(別名) |

> 注: Σ(U+03A3 ギリシャ) と ∑(U+2211 総和演算子) は**別字**。数式主役の大型総和は §4 C2 の `sum` を用いる。
> 同様に Π(U+03A0) と ∏(U+220F) も区別する。

---

## 3. 合成グリフ（作字不要・最優先）

### A1 上付き（0–9・演算子・n/i）— **実装済み（v3.1.0 で作字）**

> **当初計画からの変更**: 既存 0–9 と `+ - = ( )` の縮小・上寄せによる**合成**を想定していたが、
> v3.1.0-develop で **作者が実グリフとして作字した**。よって合成処理は実装せず、
> 既存グリフと同じ経路（extract → decal）でそのまま処理される。トークン名は下表のまま確定。
> 字面は既存グリフの縦方向の範囲に収まるため、全グリフ共通の固定縦バンドは変化しない。

| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `⁰` | U+2070 | E2 81 B0 | `sup0` | `sup0p` | superscript, sup_0 |
| `¹` | U+00B9 | C2 B9 | `sup1` | `sup1p` | superscript, sup_1 |
| `²` | U+00B2 | C2 B2 | `sup2` | `sup2p` | superscript, sup_2 |
| `³` | U+00B3 | C2 B3 | `sup3` | `sup3p` | superscript, sup_3 |
| `⁴` | U+2074 | E2 81 B4 | `sup4` | `sup4p` | superscript, sup_4 |
| `⁵` | U+2075 | E2 81 B5 | `sup5` | `sup5p` | superscript, sup_5 |
| `⁶` | U+2076 | E2 81 B6 | `sup6` | `sup6p` | superscript, sup_6 |
| `⁷` | U+2077 | E2 81 B7 | `sup7` | `sup7p` | superscript, sup_7 |
| `⁸` | U+2078 | E2 81 B8 | `sup8` | `sup8p` | superscript, sup_8 |
| `⁹` | U+2079 | E2 81 B9 | `sup9` | `sup9p` | superscript, sup_9 |
| `⁺` | U+207A | E2 81 BA | `supplus` | `supplusp` | superscript, sup_plus |
| `⁻` | U+207B | E2 81 BB | `supminus` | `supminusp` | superscript, sup_minus |
| `⁼` | U+207C | E2 81 BC | `supeq` | `supeqp` | superscript, sup_eq |
| `⁽` | U+207D | E2 81 BD | `suplp` | `suplpp` | superscript, sup_lp |
| `⁾` | U+207E | E2 81 BE | `suprp` | `suprpp` | superscript, sup_rp |
| `ⁿ` | U+207F | E2 81 BF | `supn` | `supnp` | superscript, sup_n |
| `ⁱ` | U+2071 | E2 81 B1 | `supi` | `supip` | superscript, sup_i |

### A2 下付き（0–9・演算子・n）— **実装済み（v3.1.0 で作字）**

添字（H₂O、x₁、CO₂）に必須。A1 と同じく**合成ではなく作者の作字**に変更された。

| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `₀` | U+2080 | E2 82 80 | `sub0` | `sub0p` | subscript, sub_0 |
| `₁` | U+2081 | E2 82 81 | `sub1` | `sub1p` | subscript, sub_1 |
| `₂` | U+2082 | E2 82 82 | `sub2` | `sub2p` | subscript, sub_2 |
| `₃` | U+2083 | E2 82 83 | `sub3` | `sub3p` | subscript, sub_3 |
| `₄` | U+2084 | E2 82 84 | `sub4` | `sub4p` | subscript, sub_4 |
| `₅` | U+2085 | E2 82 85 | `sub5` | `sub5p` | subscript, sub_5 |
| `₆` | U+2086 | E2 82 86 | `sub6` | `sub6p` | subscript, sub_6 |
| `₇` | U+2087 | E2 82 87 | `sub7` | `sub7p` | subscript, sub_7 |
| `₈` | U+2088 | E2 82 88 | `sub8` | `sub8p` | subscript, sub_8 |
| `₉` | U+2089 | E2 82 89 | `sub9` | `sub9p` | subscript, sub_9 |
| `₊` | U+208A | E2 82 8A | `subplus` | `subplusp` | subscript, sub_plus |
| `₋` | U+208B | E2 82 8B | `subminus` | `subminusp` | subscript, sub_minus |
| `₌` | U+208C | E2 82 8C | `subeq` | `subeqp` | subscript, sub_eq |
| `₍` | U+208D | E2 82 8D | `sublp` | `sublpp` | subscript, sub_lp |
| `₎` | U+208E | E2 82 8E | `subrp` | `subrpp` | subscript, sub_rp |
| `ₙ` | U+2099 | E2 82 99 | `subn` | `subnp` | subscript, sub_n |

### スペーサ（実装済み・バリアント非依存）

コードポイントを持たない独自アセット。**5バリアントで見た目が変わらない完全透過PNG**
のため、スキーム別に複製せず **1 組のみ** 生成する。後置タグは**プロジェクト印 `p` のみ**
（バリアント記号を持たない ＝ [SPEC §2.4] 注記）。作字不要で、幅は参照グリフのデカールPNG
実測値なのでフォント更新にも自動追従する。

| トークン | 名前 | 内容 | 参照グリフ | 512px | 128px | 主なエイリアス |
| --- | --- | --- | --- | --- | --- | --- |
| `spc` | `spcp` | 全角スペース | `m` (U+006D) | 290×512 | 73×128 | space, emsp, zenkaku, 全角, スペース, spacer |
| `gap` | `gapp` | 半角スペース | `I` (U+0049) | 141×512 | 35×128 | ensp, halfspace, hankaku, 半角, スペース, spacer |

- `m` は全148グリフ中の**最大幅**（w/ψ/φ/ω/# と同値）＝ em 幅。`I` はその **48.6%** ＝ ほぼ半角。
- 生成: `scripts/generate_spacers.py` → `dist/glyphs_spacer/spacer_{token}_{512,128}.png`
  ＋ `docs/glyph_spacers.json`（対応表）。
- **Misskey 専用**。Discord は絵文字を正方形スロットで表示するため、正方形パディング後は
  `spcp` と `gapp` が完全透過の同一画像に潰れて区別できない。よって正方形版は生成しない。
  この非対称は仕様（ギリシャ統合と同様）。
- 汎用語すぎて既存絵文字と衝突しやすい `blank`（正方形いっぱいの余白）は**登録しない**。
- 留意: 完全透過のためピッカー・管理画面ではサムネイルが空白になる。名前・エイリアス・
  カテゴリ（`PenchantManufacture/共通/スペーサ`）が唯一の手掛かりとなる。

### 単位/型番合字（合成・未実装）

| 種別 | トークン | 既定名(墨) | 内容 | 主なエイリアス |
| --- | --- | --- | --- | --- |
| 単位合字 | `hz` `khz` `mhz` `ghz` | `hzp` … | Hz/kHz/MHz/GHz を1枚に合成 | unit, freq |
| 単位合字 | `ns` `us` `ms` `db` | `nsp` … | ns/µs/ms/dB | unit |
| 型番合字 | `no` `ver` `rev` `sn` `pn` `lot` | `nop` … | No. / Ver. / Rev. / S/N / P/N / Lot | model, part |

> 合字は「1絵文字＝1単位/接頭辞」で **短縮入力**（[SPEC §0-2]）の直接実装。既存英字グリフの合成のみで作字不要。

---

## 4. 作字グリフ（フォント追加が前提）

### C1 キリル文字（型番用）— **作字中・ビルド対象外**

Russian 基本 66 字（А–Я/а–я＋Ё/ё）。トークン `y`＋`u/l`＋翻字。型番で使う字を優先し、
サブセット着手も可。翻字は BGN/PCGN 準拠の簡易版（確定時に微調整可）。

> **現況（v3.1.0-develop）**: 大文字 `А`–`Щ` ＋ `Ё` の **27字が作字済み**、残り39字
> （`Ъ Ы Ь Э Ю Я` と小文字33字）は未着手。字形調整が続くため、
> `extract_glyphs.py` の `PENDING_RANGES`（U+0400–U+04FF）で **既定でビルド対象外**。
> 先に絵文字化すると差し替え時に登録済み絵文字を作り直すことになるため。
>
> 完成したら `PENDING_RANGES` からこの範囲を外すだけでよい。ただしその際、
> `А В К О С Т` はラテン `A B K O C T` とアウトラインが完全一致し、`Е М Н Р Х` も
> 1ユニット差で絵文字サイズでは同一に潰れるため、**`dedupe_renders` によりラテン側へ
> 統合される見込み**（ギリシャ同形と同じ扱い）。型番用途としてキリルを独立させたい場合は
> 統合対象から外す判断が別途必要。

#### C1 キリル大文字
| 字 | U+ | UTF-8 | 翻字 | トークン | 既定名(墨) |
| --- | --- | --- | --- | --- | --- |
| `А` | U+0410 | D0 90 | a | `yua` | `yuap` |
| `Б` | U+0411 | D0 91 | b | `yub` | `yubp` |
| `В` | U+0412 | D0 92 | v | `yuv` | `yuvp` |
| `Г` | U+0413 | D0 93 | g | `yug` | `yugp` |
| `Д` | U+0414 | D0 94 | d | `yud` | `yudp` |
| `Е` | U+0415 | D0 95 | e | `yue` | `yuep` |
| `Ё` | U+0401 | D0 81 | yo | `yuyo` | `yuyop` |
| `Ж` | U+0416 | D0 96 | zh | `yuzh` | `yuzhp` |
| `З` | U+0417 | D0 97 | z | `yuz` | `yuzp` |
| `И` | U+0418 | D0 98 | i | `yui` | `yuip` |
| `Й` | U+0419 | D0 99 | j | `yuj` | `yujp` |
| `К` | U+041A | D0 9A | k | `yuk` | `yukp` |
| `Л` | U+041B | D0 9B | l | `yul` | `yulp` |
| `М` | U+041C | D0 9C | m | `yum` | `yump` |
| `Н` | U+041D | D0 9D | n | `yun` | `yunp` |
| `О` | U+041E | D0 9E | o | `yuo` | `yuop` |
| `П` | U+041F | D0 9F | p | `yup` | `yupp` |
| `Р` | U+0420 | D0 A0 | r | `yur` | `yurp` |
| `С` | U+0421 | D0 A1 | s | `yus` | `yusp` |
| `Т` | U+0422 | D0 A2 | t | `yut` | `yutp` |
| `У` | U+0423 | D0 A3 | u | `yuu` | `yuup` |
| `Ф` | U+0424 | D0 A4 | f | `yuf` | `yufp` |
| `Х` | U+0425 | D0 A5 | kh | `yukh` | `yukhp` |
| `Ц` | U+0426 | D0 A6 | ts | `yuts` | `yutsp` |
| `Ч` | U+0427 | D0 A7 | ch | `yuch` | `yuchp` |
| `Ш` | U+0428 | D0 A8 | sh | `yush` | `yushp` |
| `Щ` | U+0429 | D0 A9 | shch | `yushch` | `yushchp` |
| `Ъ` | U+042A | D0 AA | hard | `yuhard` | `yuhardp` |
| `Ы` | U+042B | D0 AB | y | `yuy` | `yuyp` |
| `Ь` | U+042C | D0 AC | soft | `yusoft` | `yusoftp` |
| `Э` | U+042D | D0 AD | eh | `yueh` | `yuehp` |
| `Ю` | U+042E | D0 AE | yu | `yuyu` | `yuyup` |
| `Я` | U+042F | D0 AF | ya | `yuya` | `yuyap` |

#### C1 キリル小文字
| 字 | U+ | UTF-8 | 翻字 | トークン | 既定名(墨) |
| --- | --- | --- | --- | --- | --- |
| `а` | U+0430 | D0 B0 | a | `yla` | `ylap` |
| `б` | U+0431 | D0 B1 | b | `ylb` | `ylbp` |
| `в` | U+0432 | D0 B2 | v | `ylv` | `ylvp` |
| `г` | U+0433 | D0 B3 | g | `ylg` | `ylgp` |
| `д` | U+0434 | D0 B4 | d | `yld` | `yldp` |
| `е` | U+0435 | D0 B5 | e | `yle` | `ylep` |
| `ё` | U+0451 | D1 91 | yo | `ylyo` | `ylyop` |
| `ж` | U+0436 | D0 B6 | zh | `ylzh` | `ylzhp` |
| `з` | U+0437 | D0 B7 | z | `ylz` | `ylzp` |
| `и` | U+0438 | D0 B8 | i | `yli` | `ylip` |
| `й` | U+0439 | D0 B9 | j | `ylj` | `yljp` |
| `к` | U+043A | D0 BA | k | `ylk` | `ylkp` |
| `л` | U+043B | D0 BB | l | `yll` | `yllp` |
| `м` | U+043C | D0 BC | m | `ylm` | `ylmp` |
| `н` | U+043D | D0 BD | n | `yln` | `ylnp` |
| `о` | U+043E | D0 BE | o | `ylo` | `ylop` |
| `п` | U+043F | D0 BF | p | `ylp` | `ylpp` |
| `р` | U+0440 | D1 80 | r | `ylr` | `ylrp` |
| `с` | U+0441 | D1 81 | s | `yls` | `ylsp` |
| `т` | U+0442 | D1 82 | t | `ylt` | `yltp` |
| `у` | U+0443 | D1 83 | u | `ylu` | `ylup` |
| `ф` | U+0444 | D1 84 | f | `ylf` | `ylfp` |
| `х` | U+0445 | D1 85 | kh | `ylkh` | `ylkhp` |
| `ц` | U+0446 | D1 86 | ts | `ylts` | `yltsp` |
| `ч` | U+0447 | D1 87 | ch | `ylch` | `ylchp` |
| `ш` | U+0448 | D1 88 | sh | `ylsh` | `ylshp` |
| `щ` | U+0449 | D1 89 | shch | `ylshch` | `ylshchp` |
| `ъ` | U+044A | D1 8A | hard | `ylhard` | `ylhardp` |
| `ы` | U+044B | D1 8B | y | `yly` | `ylyp` |
| `ь` | U+044C | D1 8C | soft | `ylsoft` | `ylsoftp` |
| `э` | U+044D | D1 8D | eh | `yleh` | `ylehp` |
| `ю` | U+044E | D1 8E | yu | `ylyu` | `ylyup` |
| `я` | U+044F | D1 8F | ya | `ylya` | `ylyap` |

### C2 大型演算子（正方枠いっぱい・数式主役）
正方フレームを最大に埋めるサイズで作字。字面が大きい記号群。

| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `∑` | U+2211 | E2 88 91 | `sum` | `sump` | summation, sigma_big, math |
| `∏` | U+220F | E2 88 8F | `prod` | `prodp` | product, pi_big, math |
| `∐` | U+2210 | E2 88 90 | `coprod` | `coprodp` | coproduct |
| `∫` | U+222B | E2 88 AB | `int` | `intp` | integral, math |
| `∮` | U+222E | E2 88 AE | `oint` | `ointp` | contour |
| `∬` | U+222C | E2 88 AC | `iint` | `iintp` | double_int |
| `∭` | U+222D | E2 88 AD | `iiint` | `iiintp` | triple_int |
| `∯` | U+222F | E2 88 AF | `oiint` | `oiintp` | surface_int |
| `⨁` | U+2A01 | E2 A8 81 | `bigoplus` | `bigoplusp` | nary_oplus |
| `⨂` | U+2A02 | E2 A8 82 | `bigotimes` | `bigotimesp` | nary_otimes |
| `⨀` | U+2A00 | E2 A8 80 | `bigodot` | `bigodotp` | nary_odot |
| `⋃` | U+22C3 | E2 8B 83 | `bigcup` | `bigcupp` | nary_union |
| `⋂` | U+22C2 | E2 8B 82 | `bigcap` | `bigcapp` | nary_inter |
| `⋁` | U+22C1 | E2 8B 81 | `bigvee` | `bigveep` | nary_or |
| `⋀` | U+22C0 | E2 8B 80 | `bigwedge` | `bigwedgep` | nary_and |

### C3 科学単位 特殊字
µ/Ω/Å は既存グリフ（μ / Ω / Aring）と同形の別名運用も可（§1「別名のみ」）。ℓ/℧/ℏ は新規作字。

| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `ℓ` | U+2113 | E2 84 93 | `ell` | `ellp` | liter, litre, scriptl |
| `℧` | U+2127 | E2 84 A7 | `mho` | `mhop` | invohm, conductance |
| `Å` | U+00C5 | C3 85 | `angst` | `angstp` | angstrom, aring |
| `ℏ` | U+210F | E2 84 8F | `hbar` | `hbarp` | planck, hslash |
| `Ω` | U+03A9 | CE A9 | `ohm` | `ohmp` | omega_unit, resistance |
| `µ` | U+00B5 | C2 B5 | `micro` | `microp` | mu_unit, u_prefix |
| `∅` | U+2205 | E2 88 85 | `empty` | `emptyp` | emptyset, null |
| `℮` | U+212E | E2 84 AE | `estd` | `estdp` | estimated |

### B1 数式演算子（通常サイズ）
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `×` | U+00D7 | C3 97 | `times` | `timesp` | multiply, mul |
| `÷` | U+00F7 | C3 B7 | `div` | `divp` | divide |
| `±` | U+00B1 | C2 B1 | `pm` | `pmp` | plusminus |
| `∓` | U+2213 | E2 88 93 | `mp` | `mpp` | minusplus |
| `≈` | U+2248 | E2 89 88 | `approx` | `approxp` | almosteq |
| `≠` | U+2260 | E2 89 A0 | `neq` | `neqp` | notequal |
| `≤` | U+2264 | E2 89 A4 | `leq` | `leqp` | lessequal |
| `≥` | U+2265 | E2 89 A5 | `geq` | `geqp` | greaterequal |
| `√` | U+221A | E2 88 9A | `sqrt` | `sqrtp` | radical, root |
| `∞` | U+221E | E2 88 9E | `inf` | `infp` | infinity |
| `∂` | U+2202 | E2 88 82 | `del` | `delp` | partial |
| `∇` | U+2207 | E2 88 87 | `nabla` | `nablap` | gradient |
| `∈` | U+2208 | E2 88 88 | `isin` | `isinp` | element, in |
| `∉` | U+2209 | E2 88 89 | `notin` | `notinp` | notelement |
| `∋` | U+220B | E2 88 8B | `sthat` | `sthatp` | suchthat, owns |
| `⊂` | U+2282 | E2 8A 82 | `subset` | `subsetp` | propersubset |
| `⊃` | U+2283 | E2 8A 83 | `supset` | `supsetp` | propersuperset |
| `⊆` | U+2286 | E2 8A 86 | `sube` | `subep` | subseteq |
| `⊇` | U+2287 | E2 8A 87 | `supe` | `supep` | supseteq |
| `∩` | U+2229 | E2 88 A9 | `cap` | `capp` | intersection |
| `∪` | U+222A | E2 88 AA | `cup` | `cupp` | union |
| `∴` | U+2234 | E2 88 B4 | `there4` | `there4p` | therefore |
| `∵` | U+2235 | E2 88 B5 | `becoz` | `becozp` | because |
| `∝` | U+221D | E2 88 9D | `propto` | `proptop` | proportional |
| `≡` | U+2261 | E2 89 A1 | `equiv` | `equivp` | identical |
| `≅` | U+2245 | E2 89 85 | `cong` | `congp` | congruent |
| `⊕` | U+2295 | E2 8A 95 | `oplus` | `oplusp` | circleplus |
| `⊗` | U+2297 | E2 8A 97 | `otimes` | `otimesp` | circletimes |
| `∘` | U+2218 | E2 88 98 | `ring` | `ringp` | compose |

### B2 矢印
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `→` | U+2192 | E2 86 92 | `rarr` | `rarrp` | arrowright, to |
| `←` | U+2190 | E2 86 90 | `larr` | `larrp` | arrowleft |
| `↑` | U+2191 | E2 86 91 | `uarr` | `uarrp` | arrowup |
| `↓` | U+2193 | E2 86 93 | `darr` | `darrp` | arrowdown |
| `↔` | U+2194 | E2 86 94 | `harr` | `harrp` | arrowboth |
| `↕` | U+2195 | E2 86 95 | `varr` | `varrp` | arrowupdn |
| `⇒` | U+21D2 | E2 87 92 | `drarr` | `drarrp` | dblright, implies |
| `⇐` | U+21D0 | E2 87 90 | `dlarr` | `dlarrp` | dblleft |
| `⇔` | U+21D4 | E2 87 94 | `dharr` | `dharrp` | dblboth, iff |
| `↦` | U+21A6 | E2 86 A6 | `mapsto` | `mapstop` | maparrow |
| `↳` | U+21B3 | E2 86 B3 | `hookr` | `hookrp` | downright |
| `↰` | U+21B0 | E2 86 B0 | `hookl` | `hooklp` | upleft |
| `⤷` | U+2937 | E2 A4 B7 | `curvr` | `curvrp` | curvedown |

### B3 度・プライム
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `°` | U+00B0 | C2 B0 | `deg` | `degp` | degree |
| `′` | U+2032 | E2 80 B2 | `prime` | `primep` | minute, foot |
| `″` | U+2033 | E2 80 B3 | `dprime` | `dprimep` | second, inch |
| `‴` | U+2034 | E2 80 B4 | `tprime` | `tprimep` | triprime |

### B4 参照・校正記号
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `№` | U+2116 | E2 84 96 | `numero` | `numerop` | numbersign_no, no |
| `§` | U+00A7 | C2 A7 | `sect` | `sectp` | section |
| `¶` | U+00B6 | C2 B6 | `para` | `parap` | pilcrow, paragraph |
| `†` | U+2020 | E2 80 A0 | `dagger` | `daggerp` | obelisk |
| `‡` | U+2021 | E2 80 A1 | `ddagger` | `ddaggerp` | dbldagger |
| `※` | U+203B | E2 80 BB | `refmark` | `refmarkp` | komejirushi, reference |
| `®` | U+00AE | C2 AE | `reg` | `regp` | registered |
| `™` | U+2122 | E2 84 A2 | `tm` | `tmp` | trademark |
| `©` | U+00A9 | C2 A9 | `copy` | `copyp` | copyright |

### B5 状態・チェック・図形
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `✓` | U+2713 | E2 9C 93 | `check` | `checkp` | ok, pass, tick |
| `✔` | U+2714 | E2 9C 94 | `hcheck` | `hcheckp` | heavycheck |
| `✗` | U+2717 | E2 9C 97 | `cross` | `crossp` | ng, fail |
| `✘` | U+2718 | E2 9C 98 | `hcross` | `hcrossp` | heavycross |
| `●` | U+25CF | E2 97 8F | `bcirc` | `bcircp` | blackcircle, dot |
| `○` | U+25CB | E2 97 8B | `wcirc` | `wcircp` | whitecircle |
| `◆` | U+25C6 | E2 97 86 | `bdia` | `bdiap` | blackdiamond |
| `◇` | U+25C7 | E2 97 87 | `wdia` | `wdiap` | whitediamond |
| `■` | U+25A0 | E2 96 A0 | `bsq` | `bsqp` | blacksquare |
| `□` | U+25A1 | E2 96 A1 | `wsq` | `wsqp` | whitesquare |
| `▲` | U+25B2 | E2 96 B2 | `btriup` | `btriupp` | blacktriup |
| `△` | U+25B3 | E2 96 B3 | `wtriup` | `wtriupp` | whitetriup |
| `▶` | U+25B6 | E2 96 B6 | `btrir` | `btrirp` | play, blacktriright |
| `◀` | U+25C0 | E2 97 80 | `btril` | `btrilp` | blacktrileft |
| `▼` | U+25BC | E2 96 BC | `btrid` | `btridp` | blacktridown |
| `★` | U+2605 | E2 98 85 | `bstar` | `bstarp` | blackstar |
| `☆` | U+2606 | E2 98 86 | `wstar` | `wstarp` | whitestar |
| `⚠` | U+26A0 | E2 9A A0 | `warn` | `warnp` | warning, caution |

### B6 通貨
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `¥` | U+00A5 | C2 A5 | `yen` | `yenp` | jpy, yensign |
| `€` | U+20AC | E2 82 AC | `euro` | `europ` | eur |
| `£` | U+00A3 | C2 A3 | `gbp` | `gbpp` | sterling, pound |
| `¢` | U+00A2 | C2 A2 | `cent` | `centp` | centsign |
| `₩` | U+20A9 | E2 82 A9 | `won` | `wonp` | krw |
| `₽` | U+20BD | E2 82 BD | `rub` | `rubp` | ruble |
| `¤` | U+00A4 | C2 A4 | `curr` | `currp` | currency |

### B7 可読補助
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `·` | U+00B7 | C2 B7 | `mdot` | `mdotp` | middot, centerdot |
| `…` | U+2026 | E2 80 A6 | `hellip` | `hellipp` | ellipsis, dots |
| `‰` | U+2030 | E2 80 B0 | `permil` | `permilp` | perthousand |
| `‱` | U+2031 | E2 80 B1 | `pertt` | `perttp` | pertenk |
| `–` | U+2013 | E2 80 93 | `ndash` | `ndashp` | endash |
| `—` | U+2014 | E2 80 94 | `mdash` | `mdashp` | emdash |

### B8 囲み・山括弧
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `⟨` | U+27E8 | E2 9F A8 | `langle` | `langlep` | mathlangle, vector_l |
| `⟩` | U+27E9 | E2 9F A9 | `rangle` | `ranglep` | mathrangle, vector_r |
| `«` | U+00AB | C2 AB | `ldaquo` | `ldaquop` | guillemet_l |
| `»` | U+00BB | C2 BB | `rdaquo` | `rdaquop` | guillemet_r |
| `‹` | U+2039 | E2 80 B9 | `lsaquo` | `lsaquop` | sguillemet_l |
| `›` | U+203A | E2 80 BA | `rsaquo` | `rsaquop` | sguillemet_r |
| `【` | U+3010 | E3 80 90 | `jlbk` | `jlbkp` | lenticular_l |
| `】` | U+3011 | E3 80 91 | `jrbk` | `jrbkp` | lenticular_r |
| `「` | U+300C | E3 80 8C | `jlcb` | `jlcbp` | kagi_l |
| `」` | U+300D | E3 80 8D | `jrcb` | `jrcbp` | kagi_r |
| `『` | U+300E | E3 80 8E | `jldb` | `jldbp` | dblkagi_l |
| `』` | U+300F | E3 80 8F | `jrdb` | `jrdbp` | dblkagi_r |

### B9 分数（優先度低）
| 字 | U+ | UTF-8 | トークン | 既定名(墨) | 主なエイリアス |
| --- | --- | --- | --- | --- | --- |
| `½` | U+00BD | C2 BD | `half` | `halfp` | onehalf |
| `¼` | U+00BC | C2 BC | `quart` | `quartp` | onequarter |
| `¾` | U+00BE | C2 BE | `thrqrt` | `thrqrtp` | threequarters |
| `⅓` | U+2153 | E2 85 93 | `third` | `thirdp` | onethird |
| `⅔` | U+2154 | E2 85 94 | `twthrd` | `twthrdp` | twothirds |
| `⅛` | U+215B | E2 85 9B | `eighth` | `eighthp` | oneeighth |

---

## 5. エイリアス設定（実装予定・将来対応）

[SPEC §2.6] を各拡張カテゴリへ展開する共通規則:

1. **トークン素名**（`sum` `rarr` `yuzh` `sup2` 等）と **既定名**（`sump` …）は常に付与。
2. **AGL / HTML エンティティ名**（`summation` `arrowright` `notequal` 等）を検索用に付与。
3. **リテラル文字**（`∑` `→` `≠` `α` `Ω` 等、Misskey は非ASCIIも別名可）を付与し、字そのもので検索可能に。
4. **日本語別名**（`そうわ`=∑ / `やじるし`=→ / `おんど`=° / `おおむ`=Ω など）を任意付与。
5. **用途タグ**（`math` `unit` `arrow` `status` `date` `code` `model`）でカテゴリ横断検索。
6. **同形統合**（§1 別名のみ）: µ→μ、Ω→Ω(greek)、∆→Δ、Å→Aring、∑↔Σ は**区別**（統合しない）。
7. **キリル**: 翻字別名（`zh` `shch` 等）＋リテラル字。型番検索での可読性を確保。
8. Discord は名前のみのため、**既定（墨）の素名運用**を基本とし、別名は Misskey 限定と明記。

---

## 6. 実装フェーズ（推奨順）

| 相 | 内容 | 経路 | 依存 |
| --- | --- | --- | --- |
| P0 | 命名様式確定（済） | — | [SPEC] |
| P1 | 既定バリアント `sumi`（墨）実装＋既存143字を新命名で再ビルド | pipeline | generate_decal/misskey_zip 改修 |
| P2a | スペーサ `spcp` / `gapp`（**済**） | 合成 | P1 |
| P2b | A1 上付き 17字 / A2 下付き 16字（**済**） | 作字（v3.1.0） | P1 |
| P2c | 単位・型番合字 | 合成 | P1 |
| P3 | `text_to_emoji.py`＋チートシート | tool | P1,P2 |
| P4 | C2 大型演算子・B1 演算子・B2 矢印・B3 度/プライム・B5 状態 | 作字 | 作者作字 |
| P5 | C1 キリル（大文字27字 作字済／残39字 作字中・**ビルド対象外**）・C3 単位特殊字 | 作字 | 作者作字 |
| P6 | B4 参照 / B6 通貨 / B7 補助 / B8 括弧 / B9 分数 / 特殊合字 | 作字 | 作者作字 |

---

## 7. 留意点

- **トークン衝突回避**: 語トークンは `n`+数字 / `l`・`u`+1字 の2字パターンおよび `c`+ギリシャ名と
  重複しないよう選定済み（例: ≤ は `le` でなく `leq`）。新規追加時も本規則を順守。
- **Discord 点数**: 拡張で総数が増えるため、Discord は既定（墨）の技術用途サブセットを優先登録する。
- **フォント更新手順**: 作字後は `inspect_font.py` 再実行 → `docs/glyph_map.txt` 差分確認 →
  `extract_glyphs.py` → デカール再生成（[AGENTS.md] 手順）。`_original-fonts/` は読み取り専用。
- 参照: [EMOJI_TECHCODE_SPEC.md]（命名様式）/ [DECAL_VARIANTS.md]（バリアント質感）/ [glyph_map.txt]（現行収録）。
