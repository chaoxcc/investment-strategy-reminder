#!/usr/bin/env python3
from datetime import datetime

# 模拟核心的触发和邮件生成
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


def build_email_content(triggers):
    content = f"【投资策略提醒】\n"
    content += f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    if not triggers:
        content += "今日无触发规则，继续持有，定投照常。\n"
    else:
        for rule, msg, action in triggers:
            content += "---\n"
            content += f"触发规则: {rule}\n"
            content += f"信号数据: {msg}\n"
            content += f"执行操作: {action}\n"
            
            if rule in ["A股卖出", "美股卖出"]:
                content += "冷却提醒: 该品种进入20个交易日冷却期\n"
            if rule == "美股卖出":
                content += "资金提醒: 赎回后请按回补规则操作\n"
            if rule in ["A股卖出", "美股卖出"]:
                content += "窗口提醒: 请在周一15:00前完成操作\n"
            elif rule == "A股加仓":
                content += "窗口提醒: 请在今日15:00前完成操作\n"
            
            content += "\n"
    
    content += "\n---\n"
    content += "定投纪律：无论市场涨跌，定投绝不停止。\n"
    return content


if __name__ == '__main__':
    print("=== 测试full模式 ===")
    triggers = get_simulated_triggers('full')
    email_content = build_email_content(triggers)
    print(email_content)
    print("\n=== 测试完成 ===")
