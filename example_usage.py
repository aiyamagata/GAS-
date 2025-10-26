"""
GoogleカレンダーAPIの使用例
"""

from datetime import datetime, timedelta
from google_calendar_client import GoogleCalendarClient


def main():
    """メイン関数 - 使用例の実行"""
    
    # 設定
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-key.json'  # サービスアカウントファイルのパス
    CALENDAR_ID = 'primary'  # 使用するカレンダーID（'primary'はデフォルトのカレンダー）
    
    try:
        # クライアントを初期化
        print("Googleカレンダークライアントを初期化中...")
        client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE, CALENDAR_ID)
        
        # 1. カレンダーリストを取得
        print("\n=== 利用可能なカレンダーリスト ===")
        calendars = client.get_calendar_list()
        
        # 2. 通常の予定を作成
        print("\n=== 通常の予定を作成 ===")
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        event = client.create_event(
            summary="会議",
            start_datetime=start_time.isoformat(),
            end_datetime=end_time.isoformat(),
            description="プロジェクトの進捗確認会議",
            location="会議室A",
            attendees=["example1@company.com", "example2@company.com"]
        )
        
        # 3. 終日予定を作成
        print("\n=== 終日予定を作成 ===")
        tomorrow = datetime.now() + timedelta(days=1)
        all_day_event = client.create_all_day_event(
            summary="休暇",
            date=tomorrow.strftime('%Y-%m-%d'),
            description="有給休暇",
            location="自宅"
        )
        
        # 4. 予定を取得
        print("\n=== 今後の予定を取得 ===")
        time_min = datetime.now().isoformat()
        time_max = (datetime.now() + timedelta(days=7)).isoformat()
        
        events = client.get_events(
            time_min=time_min,
            time_max=time_max,
            max_results=5
        )
        
        for event in events:
            print(f"- {event.get('summary')}: {event.get('start').get('dateTime', event.get('start').get('date'))}")
        
        # 5. 特定の予定を削除（オプション）
        # print("\n=== 予定を削除 ===")
        # client.delete_event(event.get('id'))
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")


def create_sample_events():
    """サンプル予定を作成する関数"""
    
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-key.json'
    client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
    
    # 複数のサンプル予定を作成
    sample_events = [
        {
            'summary': '朝のミーティング',
            'start': datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
            'end': datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
            'description': '日次スタンドアップミーティング',
            'location': '会議室B'
        },
        {
            'summary': 'ランチミーティング',
            'start': datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),
            'end': datetime.now().replace(hour=13, minute=0, second=0, microsecond=0),
            'description': 'クライアントとの打ち合わせ',
            'location': 'レストラン'
        },
        {
            'summary': 'プロジェクトレビュー',
            'start': datetime.now().replace(hour=15, minute=0, second=0, microsecond=0),
            'end': datetime.now().replace(hour=16, minute=30, second=0, microsecond=0),
            'description': '四半期プロジェクトレビュー会議',
            'location': '会議室C'
        }
    ]
    
    for event_data in sample_events:
        try:
            event = client.create_event(
                summary=event_data['summary'],
                start_datetime=event_data['start'].isoformat(),
                end_datetime=event_data['end'].isoformat(),
                description=event_data['description'],
                location=event_data['location']
            )
            print(f"予定を作成しました: {event_data['summary']}")
        except Exception as e:
            print(f"予定の作成に失敗しました ({event_data['summary']}): {str(e)}")


def create_recurring_events():
    """繰り返し予定を作成する関数"""
    
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-key.json'
    client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
    
    # 毎週の定例会議
    start_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # 繰り返しルールを設定
    recurring_event = {
        'summary': '週次定例会議',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'description': '毎週の定例会議',
        'location': '会議室A',
        'recurrence': [
            'RRULE:FREQ=WEEKLY;BYDAY=MO'  # 毎週月曜日
        ]
    }
    
    try:
        created_event = client.service.events().insert(
            calendarId=client.calendar_id,
            body=recurring_event
        ).execute()
        print(f"繰り返し予定を作成しました: {created_event.get('summary')}")
    except Exception as e:
        print(f"繰り返し予定の作成に失敗しました: {str(e)}")


if __name__ == "__main__":
    # メインの使用例を実行
    main()
    
    # 追加の例を実行したい場合は以下のコメントを外してください
    # create_sample_events()
    # create_recurring_events()
