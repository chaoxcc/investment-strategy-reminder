from datetime import datetime
from data_fetcher import (
    get_chuangye_index_data, get_nasdaq100_data,
    get_chuangye_realtime, get_nasdaq100_with_ma
)
from history_manager import (
    get_monthly_add_count, is_in_cooldown, set_cooldown,
    has_us_redeemed, load_us_redemption_status, save_us_redemption_status
)


def _calculate_window_change(df, window_days=20, is_a_stock=True):
    """
    计算滚动窗口涨跌幅
    df: 按日期降序排列的数据
    window_days: 窗口天数
    is_a_stock: 是否是A股
    返回：(涨跌幅百分比, 是否有效)
    """
    if df is None or len(df) < window_days + 1:
        return None, False
    
    try:
        if is_a_stock:
            current_close = float(df.iloc[0]['收盘'])
            close_window_ago = float(df.iloc[window_days]['收盘'])
        else:
            current_close = float(df.iloc[0]['收盘'])
            close_window_ago = float(df.iloc[window_days]['收盘'])
        
        change_pct = (current_close - close_window_ago) / close_window_ago * 100
        return change_pct, True
    except Exception as e:
        print(f"计算窗口涨跌幅失败: {e}")
        return None, False


def check_a_stock_sell():
    """
    A股卖出检查
    创业板指滚动20日涨幅首次>8%，且不在冷却期
    """
    if is_in_cooldown('a_sell'):
        return None, None, "在冷却期内"
    
    df = get_chuangye_index_data(window_days=20)
    change_pct, is_valid = _calculate_window_change(df, window_days=20, is_a_stock=True)
    
    if not is_valid:
        return None, None, "数据不足"
    
    if change_pct > 8:
        rule = "A股卖出"
        msg = f"创业板指滚动20日涨幅 +{change_pct:.1f}%"
        action = "请赎回融通创业板 + 广发中证500 各1/3"
        return rule, msg, action
    return None, None, "未触发"


def check_us_stock_sell():
    """
    美股卖出检查
    纳斯达克100滚动20日跌幅>5%，且不在冷却期
    """
    if is_in_cooldown('us_sell'):
        return None, None, "在冷却期内"
    
    df = get_nasdaq100_data(window_days=20)
    change_pct, is_valid = _calculate_window_change(df, window_days=20, is_a_stock=False)
    
    if not is_valid:
        return None, None, "数据不足"
    
    if change_pct < -5:
        rule = "美股卖出"
        msg = f"纳斯达克100滚动20日跌幅 {change_pct:.1f}%"
        action = "请赎回嘉实美国成长 + 广发全球精选 各1/3（趋势破位避险）"
        return rule, msg, action
    return None, None, "未触发"


def check_a_stock_add():
    """
    A股加仓检查
    创业板指当日实时跌幅>3% 且 本月加仓<2次
    """
    realtime_change = get_chuangye_realtime()
    monthly_count = get_monthly_add_count()
    
    if realtime_change is not None and realtime_change < -3 and monthly_count < 2:
        rule = "A股加仓"
        msg = f"创业板指当日跌幅 {realtime_change:.1f}%，本月已加仓{monthly_count}次"
        action = "请手动加仓融通创业板 1000元"
        return rule, msg, action
    return None, None, "未触发"


def check_us_stock_phase1_backfill():
    """
    美股回补第一阶段检查
    连续2周不创新低（本周最低点 > 上周最低点）
    """
    if not has_us_redeemed():
        return None, None, "未赎回过"
    
    status = load_us_redemption_status()
    if status.get('phase1_completed', False):
        return None, None, "第一阶段已完成"
    
    df = get_nasdaq100_data(window_days=30)
    if df is None or len(df) < 14:
        return None, None, "数据不足"
    
    try:
        # 本周最低点（最近5个交易日）
        this_week_low = min([float(df.iloc[i]['最低']) for i in range(min(5, len(df)))])
        # 上周最低点（接下来5个交易日）
        last_week_low = min([float(df.iloc[i]['最低']) for i in range(5, min(10, len(df)))])
        
        if this_week_low > last_week_low:
            rule = "美股回补-第一阶段"
            msg = "纳斯达克100连续2周不创新低"
            action = "请将赎回资金的50%分批买回"
            return rule, msg, action
    except Exception as e:
        print(f"检查美股回补第一阶段失败: {e}")
    
    return None, None, "未触发"


def check_us_stock_phase2_backfill():
    """
    美股回补第二阶段检查
    纳指100重回60日均线上方
    """
    if not has_us_redeemed():
        return None, None, "未赎回过"
    
    status = load_us_redemption_status()
    if not status.get('phase1_completed', False):
        return None, None, "请先完成第一阶段"
    if status.get('phase2_completed', False):
        return None, None, "第二阶段已完成"
    
    df = get_nasdaq100_with_ma()
    if df is None or len(df) < 60:
        return None, None, "数据不足"
    
    try:
        current_close = float(df.iloc[0]['收盘'])
        ma60 = float(df.iloc[0]['MA60'])
        
        if current_close > ma60:
            rule = "美股回补-第二阶段"
            msg = f"纳斯达克100已站上60日均线（当前：{current_close:.2f}，MA60：{ma60:.2f}）"
            action = "请将剩余50%赎回资金买回"
            return rule, msg, action
    except Exception as e:
        print(f"检查美股回补第二阶段失败: {e}")
    
    return None, None, "未触发"


def check_all_rules():
    """
    检查所有规则
    返回：[(规则名, 信号数据, 操作), ...]
    """
    triggers = []
    
    # A股卖出
    rule, msg, action = check_a_stock_sell()
    if rule:
        triggers.append((rule, msg, action))
    
    # 美股卖出
    rule, msg, action = check_us_stock_sell()
    if rule:
        triggers.append((rule, msg, action))
    
    # A股加仓
    rule, msg, action = check_a_stock_add()
    if rule:
        triggers.append((rule, msg, action))
    
    # 美股回补第一阶段
    rule, msg, action = check_us_stock_phase1_backfill()
    if rule:
        triggers.append((rule, msg, action))
    
    # 美股回补第二阶段
    rule, msg, action = check_us_stock_phase2_backfill()
    if rule:
        triggers.append((rule, msg, action))
    
    return triggers
