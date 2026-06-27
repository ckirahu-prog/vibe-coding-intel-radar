# 信息雷达项目 — 开发心得与避坑指南

> 记录「AI 游戏 & Vibe Coding 信息雷达」从零到 **2.0 Final** 的经验，供下次做同类产品时复用。  
> 项目仓库：[vibe-coding-intel-radar](https://github.com/ckirahu-prog/vibe-coding-intel-radar)

---

## 一、我们最终做成了什么（2.0 Final）

**目标**：零基础可读的单文件中文周报——**副业机会（中国本土）** + **AI 游戏 / 热门题材** + **Vibe 商业化**，关机也能跑，成本可控，QQ 邮箱送达。

**最终架构**：

```
每天 08:00  GitHub Actions 采集 → data/raw/ + data/daily-index/（免费，无 LLM）
周六 09:00  Cursor Weekly Automation → reports/weekly/YYYY-Www.md（单文件四模块）
                    │
                    └── push 触发 Send Report Email → QQ 邮箱（一份 HTML）
```

**2.0 关键决策**：

| 决策 | 原因 |
|------|------|
| **单文件四模块**（A/B/C/D） | 一条阅读线；邮件只发一份 |
| **方法论内嵌 Prompt** | 不 @ 5 个 skill → 省 token、固定输入 |
| **A4 + B2 有限联网 ≤3/周** | 竞品与 Steam/itch 需补全；其余禁网控幻觉 |
| **中文源 + Steam/itch** | 副业 friction 与 B2 题材主信号 |
| **A1 宁可空不凑数** | 避免 AI 编造需求 |

**刻意没做的**：日频 LLM、Apify、第二条 Automation、双文件主刊+副刊、Automation @ skills。

---

## 二、核心方法论（下次做同类产品直接用）

### 2.1 三层拆分，别用一个工具包打天下

| 层级 | 目标 | 推荐方案 | 原因 |
|------|------|----------|------|
| **采集** | 稳定、便宜、可定时 | GitHub Actions + RSS/API + 去重 | 无 LLM、公开 repo 免费 |
| **解读** | 结构化、有深度 | Cursor Automation + **单 Prompt + 内嵌 cheatsheet** | 低频 LLM；规则固定 |
| **触达** | 送到手边、可读 | SMTP + `build_report_email.py` HTML | 模块 h2 可加分隔样式 |

### 2.2 先定 mock，再写 Prompt 和源

1. 链接列表 → 太薄  
2. 案例拆解表 → 1.0  
3. **2.0**：四模块单文件 + `docs/mock-weekly-2.0.md` 假数据样例  

**下次做法**：mock 定稿后再改 `sources.yaml` 和 `weekly-prompt.md`。

### 2.3 Prompt = 填表机器 + 分区联网策略

- 统一「案例卡片」表头（A1/A2/B1/B2/C1）
- 原文没有就「未知」，**禁止编造**
- **分区禁网**：A1–A3、B1、C 只读仓库；A4+B2 共享 ≤3 次/周
- D3 **一处**审计联网；D4 三行行动（副业/游戏/商业化）
- 处理条数上限（80 条）

### 2.4 数据源比 Prompt 更重要

- **A 级源**：垂直必收录  
- **B 级源**：关键词命中（中文副业用 friction 关键词，不用宽泛 `ai`）  
- **中文社区 60% + 媒体 40%**：媒体 alone 不进 A1  
- **`manual-urls.yaml`**：提升 A1/B1 密度最快  

**运维**：上线约 1 周后读 `data/stats.json`，长期 0 命中源从 `sources.yaml` 删除。

### 2.5 Skills 与 Automation 分离

- `.cursor/skills/` **保留供本地参考**  
- Automation **只读** `templates/weekly-prompt.md` + 内嵌 `methodology-cheatsheet.md`  
- **改 skill 须同步改 cheatsheet**（见 `SKILLS-MANIFEST.md`）

---

## 三、踩过的坑（现象 → 原因 → 修复）

### 3.1 邮件：Actions 绿色成功，但没收到信

**修复**：文件名正则 `'^reports/(daily|weekly)/.+\.md$'`；push 无报告时 exit 1；手动 Run `weekly`。

### 3.2 邮件：满屏 `###`

**修复**：`scripts/build_report_email.py` 预渲染 HTML；2.0 为 `## 模块` h2 加 `.module-heading` 样式。

### 3.3 双 Prompt + @ Skills token 爆炸

**现象**：单次 Automation 可能多读 1–2 万 token skill 全文。

**修复（2.0 Final）**：单 Prompt 内嵌 ~800–1200 字 cheatsheet；废弃 `side-hustle-prompt.md`。

### 3.4 副业「需求」被 AI 编造

**修复**：A1 准入：friction 引用 ≤40 字 + 场景 + URL；媒体 alone 不进 A1；单源标「待交叉验证」。

### 3.5 B2 推 3A / 联机大作

**修复**：CHEAT-GENRE strict scope；无热门依据+日期+URL 不进 B2 主表。

### 3.6 本地 `git push` 不稳定

见 `docs/GITHUB-SYNC-FIX.md`；skills 可 raw 同步。

---

## 四、推荐实施顺序（2.0）

1. **`docs/mock-weekly-2.0.md`** + **`templates/methodology-cheatsheet.md`**
2. **`config/topics.yaml`** 加 `sideline-pain-opportunity`；**`sources.yaml`** 加中文源 + Steam/itch
3. **`scripts/collect.py`** 跑通；Actions 采 1 周 → **stats 删 0 命中源**
4. **`templates/weekly-prompt.md`** 重写（内嵌 cheatsheet + 四模块）
5. **Automation** 仅 `@templates/weekly-prompt.md`；Run now 审计 D3/A1/B2
6. **发信** 单文件；更新 README

---

## 五、上线前检查清单（2.0）

```
交付物
- [ ] mock-weekly-2.0.md 结构与字段认可
- [ ] 单文件 YYYY-Www.md，无 side-hustle 副刊

采集
- [ ] sideline-pain-opportunity 主题 + 中文源已加
- [ ] collect 跑通；1 周后 stats 删死源

解读
- [ ] Prompt：分区联网、A4+B2 ≤3、禁止编造
- [ ] Automation：零 @ skill；Spend limit $5

触达
- [ ] 手动 Run Send Report Email → weekly，HTML 可读
- [ ] push 触发排除 *-side-hustle.md

验收
- [ ] A1 2–3 簇或诚实为空
- [ ] B2 strict scope + 热门依据
- [ ] D3 联网审计完整
```

---

## 六、可复用文件（本仓库）

| 文件 | 作用 |
|------|------|
| `templates/methodology-cheatsheet.md` | 5 块 CHEAT 规则（Prompt 提炼源） |
| `templates/weekly-prompt.md` | 2.0 单文件 Prompt |
| `docs/mock-weekly-2.0.md` | 四模块排版样例 |
| `config/sources.yaml` | 含 V2EX/36kr/Steam/itch 等 |
| `scripts/build_report_email.py` | Markdown → HTML（模块 h2 样式） |
| `.cursor/automation-draft.md` | 单 Prompt Instructions |

---

## 七、一句话总结

> **免费规则引擎收素材（含中文 friction 源），低频 LLM 按四模块固定表格解读，有限联网只给竞品与题材，HTML 单封邮件送达——2.0 Final 验证过的省力、可控路线。**

---

## 八、2.0 Final 之后的新增踩坑（2026-06-26 蒸馏）

> 来源：commit `efec8fe`（邮件渲染修复）+ 推送 2.0 期间的 Git 协作过程。

### 8.1 邮件：QQ 邮箱里表格/样式全丢 [presentation]

**现象**：源码 Markdown 正常，但 QQ 邮箱收到的是无表格、无样式的纯文本块。

**三个并发根因 → 修复**（见 `scripts/build_report_email.py`）：
- QQ 等客户端**剥离 `<head>` 内 `<style>`** → 把关键样式**内联到标签上**（`BODY_STYLE` + `inline_email_styles`），并避免依赖 `linear-gradient`/`border-radius`/`nth-child` 等易被吞的属性。
- 案例卡片是**两列无表头**的伪表格，缺 GFM 分隔行 `|---|---|` → markdown 库不渲染为 `<table>` → `fix_markdown_tables` **自动补插分隔行**再转换。
- **经验**：「在源格式里正确」≠「在真实客户端里正确」，邮件/IM 类交付必须在目标客户端实测。

### 8.2 邮件：手动触发默认发了旧日报 [integration/ops]

**现象**：手动 Run 邮件工作流，开头一堆原始 RSS 链接标题。

**根因 → 修复**：手动触发 `send_latest` 默认 `both`，把旧格式日报（满是原始链接）也发了 → 改默认 `weekly`（`send-report-email.yml`）。

**经验**：手动/高风险触发的**默认值要选最安全那个**，别让误触发出脏结果。

### 8.3 Git：自动采集 bot 把 main 推歪，本地 push 被拒 [execution/ops]

**现象**：每天 `chore(intel): daily collect` 由 Actions 直接提交到 main，本地历史落后 → `git push` 被拒 → `rebase` 起冲突。

**处理路径**：`git fetch` → `reset --hard origin/main` → `cherry-pick` 目标提交（比 rebase 更干净）→ 手动解 `build_report_email.py` 冲突 → `--continue`。

**经验**：
- **会自动提交到共享分支的 bot 会让本地历史频繁分叉**；本地动手前先 `fetch`，推之前先同步。
- 历史已纠缠时，**挑单个提交 `cherry-pick` 通常比 `rebase` 整条线更省事**。
- `reset --hard` 后可能 `Author identity unknown` → 临时设 `GIT_AUTHOR_NAME/EMAIL` 环境变量即可提交。

### 8.4 本地 Python/pip 不可用，改走 CI [execution]

**现象**：Windows PowerShell 下 `python`/`pip` 被禁用或不在 PATH，`collect.py` 跑不起来。

**修复/经验**：不强求本地环境可复现，**用 GitHub Actions 跑采集与验证**作为可靠回路；本地仅做编辑。

---

## 九、2026-06-27 周六运维复盘（邮件 + push + W27 验收）

> 来源：W27 Automation 成功但用户未收信；Actions 报错；commit `cdf58aa` / `cfc311b`；中国大陆 push 不稳定实测。

### 9.1 周六没收到邮件：周报已在周中 push 过 [integration/ops]

**现象**：用户期待周六 09:00 收信，但 6/26 试跑已 push `2026-W26`，6/27 上午无新 `reports/weekly/` commit → **发信 workflow 根本不触发**。

**根因**：发信仅 `on.push paths: reports/weekly/**`，**没有 cron**（当时版本）。

**修复**：加 **周六 10:00 定时兜底**（`cdf58aa`，cron `0 2 * * 6`），手动/定时模式改为「取最新周报」而非只看本次 push diff。

**经验**：「定时生成」和「push 触发触达」是两条链；若允许试跑提前产出，必须加 **兜底触达**，不能假设「周六一定会产生新 push」。

### 9.2 W27 已生成但发信 Actions 报 exit 1 [integration]

**现象**：Cursor Automation 09:02 成功 push `2026-W27`（`226c318`），但 Send Report Email 红色失败：`Push 触发了发信 workflow，但未检测到 reports/*.md 变更`。

**根因**：检测逻辑用 `git diff-tree` **只看 HEAD 一个 commit**。一次 push 若含多个 commit（path filter 因中间某 commit 改了 `reports/weekly/**` 而触发，但 HEAD 是别的文件如 workflow），就会误报。

**修复**（`cfc311b`）：
- `fetch-depth: 0`
- 用 `github.event.before..github.sha` **整次 push diff** 找报告文件
- 仍找不到时 **回退发最新周报**，避免 exit 1

**经验**：path filter 触发 ≠ HEAD 含目标文件；push 触发型下游必须扫 **整次 push 范围**。

### 9.3 中国大陆本地 push 不稳定，云端 Automation push 可靠 [execution]

**现象**：本地 `git push` 多次 `Failed to connect` / `Connection reset`；同一时段 Cursor Cloud Agent push W27 成功。

**处理**：网络恢复后 `git fetch` → `stash` → `pull --rebase` → 设 `GIT_AUTHOR_*` 环境变量 → push 成功。

**经验**：
- **写+push 尽量交给云端 agent**（Automation 已验证）；本地以编辑、pull、手动 Actions 为主。
- 不稳定网络下：**HTTPS + 代理** 或 **SSH 443**（`ssh.github.com:443`）二选一固定配置。
- push 前先 `fetch`，有 bot 自动提交时优先 `rebase`/`cherry-pick`，避免 history 纠缠。

### 9.4 W27 端到端验收（Automation 链路通） [product]

**已验证**（`226c318`）：
- 单文件四模块结构正确；A 模块 3 簇有 friction 引用（均标单源待交叉验证）
- B2 有 Steam 依据；D3 联网 2/3 在配额内
- 直接 push 到 `main` 符合 Instructions

**待用户确认**：修复 push 后，手动 Run Send Report Email → `weekly` 或等周六 10:00 兜底，确认 QQ 邮箱收到 W27。

---

*文档版本：2026-06-27 · 追加第九节（周六邮件运维 + W27 验收）*
