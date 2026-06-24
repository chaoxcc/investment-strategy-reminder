import argparse
from datetime import datetime
from email_sender import send_email, build_email_content
from history_manager import (
    add_operation, load_us_redemption_status, save_us_redemption_status,
    set_cooldown
)


def get_simulated_triggers(simulate_rule):
    simulated_messages = {
        'a_sell': [('A股卖出', '创业板指滚动20日涨幅 +8.5%', '请赎回融通创业板 + 广发中证500 各1/3')],
        'us_sell': [('美股卖出', '纳斯达克100滚动20日跌幅 -6.2%', '请赎回嘉实美国成长 + 广发全球精选 各1/3（趋势破位避险）')],
        'a_add': [('A股加仓', '创业板指当日跌幅 -3.6%，本月已加仓1次', '请手动加仓融通创业板 1000元')],
        'us_backfill_1': [('美股回补-第一阶段', '纳斯达克100连续2周不创新低', '请将赎回资金的50%分批买回')],
        'us_backfill_2': [('美股回补-第二阶段', '纳斯达克100已站上60日均线', '请将剩余50%赎回资金买回')],
        'none': [],
        'full': [
            ('A股加仓', '创业板指当日跌幅 -3.2%，本月已加仓0次', '请手动加仓融通创业板 1000元'),
            ('A股卖出', '创业板指滚动20日涨幅 +8.7%', '请赎回融通创业板 + 广发中证500 各1/3'),
            ('美股卖出', '纳斯达克100滚动20日跌幅 -5.3%', '请赎回嘉实美国成长 + 广发全球精选 各1/3（趋势破位避险）')
        ],
    }
    return simulated_messages[simulate_rule]


def parse_args():
    parser = argparse.ArgumentParser(description='投资策略提醒工具')
    parser.add_argument(
        '--simulate',
        choices=['a_sell', 'us_sell', 'a_add', 'us_backfill_1', 'us_backfill_2', 'none', 'full'],
        help='模拟触发某个策略，不调用真实行情接口'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"开始执行投资策略检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.simulate:
        triggers = get_simulated_triggers(args.simulate)
    else:
        from rule_engine import check_all_rules
        triggers = check_all_rules()
    
    for rule, msg, action in triggers:
        add_operation(rule, action, msg)
        
        # 设置冷却期
        if rule == "A股卖出":
            set_cooldown('a_sell')
        elif rule == "美股卖出":
            set_cooldown('us_sell')
            status = load_us_redemption_status()
            if not status.get('has_redeemed', False):
                status['has_redeemed'] = True
                status['redemption_date'] = datetime.now().strftime('%Y-%m-%d')
                save_us_redemption_status(status)
        # 更新回补状态
        elif rule == "美股回补-第一阶段":
            status = load_us_redemption_status()
            status['phase1_completed'] = True
            save_us_redemption_status(status)
        elif rule == "美股回补-第二阶段":
            status = load_us_redemption_status()
            status['phase2_completed'] = True
            save_us_redemption_status(status)
    
    email_content = build_email_content(triggers)
    subject = f"【投资策略提醒】{datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, email_content)
    print('检查完成')


if __name__ == '__main__':
    main()
