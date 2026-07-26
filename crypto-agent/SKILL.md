---
name: crypto-agent
description: Autonomous crypto news scanner and signal generator. Uses browser automation via CDP to read Perplexity, CoinGecko, CryptoRank and other sources, then produces long-term and short-term trade signals with confidence, horizon, and risk. Stores signal history locally and supports scheduled scans.
---

# Crypto Agent

Autonomous agent that monitors crypto news/funding flows and generates buy signals for both long-term investments and short-term speculative trades.

## Setup

1. Start isolated Chrome with CDP:
   ```bash
   zsh /Users/andrew/Documents/скрипты hermes/web-search/scripts/start-agent-chrome.sh
   ```
2. Run a scan:
   ```bash
   python3 /Users/andrew/Documents/скрипты\ hermes/web-search/crypto-agent/scripts/crypto_agent.py scan
   ```

## Modes

- `scan` — run one scan and output ranked signals
- `watch` — continuous polling mode

## Outputs

Signals are printed as JSON and appended to `data/signals.jsonl`.
