#!/usr/bin/env python3
"""Daily intel collector: RSS/API fetch, dedup, tag, write raw JSON + daily report."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INDEX_DIR = DATA_DIR / "daily-index"

SEEN_FILE = DATA_DIR / "seen.json"
STATS_FILE = DATA_DIR / "stats.json"
TOPICS_FILE = CONFIG_DIR / "topics.yaml"
SOURCES_FILE = CONFIG_DIR / "sources.yaml"
MANUAL_FILE = CONFIG_DIR / "manual-urls.yaml"

SUMMARY_MAX_LEN = 400
HIGH_VALUE_KEYWORDS = {
    "ai-game-dev": [
        "tutorial", "how to", "workflow", "tool", "release", "launch", "free",
        "open source", "godot", "unity", "cursor", "mcp", "rosebud", "meshy",
        "game jam", "steam", "itch", "playtest", "demo", "guide",
    ],
    "vibe-coding-commercial": [
        "mrr", "revenue", "arr", "customers", "subscribers", "pricing", "launched",
        "shipped", "stripe", "bootstrapped", "profit", "paying", "show hn",
        "product hunt", "built with cursor", "vibe coding", "solo founder",
    ],
    "sideline-pain-opportunity": [
        "副业", "兼职", "自由职业", "接单", "外包", "个体户", "小微", "对账",
        "发票", "合同", "报价", "痛点", "吐槽", "有没有", "工具", "月入", "变现",
        "side hustle", "freelance", "micro saas", "独立开发",
    ],
}
USER_AGENT = "IntelRadar/1.0 (github-actions; info-collector)"
GITHUB_API = "https://api.github.com"
CLI_TIMEOUT_SEC = 45


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


def score_item(item: dict, topic_keywords: dict[str, list[str]]) -> int:
    """Heuristic relevance score for daily highlights."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    score = 0
    for topic_id in item.get("topics") or []:
        for kw in topic_keywords.get(topic_id, []):
            if kw.lower() in text:
                score += 2
        for kw in HIGH_VALUE_KEYWORDS.get(topic_id, []):
            if kw.lower() in text:
                score += 3
    if item.get("source_id") == "manual":
        score += 5
    tier_a_sources = {"reddit-aigamedev", "github-game-ai", "github-vibe-coding"}
    if item.get("source_id") in tier_a_sources:
        score += 2
    if len(item.get("summary") or "") > 120:
        score += 1
    return score


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

    # Cross-tag: disabled — avoid Show HN / generic AI news flooding ai-game-dev
    return sorted(matched)


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")


def fetch_with_retry(url: str, headers: dict, retries: int = 3) -> requests.Response:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt + 1)
                continue
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt + 1)
    raise last_err or RuntimeError(f"Failed to fetch {url}")


def fetch_rss(source: dict) -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    url = source["url"]
    # old.reddit.com is more reliable from CI than www.reddit.com
    if "reddit.com" in url and "old.reddit.com" not in url:
        url = url.replace("www.reddit.com", "old.reddit.com")
    resp = fetch_with_retry(url, headers)
    feed = feedparser.parse(resp.content)

    items = []
    for entry in feed.entries[:50]:
        link = entry.get("link") or entry.get("id") or ""
        title = strip_html(entry.get("title", "Untitled"))
        summary = strip_html(entry.get("summary") or entry.get("description") or "")
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

    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    query = source["query"].replace(">7d", f">{since}")

    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 20,
    }

    last_err: Exception | None = None
    data = {}
    for attempt in range(3):
        try:
            resp = requests.get(
                f"{GITHUB_API}/search/repositories",
                headers=headers,
                params=params,
                timeout=30,
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt + 1)
                continue
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt + 1)
    else:
        raise last_err or RuntimeError("GitHub search failed")

    items = []
    for repo in data.get("items", []):
        items.append({
            "title": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "summary": truncate(repo.get("description") or ""),
            "published": repo.get("updated_at") or repo.get("pushed_at") or "",
        })
    return items


def source_enabled(source: dict) -> bool:
    """Sources with enabled: false are skipped (Agent-Reach optional backends)."""
    return source.get("enabled", True)


def run_cli(cmd: list[str], timeout: int = CLI_TIMEOUT_SEC) -> tuple[str, str, int]:
    """Run external CLI; return stdout, stderr, returncode."""
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout or "", proc.stderr or "", proc.returncode


def cli_available(name: str) -> bool:
    return shutil.which(name) is not None


