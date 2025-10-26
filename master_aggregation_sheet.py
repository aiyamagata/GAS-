#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マスター集約用スプレッドシート作成スクリプト
従業員のシフト希望を集約するためのマスターシートを作成
"""

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class MasterAggregationSheetCreator:
    """マスター集約シート作成クラス"""
    
    def __init__(self, credentials_file):
        """初期化"""
        self.credentials_file = credentials_file
        self.service = self._setup_service()
    
    def _setup_service(self):
        """Google Sheets API サービスを設定"""
        try:
            # 認証情報を読み込み
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive']
            )
            
            # Google Sheets API サービスを構築
            service = build('sheets', 'v4', credentials=creds)
            return service
            
        except Exception as e:
            print(f"❌ 認証エラー: {e}")
            return None
    
    def create_master_sheet(self):
        """
        マスター集約用スプレッドシートを作成
        
        Returns:
            str: 作成されたスプレッドシートのID
        """
        try:
            # 新しいスプレッドシートを作成
            spreadsheet_body = {
                'properties': {
                    'title': 'シフト集約マスター - 自動化システム'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'config',
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'aggregated_shifts',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 15
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'logs',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            # スプレッドシートを作成
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            print(f"✅ マスタースプレッドシートを作成しました: {spreadsheet_id}")
            
            # 各シートの設定
            self._setup_config_sheet(spreadsheet_id)
            self._setup_aggregated_shifts_sheet(spreadsheet_id)
            self._setup_logs_sheet(spreadsheet_id)
            
            print(f"✅ マスターシートの設定が完了しました")
            print(f"📋 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return spreadsheet_id
            
        except HttpError as e:
            print(f"❌ Google Sheets API エラー: {e}")
            return None
        except Exception as e:
            print(f"❌ マスターシート作成エラー: {e}")
            return None
    
    def _setup_config_sheet(self, spreadsheet_id):
        """設定シートをセットアップ"""
        # ヘッダー行
        headers = [
            'employee_id', 'employee_name', 'spreadsheet_id', 'store', 'role',
            'slack_webhook_url', 'notification_time', 'status', 'last_updated', 'notes'
        ]
        
        # ヘッダーを設定
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='config!A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # サンプルデータ
        sample_data = [
            ['EID-001', '山田太郎', '', '東京', '販売', '', '10:00', 'Active', '', ''],
            ['EID-002', '佐藤花子', '', '大阪', '受付', '', '10:00', 'Active', '', ''],
            ['EID-003', '田中一郎', '', '名古屋', '事務', '', '10:00', 'Active', '', '']
        ]
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='config!A2:J4',
            valueInputOption='RAW',
            body={'values': sample_data}
        ).execute()
        
        # ヘッダー行の書式設定
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
    
    def _setup_aggregated_shifts_sheet(self, spreadsheet_id):
        """集約シフトシートをセットアップ"""
        # ヘッダー行
        headers = [
            'date', 'store', 'employee_id', 'employee_name', 'role',
            'start_time', 'end_time', 'break_min', 'shift_type', 'notes',
            'manager', 'approved_at', 'source_spreadsheet_id', 'created_at', 'updated_at'
        ]
        
        # ヘッダーを設定
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='aggregated_shifts!A1:O1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # ヘッダー行の書式設定
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 1,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.8, 'green': 0.4, 'blue': 0.2},
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
    
    def _setup_logs_sheet(self, spreadsheet_id):
        """ログシートをセットアップ"""
        # ヘッダー行
        headers = [
            'timestamp', 'action', 'employee_id', 'status', 'message',
            'spreadsheet_id', 'records_processed', 'error_details', 'execution_time', 'notes'
        ]
        
        # ヘッダーを設定
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='logs!A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # ヘッダー行の書式設定
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 2,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🏢 マスター集約シート作成システム")
    print("=" * 60)
    
    # 認証ファイルのパス
    credentials_file = 'rapid-being-472521-a0-d01f438f34a9.json'
    
    if not os.path.exists(credentials_file):
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        return
    
    # マスターシート作成器を初期化
    creator = MasterAggregationSheetCreator(credentials_file)
    
    if not creator.service:
        print("❌ Google Sheets API の初期化に失敗しました")
        return
    
    # マスターシートを作成
    print("\n🔄 マスター集約シートを作成中...")
    spreadsheet_id = creator.create_master_sheet()
    
    if spreadsheet_id:
        print(f"\n✅ マスターシートの作成が完了しました！")
        print(f"📋 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print(f"📋 スプレッドシートID: {spreadsheet_id}")
        print("\n📝 シート構成:")
        print("- config: 従業員設定とスプレッドシートID管理")
        print("- aggregated_shifts: 集約されたシフトデータ")
        print("- logs: 実行ログとエラー記録")
        print("\n💡 次のステップ:")
        print("1. configシートに従業員のスプレッドシートIDを登録")
        print("2. GASスクリプトをこのスプレッドシートに追加")
        print("3. 自動化のトリガーを設定")
    else:
        print("❌ マスターシートの作成に失敗しました")

if __name__ == "__main__":
    main()
