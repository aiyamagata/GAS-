# シフト自動化システム - 実装ファイル

このディレクトリには、シフト自動化システムの実装に必要なファイルが含まれています。

## 📁 ファイル一覧

### メインファイル
- `gas_aggregation_script.js` - GASスクリプト（メイン機能）
- `README.md` - プロジェクトの概要と使用方法
- `SETUP_GUIDE.md` - 詳細なセットアップガイド

### 自動化スクリプト（Python）
- `employee_shift_template.py` - 従業員用テンプレート作成
- `master_aggregation_sheet.py` - マスターシート作成
- `setup_shift_automation.py` - 完全自動セットアップ

### ドキュメント
- `SHIFT_AUTOMATION_GUIDE.md` - 詳細な運用ガイド
- `CSV_TO_SLACK_ガイド.md` - CSV連携ガイド
- `GoogleCloud_デプロイガイド.md` - Google Cloud デプロイガイド

## 🚀 クイックスタート

### 手動セットアップ（推奨）
1. `SETUP_GUIDE.md`を参照してセットアップ
2. `gas_aggregation_script.js`をGASエディタに貼り付け
3. プロパティとトリガーを設定

### 自動セットアップ（上級者向け）
1. Google Cloud Consoleでサービスアカウントを作成
2. `setup_shift_automation.py`を実行
3. 生成されたスプレッドシートでGASスクリプトを設定

## 📋 システム要件

- Googleアカウント
- Slackワークスペース
- Googleスプレッドシート
- Google Apps Script

## 🔧 カスタマイズ

各ファイルは独立してカスタマイズ可能です：

- **GASスクリプト**: 集約ロジックとSlack投稿のカスタマイズ
- **Pythonスクリプト**: テンプレート作成の自動化
- **設定ファイル**: 店舗、役職、シフトタイプの追加

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. `SETUP_GUIDE.md`のトラブルシューティングセクション
2. GASエディタの実行ログ
3. マスター集約シートの`logs`シート

## 📄 ライセンス

MIT License

---

**🎉 シフト管理を自動化して、チームの生産性を向上させましょう！**
