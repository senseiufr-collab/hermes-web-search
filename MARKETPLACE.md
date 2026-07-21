# Hermes Web Search — marketplace listing

## Short description
Turn Hermes Agent into a business intelligence search assistant that finds market signals, competitors, clients, regulations, and funding from the open web — with caching, dorks, JSON/CSV export, and optional Google CSE backend.

## Long description
Hermes Web Search is a centralized web search CLI and skill for Hermes Agent on macOS. It gives you:

- Multi-engine search: Bing, DuckDuckGo, optional Google CSE
- Dork presets: site, filetype, intitle, inurl, exact, related
- Business scan module: category-based intelligence with auto-classification
- Local cache, JSON/CSV export, shell aliases `hsearch` / `hscan`

Use it for:
- niche market research
- competitor monitoring
- client discovery
- regulations and compliance scans
- funding and partnership signals

## Key benefits
- Works offline after first fetch: cache reduces repeated lookups
- Business-focused dorks classify results automatically
- Export reduces manual copy-paste
- Single install: `bash install.sh && source ~/.zshrc`

## Use cases / examples
```bash
hsearch "AI" -n 5
hsearch "PDF" --dork site arxiv.org --dork-value arxiv.org -n 10
hsearch "funding" -b google_cse --google-api-key KEY --google-cse-id CSE -n 5
hscan "local AI" -n 3 -c market,competitors,clients --csv
```

## Compatibility
- macOS, Linux
- Python 3.9+
- Hermes Agent skill included

## Pricing model
- MIT-licensed core
- Premium: hosted plans, support, custom scans
- One-off reports available
