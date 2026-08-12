"""Ultimate Pro Trading Scanner - live NSE/MCX multi-indicator dashboard.

Data flow: a single background thread downloads every timeframe for the whole
symbol universe in batch, computes indicators once, and stores a snapshot of
plain values. Every HTTP handler reads that snapshot, so requests never touch
Yahoo Finance and cannot block on it.
"""

import os
import re
import csv
import time
import logging
import threading
from io import StringIO

from flask import Flask, jsonify, render_template, request, Response
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scanner")

app = Flask(__name__)

APP_VERSION = "v3.0-multipage"
IST = pytz.timezone("Asia/Kolkata")
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "90"))

# Symbols only ever contain these characters (BAJAJ-AUTO, M&M, ^NSEI, INR=X).
SYMBOL_RE = re.compile(r"^[A-Z0-9&^.=\-]{1,20}$")

gemini_client = None
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY:
    try:
        from google import genai

        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        log.info("Gemini assistant enabled")
    except Exception as exc:
        log.warning("Gemini assistant disabled: %s", exc)
else:
    log.info("Gemini assistant disabled: GEMINI_API_KEY not set")


NIFTY50_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "JSWSTEEL",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "BAJFINANCE", "HCLTECH",
    "ADANIENT", "TATASTEEL", "POWERGRID", "NTPC", "GRASIM", "BAJAJFINSV", "WIPRO", "INDUSINDBK", "ONGC", "COALINDIA",
    "BPCL", "HEROMOTOCO", "EICHERMOT", "DIVISLAB", "BRITANNIA", "TECHM", "NESTLEIND", "CIPLA", "APOLLOHOSP", "TATACONSUM",
    "SBILIFE", "HDFCLIFE", "BAJAJ-AUTO", "HINDALCO", "ULTRACEMCO", "DRREDDY", "ADANIPORTS", "SHRIRAMFIN", "TRENT", "M&M"
]

BANKNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
    "BANKBARODA", "PNB", "IDFCFIRSTB", "AUBANK", "FEDERALBNK", "BANDHANBNK"
]

COMMODITIES_STOCKS = ["GOLD", "GOLDM", "SILVER", "SILVERM", "CRUDEOIL", "CRUDEOILM", "NATURALGAS", "COPPER"]

GIFTNIFTY_STOCKS = ["NIFTY", "BANKNIFTY", "USDINR"]

FINNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BAJFINANCE",
    "SHRIRAMFIN", "SBILIFE", "HDFCLIFE", "CHOLAFIN"
]

TABLES = {
    "nifty50": NIFTY50_STOCKS,
    "banknifty": BANKNIFTY_STOCKS,
    "commodities": COMMODITIES_STOCKS,
    "giftnifty": GIFTNIFTY_STOCKS,
    "finnifty": FINNIFTY_STOCKS,
}

TABLE_LABELS = {
    "nifty50": "Nifty 50",
    "banknifty": "Bank Nifty",
    "commodities": "Commodities",
    "giftnifty": "Gift Nifty",
    "finnifty": "Fin Nifty",
}

FX_TICKERS = {"inr": "INR=X", "cny": "CNY=X", "rub": "RUB=X", "cad": "CAD=X"}
FX_DEFAULTS = {"inr": 83.50, "cny": 7.25, "rub": 91.50, "cad": 1.35}

LOT_SIZES = {
    "NIFTY": 25, "BANKNIFTY": 15, "FINNIFTY": 25, "RELIANCE": 250, "TCS": 175, "HDFCBANK": 550,
    "ICICIBANK": 700, "SBIN": 750, "INFY": 400, "AXISBANK": 625, "KOTAKBANK": 400, "ITC": 1600,
    "BHARTIARTL": 475, "LT": 150, "BAJFINANCE": 125, "MARUTI": 50, "SUNPHARMA": 350, "TITAN": 175,
    "TATASTEEL": 5500, "WIPRO": 1500, "ONGC": 2875, "NTPC": 1500, "POWERGRID": 2400, "COALINDIA": 2100,
    "ASIANPAINT": 300, "HCLTECH": 350, "ADANIENT": 300, "ADANIPORTS": 400, "BAJAJFINSV": 500,
    "BAJAJ-AUTO": 75, "CIPLA": 350, "DRREDDY": 125, "GRASIM": 250, "HINDALCO": 1075, "HINDUNILVR": 300,
    "INDUSINDBK": 500, "M&M": 350, "NESTLEIND": 200, "TECHM": 600, "ULTRACEMCO": 100, "BRITANNIA": 200,
    "EICHERMOT": 175, "HEROMOTOCO": 150, "SHRIRAMFIN": 300, "TRENT": 150, "APOLLOHOSP": 125,
    "HDFCLIFE": 1100, "SBILIFE": 750, "TATACONSUM": 600, "JSWSTEEL": 675,
}


