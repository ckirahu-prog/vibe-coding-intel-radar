# 项目 Skills 清单

> 安装方式：因本机 `git clone` / `npx skills add` 连 GitHub 443 不稳定，改为从 raw.githubusercontent.com 手动同步到 `.cursor/skills/`。  
> 若网络恢复，可用官方命令重装：`npx skills add <owner/repo@skill> -y`

| Skill | 来源 | 用途 |
|-------|------|------|
| `mom-test` | [wondelai/skills](https://github.com/wondelai/skills) | D4 验证行动、避免 leading question |
| `ideal-customer-profile` | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | A1 人群 / 场景 / JTBD |
| `review-mining` | [shawnpang/startup-founder-skills](https://github.com/shawnpang/startup-founder-skills) | 社区 friction 挖掘 |
| `competitor-analysis` | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | A4 竞品简表 |
| `design-game` | playableintelligence 镜像 | 本地参考；**B2 用 CHEAT-GENRE，不读全文** |

安装日期：2026-06-21（首批 3 个）· 2026-06-24（competitor-analysis、design-game）

---

## 2.0 Final：Automation **不 @ skills**

Cursor Weekly Automation 只读 [`templates/weekly-prompt.md`](../../templates/weekly-prompt.md)，其中内嵌 [`templates/methodology-cheatsheet.md`](../../templates/methodology-cheatsheet.md) 提炼规则。

**本地开发**时可 `@` skill 辅助写 Prompt / mock；**改 skill 时须同步改 cheatsheet**，避免漂移。

### 本地参考路径（Automation 勿用）

- `@.cursor/skills/mom-test/SKILL.md`
- `@.cursor/skills/ideal-customer-profile/SKILL.md`
- `@.cursor/skills/review-mining/SKILL.md`
- `@.cursor/skills/competitor-analysis/SKILL.md`
- `@.cursor/skills/design-game/SKILL.md`
