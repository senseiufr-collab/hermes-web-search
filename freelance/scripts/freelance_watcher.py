#!/usr/bin/env python3
"""Minimal freelance order watcher: checks RSS/search feeds for relevant gigs."""
from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
OUT = BASE_DIR / "output"
OUT.mkdir(exist_ok=True)
FEEDS = [
    "https://habr.com/ru/rss/fl_django/",
    "https://habr.com/ru/rss/fl_python/",
    "https://habr.com/ru/rss/fl_webdev/",
    "https://www.fl.ru/rss/all.xml",
    "https://kwork.ru/rss",
]
QUERIES = [
    "парсер python",
    "telegram bot",
    "crypto signals",
    "автоматизация python",
    "bot telegram",
    "parsing python",
    "selenium python",
    "api python",
    "scraping python",
]


def _clean(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_feed(url: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            title = _clean(next((t.text or "" for t in item.iter("title")), ""))
            link = next((l.text or "" for l in item.iter("link")), "")
            desc = _clean(next((d.text or "" for d in item.iter("description")), ""))
            pub = next((p.text or "" for p in item.iter("pubDate")), "")
            if title:
                out.append({"title": title, "href": link, "body": desc[:800], "ts": pub})
    except Exception:
        pass
    return out


def match_query(item: Dict[str, str], queries: List[str]) -> List[str]:
    text = (item.get("title", "") + " " + item.get("body", "")).lower()
    return [q for q in queries if q.lower() in text]


def save_results(items: List[Dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({"ts": datetime.now(timezone.utc).isoformat(), "items": items}, f, ensure_ascii=False, indent=2)


def main() -> int:
    seen: set = set()
    matched: List[Dict[str, Any]] = []
    for url in FEEDS:
        for item in fetch_feed(url):
            key = item.get("href") or item.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            hits = match_query(item, QUERIES)
            if hits:
                matched.append({**item, "matched_queries": hits})
    matched.sort(key=lambda x: x.get("title", ""))
    save_results(matched, OUT / "freelance_gigs.json")
    print(f"Matched gigs: {len(matched)}")
    for it in matched[:20]:
        print('-', it.get('title'), '|', it.get('href'))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
