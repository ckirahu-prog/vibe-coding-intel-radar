# Cursor Automation 配置指南（信息雷达 4.0.1 · 任务型周报）

在 [cursor.com/automations](https://cursor.com/automations) 配置 **一条** Weekly Automation 即可。

---

## Weekly Intel Report

| 字段 | 值 |
|------|-----|
| **名称** | Weekly Intel Report（或你已有的名字） |
| **描述** | 每周生成任务型周报：跟进台 + 机会 + 游戏向技术雷达 + 游戏启发 |
| **触发** | Cron：`0 1 * * 6`（UTC 周六 01:00 = **北京时间周六 09:00**） |
| **仓库** | [ckirahu-prog/vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar) |
| **分支** | `main` |
| **模型** | **Grok 4.5 Medium**（Automations 固定 Max，无法关闭；勿选 Fast） |
| **Spend limit** | Dashboard → Spending 设 **$5/月**（可按 Usage 再调） |

### Instructions（整段粘贴）

```
请阅读 @templates/weekly-prompt.md（信息雷达 4.0.1），严格按其中 CHEAT 规则生成。

主线：独立游戏/单人小品 + Vibe Coding 做游戏的技术（引擎 MCP、生图/精灵图、游戏向工具）；其次才是可小做的机会/案例。
弱相关（API 中转账单、纯 WP 交付、内网数据库网关、职场仲裁等）禁止进「本周试一试」，默认观察/跳过/B3/附录溢出。

优先只读 data/weekly-digest/ 本期 YYYY-Www.json；不要通读全部 raw/daily-index，仅缺原文时点查。
再读上一期周报（A 跟进台 + 条目标题 + 附录上周状态）。
输出 reports/weekly/YYYY-Www.md：周号必须与 digest 的 ISO 周对齐；禁止覆盖其他周的旧文件来重跑。

「本周试一试」≤2：必须是动手推进（安装试用/最小切片）；禁止用「只找第二源」占试一试；至少 1 条是游戏向技术或可玩切片。
B/C/D 详情用薄卡片（≤5 字段），不要写「接下来怎么看」（只写在 A）。
专名首次必须括号人话。附录审计≤12 行。
B/C/D 正文禁止联网；附录竞品+D2 补页合计≤3 次并审计。
不要 @ .cursor/skills/。
完成后 commit 并 push 一个文件到 main，不要只留在 cursor/* 分支。
```

> 须先将最新 `templates/weekly-prompt.md` push 到 GitHub，再 **Run now**。

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
| 仍跟中转价/WP 当试一试 | 确认已 push 4.0.1 prompt，并更新云端 Instructions |
| 周号错乱 / 覆盖旧周 | Instructions 含 CHEAT-WEEK；检查 digest 文件名 |
| token 仍很高 | Automations 无法关 Max；靠「只读 digest、点查 raw」降上下文 |
| 邮件摘要旧格式 | 周报须含 `## A · 本周跟进台` |
