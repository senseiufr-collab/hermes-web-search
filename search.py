#!/usr/bin/env python3
"""Centralized web search CLI for Hermes.
- direct search via requests + BeautifulSoup
- browser search via local CDP
- optional Google Custom Search JSON API backend
- dork presets
- caching
- export: text/json/csv
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

# Quick --help gate: show help before checking deps
if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__.split("\n-")[0].strip())
    print("Usage: python3 search.py <query> [-n N] [-b backend] [--json] [--csv] [--no-cache]")
    print("       [--dork DORK] [--dork-value VAL] [--google-api-key KEY] [--google-cse-id ID]")
    print("       [--cdp URL] [--proxy URL]")
    print("Backends: auto, bing, duckduckgo, google_cse, searx, brave, yandex, tavily, cdp")
    sys.exit(0)

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

try:
    import tavily  # type: ignore

    HAS_TAVILY = False
except ImportError:
    HAS_TAVILY = False

try:
    import websocket  # type: ignore
except ImportError:
    websocket = None

CACHE_DIR = Path.home() / ".cache" / "web-search"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_MAX_RESULTS = 10
DEFAULT_TTL_MINUTES = 15
DEFAULT_CDP = "http://127.0.0.1:9222"

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
import time
from datetime import datetime, timedelta


def search_bing(query: str, max_results: int = 10, market: str = "en-US", lang: str = "en", timeout: int = 12):
    url = "https://www.bing.com/search"
    params = {"q": query, "count": max_results, "setmkt": market, "setlang": lang}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    text = resp.text
    if 'id="b_results"' not in text:
        raise RuntimeError("Bing blocked")
    soup = BeautifulSoup(text, "html.parser")
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
            results.append({"title": title, "href": href, "body": body, "source": "bing"})
        if len(results) >= max_results:
            break
    if not results:
        results.append(
            {
                "title": "Bing results page",
                "href": resp.url,
                "body": text[:500],
                "source": "bing-raw",
            }
        )
    return results


def search_duckduckgo(query: str, max_results: int = 10, timeout: int = 12):
    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": USER_AGENT}
    data = {"q": query}
    resp = requests.post(url, data=data, headers=headers, timeout=timeout)
    text = resp.text
    if "anomaly-modal" in text:
        raise RuntimeError("DuckDuckGo blocked")
    soup = BeautifulSoup(text, "html.parser")
    results = []
    selectors = [
        (".result__a", ".result__snippet"),
        (".result__title a", ".result__snippet"),
        ("a.result__a", ".result__body"),
        (".links_main .result__a", ".links_main .result__snippet"),
    ]
    for title_sel, snippet_sel in selectors:
        for a in soup.select(title_sel)[: max_results - len(results)]:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            snippet = None
            parent = a.find_parent(".result") or a.find_parent(".links_main")
            if parent:
                snippet = parent.select_one(snippet_sel)
            body = snippet.get_text(strip=True) if snippet else ""
            if title or href:
                results.append({"title": title, "href": href, "body": body, "source": "duckduckgo"})
            if len(results) >= max_results:
                break
        if results:
            break
    if not results:
        sys.stderr.write(
            "DuckDuckGo did not return result cards. Try again shortly or switch backend with -b brave | bing.\n"
        )
        return []
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
        results.append(
            {
                "title": item.get("title", ""),
                "href": item.get("link", ""),
                "body": item.get("snippet", ""),
            }
        )
    return results


def search_searx(query: str, max_results: int = 10, instance: str = "https://search.sapti.me", timeout: int = 12):
    url = f"{instance}/search"
    params = {"q": query, "format": "json", "engines": "google,bing,duckduckgo"}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("results", [])[:max_results]:
        results.append(
            {
                "title": item.get("title", ""),
                "href": item.get("url", ""),
                "body": item.get("content", ""),
            }
        )
    return results


def search_seznam(query: str, max_results: int = 10, timeout: int = 12):
    url = "https://www.seznam.cz/search"
    params = {"q": query, "count": max_results}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    text = resp.text
    soup = BeautifulSoup(text, "html.parser")
    results = []
    for item in soup.select(".result__item, .Result")[:max_results]:
        title_el = item.select_one("h3 a, .title a")
        title = title_el.get_text(strip=True) if title_el else ""
        href = title_el.get("href", "") if title_el else ""
        body_el = item.select_one(".result__desc, .description, p")
        body = body_el.get_text(strip=True) if body_el else ""
        if title or href:
            results.append({"title": title, "href": href, "body": body, "source": "seznam"})
    if not results:
        results.append(
            {"title": "Seznam results page", "href": resp.url, "body": text[:500], "source": "seznam-raw"}
        )
    return results

def search_brave(query: str, max_results: int = 10, timeout: int = 12):
    url = "https://search.brave.com/search"
    params = {"q": query, "source": "web"}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    text = resp.text
    if ".snippet" not in text:
        raise RuntimeError("Brave blocked")
    soup = BeautifulSoup(text, "html.parser")
    results = []
    for snippet in soup.select(".snippet")[:max_results]:
        title_el = snippet.select_one(".snippet-title a, .title a")
        title = title_el.get_text(strip=True) if title_el else ""
        href = title_el.get("href", "") if title_el else ""
        body_el = snippet.select_one(".snippet-description, .description")
        body = body_el.get_text(strip=True) if body_el else ""
        if title or href:
            results.append({"title": title, "href": href, "body": body, "source": "brave"})
    if not results:
        results.append(
            {"title": "Brave results page", "href": resp.url, "body": text[:500], "source": "brave-raw"}
        )
    return results


def search_yandex(query: str, max_results: int = 10, timeout: int = 12):
    url = "https://yandex.com/search/"
    params = {"text": query, "numdoc": max_results}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    text = resp.text
    if 'class="serp-list"' not in text:
        raise RuntimeError("Yandex blocked")
    soup = BeautifulSoup(text, "html.parser")
    results = []
    for li in soup.select("li.serp-item")[:max_results]:
        title_el = li.select_one("h2 a")
        title = title_el.get_text(strip=True) if title_el else ""
        href = title_el.get("href", "") if title_el else ""
        body_el = li.select_one(".text-container, .organic__text")
        body = body_el.get_text(strip=True) if body_el else ""
        if title or href:
            results.append({"title": title, "href": href, "body": body, "source": "yandex"})
    if not results:
        results.append(
            {"title": "Yandex results page", "href": resp.url, "body": text[:500], "source": "yandex-raw"}
        )
    return results


def _cdp_get(base, path, timeout=30):
    url = base.rstrip("/") + path
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ws_client(ws_url):
    if websocket is None:
        raise RuntimeError("websocket-client is not installed")
    return websocket.create_connection(ws_url, timeout=30)


def search_cdp(query: str, max_results: int = 10, cdp: str = DEFAULT_CDP):
    targets = _cdp_get(cdp, "/json", timeout=10)
    page = next((t for t in targets if t.get("type") == "page" and t.get("webSocketDebuggerUrl")), None)
    if not page:
        raise RuntimeError("CDP has no page target")

    ws = _ws_client(page["webSocketDebuggerUrl"])
    try:
        ws.settimeout(30)
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.querySelectorAll('li.b_algo').length", "returnByValue": True}}))
        ws.recv()

        ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
            "expression": "Array.from(document.querySelectorAll('li.b_algo, li.serp-item, .result, .organic')).slice(0, " + str(max_results) + ").map(li => { const a = li.querySelector('h2 a, a.result__link, a[href]'); const s = li.querySelector('.b_caption p, .snippet-description, .result__snippet, p'); return {title: a ? a.innerText.trim() : '', href: a ? a.href : '', body: s ? s.innerText.trim() : ''}; })",
            "returnByValue": True,
        }}))
        raw = ws.recv()
        data = json.loads(raw)
        items = (((data or {}).get("result") or {}).get("result") or {}).get("value") or []
        results = [item for item in items if item.get("title") or item.get("href")]
        if not results and isinstance(items, list):
            ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {
                "expression": "Array.from(document.querySelectorAll('a[href]')).slice(0, " + str(max_results) + ").map(a => ({title: a.innerText.trim(), href: a.href, body: ''}))",
                "returnByValue": True,
            }}))
            raw = ws.recv()
            data = json.loads(raw)
            items = (((data or {}).get("result") or {}).get("result") or {}).get("value") or []
            results = [item for item in items if item.get("title") or item.get("href")]
        if not results:
            results.append({"title": "CDP empty result", "href": "", "body": (((data or {}).get("result") or {}).get("result") or {}).get("subtype") or "no-items", "source": "cdp-empty"})
        for item in results:
            item.setdefault("source", "cdp-bing")
        return results
    finally:
        try:
            ws.close()
        except Exception:
            pass


def search_tavily(query: str, max_results: int = 10):
    if not HAS_TAVILY:
        raise RuntimeError("tavily-python is not installed")
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")
    client_cls = getattr(tavily, "TavilyClient", None) or tavily.Client
    client = client_cls(api_key=api_key)
    response = client.search(query, max_results=max_results, include_raw_content=False, include_images=False)
    results = []
    for i, item in enumerate(response.get("results", [])[:max_results]):
        results.append(
            {
                "title": item.get("title", ""),
                "href": item.get("url", ""),
                "body": item.get("content", ""),
                "source": "tavily",
            }
        )
    if not results:
        results.append({"title": "Tavily raw", "href": "", "body": str(response)[:500], "source": "tavily-raw"})
    return results


def text_search(query: str, max_results: int, backend: str, ttl_minutes: int, google_api_key: str = "", google_cse_id: str = ""):
    key = cache_key(query, backend)
    cached = load_cache(key, ttl_minutes)
    if cached is not None:
        return cached

    strategies = []
    if backend == "bing":
        strategies = [("bing", lambda q: search_bing(q, max_results=max_results, timeout=12))]
    elif backend == "duckduckgo":
        strategies = [("duckduckgo", lambda q: search_duckduckgo(q, max_results=max_results, timeout=12))]
    elif backend == "google_cse":
        if google_api_key and google_cse_id:
            strategies = [("google_cse", lambda q: search_google_cse(q, max_results=max_results, api_key=google_api_key, cse_id=google_cse_id))]
    elif backend == "searx":
        strategies = [("searx", lambda q: search_searx(q, max_results=max_results, timeout=12))]
    elif backend == "brave":
        strategies = [("brave", lambda q: search_brave(q, max_results=max_results, timeout=12))]
    elif backend == "yandex":
        strategies = [("yandex", lambda q: search_yandex(q, max_results=max_results, timeout=12))]
    elif backend == "tavily":
        if HAS_TAVILY:
            strategies = [("tavily", lambda q: search_tavily(q, max_results=max_results))]
    elif backend == "cdp":
        strategies = [("cdp", lambda q: search_cdp(q, max_results=max_results))]
    else:
        seen = set()
        candidates = [
            ("searx", lambda q: search_searx(q, max_results=max_results, timeout=10)),
            ("cdp", lambda q: search_cdp(q, max_results=max_results)),
            ("seznam", lambda q: search_seznam(q, max_results=max_results, timeout=10)),
            ("bing", lambda q: search_bing(q, max_results=max_results, timeout=10)),
            ("duckduckgo", lambda q: search_duckduckgo(q, max_results=max_results, timeout=10)),
            ("brave", lambda q: search_brave(q, max_results=max_results, timeout=10)),
            ("yandex", lambda q: search_yandex(q, max_results=max_results, timeout=10)),
        ]
        strategies = [(name, fn) for name, fn in candidates if not (name in seen or seen.add(name))]
        if HAS_TAVILY:
            strategies.append(("tavily", lambda q: search_tavily(q, max_results=max_results)))
        if google_api_key and google_cse_id:
            strategies.append(
                (
                    "google_cse",
                    lambda q, api_key=google_api_key, cse_id=google_cse_id: search_google_cse(
                        q, max_results=max_results, api_key=api_key, cse_id=cse_id
                    ),
                )
            )

    errors = []
    for name, fn in strategies:
        try:
            results = fn(query)
            if results:
                save_cache(key, results)
                return results
        except Exception as e:
            errors.append((name, str(e)))

    print("Search backends failed:", errors, file=sys.stderr)
    save_cache(key, [])
    return []


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
    parser.add_argument(
        "-b",
        "--backend",
        default="auto",
        choices=["auto", "bing", "duckduckgo", "google_cse", "searx", "brave", "yandex", "tavily", "cdp"],
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-ttl", type=int, default=DEFAULT_TTL_MINUTES, help="Cache TTL in minutes")
    parser.add_argument("--dork", choices=list(DORK_PRESETS.keys()), help="Dork preset")
    parser.add_argument("--dork-value", default="", help="Value for dork preset")
    parser.add_argument("--google-api-key", default="", help="Google Custom Search API key")
    parser.add_argument("--google-cse-id", default="", help="Google Custom Search Engine ID")
    parser.add_argument("--cdp", default=DEFAULT_CDP, help="CDP endpoint for browser backend")
    parser.add_argument("--proxy", default="", help="HTTP/HTTPS proxy URL for direct backends")
    args = parser.parse_args()

    query = apply_dork(args.query, args.dork, args.dork_value)
    ttl = 0 if args.no_cache else args.cache_ttl

    proxy = args.proxy.strip()
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy
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
