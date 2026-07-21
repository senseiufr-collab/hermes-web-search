#!/usr/bin/env python3
"""
Centralized web search CLI for Hermes.
- direct search via requests + BeautifulSoup
- optional Google Custom Search JSON API backend
- dork presets
- caching
- export: text/json/csv
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Run install script or: pip3 install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    from googleapiclient.discovery import build
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

CACHE_DIR = Path.home() / ".cache" / "web-search"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_MAX_RESULTS = 10
DEFAULT_TTL_MINUTES = 15

DORK_PRESETS = {
    "site": "site:{domain}",
    "filetype": "filetype:{ext}",
    "intitle": "intitle:{text}",
    "inurl": "inurl:{text}",
    "exact": '"{text}"',
    "related": "related:{domain}",
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"


def cache_key(query: str, backend: str) -> Path:
    raw = f"{backend}:{query}".encode("utf-8")
    return CACHE_DIR / f"{hashlib.sha256(raw).hexdigest()}.json"


def load_cache(key: Path, ttl_minutes: int):
    if not key.exists():
        return None
    try:
        data = json.loads(key.read_text())
        ts = datetime.fromisoformat(data["ts"])
        if datetime.utcnow() - ts > timedelta(minutes=ttl_minutes):
            return None
        return data["results"]
    except Exception:
        return None


def save_cache(key: Path, results) -> None:
    try:
        key.write_text(
            json.dumps({"ts": datetime.utcnow().isoformat(), "results": results}, ensure_ascii=False)
        )
    except Exception:
        pass


import datetime
from datetime import datetime, timedelta


def search_bing(query: str, max_results: int = 10, market: str = "en-US", lang: str = "en"):
    url = "https://www.bing.com/search"
    params = {"q": query, "count": max_results, "setmkt": market, "setlang": lang}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for li in soup.select("li.b_algo"):
        title_el = li.select_one("h2 a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        snippet_el = li.select_one(".b_caption p, .b_paractl")
        body = snippet_el.get_text(strip=True) if snippet_el else ""
        if title or href:
            results.append({"title": title, "href": href, "body": body})
        if len(results) >= max_results:
            break
    return results


def search_duckduckgo(query: str, max_results: int = 10):
    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": USER_AGENT}
    data = {"q": query}
    resp = requests.post(url, data=data, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for a in soup.select(".result__a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        snippet_el = a.find_parent(".result") and a.find_parent(".result").select_one(".result__snippet")
        body = snippet_el.get_text(strip=True) if snippet_el else ""
        results.append({"title": title, "href": href, "body": body})
        if len(results) >= max_results:
            break
    return results


def search_google_cse(query: str, max_results: int = 10, api_key: str = "", cse_id: str = ""):
    if not HAS_GOOGLE:
        raise RuntimeError("google-api-python-client is not installed")
    if not api_key or not cse_id:
        raise RuntimeError("Google CSE requires --google-api-key and --google-cse-id")
    service = build("customsearch", "v1", developerKey=api_key, cache_discovery=False)
    res = service.cse().list(q=query, cx=cse_id, num=max_results).execute()
    results = []
    for item in res.get("items", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "href": item.get("link", ""),
            "body": item.get("snippet", ""),
        })
    return results


def text_search(query: str, max_results: int, backend: str, ttl_minutes: int, google_api_key: str = "", google_cse_id: str = ""):
    key = cache_key(query, backend)
    cached = load_cache(key, ttl_minutes)
    if cached is not None:
        return cached

    results = []
    if backend == "bing":
        results = search_bing(query, max_results=max_results)
    elif backend == "duckduckgo":
        results = search_duckduckgo(query, max_results=max_results)
    elif backend == "google_cse":
        results = search_google_cse(query, max_results=max_results, api_key=google_api_key, cse_id=google_cse_id)
    else:
        # auto fallback
        errors = []
        try:
            results = search_bing(query, max_results=max_results)
        except Exception as e:
            errors.append(("bing", e))
        if not results:
            try:
                results = search_duckduckgo(query, max_results=max_results)
            except Exception as e:
                errors.append(("duckduckgo", e))
        if not results and google_api_key and google_cse_id:
            try:
                results = search_google_cse(query, max_results=max_results, api_key=google_api_key, cse_id=google_cse_id)
            except Exception as e:
                errors.append(("google_cse", e))
        if errors:
            print("Search backends failed:", errors, file=sys.stderr)

    save_cache(key, results)
    return results


def format_text(results, json_output=False, csv_output=False):
    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if csv_output:
        import csv
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=["title", "href", "body"],
            extrasaction="ignore",
        )
        writer.writeheader()
        for r in results:
            writer.writerow(r)
        return

    if not results:
        print("No results found.")
        return

    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        href = r.get("href", "")
        body = r.get("body", "")
        print(f"{i}. {title}")
        print(f"   {href}")
        if body:
            print(f"   {body[:220]}")
        print()


def apply_dork(query, preset, value):
    if not preset or not value:
        return query
    tpl = DORK_PRESETS.get(preset)
    if not tpl:
        return query
    arg = tpl.format(domain=value, ext=value, text=value)
    return f"{arg} {query}"


def main():
    parser = argparse.ArgumentParser(description="Hermes centralized web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    parser.add_argument("-b", "--backend", default="auto", choices=["auto", "bing", "duckduckgo", "google_cse"])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-ttl", type=int, default=DEFAULT_TTL_MINUTES, help="Cache TTL in minutes")
    parser.add_argument("--dork", choices=list(DORK_PRESETS.keys()), help="Dork preset")
    parser.add_argument("--dork-value", default="", help="Value for dork preset")
    parser.add_argument("--google-api-key", default="", help="Google Custom Search API key")
    parser.add_argument("--google-cse-id", default="", help="Google Custom Search Engine ID")
    args = parser.parse_args()

    query = apply_dork(args.query, args.dork, args.dork_value)
    ttl = 0 if args.no_cache else args.cache_ttl

    results = text_search(
        query,
        args.max_results,
        args.backend,
        ttl,
        google_api_key=args.google_api_key,
        google_cse_id=args.google_cse_id,
    )
    format_text(results, json_output=args.json, csv_output=args.csv)


if __name__ == "__main__":
    main()
