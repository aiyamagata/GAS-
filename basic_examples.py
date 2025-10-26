"""
GoogleカレンダーAPIの基本的な活用例
"""

from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

def basic_examples():
    """基本的な活用例を実行"""
    
    SERVICE_ACCOUNT_FILE = 'rapid-being-472521-a0-d01f438f34a9.json'
    client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
    
    print("=== GoogleカレンダーAPI 基本的な活用例 ===\n")
    
    # 1. 定期的な会議の登録
    print("1. 定期的な会議の登録")
    create_weekly_meeting(client)
    
    # 2. 今日のタスクを予定として追加
    print("\n2. 今日のタスクを予定として追加")
    create_daily_tasks(client)
    
    # 3. 休暇申請の自動登録
    print("\n3. 休暇申請の自動登録")
    create_vacation_request(client)
    
    # 4. プロジェクトのマイルストーン
    print("\n4. プロジェクトのマイルストーン")
    create_project_milestones(client)

def create_weekly_meeting(client):
    """週次の定例会議を作成"""
    try:
        # 来週月曜日の10:00-11:00に定例会議
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()) % 7)
        start_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
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
            'description': '毎週のプロジェクト進捗確認と今後の予定について話し合います',
            'location': '会議室A',
            'recurrence': [
                'RRULE:FREQ=WEEKLY;BYDAY=MO'  # 毎週月曜日
            ]
        }
        
        created_event = client.service.events().insert(
            calendarId=client.calendar_id,
            body=recurring_event
        ).execute()
        
        print(f"✅ 週次定例会議を作成しました: {created_event.get('summary')}")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def create_daily_tasks(client):
    """今日のタスクを予定として追加"""
    try:
        # 明日の日付を使用（今日だと過去の時刻になってしまうため）
        tomorrow = datetime.now() + timedelta(days=1)
        tasks = [
            {"title": "メール確認", "time": 9, "duration": 30},
            {"title": "プロジェクト進捗確認", "time": 11, "duration": 60},
            {"title": "資料作成", "time": 14, "duration": 120},
            {"title": "明日の準備", "time": 17, "duration": 30}
        ]
        
        for task in tasks:
            start_time = tomorrow.replace(hour=task["time"], minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=task["duration"])
            
            event = client.create_event(
                summary=task["title"],
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat(),
                description=f"明日のタスク: {task['title']}"
            )
            print(f"✅ タスクを追加: {task['title']} ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')})")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def create_vacation_request(client):
    """休暇申請の自動登録"""
    try:
        # 来週の金曜日を休暇として申請
        vacation_date = datetime.now() + timedelta(days=7)
        vacation_date = vacation_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        event = client.create_all_day_event(
            summary="有給休暇申請",
            date=vacation_date.strftime('%Y-%m-%d'),
            description="私用のため休暇をいただきます",
            location="自宅"
        )
        print(f"✅ 休暇申請を登録しました: {vacation_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def create_project_milestones(client):
    """プロジェクトのマイルストーンを作成"""
    try:
        milestones = [
            {"title": "要件定義完了", "days": 3},
            {"title": "設計書作成完了", "days": 7},
            {"title": "開発開始", "days": 10},
            {"title": "テスト開始", "days": 20},
            {"title": "リリース", "days": 30}
        ]
        
        for milestone in milestones:
            milestone_date = datetime.now() + timedelta(days=milestone["days"])
            
            event = client.create_all_day_event(
                summary=f"【マイルストーン】{milestone['title']}",
                date=milestone_date.strftime('%Y-%m-%d'),
                description=f"プロジェクトマイルストーン: {milestone['title']}"
            )
            print(f"✅ マイルストーンを追加: {milestone['title']}")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

if __name__ == "__main__":
    basic_examples()
