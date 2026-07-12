# 周报任务型框架 4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把周报从领域平铺（副业/游戏/商业化）改成任务型结构（跟进台 → 机会 → 技术 → 游戏启发 → 附录），并让邮件摘要卡与人话写作规则落地。

**Architecture:** 规范真相源是 `docs/superpowers/specs/2026-07-12-weekly-report-task-framework-design.md`。Automation 只读 `templates/weekly-prompt.md`，故主改造在该 prompt + `docs/mock-weekly-4.0.md` 样例；`scripts/build_report_email.py` 改摘要卡解析以匹配 A 跟进台；文档（README / automation-draft / PILOT）与版本号对齐 4.0。采集/digest 流水线不改。

**Tech Stack:** Markdown 模板、Python 3（email builder）、现有 GitHub Actions 发信

## Global Constraints

- 单文件周报；B+C+D 展开卡合计 ≤15；A 5–7 条（可更少）；试一试 ≤2；跳过 ≤2
- 人话优先；专名首次括号解释；事实/【判断】/【推断】/【估计】分标
- 技术过门槛后优先占 A ≥1；禁止硬塞；宁缺毋滥
- 摘要卡解析失败 → 明文降级，不猜内容、不回退「只做 1 件事」
- 不拆双邮件；不重写 digest/collect

## File map

| 文件 | 职责 |
|------|------|
| `templates/weekly-prompt.md` | Automation 生成规范（主改造） |
| `docs/mock-weekly-4.0.md` | 假数据排版样例 |
| `scripts/build_report_email.py` | 邮件摘要卡提取 |
| `scripts/test_build_report_email.py` | 摘要卡单测 |
| `README.md` / `.cursor/automation-draft.md` / `docs/PILOT-CHECKLIST.md` | 对外说明与验收 |
| `docs/superpowers/specs/2026-07-12-*.md` | 已定规格（状态改为已批准） |

---

### Task 1: 提交修订规格 + 本计划

**Files:**
- Modify: `docs/superpowers/specs/2026-07-12-weekly-report-task-framework-design.md`（状态行）
- Create: `docs/superpowers/plans/2026-07-12-weekly-report-task-framework.md`

- [ ] **Step 1:** 规格状态改为「已批准」
- [ ] **Step 2:** 保存本计划文件
- [ ] **Step 3:** Commit

```bash
git add docs/superpowers/
git commit -m "docs: approve task-framework spec and add implementation plan"
```

---

### Task 2: 重写 `templates/weekly-prompt.md` 为 4.0

**Files:**
- Modify: `templates/weekly-prompt.md`（整文件）

**Produces:** Automation 可按新结构生成 `reports/weekly/YYYY-Www.md`

- [ ] **Step 1:** 将标题/角色改为「信息雷达 4.0 · 任务型周报」；读者描述强调技术不多、要跟进清单
- [ ] **Step 2:** 更新「你的任务」：上期只读「A 跟进台 + B1/B2 + C 条目标题 + 附录上周状态」；digest `multi_source` 仍可用于 B1 双源
- [ ] **Step 3:** 改 CHEAT 命名对齐新模块：
  - CHEAT-ICP / REVIEW / CROSS → **B1 机会**（原 A1 规则）
  - CHEAT-COMP → 附录竞品
  - CHEAT-MOM → A「本周试一试」动作
  - CHEAT-TREND → A 周对周短标 + 附录完整状态
  - CHEAT-GENRE → D2
  - 新增 CHEAT-VOICE（人话）、CHEAT-TECH（C 成熟度依据）、CHEAT-QUOTA（条数与总量）、CHEAT-LABEL（事实标记）
- [ ] **Step 4:** 固定报告结构替换为规格 §3–§5 的 Markdown 骨架（A 四档、B1–B3、C1–C4、D1–D4、附录）
- [ ] **Step 5:** 质量检查清单对齐规格 §10
- [ ] **Step 6:** Commit `feat(intel): weekly prompt 4.0 task framework`

---

### Task 3: 新增 `docs/mock-weekly-4.0.md` 样例