def get_ticker_symbol(query):
    query = query.upper()
    if query == "NIFTY": return "^NSEI"
    elif query == "BANKNIFTY": return "^NSEBANK"
    elif query in ("GOLD", "GOLDM"): return "GC=F"
    elif query in ("SILVER", "SILVERM"): return "SI=F"
    elif query in ("CRUDEOIL", "CRUDEOILM"): return "CL=F"
    elif query == "NATURALGAS": return "NG=F"
    elif query == "COPPER": return "HG=F"
    elif query == "USDINR": return "INR=X"
    elif query == "M&M": return "M&M.NS"
    elif query.endswith(".NS") or query.startswith("^") or query.endswith("=F") or query.endswith("=X"): return query
    else: return query + ".NS"


def clean_symbol(raw):
    """Reject anything that is not a plausible ticker before it reaches yfinance
    or gets echoed back into a page."""
    sym = (raw or "").strip().upper()
    return sym if SYMBOL_RE.match(sym) else None


def format_ist_time(raw_time):
    try:
        if hasattr(raw_time, "tzinfo") and raw_time.tzinfo is not None:
            return raw_time.astimezone(IST).strftime("%d/%m %H:%M")
        return pd.to_datetime(raw_time).strftime("%d/%m %H:%M")
    except Exception:
        return str(raw_time)


UNIVERSE = []
for _syms in TABLES.values():
    for _s in _syms:
        if _s not in UNIVERSE:
            UNIVERSE.append(_s)

SYMBOL_TO_TICKER = {s: get_ticker_symbol(s) for s in UNIVERSE}
UNIQUE_TICKERS = sorted(set(SYMBOL_TO_TICKER.values()) | set(FX_TICKERS.values()))

FRAME_SPECS = {
    "1d": ("1mo", "1d"),
    "15m": ("5d", "15m"),
    "1h": ("1mo", "1h"),
    "5m": ("5d", "5m"),
}


def batch_history(tickers, period, interval):
    """One Yahoo request for every ticker instead of one request per ticker."""
    frames = {}
    if not tickers:
        return frames
    try:
        data = yf.download(
            tickers=list(tickers), period=period, interval=interval,
            group_by="ticker", auto_adjust=False, actions=False,
            progress=False, threads=True,
        )
    except Exception as exc:
        log.error("batch download failed for %s/%s: %s", period, interval, exc)
        return frames

    if data is None or len(data) == 0:
        log.warning("batch download empty for %s/%s", period, interval)
        return frames

    multi = isinstance(data.columns, pd.MultiIndex)
    available = set(data.columns.get_level_values(0)) if multi else set()

    for ticker in tickers:
        try:
            if multi:
                if ticker not in available:
                    continue
                df = data[ticker]
            else:
                df = data
            if "Close" not in df.columns:
                continue
            # yfinance aligns every ticker onto one shared index, so a symbol that
            # did not trade in a bar keeps the row with a NaN close. Those rows would
            # render as "nan" prices and poison every rolling indicator.
            df = df[df["Close"].notna()]
            if not df.empty:
                frames[ticker] = df
        except Exception:
            continue
    return frames


def _pick(frames_by_interval, ticker, preferred):
    """Preferred timeframe, falling back to daily when Yahoo throttles intraday."""
    df = frames_by_interval.get(preferred, {}).get(ticker)
    if df is not None and len(df) >= 30:
        return df
    return frames_by_interval.get("1d", {}).get(ticker)


