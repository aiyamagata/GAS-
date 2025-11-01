/**
 * シフト集約自動化システム - Google Apps Script
 * 複数の従業員シートからシフト希望を集約してSlackに投稿
 */

// ===== 設定値（プロパティから取得） =====
function getProp_(key, required = true) {
  const v = PropertiesService.getScriptProperties().getProperty(key);
  if (required && !v) throw new Error(`Missing property: ${key}`);
  return v;
}

// ===== メイン実行関数 =====
function aggregateShiftsAndPostToSlack() {
  const startTime = new Date();
  let logData = {
    timestamp: Utilities.formatDate(startTime, 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss'),
    action: 'aggregate_shifts',
    status: 'started',
    records_processed: 0,
    error_details: '',
    execution_time: 0
  };
  
  try {
    console.log('🚀 シフト集約処理を開始します...');
    
    // 1. 設定シートから従業員情報を取得
    const configData = getConfigData_();
    console.log(`📋 ${configData.length}名の従業員設定を取得しました`);
    
    // 2. 各従業員シートからシフトデータを集約
    const allShifts = [];
    let processedEmployees = 0;
    
    for (const employee of configData) {
      if (employee.status !== 'Active' || !employee.spreadsheet_id) {
        console.log(`⏭️ ${employee.employee_name} はスキップします（非アクティブまたはスプレッドシートID未設定）`);
        continue;
      }
      
      try {
        console.log(`📥 ${employee.employee_name} のシフトデータを取得中...`);
        const shifts = getEmployeeShifts_(employee.spreadsheet_id, employee.employee_id);
        
        if (shifts.length > 0) {
          allShifts.push(...shifts);
          console.log(`✅ ${employee.employee_name}: ${shifts.length}件のシフトを取得`);
        } else {
          console.log(`ℹ️ ${employee.employee_name}: シフトデータなし`);
        }
        
        processedEmployees++;
        
      } catch (error) {
        console.error(`❌ ${employee.employee_name} のデータ取得エラー:`, error);
        logData.error_details += `${employee.employee_name}: ${error.message}; `;
      }
    }
    
    console.log(`📊 合計 ${allShifts.length}件のシフトデータを集約しました`);
    
    // 3. 集約データをマスターシートに保存
    if (allShifts.length > 0) {
      saveAggregatedShifts_(allShifts);
      console.log('💾 集約データをマスターシートに保存しました');
    }
    
    // 4. CSVファイルを作成してGoogleドライブに保存
    const csvBlob = createCsvBlob_(allShifts);
    const driveFile = saveToDrive_(csvBlob);
    console.log(`📁 CSVファイルをドライブに保存しました: ${driveFile.getName()}`);
    
    // 5. Slackに投稿
    const slackMessage = createSlackMessage_(allShifts, driveFile.getUrl());
    postToSlack_(slackMessage);
    console.log('📤 Slackに投稿しました');
    
    // 6. ログを記録
    logData.status = 'success';
    logData.records_processed = allShifts.length;
    logData.execution_time = new Date() - startTime;
    saveLog_(logData);
    
    console.log('✅ シフト集約処理が完了しました');
    
  } catch (error) {
    console.error('❌ シフト集約処理でエラーが発生しました:', error);
    
    logData.status = 'error';
    logData.error_details = error.message;
    logData.execution_time = new Date() - startTime;
    saveLog_(logData);
    
    // エラー通知をSlackに送信
    const errorMessage = `🚨 シフト集約処理でエラーが発生しました\n\`\`\`${error.message}\`\`\``;
    postToSlack_(errorMessage);
  }
}

// ===== 設定データ取得 =====
function getConfigData_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const configSheet = ss.getSheetByName('config');
  
  if (!configSheet) {
    throw new Error('configシートが見つかりません');
  }
  
  const data = configSheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);
  
  return rows.map(row => {
    const obj = {};
    headers.forEach((header, index) => {
      obj[header] = row[index];
    });
    return obj;
  }).filter(row => row.employee_id); // 空行を除外
}

// ===== 従業員シフトデータ取得 =====
function getEmployeeShifts_(spreadsheetId, employeeId) {
  try {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const requestSheet = ss.getSheetByName('request');
    
    if (!requestSheet) {
      throw new Error('requestシートが見つかりません');
    }
    
    const data = requestSheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1);
    
    const shifts = [];
    
    for (const row of rows) {
      if (!row[0]) continue; // 空行をスキップ
      
      const shift = {};
      headers.forEach((header, index) => {
        shift[header] = row[index];
      });
      
      // 承認済みのシフトのみを対象
      if (shift.status === '承認') {
        shifts.push(shift);
      }
    }
    
    return shifts;
    
  } catch (error) {
    console.error(`従業員シート取得エラー (${spreadsheetId}):`, error);
    throw error;
  }
}

