#!/usr/bin/env python3
"""Crypto agent: collect sources and generate long/short signals."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from modules.sources import collect_sources
from modules.scorer import rank_signals


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SIGNALS_FILE = DATA_DIR / "signals.jsonl"
QUERIES = [
    "crypto funding round altcoin 2026",
    "new altcoin opportunities tokenization infrastructure",
    "crypto ETF institutional flow 2026",
]


def append_signal(record: Dict[str, Any]) -> None:
    try:
        with SIGNALS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def notify(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_ALLOWED_USERS") or os.environ.get("TELEGRAM_HOME_CHANNEL")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass


def scan() -> int:
    collected = collect_sources(QUERIES)
    items: List[Dict[str, Any]] = []
    # Flatten browser answers
    for entry in collected.get("perplexity", []):
        text = entry.get("text", "")
        if text:
            items.append({"title": entry.get("query", ""), "body": text, "source": "perplexity"})
        for src in entry.get("sources", [])[:5]:
            items.append({"title": src.get("title", ""), "body": "", "href": src.get("href", ""), "source": "perplexity_source"})
    # Flatten page sources
    for key in ("coingecko_funding", ):
        val = collected.get(key, [])
        if isinstance(val, list):
            items.extend([{**x, "source": key} for x in val[:20]])
    if not items:
        items.append({"title": "No signals collected", "body": "", "source": "agent"})

    ranked_long = rank_signals(items, horizon="long")[:10]
    ranked_short = rank_signals(items, horizon="short")[:10]

    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "long": ranked_long,
        "short": ranked_short,
        "sources": collected,
    }
    append_signal(report)
    summary = (
        "Crypto signals:\n"
        f"- Long-term candidates: {len(ranked_long)}\n"
        f"- Short-term candidates: {len(ranked_short)}\n"
        f"Top long: {ranked_long[0].get('title') if ranked_long else '—'} | score={ranked_long[0].get('score') if ranked_long else '—'}\n"
        f"Top short: {ranked_short[0].get('title') if ranked_short else '—'} | score={ranked_short[0].get('score') if ranked_short else '—'}"
    )
    print(summary)
    notify(summary)
    return 0


def watch(interval: int = 600) -> int:
    print(f"Watching for crypto signals every {interval}s...")
    try:
        while True:
            try:
                scan()
            except Exception as e:
                print("scan_error:", e, file=sys.stderr)
            time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "scan"
    if cmd == "scan":
        return scan()
    if cmd == "watch":
        return watch(int(argv[1]) if len(argv) > 1 else 600)
    print("Commands: scan | watch [interval_seconds]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