def _rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _adx(df, window=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where(up_move > down_move, np.maximum(up_move, 0), 0)
    minus_dm = np.where(down_move > up_move, np.maximum(down_move, 0), 0)

    tr14 = tr.rolling(window=window).sum()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(window=window).sum() / tr14)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(window=window).sum() / tr14)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return plus_di, minus_di, dx.rolling(window=window).mean()


def _commodity_price(sym, price, inr_rate):
    """Yahoo quotes these in USD per troy ounce / barrel; MCX quotes rupees."""
    if sym in ("GOLD", "GOLDM"):
        price = price * inr_rate / 10.0
        return price * 0.995 if sym == "GOLDM" else price
    if sym in ("SILVER", "SILVERM"):
        price = price * inr_rate / 31.1035 * 1000
        return price * 0.995 if sym == "SILVERM" else price
    if sym in ("CRUDEOIL", "CRUDEOILM", "COPPER"):
        return price * inr_rate
    return price


def compute_metrics(sym, frames_by_interval, inr_rate):
    """Every indicator for one symbol, as plain values the pages can render or filter."""
    ticker = SYMBOL_TO_TICKER[sym]
    daily = frames_by_interval.get("1d", {}).get(ticker)
    if daily is None or daily.empty:
        return None

    price = float(daily["Close"].iloc[-1])
    prev_close = float(daily["Close"].iloc[-2]) if len(daily) >= 2 else price
    if not np.isfinite(price) or not np.isfinite(prev_close) or price <= 0:
        return None

    if sym in COMMODITIES_STOCKS:
        price = _commodity_price(sym, price, inr_rate)
        prev_close = _commodity_price(sym, prev_close, inr_rate)

    m = {
        "symbol": sym,
        "price": round(price, 2),
        "prev_close": round(prev_close, 2),
        "pct": round((price - prev_close) / prev_close * 100, 2) if prev_close else 0.0,
        "big_candle": None, "macd": None, "dow": None, "ema": None, "bb": None,
        "rsi": None, "rsi_trend": None, "dmi": None, "adx": None, "adx_trend": None,
        "bull_15m": False, "hourly_trend": "Sideways", "score": 0,
    }

    df15 = _pick(frames_by_interval, ticker, "15m")
    if df15 is not None and len(df15) >= 30:
        close, high, low, open_ = df15["Close"], df15["High"], df15["Low"], df15["Open"]
        cp = float(close.iloc[-1])

        candle_range = float(high.iloc[-1] - low.iloc[-1])
        avg_range = float((high - low).rolling(window=10).mean().iloc[-1])
        if candle_range > 0 and avg_range > 0 and candle_range >= 1.5 * avg_range:
            m["big_candle"] = "bull" if cp > float(open_.iloc[-1]) else "bear"
        else:
            m["big_candle"] = "normal"

        swing_high = float(high.iloc[-7:-1].max())
        swing_low = float(low.iloc[-7:-1].min())
        m["dow"] = "buy" if cp > swing_high else ("sell" if cp < swing_low else "wait")

        bb_mid = close.rolling(window=20).mean()
        bb_up = bb_mid + close.rolling(window=20).std() * 2
        if not pd.isna(bb_up.iloc[-1]):
            m["bb"] = "up" if cp >= float(bb_up.iloc[-1]) * 0.995 else "down"

        rsi = _rsi(close)
        if len(rsi) >= 2 and not pd.isna(rsi.iloc[-1]):
            curr_rsi, prev_rsi = float(rsi.iloc[-1]), float(rsi.iloc[-2])
            m["rsi"] = round(curr_rsi, 1)
            m["rsi_trend"] = "up" if curr_rsi > prev_rsi else ("down" if curr_rsi < prev_rsi else "flat")

        plus_di, minus_di, adx = _adx(df15)
        if len(plus_di) >= 2 and not pd.isna(plus_di.iloc[-1]) and not pd.isna(minus_di.iloc[-1]):
            m["dmi"] = "bull" if float(plus_di.iloc[-1]) >= float(minus_di.iloc[-1]) else "bear"
        if len(adx) >= 2 and not pd.isna(adx.iloc[-1]) and not pd.isna(adx.iloc[-2]):
            curr_adx, prev_adx = float(adx.iloc[-1]), float(adx.iloc[-2])
            m["adx"] = round(curr_adx, 1)
            m["adx_trend"] = "up" if curr_adx > prev_adx else ("down" if curr_adx < prev_adx else "flat")

        m["bull_15m"] = cp >= float(close.ewm(span=20, adjust=False).mean().iloc[-1])

    df1h = _pick(frames_by_interval, ticker, "1h")
    if df1h is not None and len(df1h) >= 30:
        close = df1h["Close"]
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        if not pd.isna(macd.iloc[-1]) and not pd.isna(signal.iloc[-1]):
            m["macd"] = "bull" if float(macd.iloc[-1]) >= float(signal.iloc[-1]) else "bear"

        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        last = float(close.iloc[-1])
        if last > ema20 * 1.001:
            m["hourly_trend"] = "Bull"
        elif last < ema20 * 0.999:
            m["hourly_trend"] = "Bear"

    df5m = _pick(frames_by_interval, ticker, "5m")
    if df5m is not None and len(df5m) >= 30:
        close = df5m["Close"]
        e20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        e50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        m["ema"] = "golden" if e20 >= e50 else "death"

    # Net signal count drives the screener's "strongest setups first" ordering.
    bulls = {"big_candle": "bull", "macd": "bull", "dow": "buy", "ema": "golden",
             "bb": "up", "rsi_trend": "up", "dmi": "bull"}
    bears = {"big_candle": "bear", "macd": "bear", "dow": "sell", "ema": "death",
             "bb": "down", "rsi_trend": "down", "dmi": "bear"}
    m["score"] = sum(1 for k, v in bulls.items() if m[k] == v) - sum(1 for k, v in bears.items() if m[k] == v)
    return m


