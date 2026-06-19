# Cursor Automation 配置指南

在 [cursor.com/automations](https://cursor.com/automations) 创建 Weekly Intel Report Automation。

## 配置表

| 字段 | 值 |
|------|-----|
| **名称** | Weekly Intel Report |
| **描述** | 每周基于 repo 内采集数据生成 **新手向** AI 游戏 & Vibe Coding 中文周报 |
| **触发** | Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**） |
| **仓库** | [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar) |
| **分支** | `main` |
| **模型** | 最便宜可用档（Flash / Haiku / Composer Fast），**不要用 Opus** |
| **Spend limit** | 在 [cursor.com/dashboard](https://cursor.com/dashboard) → Spending 设 **$5/月** |

## Instructions（Prompt）

将 [`templates/weekly-prompt.md`](../templates/weekly-prompt.md) 的全文粘贴到 Automation Instructions，**或（推荐）** 只写一行，Automation 每次从 repo 读最新 prompt：

```
请阅读 @templates/weekly-prompt.md 并按其中规范执行本周周报任务。
```

> 使用 `@` 引用时，须先将 prompt 改动 push 到 GitHub，再点 Run now。

## 前置条件

1. 本 repo 已 push 到 GitHub，且 Cursor 已连接该 repo。
2. Dashboard 已开启 **on-demand billing** 并设置 spend limit（Cloud Agent 要求）。
3. 至少运行过 1 次 Daily Collect（GitHub Actions），`data/raw/` 中有数据。

## 首次验证

1. 在 Automations UI 手动 **Run now** 触发一次。
2. 到 Dashboard → Usage 查看本次 token 消耗（预期 $0.15–$0.40）。
3. 检查 `reports/weekly/` 是否生成了新的 Markdown 文件；若已配置 QQ 邮箱 Secrets，应收到 **Send Report Email** 推送。

## 成本预期（Pro 计划）

- 4 次/月 × ~$0.15–$0.40 ≈ **$0.6–$1.6/月**（约占 $20 included 的 **3–8%**）

## 故障排查

| 问题 | 处理 |
|------|------|
| Agent 无法 push | 确认 Cursor Cloud Agent 有 repo write 权限 |
| 报告内容编造 | 检查 prompt 是否包含「禁止上网搜索」约束 |
| 费用偏高 | 换更便宜模型；确认 prompt 限制 50 条 |
| 无数据可汇总 | 先确认 GitHub Actions daily collect 正常运行 |
