#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シフト自動化システム セットアップスクリプト
従業員テンプレート作成からマスターシート作成まで一括実行
"""

import os
import json
import time
from employee_shift_template import EmployeeShiftTemplateCreator
from master_aggregation_sheet import MasterAggregationSheetCreator

class ShiftAutomationSetup:
    """シフト自動化システムセットアップクラス"""
    
    def __init__(self, credentials_file):
        """初期化"""
        self.credentials_file = credentials_file
        self.employee_creator = EmployeeShiftTemplateCreator(credentials_file)
        self.master_creator = MasterAggregationSheetCreator(credentials_file)
        self.created_sheets = []
    
    def setup_complete_system(self):
        """完全なシフト自動化システムをセットアップ"""
        print("=" * 80)
        print("🚀 シフト自動化システム 完全セットアップ")
        print("=" * 80)
        
        try:
            # 1. マスターシートを作成
            print("\n📋 ステップ1: マスター集約シートを作成中...")
            master_sheet_id = self.master_creator.create_master_sheet()
            
            if not master_sheet_id:
                print("❌ マスターシートの作成に失敗しました")
                return False
            
            self.created_sheets.append({
                'type': 'master',
                'id': master_sheet_id,
                'name': 'シフト集約マスター',
                'url': f'https://docs.google.com/spreadsheets/d/{master_sheet_id}'
            })
            
            print(f"✅ マスターシートを作成しました: {master_sheet_id}")
            
            # 2. 従業員テンプレートを作成
            print("\n👥 ステップ2: 従業員テンプレートを作成中...")
            employees = self._get_employee_list()
            
            for employee in employees:
                print(f"\n📝 {employee['name']} のテンプレートを作成中...")
                sheet_id = self.employee_creator.create_employee_template(
                    employee['id'],
                    employee['name'],
                    employee['store']
                )
                
                if sheet_id:
                    self.created_sheets.append({
                        'type': 'employee',
                        'id': sheet_id,
                        'name': f"{employee['name']} - シフト希望",
                        'url': f'https://docs.google.com/spreadsheets/d/{sheet_id}',
                        'employee_id': employee['id'],
                        'employee_name': employee['name'],
                        'store': employee['store']
                    })
                    print(f"✅ {employee['name']} のテンプレートを作成しました")
                else:
                    print(f"❌ {employee['name']} のテンプレート作成に失敗しました")
            
            # 3. 設定ファイルを生成
            print("\n⚙️ ステップ3: 設定ファイルを生成中...")
            self._generate_config_file()
            
            # 4. セットアップ完了レポート
            print("\n📊 セットアップ完了レポート")
            print("=" * 80)
            self._print_setup_report()
            
            print("\n🎉 シフト自動化システムのセットアップが完了しました！")
            print("\n📋 次のステップ:")
            print("1. マスターシートのconfigシートに従業員のスプレッドシートIDを登録")
            print("2. マスターシートにGASスクリプトを追加")
            print("3. プロパティを設定（Slack Webhook URL等）")
            print("4. 自動化のトリガーを設定")
            print("5. 従業員にシフト希望入力の依頼")
            
            return True
            
        except Exception as e:
            print(f"❌ セットアップ中にエラーが発生しました: {e}")
            return False
    
    def _get_employee_list(self):
        """従業員リストを取得（実際の運用では外部ファイルやDBから取得）"""
        # サンプル従業員データ
        employees = [
            {'id': 'EID-001', 'name': '山田太郎', 'store': '東京'},
            {'id': 'EID-002', 'name': '佐藤花子', 'store': '大阪'},
            {'id': 'EID-003', 'name': '田中一郎', 'store': '名古屋'},
            {'id': 'EID-004', 'name': '鈴木次郎', 'store': '東京'},
            {'id': 'EID-005', 'name': '高橋三郎', 'store': '大阪'}
        ]
        
        print(f"📋 {len(employees)}名の従業員テンプレートを作成します")
        return employees
    
    def _generate_config_file(self):
        """設定ファイルを生成"""
        config = {
            'master_sheet_id': self.created_sheets[0]['id'],
            'employees': [
                {
                    'employee_id': sheet['employee_id'],
                    'employee_name': sheet['employee_name'],
                    'spreadsheet_id': sheet['id'],
                    'store': sheet['store']
                }
                for sheet in self.created_sheets[1:]  # マスターシート以外
            ],
            'slack_settings': {
                'webhook_url': 'https://hooks.slack.com/services/YOUR_WEBHOOK_URL',
                'channel': '#リモートチーム勤怠報告'
            },
            'drive_settings': {
                'folder_id': 'YOUR_DRIVE_FOLDER_ID'  # 任意
            },
            'schedule_settings': {
                'notification_time': '10:00',
                'timezone': 'Asia/Tokyo'
            }
        }
        
        # 設定ファイルを保存
        with open('shift_automation_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 設定ファイルを生成しました: shift_automation_config.json")
    
    def _print_setup_report(self):
        """セットアップレポートを表示"""
        print(f"📊 作成されたスプレッドシート: {len(self.created_sheets)}件")
        print()
        
        for i, sheet in enumerate(self.created_sheets, 1):
            print(f"{i}. {sheet['name']}")
            print(f"   📋 ID: {sheet['id']}")
            print(f"   🔗 URL: {sheet['url']}")
            if sheet['type'] == 'employee':
                print(f"   👤 従業員: {sheet['employee_name']} ({sheet['employee_id']})")
                print(f"   🏪 店舗: {sheet['store']}")
            print()
    
    def create_employee_template_manual(self):
        """手動で従業員テンプレートを作成"""
        print("=" * 60)
        print("👤 従業員テンプレート手動作成")
        print("=" * 60)
        
        while True:
            print("\n📝 従業員情報を入力してください:")
            employee_id = input("従業員ID (終了する場合は 'quit'): ").strip()
            
            if employee_id.lower() == 'quit':
                break
            
            employee_name = input("従業員名: ").strip()
            store_name = input("店舗名 (東京/大阪/名古屋): ").strip()
            
            if not all([employee_id, employee_name, store_name]):
                print("❌ すべての項目を入力してください")
                continue
            
            print(f"\n🔄 {employee_name} のテンプレートを作成中...")
            sheet_id = self.employee_creator.create_employee_template(
                employee_id, employee_name, store_name
            )
            
            if sheet_id:
                print(f"✅ テンプレートを作成しました: {sheet_id}")
                self.created_sheets.append({
                    'type': 'employee',
                    'id': sheet_id,
                    'name': f"{employee_name} - シフト希望",
                    'url': f'https://docs.google.com/spreadsheets/d/{sheet_id}',
                    'employee_id': employee_id,
                    'employee_name': employee_name,
                    'store': store_name
                })
            else:
                print("❌ テンプレートの作成に失敗しました")

def main():
    """メイン実行関数"""
    print("🏢 シフト自動化システム セットアップ")
    print("=" * 60)
    
    # 認証ファイルのパス
    credentials_file = 'rapid-being-472521-a0-d01f438f34a9.json'
    
    if not os.path.exists(credentials_file):
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        print("💡 Google Cloud Console でサービスアカウントキーをダウンロードしてください")
        return
    
    # セットアップを初期化
    setup = ShiftAutomationSetup(credentials_file)
    
    print("\n🚀 完全自動セットアップを開始します...")
    print("📋 以下の処理を実行します:")
    print("1. マスター集約シートの作成")
    print("2. 従業員テンプレートの作成（5名分）")
    print("3. 設定ファイルの生成")
    
    # 完全自動セットアップを実行
    success = setup.setup_complete_system()
    
    if success:
        print("\n🎉 セットアップが完了しました！")
    else:
        print("\n❌ セットアップに失敗しました")

if __name__ == "__main__":
    main()