BADGES = {
    "big_candle": {"bull": ("badge-bull", "▲ Big Bull"), "bear": ("badge-bear", "▼ Big Bear"),
                   "normal": ("text-muted", "Normal")},
    "macd": {"bull": ("badge-bull", "▲ Bullish"), "bear": ("badge-bear", "▼ Bearish")},
    "dow": {"buy": ("badge-buy", "BUY"), "sell": ("badge-sell", "SELL"), "wait": ("text-muted", "WAIT")},
    "ema": {"golden": ("badge-golden", "Golden"), "death": ("badge-death", "Death")},
    "bb": {"up": ("badge-bull", "▲ Up"), "down": ("badge-bear", "▼ Down")},
    "rsi_trend": {"up": ("badge-bull", "Uptick"), "down": ("badge-bear", "Downtick"),
                  "flat": ("text-warning", "Flat")},
    "dmi": {"bull": ("badge-bull", "Bullish Cross"), "bear": ("badge-bear", "Bearish Cross")},
    "adx_trend": {"up": ("badge-bull", "Uptick"), "down": ("badge-bear", "Downtick"),
                  "flat": ("text-warning", "Flat")},
}


def badge(field, value, sym):
    if value is None or field not in BADGES or value not in BADGES[field]:
        return "-"
    cls, text = BADGES[field][value]
    if cls.startswith("text-"):
        return f"<span class='{cls}'>{text}</span>"
    return f"<span class='{cls} clickable-badge' onclick=\"openIndicatorChart('{sym}')\">{text}</span>"


