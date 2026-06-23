#!/usr/bin/env python3
from datetime import datetime
from email_sender import send_email, build_email_content

subject = "【投资策略提醒】测试邮件 - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
triggers = [('美股回补-第一阶段', '纳斯达克100连续2周不创新低', '请将赎回资金的50%分批买回')]
content = build_email_content(triggers)
print("准备发送邮件...")
print("Subject:", subject)
print("To:", "2247229894@qq.com")
print("Content:\n", content)
print("\n---")
result = send_email(subject, content)
print("\n结果:", "发送成功" if result else "发送失败")
