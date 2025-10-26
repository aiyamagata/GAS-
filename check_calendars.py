"""
利用可能なカレンダーを確認するスクリプト
"""

from google_calendar_client import GoogleCalendarClient

def check_available_calendars():
    """利用可能なカレンダーを確認"""
    
    SERVICE_ACCOUNT_FILE = 'rapid-being-472521-a0-d01f438f34a9.json'
    
    try:
        print("Googleカレンダークライアントを初期化中...")
        client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
        
        print("\n=== 利用可能なカレンダーを取得 ===")
        calendars = client.get_calendar_list()
        
        if calendars:
            print(f"✅ {len(calendars)}個のカレンダーが見つかりました！")
            print("\n利用可能なカレンダー:")
            for i, calendar in enumerate(calendars, 1):
                print(f"{i}. カレンダー名: {calendar.get('summary', 'N/A')}")
                print(f"   カレンダーID: {calendar.get('id', 'N/A')}")
                print(f"   説明: {calendar.get('description', 'N/A')}")
                print(f"   アクセスレベル: {calendar.get('accessRole', 'N/A')}")
                print("-" * 50)
        else:
            print("❌ カレンダーが見つかりません。")
            print("\n考えられる原因:")
            print("1. カレンダーがサービスアカウントと共有されていない")
            print("2. サービスアカウントにアクセス権限がない")
            print("3. Google Calendar APIが有効化されていない")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    check_available_calendars()