def render_row(m):
    sym = m["symbol"]
    pct_class = "text-success" if m["pct"] >= 0 else "text-danger"
    pct_sign = "+" if m["pct"] >= 0 else ""
    trend_badge = ("<span class='badge-bull' style='font-size:0.65rem; padding:1px 5px;'>15M Bull</span>"
                   if m["bull_15m"] else
                   "<span class='badge-bear' style='font-size:0.65rem; padding:1px 5px;'>15M Bear</span>")

    click = f"onclick=\"openIndicatorChart('{sym}')\""
    rsi_cell = f"<span class='clickable-badge' {click}>{m['rsi']}</span>" if m["rsi"] is not None else "-"
    adx_cell = f"<span class='clickable-badge' {click}>{m['adx']}</span>" if m["adx"] is not None else "-"

    return f"""
    <tr>
        <td class="symbol-col">
            <div class="d-flex justify-content-between align-items-center gap-2">
                <span onclick="scanStock('{sym}'); return false;" class='symbol-link'>{sym}</span>
                <span class="fw-bold text-success" style="font-size: 0.8rem;">₹{m['price']}</span>
                {trend_badge}
            </div>
            <div style='font-size: 0.72rem;' class='{pct_class} fw-bold'>Daily: {pct_sign}{m['pct']}%</div>
        </td>
        <td data-label="Big Candle">{badge('big_candle', m['big_candle'], sym)}</td>
        <td data-label="MACD 1H">{badge('macd', m['macd'], sym)}</td>
        <td data-label="DOW 15M">{badge('dow', m['dow'], sym)}</td>
        <td data-label="EMA 5M">{badge('ema', m['ema'], sym)}</td>
        <td data-label="Bollinger">{badge('bb', m['bb'], sym)}</td>
        <td data-label="RSI">{rsi_cell}</td>
        <td data-label="RSI Trend">{badge('rsi_trend', m['rsi_trend'], sym)}</td>
        <td data-label="DMI">{badge('dmi', m['dmi'], sym)}</td>
        <td data-label="ADX">{adx_cell}</td>
        <td data-label="ADX Trend">{badge('adx_trend', m['adx_trend'], sym)}</td>
        <td class="chart-col">
            <select class="chart-select" onchange="openChart(this, '{sym}')">
                <option value="" selected disabled>Select Chart</option>
                <option value="tradingview">TradingView</option>
                <option value="groww">Groww Chart</option>
            </select>
        </td>
    </tr>
    """


# Readers take this reference without locking; the refresh thread swaps it wholesale.
SNAPSHOT = {
    "tables": {t: {"rows": [], "stats": {"up_count": 0, "down_count": 0, "up_pct": 0, "down_pct": 0}} for t in TABLES},
    "metrics": {},
    "fx": dict(FX_DEFAULTS),
    "updated_at": 0,
    "status": "warming",
    "message": "Fetching live market data...",
}


def build_snapshot():
    started = time.time()
    frames_by_interval = {}
    for key, (period, interval) in FRAME_SPECS.items():
        frames_by_interval[key] = batch_history(UNIQUE_TICKERS, period, interval)
        log.info("fetched %s: %d/%d tickers", key, len(frames_by_interval[key]), len(UNIQUE_TICKERS))

    daily_frames = frames_by_interval.get("1d", {})
    if not daily_frames:
        raise RuntimeError("Yahoo Finance returned no daily data for any ticker")

    fx = dict(FX_DEFAULTS)
    for name, ticker in FX_TICKERS.items():
        df = daily_frames.get(ticker)
        if df is not None and not df.empty:
            fx[name] = round(float(df["Close"].iloc[-1]), 2)

    metrics = {}
    for sym in UNIVERSE:
        try:
            computed = compute_metrics(sym, frames_by_interval, fx["inr"])
            if computed:
                metrics[sym] = computed
        except Exception as exc:
            log.error("metrics failed for %s: %s: %s", sym, type(exc).__name__, exc)

    tables = {}
    for table_type, syms in TABLES.items():
        rows, up_count, down_count, scanned = [], 0, 0, 0
        for sym in syms:
            m = metrics.get(sym)
            if not m:
                continue
            rows.append(render_row(m))
            if m["macd"]:
                scanned += 1
                if m["macd"] == "bull":
                    up_count += 1
                else:
                    down_count += 1
        tables[table_type] = {
            "rows": rows,
            "stats": {
                "up_count": up_count, "down_count": down_count,
                "up_pct": round(up_count / scanned * 100, 1) if scanned else 0,
                "down_pct": round(down_count / scanned * 100, 1) if scanned else 0,
            },
        }

    global SNAPSHOT
    SNAPSHOT = {
        "tables": tables, "metrics": metrics, "fx": fx,
        "updated_at": time.time(), "status": "ok", "message": "",
    }
    log.info("snapshot built in %.1fs - %d symbols priced", time.time() - started, len(metrics))


