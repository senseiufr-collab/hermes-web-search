# Hermes Web Search

Universal web search CLI for Hermes and macOS.
Supports Bing, DuckDuckGo, optional Google CSE, dorks, caching, and JSON/CSV export.

## Features
- Multi-engine search: `auto`, `bing`, `duckduckgo`, `google_cse`
- Dork presets: `site`, `filetype`, `intitle`, `inurl`, `exact`, `related`
- Local cache to reduce repeated lookups
- Export: text, JSON, CSV
- Hermes skill included

## Install
```bash
cd "/Users/andrew/Documents/скрипты hermes/web-search"
bash install.sh
source ~/.zshrc
```

## Usage
```bash
hsearch "Osaurus AI" -n 5
hsearch "AI" --dork site github.com --dork-value github.com -n 10
hsearch "report" --json
hsearch "docs" -b google_cse --google-api-key KEY --google-cse-id CSE -n 5
```

## Business module
```bash
hscan "local AI" -n 3 -c market,competitors,clients --csv
```

## License
MIT
