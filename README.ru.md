# Hermes Web Search

Универсальный CLI для поиска в интернете для Hermes и macOS.
Поддерживает Bing, DuckDuckGo, опциональный Google CSE, дорки, кэширование и экспорт в JSON/CSV.

## Возможности
- Поиск через несколько движков: `auto`, `bing`, `duckduckgo`, `google_cse`
- Дорки: `site`, `filetype`, `intitle`, `inurl`, `exact`, `related`
- Локальный кэш для повторяющихся запросов
- Экспорт: текст, JSON, CSV
- Включен навык Hermes

## Установка
```bash
cd web-search
bash install.sh
source ~/.zshrc
```

## Использование
```bash
hsearch "Osaurus AI" -n 5
hsearch "AI" --dork site github.com --dork-value github.com -n 10
hsearch "report" --json
hsearch "docs" -b google_cse --google-api-key KEY --google-cse-id CSE -n 5
```

## Бизнес-модуль
```bash
hscan "local AI" -n 3 -c market,competitors,clients --csv
```

## Лицензия
MIT
