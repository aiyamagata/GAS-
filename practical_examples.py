"""
実用的なGoogleカレンダーAPI活用例
"""

from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta
import json

def practical_examples():
    """実用的な活用例を実行"""
    
    SERVICE_ACCOUNT_FILE = 'rapid-being-472521-a0-d01f438f34a9.json'
    client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
    
    print("=== GoogleカレンダーAPI 実用的な活用例 ===\n")
    
    # 1. CSVファイルから予定を一括登録
    print("1. CSVファイルから予定を一括登録")
    import_from_csv(client)
    
    # 2. 他のシステムとの連携
    print("\n2. 他のシステムとの連携")
    integrate_with_other_systems(client)
    
    # 3. 自動リマインダー機能
    print("\n3. 自動リマインダー機能")
    create_reminders(client)
    
    # 4. カレンダー分析
    print("\n4. カレンダー分析")
    analyze_calendar(client)

def import_from_csv(client):
    """CSVファイルから予定を一括登録"""
    try:
        # サンプルデータ（実際にはCSVファイルから読み込み）
        sample_events = [
            {"title": "顧客Aとの打ち合わせ", "date": "2024-09-25", "time": "14:00", "duration": 60},
            {"title": "チームミーティング", "date": "2024-09-26", "time": "10:00", "duration": 90},
            {"title": "プロジェクトレビュー", "date": "2024-09-27", "time": "15:30", "duration": 120},
            {"title": "研修参加", "date": "2024-09-28", "time": "09:00", "duration": 480}
        ]
        
        for event_data in sample_events:
            # 日時を結合
            start_datetime = f"{event_data['date']}T{event_data['time']}:00"
            end_datetime = f"{event_data['date']}T{event_data['time']}:00"
            
            # 終了時間を計算
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
            end_dt = start_dt + timedelta(minutes=event_data['duration'])
            end_datetime = end_dt.isoformat()
            
            event = client.create_event(
                summary=event_data['title'],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description=f"CSVから一括登録: {event_data['title']}"
            )
            print(f"✅ 予定を登録: {event_data['title']}")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def integrate_with_other_systems(client):
    """他のシステムとの連携例"""
    try:
        # 例1: Slack通知のための予定作成
        slack_events = [
            {"title": "🔔 朝のスタンドアップ", "time": 9, "channel": "#daily-standup"},
            {"title": "📊 週次レポート提出", "time": 17, "channel": "#reports"},
            {"title": "🎉 チームビルディング", "time": 18, "channel": "#team-events"}
        ]
        
        for event_data in slack_events:
            start_time = datetime.now().replace(hour=event_data["time"], minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            event = client.create_event(
                summary=event_data["title"],
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat(),
                description=f"Slack通知対象: {event_data['channel']}"
            )
            print(f"✅ Slack連携予定を作成: {event_data['title']}")
            
        # 例2: 外部APIからの予定同期（サンプル）
        external_events = [
            {"title": "📅 外部システム同期テスト", "source": "CRM System"},
            {"title": "🔄 データ同期", "source": "Database System"}
        ]
        
        for event_data in external_events:
            start_time = datetime.now() + timedelta(hours=2)
            end_time = start_time + timedelta(minutes=30)
            
            event = client.create_event(
                summary=event_data["title"],
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat(),
                description=f"外部システムからの同期: {event_data['source']}"
            )
            print(f"✅ 外部システム連携予定を作成: {event_data['title']}")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def create_reminders(client):
    """自動リマインダー機能"""
    try:
        # 重要な予定の前にリマインダーを設定
        important_events = [
            {"title": "重要なプレゼンテーション", "reminder_hours": [24, 2, 0.5]},  # 1日前、2時間前、30分前
            {"title": "締切プロジェクト", "reminder_hours": [48, 24, 4]},  # 2日前、1日前、4時間前
            {"title": "会議準備", "reminder_hours": [1]}  # 1時間前
        ]
        
        for event_data in important_events:
            start_time = datetime.now() + timedelta(hours=3)
            end_time = start_time + timedelta(hours=1)
            
            # リマインダー設定を含む予定を作成
            event = {
                'summary': event_data['title'],
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'description': f"重要な予定: {event_data['title']}",
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': int(reminder * 60)} for reminder in event_data['reminder_hours']
                    ]
                }
            }
            
            created_event = client.service.events().insert(
                calendarId=client.calendar_id,
                body=event
            ).execute()
            
            print(f"✅ リマインダー付き予定を作成: {event_data['title']}")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def analyze_calendar(client):
    """カレンダー分析"""
    try:
        # 今月の予定を取得（ISO形式で正しくフォーマット）
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = start_of_month + timedelta(days=31)
        
        # ISO形式で正しくフォーマット
        time_min = start_of_month.isoformat() + '+09:00'  # 日本時間を明示
        time_max = end_of_month.isoformat() + '+09:00'
        
        events = client.get_events(
            time_min=time_min,
            time_max=time_max,
            max_results=100
        )
        
        print(f"📊 今月の予定分析:")
        print(f"   総予定数: {len(events)}")
        
        # 予定の種類別集計
        event_types = {}
        total_duration = 0
        
        for event in events:
            summary = event.get('summary', 'Untitled')
            
            # 予定の種類を判定（簡単な例）
            if '会議' in summary or 'ミーティング' in summary:
                event_type = '会議'
            elif '休暇' in summary or '休み' in summary:
                event_type = '休暇'
            elif '作業' in summary or 'タスク' in summary:
                event_type = '作業'
            else:
                event_type = 'その他'
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # 時間を計算
            start = event.get('start', {})
            end = event.get('end', {})
            
            if 'dateTime' in start and 'dateTime' in end:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds() / 3600  # 時間
                total_duration += duration
        
        print(f"   総時間: {total_duration:.1f}時間")
        print(f"   予定の種類別:")
        for event_type, count in event_types.items():
            print(f"     {event_type}: {count}件")
        
        # 忙しい日を特定
        busy_days = {}
        for event in events:
            start = event.get('start', {})
            if 'dateTime' in start:
                date = start['dateTime'][:10]  # YYYY-MM-DD
                busy_days[date] = busy_days.get(date, 0) + 1
        
        if busy_days:
            busiest_day = max(busy_days, key=busy_days.get)
            print(f"   最も忙しい日: {busiest_day} ({busy_days[busiest_day]}件)")
        
    except Exception as e:
        print(f"❌ カレンダー分析エラー: {str(e)}")
        print("   分析をスキップして続行します...")

if __name__ == "__main__":
    practical_examples()
