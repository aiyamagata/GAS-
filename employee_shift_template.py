#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
従業員用シフト希望入力テンプレート作成スクリプト
Google Sheets APIを使用してテンプレートを作成
"""

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class EmployeeShiftTemplateCreator:
    """従業員シフト希望テンプレート作成クラス"""
    
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
    
    def create_employee_template(self, employee_id, employee_name, store_name):
        """
        従業員用のシフト希望テンプレートを作成
        
        Args:
            employee_id (str): 従業員ID
            employee_name (str): 従業員名
            store_name (str): 店舗名
            
        Returns:
            str: 作成されたスプレッドシートのID
        """
        try:
            # 新しいスプレッドシートを作成
            spreadsheet_body = {
                'properties': {
                    'title': f'{employee_name} - シフト希望入力 ({store_name})'
                },
                'sheets': [{
                    'properties': {
                        'title': 'request',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 13
                        }
                    }
                }]
            }
            
            # スプレッドシートを作成
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            print(f"✅ スプレッドシートを作成しました: {spreadsheet_id}")
            
            # ヘッダー行を設定
            self._setup_headers(spreadsheet_id)
            
            # データ検証ルールを設定
            self._setup_data_validation(spreadsheet_id)
            
            # 従業員情報を固定値として設定
            self._setup_employee_info(spreadsheet_id, employee_id, employee_name, store_name)
            
            # 条件付き書式を設定
            self._setup_conditional_formatting(spreadsheet_id)
            
            print(f"✅ テンプレートの設定が完了しました")
            print(f"📋 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return spreadsheet_id
            
        except HttpError as e:
            print(f"❌ Google Sheets API エラー: {e}")
            return None
        except Exception as e:
            print(f"❌ テンプレート作成エラー: {e}")
            return None
    
    def _setup_headers(self, spreadsheet_id):
        """ヘッダー行を設定"""
        headers = [
            'employee_id', 'employee_name', 'store', 'role', 'date',
            'start_time', 'end_time', 'break_min', 'shift_type', 'notes',
            'status', 'manager', 'approved_at'
        ]
        
        # ヘッダーを設定
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='request!A1:M1',
            valueInputOption='RAW',
            body={'values': [headers]}
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
                        'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
    
    def _setup_data_validation(self, spreadsheet_id):
        """データ検証ルールを設定"""
        requests = []
        
        # 店舗選択（C列）
        store_validation = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 2,
                'endColumnIndex': 3
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [{'userEnteredValue': '東京'}, {'userEnteredValue': '大阪'}, {'userEnteredValue': '名古屋'}]
                },
                'showCustomUi': True
            }
        }
        requests.append({'setDataValidation': store_validation})
        
        # 役職選択（D列）
        role_validation = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 3,
                'endColumnIndex': 4
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [{'userEnteredValue': '販売'}, {'userEnteredValue': '受付'}, {'userEnteredValue': '事務'}]
                },
                'showCustomUi': True
            }
        }
        requests.append({'setDataValidation': role_validation})
        
        # シフトタイプ選択（I列）
        shift_validation = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 8,
                'endColumnIndex': 9
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [{'userEnteredValue': '通常'}, {'userEnteredValue': '早番'}, {'userEnteredValue': '遅番'}, {'userEnteredValue': '休'}]
                },
                'showCustomUi': True
            }
        }
        requests.append({'setDataValidation': shift_validation})
        
        # ステータス選択（K列）
        status_validation = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 10,
                'endColumnIndex': 11
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [{'userEnteredValue': 'Pending'}, {'userEnteredValue': 'Approved'}, {'userEnteredValue': 'Rejected'}]
                },
                'showCustomUi': True
            }
        }
        requests.append({'setDataValidation': status_validation})
        
        # 日付検証（E列）
        date_validation = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 4,
                'endColumnIndex': 5
            },
            'rule': {
                'condition': {
                    'type': 'DATE_AFTER',
                    'values': [{'userEnteredValue': 'TODAY()'}]
                }
            }
        }
        requests.append({'setDataValidation': date_validation})
        
        # バッチ更新を実行
        if requests:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
    
    def _setup_employee_info(self, spreadsheet_id, employee_id, employee_name, store_name):
        """従業員情報を固定値として設定"""
        # 従業員情報を2行目に設定（テンプレート例）
        employee_data = [
            [employee_id, employee_name, store_name, '販売', '2025-11-01', '10:00', '19:00', '60', '通常', '例：学校行事の都合でこの日だけ早上がり可', 'Pending', '', '']
        ]
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='request!A2:M2',
            valueInputOption='RAW',
            body={'values': employee_data}
        ).execute()
    
    def _setup_conditional_formatting(self, spreadsheet_id):
        """条件付き書式を設定"""
        requests = []
        
        # 土日の日付を薄色表示
        weekend_format = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 4,
                'endColumnIndex': 5
            },
            'booleanRule': {
                'condition': {
                    'type': 'CUSTOM_FORMULA',
                    'values': [{'userEnteredValue': '=OR(WEEKDAY(E2)=1,WEEKDAY(E2)=7)'}]
                },
                'format': {
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                }
            }
        }
        requests.append({'addConditionalFormatRule': weekend_format})
        
        # Rejected行をグレーアウト
        rejected_format = {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 1000,
                'startColumnIndex': 0,
                'endColumnIndex': 13
            },
            'booleanRule': {
                'condition': {
                    'type': 'TEXT_EQ',
                    'values': [{'userEnteredValue': 'Rejected'}]
                },
                'format': {
                    'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                    'textFormat': {'foregroundColor': {'red': 0.5, 'green': 0.5, 'blue': 0.5}}
                }
            }
        }
        requests.append({'addConditionalFormatRule': rejected_format})
        
        # バッチ更新を実行
        if requests:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🏢 従業員シフト希望テンプレート作成システム")
    print("=" * 60)
    
    # 認証ファイルのパス
    credentials_file = 'rapid-being-472521-a0-d01f438f34a9.json'
    
    if not os.path.exists(credentials_file):
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        return
    
    # テンプレート作成器を初期化
    creator = EmployeeShiftTemplateCreator(credentials_file)
    
    if not creator.service:
        print("❌ Google Sheets API の初期化に失敗しました")
        return
    
    # 従業員情報を入力
    print("\n📝 従業員情報を入力してください:")
    employee_id = input("従業員ID: ").strip()
    employee_name = input("従業員名: ").strip()
    store_name = input("店舗名 (東京/大阪/名古屋): ").strip()
    
    if not all([employee_id, employee_name, store_name]):
        print("❌ すべての項目を入力してください")
        return
    
    # テンプレートを作成
    print(f"\n🔄 {employee_name}さんのテンプレートを作成中...")
    spreadsheet_id = creator.create_employee_template(employee_id, employee_name, store_name)
    
    if spreadsheet_id:
        print(f"\n✅ テンプレートの作成が完了しました！")
        print(f"📋 スプレッドシートURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print(f"📋 スプレッドシートID: {spreadsheet_id}")
        print("\n💡 次のステップ:")
        print("1. スプレッドシートの共有権限を従業員に付与")
        print("2. マスター集約シートにスプレッドシートIDを登録")
        print("3. 従業員にシフト希望の入力を依頼")
    else:
        print("❌ テンプレートの作成に失敗しました")

if __name__ == "__main__":
    main()
