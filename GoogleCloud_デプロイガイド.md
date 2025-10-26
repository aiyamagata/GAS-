# Google Cloud デプロイガイド

## 🚀 Google Cloud Functions での自動スケジューラー

### 📋 概要
Google Cloud Functionsを使用して、CSVファイルからSlackに自動送信するシステムを24時間稼働させます。

## 🛠️ 必要な準備

### 1. Google Cloud プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトIDを記録

### 2. 必要なAPIの有効化
```bash
# Cloud Functions API
# Cloud Storage API
# Cloud Scheduler API
```

### 3. 必要なライブラリのインストール
```bash
pip install google-cloud-functions
pip install google-cloud-storage
pip install google-cloud-scheduler
```

## 📁 ファイル構成

### 1. main.py (Cloud Function)
```python
import functions_framework
import requests
import json
from datetime import datetime
import pandas as pd
from google.cloud import storage
import pytz

@functions_framework.http
def send_daily_schedule(request):
    """Cloud Function: 毎日の予定をSlackに送信"""
    
    # 設定
    BUCKET_NAME = "your-bucket-name"
    CSV_FILE = "schedule.csv"
    SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    try:
        # Cloud StorageからCSVファイルを取得
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(CSV_FILE)
        csv_content = blob.download_as_text()
        
        # CSVを解析
        df = pd.read_csv(StringIO(csv_content))
        
        # 今日の日付を取得
        jst = pytz.timezone('Asia/Tokyo')
        today = datetime.now(jst).strftime('%Y-%m-%d')
        
        # 今日の予定を抽出
        today_data = df[df['日付'] == today]
        
        if len(today_data) == 0:
            message = f"📝 {today}の予定はありません。"
        else:
            # メッセージをフォーマット
            message = f"🌅 おはようございます！\n📅 {today}の予定 📅\n\n"
            
            for _, row in today_data.iterrows():
                message += f"🕐 *{row['開始時間']}-{row['終了時間']}*: {row['名前']}: {row['タスク内容']}\n"
            
            message += "\n💪 今日も一日頑張りましょう！"
        
        # Slackに送信
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        
        return f"成功: {response.status_code}"
        
    except Exception as e:
        return f"エラー: {str(e)}"
```

### 2. requirements.txt
```
functions-framework==3.*
google-cloud-storage==2.*
pandas==2.*
requests==2.*
pytz==2023.*
```

### 3. deploy.sh (デプロイスクリプト)
```bash
#!/bin/bash

# 設定
PROJECT_ID="your-project-id"
FUNCTION_NAME="daily-schedule-sender"
REGION="asia-northeast1"
BUCKET_NAME="your-bucket-name"

# デプロイ
gcloud functions deploy $FUNCTION_NAME \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --region $REGION \
    --source . \
    --entry-point send_daily_schedule

echo "デプロイ完了: $FUNCTION_NAME"
```

## 🔧 セットアップ手順

### 1. Google Cloud SDKのインストール
```bash
# macOS
brew install google-cloud-sdk

# 認証
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Cloud Storageバケットの作成
```bash
gsutil mb gs://your-bucket-name
```

### 3. CSVファイルのアップロード
```bash
gsutil cp "schedule test - シート2 (1).csv" gs://your-bucket-name/schedule.csv
```

### 4. Cloud Functionのデプロイ
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. Cloud Schedulerの設定
```bash
gcloud scheduler jobs create http daily-schedule-job \
    --schedule="0 1 * * *" \
    --uri="https://asia-northeast1-YOUR_PROJECT_ID.cloudfunctions.net/daily-schedule-sender" \
    --http-method=GET \
    --time-zone="Asia/Tokyo"
```

## 💰 料金目安

### Google Cloud Functions
- **無料枠**: 月200万リクエスト
- **超過分**: $0.40/100万リクエスト

### Cloud Storage
- **無料枠**: 5GB
- **超過分**: $0.020/GB/月

### Cloud Scheduler
- **無料枠**: 月3ジョブ
- **超過分**: $0.10/ジョブ/月

**月額料金目安: ほぼ無料（月1回の実行なら無料枠内）**

## 🔄 運用フロー

### 1. CSVファイルの更新
```bash
# 新しいCSVファイルをアップロード
gsutil cp "新しいスケジュール.csv" gs://your-bucket-name/schedule.csv
```

### 2. 手動実行（テスト用）
```bash
curl "https://asia-northeast1-YOUR_PROJECT_ID.cloudfunctions.net/daily-schedule-sender"
```

### 3. ログの確認
```bash
gcloud functions logs read daily-schedule-sender
```

## 🛡️ セキュリティ設定

### 1. IAMロールの設定
```bash
# Cloud Function用のサービスアカウント
gcloud iam service-accounts create schedule-sender \
    --display-name="Schedule Sender"

# 必要な権限を付与
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:schedule-sender@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### 2. 環境変数の設定
```bash
gcloud functions deploy daily-schedule-sender \
    --set-env-vars SLACK_WEBHOOK_URL="your-webhook-url" \
    --set-env-vars BUCKET_NAME="your-bucket-name"
```

## 📊 監視・アラート

### 1. Cloud Monitoringの設定
- 関数の実行回数
- エラー率
- 実行時間

### 2. アラートの設定
- 実行失敗時の通知
- 異常な実行時間の通知

## 🔧 トラブルシューティング

### よくある問題
1. **認証エラー**: サービスアカウントの権限確認
2. **CSVファイルが見つからない**: ファイルパスの確認
3. **Slack送信エラー**: Webhook URLの確認

### デバッグ方法
```bash
# ログの確認
gcloud functions logs read daily-schedule-sender --limit 50

# 関数のテスト
gcloud functions call daily-schedule-sender
```

## 🚀 次のステップ

1. **基本セットアップ**: 上記手順でCloud Functionをデプロイ
2. **テスト実行**: 手動で関数を実行してテスト
3. **スケジューラー設定**: 毎朝10:00の自動実行を設定
4. **監視設定**: ログとアラートの設定

これで24時間稼働の自動スケジューラーが完成します！
