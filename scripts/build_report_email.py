#!/usr/bin/env python3
"""Convert report Markdown files to a styled HTML email body."""

from __future__ import annotations

import sys
from pathlib import Path

import markdown

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
    background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
    border-left: 4px solid #2563eb;
    border-radius: 0 6px 6px 0;
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
  tr:nth-child(even) td { background: #f9fafb; }
  a { color: #2563eb; text-decoration: none; }
  a:hover { text-decoration: underline; }
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
    border-radius: 8px;
    font-size: 13px;
    color: #6b7280;
    border: 1px solid #e5e7eb;
  }
  em { color: #6b7280; }
</style>
"""


def markdown_to_html(text: str) -> str:
    html = markdown.Markdown(
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    ).convert(text)
    html = html.replace(
        "<h2>模块 ",
        '<h2 class="module-heading">模块 ',
    )
    return html


def build_email_html(paths: list[Path]) -> str:
    sections: list[str] = []
    for i, path in enumerate(paths):
        if i > 0:
            sections.append(f'<div class="report-sep">📄 {path.as_posix()}</div>')
        sections.append(markdown_to_html(path.read_text(encoding="utf-8")))
    body = "\n".join(sections)
    return (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f"{EMAIL_CSS}</head><body>{body}</body></html>"
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