def fetch_agent_reach_v2ex(source: dict) -> list[dict]:
    """V2EX JSON API (Agent-Reach compatible; no login)."""
    api_kind = source.get("api", "hot")
    url = f"https://www.v2ex.com/api/topics/{api_kind}.json"
    resp = fetch_with_retry(url, {"User-Agent": USER_AGENT})
    payload = resp.json()
    items = []
    for topic in payload[:40]:
        if not isinstance(topic, dict):
            continue
        title = topic.get("title") or "Untitled"
        topic_id = topic.get("id")
        if not topic_id:
            continue
        link = f"https://www.v2ex.com/t/{topic_id}"
        content = strip_html(topic.get("content") or "")
        replies = topic.get("replies", 0)
        summary = truncate(content) if content else f"回复 {replies}"
        items.append({
            "title": truncate(title, 300),
            "url": link,
            "summary": summary,
            "published": topic.get("last_modified") or topic.get("created") or "",
        })
    return items


def fetch_agent_reach_bilibili_search(source: dict) -> list[dict]:
    """B站搜索 via bili-cli (Agent-Reach upstream). Fails soft if CLI missing."""
    query = source.get("query", "").strip()
    if not query:
        return []
    if not cli_available("bili"):
        raise RuntimeError("bili CLI not on PATH (install via Agent-Reach / bili-cli)")

    stdout, stderr, code = run_cli(["bili", "search", query])
    if code != 0:
        raise RuntimeError(stderr.strip() or stdout.strip() or f"bili search exited {code}")

    items: list[dict] = []
    # Try JSON lines first
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            bvid = row.get("bvid") or row.get("BV")
            title = row.get("title") or row.get("name") or "Bilibili video"
            url = row.get("url") or row.get("link")
            if not url and bvid:
                url = f"https://www.bilibili.com/video/{bvid}"
            if url:
                items.append({
                    "title": truncate(str(title), 300),
                    "url": str(url),
                    "summary": truncate(str(row.get("description") or row.get("desc") or "")),
                    "published": str(row.get("pubdate") or row.get("published") or ""),
                })
            continue
        # Fallback: URL in line
        url_match = re.search(r"https?://(?:www\.)?bilibili\.com/video/[A-Za-z0-9]+", line)
        if url_match:
            title = line[: url_match.start()].strip(" -|\t") or "Bilibili video"
            items.append({
                "title": truncate(title, 300),
                "url": url_match.group(0),
                "summary": "",
                "published": "",
            })

    if not items:
        raise RuntimeError("bili search returned no parseable results")
    return items[:20]


def fetch_agent_reach_youtube_search(source: dict) -> list[dict]:
    """YouTube search via yt-dlp (Agent-Reach upstream). Fails soft if CLI missing."""
    query = source.get("query", "").strip()
    if not query:
        return []
    if not cli_available("yt-dlp"):
        raise RuntimeError("yt-dlp not on PATH (install via Agent-Reach / yt-dlp)")

    max_results = int(source.get("max_results", 8))
    search_url = f"ytsearch{max_results}:{query}"
    stdout, stderr, code = run_cli([
        "yt-dlp",
        search_url,
        "--flat-playlist",
        "--print",
        "%(title)s",
        "--print",
        "%(webpage_url)s",
        "--print",
        "%(upload_date)s",
    ])
    if code != 0:
        raise RuntimeError(stderr.strip() or stdout.strip() or f"yt-dlp exited {code}")

    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    items: list[dict] = []
    i = 0
    while i + 2 < len(lines):
        title, url, uploaded = lines[i], lines[i + 1], lines[i + 2]
        if url.startswith("http"):
            pub = ""
            if uploaded and uploaded.isdigit() and len(uploaded) == 8:
                pub = f"{uploaded[:4]}-{uploaded[4:6]}-{uploaded[6:8]}"
            items.append({
                "title": truncate(title, 300),
                "url": url,
                "summary": f"YouTube search: {query}",
                "published": pub,
            })
        i += 3

    if not items:
        raise RuntimeError("yt-dlp search returned no parseable results")
    return items


def fetch_source(source: dict) -> list[dict]:
    """Dispatch fetch by source type."""
    stype = source["type"]
    if stype == "rss":
        return fetch_rss(source)
    if stype == "github_search":
        return fetch_github_search(source)
    if stype == "agent_reach_v2ex":
        return fetch_agent_reach_v2ex(source)
    if stype == "agent_reach_bilibili_search":
        return fetch_agent_reach_bilibili_search(source)
    if stype == "agent_reach_youtube_search":
        return fetch_agent_reach_youtube_search(source)
    raise ValueError(f"Unknown source type: {stype}")


def ingest_raw_items(
    raw_items: list[dict],
    source: dict,
    source_id: str,
    seen: dict,
    topic_keywords: dict[str, list[str]],
    now: datetime,
) -> tuple[list[dict], int]:
    """Dedup, classify, and build collector items from raw fetch rows."""
    new_items: list[dict] = []
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
    return new_items, source_new


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


def format_item_line(item: dict, *, verbose: bool = False) -> str:
    summary = item.get("summary") or ""
    if verbose and summary:
        return (
            f"- **[{item['title']}]({item['url']})**\n"
            f"  - 来源：{item['source_name']}\n"
            f"  - 摘要：{summary}"
        )
    summary_part = f" — {summary}" if summary else ""
    return f"- [{item['title']}]({item['url']}) · {item['source_name']}{summary_part}"


