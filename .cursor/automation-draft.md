# Cursor Automation 配置指南（信息雷达 2.0 Final · 单文件周报）

在 [cursor.com/automations](https://cursor.com/automations) 配置 **一条** Weekly Automation 即可。

---

## Weekly Intel Report

| 字段 | 值 |
|------|-----|
| **名称** | Weekly Intel Report（或你已有的名字） |
| **描述** | 每周生成 **单文件四模块周报**（副业 A + 游戏 B + 商业化 C + 附录 D） |
| **触发** | Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**） |
| **仓库** | [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar) |
| **分支** | `main` |
| **模型** | 最便宜档（Flash / Haiku / Composer Fast），**不要用 Opus** |
| **Spend limit** | Dashboard → Spending 设 **$5/月** |

### Instructions（整段粘贴）

```
请阅读 @templates/weekly-prompt.md（含内嵌方法论速查表），
只读 data/raw/、data/daily-index/、config/ 生成单文件
reports/weekly/YYYY-Www.md（四模块+附录结构）。

模块 A1–A3、B1、C 禁止联网。
模块 A4 + B2 联网合计每周 ≤3 次，须在 D3 审计。
不要 @ .cursor/skills/ 下的任何 skill 文件。
完成后 commit 并 push 一个文件。必须 push 到 main 分支，不要只留在 cursor/* 分支。
```

> 使用 `@templates/weekly-prompt.md` 时，须先将 `templates/` push 到 GitHub，再点 **Run now**。

---

## 整体流水线

```
每天 08:00  GitHub Actions 采集 → data/raw/ + data/daily-index/（免费，无 LLM）
周六 09:00  Cursor Weekly Automation → reports/weekly/YYYY-Www.md → QQ 邮箱
```

- **不需要** Daily Automation
- **不需要** 第二条 Automation
- **不需要** `@` skill 文件（规则已内嵌 prompt）

---

## 重做 / 更新现有 Automation 的步骤

1. 打开 [cursor.com/automations](https://cursor.com/automations) → 点你 **周六 9 点** 那条
2. **Cron** 保持：`0 1 * * 6`
3. **Instructions** 改成上面整段（**仅** `@templates/weekly-prompt.md`，去掉 side-hustle 与 skills）
4. **模型** 选最便宜档；**Spend limit** $5/月
5. 本地改动 push 到 GitHub
6. 点 **Run now** 试跑 → 检查：
   - 是否 **单文件** `YYYY-Www.md`
   - **D3** 联网次数 ≤3
   - **A1** 是否有 friction 引用
   - **B2** 是否符合 strict scope

---

## 前置条件

1. Repo 已 push，Cursor 已连接该 repo
2. Dashboard 已开启 on-demand billing
3. GitHub Actions **Daily Intel Collect** 至少跑过几次（`data/raw/` 有数据；含中文源/Steam/itch）
4. QQ 邮箱 Secrets 已配置（见 README）

---

## 成本预期

- 4 次/月 × ~$0.20–$0.50 ≈ **$0.8–$2/月**（内联 Prompt 后 token 低于双 Prompt + Skills 方案）

---

## 故障排查

| 问题 | 处理 |
|------|------|
| 报告仍是双文件/旧 Part 编号 | Instructions 应只引用 `weekly-prompt.md`；删除 side-hustle 引用 |
| 案例字段全是「未知」 | 补 `config/manual-urls.yaml` 或等中文源采集命中 |
| Agent 无法 push | 确认 Cloud Agent 有 repo write 权限 |
| 没收到邮件 | Actions → Send Report Email → Run workflow → `weekly`；查垃圾箱 |
| 联网超配额 | 检查 D3；Prompt 硬顶 A4+B2 ≤3 |
| 费用偏高 | 换更便宜模型；确认未 @ skills |
