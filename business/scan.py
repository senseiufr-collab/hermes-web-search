#!/usr/bin/env python3
"""
Business scan module.
Run focused searches for a business niche/domain and extract potentially valuable signals:
news, market trends, competitors, potential clients, regulations, partnerships.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from search import text_search, format_text, CACHE_DIR

BUSINESS_DORKS = {
    "market": [
        '"{query}" market size growth forecast',
        '"{query}" industry trends 2025 2026',
        '"{query}" market report',
    ],
    "competitors": [
        '"{query}" competitors comparison',
        'top "{query}" companies',
        '"{query}" alternatives',
    ],
    "clients": [
        '"{query}" customers case studies',
        '"{query}" B2B clients reviews',
        '"looking for" "{query}"',
    ],
    "partnerships": [
        '"{query}" partnership integration API',
        '"{query}" ecosystem vendors',
        '"{query}" channel partner program',
    ],
    "regulations": [
        '"{query}" regulation compliance requirements',
        '"{query}" policy changes 2025 2026',
        '"{query}" licensing permits',
    ],
    "signals": [
        '"{query}" funding investment acquisition',
        '"{query}" hiring expansion growth',
        '"{query}" press release announcement',
    ],
}

CATEGORIES = list(BUSINESS_DORKS.keys())


def search_category(query: str, category: str, max_per_query: int = 5, ttl_minutes: int = 15, backend: str = "auto"):
    queries = BUSINESS_DORKS[category]
    seen = set()
    results = []
    for q in queries:
        formatted = q.format(query=query)
        items = text_search(formatted, max_results=max_per_query, backend=backend, ttl_minutes=ttl_minutes)
        for item in items:
            key = item.get("href") or item.get("title")
            if key and key not in seen:
                seen.add(key)
                item["category"] = category
                item["query"] = formatted
                results.append(item)
    return results


def classify_result(item):
    title = (item.get("title") or "").lower()
    body = (item.get("body") or "").lower()
    text = title + " " + body
    if any(k in text for k in [" funding ", " investment ", " acquired ", " acquisition ", " round ", " valuation "]):
        return "funding"
    if any(k in text for k in [" partnership ", " integrate ", " api ", " ecosystem ", " channel "]):
        return "partnership"
    if any(k in text for k in [" competitors ", " alternative ", " versus ", " vs ", " comparison "]):
        return "competitor"
    if any(k in text for k in [" regulation ", " compliance ", " policy ", " licensing ", " permit "]):
        return "regulation"
    if any(k in text for k in [" report ", " trends ", " forecast ", " market size ", " growth "]):
        return "market"
    if any(k in text for k in [" case study", " client ", " customer ", " review ", " testimonial "]):
        return "client"
    return "signal"


def format_business(results, json_output=False, csv_output=False):
    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if csv_output:
        fieldnames = ["category", "value_type", "title", "href", "body", "query"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            r = dict(r)
            r["value_type"] = classify_result(r)
            writer.writerow(r)
        return

    if not results:
        print("No business results found.")
        return

    for i, r in enumerate(results, 1):
        value_type = classify_result(r)
        print(f"{i}. [{r.get('category', '')} | {value_type}] {r.get('title', '')}")
        print(f"   {r.get('href', '')}")
        body = r.get("body", "")
        if body:
            print(f"   {body[:220]}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Business scan: find valuable market signals")
    parser.add_argument("query", help="Business niche/domain/company")
    parser.add_argument("-n", "--max-results", type=int, default=6)
    parser.add_argument("-c", "--categories", default=",".join(CATEGORIES))
    parser.add_argument("-b", "--backend", default="auto")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-ttl", type=int, default=15)
    args = parser.parse_args()

    selected = [c.strip() for c in args.categories.split(",") if c.strip() in CATEGORIES]
    if not selected:
        selected = CATEGORIES

    ttl = 0 if args.no_cache else args.cache_ttl
    combined = []
    for category in selected:
        combined.extend(search_category(args.query, category, max_per_query=args.max_results, ttl_minutes=ttl, backend=args.backend))

    format_business(combined, json_output=args.json, csv_output=args.csv)


if __name__ == "__main__":
    main()
