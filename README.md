# AI 游戏 & Vibe Coding 信息雷达 2.0

**GitHub Actions 每日免费采集** + **Cursor Automation 每周六单文件四模块周报**，关机可跑，月成本约 **$1.5–3.5**。

## 三条主题线

| 主题 ID | 名称 | 周报模块 |
|---------|------|----------|
| `sideline-pain-opportunity` | 副业机会 · 痛点 | **模块 A**（中国本土 friction） |
| `ai-game-dev` | AI 做游戏 | **模块 B**（AI 案例 + 热门题材） |
| `vibe-coding-commercial` | Vibe Coding 商业化 | **模块 C** |

## 架构（2.0 Final · 单文件 + 可选增强层）

```
每天 08:00  GitHub Actions 采集 → data/raw/ + data/daily-index/（免费，无 LLM）
       │      可选 Agent-Reach 源（本地/自托管，默认关闭）→ 同上
周中手动  last30days 定向深研 → data/enriched/（1–3 条/周，不进周六现场搜索）
周六 09:00  Cursor Weekly Automation → reports/weekly/YYYY-Www.md（四模块周报）
                    │
                    └── push 触发 → QQ 邮箱发信（一份 HTML）
```

### 三种运行模式

| 模式 | 做什么 | 成本 | 何时用 |
|------|--------|------|--------|
| **每日采集** | `collect.py`：RSS + GitHub Search | $0 | 每天自动 |
| **可选增强** | Agent-Reach 源 / last30days 深研 | 本地 $0；部分渠道需 Cookie | A1 单源待验证、中文源缺口 |
| **周报合成** | 只读仓库素材 + A4/B2 有限联网 | ~$0.2–0.5/次 | 周六 Automation |

- **采集**：RSS/API + 中文社区/媒体 + Steam/itch，**无 LLM**
- **周报**：单文件 **A 副业 / B 游戏 / C 商业化 / D 附录**；方法论内嵌 Prompt，**不 @ skills**
- **联网**：仅 A4 竞品 + B2 题材补全，**合计 ≤3 次/周**（D3 审计）；**禁止**周六现场跑 `/last30days` 或 Agent-Reach

## 快速开始

### 1. Push 到 GitHub

见仓库 [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar)。

### 2. 开启 GitHub Actions

Push 后自动启用。手动触发：**Actions → Daily Intel Collect → Run workflow**。

### 3. 配置 QQ 邮箱推送

[`send-report-email.yml`](.github/workflows/send-report-email.yml) 在 **周报 commit** 后发 **一份** HTML 邮件。

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
| Instructions | 见 automation-draft（**仅** `@templates/weekly-prompt.md`） |
| 模型 | 最便宜档 |
| Spend limit | $5/月 |

**Run now 试跑后检查**：单文件 `YYYY-Www.md`、D3 联网 ≤3、A1 有 friction 引用、B2 strict scope。

### 5. 本地测试采集

```bash
pip install -r scripts/requirements.txt
python scripts/collect.py
```

上线约 1 周后查看 [`data/stats.json`](data/stats.json)，长期 0 命中的源可从 `sources.yaml` 删除。

### 6. 可选：Agent-Reach 增强源（默认关闭）

[`config/sources.yaml`](config/sources.yaml) 中含 `enabled: false` 的 Agent-Reach 兼容源（B站搜索、V2EX API、YouTube 搜索）。本地安装 [Agent-Reach](https://github.com/Panniantong/Agent-Reach) 后，将对应源 `enabled: true` 再跑采集：

```bash
pip install agent-reach   # 或按 Agent-Reach 文档安装上游 CLI
python scripts/collect.py
```

GitHub Actions **不安装**这些 CLI；缺工具时采集器会跳过并记入 `data/stats.json`，不影响主流程。

### 7. 可选：last30days 定向深研（周中手动）

用于 A1「单源，待交叉验证」或 A4/B2 对比题，每周 **1–3 次**，结果写入 `data/enriched/` 供周六周报读取：

```bash
# 导入已有 brief（markdown），规范化入库
python scripts/enrich_last30days.py --import-brief ~/Documents/Last30Days/电鸭-brief.md \
  --topic "电鸭 找到工作" --topics sideline-pain-opportunity

# 若已安装 last30days skill，可尝试自动调用（需本机配置）
python scripts/enrich_last30days.py --topic "电鸭 找到工作" --topics sideline-pain-opportunity
```

高置信 URL 也可直接写入 [`config/manual-urls.yaml`](config/manual-urls.yaml)。

## 目录结构

```
config/           topics.yaml · sources.yaml · manual-urls.yaml
scripts/          collect.py · enrich_last30days.py · build_report_email.py
data/raw/         每日 JSON（周报主要输入）
data/enriched/    last30days 定向深研产物（可选）
data/daily-index/ 每日链接索引
reports/weekly/   单文件四模块周报
templates/        weekly-prompt.md · methodology-cheatsheet.md
docs/             mock-weekly-2.0.md（排版样例）
.cursor/skills/   本地参考；Automation 不 @
```

## 周报结构（单文件）

```
开篇 · 本周决策（4 bullet，仅此一处）
模块 A · 副业机会（A1–A4）
模块 B · 游戏制作（B1–B3）
模块 C · 商业化（C1–C2）
附录 D（D1 工具 / D2 词表 / D3 审计 / D4 行动）
```

样例：[`docs/mock-weekly-2.0.md`](docs/mock-weekly-2.0.md)

## 定时任务

| 任务 | Cron (UTC) | 北京时间 |
|------|------------|----------|
| 每日采集 | `0 0 * * *` | 08:00 |
| **每周周报** | `0 1 * * 6` | **周六 09:00** |
| 发信（push 触发） | push 到 `reports/weekly/` | 紧随周报 commit |
| **发信（周六兜底）** | `0 2 * * 6` | **周六 10:00** 发最新周报 |

## 成本

| 组件 | 成本 |
|------|------|
| GitHub Actions 采集 | $0 |
| Cursor 周报 × 4/月 | ~$1.5–3.5/月 |

## 常见问题

**Q: 只要周报，平时收什么？**  
A: 平时只有 GitHub 在采集；**周六 9 点** 收一封四模块周报。

**Q: 副业模块 A 经常为空？**  
A: 正常；宁可空不凑数。补 `manual-urls.yaml`、启用本地 Agent-Reach 源，或周中跑 `enrich_last30days.py` 写 `data/enriched/`。

**Q: A1 全是「单源，待交叉验证」？**  
A: 用 `enrich_last30days.py` 或 `manual-urls.yaml` 补第二源；周六 Automation 只读仓库，不会自动深研。

**Q: 没收到邮件？**  
A: 确认 Weekly Automation 成功 push **一个** `YYYY-Www.md`；或 Actions → Send Report Email → `weekly`；查垃圾箱。若周报已在周中提前生成（如试跑），周六 09:00 可能无新 push——现已加 **周六 10:00 兜底发信**。

## License

MIT
