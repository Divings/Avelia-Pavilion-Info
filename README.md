# Avelia Pavilion Info

Avelia Pavilionの製品情報とWebAdmin追加パッチを公開するリポジトリです。

公開サイト: https://divings.github.io/Avelia-Pavilion-Info/

## 構成

- doc/: GitHub Pages向け静的HTML・CSS・JavaScriptと画像。
- patches/image-preview/: 画像プレビューパッチ、説明、SHA-256。
- patches/directory-protection/: ディレクトリ保護パッチFixed版、説明、SHA-256。
- scripts/build.py: docとpatchesを_siteへ組み立てます。
- .github/workflows/pages.yml: 検証・組み立て後にGitHub Pagesへデプロイします。

製品本体ZIP、接続鍵、サーバー固有の運用設定は含みません。パッチは元ZIPの内容を保持し、配布ファイル名だけ短く整理しています。

## 更新・確認

```sh
python scripts/validate.py
python scripts/build.py
python -m http.server 8765 --directory _site
```

パッチ追加時は専用ディレクトリをpatches/配下に作成し、ZIP・README・SHA256SUMS.txtを配置してください。doc/patches.htmlとルートSHA256SUMS.txtも更新します。公開前にZIPの整合性・相対リンクと内容を確認してください。

## 確認状況

画像プレビューパッチは2026-10-28に対象環境へ適用し、利用者より動作確認完了の報告を受けています。その他の構成や全機能の検証完了を意味しません。詳細な対象・制約・適用手順はサイトおよびZIP内READMEを参照してください。
