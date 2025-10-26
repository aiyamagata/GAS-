#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル自動スケジューラー
CSVファイルから直接Slackに送信（Googleカレンダー連携なし）
重複実行防止機能付き
"""

import schedule
import time
import signal
import sys
import os
import psutil
from datetime import datetime
from csv_direct_slack import CSVToSlackDirect

class SimpleAutoScheduler:
    """シンプル自動スケジューリングクラス"""
    
    def __init__(self, slack_webhook_url, csv_file, channel=None):
        """
        初期化
        
        Args:
            slack_webhook_url (str): SlackのWebhook URL
            csv_file (str): CSVファイルのパス
            channel (str, optional): 送信先チャンネル
        """
        self.slack_sender = CSVToSlackDirect(slack_webhook_url)
        self.csv_file = csv_file
        self.channel = channel
        self.pid_file = "scheduler.pid"
        print("✅ シンプル自動スケジューラーが準備完了しました")
    
    def check_existing_processes(self):
        """
        既存のスケジューラープロセスをチェックして停止
        
        Returns:
            bool: 既存プロセスが見つかった場合True
        """
        try:
            # 関連するプロセス名のリスト
            target_processes = [
                'start_auto_scheduler.py',
                'quick_start_scheduler.py', 
                'start_scheduler.py',
                'simple_auto_scheduler.py'
            ]
            
            found_processes = []
            current_pid = os.getpid()
            
            # 全プロセスをチェック
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # 対象プロセスかチェック（自分自身は除く）
                    if any(target in cmdline for target in target_processes) and proc.info['pid'] != current_pid:
                        found_processes.append(proc.info['pid'])
                        print(f"⚠️  既存のスケジューラープロセスを発見: PID {proc.info['pid']}")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 既存プロセスを停止
            if found_processes:
                print(f"🛑 {len(found_processes)}個の既存プロセスを停止します...")
                for pid in found_processes:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ PID {pid} を停止しました")
                    except ProcessLookupError:
                        print(f"⚠️  PID {pid} は既に停止済みです")
                    except PermissionError:
                        print(f"❌ PID {pid} の停止に失敗しました（権限不足）")
                
                # プロセス停止を待つ
                time.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  プロセスチェックエラー: {e}")
            return False
    
    def create_pid_file(self):
        """PIDファイルを作成"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            print(f"📝 PIDファイルを作成しました: {self.pid_file}")
        except Exception as e:
            print(f"⚠️  PIDファイル作成エラー: {e}")
    
    def remove_pid_file(self):
        """PIDファイルを削除"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                print(f"🗑️  PIDファイルを削除しました: {self.pid_file}")
        except Exception as e:
            print(f"⚠️  PIDファイル削除エラー: {e}")
    
    def daily_schedule_job(self):
        """毎朝10時に実行されるジョブ"""
        try:
            print(f"🕙 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 朝10時の自動投稿を開始")
            
            # CSVファイルから今日の予定を取得してSlackに送信
            success = self.slack_sender.send_daily_schedule(
                csv_file=self.csv_file,
                channel=self.channel
            )
            
            if success:
                print("✅ 朝10時の自動投稿が完了しました")
            else:
                print("❌ 朝10時の自動投稿に失敗しました")
                
        except Exception as e:
            print(f"❌ 自動投稿エラー: {e}")
    
    def start_daily_scheduler(self, notification_time="10:00"):
        """
        毎日の自動スケジューリングを開始
        
        Args:
            notification_time (str): 通知時間（HH:MM形式）
        """
        try:
            # 既存プロセスをチェックして停止
            print("🔍 既存のスケジューラープロセスをチェック中...")
            self.check_existing_processes()
            
            # PIDファイルを作成
            self.create_pid_file()
            
            # 既存のスケジュールをクリア
            schedule.clear()
            
            # 毎日のスケジュールを設定
            schedule.every().day.at(notification_time).do(self.daily_schedule_job)
            
            print(f"⏰ 毎日{notification_time}に自動投稿するようにスケジュールを設定しました")
            print("🔄 スケジューラーを開始します...")
            
            # スケジューラーを実行
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
                
        except KeyboardInterrupt:
            print("\n🛑 スケジューラーを停止します...")
        except Exception as e:
            print(f"❌ スケジューラーエラー: {e}")
        finally:
            # PIDファイルを削除
            self.remove_pid_file()

def signal_handler(sig, frame):
    """シグナルハンドラー（Ctrl+Cで終了）"""
    print('\n🛑 自動スケジューラーを停止します...')
    sys.exit(0)

def main():
    """メイン実行関数"""
    from config import SLACK_WEBHOOK_URL, CSV_FILE, SLACK_CHANNEL, NOTIFICATION_TIME
    
    print("=" * 60)
    print("🚀 シンプル自動スケジューラー起動")
    print("=" * 60)
    
    try:
        # 設定確認
        print(f"📋 設定確認:")
        print(f"   - Slack Webhook: {SLACK_WEBHOOK_URL[:50]}...")
        print(f"   - CSVファイル: {CSV_FILE}")
        print(f"   - Slack チャンネル: {SLACK_CHANNEL}")
        print(f"   - 通知時間: {NOTIFICATION_TIME}")
        
        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # シンプル自動スケジューラーを初期化
        print(f"\n⏰ シンプル自動スケジューラーを初期化中...")
        scheduler = SimpleAutoScheduler(
            slack_webhook_url=SLACK_WEBHOOK_URL,
            csv_file=CSV_FILE,
            channel=SLACK_CHANNEL
        )
        
        print("✅ シンプル自動スケジューラーが起動しました")
        print(f"📅 毎朝{NOTIFICATION_TIME}にCSVファイルからSlack通知が送信されます")
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 Ctrl+C で停止できます")
        print("=" * 60)
        
        # スケジューラーを開始
        scheduler.start_daily_scheduler(NOTIFICATION_TIME)
        
    except KeyboardInterrupt:
        print('\n🛑 自動スケジューラーを停止します...')
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
