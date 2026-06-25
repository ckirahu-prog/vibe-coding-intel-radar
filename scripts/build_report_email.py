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
</style>
"""

BODY_STYLE = (
    'font-family: "PingFang SC", "Microsoft YaHei", sans-serif; '
    "line-height: 1.65; color: #1f2937; max-width: 720px; "
    "margin: 0 auto; padding: 20px; background: #ffffff;"
)

PIPE_ROW_RE = re.compile(r"^\|.+\|$")
SEPARATOR_RE = re.compile(r"^\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|$")

KV_FIRST_COLS = {
    "是什么", "关键证据", "为什么重要", "你可以做什么", "原文",
    "需求", "收益", "技术", "代表游戏", "热门依据", "类型特点",
    "吸引原因", "为何符合 solo+AI", "单人 scope", "AI 可介入",
}


def _pipe_cols(line: str) -> int:
    return len([c for c in line.strip().strip("|").split("|") if c.strip()])


def _is_separator_row(line: str) -> bool:
    return bool(SEPARATOR_RE.match(line.strip()))


def _is_pipe_row(line: str) -> bool:
    return bool(PIPE_ROW_RE.match(line.strip()))


def fix_markdown_tables(text: str) -> str:
    """Insert GFM table separators; weekly 案例卡片 uses 2-col rows without header."""
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
        if cols == 2:
            first_cells = {
                block_line.strip().strip("|").split("|")[0].strip()
                for block_line in block
            }
            if first_cells & KV_FIRST_COLS or len(block) >= 2:
                out.append("| 字段 | 内容 |")
                out.append("| --- | --- |")
                out.extend(block)
                continue

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
        sections.append(markdown_to_html(path.read_text(encoding="utf-8")))
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
