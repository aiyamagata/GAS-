#!/bin/bash

# Google Cloud Functions デプロイスクリプト

echo "🚀 Google Cloud Functions デプロイ開始"

# 設定（実際の値に変更してください）
PROJECT_ID="your-project-id"
FUNCTION_NAME="daily-schedule-sender"
REGION="asia-northeast1"
BUCKET_NAME="your-schedule-bucket"
CSV_FILE="schedule.csv"

# 現在のディレクトリを確認
echo "📁 現在のディレクトリ: $(pwd)"

# 必要なファイルの存在確認
if [ ! -f "cloud_function_main.py" ]; then
    echo "❌ cloud_function_main.py が見つかりません"
    exit 1
fi

if [ ! -f "cloud_requirements.txt" ]; then
    echo "❌ cloud_requirements.txt が見つかりません"
    exit 1
fi

# Google Cloud SDKの認証確認
echo "🔐 Google Cloud認証確認"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Google Cloud認証が必要です"
    echo "gcloud auth login を実行してください"
    exit 1
fi

# プロジェクト設定
echo "⚙️ プロジェクト設定: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# 必要なAPIの有効化
echo "🔧 必要なAPIを有効化中..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Cloud Storageバケットの作成（存在しない場合）
echo "🪣 Cloud Storageバケット確認: $BUCKET_NAME"
if ! gsutil ls gs://$BUCKET_NAME &>/dev/null; then
    echo "📦 バケットを作成中..."
    gsutil mb gs://$BUCKET_NAME
else
    echo "✅ バケットは既に存在します"
fi

# CSVファイルのアップロード
if [ -f "schedule test - シート2 (1).csv" ]; then
    echo "📤 CSVファイルをアップロード中..."
    gsutil cp "schedule test - シート2 (1).csv" gs://$BUCKET_NAME/$CSV_FILE
    echo "✅ CSVファイルをアップロードしました"
else
    echo "⚠️ CSVファイルが見つかりません。手動でアップロードしてください"
fi

# Cloud Functionのデプロイ
echo "🚀 Cloud Functionをデプロイ中..."
gcloud functions deploy $FUNCTION_NAME \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --region $REGION \
    --source . \
    --entry-point send_daily_schedule \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME,CSV_FILE=$CSV_FILE \
    --timeout 60s \
    --memory 256MB

if [ $? -eq 0 ]; then
    echo "✅ Cloud Functionのデプロイが完了しました"
    
    # 関数のURLを取得
    FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(httpsTrigger.url)")
    echo "🔗 関数URL: $FUNCTION_URL"
    
    # テスト実行
    echo "🧪 関数をテスト実行中..."
    curl -X POST "$FUNCTION_URL" -H "Content-Type: application/json" -d '{}'
    
    echo ""
    echo "📅 Cloud Schedulerの設定"
    echo "以下のコマンドで毎朝10:00の自動実行を設定できます:"
    echo ""
    echo "gcloud scheduler jobs create http daily-schedule-job \\"
    echo "    --schedule=\"0 1 * * *\" \\"
    echo "    --uri=\"$FUNCTION_URL\" \\"
    echo "    --http-method=POST \\"
    echo "    --time-zone=\"Asia/Tokyo\""
    
else
    echo "❌ デプロイに失敗しました"
    exit 1
fi

echo ""
echo "🎉 デプロイ完了！"
echo "💡 次のステップ:"
echo "1. 環境変数 SLACK_WEBHOOK_URL を設定"
echo "2. Cloud Schedulerで毎朝10:00の自動実行を設定"
echo "3. テスト実行でSlack通知を確認"
