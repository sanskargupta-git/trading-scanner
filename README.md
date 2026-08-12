# 🚀 Ultimate Pro Trading Scanner

A live multi-indicator dashboard for Nifty 50, Bank Nifty, Fin Nifty, Gift Nifty and MCX
commodities. Built with Flask and yfinance.

**Live:** https://web-production-8a158.up.railway.app

---

## Pages

| Page | What it does |
|---|---|
| **Dashboard** (`/`) | Every segment as a live table with 10 indicators per symbol, plus single-stock scan, watchlist and option calculator |
| **Screener** (`/screener`) | Stack signal filters (MACD, DOW, EMA, Bollinger, DMI, RSI, ADX) to shortlist setups, sort by strength, export CSV |
| **Heatmap** (`/heatmap`) | The whole universe as coloured tiles — by daily move, signal score or RSI |
| **About** (`/about`) | What each indicator means and how the data pipeline works |

---

## Quick start

```bash
pip install -r requirements.txt
python trading_scanner.py
```

Open http://localhost:5000

The first load shows a spinner for ~10–15 seconds while the background job fetches the
first snapshot. After that every page is served from cache and loads instantly.

### Production

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 trading_scanner:app
```

Use **one worker**. The cache and its refresh thread live in process memory, so extra
workers would each fetch their own copy and multiply the load on Yahoo Finance.

---

## Configuration

Copy `.env.example` and set what you need. Nothing is required — the scanner runs fine
with no configuration at all.

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `5000` | Port to bind |
| `REFRESH_SECONDS` | `90` | How often the background job refetches every symbol |
| `GEMINI_API_KEY` | *(unset)* | Enables the ✨ AI assistant. Without it the button politely says it is not configured |

**Never commit a real key.** `.env` is gitignored; set the variable in your host's
dashboard instead (on Railway: Variables → New Variable).

---

## How it works

The naive approach — one yfinance call per symbol per timeframe — is 250+ sequential HTTP
requests per page load. That times out and gets rate-limited on any cloud host.

Instead:

1. A **background thread** wakes every `REFRESH_SECONDS`.
2. It issues **one batched `yf.download` per timeframe** (`1d`, `15m`, `1h`, `5m`) covering
   the entire ~67-ticker universe — 4 requests per cycle, not 250 per visitor.
3. Indicators are computed once per symbol and stored as plain values in a snapshot dict.
4. Every HTTP handler reads that snapshot. Requests never touch Yahoo, so they answer in
   milliseconds and cannot time out.

If Yahoo throttles an intraday timeframe, indicators fall back to daily bars so cells
degrade gracefully instead of going blank. On repeated failures the refresh loop backs
off rather than hammering the provider.

### Endpoints

| Route | Returns |
|---|---|
| `/get_master_table_data?type=` | Rendered dashboard rows + up/down stats |
| `/api/stocks?type=` | Raw indicator values (JSON) — powers screener and heatmap |
| `/export.csv?type=` | The current snapshot as CSV |
| `/healthz` | Snapshot status, symbol count, data age |
| `/version` | Build version and yfinance version |

`type` accepts `nifty50`, `banknifty`, `finnifty`, `commodities`, `giftnifty`, `all`.

---

## Layout

```
trading_scanner.py     Flask app: data layer, indicators, routes
templates/             base.html + one template per page
static/css/app.css     All styling, including the mobile card layout
static/js/             app.js (shared) + one script per page
```

---

## Notes and limits

- Prices are **delayed** Yahoo Finance data, not an exchange feed.
- The option chain uses **estimated** premiums derived from spot and strike distance. It is
  a position-sizing aid, not a real chain quote.
- Indian tickers are resolved by appending `.NS`; indices and commodities map to their
  Yahoo equivalents (`^NSEI`, `GC=F`, …).
- Commodity prices are converted from USD to an approximate MCX rupee quote using the live
  USD/INR rate.

**This is not investment advice.** For education and research only.
