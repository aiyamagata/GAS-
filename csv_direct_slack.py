#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSVファイルから直接Slack送信システム
Googleカレンダー連携なし
"""

import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import os

class CSVToSlackDirect:
    """CSVファイルから直接Slackに送信するクラス"""
    
    def __init__(self, slack_webhook_url):
        """
        初期化
        
        Args:
            slack_webhook_url (str): SlackのWebhook URL
        """
        self.webhook_url = slack_webhook_url
        self.jst = pytz.timezone('Asia/Tokyo')
        print("✅ CSV→Slack直接送信システムが準備完了しました")
    
    def read_csv_schedule(self, csv_file, target_date=None):
        """
        CSVファイルから指定日の予定を読み取り
        
        Args:
            csv_file (str): CSVファイルのパス
            target_date (str, optional): 対象日付（YYYY-MM-DD形式）。Noneの場合は今日
        
        Returns:
            list: 予定のリスト
        """
        try:
            # 対象日付を決定
            if target_date is None:
                target_date = datetime.now(self.jst).strftime('%Y-%m-%d')
            
            # CSVファイルの存在確認
            if not os.path.exists(csv_file):
                print(f"❌ CSVファイルが見つかりません: {csv_file}")
                return []
            
            # CSVファイルを読み込み
            df = pd.read_csv(csv_file)
            
            # 指定日のデータを抽出
            day_data = df[df['日付'] == target_date]
            
            if len(day_data) == 0:
                print(f"⚠️  {target_date}のデータがCSVファイルにありません")
                return []
            
            # 予定リストを作成
            schedule_list = []
            for _, row in day_data.iterrows():
                schedule_list.append({
                    'title': f"{row['名前']}: {row['タスク内容']}",
                    'start_time': row['開始時間'],
                    'end_time': row['終了時間']
                })
            
            print(f"✅ {target_date}の予定を{len(schedule_list)}件取得しました")
            return schedule_list
            
        except Exception as e:
            print(f"❌ CSV読み込みエラー: {e}")
            return []
    
    def format_schedule_message(self, schedule_list, target_date=None):
        """
        予定をSlackメッセージ形式にフォーマット
        
        Args:
            schedule_list (list): 予定のリスト
            target_date (str, optional): 対象日付
        
        Returns:
            str: フォーマットされたメッセージ
        """
        if target_date is None:
            target_date = datetime.now(self.jst).strftime('%Y-%m-%d')
        
        # メッセージのヘッダー
        message = f"🌅 おはようございます！\n"
        message += f"📅 {target_date}の予定 📅\n\n"
        
        if not schedule_list:
            message += "📝 今日の予定はありません。\n\n"
            message += "💪 今日も一日頑張りましょう！"
            return message
        
        # 予定を時間順にソート
        sorted_schedule = sorted(schedule_list, key=lambda x: x['start_time'])
        
        # 各予定を追加
        for schedule in sorted_schedule:
            title = schedule['title']
            start_time = schedule['start_time']
            end_time = schedule['end_time']
            
            message += f"🕐 *{start_time}-{end_time}*: {title}\n"
        
        message += "\n💪 今日も一日頑張りましょう！"
        return message
    
    def send_daily_schedule(self, csv_file, target_date=None, channel=None):
        """
        指定日の予定をSlackに送信
        
        Args:
            csv_file (str): CSVファイルのパス
            target_date (str, optional): 対象日付
            channel (str, optional): 送信先チャンネル
        
        Returns:
            bool: 送信成功の可否
        """
        try:
            # CSVファイルから予定を取得
            schedule_list = self.read_csv_schedule(csv_file, target_date)
            
            # メッセージをフォーマット
            message = self.format_schedule_message(schedule_list, target_date)
            
            # Slackに送信
            return self.send_message(message, channel)
            
        except Exception as e:
            print(f"❌ 予定送信エラー: {e}")
            return False
    
    def send_message(self, message, channel=None):
        """
        Slackにメッセージを送信
        
        Args:
            message (str): 送信するメッセージ
            channel (str, optional): 送信先チャンネル
        
        Returns:
            bool: 送信成功の可否
        """
        try:
            # Slack Webhook用のペイロード
            payload = {
                "text": message
            }
            
            # チャンネルが指定されている場合は追加
            if channel:
                payload["channel"] = channel
            
            # Slackに送信
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Slackにメッセージを送信しました")
                return True
            else:
                print(f"❌ Slack送信に失敗しました: {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Slack送信エラー: {e}")
            return False

def main():
    """テスト用のメイン関数"""
    from config import SLACK_WEBHOOK_URL, CSV_FILE, SLACK_CHANNEL
    
    # CSVToSlackDirectを初期化
    slack_sender = CSVToSlackDirect(SLACK_WEBHOOK_URL)
    
    # 今日の予定を送信
    success = slack_sender.send_daily_schedule(
        csv_file=CSV_FILE,
        channel=SLACK_CHANNEL
    )
    
    if success:
        print("✅ 今日の予定が正常に送信されました！")
    else:
        print("❌ 予定の送信に失敗しました")

if __name__ == "__main__":
    main()
