#!/usr/bin/env python3
"""Daily intel collector: RSS/API fetch, dedup, tag, write raw JSON + daily report."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REPORTS_DIR = ROOT / "reports" / "daily"

SEEN_FILE = DATA_DIR / "seen.json"
STATS_FILE = DATA_DIR / "stats.json"
TOPICS_FILE = CONFIG_DIR / "topics.yaml"
SOURCES_FILE = CONFIG_DIR / "sources.yaml"
MANUAL_FILE = CONFIG_DIR / "manual-urls.yaml"

SUMMARY_MAX_LEN = 200
USER_AGENT = "IntelRadar/1.0 (github-actions; info-collector)"
GITHUB_API = "https://api.github.com"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_url(url: str) -> str:
    """Strip tracking params and fragments for dedup."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    drop_params = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "source", "fbclid", "gclid",
    }
    qs = parse_qs(parsed.query, keep_blank_values=False)
    clean_qs = {k: v for k, v in qs.items() if k.lower() not in drop_params}
    new_query = urlencode(clean_qs, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()[:16]


def truncate(text: str, max_len: int = SUMMARY_MAX_LEN) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def match_keywords(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(kw.lower() in lower for kw in keywords)


def classify_topics(
    title: str,
    summary: str,
    source_topics: list[str],
    tier: str,
    all_topic_keywords: dict[str, list[str]],
) -> list[str]:
    text = f"{title} {summary}"
    matched: set[str] = set()

    if tier == "A":
        matched.update(source_topics)
    else:
        for topic_id in source_topics:
            keywords = all_topic_keywords.get(topic_id, [])
            if match_keywords(text, keywords):
                matched.add(topic_id)

    # Cross-tag: check other topics' keywords for broader sources
    for topic_id, keywords in all_topic_keywords.items():
        if topic_id not in source_topics and match_keywords(text, keywords):
            matched.add(topic_id)

    return sorted(matched)


def fetch_rss(source: dict) -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(source["url"], headers=headers, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    items = []
    for entry in feed.entries[:50]:
        link = entry.get("link") or entry.get("id") or ""
        title = entry.get("title", "Untitled")
        summary = entry.get("summary") or entry.get("description") or ""
        published = entry.get("published") or entry.get("updated") or ""
        items.append({
            "title": truncate(title, 300),
            "url": link,
            "summary": truncate(summary),
            "published": published,
        })
    return items


def fetch_github_search(source: dict) -> list[dict]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    token = __import__("os").environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {
        "q": source["query"],
        "sort": "updated",
        "order": "desc",
        "per_page": 20,
    }
    resp = requests.get(f"{GITHUB_API}/search/repositories", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for repo in data.get("items", []):
        items.append({
            "title": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "summary": truncate(repo.get("description") or ""),
            "published": repo.get("updated_at") or repo.get("pushed_at") or "",
        })
    return items


def record_stat(stats: dict, source_id: str, count: int, error: str | None = None) -> None:
    sources = stats.setdefault("sources", {})
    entry = sources.setdefault(source_id, {"hits": 0, "errors": 0, "last_error": None})
    entry["hits"] = entry.get("hits", 0) + count
    if error:
        entry["errors"] = entry.get("errors", 0) + 1
        entry["last_error"] = error
    stats["last_updated"] = datetime.now(timezone.utc).isoformat()


def process_manual_urls(
    manual: dict,
    seen: dict,
    topic_keywords: dict[str, list[str]],
    topic_names: dict[str, str],
) -> list[dict]:
    new_items = []
    for entry in manual.get("urls") or []:
        url = entry.get("url", "")
        if not url:
            continue
        h = url_hash(url)
        if h in seen.get("urls", {}):
            continue
        topics = entry.get("topics") or []
        item = {
            "id": h,
            "title": entry.get("title") or url,
            "url": url,
            "summary": entry.get("note") or "",
            "source_id": "manual",
            "source_name": "Manual",
            "topics": topics,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "published": "",
        }
        seen.setdefault("urls", {})[h] = {"url": url, "first_seen": item["fetched_at"]}
        new_items.append(item)
    return new_items


def generate_daily_report(date_str: str, items: list[dict], topic_names: dict[str, str]) -> str:
    lines = [f"# 信息雷达日报 {date_str}", ""]

    by_topic: dict[str, list[dict]] = {}
    untagged: list[dict] = []
    for item in items:
        if item["topics"]:
            for t in item["topics"]:
                by_topic.setdefault(t, []).append(item)
        else:
            untagged.append(item)

    topic_order = ["ai-game-dev", "vibe-coding-commercial"]
    for topic_id in topic_order:
        name = topic_names.get(topic_id, topic_id)
        topic_items = by_topic.get(topic_id, [])
        lines.append(f"## {name} ({len(topic_items)} 条)")
        if not topic_items:
            lines.append("")
            lines.append("_无新增_")
        else:
            for item in topic_items:
                summary_part = f" | {item['summary']}" if item["summary"] else ""
                lines.append(f"- [{item['title']}]({item['url']}) — {item['source_name']}{summary_part}")
        lines.append("")

    if untagged:
        lines.append(f"## 未分类 ({len(untagged)} 条)")
        for item in untagged:
            lines.append(f"- [{item['title']}]({item['url']}) — {item['source_name']}")
        lines.append("")

    lines.append("---")
    lines.append(f"_共收录 {len(items)} 条新内容，由 GitHub Actions 自动生成，无 LLM 参与。_")
    return "\n".join(lines)


def main() -> int:
    topics_cfg = load_yaml(TOPICS_FILE)
    sources_cfg = load_yaml(SOURCES_FILE)
    manual_cfg = load_yaml(MANUAL_FILE)

    topics = topics_cfg.get("topics", {})
    topic_names = {tid: t.get("name", tid) for tid, t in topics.items()}
    topic_keywords = {tid: t.get("keywords", []) for tid, t in topics.items()}

    seen = load_json(SEEN_FILE, {"urls": {}})
    stats = load_json(STATS_FILE, {"sources": {}, "last_updated": None})

    new_items: list[dict] = []
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    for source in sources_cfg.get("sources", []):
        source_id = source["id"]
        try:
            if source["type"] == "rss":
                raw_items = fetch_rss(source)
            elif source["type"] == "github_search":
                raw_items = fetch_github_search(source)
            else:
                print(f"Unknown source type: {source['type']}", file=sys.stderr)
                continue

            source_new = 0
            for raw in raw_items:
                url = raw.get("url", "")
                if not url:
                    continue
                h = url_hash(url)
                if h in seen.get("urls", {}):
                    continue

                title = raw.get("title", "Untitled")
                summary = raw.get("summary", "")
                matched_topics = classify_topics(
                    title, summary,
                    source.get("topics", []),
                    source.get("tier", "B"),
                    topic_keywords,
                )

                # B-tier with no keyword match → skip
                if source.get("tier", "B") == "B" and not matched_topics:
                    continue

                item = {
                    "id": h,
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "source_id": source_id,
                    "source_name": source.get("name", source_id),
                    "topics": matched_topics,
                    "fetched_at": now.isoformat(),
                    "published": raw.get("published", ""),
                }
                seen.setdefault("urls", {})[h] = {
                    "url": url,
                    "first_seen": now.isoformat(),
                    "source_id": source_id,
                }
                new_items.append(item)
                source_new += 1

            record_stat(stats, source_id, source_new)
            print(f"[OK] {source_id}: {source_new} new items")

        except Exception as e:
            record_stat(stats, source_id, 0, str(e))
            print(f"[ERR] {source_id}: {e}", file=sys.stderr)

    manual_items = process_manual_urls(manual_cfg, seen, topic_keywords, topic_names)
    new_items.extend(manual_items)
    if manual_items:
        record_stat(stats, "manual", len(manual_items))
        print(f"[OK] manual: {len(manual_items)} new items")

    if not new_items:
        print("No new items today — skipping report commit.")
        save_json(SEEN_FILE, seen)
        save_json(STATS_FILE, stats)
        return 0

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{date_str}.json"
    save_json(raw_path, new_items)

    report = generate_daily_report(date_str, new_items, topic_names)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{date_str}.md"
    report_path.write_text(report, encoding="utf-8")

    save_json(SEEN_FILE, seen)
    save_json(STATS_FILE, stats)

    print(f"Wrote {len(new_items)} items → {raw_path.name}, {report_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
