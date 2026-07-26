---
name: web-search
description: Universal multi-backend search CLI. 7+ backends, dork presets, caching, JSON/CSV export, business scan module. Use for web search, dork queries, OSINT, market research.
tags:
  - search
  - osint
  - business-intelligence
  - paid
---

# 🌐 Hermes Web Search

**Version:** 1.3  
**Category:** Web Search / OSINT  
**Price:** Core (MIT free) | Pro ($19) | Enterprise ($49/mo)  
**Demo:** `python3 search.py "test" -n 2 -b brave`

## Package contents

| File | Purpose |
|------|---------|
| `search.py` | Main CLI — 504 lines, 8 backends, dorks, caching, export |
| `business/scan.py` | Business signal scanner (6 categories) |
| `gui/scan/server.py` | Web GUI (stdlib, no dependencies) |
| `gui/scan/index.html` | Dark-theme UI |
| `install.sh` | One-line setup + shell aliases |
| `scripts/start-agent-chrome.sh` | Isolated Chrome CDP launcher |
| `freelance/README.md` | Freelance positioning guide |

## Selling points

- **8 search backends** with intelligent auto-fallback
- **6 dork presets** — `site:`, `filetype:`, `intitle:`, `inurl:`, exact, related
- **Business scan module** — 6-category competitor/market scanner
- **CDP browser** — renders JavaScript pages
- **Proxy support** — for restricted environments
- **JSON/CSV export** — pipeline-ready

## Marketplace copy (English)

> **Stop switching between search engines. One CLI to rule them all.**
>
> Hermes Web Search wraps 8 search backends (Bing, DuckDuckGo, Brave, Google CSE, SearX, Yandex, CDP, Tavily) with smart fallback, dork queries, caching, and JSON/CSV export. Includes a business signal scanner module for market research. CLI + web GUI included. MIT free core.

## Marketplace copy (Russian)

> **Хватит переключаться между поисковиками. Один CLI чтобы править всеми.**
>
> Hermes Web Search объединяет 8 бэкендов с умным фолбеком, дорками, кэшированием и экспортом. Включает бизнес-сканер для исследования рынков. CLI + веб-GUI. Бесплатное ядро MIT.