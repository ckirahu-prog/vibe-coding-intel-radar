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

## 十、2026-07-06 信息雷达 3.0 复盘

> 来源：commit `7753d91`（3.0：weekly digest prefilter、周对周追踪、源清理）、`README.md` 3.0 架构、`templates/weekly-prompt.md` 3.0 约束、`scripts/digest_weekly.py`、`data/stats.json` 中长期 0 命中/失败源记录，以及本次用户要求「周报信息更全更易读，更符合工具初衷」。

### 给人的心得

#### 产品设计 / 用户体验 / 项目节奏 / 运维判断

- 周报 2.0 已经能生成，但 456 条素材只让 LLM 现场挑 80 条，且 A1 多为「单源，待交叉验证」 -> 根因是把「筛选/聚类/找第二源」都丢给周六低频 LLM [data/prompt] -> 3.0 新增 `scripts/digest_weekly.py`，周五免费把近 7 天 raw 做去重、评分、top-80、跨源 `multi_source` 聚类 -> **经验**：信息产品的 LLM 应该主要做判断与解释，重复、排序、去重、粗聚类尽量先用便宜确定性的规则层完成。边界：规则预筛只能减少噪音，不能替代 A1 的 verbatim friction 审核。

- 2.0 周报每期都是高质量快照，但用户很难看出「上周机会有没有继续、行动有没有结果」 -> 根因是周期产物没有读取上一期状态 [product-design/user-experience] -> 3.0 让 `weekly-prompt.md` 读取上一期 `reports/weekly/` 的「本周决策/A1/A3/D4」，新增「上周回顾」和 A3 趋势标记（新增/持续 N 周/降温） -> **经验**：周期性情报产品不只要回答「本周有什么」，还要回答「上周判断现在怎么样」。边界：首期或历史格式不兼容时要明确写「无可比对」，不能为了连续性编造趋势。

- QQ 邮件 2.0 为兼容无表头案例卡片，在渲染层写了 `fix_markdown_tables` 猜表头逻辑 -> 根因是生成格式不标准，导致呈现层背了结构修复责任 [presentation] -> 3.0 从 prompt 规定所有案例卡片必须带 `| 字段 | 内容 |` 表头，邮件脚本只兜底补 GFM 分隔行，并加顶部摘要卡 -> **经验**：真实客户端可读性要从源格式约束开始，渲染层只做样式和极小兜底，不该猜业务结构。边界：旧历史内容仍可保留兼容兜底，但新内容必须由生成端输出标准结构。

- `data/stats.json` 已暴露 `sspai` 0 命中、`huxiu` 超时、V2EX 分区 feed 404，但 2.0 没把「删源/换源」变成固定运营动作 -> 根因是数据源健康没有纳入版本节奏 [data/ops] -> 3.0 下线长期失效源，启用无需 CLI 的 V2EX 官方 JSON API 源，并在 `PILOT-CHECKLIST.md` 里要求看 digest 的 `multi_source_clusters` -> **经验**：情报工具的质量上限首先由源决定，Prompt 优化之前要先清掉死源、补稳定源。边界：少量偶发失败不应立刻删源，必须看连续命中/错误趋势。

### 给 AI 执行的心得

#### Prompt / 证据 / 工具 / Git-CI-Automation / 失败处理

- `weekly-prompt.md` 2.0 只写「最多处理 80 条」，但没有机械输入文件约束 -> 根因是把预算限制写成自然语言愿望 [prompt/execution] -> 3.0 增加 `data/weekly-digest/YYYY-Www.json` 作为优先输入，`digest_weekly.py --top 80` 先截断，再由 prompt 读 digest -> **经验**：token/条数上限这类执行约束，能用脚本保证就不要只靠 prompt 自律。边界：探索性分析可先口头限量，但进入定时自动化后必须把限制落到文件或 CI。

- 本机 Windows 环境没有可用 Python（只有 Windows Store 占位别名），无法本地跑 `digest_weekly.py` -> 根因是本地运行环境不可控 [execution] -> 3.0 新增 `.github/workflows/unit-tests.yml`，并把 digest 逻辑的聚类/同源不合并/top-N 选择加入 `scripts/test_collect_unit.py` -> **经验**：当本地解释器不可用时，不要降低验证要求；把可运行测试固化进 CI，至少让远程 runner 覆盖关键路径。边界：CI 不能替代需要本地凭证/私网/GUI 的验收。

- 推送 3.0 时远程已有多条 bot 自动采集/周报 commit，本地 push 被拒 -> 根因是共享分支有定时 bot 直推 [git-ci-automation] -> 处理路径是 `git fetch` 查远程新增提交、`git pull --rebase origin main` 无冲突重放、再 push -> **经验**：有 bot 直推的仓库，提交前干净不代表推送前仍干净；push 被拒时先读远程新增 commit，优先 rebase 小范围本地提交。边界：若冲突复杂或本地提交很多，按第 8.3 节经验可改用干净基底 cherry-pick。

### 最高价值下一步

1. 等 `Weekly Digest` 和 `Unit Tests` 两个 GitHub Actions 至少各跑绿一次，确认 3.0 新脚本在远程 Python 环境可执行。
2. 连续观察 2–4 周 `data/weekly-digest/*.json` 的 `multi_source_clusters`：若仍为 0，说明免费跨源聚类不足，需要补 `manual-urls.yaml` 或开启周中 enrichment。
3. 生成第一期 3.0 周报后，重点验收「上周回顾」是否真的减少阅读成本，而不是新增一段模板化噪音。

---

---

