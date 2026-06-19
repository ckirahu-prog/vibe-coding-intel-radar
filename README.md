# AI 游戏 & Vibe Coding 信息雷达

Pro 优化版信息收集工具：**GitHub Actions 每日免费采集** + **Cursor Automation 每周汇总**，关机可跑，月成本约 Pro 额度的 5–10%。

## 两条主题线

| 主题 ID | 名称 | 内容 |
|---------|------|------|
| `ai-game-dev` | AI 做游戏 | 工具、工作流、方向、产品思路 |
| `vibe-coding-commercial` | Vibe Coding 商业化 | 独立开发者用 AI 编程做出并赚钱的产品案例 |

## 架构

```
GitHub Actions (每日)          Cursor Automation (每周一)
     │                              │
     ▼                              ▼
 RSS/API 采集 ──→ data/raw/ ──→ 中文周报
     │                              │
     ▼                              ▼
 reports/daily/              reports/weekly/
     │                              │
     └──────── GitHub 邮件通知 ──────┘
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

### 3. 设置邮件通知

在 GitHub repo 页面点击 **Watch → All Activity**（或 Custom，只勾选相关 commit 通知）。  
有新 `reports/daily/` 或 `reports/weekly/` commit 时会收到邮件。

### 4. 配置 Cursor Automation（周报）

详见 [`.cursor/automation-draft.md`](.cursor/automation-draft.md)：

- Cron：`0 1 * * 1`（北京时间周一 09:00）
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
| 每日采集 | `0 0 * * *` | 08:00 |
| 每周汇总 | `0 1 * * 1` | 周一 09:00 |

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
A: 可能当日无新内容（脚本不会空 commit）。可在 Actions 日志确认，或本地跑 `collect.py` 测试。

**Q: Reddit RSS 拉不到？**  
A: Reddit 可能限流；GitHub Actions 环境通常可用。持续失败可在 `stats.json` 查看 `last_error`。

**Q: GitHub Search 限额？**  
A: 无 token 时 60 次/小时；Actions 内置 `GITHUB_TOKEN` 为 5000 次/小时，workflow 已配置。

## License

MIT
