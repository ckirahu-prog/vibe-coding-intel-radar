#!/usr/bin/env python3
"""Convert report Markdown files to a styled HTML email body."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown

# QQ 等客户端常剥离 <head> 内样式，关键样式同时内联到标签上
EMAIL_CSS = """
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
      "Microsoft YaHei", sans-serif;
    line-height: 1.65;
    color: #1f2937;
    max-width: 720px;
    margin: 0 auto;
    padding: 20px;
    background: #ffffff;
  }
  h1 { font-size: 22px; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-top: 0; }
  h2 { font-size: 18px; margin-top: 28px; color: #1e40af; }
  h2.module-heading {
    margin-top: 36px;
    padding: 10px 14px;
    background: #eff6ff;
    border-left: 4px solid #2563eb;
  }
  h3 { font-size: 16px; margin-top: 20px; color: #374151; }
  h4 { font-size: 15px; margin-top: 16px; color: #4b5563; }
  p { margin: 10px 0; }
  blockquote {
    border-left: 4px solid #93c5fd;
    margin: 12px 0;
    padding: 8px 16px;
    background: #eff6ff;
    color: #1e3a8a;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 14px 0;
    font-size: 14px;
  }
  th, td {
    border: 1px solid #d1d5db;
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
  }
  th { background: #f3f4f6; font-weight: 600; }
  a { color: #2563eb; text-decoration: none; }
  hr { border: none; border-top: 1px solid #e5e7eb; margin: 24px 0; }
  ul, ol { padding-left: 22px; margin: 10px 0; }
  li { margin: 5px 0; }
  code {
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
  }
  .report-sep {
    margin: 32px 0 24px;
    padding: 10px 14px;
    background: #f9fafb;
    font-size: 13px;
    color: #6b7280;
    border: 1px solid #e5e7eb;
  }
  .summary-card {
    margin: 0 0 20px;
    padding: 14px 16px;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    font-size: 14px;
  }
  .summary-card .summary-stats { color: #0369a1; font-weight: 600; margin-bottom: 6px; }
  .summary-card .summary-action { color: #1f2937; }
</style>
"""

BODY_STYLE = (
    'font-family: "PingFang SC", "Microsoft YaHei", sans-serif; '
    "line-height: 1.65; color: #1f2937; max-width: 720px; "
    "margin: 0 auto; padding: 20px; background: #ffffff;"
)

PIPE_ROW_RE = re.compile(r"^\|.+\|$")
SEPARATOR_RE = re.compile(r"^\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|$")


def _pipe_cols(line: str) -> int:
    return len([c for c in line.strip().strip("|").split("|") if c.strip()])


def _is_separator_row(line: str) -> bool:
    return bool(SEPARATOR_RE.match(line.strip()))


def _is_pipe_row(line: str) -> bool:
    return bool(PIPE_ROW_RE.match(line.strip()))


def fix_markdown_tables(text: str) -> str:
    """Insert a GFM separator row for any pipe-table block missing one.

    3.0 的 weekly-prompt 已要求所有案例卡片自带表头（`| 字段 | 内容 |`），
    这里只兜底修复"忘记加分隔行"的情况，不再猜测/伪造表头内容。
    """
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not _is_pipe_row(line):
            out.append(line)
            i += 1
            continue

        block: list[str] = []
        while i < len(lines) and _is_pipe_row(lines[i]):
            block.append(lines[i])
            i += 1

        if len(block) >= 2 and _is_separator_row(block[1]):
            out.extend(block)
            continue

        cols = _pipe_cols(block[0])
        if cols >= 2:
            sep = "| " + " | ".join(["---"] * cols) + " |"
            out.append(block[0])
            out.append(sep)
            out.extend(block[1:])
            continue

        out.extend(block)

    return "\n".join(out)


def inline_email_styles(html: str) -> str:
    """QQ 邮箱等常忽略 head 样式，给关键标签加 inline style。"""
    html = html.replace(
        "<h1>",
        '<h1 style="font-size:22px;border-bottom:2px solid #2563eb;'
        'padding-bottom:8px;margin-top:0;">',
    )
    html = html.replace(
        '<h2 class="module-heading">',
        '<h2 style="font-size:18px;margin-top:36px;padding:10px 14px;'
        'background:#eff6ff;border-left:4px solid #2563eb;color:#1e40af;">',
    )
    html = html.replace(
        "<h2>",
        '<h2 style="font-size:18px;margin-top:28px;color:#1e40af;">',
    )
    html = html.replace(
        "<h3>",
        '<h3 style="font-size:16px;margin-top:20px;color:#374151;">',
    )
    html = html.replace(
        "<blockquote>",
        '<blockquote style="border-left:4px solid #93c5fd;margin:12px 0;'
        'padding:8px 16px;background:#eff6ff;color:#1e3a8a;">',
    )
    html = html.replace(
        "<table>",
        '<table style="border-collapse:collapse;width:100%;margin:14px 0;'
        'font-size:14px;">',
    )
    html = html.replace(
        "<th>",
        '<th style="border:1px solid #d1d5db;padding:8px 10px;background:#f3f4f6;'
        'font-weight:600;text-align:left;vertical-align:top;">',
    )
    html = html.replace(
        "<td>",
        '<td style="border:1px solid #d1d5db;padding:8px 10px;'
        'vertical-align:top;">',
    )
    html = html.replace(
        "<a ",
        '<a style="color:#2563eb;text-decoration:none;" ',
    )
    return html


STATS_LINE_RE = re.compile(r"^>\s*周期.*$", re.MULTILINE)
ACTION_LINE_RE = re.compile(r"^-\s*\*\*本周只做\s*1\s*件事\*\*[:：]?\s*(.+)$", re.MULTILINE)


def extract_summary_card(text: str) -> str:
    """手机邮件顶部摘要卡：周期/素材统计 + 本周唯一行动，方便一屏读完。
    仅在能明确解析到这两行时渲染；解析不到就跳过，不猜测内容。"""
    stats_match = STATS_LINE_RE.search(text)
    action_match = ACTION_LINE_RE.search(text)
    if not stats_match and not action_match:
        return ""

    parts = ['<div class="summary-card" style="margin:0 0 20px;padding:14px 16px;'
             'background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;font-size:14px;">']
    if stats_match:
        stats_text = stats_match.group(0).lstrip("> ").strip()
        parts.append(
            f'<div class="summary-stats" style="color:#0369a1;font-weight:600;'
            f'margin-bottom:6px;">{stats_text}</div>'
        )
    if action_match:
        parts.append(
            f'<div class="summary-action" style="color:#1f2937;">'
            f'👉 本周只做 1 件事：{action_match.group(1).strip()}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def markdown_to_html(text: str) -> str:
    text = fix_markdown_tables(text)
    html = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists"],
    ).convert(text)
    html = html.replace(
        "<h2>模块 ",
        '<h2 class="module-heading">模块 ',
    )
    return inline_email_styles(html)


def build_email_html(paths: list[Path]) -> str:
    sections: list[str] = []
    for i, path in enumerate(paths):
        if i > 0:
            sections.append(
                f'<div class="report-sep" style="margin:32px 0 24px;padding:10px 14px;'
                f'background:#f9fafb;font-size:13px;color:#6b7280;'
                f'border:1px solid #e5e7eb;">📄 {path.as_posix()}</div>'
            )
        raw_text = path.read_text(encoding="utf-8")
        if "reports/weekly" in path.as_posix() or "weekly" in path.parts:
            summary_html = extract_summary_card(raw_text)
            if summary_html:
                sections.append(summary_html)
        sections.append(markdown_to_html(raw_text))
    body = "\n".join(sections)
    return (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f"{EMAIL_CSS}</head>"
        f'<body style="{BODY_STYLE}">{EMAIL_CSS}{body}</body></html>'
    )


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: build_report_email.py OUTPUT.html FILE.md ...", file=sys.stderr)
        return 1
    out = Path(sys.argv[1])
    paths = [Path(p) for p in sys.argv[2:] if p.strip()]
    if not paths:
        print("No input files", file=sys.stderr)
        return 1
    for p in paths:
        if not p.is_file():
            print(f"Missing file: {p}", file=sys.stderr)
            return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_email_html(paths), encoding="utf-8")
    print(f"Wrote {out} ({len(paths)} report(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