**Files:**
- Create: `docs/mock-weekly-4.0.md`
- Optional keep: `docs/mock-weekly-2.0.md`（标注历史）

- [ ] **Step 1:** 用假数据写完整一期：A 6 条含试一试/观察/收藏/跳过与周对周短标；B/C/D 展开卡合计 ≤15；人话背景句；词表在附录
- [ ] **Step 2:** 文首注明「假数据 · 对齐 weekly-prompt 4.0」
- [ ] **Step 3:** Commit

---

### Task 4: 邮件摘要卡解析跟进台 + 单测

**Files:**
- Modify: `scripts/build_report_email.py`（`extract_summary_card` 及模块 heading 样式）
- Create: `scripts/test_build_report_email.py`

**Interfaces:**
- `extract_summary_card(text: str) -> str`
- 解析 `## A ·` / `## 本周跟进台` 下列表项；优先含「本周试一试」「继续观察」的条目，最多 5 条
- 兼容旧稿：若仍有 `**本周只做 1 件事**` 且无 A 跟进台，可显示旧行动行（过渡）
- 新旧皆无 → 若有周期行则只显示周期 +「请打开正文看本周跟进台」；皆无则返回 `""`

- [ ] **Step 1:** 写失败单测（4.0 样例片段应出现跟进条目；无跟进台有周期时应降级文案；空输入返回空）
- [ ] **Step 2:** 实现解析逻辑；`h2` 替换同时匹配 `模块 ` 与 `A ·`/`B ·`/`C ·`/`D ·`/`附录`
- [ ] **Step 3:** `python -m pytest scripts/test_build_report_email.py -v`（或 unittest）通过
- [ ] **Step 4:** 对 mock 跑 `python scripts/build_report_email.py /tmp/out.html docs/mock-weekly-4.0.md` 目测摘要卡
- [ ] **Step 5:** Commit

---

### Task 5: 文档与验收清单对齐 4.0

**Files:**
- Modify: `README.md`（架构图、模块说明、FAQ）
- Modify: `.cursor/automation-draft.md`
- Modify: `docs/PILOT-CHECKLIST.md`
- Modify: `templates/side-hustle-prompt.md` 指向说明（若仍存在）

- [ ] **Step 1:** README 改为任务型四模块 + 附录；去掉「副业 A 经常为空」过时表述或改写
- [ ] **Step 2:** automation-draft Instructions 仍只 @ weekly-prompt；描述改为 4.0
- [ ] **Step 3:** PILOT 增加：A 档位配额、总量 ≤15、人话抽查、摘要卡跟进名单、W28/样稿 30 秒对比项
- [ ] **Step 4:** Commit `docs: align README and pilot checklist with weekly 4.0`

---

### Task 6: W28 对照样稿（只读素材重排，不替代历史真稿）

**Files:**
- Create: `docs/mock-from-w28-4.0.md`（基于 W28 真实素材重写成 4.0 结构，标明「对照样稿」）

- [ ] **Step 1:** 从 `reports/weekly/2026-W28.md` 抽取机会/技术/题材填入新骨架；遵守配额与人话
- [ ] **Step 2:** 自检验收清单 §10；与原 W28 开篇做 30 秒可读性自检笔记写在文件顶部
- [ ] **Step 3:** Commit

---

### Task 7: 收尾验证

- [ ] 跑 `python scripts/test_collect_unit.py` 与 `python scripts/test_build_report_email.py`
- [ ] `git status` 干净；规格/计划/模板/邮件/文档均已提交
- [ ] 向用户汇报：下一期 Automation 将产出 4.0；历史 W25–W28 不改写

---

## Spec coverage (self-review)

| 规格要点 | 任务 |
|----------|------|
| A/B/C/D/附录职责 | T2 |
| 条数与总量 | T2 CHEAT-QUOTA、T3/T6 样例 |
| 四档分流与筛选 | T2 |
| 周对周短标 | T2、T3 |
| 成熟度/事实标记 | T2 CHEAT-TECH/LABEL |
| 人话规则 | T2 CHEAT-VOICE |
| 邮件摘要与降级 | T4 |
| 文档/验收 | T5、T7 |
| 30 秒对比 | T6 |