// ===== 集約データをマスターシートに保存 =====
function saveAggregatedShifts_(shifts) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const aggregatedSheet = ss.getSheetByName('aggregated_shifts');
  
  if (!aggregatedSheet) {
    throw new Error('aggregated_shiftsシートが見つかりません');
  }
  
  // 既存データをクリア
  aggregatedSheet.clear();
  
  // ヘッダーを設定
  const headers = [
    'date', 'store', 'employee_id', 'employee_name', 'role',
    'start_time', 'end_time', 'break_hour', 'total_hour', 'shift_type', 'work_content', 'notes',
    'manager', 'approved_at', 'source_spreadsheet_id', 'created_at', 'updated_at'
  ];
  
  aggregatedSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // データを追加
  if (shifts.length > 0) {
    const now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');
    
    const data = shifts.map(shift => {
      // 総労働時間を計算（start_time, end_time, break_hourから）
      const totalHour = calculateTotalHour_(shift.start_time, shift.end_time, shift.break_hour);
      
      return [
        shift.date,
        shift.store,
        shift.employee_id,
        shift.employee_name,
        shift.role,
        shift.start_time,
        shift.end_time,
        shift.break_hour || '', // break_hour（時間）
        totalHour, // total_hour（計算値）
        shift.shift_type,
        shift.work_content || '', // work_content
        shift.notes,
        shift.manager,
        shift.approved_at,
        '', // source_spreadsheet_id
        now, // created_at
        now  // updated_at
      ];
    });
    
    aggregatedSheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
}

// ===== 総労働時間を計算 =====
function calculateTotalHour_(startTime, endTime, breakHour) {
  try {
    // 時間文字列（HH:MM形式）を分に変換
    const startMinutes = timeToMinutes_(startTime);
    const endMinutes = timeToMinutes_(endTime);
    
    // 休憩時間を分に変換（break_hourが時間単位の場合）
    const breakMinutes = parseFloat(breakHour) * 60 || 0;
    
    // 総労働時間を計算（分）
    const totalMinutes = endMinutes - startMinutes - breakMinutes;
    
    // 時間に変換（小数点以下2桁まで）
    const totalHour = (totalMinutes / 60).toFixed(2);
    
    return totalHour;
  } catch (error) {
    console.error('総労働時間計算エラー:', error);
    return '';
  }
}

// ===== 時間文字列を分に変換 =====
function timeToMinutes_(timeString) {
  const parts = timeString.split(':');
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1] || 0, 10);
  return hours * 60 + minutes;
}

// ===== CSVファイル作成 =====
function createCsvBlob_(shifts) {
  if (shifts.length === 0) {
    return Utilities.newBlob('日付,店舗,従業員ID,従業員名,役職,開始時間,終了時間,休憩時間(時間),総労働時間(時間),シフトタイプ,業務内容,備考,承認者,承認日時\n', 'text/csv', 'shifts.csv');
  }
  
  // ヘッダー行
  const headers = '日付,店舗,従業員ID,従業員名,役職,開始時間,終了時間,休憩時間(時間),総労働時間(時間),シフトタイプ,業務内容,備考,承認者,承認日時';
  
  // データ行
  const csvLines = [headers];
  
  for (const shift of shifts) {
    // 総労働時間を計算
    const totalHour = calculateTotalHour_(shift.start_time, shift.end_time, shift.break_hour);
    
    const row = [
      shift.date,
      shift.store,
      shift.employee_id,
      shift.employee_name,
      shift.role,
      shift.start_time,
      shift.end_time,
      shift.break_hour || '', // 休憩時間（時間）
      totalHour, // 総労働時間（時間）
      shift.shift_type,
      shift.work_content || '', // 業務内容
      shift.notes,
      shift.manager,
      shift.approved_at
    ].map(field => escapeCsv_(field)).join(',');
    
    csvLines.push(row);
  }
  
  const csvContent = csvLines.join('\n');
  const bom = '\uFEFF'; // Excel対策
  return Utilities.newBlob(bom + csvContent, 'text/csv', 'shifts.csv');
}