## 十一、2026-07-12 信息雷达 4.0 / 4.0.1 复盘（任务型周报）

> 来源：commits `abe8b27`（规格）、`90ba167`（4.0 框架）、`763590a`（4.0.1 主线+薄卡）、`a1d563a`/`d62b74e`（周号权威与归档抢跑稿）、用户「信息很碎/看不懂」与可读性验收反馈、云端 Automation 试跑（Grok 4.5 Medium + Max ≈119.7 万 token）、错标/抢跑 `W29` 事故。

### 给人的心得

#### 产品设计 / 用户体验

- 3.0 结构「副业 A / 游戏 B / 商业化 C」能装下采集主题，但用户真实工作是「扫值得跟的机会/案例 + 可试的 Vibe 技术」 -> 根因是按**采集分类**组织阅读，而不是按**用户任务** [requirements/product-design] -> 4.0 改为 A 跟进台 → B 机会 → C 技术雷达 → D 游戏启发 → 附录 -> **经验**：情报产品的目录应按读者下一步动作排，主题线只当素材标签。边界：采集配置仍可按主题分源，不必与阅读 IA 一一对应。

- 开篇「本周只做 1 件事」+ 等权长表 -> 用户觉得碎、读完不知跟哪条 -> 根因是决策层太薄、证据层占主舞台 [user-experience] -> A 台四档（试一试/观察/收藏/跳过）+ 详情薄卡 ≤5 字段 + 「接下来怎么看」只写在 A -> **经验**：跟进类产物用档位分流，比统一行动清单或百科展开更省力。边界：合规审计类产物仍需要完整证据面，可放附录。

- 第一期 4.0 试跑里「中转价/WP」占试一试或观察，Godot-MCP 等才贴主线 -> 根因是 digest「什么吵跟什么」且试一试被「找第二源」占用 [product-design] -> 4.0.1 写死主线（游戏+Vibe 做游戏）、弱相关禁试一试、试一试必须动手且 ≥1 条 P0 技术/可玩切片 -> **经验**：编辑优先级要写进生成规范，不能假设模型会自动对齐用户目标。边界：主线外的强信号可进观察/B3，不要假装没看见。

#### 运维判断 / 项目节奏

- Automation 账单显示 Grok 4.5 Medium + **Max** + ~120 万 token，且平台规定 Cloud Automations **无法关 Max** -> 根因是把「关 Max」当成本旋钮，实际只能缩输入 [ops] -> Instructions 要求优先只读 digest、禁止通读 raw -> **经验**：平台强制大上下文时，成本控制靠输入裁剪与模型档位，不靠寻找不存在的开关。边界：本地 IDE Agent 仍可能可关 Max，不要与云端 Automation 混为一谈。

- 仓库出现文件名 `W29`、正文却是 07-04~10 或抢跑 07-13~19，而 digest 仍停在 `W28`、日历才 7/12 -> 根因是用「更大文件名」或错误抬周规则驱动生成 [ops/integration] -> 规定 `W_this`=digest 最大周（无则运行日 ISO 周），周期行=该周周一～周日，错标/大于本期的文件归档忽略 -> **经验**：周期产物的身份键必须来自权威日历/预筛文件名，不能来自「目录里最大的那个 md」。边界：人工明确要求重跑某一旧周时可以例外，但自动化默认禁止。

### 给 AI 执行的心得

#### Prompt / 证据

- 只改云端 Instructions 能快速纠选题，但卡片字段仍跟长模板走 -> 根因是 durable 规格在 `weekly-prompt.md`，Instructions 权重不够压住字段表 [prompt] -> 采用 **Instructions + prompt 小改**（薄卡、去重复下一步、CHEAT-FOCUS/TRY/WEEK）-> **经验**：云端短 Instructions 管「选什么」；长模板管「写成什么样」；两者要一起改才稳。边界：一次性试跑可只改 Instructions；进入例行自动化必须回写模板。

- 推广帖/自述仍可能进 B1，但若占试一试会虚增「可行动感」 -> 根因是软证据与主 CTA 未隔离 [evidence-rules] -> 软证据默认可观察/B3，禁止进试一试 -> **经验**：证据弱不等于不能写，但不能占最高行动档。边界：双源非推广吐槽仍可升级。

#### Git-CI-Automation / 失败处理

- 修复「禁止倒退覆盖」时曾写成 `R_max > D_max 则写 R_max`，结果在错标/抢跑 `W29` 上继续生成未来周 -> 根因是用文件名最大值当真相 [git-ci-automation] -> 撤销该抬周逻辑，归档抢跑稿，权威改回 digest/ISO -> **经验**：修复规则要用反例验收（错标更大文件名是否还会被选中）。边界：当 digest 周确实前进时，写更大周号是正确行为。

- 本地无 Python 时邮件摘要单测无法跑，但已加 `test_build_report_email.py` 进 CI -> 延续 3.0「本地环境不可靠就留 CI 路径」[execution]。

### 最高价值下一步

1. 云端 Instructions 换成含 digest/ISO 周号段的完整版；再试跑时应只更新/生成与 digest 一致的周，不再出现无 digest 的未来周。
2. 等周五产出下一期 digest 后，验收一期「干净」的 4.0.1（周号、主线试一试、薄卡、邮件跟进摘要）。
3. 对比关输入裁剪前后的 Automation Usage；若仍经常 >50–100 万 token，考虑换更便宜一等模型或进一步限制可读路径。

---

*文档版本：2026-07-12 · 追加第十一节（4.0 任务型周报 + 4.0.1 主线/周号复盘）*
