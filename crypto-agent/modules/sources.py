#!/usr/bin/env python3
"""Sources collector for crypto-agent."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any
from urllib.parse import quote
import requests

from modules.browser import find_perplexity_tab, navigate, evaluate

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


def fetch_perplexity_answer(query: str) -> Dict[str, Any]:
    tab = find_perplexity_tab()
    if not tab:
        return {"query": query, "error": "no_perplexity_tab"}
    pid = tab["id"]
    navigate(f"https://www.perplexity.ai/search?q={requests.utils.quote(query)}", pid)
    try:
        text = evaluate("document.body.innerText", pid) or ""
    except Exception:
        text = ""
    sources = []
    try:
        html = evaluate("document.body.innerHTML", pid) or ""
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select('a[href]'):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if href.startswith("http") and title and len(title) > 10:
                sources.append({"title": title, "href": href})
    except Exception:
        pass
    return {
        "query": query,
        "text": text,
        "sources": sources,
        "ts": datetime.now(timezone.utc).isoformat(),
        "tab": pid,
    }


def fetch_coingecko_funding() -> List[Dict[str, Any]]:
    url = "https://www.coingecko.com/en/funding-rounds"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return [{"source": "coingecko", "error": str(e)}]
    soup = BeautifulSoup(r.text, "html.parser")
    rows = []
    for card in soup.select(".fund-round-card"):
        try:
            title = card.select_one(".fund-round-name")
            amount = card.select_one(".fund-round-amount")
            stage = card.select_one(".fund-round-stage")
            rows.append({
                "source": "coingecko",
                "title": title.get_text(strip=True) if title else "",
                "amount": amount.get_text(strip=True) if amount else "",
                "stage": stage.get_text(strip=True) if stage else "",
            })
        except Exception:
            continue
    return rows


def default_fallback() -> Dict[str, Any]:
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "note": "fallback source list only; browser/perplexity not available",
        "items": [
            {"name": "perplexity", "url": "https://www.perplexity.ai/", "type": "browser"},
            {"name": "coingecko_funding", "url": "https://www.coingecko.com/en/funding-rounds", "type": "page"},
            {"name": "cryptorank_funding", "url": "https://cryptorank.io/fundings", "type": "page"},
            {"name": "theblock", "url": "https://www.theblock.co/crypto/", "type": "page"},
            {"name": "cointelegraph_altcoins", "url": "https://cointelegraph.com/categories/altcoins", "type": "page"},
            {"name": "news_bitcoin_com_altcoins", "url": "https://news.bitcoin.com/category/altcoins/", "type": "page"},
        ],
    }


def collect_sources(queries: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"ts": datetime.now(timezone.utc).isoformat()}
    # Browser-backed Perplexity
    try:
        out["perplexity"] = [fetch_perplexity_answer(q) for q in queries[:3]]
    except Exception as e:
        out["perplexity_error"] = str(e)
    # Page sources
    try:
        out["coingecko_funding"] = fetch_coingecko_funding()
    except Exception as e:
        out["coingecko_error"] = str(e)
    out["fallback"] = default_fallback()
    return out
