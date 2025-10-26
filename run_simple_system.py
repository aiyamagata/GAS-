#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルシステム実行スクリプト
CSVファイルから直接Slack送信（Googleカレンダー連携なし）
"""

import sys
import os
from datetime import datetime

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from csv_direct_slack import CSVToSlackDirect
from simple_auto_scheduler import SimpleAutoScheduler
from config import SLACK_WEBHOOK_URL, CSV_FILE, SLACK_CHANNEL, NOTIFICATION_TIME

class SimpleSystemManager:
    """シンプルシステム管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.slack_sender = CSVToSlackDirect(SLACK_WEBHOOK_URL)
        self.csv_file = CSV_FILE
        self.slack_channel = SLACK_CHANNEL
        self.notification_time = NOTIFICATION_TIME
    
    def show_menu(self):
        """メニューを表示"""
        print("\n" + "=" * 50)
        print("📋 シンプルシステムメニュー")
        print("=" * 50)
        print("1. 今日の予定をSlackに送信（テスト）")
        print("2. 指定日の予定をSlackに送信")
        print("3. 自動スケジューラー開始")
        print("4. システム情報表示")
        print("5. 終了")
        print("=" * 50)
    
    def test_slack_notification(self):
        """Slack通知をテスト"""
        print("\n🧪 Slack通知テスト")
        print("-" * 30)
        
        try:
            success = self.slack_sender.send_daily_schedule(
                csv_file=self.csv_file,
                channel=self.slack_channel
            )
            
            if success:
                print("✅ テスト通知が正常に送信されました！")
            else:
                print("❌ テスト通知の送信に失敗しました")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def send_specific_date(self):
        """指定日の予定を送信"""
        print("\n📅 指定日の予定送信")
        print("-" * 30)
        
        try:
            date_input = input("送信する日付を入力してください (YYYY-MM-DD形式、例: 2025-09-21): ")
            
            # 日付形式をチェック
            datetime.strptime(date_input, '%Y-%m-%d')
            
            success = self.slack_sender.send_daily_schedule(
                csv_file=self.csv_file,
                target_date=date_input,
                channel=self.slack_channel
            )
            
            if success:
                print(f"✅ {date_input}の予定が正常に送信されました！")
            else:
                print(f"❌ {date_input}の予定送信に失敗しました")
                
        except ValueError:
            print("❌ 日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。")
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def start_auto_scheduler(self):
        """自動スケジューラーを開始"""
        print("\n⏰ 自動スケジューラー開始")
        print("-" * 30)
        
        try:
            print(f"📋 設定:")
            print(f"   - 通知時間: {self.notification_time}")
            print(f"   - CSVファイル: {self.csv_file}")
            print(f"   - Slack チャンネル: {self.slack_channel}")
            
            confirm = input("\n自動スケジューラーを開始しますか？ (y/N): ")
            if confirm.lower() != 'y':
                print("❌ 自動スケジューラーの開始をキャンセルしました")
                return
            
            print("\n🚀 自動スケジューラーを開始します...")
            print("💡 Ctrl+C で停止できます")
            
            # 自動スケジューラーを初期化して開始
            scheduler = SimpleAutoScheduler(
                slack_webhook_url=SLACK_WEBHOOK_URL,
                csv_file=self.csv_file,
                channel=self.slack_channel
            )
            
            scheduler.start_daily_scheduler(self.notification_time)
            
        except KeyboardInterrupt:
            print("\n🛑 自動スケジューラーを停止します...")
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def show_system_info(self):
        """システム情報を表示"""
        print("\n📊 システム情報")
        print("-" * 30)
        print(f"📁 CSVファイル: {self.csv_file}")
        print(f"💬 Slack チャンネル: {self.slack_channel}")
        print(f"⏰ 通知時間: {self.notification_time}")
        print(f"🔗 Webhook URL: {SLACK_WEBHOOK_URL[:50]}...")
        
        # CSVファイルの存在確認
        if os.path.exists(self.csv_file):
            print("✅ CSVファイルが存在します")
        else:
            print("❌ CSVファイルが見つかりません")
    
    def run(self):
        """メイン実行"""
        print("🚀 CSV→Slack直接送信システム")
        print("=" * 50)
        print("📋 使用方法:")
        print("1. CSVファイルを準備")
        print("2. メニューから操作を選択")
        print("3. 毎朝自動でSlack通知")
        print("=" * 50)
        
        while True:
            try:
                self.show_menu()
                choice = input("選択してください (1-5): ").strip()
                
                if choice == '1':
                    self.test_slack_notification()
                elif choice == '2':
                    self.send_specific_date()
                elif choice == '3':
                    self.start_auto_scheduler()
                elif choice == '4':
                    self.show_system_info()
                elif choice == '5':
                    print("👋 システムを終了します")
                    break
                else:
                    print("❌ 無効な選択です。1-5の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n👋 システムを終了します")
                break
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")

def main():
    """メイン実行関数"""
    try:
        system = SimpleSystemManager()
        system.run()
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()
