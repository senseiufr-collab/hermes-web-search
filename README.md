# 🌐 Hermes Web Search — Universal Multi-Backend Search CLI

> **Search the web from your terminal with 7+ backends, dork presets, caching, and JSON/CSV export.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-ready-success)]()

---

## ✨ What It Does

A single CLI that wraps 7+ search backends with fallback logic, caching, dork support, and multiple output formats.

| Backend | Type | Notes |
|---------|------|-------|
| **Bing** | Direct HTML parse | ✅ Reliable, primary backend |
| **DuckDuckGo** | Direct HTML parse | ✅ Privacy-first |
| **Brave** | Direct HTML parse | ✅ Fast, clean results |
| **Google CSE** | API (requires key) | ⭐ Best quality, needs config |
| **SearX** | API | ✅ Self-hostable metasearch |
| **Yandex** | Direct HTML parse | ✅ Russian-language search |
| **CDP Browser** | Chrome DevTools | ✅ JS-rendered pages |
| **Tavily** | API | ✅ AI-native search |

**Auto mode** tries each backend in order and returns the first successful result set.

---

## 🚀 Quick Start

```bash
# One-line install
curl -sL https://raw.githubusercontent.com/senseiufr-collab/hermes-web-search/main/install.sh | bash

# Or manual
cd web-search
bash install.sh
source ~/.zshrc

# Search
hsearch "quantum computing breakthroughs" -n 10

# With dork
hsearch "report" --dork filetype pdf --dork-value pdf -n 10

# Export
hsearch "AI startups" --json > ai-startups.json
hsearch "market trends" --csv > trends.csv
```

---

## 📦 Features

- ✅ **7+ backends** with auto-fallback
- ✅ **Dork presets**: `site:`, `filetype:`, `intitle:`, `inurl:`, exact phrase, related
- ✅ **Caching** — configurable TTL (default 15 min), stored in `~/.cache/web-search/`
- ✅ **Export** — text, JSON, CSV
- ✅ **Proxy support** — `--proxy http://localhost:8080`
- ✅ **CDP browser** — for JS-rendered content
- ✅ **Business scan module** included — `hscan` alias
- ✅ **Zero API keys** for common backends
- ✅ **Shell aliases**: `hsearch`, `hscan`

---

## 🔧 Usage Examples

```bash
# Basic
hsearch "your query"

# More results
hsearch "AI regulation 2026" -n 20

# Specific backend
hsearch "Rust programming" -b brave

# Dork by domain
hsearch "open positions" --dork site --dork-value tesla.com

# Dork by file type
hsearch "research paper" --dork filetype --dork-value pdf

# Disable cache
hsearch "breaking news" --no-cache

# Use proxy
hsearch "blocked content" --proxy http://127.0.0.1:8080

# Business scan
hscan "cybersecurity" -n 5 -c market,competitors,signals --csv
```

---

## 🖥️ GUI Included

```bash
python3 gui/scan/server.py
# Open http://127.0.0.1:7777
```

Dark-themed web interface with category selection, backend chooser, and live results.

---

## 💼 Who It's For

| Who | Why |
|-----|-----|
| **Developer** | Quick CLI search, grep-friendly output |
| **Researcher** | Dork-based deep search, export to spreadsheets |
| **Data analyst** | JSON/CSV export for processing pipelines |
| **OSINT enthusiast** | Multi-backend with proxy + CDP |
| **Business user** | Built-in business scan module |

---

## 💰 Pricing

| Tier | Price | What You Get |
|------|-------|-------------|
| **Core** | **Free** (MIT) | Full CLI, 7+ backends, caching, dorks |
| **Pro** | $19 one-time | Priority support + CDP guide + custom dorks |
| **Enterprise** | $49/mo | Dedicated backend config, SLA, team deploy |

---

## 📦 What's Included

```
search.py            → Main CLI (504 lines, 7 backends)
business/scan.py     → Business signal scanner
install.sh           → Setup script
scripts/             → Helper scripts (CDP Chrome launcher)
gui/scan/server.py   → Web UI (stdlib http.server)
gui/scan/index.html  → Dark-theme interface
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Search smarter, not harder.*