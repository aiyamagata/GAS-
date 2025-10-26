#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Cloud Functions 用メイン関数
CSVファイルからSlackに自動送信
"""

import functions_framework
import requests
import json
from datetime import datetime
import pandas as pd
from google.cloud import storage
import pytz
from io import StringIO
import os

@functions_framework.http
def send_daily_schedule(request):
    """Cloud Function: 毎日の予定をSlackに送信"""
    
    # 環境変数から設定を取得
    BUCKET_NAME = os.environ.get('BUCKET_NAME', 'your-bucket-name')
    CSV_FILE = os.environ.get('CSV_FILE', 'schedule.csv')
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#リモートチーム勤怠報告')
    
    if not SLACK_WEBHOOK_URL:
        return {"error": "SLACK_WEBHOOK_URL not configured"}, 500
    
    try:
        # Cloud StorageからCSVファイルを取得
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(CSV_FILE)
        csv_content = blob.download_as_text()
        
        # CSVを解析
        df = pd.read_csv(StringIO(csv_content))
        
        # 今日の日付を取得（日本時間）
        jst = pytz.timezone('Asia/Tokyo')
        today = datetime.now(jst).strftime('%Y-%m-%d')
        
        # 今日の予定を抽出
        today_data = df[df['日付'] == today]
        
        if len(today_data) == 0:
            message = f"📝 {today}の予定はありません。"
        else:
            # メッセージをフォーマット
            message = f"🌅 おはようございます！\n📅 {today}の予定 📅\n\n"
            
            # 予定を時間順にソート
            sorted_data = today_data.sort_values('開始時間')
            
            for _, row in sorted_data.iterrows():
                message += f"🕐 *{row['開始時間']}-{row['終了時間']}*: {row['名前']}: {row['タスク内容']}\n"
            
            message += "\n💪 今日も一日頑張りましょう！"
        
        # Slackに送信
        payload = {
            "text": message,
            "channel": SLACK_CHANNEL
        }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"Sent schedule for {today}",
                "schedule_count": len(today_data)
            }
        else:
            return {
                "status": "error",
                "message": f"Slack API error: {response.status_code}",
                "response": response.text
            }, 500
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500

@functions_framework.http
def test_function(request):
    """テスト用関数"""
    return {
        "status": "ok",
        "message": "Cloud Function is working",
        "timestamp": datetime.now().isoformat()
    }
