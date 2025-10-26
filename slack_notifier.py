"""
Slack連携機能
朝10時にその日の予定を自動投稿する
"""

import requests
import json
from datetime import datetime, timedelta
from csv_to_calendar import CSVToCalendarManager

class SlackNotifier:
    """Slack通知を送信するクラス"""
    
    def __init__(self, slack_webhook_url):
        """
        初期化
        
        Args:
            slack_webhook_url (str): SlackのWebhook URL
        """
        self.webhook_url = slack_webhook_url
        print("✅ Slack通知システムが準備完了しました")
    
    def send_message(self, message, channel=None):
        """
        Slackにメッセージを送信
        
        Args:
            message (str): 送信するメッセージ
            channel (str, optional): 送信先チャンネル（例: #general）
            
        Returns:
            bool: 送信成功の場合True
        """
        try:
            # 送信データを準備
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
                return False
                
        except Exception as e:
            print(f"❌ Slack送信エラー: {str(e)}")
            return False
    
    def format_schedule_message(self, schedule_data):
        """
        予定データをSlack用のメッセージに整形
        
        Args:
            schedule_data (list): 予定データのリスト
            
        Returns:
            str: 整形されたメッセージ
        """
        if not schedule_data:
            return "📅 今日の予定はありません。"
        
        # メッセージのヘッダー
        today = datetime.now().strftime('%Y年%m月%d日')
        message = f"🌅 おはようございます！\n📅 *{today}の予定* 📅\n\n"
        
        # 予定を時間順にソート
        sorted_schedule = sorted(schedule_data, key=lambda x: x['start_time'])
        
        # 各予定を追加（修正版：場所表示を削除）
        for schedule in sorted_schedule:
            title = schedule['title']
            start_time = schedule['start_time']
            end_time = schedule['end_time']
            
            # CSVの時間をそのまま表示（場所表示は削除）
            message += f"🕐 *{start_time}-{end_time}*: {title}\n"
        
        # フッター
        message += f"\n💪 今日も一日頑張りましょう！"
        
        return message
    
    def send_daily_schedule(self, schedule_data, channel=None):
        """
        その日の予定をSlackに送信
        
        Args:
            schedule_data (list): 予定データのリスト
            channel (str, optional): 送信先チャンネル
            
        Returns:
            bool: 送信成功の場合True
        """
        message = self.format_schedule_message(schedule_data)
        return self.send_message(message, channel)

class CalendarSlackIntegration:
    """カレンダーとSlackの統合クラス"""
    
    def __init__(self, service_account_file, slack_webhook_url):
        """
        初期化
        
        Args:
            service_account_file (str): Googleサービスアカウントファイルのパス
            slack_webhook_url (str): SlackのWebhook URL
        """
        self.calendar_manager = CSVToCalendarManager(service_account_file)
        self.slack_notifier = SlackNotifier(slack_webhook_url)
        print("✅ カレンダー×Slack統合システムが準備完了しました")
    
    def send_today_schedule_to_slack(self, channel=None):
        """
        今日の予定をSlackに送信
        
        Args:
            channel (str, optional): 送信先チャンネル
            
        Returns:
            bool: 送信成功の場合True
        """
        try:
            # 今日の予定を取得
            print("📅 今日の予定を取得中...")
            today_schedule = self.calendar_manager.get_today_schedule()
            
            if not today_schedule:
                print("ℹ️ 今日の予定はありません")
                return False
            
            # Slackに送信
            print("📤 Slackに送信中...")
            success = self.slack_notifier.send_daily_schedule(today_schedule, channel)
            
            if success:
                print(f"🎉 今日の予定をSlackに送信しました！ ({len(today_schedule)}件の予定)")
            
            return success
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            return False
    
    def import_csv_and_send_notification(self, csv_file_path, channel=None):
        """
        CSVファイルから予定をインポートして、今日の予定をSlackに送信
        
        Args:
            csv_file_path (str): CSVファイルのパス
            channel (str, optional): 送信先チャンネル
            
        Returns:
            bool: 成功の場合True
        """
        try:
            # CSVファイルから予定を作成
            print("📥 CSVファイルから予定をインポート中...")
            created_events = self.calendar_manager.create_events_from_csv(csv_file_path)
            
            if not created_events:
                print("❌ 予定の作成に失敗しました")
                return False
            
            # 今日の予定をSlackに送信
            print("📤 今日の予定をSlackに送信中...")
            success = self.send_today_schedule_to_slack(channel)
            
            return success
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            return False

def main():
    """メイン関数 - 使用例"""
    
    # 設定（実際の値に変更してください）
    SERVICE_ACCOUNT_FILE = 'rapid-being-472521-a0-d01f438f34a9.json'
    SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'  # 実際のWebhook URLに変更
    CSV_FILE_PATH = 'sample_schedule.csv'
    SLACK_CHANNEL = '#general'  # 送信先チャンネル
    
    try:
        # 統合システムを初期化
        integration = CalendarSlackIntegration(SERVICE_ACCOUNT_FILE, SLACK_WEBHOOK_URL)
        
        # オプション1: CSVから予定をインポートしてSlackに送信
        print("=== オプション1: CSVインポート + Slack送信 ===")
        # success = integration.import_csv_and_send_notification(CSV_FILE_PATH, SLACK_CHANNEL)
        
        # オプション2: 今日の予定のみをSlackに送信
        print("=== オプション2: 今日の予定をSlackに送信 ===")
        success = integration.send_today_schedule_to_slack(SLACK_CHANNEL)
        
        if success:
            print("🎉 すべて完了しました！")
        else:
            print("❌ 処理に失敗しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
