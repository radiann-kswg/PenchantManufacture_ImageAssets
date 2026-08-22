# PenchantManufacture 文字列コンバーター

`aiscript/penchant-string-converter.is` は、入力した文字列をこのリポジトリ由来の
PenchantManufacture 工業デカール絵文字の MFM に変換する Misskey AiScript です。

## 動作環境

- AiScript 1.2.1
- `Ui:C:*` を利用できる Misskey Play、AiScript App、Scratchpad
- PenchantManufacture のカスタム絵文字を登録済みの Misskey サーバー

本スクリプトは `https://radiann6631.xsns.jp` の公開絵文字一覧に基づいています。
別のサーバーでは、`_exported-dist/` の一括インポート zip を取り込むなどして、
同じ絵文字名で PenchantManufacture 一式が登録されている必要があります。

## 導入

1. [`aiscript/penchant-string-converter.is`](../aiscript/penchant-string-converter.is)を開く。
2. 内容全体をMisskeyのPlay、AiScript App、またはScratchpadへ貼り付ける。
3. 実行後、文字列を入力してバリアントを選び、「変換」を押す。
4. 「出力MFM」に表示された文字列をコピーしてノートなどで使用する。

外部APIやアクセストークンは使用しません。

## バリアント

次の5種類をプルダウンから選択できます（`scripts/glyph_tokens.py` の
`VARIANT_JP` / `VARIANT_SUFFIX` が正）。

| 表示名 | 絵文字名の接尾辞 |
| --- | --- |
| 墨 | `p` |
| 酸鉄 | `pr` |
| 警戒 | `ph` |
| 緑青真鍮 | `pt` |
| 白銅燐光 | `pn` |

スペーサだけはバリアント非依存で、常に `:gapp:`（半角スペース）/
`:spcp:`（全角スペース）へ変換されます。

## 変換仕様

- 収録文字は対応する工業デカール絵文字のMFM（例: `:uap:`）へ変換します。
- 描画一致で統合された異体字（ギリシャ大文字 `Α` など）も、統合先の絵文字
  （`Α` → `:uap:`）へ変換します。リポジトリの「同形は作らない」方針と同じ扱いです。
- ローマ数字13～39は、複数のUnicode表現（`ⅩⅢ` / `ⅩⅡⅠ` / `ⅫⅠ` など）を
  字詰め済み合成絵文字へ最長一致で変換します（大文字 `rom13`～`rom39`、
  小文字 `lrom13`～`lrom39`）。
- 対応する絵文字がない文字は、出力中へ次の赤太字MFM形式で記録します。

```text
$[fg.color=f44 **エラー: N文字目「文字」に該当するカスタム絵文字がありません。**]
```

## 対応表の更新（自動生成）

`let character_map` から `let variants` までの**データ部は自動生成**です。手で編集せず、
グリフを追加・改名したら次を実行して再生成し、生成結果をコミットしてください。

```bash
python scripts/build.py --step aiscript   # = python scripts/generate_aiscript.py
python scripts/generate_aiscript.py --dry-run   # 差分の有無だけ確認
```

生成元は `build_misskey_zip.py` と同じ収録判定（`dist/glyphs_decal/sumi/` ＋
`scripts/glyph_tokens.py` ＋ `docs/glyph_*.json`）なので、
**一括インポートzipに入る絵文字＝このツールで変換できる文字**になります。

`@convert` 以降のUI・変換ロジックは手編集して構いません。

## ライセンスとクレジット

本スクリプトはリポジトリ本体と同じCC BY 4.0で提供します。
PenchantManufactureおよび画像アセットの著作者は
RadianN_kswg / ラジアン（柏木主税）です。
