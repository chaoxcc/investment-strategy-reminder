from datetime import datetime
from data_fetcher import get_chuangye_index_data, get_nasdaq100_data, get_chuangye_realtime, get_nasdaq100_with_ma
from history_manager import get_monthly_add_count, has_us_redeemed, load_us_redemption_status, save_us_redemption_status

def check_a_stock_sell():
    df = get_chuangye_index_data(5)
    if df is None or len(df) < 6:
        return None, None
    current_close = df.iloc[0]['收盘']
    close_5days_ago = df.iloc[5]['收盘']
    change_pct = (current_close - close_5days_ago) / close_5days_ago * 100
    if change_pct > 8:
        return 'A股赎回', f'创业板指近5日涨幅 +{change_pct:.1f}%，请赎回融通创业板 + 广发中证500 各1/3'
    return None, None

def check_us_stock_sell():
    df = get_nasdaq100_data(5)
    if df is None or len(df) < 6:
        return None, None
    current_close = df.iloc[0]['收盘']
    close_5days_ago = df.iloc[5]['收盘']
    change_pct = (current_close - close_5days_ago) / close_5days_ago * 100
    if change_pct < -5:
        status = load_us_redemption_status()
        if not status['has_redeemed']:
            status['has_redeemed'] = True
            status['redemption_date'] = datetime.now().strftime('%Y-%m-%d')
            save_us_redemption_status(status)
        return '美股赎回', f'纳斯达克100近5日跌幅 {change_pct:.1f}%，请赎回嘉实美国成长 + 广发全球精选 各1/3（趋势破位避险）'
    return None, None

def check_a_stock_add():
    realtime_change = get_chuangye_realtime()
    monthly_count = get_monthly_add_count()
    if realtime_change is not None and realtime_change < -3 and monthly_count < 2:
        return 'A股加仓', f'创业板指当日跌幅 {realtime_change:.1f}%，本月已加仓{monthly_count}次，请手动加仓融通创业板 1000元'
    return None, None

def check_us_stock_phase1_backfill():
    if not has_us_redeemed():
        return None, None
    status = load_us_redemption_status()
    if status['phase1_completed']:
        return None, None
    df = get_nasdaq100_with_ma(30)
    if df is None or len(df) < 14:
        return None, None
    this_week_low = df.iloc[0:5]['最低'].min()
    last_week_low = df.iloc[5:10]['最低'].min()
    if this_week_low > last_week_low:
        return '美股回补-第一阶段', f'纳斯达克100连续2周不创新低，请将赎回资金的50%分批买回'
    return None, None

def check_us_stock_phase2_backfill():
    if not has_us_redeemed():
        return None, None
    status = load_us_redemption_status()
    if not status['phase1_completed'] or status['phase2_completed']:
        return None, None
    df = get_nasdaq100_with_ma(80)
    if df is None or len(df) < 60:
        return None, None
    current_close = df.iloc[0]['收盘']
    ma60 = df.iloc[0]['MA60']
    if current_close > ma60:
        return '美股回补-第二阶段', f'纳斯达克100已站上60日均线，请将剩余50%赎回资金买回'
    return None, None

def check_all_rules():
    triggers = []
    rule1, msg1 = check_a_stock_sell()
    if rule1:
        triggers.append((rule1, msg1))
    rule2, msg2 = check_us_stock_sell()
    if rule2:
        triggers.append((rule2, msg2))
    rule3, msg3 = check_a_stock_add()
    if rule3:
        triggers.append((rule3, msg3))
    rule4, msg4 = check_us_stock_phase1_backfill()
    if rule4:
        triggers.append((rule4, msg4))
    rule5, msg5 = check_us_stock_phase2_backfill()
    if rule5:
        triggers.append((rule5, msg5))
    return triggers