def refresh_loop():
    failures = 0
    while True:
        try:
            build_snapshot()
            failures = 0
        except Exception as exc:
            failures += 1
            log.error("refresh failed (%d in a row): %s: %s", failures, type(exc).__name__, exc)
            if SNAPSHOT["status"] != "ok":
                SNAPSHOT["message"] = "Market data provider is not responding. Retrying..."
        # Back off when Yahoo is unhappy so we do not make the throttling worse.
        time.sleep(REFRESH_SECONDS * min(failures + 1, 4) if failures else REFRESH_SECONDS)


_worker_lock = threading.Lock()
_worker_started = False


def start_worker():
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        _worker_started = True
        threading.Thread(target=refresh_loop, name="scanner-refresh", daemon=True).start()
        log.info("background refresh thread started (every %ss)", REFRESH_SECONDS)


start_worker()


@app.after_request
def set_security_headers(response):
    # Inline handlers are used throughout the markup, so script-src still needs
    # 'unsafe-inline'; everything else is locked to this origin plus the CDN.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'",
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    return response


def page_context(active):
    return {"active": active, "version": APP_VERSION, "tables": TABLE_LABELS}


@app.route("/")
def home():
    return render_template("dashboard.html", **page_context("dashboard"), lot_sizes=LOT_SIZES,
                           watchlist=NIFTY50_STOCKS)


@app.route("/screener")
def screener():
    return render_template("screener.html", **page_context("screener"))


@app.route("/heatmap")
def heatmap():
    return render_template("heatmap.html", **page_context("heatmap"))


@app.route("/about")
def about():
    return render_template("about.html", **page_context("about"),
                           refresh_seconds=REFRESH_SECONDS, universe=len(UNIVERSE))


@app.route("/healthz")
def healthz():
    snap = SNAPSHOT
    return jsonify({
        "ok": True, "status": snap["status"], "symbols": len(snap["metrics"]),
        "age_seconds": round(time.time() - snap["updated_at"], 1) if snap["updated_at"] else None,
    })


@app.route("/version")
def version():
    return jsonify({"version": APP_VERSION, "yfinance": getattr(yf, "__version__", "unknown")})


@app.route("/get_master_table_data")
def get_master_table_data():
    table_type = request.args.get("type", "nifty50")
    if table_type not in TABLES:
        table_type = "nifty50"
    snap = SNAPSHOT
    table = snap["tables"].get(table_type, {"rows": [], "stats": {}})
    return jsonify({
        "rows": table["rows"], "stats": table["stats"],
        "status": snap["status"], "message": snap["message"], "updated_at": snap["updated_at"],
    })


@app.route("/api/stocks")
def api_stocks():
    """Raw indicator values - the screener and heatmap render from this."""
    table_type = request.args.get("type", "nifty50")
    snap = SNAPSHOT
    if table_type == "all":
        syms = UNIVERSE
    else:
        syms = TABLES.get(table_type, NIFTY50_STOCKS)
    return jsonify({
        "stocks": [snap["metrics"][s] for s in syms if s in snap["metrics"]],
        "status": snap["status"], "message": snap["message"], "updated_at": snap["updated_at"],
    })


@app.route("/export.csv")
def export_csv():
    table_type = request.args.get("type", "nifty50")
    syms = UNIVERSE if table_type == "all" else TABLES.get(table_type, NIFTY50_STOCKS)
    metrics = SNAPSHOT["metrics"]

    buf = StringIO()
    cols = ["symbol", "price", "pct", "big_candle", "macd", "dow", "ema", "bb",
            "rsi", "rsi_trend", "dmi", "adx", "adx_trend", "hourly_trend", "score"]
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    for s in syms:
        if s in metrics:
            writer.writerow(metrics[s])

    label = TABLE_LABELS.get(table_type, table_type).replace(" ", "-").lower()
    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scanner-{label}.csv"},
    )


@app.route("/get_movers")
def get_movers():
    metrics = SNAPSHOT["metrics"]
    scored = [{"symbol": s, "pct": metrics[s]["pct"]} for s in NIFTY50_STOCKS if s in metrics]
    scored.sort(key=lambda x: x["pct"], reverse=True)
    movers = scored[:2] + scored[-2:] if len(scored) >= 4 else scored
    return jsonify({"movers": movers})


