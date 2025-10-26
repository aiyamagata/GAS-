"""
GoogleカレンダーAPI 自動化活用例
"""

from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta
import json
import random

def automation_examples():
    """自動化活用例を実行"""
    
    SERVICE_ACCOUNT_FILE = 'rapid-being-472521-a0-d01f438f34a9.json'
    client = GoogleCalendarClient(SERVICE_ACCOUNT_FILE)
    
    print("=== GoogleカレンダーAPI 自動化活用例 ===\n")
    
    # 1. 自動スケジュール調整
    print("1. 自動スケジュール調整")
    auto_schedule_adjustment(client)
    
    # 2. チーム予定の自動同期
    print("\n2. チーム予定の自動同期")
    team_schedule_sync(client)
    
    # 3. スマートリマインダー
    print("\n3. スマートリマインダー")
    smart_reminders(client)
    
    # 4. 予定の自動分類
    print("\n4. 予定の自動分類")
    auto_categorize_events(client)

def auto_schedule_adjustment(client):
    """自動スケジュール調整"""
    try:
        # 例: 会議の自動調整
        meetings = [
            {"title": "プロジェクトA進捗会議", "duration": 60, "priority": "high"},
            {"title": "プロジェクトB計画会議", "duration": 90, "priority": "medium"},
            {"title": "チーム定例会議", "duration": 45, "priority": "low"},
            {"title": "クライアント打ち合わせ", "duration": 120, "priority": "high"}
        ]
        
        # 優先度に基づいてスケジュールを自動調整
        current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for meeting in meetings:
            # 優先度に応じて時間を調整
            if meeting["priority"] == "high":
                start_time = current_time
            elif meeting["priority"] == "medium":
                start_time = current_time + timedelta(hours=1)
            else:
                start_time = current_time + timedelta(hours=2)
            
            end_time = start_time + timedelta(minutes=meeting["duration"])
            
            event = client.create_event(
                summary=f"🔴 {meeting['title']}" if meeting["priority"] == "high" else 
                       f"🟡 {meeting['title']}" if meeting["priority"] == "medium" else 
                       f"🟢 {meeting['title']}",
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat(),
                description=f"優先度: {meeting['priority']}, 自動調整済み"
            )
            
            current_time = end_time + timedelta(minutes=15)  # 15分の間隔
            print(f"✅ 自動調整済み予定: {meeting['title']} (優先度: {meeting['priority']})")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def team_schedule_sync(client):
    """チーム予定の自動同期"""
    try:
        # チームメンバーの予定をシミュレート
        team_members = ["田中さん", "佐藤さん", "鈴木さん", "高橋さん"]
        
        for member in team_members:
            # 各メンバーの予定を作成
            member_events = [
                {"title": f"{member} - 朝の作業", "time": 9, "duration": 120},
                {"title": f"{member} - チームミーティング", "time": 11, "duration": 60},
                {"title": f"{member} - 個別作業", "time": 14, "duration": 180},
                {"title": f"{member} - 夕方の報告", "time": 17, "duration": 30}
            ]
            
            for event_data in member_events:
                start_time = datetime.now().replace(hour=event_data["time"], minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=event_data["duration"])
                
                event = client.create_event(
                    summary=event_data["title"],
                    start_datetime=start_time.isoformat(),
                    end_datetime=end_time.isoformat(),
                    description=f"チーム同期: {member}の予定"
                )
            
            print(f"✅ {member}の予定を同期しました")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def smart_reminders(client):
    """スマートリマインダー"""
    try:
        # 予定の種類に応じたリマインダーを自動設定
        smart_events = [
            {
                "title": "重要なプレゼンテーション",
                "type": "presentation",
                "prep_time": 60  # 準備時間（分）
            },
            {
                "title": "クライアントとの打ち合わせ",
                "type": "client_meeting",
                "prep_time": 30
            },
            {
                "title": "プロジェクト締切",
                "type": "deadline",
                "prep_time": 0
            },
            {
                "title": "研修参加",
                "type": "training",
                "prep_time": 15
            }
        ]
        
        for event_data in smart_events:
            start_time = datetime.now() + timedelta(hours=2)
            end_time = start_time + timedelta(hours=1)
            
            # 予定の種類に応じたリマインダーを設定
            reminder_minutes = []
            
            if event_data["type"] == "presentation":
                reminder_minutes = [1440, 60, 15]  # 1日前、1時間前、15分前
            elif event_data["type"] == "client_meeting":
                reminder_minutes = [1440, 30, 5]  # 1日前、30分前、5分前
            elif event_data["type"] == "deadline":
                reminder_minutes = [2880, 1440, 240]  # 2日前、1日前、4時間前
            elif event_data["type"] == "training":
                reminder_minutes = [60, 10]  # 1時間前、10分前
            
            # 準備時間の予定も追加
            if event_data["prep_time"] > 0:
                prep_start = start_time - timedelta(minutes=event_data["prep_time"])
                prep_end = start_time
                
                prep_event = client.create_event(
                    summary=f"🔧 {event_data['title']} - 準備時間",
                    start_datetime=prep_start.isoformat(),
                    end_datetime=prep_end.isoformat(),
                    description=f"準備時間: {event_data['prep_time']}分"
                )
                print(f"✅ 準備時間を追加: {event_data['title']}")
            
            # メイン予定を作成
            event = {
                'summary': f"📅 {event_data['title']}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'description': f"種類: {event_data['type']}, スマートリマインダー設定済み",
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': minutes} for minutes in reminder_minutes
                    ]
                }
            }
            
            created_event = client.service.events().insert(
                calendarId=client.calendar_id,
                body=event
            ).execute()
            
            print(f"✅ スマートリマインダー付き予定: {event_data['title']}")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

def auto_categorize_events(client):
    """予定の自動分類"""
    try:
        # 予定を自動的に分類して色分け
        categorized_events = [
            {"title": "重要会議", "category": "meeting", "color": "red"},
            {"title": "個人作業", "category": "work", "color": "blue"},
            {"title": "休暇", "category": "vacation", "color": "green"},
            {"title": "研修", "category": "learning", "color": "purple"},
            {"title": "プロジェクト作業", "category": "project", "color": "orange"}
        ]
        
        # 色のマッピング
        color_mapping = {
            "red": "1",
            "blue": "2", 
            "green": "3",
            "purple": "4",
            "orange": "5"
        }
        
        for event_data in categorized_events:
            start_time = datetime.now() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
            
            event = {
                'summary': f"🏷️ {event_data['title']}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'description': f"自動分類: {event_data['category']}",
                'colorId': color_mapping.get(event_data['color'], '1')
            }
            
            created_event = client.service.events().insert(
                calendarId=client.calendar_id,
                body=event
            ).execute()
            
            print(f"✅ 自動分類済み予定: {event_data['title']} ({event_data['category']})")
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

if __name__ == "__main__":
    automation_examples()
