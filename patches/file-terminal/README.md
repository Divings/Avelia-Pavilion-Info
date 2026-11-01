# APFT 1.4 — Webファイルコンソール

導入済みAvelia Pavilion WebAdmin向けのファイル操作コンソールです。Oracle Linux 9 / 10を対象とし、既存のfiles_api.phpを利用します。OSのシェルは実行しません。

## 機能
ls、cd、cat、mkdir、touch、mv、rm、info、downloadと、フォルダ保護のlock・unlock・unprotectを提供します。files.phpのリンクを/file_terminal.phpへ変更し、元のAveliaターミナルは/に保持します。既存のログイン・CSRF・フォルダ保護を利用します。画像/PDFプレビューを上書きしません。

## 導入
事前にVMスナップショットと設定バックアップを取得し、ZIPを展開して実行してください。

```bash
sudo bash install-apft.sh
```

既定配置先は/opt/avelia-web-terminal/public、Nginx設定は/etc/nginx/conf.d/avelia-terminal.confです。既存リンクとNginx設定形式が一致する必要があります。インストーラーがPHP実行ルートを追加し、構文確認後にNginxを再読み込みします。失敗時はファイル・設定を復元し、復元後の検証・再読み込みを試みます。バックアップは/var/tmp/apft-backup.*です。

## 確認状況・制限
2026-10-31、Oracle Linux 9のPavilion 1.5.0（フォルダ保護・画像/PDFプレビューあり）へ適用しました。PHP・Nginx構文、未ログイン時の303転送、JS配信、関連サービス稼働を確認済みです。ログイン後のブラウザー全操作とOL10実機動作は未確認です。

保護対象は既存WebAdmin APIが扱う操作です。SSH・FTP・OSからの直接操作には適用しません。unprotectは保護ルールの削除、unlockは現在セッションでの一時解除です。親フォルダを先に解除してください。touchは既存ファイルに対するUnix touchと同じ動作ではなく、既存ファイルでは上書き確認エラーになります。

配布ZIPは元のバイト列を保持しています。画面表示は1.4ですが、インストール完了メッセージには1.3と表示されます。RPM本体に含まれるものではなく、RPM更新でリンク変更が上書きされる場合があります。
