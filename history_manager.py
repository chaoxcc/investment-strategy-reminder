import csv
import json
import os
from datetime import datetime
from config import Config

US_REDEMPTION_STATUS_FILE = os.path.join(Config.DATA_DIR, 'us_redemption_status.json')

def ensure_data_dir():
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)

def load_history():
    ensure_data_dir()
    if os.path.exists(Config.HISTORY_FILE):
        with open(Config.HISTORY_FILE, 'r', encoding='utf-8', newline='') as file:
            return list(csv.DictReader(file))
    return []

def save_history(history_rows):
    ensure_data_dir()
    with open(Config.HISTORY_FILE, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'rule_triggered', 'action', 'notes'])
        writer.writeheader()
        writer.writerows(history_rows)

def get_monthly_add_count():
    history_rows = load_history()
    if not history_rows:
        return 0
    current_month = datetime.now().strftime('%Y-%m')
    count = 0
    for row in history_rows:
        row_date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
        if row_date.strftime('%Y-%m') == current_month and row['rule_triggered'] == 'A股加仓':
            count += 1
    return count

def add_operation(rule_triggered, action, notes=''):
    history_rows = load_history()
    history_rows.append({
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rule_triggered': rule_triggered,
        'action': action,
        'notes': notes,
    })
    save_history(history_rows)

def load_us_redemption_status():
    ensure_data_dir()
    if os.path.exists(US_REDEMPTION_STATUS_FILE):
        with open(US_REDEMPTION_STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'has_redeemed': False, 'phase1_completed': False, 'phase2_completed': False, 'redemption_date': None}

def save_us_redemption_status(status):
    ensure_data_dir()
    with open(US_REDEMPTION_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def has_us_redeemed():
    status = load_us_redemption_status()
    return status['has_redeemed']