def generate_daily_index(
    date_str: str,
    items: list[dict],
    topic_names: dict[str, str],
    topic_keywords: dict[str, list[str]],
) -> str:
    """Raw link index for Daily Cursor Automation — not the final user-facing report."""
    lines = [
        f"# 日报素材索引 {date_str}",
        "",
        "> 供 Cursor Daily Automation 读取；最终案例拆解日报见 `reports/daily/YYYY-MM-DD.md`",
        "",
        f"共 {len(items)} 条新内容",
        "",
    ]

    scored = sorted(
        items,
        key=lambda it: score_item(it, topic_keywords),
        reverse=True,
    )
    highlights = [it for it in scored if score_item(it, topic_keywords) >= 4][:8]
    if highlights:
        lines.append("## 今日精选（优先阅读）")
        lines.append("")
        for item in highlights:
            topics = "、".join(topic_names.get(t, t) for t in item.get("topics") or [])
            tag = f" · {topics}" if topics else ""
            lines.append(format_item_line(item, verbose=True) + tag)
            lines.append("")

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
        lines.append(f"## {name}（{len(topic_items)} 条）")
        if not topic_items:
            lines.append("")
            lines.append("_无新增_")
        else:
            by_source: dict[str, list[dict]] = {}
            for item in topic_items:
                by_source.setdefault(item["source_name"], []).append(item)
            for source_name, source_items in sorted(by_source.items()):
                lines.append("")
                lines.append(f"### {source_name}（{len(source_items)}）")
                for item in source_items:
                    lines.append(format_item_line(item))
        lines.append("")

    if untagged:
        lines.append(f"## 未分类（{len(untagged)} 条）")
        for item in untagged:
            lines.append(format_item_line(item))
        lines.append("")

    lines.append("---")
    lines.append("_采集器自动生成 · 无 LLM · 仅供日报 Agent 分析输入_")
    return "\n".join(lines)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
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
        if not source_enabled(source):
            print(f"[SKIP] {source_id}: disabled")
            continue
        # Stagger Reddit requests to reduce 429 rate limits
        if "reddit" in source_id:
            time.sleep(2)
        try:
            raw_items = fetch_source(source)
            if dry_run:
                print(f"[DRY] {source_id}: would fetch {len(raw_items)} items")
                continue

            batch, source_new = ingest_raw_items(
                raw_items, source, source_id, seen, topic_keywords, now,
            )
            new_items.extend(batch)
            record_stat(stats, source_id, source_new)
            print(f"[OK] {source_id}: {source_new} new items")

        except Exception as e:
            if not dry_run:
                record_stat(stats, source_id, 0, str(e))
            print(f"[ERR] {source_id}: {e}", file=sys.stderr)

    if dry_run:
        enabled = [s["id"] for s in sources_cfg.get("sources", []) if source_enabled(s)]
        print(f"\n=== Dry run: {len(enabled)} enabled sources ===")
        return 0

    manual_items = process_manual_urls(manual_cfg, seen, topic_keywords, topic_names)
    new_items.extend(manual_items)
    if manual_items:
        record_stat(stats, "manual", len(manual_items))
        print(f"[OK] manual: {len(manual_items)} new items")

    if not new_items:
        print("No new items today — skipping report commit.")
        save_json(SEEN_FILE, seen)
        save_json(STATS_FILE, stats)
        print_summary(stats)
        return 0

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{date_str}.json"
    save_json(raw_path, new_items)

    report = generate_daily_index(date_str, new_items, topic_names, topic_keywords)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index_path = INDEX_DIR / f"{date_str}.md"
    index_path.write_text(report, encoding="utf-8")

    save_json(SEEN_FILE, seen)
    save_json(STATS_FILE, stats)

    print(f"Wrote {len(new_items)} items → {raw_path.name}, {index_path.name}")
    print_summary(stats)
    return 0


def print_summary(stats: dict) -> None:
    sources = stats.get("sources", {})
    ok = [sid for sid, s in sources.items() if s.get("errors", 0) == 0 and s.get("hits", 0) > 0]
    empty = [sid for sid, s in sources.items() if s.get("errors", 0) == 0 and s.get("hits", 0) == 0]
    failed = [sid for sid, s in sources.items() if s.get("errors", 0) > 0]
    print(f"\n=== Summary: {len(ok)} sources OK, {len(empty)} empty, {len(failed)} failed ===")
    if failed:
        for sid in failed:
            err = sources[sid].get("last_error", "unknown")
            print(f"  [FAILED] {sid}: {err}")
    if empty:
        print(f"  [EMPTY]  {', '.join(empty)}")


if __name__ == "__main__":
    sys.exit(main())
