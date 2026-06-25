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

*文档版本：2026-06-21 · 对应 2.0 Final 单文件架构*
