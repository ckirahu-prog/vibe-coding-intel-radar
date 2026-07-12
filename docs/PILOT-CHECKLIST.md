# 部署后验证清单（Pilot Run）

> 本清单对应 **4.0 任务型周报**：每天只有免费采集，**没有独立日报**；周五 digest 预筛 + 周六周报是唯一需要人工验证的产出。1.0 时期的 `reports/daily/` 日报邮件已废弃；2.0/3.0 历史周报仍保留在 `reports/weekly/`，不改写。

Push 到 GitHub 后，按以下步骤验证系统正常运行。

## 立即验证（Day 0）

- [ ] **Push 代码**到 GitHub `main` 分支（含最新 `templates/weekly-prompt.md` 4.0）
- [ ] 打开 **Actions → Daily Intel Collect → Run workflow** 手动触发一次
- [ ] 确认 workflow 绿色通过
- [ ] 运行 `python scripts/collect.py --dry-run`，确认 Agent-Reach 中仍关闭的源显示 `[SKIP] ... disabled`
- [ ] 运行 `python scripts/test_collect_unit.py` 与 `python scripts/test_build_report_email.py`，全部 PASS
- [ ] 检查是否生成：
  - `data/raw/YYYY-MM-DD.json`
  - `data/daily-index/YYYY-MM-DD.md`（供 Automation 读取的素材索引，非最终报告）
  - `data/seen.json` 和 `data/stats.json` 有更新
- [ ] 配置 QQ 邮箱 Secrets：`MAIL_USERNAME`、`MAIL_PASSWORD`、`MAIL_TO`（见 README）

## 采集观察（Day 1–5）

- [ ] 查看 `data/stats.json`，标记连续失败（`errors > 0` 且长期无 `hits`）的源，从 `config/sources.yaml` 删除或修 URL
- [ ] 查看 `data/daily-index/`，评估三条主题线（副业/游戏/商业化）是否都有条目
- [ ] 若噪音多：编辑 `config/topics.yaml` 增加/收紧关键词
- [ ] 若漏报多：编辑 `config/sources.yaml` 加源或改 tier；本地可 `enabled: true` Agent-Reach 源

## 周五 Digest 验证

- [ ] 打开 **Actions → Weekly Digest → Run workflow** 手动触发一次
- [ ] 确认生成 `data/weekly-digest/YYYY-Www.json` 并已 commit
- [ ] 检查 JSON 中 `totals.selected` 是否接近 80、`totals.multi_source_clusters` 是否 > 0
- [ ] 若 `multi_source_clusters` 长期为 0：说明中文源覆盖仍不足同一事件的第二来源，考虑补 `manual-urls.yaml` 或跑 `enrich_last30days.py`

## 可选增强层验证（周中手动）

- [ ] `python scripts/enrich_last30days.py --topic "测试主题" --dry-run` 可运行
- [ ] 用 `--import-brief` 导入样例 markdown 后，`data/enriched/YYYY-MM-DD-*.json` 含 `confirming_urls`
- [ ] 高置信 URL 写入 `config/manual-urls.yaml` 后，下次 `collect.py` 收录为 `manual` 源
- [ ] 本地启用 `agent-reach-bili-ai-game` / `agent-reach-youtube-ai-gamedev`（`enabled: true`）后采集成功；GitHub Actions 缺 CLI 时该源 `[ERR]` 但不阻断 workflow

## 周报验证（4.0 · Day 0 或 Day 7）

- [ ] 按 [`.cursor/automation-draft.md`](../.cursor/automation-draft.md) 配置 Cursor Automation（Instructions 已是 4.0 文案）
- [ ] Dashboard 设 spend limit **$5/月**
- [ ] Automation Cron 设为 **`0 1 * * 6`**（北京时间周六 09:00，Weekly Digest 周五 22:00 UTC 已先跑完）
- [ ] 选手动 **Run now** 触发一次（不必等周六）
- [ ] 确认 `reports/weekly/YYYY-Www.md` 标题为 **4.0**，结构为 A/B/C/D/附录（不是旧「副业/游戏/商业化」）
- [ ] QQ 邮箱摘要卡显示 **本周跟进** 短名单（不是「只做 1 件事」）；解析失败时应提示打开正文跟进台
- [ ] A 档位配额：试一试 ≤2、跳过 ≤2；有周对周短标
- [ ] B+C+D 展开卡合计 ≤15；有「一句话背景」；人话抽查通过
- [ ] C 独立存在；技术不过度埋在游戏案例里
- [ ] 附录含质量说明 + 联网 ≤3；词表在附录
- [ ] 若 digest 中有 `multi_source: true` 簇，B1 是否正确引用为双源
- [ ] （可选）对照 [`docs/mock-from-w28-4.0.md`](mock-from-w28-4.0.md) 做 30 秒可读性对比
- [ ] 到 [cursor.com/dashboard](https://cursor.com/dashboard) → Usage 记录本次费用
  - 预期：**$0.15–$0.40/次**
  - 若超过 $1：检查是否用了 Opus 或 Agent 上网搜索了

## 调优参考

| 现象 | 操作 |
|------|------|
| Reddit 源 0 命中 | 正常，B 级需关键词；可改 tier 或加关键词 |
| Product Hunt 噪音大 | 在 keywords 加 `cursor`, `ai`, `saas` 等 |
| GitHub Search 重复 | seen.json 会去重，无需处理 |
| 周报内容编造 | 确认 prompt 含禁止编造与联网表 |
| B1 全是单源 | 先看 digest 的 `multi_source` 簇；仍不足再跑 `enrich_last30days.py` 或补 `manual-urls.yaml` |
| 邮件仍是旧摘要 | 确认周报有 `## A · 本周跟进台` 且已 push 新 `build_report_email.py` |
| Agent-Reach 源失败 | 正常（CI 无 CLI）；本地安装后 `enabled: true` |
| enrichment 未进周报 | 确认 JSON 在 `data/enriched/` 且日期在近 30 天内 |
| 月费超 $2 | 换便宜模型；prompt 限制 80 条（digest 已机械保证） |
| 读起来仍碎/像作业 | 检查试一试是否超过 2 条；是否每条都在派活 |

## 预期指标（2 周后评估）

| 指标 | 目标 |
|------|------|
| 采集有新内容天数 | ≥ 6/7 天 |
| digest 多源簇占比 | 逐步提升，非 0 |
| 周报阅读时间（正文） | **8–10 分钟**（附录另计） |
| 30 秒能说出 | ≥2 机会/案例 + ≥1 技术专名 |
| Automation 月成本 | < $2（Pro 额度 10% 以内） |
