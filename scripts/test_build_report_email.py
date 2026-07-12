#!/usr/bin/env python3
"""Unit tests for weekly email summary-card extraction (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_report_email import extract_summary_card  # noqa: E402

SAMPLE_4_0 = """# 信息雷达周报 4.0 · 2026-W99

> 周期：2026-06-28 ~ 2026-07-03 | 素材 120 条（digest 精选 40 条）| 跟进台 6 条 | 正文展开卡 12 条

## A · 本周跟进台

### 本周试一试（≤2）

- **Godot-MCP（示例）**（技术 · 新出现）— 能让 AI 在游戏引擎里直接摆东西。接下来怎么看：装上，自己做一次「加个节点 → 运行 → 截张图」。 → [详情](#c-godot-mcp)
- **客服机器人代码看不懂**（机会 · 新出现）— 国内有人抱怨 AI 写的项目自己改不动。接下来怎么看：在 V2EX 再搜 3 条近一周帖。 → [详情](#b1-agent-maintain)

### 继续观察

- **小工具记住聊天进度**（案例 · 连续第 2 周）— 有人说两周就有几十个付费用户。接下来怎么看：看原帖。 → [详情](#b2-ambient)

### 先收藏

- **改完要交证明的小检查**（案例 · 新出现）— AI 说做完了却没测过时用得上。接下来怎么看：有项目再写清单。 → [详情](#b2-donecheck)

### 本周跳过（≤2，无详情链接）

- **某大厂套餐天天抢购** — 跳过原因：和做游戏主线关系弱。

## B · 机会与真实案例

正文…
"""

SAMPLE_LEGACY = """# 信息雷达周报 2.0 · 2026-W28

> 周期：2026-06-28 ~ 2026-07-03 | 素材 563 条

## 开篇 · 本周决策

- **副业**：示例
- **本周只做 1 件事**：在 V2EX 搜第二源（≤2 小时）。
"""

SAMPLE_STATS_ONLY = """# 信息雷达周报 4.0 · 2026-W99

> 周期：2026-06-28 ~ 2026-07-03 | 素材 10 条

## B · 机会与真实案例

无跟进台。
"""


def test_extract_follow_desk_prefers_try_and_watch():
    html = extract_summary_card(SAMPLE_4_0)
    assert "本周跟进" in html
    assert "Godot-MCP" in html
    assert "客服机器人" in html
    assert "小工具记住聊天进度" in html
    assert "本周只做 1 件事" not in html
    # 跳过档不应进摘要卡
    assert "套餐天天抢购" not in html
    # 「节点 → 运行」中的箭头不应截断文案
    assert "截张图" in html


def test_extract_legacy_action_line():
    html = extract_summary_card(SAMPLE_LEGACY)
    assert "本周只做 1 件事" in html
    assert "V2EX" in html


def test_extract_stats_only_fallback_message():
    html = extract_summary_card(SAMPLE_STATS_ONLY)
    assert "周期" in html
    assert "本周跟进台" in html
    assert "本周只做 1 件事" not in html


def test_extract_empty_returns_empty():
    assert extract_summary_card("# 标题\n\n正文") == ""


if __name__ == "__main__":
    test_extract_follow_desk_prefers_try_and_watch()
    test_extract_legacy_action_line()
    test_extract_stats_only_fallback_message()
    test_extract_empty_returns_empty()
    print("ok")
