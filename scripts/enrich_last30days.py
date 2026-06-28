#!/usr/bin/env python3
"""Import or run last30days research into data/enriched/ for weekly report consumption."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENRICHED_DIR = ROOT / "data" / "enriched"
CLI_TIMEOUT_SEC = 600
URL_RE = re.compile(r"https?://[^\s\)\]>\"']+")


def slugify(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return (slug or "topic")[:max_len]


def extract_urls(text: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;)")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def guess_platform(url: str) -> str:
    host = re.sub(r"^www\.", "", url.split("/")[2] if "://" in url else "")
    mapping = {
        "v2ex.com": "v2ex",
        "zhihu.com": "zhihu",
        "reddit.com": "reddit",
        "old.reddit.com": "reddit",
        "bilibili.com": "bilibili",
        "youtube.com": "youtube",
        "youtu.be": "youtube",
        "github.com": "github",
        "news.ycombinator.com": "hackernews",
    }
    for key, name in mapping.items():
        if key in host:
            return name
    return host or "web"


def build_artifact(
    topic: str,
    topics: list[str],
    summary: str,
    confirming_urls: list[dict],
    *,
    source: str = "last30days",
    raw_path: str | None = None,
    brief_excerpt: str | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    artifact_id = hashlib.sha256(f"{topic}:{now.isoformat()}".encode()).hexdigest()[:16]
    return {
        "id": artifact_id,
        "topic": topic,
        "topics": topics,
        "created_at": now.isoformat(),
        "source": source,
        "summary": summary[:2000],
        "confirming_urls": confirming_urls,
        "brief_excerpt": (brief_excerpt or summary)[:4000],
        "raw_path": raw_path,
    }


def parse_brief_markdown(path: Path, topic: str) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8")
    urls = extract_urls(text)
    confirming = []
    for url in urls[:25]:
        confirming.append({
            "url": url,
            "title": "",
            "platform": guess_platform(url),
        })
    # First non-empty paragraph as summary
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    summary = paragraphs[0][:500] if paragraphs else f"Imported brief for {topic}"
    return summary, confirming


def find_last30days_script() -> Path | None:
    env_path = os.environ.get("LAST30DAYS_SCRIPT")
    if env_path:
        p = Path(env_path).expanduser()
        if p.is_file():
            return p

    candidates = [
        Path.home() / ".agents" / "skills" / "last30days" / "scripts" / "last30days.py",
        Path.home() / ".cursor" / "skills" / "last30days" / "scripts" / "last30days.py",
        Path.home() / ".claude" / "skills" / "last30days" / "scripts" / "last30days.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def run_last30days(topic: str, save_dir: Path) -> Path | None:
    script = find_last30days_script()
    if not script:
        raise RuntimeError(
            "last30days.py not found. Set LAST30DAYS_SCRIPT or use --import-brief."
        )

    save_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(script),
        topic,
        "--save-dir",
        str(save_dir),
        "--emit=markdown",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT_SEC,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "last30days failed")

    slug = slugify(topic)
    candidates = sorted(save_dir.glob(f"{slug}*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    any_md = sorted(save_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return any_md[0] if any_md else None


def write_artifact(artifact: dict, dry_run: bool = False) -> Path:
    date_str = artifact["created_at"][:10]
    slug = slugify(artifact["topic"])
    out_path = ENRICHED_DIR / f"{date_str}-{slug}.json"
    if dry_run:
        print(f"[DRY] would write {out_path}")
        return out_path
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize last30days output into data/enriched/")
    parser.add_argument("--topic", required=True, help="Research topic / query")
    parser.add_argument(
        "--topics",
        default="sideline-pain-opportunity",
        help="Comma-separated radar topic IDs (default: sideline-pain-opportunity)",
    )
    parser.add_argument(
        "--import-brief",
        type=Path,
        help="Import an existing last30days markdown brief instead of running the engine",
    )
    parser.add_argument(
        "--copy-raw-to",
        type=Path,
        help="Optional path to copy the source brief for archival",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned writes only")
    args = parser.parse_args()

    topic_ids = [t.strip() for t in args.topics.split(",") if t.strip()]
    brief_path: Path | None = None
    source = "last30days"

    if args.import_brief:
        brief_path = args.import_brief.expanduser()
        if not brief_path.is_file():
            print(f"Brief not found: {brief_path}", file=sys.stderr)
            return 1
        summary, confirming = parse_brief_markdown(brief_path, args.topic)
        raw_path = str(brief_path)
    else:
        if args.dry_run:
            script = find_last30days_script()
            print(f"[DRY] topic={args.topic!r} topics={topic_ids}")
            print(f"[DRY] last30days script: {script or 'NOT FOUND'}")
            write_artifact(
                build_artifact(args.topic, topic_ids, "(dry run)", [], source=source),
                dry_run=True,
            )
            return 0
        tmp_dir = ENRICHED_DIR / "_runs"
        brief_path = run_last30days(args.topic, tmp_dir)
        if not brief_path or not brief_path.is_file():
            print("last30days produced no markdown output", file=sys.stderr)
            return 1
        summary, confirming = parse_brief_markdown(brief_path, args.topic)
        raw_path = str(brief_path)

    if args.copy_raw_to and brief_path:
        dest = args.copy_raw_to.expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(brief_path, dest)
        raw_path = str(dest)

    artifact = build_artifact(
        args.topic,
        topic_ids,
        summary,
        confirming,
        source=source,
        raw_path=raw_path,
        brief_excerpt=brief_path.read_text(encoding="utf-8")[:4000] if brief_path else None,
    )
    write_artifact(artifact, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
