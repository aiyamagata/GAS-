#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動スケジューラー直接起動スクリプト
"""

import sys
import os
import time
import signal
from datetime import datetime

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_auto_scheduler import SimpleAutoScheduler
from config import SLACK_WEBHOOK_URL, CSV_FILE, SLACK_CHANNEL, NOTIFICATION_TIME

def signal_handler(sig, frame):
    """シグナルハンドラー（Ctrl+Cで終了）"""
    print('\n🛑 自動スケジューラーを停止します...')
    sys.exit(0)

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🚀 自動スケジューラー起動")
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
        print(f"\n⏰ 自動スケジューラーを初期化中...")
        scheduler = SimpleAutoScheduler(
            slack_webhook_url=SLACK_WEBHOOK_URL,
            csv_file=CSV_FILE,
            channel=SLACK_CHANNEL
        )
        
        print("✅ 自動スケジューラーが起動しました")
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
