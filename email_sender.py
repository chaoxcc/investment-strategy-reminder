import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config


def _looks_like_placeholder(value):
    if not value:
        return True
    return value.startswith('your_') or value.startswith('receiver@') or value == 'smtp.example.com'


def _save_email_preview(subject, content):
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    preview = f"Subject: {subject}\nTo: {Config.EMAIL_RECEIVER}\n\n{content}"
    with open(Config.EMAIL_PREVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write(preview)
    print(f"已生成邮件预览: {Config.EMAIL_PREVIEW_FILE}")
    return True


def send_email(subject, content):
    if Config.EMAIL_DRY_RUN:
        return _save_email_preview(subject, content)
    
    if any([
        _looks_like_placeholder(Config.EMAIL_SENDER),
        _looks_like_placeholder(Config.EMAIL_PASSWORD),
        _looks_like_placeholder(Config.EMAIL_RECEIVER),
        _looks_like_placeholder(Config.SMTP_SERVER),
    ]):
        print("邮件配置不完整，已切换为本地预览模式")
        return _save_email_preview(subject, content)
    
    msg = MIMEMultipart()
    msg['From'] = Config.EMAIL_SENDER
    msg['To'] = Config.EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.EMAIL_SENDER, Config.EMAIL_RECEIVER, text)
        server.quit()
        print("邮件发送成功")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


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
            
            # 添加冷却提醒
            if rule in ["A股卖出", "美股卖出"]:
                content += "冷却提醒: 该品种进入20个交易日冷却期\n"
            
            # 添加资金提醒
            if rule == "美股卖出":
                content += "资金提醒: 赎回后请按回补规则操作\n"
            
            # 添加窗口提醒
            if rule in ["A股卖出", "美股卖出"]:
                content += "窗口提醒: 请在周一15:00前完成操作\n"
            elif rule == "A股加仓":
                content += "窗口提醒: 请在今日15:00前完成操作\n"
            
            content += "\n"
    
    content += "\n---\n"
    content += "定投纪律：无论市场涨跌，定投绝不停止。\n"
    return content
