#!/usr/bin/env python3
"""Lightweight unit tests for collector helpers (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import collect  # noqa: E402
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


def run() -> int:
    tests = [
        test_source_enabled_defaults_true,
        test_slugify,
        test_extract_urls,
        test_guess_platform,
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
