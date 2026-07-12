# Cursor Automation 配置指南（信息雷达 4.0 · 任务型周报）

在 [cursor.com/automations](https://cursor.com/automations) 配置 **一条** Weekly Automation 即可。

---

## Weekly Intel Report

| 字段 | 值 |
|------|-----|
| **名称** | Weekly Intel Report（或你已有的名字） |
| **描述** | 每周生成 **任务型单文件周报**（A 跟进台 + B 机会 + C 技术雷达 + D 游戏启发 + 附录） |
| **触发** | Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**） |
| **仓库** | [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar) |
| **分支** | `main` |
| **模型** | 最便宜档（Flash / Haiku / Composer Fast），**不要用 Opus** |
| **Spend limit** | Dashboard → Spending 设 **$5/月** |

### Instructions（整段粘贴）

```
请阅读 @templates/weekly-prompt.md（含内嵌方法论速查表 · 信息雷达 4.0），
优先读 data/weekly-digest/YYYY-Www.json（本周预筛 top-80），
缺失时回退 data/raw/、data/daily-index/；再读 reports/weekly/ 中上一期报告
（优先读 A 跟进台、B1/B2、C 条目标题、附录上周状态；若仍是 2.0/3.0 旧稿则尽力映射），
结合 config/ 生成单文件 reports/weekly/YYYY-Www.md（任务型结构）。

B1/B2/B3、C、D 正文禁止联网。
附录竞品 + D2 题材补商店页联网合计每周 ≤3 次，须在附录审计。
遵守条数与总量：A 跟进台 5–7（可更少）、试一试≤2、跳过≤2；B+C+D 展开卡≤15。
人话优先；专名首次括号解释；禁止「本周只做 1 件事」作为唯一主 CTA。
不要 @ .cursor/skills/ 下的任何 skill 文件。
完成后 commit 并 push 一个文件。必须 push 到 main 分支，不要只留在 cursor/* 分支。
```

> 使用 `@templates/weekly-prompt.md` 时，须先将 `templates/` push 到 GitHub，再点 **Run now**。

---

## 整体流水线

```
每天  → GitHub Actions 采集（免费）
周五  → Weekly Digest 预筛 top-80（免费）
周六 09:00 → Cursor Automation 生成 4.0 周报 → push → QQ 邮件
```

### 常见问题

| 现象 | 处理 |
|------|------|
| 报告仍是旧 A/B/C 副业结构 | 确认已 push 最新 `templates/weekly-prompt.md`（4.0），再 Run now |
| 邮件摘要仍是「只做 1 件事」 | 确认周报含 `## A · 本周跟进台`；`build_report_email.py` 已更新 |
| 报告仍是双文件/旧 Part 编号 | Instructions 应只引用 `weekly-prompt.md`；删除 side-hustle 引用 |
