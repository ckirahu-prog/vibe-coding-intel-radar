---
name: distill-project-lessons
description: >-
  Distill objective, evidence-backed lessons from a project's iteration history,
  fixes, and conversation records. Splits lessons into project-specific output
  and a cross-project Chinese library, and classifies every lesson by audience
  (human vs AI execution), category, and root-cause layer. Use when the user asks
  to summarize project experience, do a retrospective, distill lessons, capture
  vibe coding learnings, or update the reusable lessons library.
disable-model-invocation: true
---

# Distill Project Lessons

## Purpose

Turn a finished or in-progress project into reusable lessons. Read what actually
happened (commits, fixes, conversation), then write two outputs:

- **Project-specific lessons** in the current project at `docs/PROJECT-LESSONS.md`
- **Universal lessons** in this skill's `library.md` (Chinese, cross-project memory)

The value is honesty: capture only lessons backed by real evidence. Do not
manufacture insights to fill a section.

---

## Step 0: Confirm scope

Default behavior: distill the **current repository**. Ask only if the project
root or target lessons file is ambiguous.

---

## Step 1: Gather evidence

Prefer primary evidence over memory. Use as many as available:

- **Iteration history**: recent `git log --oneline`
- **Why things changed**: fix/revert commits and their diffs
- **Conversation records**: agent transcripts, especially corrections, retries,
  scope changes, surprises, and user dissatisfaction
- **Current state**: README, docs, config, workflows, prior `docs/PROJECT-LESSONS.md`

If one source is unavailable, proceed and note the gap. Never block on a single
source.

---

## Step 2: Label each candidate lesson

Every candidate lesson must receive three labels.

### 2a. Root-cause layer

- requirements: deliverable was undefined or vague
- data: input quality / source reliability
- prompt: missing constraints, format, evidence rules
- execution: tool / permission / network / runtime failure
- integration: downstream not triggered, wrong branch/path
- presentation: output not readable in the real client
- ops: scheduling, cost, credentials, long-term stability

### 2b. Audience

- **human**: changes how the user should decide, design, prioritize, or operate
- **ai-execution**: changes how an agent/automation/CI should execute next time
- **both**: changes both human decision-making and AI execution

### 2c. Category

Use one or more:

- Human-facing: product-design / user-experience / project-rhythm /
  ops-decision / retrospective-judgment
- AI-execution: prompt-writing / evidence-rules / tool-use /
  git-ci-automation / failure-handling

---

## Step 3: Classify universal vs project-type

- **Universal** = applies to many projects. No project names, file paths, source
  names, vendor names, commit ids, or one-off incidents. Write in Chinese as:
  audience + category + principle + how to judge + action checklist + boundary.
- **Project-type** = useful to this or similar projects. May include concrete
  files, tools, sources, commits, and incidents.

If a universal lesson cannot survive without naming this project, it is not
universal: generalize it or move it to project-type.

---

## Step 4: Apply the anti-forcing bar

Keep a lesson only if all are true:

- Backed by a real commit, diff, transcript moment, user feedback, or code fact
- Would change a decision or execution path next time
- Not already in `library.md`; if similar, merge/refine instead of duplicating
- Stated objectively, without inflating outcomes
- Has a boundary: when not to apply it

If a candidate is only an implementation detail of an existing principle, merge
it into that principle's action checklist. Create a new entry only when it can
independently change future decisions or execution.

Drop generic advice the agent already knows unless this project gave it a
specific, transferable edge.

---

## Step 5: Cover dimensions honestly

Only cover dimensions with evidence. A dimension with no real evidence gets one
honest line saying so, not filler.

### Human lessons

- Product design: what the product is, scope kept vs cut, direction validated
- User experience: what the user actually receives/uses and whether it works
- Project rhythm: sequencing, mocks, narrow loops, review cadence
- Ops decisions: local vs cloud, scheduling, costs, ownership, manual fallback
- Retrospective judgment: what is worth distilling vs one-off noise

### AI execution lessons

- Prompt writing: constraints, input scope, output path, acceptance checks
- Evidence rules: citations, unknowns, confidence, anti-hallucination gates
- Tool use: where tools/web are allowed, budgets, audits
- Git/CI/Automation: branches, push ranges, cron, commits, runner choice
- Failure handling: exit behavior, fallback, warnings, retry path

---

## Step 6: Write outputs

### 6a. Project-specific file: `docs/PROJECT-LESSONS.md`

Create or extend it. Prefer appending a dated section. Use this shape:

```markdown
## <date/topic> 复盘

> 来源：<commits / workflows / transcript / user feedback>

### 给人的心得

#### 产品设计 / 用户体验 / 项目节奏 / 运维判断
- <symptom> -> <root cause> [layer] -> <fix> -> <lesson>

### 给 AI 执行的心得

#### Prompt / 证据 / 工具 / Git-CI-Automation / 失败处理
- <symptom> -> <root cause> [layer] -> <fix> -> <lesson>

### 最高价值下一步
1. ...
```

Do not rewrite old sections unless the user asks. Extend and dedup.

### 6b. Universal library: `library.md`

The library is Chinese and organized into two top-level audiences:

- `## 一、人类需要知道的心得`
- `## 二、AI 执行时需要知道的心得`

Entry format:

```markdown
### <精简原则标题>
受众：人类 / AI执行 / 两者
分类：产品设计 / 用户体验 / 项目节奏 / 运维决策 / Prompt编写 / 证据规则 / 工具使用 / Git-CI-Automation / 失败处理 / 复盘判断
原则：<一句话>
判断时机：<何时适用 / 如何检查>
行动：
- <可执行清单>
边界：<何时不适用，避免过度泛化>
```

Dedup first. If a similar principle exists, refine it rather than adding a new
one. Strip every project-specific name before writing.

---

## Step 7: Sync to GitHub

Persist all three outputs to GitHub so they survive across machines.

**Knowledge hub repo**:
`https://github.com/ckirahu-prog/Skills-and-Experience`, folder
`meta/distill-project-lessons/`.

1. **Project lessons -> current project's repo and hub repo.**
   Commit/push `docs/PROJECT-LESSONS.md` if changed. Mirror it into:
   `meta/distill-project-lessons/projects/<project-slug>/PROJECT-LESSONS.md`.

2. **Library + skill -> hub repo.**
   Copy this skill's `SKILL.md` and `library.md` into
   `meta/distill-project-lessons/`, then commit and push from the hub repo.

If the hub repo is not checked out locally, clone it or tell the user which
files to upload. Never change git config or remotes.

---

## Workflow checklist

```markdown
- [ ] Step 1: Gathered git history, fixes, transcripts, current docs
- [ ] Step 2: Labeled each candidate by layer + audience + category
- [ ] Step 3: Split universal vs project-type
- [ ] Step 4: Applied anti-forcing bar and merged implementation details
- [ ] Step 5: Covered human and AI-execution dimensions honestly
- [ ] Step 6a: Extended docs/PROJECT-LESSONS.md
- [ ] Step 6b: Updated Chinese library.md under the correct audience/category
- [ ] Step 7: Synced project lessons + library + skill to GitHub
- [ ] Self-check: universal library has zero project-specific names and no duplicates
```

---

## Universal lessons library

Read and extend [library.md](library.md). It is the cross-project memory. Before
starting a new project, the user can read the human section as a pre-flight
checklist and the AI-execution section as agent operating guidance.
