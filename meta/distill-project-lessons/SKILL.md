---
name: distill-project-lessons
description: >-
  Distill objective, non-forced lessons from a project's iteration history, fix
  history, and conversation records. Splits findings into universal lessons
  (cross-project, no project-specific names) and project-type lessons. Covers
  product direction, UX, why bugs/changes happened, and vibe coding process
  efficiency. Use when the user asks to summarize project experience, do a
  retrospective, distill lessons, or capture vibe coding learnings.
disable-model-invocation: true
---

# Distill Project Lessons

## Purpose

Turn a finished or in-progress project into reusable lessons. Read what actually
happened (commits, fixes, conversation), then write two things:

- **Project-specific lessons** into the current project at `docs/PROJECT-LESSONS.md`
- **Universal lessons** appended into this skill's `library.md` (cross-project memory)

The core value is honesty: capture only lessons backed by real evidence. Do not
manufacture insights to fill a section.

## When to Use

The user says things like: 总结经验 / 复盘 / distill lessons / 项目蒸馏 /
retrospective / capture learnings.

---

## Step 0: Confirm scope (1 question only if unclear)

Default behavior: distill the **current repository**. Ask only if the project
root or the target lessons file is ambiguous.

---

## Step 1: Gather evidence (do not skip)

Collect from as many of these as available. Prefer primary evidence over memory.

- **Iteration history**: `git log --oneline -50` to see how the project evolved.
- **Why things changed**: `git log --oneline --grep=fix` and read the diffs of
  notable fix/revert commits. Each fix is a candidate "why a bug happened" lesson.
- **Conversation records**: the agent transcripts for this project (past chats).
  Look for: rejected approaches, repeated retries, scope changes, surprises,
  moments where the user corrected direction.
- **Current state**: existing `README`, docs, config, and any prior
  `docs/PROJECT-LESSONS.md` (extend, do not duplicate).

If a source is unavailable (e.g. no transcripts, git offline), proceed with what
exists and note the gap. Never block on a single source.

---

## Step 2: Attribute each finding to a layer

For every candidate lesson, identify which layer it really belongs to. This keeps
lessons transferable instead of anecdotal.

- requirements: deliverable was undefined or vague
- data: input quality / source reliability
- prompt: missing constraints, format, or evidence rules
- execution: tool / permission / network / runtime failure
- integration: downstream not triggered, wrong branch/path
- presentation: output not readable in the real client
- ops: scheduling, cost, credentials, long-term stability

---

## Step 3: Classify universal vs project-type

This split is mandatory and has a hard rule.

- **Universal** = applies to most projects. **No project names, file paths,
  source names, vendor names, or one-off incidents.** Write as
  principle + how-to-judge + action checklist.
- **Project-type** = useful to similar projects. May include concrete paths,
  tools, sources, and real incidents from this project.

If a "universal" lesson cannot survive without naming this project, it is not
universal: either generalize it or move it to project-type.

---

## Step 4: Apply the anti-forcing bar

Keep a lesson only if it passes all of these:

- It is backed by a real commit, diff, transcript moment, or code fact.
- It would change a decision next time (actionable, not a platitude).
- It is not already in `library.md` (dedup; merge instead of repeat).
- It is stated objectively, without inflating outcomes.

Drop anything that is generic advice the agent already knows
("write clean code", "test your app") unless this project gave it a specific edge.

---

## Step 5: Cover these dimensions (only where evidence exists)

- **Product design direction**: what the product really is, scope kept vs cut,
  and whether the direction proved right.
- **User experience**: how the end deliverable is consumed and what made it
  readable / usable or not.
- **Why bugs or changes happened**: root cause per fix, attributed to a layer.
- **Vibe coding process efficiency**: what made the AI workflow faster or slower
  (prompt structure, how tasks were handed off, mode usage, review loops,
  rework causes).

A dimension with no real evidence gets one honest line saying so, not filler.

---

## Step 6: Write outputs

### 6a. Project-specific file: `docs/PROJECT-LESSONS.md`

Create or extend it. Use this template:

```markdown
# <Project> — Lessons

> Distilled <date> from git history, fixes, and conversation records.

## What this project is
<one-paragraph definition + scope kept vs cut>

## What worked (validated)
- <claim> — evidence: <commit / file / transcript>

## Problems and root causes
- <symptom> → <root cause> [layer] → <fix or open>

## Product & UX lessons
- ...

## Vibe coding process lessons
- ...

## Highest-value next steps
1. ...
```

### 6b. Universal library: append to this skill's `library.md`

For each new universal lesson, append an entry in the library's format
(principle + how to judge + action checklist). **Dedup first**: if a similar
principle exists, refine it rather than adding a duplicate. Strip every
project-specific name before writing.

The library is written in Chinese. Keep new entries in Chinese.

---

## Step 7: Sync to GitHub

Persist all three outputs to GitHub so they survive across machines.

**Knowledge hub repo** (stores the skill + cross-project library):
`https://github.com/ckirahu-prog/Skills-and-Experience`, folder
`meta/distill-project-lessons/`. (Change this path if the user moves the hub.)

1. **Project lessons → current project's repo and hub repo.**
   If the current project is a git repo, commit and push `docs/PROJECT-LESSONS.md`.
   Also mirror the same file into the hub repo under
   `meta/distill-project-lessons/projects/<project-slug>/PROJECT-LESSONS.md`:

```bash
git add docs/PROJECT-LESSONS.md
git commit -m "docs: distill project lessons"
git push
```

2. **Library + this skill → hub repo.**
   Copy this skill's `SKILL.md` and `library.md` into the hub folder
   `meta/distill-project-lessons/`, then commit and push from the hub repo:

```bash
git add meta/distill-project-lessons/
git commit -m "chore(skill): sync distill-project-lessons + library"
git push
```

If the current project **is** the hub repo, both happen in one repo. If the hub
is a separate repo not checked out locally, tell the user which files to upload
rather than guessing credentials. Never create or change git config or remotes.

---

## Workflow checklist

Copy and track:

```
- [ ] Step 1: Gathered git history, fixes, transcripts, current docs
- [ ] Step 2: Attributed each finding to a layer
- [ ] Step 3: Split universal vs project-type (hard rule applied)
- [ ] Step 4: Passed anti-forcing bar (dropped filler)
- [ ] Step 5: Covered the 4 dimensions honestly
- [ ] Step 6a: Wrote/extended docs/PROJECT-LESSONS.md
- [ ] Step 6b: Appended deduped universal lessons to library.md (Chinese)
- [ ] Step 7: Synced project lessons + library + skill to GitHub
- [ ] Self-check: universal section has zero project-specific names
```

---

## Universal lessons library

Read and extend [library.md](library.md). It is the cross-project memory: every
run should leave it slightly richer and never contains project-specific names.
Before starting a new project, the user can read it as a pre-flight checklist.
