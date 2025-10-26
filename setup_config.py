"""
設定変更用スクリプト
実際の運用環境に合わせて設定を変更
"""

def setup_config():
    """設定を変更"""
    
    print("⚙️ システム設定の変更")
    print("=" * 50)
    
    # 現在の設定を読み込み
    try:
        from config import *
        print("📋 現在の設定:")
        print(f"  Slack Webhook URL: {SLACK_WEBHOOK_URL[:50]}...")
        print(f"  Slack チャンネル: {SLACK_CHANNEL}")
        print(f"  CSV ファイル: {CSV_FILE}")
        print(f"  通知時間: {NOTIFICATION_TIME}")
        
    except ImportError:
        print("❌ config.pyが見つかりません")
        return
    
    print("\n🔧 設定を変更しますか？ (y/n): ", end="")
    if input().lower() != 'y':
        print("設定変更をキャンセルしました")
        return
    
    # 新しい設定を入力
    print("\n📝 新しい設定を入力してください:")
    
    new_webhook = input(f"Slack Webhook URL [{SLACK_WEBHOOK_URL}]: ").strip()
    if not new_webhook:
        new_webhook = SLACK_WEBHOOK_URL
    
    new_channel = input(f"Slack チャンネル [{SLACK_CHANNEL}]: ").strip()
    if not new_channel:
        new_channel = SLACK_CHANNEL
    
    new_csv = input(f"CSV ファイル名 [{CSV_FILE}]: ").strip()
    if not new_csv:
        new_csv = CSV_FILE
    
    new_time = input(f"通知時間 [{NOTIFICATION_TIME}]: ").strip()
    if not new_time:
        new_time = NOTIFICATION_TIME
    
    # config.pyを更新
    config_content = f'''"""
設定ファイル
実際の運用環境に合わせて設定を変更してください
"""

# Google Calendar設定
SERVICE_ACCOUNT_FILE = '{SERVICE_ACCOUNT_FILE}'

# Slack設定
SLACK_WEBHOOK_URL = '{new_webhook}'
SLACK_CHANNEL = '{new_channel}'

# CSV設定
CSV_FILE = '{new_csv}'

# スケジュール設定
NOTIFICATION_TIME = "{new_time}"  # 朝の通知時間（24時間表記）

# タイムゾーン設定
TIMEZONE = '{TIMEZONE}'  # 日本時間
'''
    
    try:
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("\n✅ 設定が更新されました！")
        print("📋 新しい設定:")
        print(f"  Slack Webhook URL: {new_webhook[:50]}...")
        print(f"  Slack チャンネル: {new_channel}")
        print(f"  CSV ファイル: {new_csv}")
        print(f"  通知時間: {new_time}")
        
    except Exception as e:
        print(f"❌ 設定の更新に失敗しました: {str(e)}")

if __name__ == "__main__":
    setup_config()
