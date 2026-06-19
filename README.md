# AI 游戏 & Vibe Coding 信息雷达

Pro 优化版信息收集工具：**GitHub Actions 每日免费采集** + **Cursor Automation 每周汇总**，关机可跑，月成本约 Pro 额度的 5–10%。

## 两条主题线

| 主题 ID | 名称 | 内容 |
|---------|------|------|
| `ai-game-dev` | AI 做游戏 | 工具、工作流、方向、产品思路 |
| `vibe-coding-commercial` | Vibe Coding 商业化 | 独立开发者用 AI 编程做出并赚钱的产品案例 |

## 架构

```
GitHub Actions (每日 08:00)       Cursor Automation (每周六 09:00)
     │                                      │
     ▼                                      ▼
 RSS/API 采集 ──→ data/raw/ ──→ 新手向中文周报
     │                                      │
     ▼                                      ▼
 reports/daily/                   reports/weekly/
     │                                      │
     └──── push 触发 ──→ QQ 邮箱 SMTP 发信 ──┘
```

- **日报**：纯链接列表，无 LLM，阅读 3–5 分钟
- **周报**：结构化中文简报 + 可行动建议，阅读 10–15 分钟

## 快速开始

### 1. Push 到 GitHub

```bash
git init
git add .
git commit -m "feat: init intel radar"
git remote add origin https://github.com/YOUR_USER/intel-radar.git
git push -u origin main
```

### 2. 开启 GitHub Actions

Push 后 Actions 自动启用。也可手动触发：**Actions → Daily Intel Collect → Run workflow**。

### 3. 配置 QQ 邮箱推送（推荐）

报告 commit 后，[`send-report-email.yml`](.github/workflows/send-report-email.yml) 会把 **日报/周报正文** 发到你的 QQ 邮箱。

**① 开启 QQ 邮箱 SMTP**

1. 登录 [mail.qq.com](https://mail.qq.com) → 设置 → 账户  
2. 开启 **POP3/SMTP 服务**  
3. 生成 **授权码**（不是 QQ 密码，妥善保管）

**② 在 GitHub 仓库添加 Secrets**

[仓库 Settings → Secrets and variables → Actions](https://github.com/ckirahu-prog/vibe-coding-intel-radar/settings/secrets/actions) → **New repository secret**：

| Secret 名 | 值 | 示例 |
|-----------|-----|------|
| `MAIL_USERNAME` | 发件 QQ 邮箱 | `1003862941@qq.com` |
| `MAIL_PASSWORD` | QQ 邮箱 **授权码** | （16 位授权码） |
| `MAIL_TO` | 收件邮箱 | `1003862941@qq.com` |

**③ 测试**

- 手动跑一次 **Daily Intel Collect**，或有新日报 commit 后，检查 QQ 邮箱  
- 或在 Actions 里运行 **Send Report Email**（需先有 reports 变更 commit）

> 未配置 Secrets 时，发信 workflow 会自动跳过，不影响采集。

（可选）GitHub **Watch → All Activity** 可同时收到 commit 通知，但不含报告正文。

### 4. 配置 Cursor Automation（周报）

详见 [`.cursor/automation-draft.md`](.cursor/automation-draft.md)：

- Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**）
- 模型：最便宜档（Flash / Haiku / Composer Fast）
- Prompt：[`templates/weekly-prompt.md`](templates/weekly-prompt.md)
- Spend limit：Dashboard 设 $5/月

### 5. 本地测试采集

```bash
pip install -r scripts/requirements.txt
python scripts/collect.py
```

## 目录结构

```
config/
  topics.yaml       # 主题与关键词
  sources.yaml      # RSS / GitHub API 源
  manual-urls.yaml  # 手动添加链接
scripts/
  collect.py        # 采集脚本
data/
  raw/              # 每日原始 JSON
  seen.json         # URL 去重
  stats.json        # 各源命中统计
reports/
  daily/            # 日报 Markdown
  weekly/           # 周报 Markdown（Automation 写入）
templates/
  weekly-prompt.md  # Automation prompt 模板
```

## 定时任务时区

| 任务 | Cron (UTC) | 北京时间 |
|------|------------|----------|
| 每日采集 | `0 0 * * *` | 每天 08:00 |
| 每周汇总 | `0 1 * * 6` | **周六 09:00** |
| 报告发信 | push 到 `reports/` 时自动 | 紧随日报/周报 commit |

修改采集时间：编辑 [`.github/workflows/collect-daily.yml`](.github/workflows/collect-daily.yml) 中的 `cron` 字段。

## 如何添加信息源

编辑 [`config/sources.yaml`](config/sources.yaml)：

```yaml
- id: my-source
  name: "来源名称"
  type: rss          # 或 github_search
  url: "https://..."  # RSS 用 url
  query: "..."        # github_search 用 query
  topics: [ai-game-dev]
  tier: B             # A = 必收录, B = 需关键词命中
```

手动添加单条链接：编辑 [`config/manual-urls.yaml`](config/manual-urls.yaml)。

## 如何调整关键词

编辑 [`config/topics.yaml`](config/topics.yaml) 中各主题的 `keywords` 列表。  
B 级源只有标题/摘要命中关键词才会收录；A 级源（如 GitHub Search）跳过关键词过滤。

## 成本说明（Cursor Pro）

| 组件 | 频率 | 成本 |
|------|------|------|
| GitHub Actions 采集 | 每日 | **$0**（公开 repo 免费） |
| Cursor Automation 周报 | 每周 | **~$0.15–0.40/次** |
| **合计** | | **~$0.6–1.6/月（约 Pro 额度的 3–8%）** |

优化要点：Automation **只读 repo 内数据、禁止联网搜索、用便宜模型**。

## 质量调优

运行 2–4 周后查看 [`data/stats.json`](data/stats.json)：

- 连续 0 命中的源 → 从 `sources.yaml` 删除
- 噪音太多 → 提高 B 级源关键词门槛或加 HN points 过滤
- 漏报 → 在 `manual-urls.yaml` 补充或新增 RSS 源

## 常见问题

**Q: 今天没有收到邮件？**  
A: 可能当日无新内容（脚本不会空 commit，也就不会发信）。检查 Actions 里 **Send Report Email** 是否运行；确认已配置 `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_TO` Secrets。

**Q: Reddit RSS 拉不到？**  
A: Reddit 可能限流；GitHub Actions 环境通常可用。持续失败可在 `stats.json` 查看 `last_error`。

**Q: GitHub Search 限额？**  
A: 无 token 时 60 次/小时；Actions 内置 `GITHUB_TOKEN` 为 5000 次/小时，workflow 已配置。

## License

MIT
