#!/usr/bin/env python3
"""Weekly digest builder: dedup-cluster + score + top-N selection.

Runs Friday (before Saturday Weekly Automation) with zero LLM cost. It reads
the past N days of `data/raw/*.json`, groups near-duplicate titles that were
picked up by different sources (cross-source clustering — the free stand-in
for A1 double-source verification), scores every item with the same
heuristic `collect.py` uses for daily highlights, and writes a machine-picked
top-80 (with cluster/multi-source flags) to `data/weekly-digest/YYYY-Www.json`.

The Weekly Automation prompt (templates/weekly-prompt.md) reads this file
first so the 80-item cap is enforced mechanically instead of left to the LLM,
and clusters with 2+ distinct URLs are visible without any extra web search.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect  # noqa: E402  (reuse load_yaml / score_item / paths)

ROOT = collect.ROOT
RAW_DIR = collect.RAW_DIR
DIGEST_DIR = collect.DATA_DIR / "weekly-digest"

DEFAULT_DAYS = 7
DEFAULT_TOP = 80
PER_TOPIC_CAP = 30  # soft cap so one noisy topic can't crowd out the other two
STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is",
    "how", "what", "why", "with", "your", "you", "my", "i", "this", "that",
}


def _cjk_and_words(text: str) -> set[str]:
    """Fingerprint tokens for near-duplicate title matching (CJK-aware)."""
    text = (text or "").lower()
    words = set(re.findall(r"[a-z0-9]+", text))
    words -= STOPWORDS
    cjk_chars = set(re.findall(r"[\u4e00-\u9fff]", text))
    return words | cjk_chars


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def load_recent_raw_items(days: int) -> tuple[list[dict], list[str]]:
    if not RAW_DIR.exists():
        return [], []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    items: list[dict] = []
    used_files: list[str] = []
    for path in sorted(RAW_DIR.glob("*.json")):
        try:
            file_date = datetime.strptime(path.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if file_date < cutoff:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            items.extend(data)
            used_files.append(path.name)
    return items, used_files


def cluster_items(items: list[dict], threshold: float = 0.45) -> list[dict]:
    """Group items with near-duplicate titles (likely the same story re-surfaced
    on a different source) into clusters. O(n^2) but n is a few hundred/week."""
    fingerprints = [_cjk_and_words(it.get("title", "")) for it in items]
    n = len(items)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        if not fingerprints[i]:
            continue
        for j in range(i + 1, n):
            if items[i].get("source_id") == items[j].get("source_id"):
                continue  # same-source duplicates are already URL-deduped upstream
            if _jaccard(fingerprints[i], fingerprints[j]) >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for idx in range(n):
        groups.setdefault(find(idx), []).append(idx)

    clusters = []
    for group_indices in groups.values():
        group_items = [items[i] for i in group_indices]
        urls = sorted({it.get("url", "") for it in group_items if it.get("url")})
        sources = sorted({it.get("source_id", "") for it in group_items})
        topics = sorted({t for it in group_items for t in (it.get("topics") or [])})
        clusters.append({
            "title": max(group_items, key=lambda it: len(it.get("title") or "")).get("title", ""),
            "topics": topics,
            "urls": urls,
            "sources": sources,
            "multi_source": len(sources) >= 2,
            "items": group_items,
        })
    return clusters


def score_cluster(cluster: dict, topic_keywords: dict[str, list[str]]) -> int:
    best = max(
        (collect.score_item(it, topic_keywords) for it in cluster["items"]),
        default=0,
    )
    return best + (3 if cluster["multi_source"] else 0)


def select_top(clusters: list[dict], topic_keywords: dict[str, list[str]], top_n: int) -> list[dict]:
    for c in clusters:
        c["score"] = score_cluster(c, topic_keywords)

    by_topic: dict[str, list[dict]] = {}
    untagged: list[dict] = []
    for c in clusters:
        if c["topics"]:
            for t in c["topics"]:
                by_topic.setdefault(t, []).append(c)
        else:
            untagged.append(c)

    selected_ids: set[int] = set()
    selected: list[dict] = []

    for topic, topic_clusters in by_topic.items():
        ranked = sorted(topic_clusters, key=lambda c: c["score"], reverse=True)
        for c in ranked[:PER_TOPIC_CAP]:
            cid = id(c)
            if cid not in selected_ids and len(selected) < top_n:
                selected_ids.add(cid)
                selected.append(c)

    remaining = sorted(
        (c for c in clusters if id(c) not in selected_ids),
        key=lambda c: c["score"],
        reverse=True,
    )
    for c in remaining:
        if len(selected) >= top_n:
            break
        selected_ids.add(id(c))
        selected.append(c)

    selected.sort(key=lambda c: c["score"], reverse=True)
    return selected


def iso_week_label(dt: datetime) -> str:
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def build_digest(days: int, top_n: int, week_label: str | None) -> dict:
    topics_cfg = collect.load_yaml(collect.TOPICS_FILE)
    topics = topics_cfg.get("topics", {})
    topic_keywords = {tid: t.get("keywords", []) for tid, t in topics.items()}
    topic_names = {tid: t.get("name", tid) for tid, t in topics.items()}

    now = datetime.now(timezone.utc)
    items, used_files = load_recent_raw_items(days)
    clusters = cluster_items(items)
    selected = select_top(clusters, topic_keywords, top_n)

    by_topic_count: dict[str, int] = {}
    for c in selected:
        for t in c["topics"] or ["未分类"]:
            by_topic_count[t] = by_topic_count.get(t, 0) + 1

    return {
        "generated_at": now.isoformat(),
        "week": week_label or iso_week_label(now),
        "period_days": days,
        "source_files": used_files,
        "totals": {
            "raw_items": len(items),
            "clusters": len(clusters),
            "multi_source_clusters": sum(1 for c in clusters if c["multi_source"]),
            "selected": len(selected),
        },
        "selected_by_topic": {
            topic_names.get(tid, tid): n for tid, n in by_topic_count.items()
        },
        "clusters": [
            {
                "title": c["title"],
                "topics": [topic_names.get(t, t) for t in c["topics"]],
                "topic_ids": c["topics"],
                "score": c["score"],
                "multi_source": c["multi_source"],
                "urls": c["urls"],
                "sources": c["sources"],
                "items": [
                    {
                        "title": it.get("title"),
                        "url": it.get("url"),
                        "summary": it.get("summary"),
                        "source_id": it.get("source_id"),
                        "source_name": it.get("source_name"),
                        "published": it.get("published"),
                    }
                    for it in c["items"]
                ],
            }
            for c in selected
        ],
    }


def main() -> int:
    days = DEFAULT_DAYS
    top_n = DEFAULT_TOP
    week_label = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
            i += 2
        elif args[i] == "--week" and i + 1 < len(args):
            week_label = args[i + 1]
            i += 2
        else:
            i += 1

    digest = build_digest(days, top_n, week_label)
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DIGEST_DIR / f"{digest['week']}.json"
    out_path.write_text(
        json.dumps(digest, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    totals = digest["totals"]
    print(
        f"Wrote {out_path.relative_to(ROOT)}: "
        f"{totals['raw_items']} raw → {totals['clusters']} clusters "
        f"({totals['multi_source_clusters']} multi-source) → "
        f"{totals['selected']} selected"
    )
    print(f"By topic: {digest['selected_by_topic']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
