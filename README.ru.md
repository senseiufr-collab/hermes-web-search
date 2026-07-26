# 🌐 Hermes Web Search — Универсальный CLI для веб-поиска

> **Ищите в интернете из терминала с 7+ бэкендами, дорками, кэшированием и экспортом в JSON/CSV.**

## ✨ Что это

Один CLI, который объединяет 7+ поисковых бэкендов с авто-фолбеком, кэшированием, дорками и множеством форматов вывода.

**Бэкенды:** Bing, DuckDuckGo, Brave, Google CSE, SearX, Yandex, CDP Browser, Tavily

## 🚀 Быстрый старт

```bash
cd web-search
bash install.sh
source ~/.zshrc
hsearch "квантовые вычисления" -n 10
hsearch "отчёт" --json > otchet.json
hscan "строительство" -n 5 -c market,competitors --csv
```

## 📦 Возможности

- ✅ 7+ бэкендов с авто-фолбеком
- ✅ Дорки: site, filetype, intitle, inurl
- ✅ Кэширование с TTL
- ✅ Экспорт: текст, JSON, CSV
- ✅ Прокси: `--proxy http://localhost:8080`
- ✅ CDP для JS-сайтов
- ✅ Бизнес-сканер в комплекте
- ✅ GUI на 127.0.0.1:7777
- ✅ Алиасы hsearch / hscan

## 💰 Цены

| Уровень | Цена |
|---------|------|
| **Core** | **Бесплатно** (MIT) |
| **Pro** | 1900 ₽ |
| **Enterprise** | 4900 ₽/мес |

## 📄 Лицензия

MIT