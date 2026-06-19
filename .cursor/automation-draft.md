# Cursor Automation 配置指南（仅周报）

在 [cursor.com/automations](https://cursor.com/automations) 配置 **一条** Weekly Automation 即可。

---

## Weekly Intel Report

| 字段 | 值 |
|------|-----|
| **名称** | Weekly Intel Report（或你已有的名字） |
| **描述** | 每周基于 repo 采集数据，生成 **案例拆解型** 中文周报 |
| **触发** | Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**） |
| **仓库** | [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar) |
| **分支** | `main` |
| **模型** | 最便宜档（Flash / Haiku / Composer Fast），**不要用 Opus** |
| **Spend limit** | Dashboard → Spending 设 **$5/月** |

### Instructions（整段粘贴，或只写下面一行）

```
请阅读 @templates/weekly-prompt.md 并按其中规范执行本周周报任务。
```

> 使用 `@` 引用时，须先将 `templates/weekly-prompt.md` push 到 GitHub，再点 **Run now**。

---

## 整体流水线（仅周报）

```
每天 08:00  GitHub Actions 采集 → data/raw/ + data/daily-index/（免费，无 LLM）
周六 09:00  Cursor Weekly Automation → reports/weekly/（案例拆解周报）→ QQ 邮箱
```

- **不需要** Daily Automation
- **不需要** 改 Cron（你已有的周六 9 点是对的）

---

## 重做 / 更新现有 Automation 的步骤

1. 打开 [cursor.com/automations](https://cursor.com/automations) → 点你 **周六 9 点** 那条
2. **Cron** 保持：`0 1 * * 6`（不用改）
3. **Instructions** 改成上面那一行（引用 `@templates/weekly-prompt.md`）
4. **模型** 选最便宜档；**Spend limit** $5/月
5. 本地改动 push 到 GitHub
6. 点 **Run now** 试跑一次 → 看 `reports/weekly/` 是否生成案例表格 → 查 QQ 邮箱

---

## 前置条件

1. Repo 已 push，Cursor 已连接该 repo
2. Dashboard 已开启 on-demand billing
3. GitHub Actions **Daily Intel Collect** 至少跑过几次（`data/raw/` 有数据）
4. QQ 邮箱 Secrets 已配置（见 README）

---

## 成本预期

- 4 次/月 × ~$0.20–$0.50 ≈ **$0.8–$2/月**（约占 Pro 额度 3–8%）

---

## 故障排查

| 问题 | 处理 |
|------|------|
| 报告仍是旧格式/太简略 | 确认 Instructions 引用了最新的 `weekly-prompt.md` 并已 push |
| 案例字段全是「未知」 | 素材原文没写；补 `config/manual-urls.yaml` 或加源 |
| Agent 无法 push | 确认 Cloud Agent 有 repo write 权限 |
| 没收到邮件 | Actions → Send Report Email → Run workflow → `weekly`；查垃圾箱 |
| 费用偏高 | 换更便宜模型；确认 prompt 限制 80 条 |
