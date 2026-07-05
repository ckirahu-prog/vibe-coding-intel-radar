#!/usr/bin/env python3
"""Lightweight unit tests for collector helpers (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import collect  # noqa: E402
import digest_weekly  # noqa: E402
from enrich_last30days import extract_urls, guess_platform, slugify  # noqa: E402


def test_source_enabled_defaults_true():
    assert collect.source_enabled({"id": "x"}) is True
    assert collect.source_enabled({"id": "x", "enabled": False}) is False
    assert collect.source_enabled({"id": "x", "enabled": True}) is True


def test_slugify():
    assert slugify("电鸭 找到工作") == "电鸭-找到工作"
    assert slugify("  Hello World!!  ") == "hello-world"


def test_extract_urls():
    text = "See https://www.v2ex.com/t/1 and https://github.com/foo/bar."
    urls = extract_urls(text)
    assert urls[0].startswith("https://www.v2ex.com")
    assert any("github.com" in u for u in urls)


def test_guess_platform():
    assert guess_platform("https://www.v2ex.com/t/1") == "v2ex"
    assert guess_platform("https://old.reddit.com/r/foo") == "reddit"


def test_cluster_items_groups_cross_source_near_duplicates():
    items = [
        {"title": "花 2 月写了一款软件，结果 claude code router 上线了", "url": "https://v2ex.com/t/1", "source_id": "v2ex-latest", "topics": ["vibe-coding-commercial"], "summary": ""},
        {"title": "花两月写软件结果 Claude Code Router 上线了同款功能", "url": "https://example.com/mirror", "source_id": "36kr", "topics": ["vibe-coding-commercial"], "summary": ""},
        {"title": "Show HN: HowMuch – Wordle but you guess prices", "url": "https://news.ycombinator.com/item?id=1", "source_id": "hn-show", "topics": ["ai-game-dev"], "summary": ""},
    ]
    clusters = digest_weekly.cluster_items(items, threshold=0.45)
    sizes = sorted(len(c["items"]) for c in clusters)
    assert sizes == [1, 2]
    multi = [c for c in clusters if c["multi_source"]]
    assert len(multi) == 1
    assert len(multi[0]["urls"]) == 2


def test_cluster_items_keeps_same_source_items_separate():
    # Same-source repeats shouldn't be force-merged here (URL dedup already
    # happens upstream in collect.py); clustering only spans different sources.
    items = [
        {"title": "AAAA duplicate title here", "url": "https://a.com/1", "source_id": "hn-show", "topics": [], "summary": ""},
        {"title": "AAAA duplicate title here", "url": "https://a.com/2", "source_id": "hn-show", "topics": [], "summary": ""},
    ]
    clusters = digest_weekly.cluster_items(items, threshold=0.45)
    assert len(clusters) == 2


def test_select_top_respects_top_n_and_topic_spread():
    topic_keywords = {"a": [], "b": []}
    clusters = []
    for i in range(5):
        clusters.append({
            "title": f"item-a-{i}", "topics": ["a"], "urls": [f"https://x.com/{i}"],
            "sources": ["s1"], "multi_source": False,
            "items": [{"title": f"item-a-{i}", "summary": "", "topics": ["a"], "source_id": "s1"}],
        })
    for i in range(5):
        clusters.append({
            "title": f"item-b-{i}", "topics": ["b"], "urls": [f"https://y.com/{i}"],
            "sources": ["s2"], "multi_source": False,
            "items": [{"title": f"item-b-{i}", "summary": "", "topics": ["b"], "source_id": "s2"}],
        })
    selected = digest_weekly.select_top(clusters, topic_keywords, top_n=6)
    assert len(selected) == 6


def run() -> int:
    tests = [
        test_source_enabled_defaults_true,
        test_slugify,
        test_extract_urls,
        test_guess_platform,
        test_cluster_items_groups_cross_source_near_duplicates,
        test_cluster_items_keeps_same_source_items_separate,
        test_select_top_respects_top_n_and_topic_spread,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