@app.route("/get_currency_rate")
def get_currency_rate():
    return jsonify(SNAPSHOT["fx"])


@app.route("/get_status_bulk")
def get_status_bulk():
    """One request for the whole watchlist, served from the cached snapshot."""
    raw = request.args.get("symbols", "")
    metrics = SNAPSHOT["metrics"]
    out = {}
    for part in raw.split(",")[:120]:
        sym = clean_symbol(part)
        if not sym:
            continue
        m = metrics.get(sym)
        if not m:
            out[sym] = {"trend": "Sideways", "daily_change": 0.0, "hourly_trend": "--"}
            continue
        out[sym] = {
            "trend": "Bullish" if m["pct"] > 0 else ("Bearish" if m["pct"] < 0 else "Sideways"),
            "daily_change": m["pct"], "hourly_trend": m["hourly_trend"],
        }
    return jsonify(out)


@app.route("/get_strike_chain")
def get_strike_chain():
    query = clean_symbol(request.args.get("symbol", "RELIANCE"))
    if not query:
        return jsonify({"error": "Invalid symbol."})
    try:
        m = SNAPSHOT["metrics"].get(query)
        if m:
            current_price = m["price"]
        else:
            df = yf.Ticker(get_ticker_symbol(query)).history(period="5d", interval="1d")
            if df.empty:
                return jsonify({"error": "Symbol not found."})
            current_price = float(df["Close"].iloc[-1])

        if query == "NIFTY": interval = 50
        elif query == "BANKNIFTY": interval = 100
        elif current_price > 5000: interval = 100
        elif current_price > 2000: interval = 50
        elif current_price > 500: interval = 20
        else: interval = 10

        atm_strike = int(round(current_price / interval) * interval)
        chain = []
        for i in range(-3, 4):
            stk = atm_strike + (i * interval)
            is_atm = stk == atm_strike
            diff = stk - current_price
            if is_atm:
                ce_p = pe_p = round(interval * 0.4, 2)
            elif stk < current_price:
                ce_p = round(abs(diff) + (interval * 0.3), 2)
                pe_p = round(max(2.5, (interval * 0.4) - abs(diff) * 0.2), 2)
            else:
                ce_p = round(max(2.5, (interval * 0.4) - abs(diff) * 0.2), 2)
                pe_p = round(abs(diff) + (interval * 0.3), 2)
            chain.append({"strike": stk, "ce_price": ce_p, "pe_price": pe_p, "is_atm": is_atm})

        return jsonify({"chain": chain, "current_price": round(current_price, 2),
                        "lot_size": LOT_SIZES.get(query, 25)})
    except Exception as exc:
        log.error("strike chain failed for %s: %s", query, exc)
        return jsonify({"error": "Could not generate strike chain."})


