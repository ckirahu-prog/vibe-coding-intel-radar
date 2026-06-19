# AI 游戏 & Vibe Coding 信息雷达

**GitHub Actions 每日免费采集** + **Cursor Automation 每周六案例周报**，关机可跑，月成本约 Pro 额度的 3–8%。

## 两条主题线

| 主题 ID | 名称 | 周报里写什么 |
|---------|------|--------------|
| `ai-game-dev` | AI 做游戏 | 哪些游戏用了 AI、什么技术、什么效果、还能做什么 |
| `vibe-coding-commercial` | Vibe Coding 商业化 | 解决什么需求、多少收益、用了什么技术 |

## 架构（仅周报）

```
每天 08:00  GitHub Actions 采集 → data/raw/ + data/daily-index/（免费）
周六 09:00  Cursor Weekly Automation → reports/weekly/（案例拆解周报）
                    │
                    └── push 触发 → QQ 邮箱发信
```

- **采集**：每天自动抓 RSS/API，存 JSON + 链接索引，**无 LLM**
- **周报**：周六 Agent 读本周素材，写案例拆解报告，**push 后发 QQ 邮件**
- **不需要** Daily Automation

## 快速开始

### 1. Push 到 GitHub

见仓库 [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar)。

### 2. 开启 GitHub Actions

Push 后自动启用。手动触发：**Actions → Daily Intel Collect → Run workflow**。

### 3. 配置 QQ 邮箱推送

[`send-report-email.yml`](.github/workflows/send-report-email.yml) 在 **周报 commit** 后发信。

| Secret | 说明 |
|--------|------|
| `MAIL_USERNAME` | 发件 QQ 邮箱 |
| `MAIL_PASSWORD` | QQ 邮箱 **授权码**（非登录密码） |
| `MAIL_TO` | 收件邮箱（可省略，默认同发件） |

**测试**：Actions → **Send Report Email** → Run workflow → 选 **`weekly`**

### 4. 配置 Cursor Automation（仅一条 · 周六 9 点）

详见 [`.cursor/automation-draft.md`](.cursor/automation-draft.md)。

| 字段 | 值 |
|------|-----|
| Cron | `0 1 * * 6`（北京时间 **周六 09:00**） |
| Instructions | `请阅读 @templates/weekly-prompt.md 并按其中规范执行本周周报任务。` |
| 模型 | 最便宜档 |
| Spend limit | $5/月 |

**你已有周六那条的话**：不用新建，只改 Instructions 为上面一行，push 最新 prompt 后 **Run now** 试跑。

### 5. 本地测试采集

```bash
pip install -r scripts/requirements.txt
python scripts/collect.py
```

## 目录结构

```
config/           topics.yaml · sources.yaml · manual-urls.yaml
scripts/          collect.py
data/raw/         每日 JSON（周报主要输入）
data/daily-index/ 每日链接索引（周报辅助输入）
reports/weekly/   案例拆解周报（Automation 写入）
templates/        weekly-prompt.md
```

## 定时任务

| 任务 | Cron (UTC) | 北京时间 |
|------|------------|----------|
| 每日采集 | `0 0 * * *` | 08:00 |
| **每周周报** | `0 1 * * 6` | **周六 09:00** |
| 发信 | push 到 `reports/weekly/` | 紧随周报 commit |

## 成本

| 组件 | 成本 |
|------|------|
| GitHub Actions 采集 | $0 |
| Cursor 周报 × 4/月 | ~$0.8–2/月 |

## 常见问题

**Q: 只要周报，平时收什么？**  
A: 平时只有 GitHub 在默默采集；**周六 9 点** 收一封案例拆解周报。中间不发邮件。

**Q: 周报很多「未知」？**  
A: 原文没写游戏名/金额时会标未知。可在 `config/manual-urls.yaml` 手动补高质量链接。

**Q: 没收到邮件？**  
A: 确认 Weekly Automation 成功 push；或 Actions → Send Report Email → `weekly`；查垃圾箱。

## License

MIT
