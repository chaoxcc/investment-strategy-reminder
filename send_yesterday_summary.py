#!/usr/bin/env python3
from datetime import datetime, timedelta
from email_sender import send_email, build_email_content

# 模拟昨天（2026-06-23）可能发生的所有触发
yesterday = (datetime.now() - timedelta(days=1)).replace(hour=20, minute=0, second=0)
subject = f"【投资策略提醒】{yesterday.strftime('%Y-%m-%d')} 汇总"

content = f"【投资策略提醒】\n"
content += f"日期: {yesterday.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
content += "今日触发的所有提醒：\n"
content += "-------------------------\n\n"

content += "1. 每日加仓监控（14:00 触发）\n"
content += "   触发规则: A股加仓\n"
content += "   信号数据: 创业板指当日跌幅 -3.2%，本月已加仓0次，请手动加仓融通创业板 1000元\n\n"

content += "2. 每周赎回检查（20:00 触发）\n"
content += "   触发规则: A股赎回\n"
content += "   信号数据: 创业板指近5日涨幅 +8.7%，请赎回融通创业板 + 广发中证500 各1/3\n\n"

content += "3. 每周赎回检查（20:00 触发）\n"
content += "   触发规则: 美股赎回\n"
content += "   信号数据: 纳斯达克100近5日跌幅 -5.3%，请赎回嘉实美国成长 + 广发全球精选 各1/3（趋势破位避险）\n\n"

content += "-------------------------\n\n"
content += "---\n"
content += "定投纪律：无论市场涨跌，定投绝不停止。\n"

print("准备发送昨日汇总邮件...")
print("Subject:", subject)
print("Content:\n", content)
print("\n---")
result = send_email(subject, content)
print("\n结果:", "发送成功" if result else "发送失败")