// ===== CSVエスケープ =====
function escapeCsv_(value) {
  if (value == null) value = '';
  const needsQuote = /[",\n]/.test(value);
  let escaped = String(value).replace(/"/g, '""');
  return needsQuote ? `"${escaped}"` : escaped;
}

// ===== ドライブに保存 =====
function saveToDrive_(csvBlob) {
  const folderId = getProp_('DRIVE_FOLDER_ID', false);
  const ymd = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd');
  const filename = `shifts_${ymd}.csv`;
  
  let file;
  if (folderId) {
    const folder = DriveApp.getFolderById(folderId);
    file = folder.createFile(csvBlob).setName(filename);
  } else {
    file = DriveApp.createFile(csvBlob).setName(filename);
  }
  
  // 共有設定
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  return file;
}

// ===== Slackメッセージ作成 =====
function createSlackMessage_(shifts, fileUrl) {
  const ymd = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd');
  const dayOfWeek = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'E');
  
  let message = `🌅 おはようございます！\n📅 ${ymd}(${dayOfWeek})のシフト集約結果 📅\n\n`;
  
  // 「休み」のシフトを除外して勤務シフトのみを抽出
  const workingShifts = shifts.filter(shift => shift.shift_type !== '休み');
  const restShifts = shifts.filter(shift => shift.shift_type === '休み');
  
  if (workingShifts.length === 0) {
    message += '📝 本日の勤務シフトはありません。';
  } else {
    message += `📊 合計 ${workingShifts.length}件の勤務シフトが承認されています\n`;
    
    // 休みの人数を表示
    if (restShifts.length > 0) {
      message += `😴 ${restShifts.length}名が休みです\n\n`;
    } else {
      message += '\n';
    }
    
    // 店舗別にグループ化（勤務シフトのみ）
    const shiftsByStore = {};
    for (const shift of workingShifts) {
      if (!shiftsByStore[shift.store]) {
        shiftsByStore[shift.store] = [];
      }
      shiftsByStore[shift.store].push(shift);
    }
    
    // 店舗別に表示
    for (const [store, storeShifts] of Object.entries(shiftsByStore)) {
      message += `🏪 **${store}店**\n`;
      
      // 時間順にソート（文字列化して安全に比較）
      storeShifts.sort((a, b) => {
        const timeA = String(a.start_time || '');
        const timeB = String(b.start_time || '');
        return timeA.localeCompare(timeB);
      });
      
      for (const shift of storeShifts) {
        message += `🕐 *${shift.start_time}-${shift.end_time}*: ${shift.employee_name} (${shift.role}) - ${shift.work_content}\n`;
      }
      message += '\n';
    }
    
    message += `📁 詳細CSVファイル: ${fileUrl}\n\n`;
    message += '💪 今日も一日頑張りましょう！';
  }
  
  return message;
}

// ===== Slack投稿 =====
function postToSlack_(message) {
  const webhookUrl = getProp_('SLACK_WEBHOOK_URL');
  const channel = getProp_('SLACK_CHANNEL', false) || '#リモートチーム勤怠報告';
  
  // Webhook URLの検証
  if (!webhookUrl || webhookUrl.includes('Slack%20Webhook%20URL') || !webhookUrl.startsWith('https://hooks.slack.com/')) {
    throw new Error('Slack Webhook URLが正しく設定されていません。GASプロパティでSLACK_WEBHOOK_URLを設定してください。');
  }
  
  const payload = {
    text: message,
    channel: channel
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  };
  
  try {
    const response = UrlFetchApp.fetch(webhookUrl, options);
    console.log('Slack投稿レスポンス:', response.getResponseCode());
    
    if (response.getResponseCode() !== 200) {
      throw new Error(`Slack API エラー: ${response.getResponseCode()} - ${response.getContentText()}`);
    }
  } catch (error) {
    console.error('Slack投稿エラー:', error);
    throw error;
  }
}

// ===== ログ保存 =====
function saveLog_(logData) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const logsSheet = ss.getSheetByName('logs');
  
  if (!logsSheet) {
    console.warn('logsシートが見つかりません');
    return;
  }
  
  const logRow = [
    logData.timestamp,
    logData.action,
    '', // employee_id
    logData.status,
    logData.error_details || 'Success',
    '', // spreadsheet_id
    logData.records_processed,
    logData.error_details,
    logData.execution_time,
    '' // notes
  ];
  
  logsSheet.appendRow(logRow);
}

// ===== テスト用関数 =====
function testAggregation() {
  console.log('🧪 テスト実行を開始します...');
  
  try {
    aggregateShiftsAndPostToSlack();
    console.log('✅ テストが完了しました');
  } catch (error) {
    console.error('❌ テストでエラーが発生しました:', error);
  }
}

// ===== 設定値の初期化 =====
function initializeProperties() {
  const properties = PropertiesService.getScriptProperties();
  
  // 必要なプロパティを設定（実際の値に置き換えてください）
  properties.setProperties({
    'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/YOUR_WEBHOOK_URL',
    'SLACK_CHANNEL': '#リモートチーム勤怠報告',
    'DRIVE_FOLDER_ID': 'YOUR_DRIVE_FOLDER_ID' // 任意
  });
  
  console.log('✅ プロパティを初期化しました');
}