@app.route("/get_signals")
def get_signals():
    symbol = clean_symbol(request.args.get("symbol", "RELIANCE"))
    if not symbol:
        return jsonify({"error": "Invalid symbol."})
    interval = request.args.get("interval", "15m")
    if interval not in ("5m", "15m", "1h", "1d"):
        interval = "15m"

    try:
        stock = yf.Ticker(get_ticker_symbol(symbol))
        period = {"5m": "5d", "15m": "1mo", "1h": "3mo", "1d": "1y"}[interval]
        df = stock.history(period=period, interval=interval)
        if df.empty or len(df) < 10:
            df = stock.history(period="1y", interval="1d")
            if df.empty:
                return jsonify({"error": "Insufficient historical data."})

        try:
            df.index = df.index.tz_convert(IST) if df.index.tz is not None else df.index.tz_localize("UTC").tz_convert(IST)
        except Exception:
            pass

        current_price = round(float(df["Close"].iloc[-1]), 2)
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
        ema_20 = round(float(df["EMA_20"].iloc[-1]), 2)
        ema_50 = round(float(df["EMA_50"].iloc[-1]), 2)
        prev_ema_20 = float(df["EMA_20"].iloc[-2]) if len(df) > 1 else ema_20
        prev_ema_50 = float(df["EMA_50"].iloc[-2]) if len(df) > 1 else ema_50

        # Vectorised crossover scan; the original looped row by row over a year of bars.
        above = df["EMA_20"] > df["EMA_50"]
        crossings = df.index[above != above.shift(1)][1:]
        last_cross_date = format_ist_time(crossings[-1]) if len(crossings) else "No Crossover Found"

        swing_high = round(float(df["High"].iloc[-6:-1].max()), 2) if len(df) >= 6 else current_price
        swing_low = round(float(df["Low"].iloc[-6:-1].min()), 2) if len(df) >= 6 else current_price
        current_high = float(df["High"].iloc[-1])
        current_low = float(df["Low"].iloc[-1])

        avg_volume = float(df["Volume"].rolling(window=10).mean().iloc[-1]) if len(df) >= 10 else float(df["Volume"].mean())
        current_volume = float(df["Volume"].iloc[-1])
        is_high_volume = current_volume > 1.2 * avg_volume if avg_volume and not pd.isna(avg_volume) else True
        volume_status = f"{'High' if is_high_volume else 'Normal'} ({int(current_volume)})"

        try:
            short_name = stock.info.get("shortName", symbol) or symbol
        except Exception:
            short_name = symbol

        dow_signal, dow_time = "WAIT", "N/A"
        if current_high > swing_high and is_high_volume and current_price > ema_20:
            dow_signal = "BUY"
            dow_message = f"Valid Setup! Price broke Previous Swing High of <b>₹{swing_high}</b> with high volume &amp; above 20 EMA."
            dow_time = format_ist_time(df.index[-1])
        elif current_low < swing_low and is_high_volume and current_price < ema_20:
            dow_signal = "SELL"
            dow_message = f"Valid Setup! Price broke Previous Swing Low of <b>₹{swing_low}</b> with high volume &amp; below 20 EMA."
            dow_time = format_ist_time(df.index[-1])
        else:
            dow_message = f"No Dow breakout matching criteria. Previous Swing High: ₹{swing_high}, Previous Swing Low: ₹{swing_low}."

        ema_signal = "WAIT"
        if prev_ema_20 <= prev_ema_50 and ema_20 > ema_50: ema_signal = "BUY"
        elif prev_ema_20 >= prev_ema_50 and ema_20 < ema_50: ema_signal = "SELL"

        m = SNAPSHOT["metrics"].get(symbol)
        pct_change = m["pct"] if m else 0.0
        gauge_score = max(-100, min(100, int(pct_change * 30)))
        if gauge_score > 25: gauge_trend = "Bullish"
        elif gauge_score > 0: gauge_trend = "Mild Bullish"
        elif gauge_score < -25: gauge_trend = "Bearish"
        elif gauge_score < 0: gauge_trend = "Mild Bearish"
        else: gauge_trend = "Neutral"

        return jsonify({
            "name": short_name, "price": current_price, "ema_20": ema_20, "ema_50": ema_50,
            "swing_high": swing_high, "swing_low": swing_low, "volume_status": volume_status,
            "dow_signal": dow_signal, "dow_message": dow_message, "dow_time": dow_time,
            "ema_signal": ema_signal, "last_cross_date": last_cross_date,
            "gauge_trend": gauge_trend, "gauge_score": gauge_score,
        })
    except Exception as exc:
        log.error("get_signals failed for %s: %s: %s", symbol, type(exc).__name__, exc)
        return jsonify({"error": "Could not scan this symbol right now."})


@app.route("/gemini_chat")
def gemini_chat():
    msg = (request.args.get("message", "") or "").strip()[:1000]
    if not msg:
        return jsonify({"reply": "Kahi tari prashan vichara."})
    if not gemini_client:
        return jsonify({"reply": "Gemini assistant configured nahi aahe (GEMINI_API_KEY set kara)."})
    try:
        response = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=msg)
        return jsonify({"reply": response.text if response and response.text else "Kahi tari technical error ala."})
    except Exception as exc:
        log.error("gemini chat failed: %s", exc)
        return jsonify({"reply": "Assistant sadhya uplabdh nahi. Nantar prayatna kara."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, threaded=True)
