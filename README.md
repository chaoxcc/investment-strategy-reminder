# 投资策略提醒工具

## 项目说明
根据你的投资策略 v1.0 开发的自动化提醒工具，包含：
- 指数数据获取（使用 AkShare 免费接口）
- 规则判断
- 历史操作记录
- 邮件通知
- GitHub Actions 云端定时运行支持

## 本地快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. 复制 `.env.example` 为 `.env`
2. 填写你的邮箱配置

### 常用邮箱 SMTP 配置
- QQ邮箱: smtp.qq.com, 端口 587
- 163邮箱: smtp.163.com, 端口 587
- Gmail: smtp.gmail.com, 端口 587

### 本地运行与模拟测试

1. 正常运行（使用真实行情）：
```bash
python main.py
```

2. 模拟触发（无需行情数据）：
```bash
# 模拟 A 股加仓
python main.py --simulate a_add

# 模拟 A 股赎回
python main.py --simulate a_sell

# 模拟美股赎回
python main.py --simulate us_sell

# 模拟美股回补第一阶段
python main.py --simulate us_backfill_1

# 模拟美股回补第二阶段
python main.py --simulate us_backfill_2

# 模拟无触发
python main.py --simulate none
```

---

## GitHub Actions 云端定时运行（推荐）

### 1. 创建 GitHub 仓库

1. 在 GitHub 上创建一个新仓库（建议设为 private）
2. 在本地终端执行：
```bash
# 初始化 git
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<你的GitHub用户名>/<你的仓库名>.git
git push -u origin main
```

### 2. 在 GitHub 仓库中添加 Secrets

1. 进入你刚创建的仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret" 依次添加以下 Secrets：

| Secret 名称 | 值 |
|------------|---|
| `EMAIL_SENDER` | 你的发件邮箱（如 `2247229894@qq.com`） |
| `EMAIL_PASSWORD` | 你的邮箱 SMTP 授权码 |
| `EMAIL_RECEIVER` | 你的收件邮箱（如 `2247229894@qq.com`） |
| `SMTP_SERVER` | 你的邮箱 SMTP 服务器（如 `smtp.qq.com`） |
| `SMTP_PORT` | SMTP 端口（如 `587`） |

### 3. 手动触发测试

1. 进入仓库页面，点击 Actions
2. 选择左侧的 "Run Investment Strategy" 工作流
3. 点击 "Run workflow" → 选择 `main` 分支 → 点击 "Run workflow"

这样就会立即运行一次，你可以看到日志和收到邮件提醒。

### 4. 定时任务说明

GitHub Actions 已配置两个定时任务：
- **每日加仓监控**：北京时间 22:00（UTC 14:00），周一至周五
- **每周赎回检查**：北京时间下周一 04:00（UTC 周日 20:00），每周日

---

## 本地 vs 线上部署建议

### 本地部署（快速验证用）
- 优点：安全、免费、简单
- 缺点：电脑必须开机
- 适合：6个月内的策略验证期

### 线上部署（GitHub Actions）
- 优点：24小时运行，不依赖本地电脑，完全免费
- 适合：策略稳定后

---

## 历史记录
- 本地历史操作保存在 `data/operation_history.csv`
- GitHub Actions 运行后，会把历史记录作为 Artifact 上传（可在 Actions 页面下载）
