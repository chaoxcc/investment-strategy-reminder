import os
import json
from datetime import datetime
from config import Config


def ensure_data_dir():
    try:
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建data目录失败: {e}")
        return False


def load_history():
    if not ensure_data_dir():
        return []
    
    if os.path.exists(Config.HISTORY_FILE):
        try:
            import csv
            history = []
            with open(Config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history.append(row)
            return history
        except Exception as e:
            print(f"读取历史记录失败: {e}")
            return []
    return []


def save_history(history):
    if not ensure_data_dir():
        return False
    
    try:
        import csv
        fieldnames = ['date', 'rule_triggered', 'action', 'notes']
        with open(Config.HISTORY_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in history:
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"保存历史记录失败: {e}")
        return False


def add_operation(rule_triggered, action, notes=''):
    history = load_history()
    new_row = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rule_triggered': rule_triggered,
        'action': action,
        'notes': notes
    }
    history.append(new_row)
    save_history(history)


def get_monthly_add_count():
    history = load_history()
    if not history:
        return 0
    current_month = datetime.now().strftime('%Y-%m')
    count = 0
    for row in history:
        if 'date' in row and row.get('rule_triggered') == 'A股加仓':
            row_month = row['date'][:7] if len(row['date']) > 7 else ''
            if row_month == current_month:
                count += 1
    return count


# --- 冷却期管理 ---

COOLDOWN_STATUS_FILE = os.path.join(Config.DATA_DIR, 'cooldown_status.json')


def load_cooldown_status():
    ensure_data_dir()
    if os.path.exists(COOLDOWN_STATUS_FILE):
        try:
            with open(COOLDOWN_STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取冷却状态失败: {e}")
    
    return {
        'a_sell_last_date': None,
        'us_sell_last_date': None,
        'a_sell_cooldown_days': 20,
        'us_sell_cooldown_days': 20
    }


def save_cooldown_status(status):
    if not ensure_data_dir():
        return False
    
    try:
        with open(COOLDOWN_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存冷却状态失败: {e}")
        return False


def is_in_cooldown(rule_type):
    """
    检查是否在冷却期
    rule_type: 'a_sell' 或 'us_sell'
    """
    status = load_cooldown_status()
    date_key = f'{rule_type}_last_date'
    days_key = f'{rule_type}_cooldown_days'
    
    last_date_str = status.get(date_key)
    if not last_date_str:
        return False
    
    try:
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        days_passed = (datetime.now() - last_date).days
        cooldown_days = status.get(days_key, 20)
        return days_passed < cooldown_days
    except Exception as e:
        print(f"检查冷却期失败: {e}")
        return False


def set_cooldown(rule_type):
    """
    设置冷却期开始时间为今天
    rule_type: 'a_sell' 或 'us_sell'
    """
    status = load_cooldown_status()
    date_key = f'{rule_type}_last_date'
    status[date_key] = datetime.now().strftime('%Y-%m-%d')
    save_cooldown_status(status)


# --- 美股赎回状态管理 ---

US_REDEMPTION_STATUS_FILE = os.path.join(Config.DATA_DIR, 'us_redemption_status.json')


def load_us_redemption_status():
    ensure_data_dir()
    if os.path.exists(US_REDEMPTION_STATUS_FILE):
        try:
            with open(US_REDEMPTION_STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取美股赎回状态失败: {e}")
    
    return {
        'has_redeemed': False,
        'phase1_completed': False,
        'phase2_completed': False,
        'redemption_date': None
    }


def save_us_redemption_status(status):
    if not ensure_data_dir():
        return False
    
    try:
        with open(US_REDEMPTION_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存美股赎回状态失败: {e}")
        return False


def has_us_redeemed():
    status = load_us_redemption_status()
    return status.get('has_redeemed', False)
