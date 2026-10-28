# Avelia Pavilion Info

Avelia Pavilionの製品情報とWebAdmin追加パッチを公開するリポジトリです。

公開サイト: https://divings.github.io/Avelia-Pavilion-Info/

## 構成

- doc/: GitHub Pages向け静的HTML・CSS・JavaScriptと画像。
- patches/pdf-preview/: PDFプレビューパッチ、説明、SHA-256。
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

パッチ追加時はpatches/配下の専用ディレクトリにZIP（名前は50文字以内）とREADME.mdを配置します。READMEの先頭見出しがリリース名になります。チェックサム更新後にmainへプッシュすると、GitHub Releasesとサイトのリリース一覧が自動更新されます。機能紹介ページdoc/patches.htmlは説明を編集するためのページで、必要に応じて別途更新します。

## 確認状況

画像プレビューパッチは2026-10-28に対象環境へ適用し、利用者より動作確認完了の報告を受けています。その他の構成や全機能の検証完了を意味しません。詳細な対象・制約・適用手順はサイトおよびZIP内READMEを参照してください。

## 自動リリース

使用技術: GitHub Actions、Python標準ライブラリ、GitHub CLI、GitHub Pages。外部の有料サービスや新しい個人用トークンは不要です。Actionsの一時的なGITHUB_TOKENをリリースジョブのcontents: write権限で使用します。

### 追加・更新方法

1. patches/パッチ名/ にZIPとREADME.mdを置く（ディレクトリ名は英小文字・数字・ハイフン）。
2. READMEに対象・変更内容・適用方法・確認状況を記載。
3. 以下を実行してチェックサムを更新・確認。

```sh
python scripts/update_checksums.py
python scripts/validate.py
python scripts/publish_releases.py
```

4. ZIP・README・SHA256SUMS.txtをコミットしてmainへプッシュ。

publish_releases.pyは引数なしでは発行予定を表示するだけです。実際の公開はActionsが--publishで実行します。初回・失敗後の再実行はActionsのPublish patch releases → Run workflowでも行えます。main以外からは公開しません。

### 自動化の範囲

- 各ZIPのCRCとSHA-256・リンクを確認してから発行。
- タグはpatch-パッチ名-ZIPのSHA256先頭12桁。ZIPが同じなら発行済みリリースを照合してスキップし、内容が変われば別リリースになります。
- ドラフト作成 → ZIP・README・SHA256SUMS.txtを添付 → 添付ファイルのSHA-256を照合 → 公開。途中失敗時はドラフトを残し、再実行で不足分だけ再開します。既存の異なるアセットは上書きしません。
- 説明文は対象ディレクトリのREADMEを基に生成します。同じZIPに対するREADMEだけの変更では、公開済みリリースは更新しません。
- doc/releases.htmlをテンプレートに、ビルド時に全パッチのリリース一覧と検索対象を生成。doc/patches.htmlの機能説明は手動編集です。
- 実機のインストールや動作試験は自動化しません。公開をトリガーするのは、人がレビューしてmainへ入れた配布物です。

リリース発行とPages公開は独立したジョブのため、数分間だけ一覧のGitHub Releaseリンクが先に表示される場合があります。失敗はGitHub Actions上で確認してください。

公式資料: [GitHub CLI in workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-github-cli)、[Release API](https://docs.github.com/en/rest/releases/releases)。

## PDFプレビュー追加（2026-10-28）

patches/pdf-preview/に追加しました。画像プレビュー＋ディレクトリ保護構成への適用・構文確認後、利用者よりテストPDFの動作確認完了報告を受けています。ZIP追加により自動リリースとリリース一覧の対象になります。
