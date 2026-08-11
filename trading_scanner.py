import os
import time
import logging
import threading

from flask import Flask, jsonify, render_template_string, request
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scanner")

app = Flask(__name__)

APP_VERSION = "v2.0-batch-cache"
IST = pytz.timezone("Asia/Kolkata")
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "90"))

# Gemini is optional. A missing/broken SDK must never stop the scanner from booting.
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

COMMODITIES_STOCKS = [
    "GOLD", "GOLDM", "SILVER", "SILVERM", "CRUDEOIL", "CRUDEOILM", "NATURALGAS", "COPPER"
]

GIFTNIFTY_STOCKS = ["NIFTY", "BANKNIFTY", "USDINR"]

FINNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BAJFINANCE", "SHRIRAMFIN", "SBILIFE", "HDFCLIFE", "CHOLAFIN"
]

TABLES = {
    "nifty50": NIFTY50_STOCKS,
    "banknifty": BANKNIFTY_STOCKS,
    "commodities": COMMODITIES_STOCKS,
    "giftnifty": GIFTNIFTY_STOCKS,
    "finnifty": FINNIFTY_STOCKS,
}

FX_TICKERS = {"inr": "INR=X", "cny": "CNY=X", "rub": "RUB=X", "cad": "CAD=X"}
FX_DEFAULTS = {"inr": 83.50, "cny": 7.25, "rub": 91.50, "cad": 1.35}


def get_ticker_symbol(query):
    query = query.upper()
    if query == "NIFTY": return "^NSEI"
    elif query == "BANKNIFTY": return "^NSEBANK"
    elif query == "GOLD" or query == "GOLDM": return "GC=F"
    elif query == "SILVER" or query == "SILVERM": return "SI=F"
    elif query == "CRUDEOIL" or query == "CRUDEOILM": return "CL=F"
    elif query == "NATURALGAS": return "NG=F"
    elif query == "COPPER": return "HG=F"
    elif query == "USDINR": return "INR=X"
    elif query == "M&M": return "M&M.NS"
    elif query.endswith(".NS") or query.startswith("^") or query.endswith("=F") or query.endswith("=X"): return query
    else: return query + ".NS"


def format_ist_time(raw_time):
    try:
        if hasattr(raw_time, "tzinfo") and raw_time.tzinfo is not None:
            return raw_time.astimezone(IST).strftime("%d/%m %H:%M")
        return pd.to_datetime(raw_time).strftime("%d/%m %H:%M")
    except Exception:
        return str(raw_time)


# Every symbol the dashboard can ever show, de-duplicated at the Yahoo-ticker level so
# GOLD and GOLDM (both GC=F) cost a single download slot.
UNIVERSE = []
for _syms in TABLES.values():
    for _s in _syms:
        if _s not in UNIVERSE:
            UNIVERSE.append(_s)

SYMBOL_TO_TICKER = {s: get_ticker_symbol(s) for s in UNIVERSE}
UNIQUE_TICKERS = sorted(set(SYMBOL_TO_TICKER.values()) | set(FX_TICKERS.values()))

# period/interval pairs pulled once per refresh cycle for the whole universe.
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
            tickers=list(tickers),
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=True,
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
            # yfinance aligns every ticker onto one shared index, so a symbol that did
            # not trade in a given bar keeps the row with a NaN close. Those rows would
            # render as "Rs nan" and poison every rolling indicator.
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
    plus_dm = np.where((up_move > down_move), np.maximum(up_move, 0), 0)
    minus_dm = np.where((down_move > up_move), np.maximum(down_move, 0), 0)

    tr14 = tr.rolling(window=window).sum()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(window=window).sum() / tr14)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(window=window).sum() / tr14)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return plus_di, minus_di, dx.rolling(window=window).mean()


def compute_metrics(sym, frames_by_interval):
    """Derive every indicator for one symbol from the already-downloaded frames."""
    ticker = SYMBOL_TO_TICKER[sym]
    daily = frames_by_interval.get("1d", {}).get(ticker)
    if daily is None or daily.empty:
        return None

    curr_price = float(daily["Close"].iloc[-1])
    prev_close = float(daily["Close"].iloc[-2]) if len(daily) >= 2 else curr_price
    if not np.isfinite(curr_price) or not np.isfinite(prev_close) or curr_price <= 0:
        return None

    m = {
        "symbol": sym,
        "curr_price": curr_price,
        "prev_close": prev_close,
        "big_candle": "-", "macd": "-", "dow": "-", "ema": "-", "bb": "-",
        "rsi_val": "-", "rsi_status": "-", "dmi": "-", "adx_val": "-", "adx_trend": "-",
        "is_bull_15m": False, "macd_bull": None, "hourly_trend": "Sideways",
    }

    click = f"onclick=\"openIndicatorChart('{sym}')\""

    df15 = _pick(frames_by_interval, ticker, "15m")
    if df15 is not None and len(df15) >= 30:
        close, high, low, open_ = df15["Close"], df15["High"], df15["Low"], df15["Open"]
        cp = float(close.iloc[-1])

        candle_range = float(high.iloc[-1] - low.iloc[-1])
        avg_range = float((high - low).rolling(window=10).mean().iloc[-1])
        if candle_range > 0 and avg_range > 0 and candle_range >= 1.5 * avg_range:
            if cp > float(open_.iloc[-1]):
                m["big_candle"] = f"<span class='badge-bull clickable-badge' {click}>▲ Big Bull</span>"
            else:
                m["big_candle"] = f"<span class='badge-bear clickable-badge' {click}>▼ Big Bear</span>"
        else:
            m["big_candle"] = "<span class='text-muted'>Normal</span>"

        swing_high = float(high.iloc[-7:-1].max())
        swing_low = float(low.iloc[-7:-1].min())
        if cp > swing_high:
            m["dow"] = f"<span class='badge-buy clickable-badge' {click}>BUY</span>"
        elif cp < swing_low:
            m["dow"] = f"<span class='badge-sell clickable-badge' {click}>SELL</span>"
        else:
            m["dow"] = "<span class='text-muted'>WAIT</span>"

        bb_mid = close.rolling(window=20).mean()
        bb_up = bb_mid + close.rolling(window=20).std() * 2
        if not pd.isna(bb_up.iloc[-1]) and cp >= float(bb_up.iloc[-1]) * 0.995:
            m["bb"] = f"<span class='badge-bull clickable-badge' {click}>▲ Up</span>"
        else:
            m["bb"] = f"<span class='badge-bear clickable-badge' {click}>▼ Down</span>"

        rsi = _rsi(close)
        if len(rsi) >= 2 and not pd.isna(rsi.iloc[-1]):
            curr_rsi, prev_rsi = float(rsi.iloc[-1]), float(rsi.iloc[-2])
            m["rsi_val"] = f"<span class='clickable-badge' {click}>{round(curr_rsi, 1)}</span>"
            if curr_rsi > prev_rsi:
                m["rsi_status"] = f"<span class='badge-bull clickable-badge' {click}>Uptick</span>"
            elif curr_rsi < prev_rsi:
                m["rsi_status"] = f"<span class='badge-bear clickable-badge' {click}>Downtick</span>"
            else:
                m["rsi_status"] = "<span class='text-warning'>Flat</span>"

        plus_di, minus_di, adx = _adx(df15)
        if len(plus_di) >= 2 and not pd.isna(plus_di.iloc[-1]) and not pd.isna(minus_di.iloc[-1]):
            if float(plus_di.iloc[-1]) >= float(minus_di.iloc[-1]):
                m["dmi"] = f"<span class='badge-bull clickable-badge' {click}>Bullish Cross</span>"
            else:
                m["dmi"] = f"<span class='badge-bear clickable-badge' {click}>Bearish Cross</span>"
        if len(adx) >= 2 and not pd.isna(adx.iloc[-1]) and not pd.isna(adx.iloc[-2]):
            curr_adx, prev_adx = float(adx.iloc[-1]), float(adx.iloc[-2])
            m["adx_val"] = f"<span class='clickable-badge' {click}>{round(curr_adx, 1)}</span>"
            if curr_adx > prev_adx:
                m["adx_trend"] = f"<span class='badge-bull clickable-badge' {click}>Uptick</span>"
            elif curr_adx < prev_adx:
                m["adx_trend"] = f"<span class='badge-bear clickable-badge' {click}>Downtick</span>"
            else:
                m["adx_trend"] = "<span class='text-warning'>Flat</span>"

        m["is_bull_15m"] = cp >= float(close.ewm(span=20, adjust=False).mean().iloc[-1])

    df1h = _pick(frames_by_interval, ticker, "1h")
    if df1h is not None and len(df1h) >= 30:
        close = df1h["Close"]
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        if not pd.isna(macd.iloc[-1]) and not pd.isna(signal.iloc[-1]):
            if float(macd.iloc[-1]) >= float(signal.iloc[-1]):
                m["macd"] = f"<span class='badge-bull clickable-badge' {click}>▲ Bullish</span>"
                m["macd_bull"] = True
            else:
                m["macd"] = f"<span class='badge-bear clickable-badge' {click}>▼ Bearish</span>"
                m["macd_bull"] = False

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
        if e20 >= e50:
            m["ema"] = f"<span class='badge-golden clickable-badge' {click}>Golden</span>"
        else:
            m["ema"] = f"<span class='badge-death clickable-badge' {click}>Death</span>"

    return m


def render_row(m, table_type, inr_rate):
    sym = m["symbol"]
    curr_price, prev_close = m["curr_price"], m["prev_close"]

    if table_type == "commodities":
        if sym in ("GOLD", "GOLDM"):
            curr_price = curr_price * inr_rate / 10.0
            prev_close = prev_close * inr_rate / 10.0
            if sym == "GOLDM":
                curr_price *= 0.995
                prev_close *= 0.995
        elif sym in ("SILVER", "SILVERM"):
            curr_price = curr_price * inr_rate / 31.1035 * 1000
            prev_close = prev_close * inr_rate / 31.1035 * 1000
            if sym == "SILVERM":
                curr_price *= 0.995
                prev_close *= 0.995
        elif sym in ("CRUDEOIL", "CRUDEOILM", "COPPER"):
            curr_price = curr_price * inr_rate
            prev_close = prev_close * inr_rate

    daily_pct = round(((curr_price - prev_close) / prev_close) * 100, 2) if prev_close else 0.0
    pct_class = "text-success" if daily_pct >= 0 else "text-danger"
    pct_sign = "+" if daily_pct >= 0 else ""
    daily_html = f"<div style='font-size: 0.72rem;' class='{pct_class} fw-bold'>Daily: {pct_sign}{daily_pct}%</div>"

    if m["is_bull_15m"]:
        b_badge = "<span class='badge-bull' style='font-size:0.65rem; padding:1px 5px;'>15M Bull</span>"
    else:
        b_badge = "<span class='badge-bear' style='font-size:0.65rem; padding:1px 5px;'>15M Bear</span>"

    return f"""
    <tr>
        <td class="symbol-col">
            <div class="d-flex justify-content-between align-items-center gap-2">
                <span onclick="scanStock('{sym}'); return false;" class='symbol-link'>{sym}</span>
                <span class="fw-bold text-success" style="font-size: 0.8rem;">₹{round(curr_price, 2)}</span>
                {b_badge}
            </div>
            {daily_html}
        </td>
        <td data-label="Big Candle">{m['big_candle']}</td>
        <td data-label="MACD 1H">{m['macd']}</td>
        <td data-label="DOW 15M">{m['dow']}</td>
        <td data-label="EMA 5M">{m['ema']}</td>
        <td data-label="Bollinger">{m['bb']}</td>
        <td data-label="RSI">{m['rsi_val']}</td>
        <td data-label="RSI Trend">{m['rsi_status']}</td>
        <td data-label="DMI">{m['dmi']}</td>
        <td data-label="ADX">{m['adx_val']}</td>
        <td data-label="ADX Trend">{m['adx_trend']}</td>
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
            computed = compute_metrics(sym, frames_by_interval)
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
            rows.append(render_row(m, table_type, fx["inr"]))
            if m["macd_bull"] is not None:
                scanned += 1
                if m["macd_bull"]:
                    up_count += 1
                else:
                    down_count += 1
        stats = {
            "up_count": up_count,
            "down_count": down_count,
            "up_pct": round(up_count / scanned * 100, 1) if scanned else 0,
            "down_pct": round(down_count / scanned * 100, 1) if scanned else 0,
        }
        tables[table_type] = {"rows": rows, "stats": stats}

    global SNAPSHOT
    SNAPSHOT = {
        "tables": tables,
        "metrics": metrics,
        "fx": fx,
        "updated_at": time.time(),
        "status": "ok",
        "message": "",
    }
    log.info("snapshot built in %.1fs — %d symbols priced", time.time() - started, len(metrics))


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

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Pro Trading Scanner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root[data-theme="dark"] {
            --bg-color: #0a0c10;
            --text-color: #e2e8f0;
            --sidebar-bg: #111318;
            --card-bg: #111318;
            --border-color: #2d3748;
            --input-bg: #111318;
            --input-text: #e2e8f0;
            --table-head-bg: #1a202c;
            --section-border: #2d3748;
            --row-hover-bg: #1e293b;
            --muted-color: #94a3b8;
        }

        :root[data-theme="light"] {
            --bg-color: #f8fafc;
            --text-color: #0f172a;
            --sidebar-bg: #ffffff;
            --card-bg: #ffffff;
            --border-color: #cbd5e1;
            --input-bg: #f1f5f9;
            --input-text: #0f172a;
            --table-head-bg: #e2e8f0;
            --section-border: #94a3b8;
            --row-hover-bg: #e0f2fe;
            --muted-color: #64748b;
        }

        /* Bootstrap's default muted grey is close to unreadable on the dark canvas. */
        .text-muted { color: var(--muted-color) !important; }
        .form-control::placeholder { color: var(--muted-color); opacity: 0.8; }

        body { background-color: var(--bg-color); color: var(--text-color); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; transition: background 0.3s, color 0.3s; }

        .sidebar { height: 100vh; position: fixed; top: 0; left: 0; width: 310px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border-color); padding: 15px; display: flex; flex-direction: column; z-index: 100; overflow-y: auto; transition: width 0.3s ease; }
        .sidebar.collapsed { width: 85px; padding: 10px 5px; }
        .sidebar.collapsed .watchlist-scroll-container,
        .sidebar.collapsed .calc-panel-sidebar,
        .sidebar.collapsed h5,
        .sidebar.collapsed .input-group { display: none !important; }

        .watchlist-scroll-container { max-height: 250px; overflow-y: auto; margin-bottom: 10px; padding-right: 5px; }
        .main-content { margin-left: 325px; padding: 25px; transition: margin-left 0.3s ease; }
        .main-content.expanded { margin-left: 100px; }

        .card { background-color: var(--card-bg) !important; color: var(--text-color) !important; border: 1px solid var(--border-color) !important; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); margin-bottom: 20px; }
        .form-control, .form-select { background-color: var(--input-bg) !important; color: var(--input-text) !important; border-color: var(--border-color) !important; }

        .top-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; overflow-x: auto; gap: 10px; }
        .broker-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 6px 14px; border-radius: 16px; font-weight: bold; font-size: 0.8rem; cursor: pointer; text-decoration: none; white-space: nowrap; transition: 0.2s; display: inline-block; }
        .broker-btn:hover { background: var(--border-color); color: #38bdf8; }

        .live-widget-box { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 5px 12px; display: flex; align-items: center; gap: 10px; font-size: 0.78rem; font-weight: 600; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.2); cursor: pointer; transition: 0.2s; }
        .live-widget-box:hover { border-color: #38bdf8; transform: scale(1.01); }
        .flag-wave { display: inline-block; animation: waveFlag 1.2s infinite ease-in-out alternate; font-size: 1.1rem; }
        @keyframes waveFlag {
            0% { transform: rotate(0deg) translateY(0); }
            100% { transform: rotate(-10deg) translateY(-2px); }
        }
        .highlight-date { background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.4); font-weight: bold; }

        .modal-content { background-color: var(--card-bg) !important; color: var(--text-color) !important; border: 1px solid var(--border-color) !important; }
        .global-card { background: var(--input-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }

        .ticker-wrapper-outer { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 10px 15px; position: relative; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .ticker-rope { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle, #38bdf8 1.2px, transparent 1.2px); background-size: 25px 25px; z-index: 1; opacity: 0.25; border-radius: 12px; }
        .ticker-wrapper-inner { display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 15px; position: relative; z-index: 2; width: 100%; }

        .ticker-item { display: flex; align-items: center; position: relative; cursor: pointer; }
        .ticker-ribbon { padding: 6px 18px; border-radius: 30px; font-weight: bold; font-size: 0.82rem; color: #0f172a; box-shadow: 0 2px 4px rgba(0,0,0,0.3); white-space: nowrap; transition: transform 0.2s; }
        .ticker-ribbon:hover { transform: scale(1.05); filter: brightness(1.1); }
        .ribbon-bull { background-color: #34d399; border: 1px solid #059669; }
        .ribbon-bear { background-color: #f87171; border: 1px solid #dc2626; color: #fff; }
        .ribbon-flat { background-color: #fbbf24; border: 1px solid #d97706; }

        .ticker-rocket { font-size: 1.3rem; position: absolute; top: 50%; transform: translateY(-50%); z-index: 3; }
        .rocket-bull { left: -10px; animation: bounceRocket 0.5s infinite alternate; }
        .rocket-bear { right: -10px; animation: bounceRocket 0.5s infinite alternate; }
        @keyframes bounceRocket {
            0% { transform: translateY(-50%) translateX(0); }
            100% { transform: translateY(-50%) translateX(4px); }
        }

        .master-table-wrapper { width: 100%; overflow-x: auto; max-height: 550px; overflow-y: auto; position: relative; }
        .master-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: center; }
        .master-table th, .master-table td { border: 1px solid var(--section-border); padding: 10px 6px; white-space: nowrap; color: var(--text-color); }

        .master-table th { background-color: var(--table-head-bg); font-weight: bold; position: sticky; top: 0; z-index: 10; }
        .master-table th.symbol-th { position: sticky; left: 0; top: 0; z-index: 30; background-color: var(--table-head-bg); }
        .symbol-col { text-align: left !important; padding-left: 12px !important; position: sticky; left: 0; background-color: var(--card-bg); z-index: 5; }

        .master-table tbody tr { transition: all 0.25s ease-in-out; cursor: pointer; }
        .master-table tbody tr:hover {
            background-color: var(--row-hover-bg) !important;
            transform: scale(1.015);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
            z-index: 20;
            position: relative;
        }
        .master-table tbody tr:hover td { background-color: transparent !important; }

        .clickable-badge { cursor: pointer; transition: transform 0.1s; display: inline-block; }
        .clickable-badge:hover { transform: scale(1.08); filter: brightness(1.2); }

        .badge-bull { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-bear { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-golden { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #059669; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-death { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #dc2626; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-buy { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-sell { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }

        .watchlist-item { padding: 8px 10px; margin-bottom: 6px; background: var(--card-bg); border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); font-size: 0.85rem; transition: 0.2s; display: flex; flex-direction: column; gap: 2px; }
        .watchlist-item:hover { border-color: #3b82f6; }

        .bull { color: #34d399; font-weight: bold; }
        .bear { color: #f87171; font-weight: bold; }
        .flat { color: #fbbf24; font-weight: bold; }

        .calc-panel-sidebar { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; margin-top: 10px; }
        .chain-table { font-size: 0.75rem; width: 100%; text-align: center; margin-top: 5px; }
        .chain-table th { background: var(--card-bg); color: var(--text-color); padding: 4px; }
        .chain-row { border-bottom: 1px solid var(--border-color); }
        .atm-row { background-color: rgba(251, 191, 36, 0.2) !important; color: #fbbf24 !important; border: 1px solid #fbbf24; font-weight: bold; }
        .call-btn, .put-btn { cursor: pointer; padding: 2px 5px; border-radius: 3px; font-weight: bold; font-size: 0.7rem; display: inline-block; margin: 1px; }
        .call-btn { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; }
        .put-btn { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; }

        .calc-chapter-box { background: var(--input-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px; margin-top: 6px; font-size: 0.75rem; display: none; }
        .calc-chapter-title { font-weight: bold; color: #38bdf8; margin-bottom: 4px; display: flex; align-items: center; gap: 5px; }

        .sidebar-toggle-btn { background: var(--border-color); color: var(--text-color); border: none; border-radius: 4px; font-size: 0.75rem; padding: 2px 6px; cursor: pointer; float: right; }
        .sidebar-toggle-btn:hover { background: #3b82f6; color: #fff; }

        .symbol-link { color: #38bdf8; text-decoration: none; font-weight: bold; cursor: pointer; }
        .symbol-link:hover { text-decoration: underline; }

        .chart-select { background: var(--input-bg); color: var(--text-color); border: 1px solid var(--border-color); font-size: 0.72rem; padding: 3px 6px; border-radius: 4px; cursor: pointer; }
        .chart-select:hover { border-color: #38bdf8; }

        .gauge-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 10px; text-align: center; }
        .meter-arc { width: 180px; height: 90px; border-top-left-radius: 180px; border-top-right-radius: 180px; background: conic-gradient(from 180deg at 50% 100%, #ef4444 0deg, #f97316 50deg, #64748b 100deg, #64748b 140deg, #22c55e 180deg); position: relative; overflow: hidden; margin-bottom: 10px; }
        .meter-needle { width: 4px; height: 75px; background: #ffffff; position: absolute; bottom: 0; left: 50%; transform-origin: bottom center; transform: translateX(-50%) rotate(45deg); transition: transform 0.6s ease-in-out; border-radius: 2px; }
        .meter-pin { width: 16px; height: 16px; background: #1e293b; border: 3px solid #fff; border-radius: 50%; position: absolute; bottom: -8px; left: calc(50% - 8px); }

        .theme-toggle-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 6px 12px; border-radius: 16px; font-weight: bold; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.2s; width: 100%; justify-content: center; margin-bottom: 6px; }
        .theme-toggle-btn:hover { border-color: #3b82f6; }

        .global-timer-badge { background: var(--card-bg); border: 1px solid var(--border-color); color: #38bdf8; padding: 4px 10px; border-radius: 16px; font-weight: bold; font-size: 0.78rem; text-align: center; width: 100%; display: block; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }

        .loading-cell { padding: 30px 10px !important; }
        .spinner-dot { display: inline-block; width: 8px; height: 8px; margin: 0 3px; border-radius: 50%; background: #38bdf8; animation: dotPulse 1.2s infinite ease-in-out; }
        .spinner-dot:nth-child(2) { animation-delay: 0.2s; }
        .spinner-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes dotPulse { 0%, 80%, 100% { opacity: 0.25; transform: scale(0.8); } 40% { opacity: 1; transform: scale(1.15); } }

        @keyframes rotateSparkle {
            0% { transform: rotate(0deg); box-shadow: 0 0 6px #3b82f6, 0 0 12px #8b5cf6, inset 0 0 6px rgba(255,255,255,0.3); }
            50% { box-shadow: 0 0 12px #60a5fa, 0 0 20px #c084fc, inset 0 0 8px rgba(255,255,255,0.5); }
            100% { transform: rotate(360deg); box-shadow: 0 0 6px #3b82f6, 0 0 12px #8b5cf6, inset 0 0 6px rgba(255,255,255,0.3); }
        }

        @keyframes pulseGlow {
            0% { transform: scale(1); }
            50% { transform: scale(1.06); }
            100% { transform: scale(1); }
        }

        .gemini-chat-btn {
            position: fixed; bottom: 20px; right: 20px; width: 50px; height: 50px;
            background: linear-gradient(135deg, #3b82f6, #9333ea, #ec4899); background-size: 300% 300%;
            color: white; border: 1.5px solid rgba(255, 255, 255, 0.5); border-radius: 50%;
            display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
            cursor: pointer; z-index: 1000; animation: pulseGlow 2.5s infinite ease-in-out;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.7); transition: transform 0.3s;
        }

        .gemini-chat-btn::before {
            content: ''; position: absolute; inset: -3px; border-radius: 50%;
            background: conic-gradient(from 0deg, #3b82f6, #ec4899, #facc15, #3b82f6);
            z-index: -1; animation: rotateSparkle 3s linear infinite;
        }

        .gemini-chat-btn:hover { transform: scale(1.12); }

        .gemini-chat-window { position: fixed; bottom: 80px; right: 20px; width: 350px; height: 450px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 1000; display: none; flex-direction: column; overflow: hidden; }
        .chat-header { background: var(--table-head-bg); padding: 12px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); color: #60a5fa; }
        .chat-body { flex: 1; padding: 12px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; }
        .chat-footer { padding: 10px; background: var(--table-head-bg); border-top: 1px solid var(--border-color); display: flex; gap: 5px; }
        .chat-msg { padding: 8px 12px; border-radius: 8px; max-width: 85%; line-height: 1.4; white-space: pre-wrap; }
        .msg-user { background: #2563eb; color: white; align-self: flex-end; }
        .msg-gemini { background: var(--border-color); color: var(--text-color); align-self: flex-start; }

        .mobile-only { display: none; }
        .sidebar-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 99; }

        @media (max-width: 900px) {
            body { overflow-x: hidden; -webkit-text-size-adjust: 100%; }
            .mobile-only { display: block; }
            .sidebar-backdrop.show { display: block; }

            /* Sidebar becomes an off-canvas drawer instead of a permanent column. */
            .sidebar { width: 84vw; max-width: 330px; padding: 15px; transform: translateX(-102%); transition: transform 0.28s ease; box-shadow: 6px 0 24px rgba(0,0,0,0.45); }
            .sidebar.mobile-open { transform: translateX(0); }
            .sidebar .sidebar-toggle-btn { display: none; }
            /* The desktop "collapsed" rules must not shrink or blank the drawer. */
            .sidebar.collapsed { width: 84vw; max-width: 330px; padding: 15px; }
            .sidebar.collapsed .watchlist-scroll-container,
            .sidebar.collapsed .calc-panel-sidebar,
            .sidebar.collapsed h5,
            .sidebar.collapsed .input-group { display: block !important; }

            .main-content, .main-content.expanded { margin-left: 0; padding: 14px 12px; }

            .menu-btn { width: 100%; background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 10px; border-radius: 10px; font-weight: bold; font-size: 0.85rem; cursor: pointer; }
            .top-nav { flex-direction: column; align-items: stretch; gap: 10px; overflow: visible; }
            .broker-row { overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 4px; }
            .nav-right { flex-direction: column; align-items: stretch !important; }
            .nav-right > div:last-child { display: flex; gap: 8px; align-items: center; }
            .theme-toggle-btn { margin-bottom: 0; flex: 1; }
            .global-timer-badge { width: auto; padding: 7px 14px; }

            /* The inline flex heading crams the stats badge onto the title line. */
            .table-heading { display: block !important; font-size: 1.02rem; line-height: 1.5; }
            .table-heading .stats-badge { display: block; font-size: 0.76rem !important; margin: 4px 0 0 0 !important; }
            .table-subtitle { display: none; }
            .live-widget-box { flex-wrap: wrap; justify-content: center; font-size: 0.72rem; }
            .theme-toggle-btn, .global-timer-badge { font-size: 0.72rem; }

            h2.fw-bold { font-size: 1.3rem; }
            .ticker-wrapper-outer { padding: 10px; }
            .ticker-ribbon { font-size: 0.72rem; padding: 5px 14px; }
            .card { margin-bottom: 14px; }

            /* Twelve columns cannot fit a phone, so each row becomes a stacked card. */
            .master-table-wrapper { max-height: 68vh; overflow-x: hidden; }
            .master-table thead { display: none; }
            .master-table, .master-table tbody { display: block; width: 100%; }
            .master-table tbody tr {
                display: grid; grid-template-columns: 1fr 1fr;
                border: 1px solid var(--section-border); border-radius: 10px;
                margin-bottom: 10px; background: var(--card-bg); overflow: hidden;
            }
            .master-table tbody tr:hover { transform: none; box-shadow: none; background: var(--card-bg) !important; }
            .master-table td {
                border: none; border-top: 1px solid var(--section-border);
                display: flex; align-items: center; justify-content: space-between;
                gap: 8px; padding: 8px 10px; font-size: 0.78rem; white-space: normal;
            }
            .master-table td::before { content: attr(data-label); color: #94a3b8; font-size: 0.68rem; font-weight: 600; text-align: left; }
            .master-table td:nth-child(even):not(.chart-col) { border-right: 1px solid var(--section-border); }

            .master-table td.symbol-col {
                grid-column: 1 / -1; position: static; display: block;
                border-top: none; background: var(--table-head-bg); padding: 10px;
            }
            .master-table td.chart-col { grid-column: 1 / -1; }
            .master-table td.symbol-col::before,
            .master-table td.chart-col::before,
            .master-table td.loading-cell::before { content: none; }
            .master-table td.chart-col .chart-select { width: 100%; padding: 8px; font-size: 0.8rem; }
            .master-table td.loading-cell { grid-column: 1 / -1; display: block; text-align: center; border-top: none; }

            .gemini-chat-window { width: auto; left: 12px; right: 12px; height: 62vh; bottom: 78px; }
            .gemini-chat-btn { bottom: 16px; right: 16px; }
        }
    </style>
</head>
<body>

<div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeMobileSidebar()"></div>

<div class="sidebar shadow-sm" id="sidebarContainer">
    <div class="d-flex justify-content-between align-items-center mb-2">
        <h5 class="fw-bold text-info mb-0">Scanner</h5>
        <button class="sidebar-toggle-btn" onclick="toggleSidebar()">&laquo;</button>
    </div>

    <div class="input-group input-group-sm mb-2">
        <input type="text" id="newStockInput" class="form-control" placeholder="Add Symbol">
        <button class="btn btn-primary" onclick="addToWatchlist()">Add</button>
    </div>

    <div class="watchlist-scroll-container" id="watchlistContainer"></div>

    <div class="calc-panel-sidebar">
        <button class="btn btn-outline-info btn-sm w-100 fw-bold mb-2" onclick="toggleOptionCalculator()">Option Calculator</button>
        <div id="optionCalcBody" style="display:none;">
            <div id="activeStockLabel" class="text-muted fs-7 text-center mb-1">Select stock</div>
            <div id="chainTableContainer" class="mb-2" style="max-height: 120px; overflow-y: auto; display:none;"></div>
            <div class="mb-1">
                <input type="text" id="selectedOptionName" class="form-control form-control-xs bg-dark text-center fw-bold text-warning" readonly placeholder="Click strike">
            </div>
            <div class="row g-1 mb-1">
                <div class="col-6">
                    <select id="calcType" class="form-select form-select-xs">
                        <option value="BUY">Buyer</option>
                        <option value="SELL">Seller</option>
                    </select>
                </div>
                <div class="col-6">
                    <input type="number" id="calcLot" class="form-control form-control-xs text-center" placeholder="Lot">
                </div>
            </div>
            <div class="row g-1 mb-1">
                <div class="col-6">
                    <input type="number" id="calcEntry" class="form-control form-control-xs text-center" placeholder="Entry Price">
                </div>
                <div class="col-6">
                    <input type="number" id="calcPoints" class="form-control form-control-xs text-center" placeholder="Live (+/-)">
                </div>
            </div>
            <button class="btn btn-success btn-xs w-100 fw-bold py-1" style="font-size: 0.75rem;" onclick="calculateOption()">Calculate P&amp;L</button>

            <div id="buyingPriceChapter" class="calc-chapter-box">
                <div class="calc-chapter-title">🟢 Invest Money</div>
                <div>Total Invested: <span id="chapterInvestedVal" class="fw-bold text-warning">--</span></div>
            </div>

            <div id="profitChapter" class="calc-chapter-box">
                <div class="calc-chapter-title">💰 Profit / Loss</div>
                <div class="text-center py-1">
                    <span id="chapterResultText" class="fw-bold" style="font-size: 1.25rem; display: block;">--</span>
                </div>
            </div>

        </div>
    </div>
</div>

<div class="main-content" id="mainContentContainer">
    <div class="container-fluid">

        <div class="top-nav">
            <button class="menu-btn mobile-only" onclick="toggleSidebar()">☰ &nbsp;Watchlist &amp; Option Calculator</button>
            <div class="d-flex gap-2 overflow-x-auto align-items-center broker-row">
                <a href="https://in.tradingview.com" target="_blank" class="broker-btn">TradingView</a>
                <a href="https://groww.in" target="_blank" class="broker-btn">Groww</a>
                <a href="https://kite.zerodha.com" target="_blank" class="broker-btn">Kite</a>
                <a href="https://www.angelone.in" target="_blank" class="broker-btn">Angel One</a>
                <a href="https://upstox.com" target="_blank" class="broker-btn">Upstox</a>
            </div>

            <div class="d-flex align-items-center gap-2 nav-right">
                <div class="live-widget-box" onclick="openGlobalModal()" title="Click to view Global Markets Time &amp; Currencies">
                    <span class="flag-wave">🇮🇳</span>
                    <span id="liveClockDisplay" class="fw-bold text-info">--:--:--</span>
                    <span class="text-muted">|</span>
                    <span id="liveDateDisplay" class="highlight-date">--/--/----</span>
                    <span class="text-muted">|</span>
                    <span id="usdInrDisplay" class="text-warning fw-bold">USD/INR: ₹--.--</span>
                </div>
                <div>
                    <button class="theme-toggle-btn" onclick="toggleTheme()">
                        <span id="themeIcon">🌙</span> <span id="themeText">Dark Mode</span>
                    </button>
                    <span id="globalRefreshTimer" class="global-timer-badge">60s</span>
                </div>
            </div>
        </div>

        <div class="modal fade" id="globalModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content p-3 shadow-lg">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold text-info mb-0">🌍 Global Financial Clocks &amp; Currencies</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div id="globalModalBody">
                        <div class="global-card">
                            <div class="d-flex align-items-center gap-2">
                                <span style="font-size: 1.3rem;">🇺🇸</span>
                                <div><b>United States (USD)</b><br><small class="text-muted" id="usDate">--</small></div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-info" id="usClock">--:--:--</span><br>
                                <span class="badge bg-secondary" id="usCurr">USD/USD: $1.00</span>
                            </div>
                        </div>
                        <div class="global-card">
                            <div class="d-flex align-items-center gap-2">
                                <span style="font-size: 1.3rem;">🇨🇳</span>
                                <div><b>China (CNY)</b><br><small class="text-muted" id="cnDate">--</small></div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-info" id="cnClock">--:--:--</span><br>
                                <span class="badge bg-warning text-dark" id="cnCurr">USD/CNY: ¥--.--</span>
                            </div>
                        </div>
                        <div class="global-card">
                            <div class="d-flex align-items-center gap-2">
                                <span style="font-size: 1.3rem;">🇷🇺</span>
                                <div><b>Russia (RUB)</b><br><small class="text-muted" id="ruDate">--</small></div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-info" id="ruClock">--:--:--</span><br>
                                <span class="badge bg-danger" id="ruCurr">USD/RUB: ₽--.--</span>
                            </div>
                        </div>
                        <div class="global-card">
                            <div class="d-flex align-items-center gap-2">
                                <span style="font-size: 1.3rem;">🇨🇦</span>
                                <div><b>Canada (CAD)</b><br><small class="text-muted" id="caDate">--</small></div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-info" id="caClock">--:--:--</span><br>
                                <span class="badge bg-success" id="caCurr">USD/CAD: $--.--</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="text-center mb-2">
            <h2 class="fw-bold text-info">ULTIMATE PRO TRADING SCANNER</h2>
            <p class="text-muted small">Advanced Live Market Multi-Indicator Analytics &amp; Breakout Dashboard</p>
        </div>

        <div class="ticker-wrapper-outer">
            <div class="ticker-rope"></div>
            <div class="ticker-wrapper-inner" id="tickerStrip">
                <div class="ticker-item"><span class="ticker-ribbon ribbon-flat">Loading live movers...</span></div>
            </div>
        </div>

        <div class="card p-3 shadow-sm mb-4">
            <div class="row g-3 align-items-center">
                <div class="col-md-5">
                    <label class="form-label fw-bold text-muted">Stock Symbol:</label>
                    <input type="text" id="stockSymbol" class="form-control" placeholder="e.g. RELIANCE">
                </div>
                <div class="col-md-5">
                    <label class="form-label fw-bold text-muted">Timeframe:</label>
                    <select id="timeframeSelect" class="form-select">
                        <option value="1d">Daily (1D)</option>
                        <option value="1h">Hourly (1H)</option>
                        <option value="15m" selected>15 Minutes (15M)</option>
                        <option value="5m">5 Minutes (5M)</option>
                    </select>
                </div>
                <div class="col-md-2 d-flex align-items-end">
                    <button class="btn btn-primary w-100 mt-2 fw-bold" onclick="scanStock()">Scan Stock</button>
                </div>
            </div>
        </div>

        <div class="row" id="resultCard" style="display:none;">
            <div class="col-md-7">
                <div class="card p-4 shadow mb-4">
                    <h4 id="stockName" class="text-center text-info"></h4>
                    <hr style="border-color: var(--border-color);">
                    <div class="row text-center mb-3">
                        <div class="col-md-3">
                            <p class="text-muted mb-1">Current Price</p>
                            <h4 id="stockPrice" class="text-success fw-bold">0</h4>
                        </div>
                        <div class="col-md-3">
                            <p class="text-muted mb-1">20 / 50 EMA</p>
                            <h6 id="emaValues" class="text-primary fw-bold">-</h6>
                        </div>
                        <div class="col-md-3">
                            <p class="text-muted mb-1">Swing High / Low</p>
                            <h6 id="swingLevels" class="text-warning fw-bold">-</h6>
                        </div>
                        <div class="col-md-3">
                            <p class="text-muted mb-1">Volume Status</p>
                            <h4 id="volumeStatus" class="text-info">-</h4>
                        </div>
                    </div>
                    <div class="alert text-center mt-3 p-3 border-secondary" id="dowSignalBox" role="alert"></div>
                    <div class="alert text-center mt-2 p-3 border-secondary" id="emaSignalBox" role="alert"></div>
                </div>
            </div>

            <div class="col-md-5">
                <div class="card p-3 shadow mb-4" style="height: 380px;">
                    <div class="board-header text-info px-1 pt-1 mb-1" style="font-size: 0.95rem;">
                        <span>📊 Stock Strength Gauge Meter</span>
                    </div>
                    <div class="gauge-container">
                        <div class="meter-arc">
                            <div class="meter-needle" id="gaugeNeedle"></div>
                            <div class="meter-pin"></div>
                        </div>
                        <h4 id="gaugeTitle" class="fw-bold mt-2 mb-1 text-success">--</h4>
                        <p id="gaugeDesc" class="text-muted small mb-0">Select a stock to evaluate trend strength.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <h5 class="fw-bold text-info mb-0 table-heading" style="cursor: pointer; display: flex; align-items: center; gap: 8px;" onclick="toggleTable('niftyTableWrapper', 'niftyToggleIcon')">
                            <span id="niftyToggleIcon">▼</span> <span>📈 Nifty 50 Stocks Live Market</span>
                            <span id="niftyStatsBadge" class="fs-6 fw-normal text-warning ms-1 stats-badge"></span>
                        </h5>
                        <span class="fs-7 text-muted table-subtitle">Master Unified Dashboard Table (All 50 Companies)</span>
                    </div>

                    <div class="master-table-wrapper" id="niftyTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th" style="vertical-align: middle;">Stock</th>
                                    <th>🔥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📈 DOW Breakouts (15M)</th>
                                    <th>⚔️ EMA Crossover (5M)</th>
                                    <th>📊 Bollinger Band (15M)</th>
                                    <th>📉 RSI Value (15M)</th>
                                    <th>📉 RSI Status (15M)</th>
                                    <th>🎯 DMI Crossover</th>
                                    <th>🎯 ADX Value (15M)</th>
                                    <th>🎯 ADX Trend (15M)</th>
                                    <th style="vertical-align: middle;">📊 Select Chart</th>
                                </tr>
                            </thead>
                            <tbody id="niftyTableBody">
                                <tr><td colspan="12" class="text-center text-muted loading-cell">Scanning Nifty 50 Live Market Data <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <h5 class="fw-bold text-info mb-0 table-heading" style="cursor: pointer; display: flex; align-items: center; gap: 8px;" onclick="toggleTable('bankNiftyTableWrapper', 'bankNiftyToggleIcon')">
                            <span id="bankNiftyToggleIcon">▼</span> <span>🏦 Bank Nifty Stocks Live Market</span>
                            <span id="bankNiftyStatsBadge" class="fs-6 fw-normal text-warning ms-1 stats-badge"></span>
                        </h5>
                        <span class="fs-7 text-muted table-subtitle">Banking Sector Dashboard Table</span>
                    </div>

                    <div class="master-table-wrapper" id="bankNiftyTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th" style="vertical-align: middle;">Stock</th>
                                    <th>🔥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📈 DOW Breakouts (15M)</th>
                                    <th>⚔️ EMA Crossover (5M)</th>
                                    <th>📊 Bollinger Band (15M)</th>
                                    <th>📉 RSI Value (15M)</th>
                                    <th>📉 RSI Status (15M)</th>
                                    <th>🎯 DMI Crossover</th>
                                    <th>🎯 ADX Value (15M)</th>
                                    <th>🎯 ADX Trend (15M)</th>
                                    <th style="vertical-align: middle;">📊 Select Chart</th>
                                </tr>
                            </thead>
                            <tbody id="bankNiftyTableBody">
                                <tr><td colspan="12" class="text-center text-muted loading-cell">Scanning Bank Nifty Live Market Data <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <h5 class="fw-bold text-info mb-0 table-heading" style="cursor: pointer; display: flex; align-items: center; gap: 8px;" onclick="toggleTable('commoditiesTableWrapper', 'commoditiesToggleIcon')">
                            <span id="commoditiesToggleIcon">▼</span> <span>🛢️ Commodities Live Market</span>
                            <span id="commoditiesStatsBadge" class="fs-6 fw-normal text-warning ms-1 stats-badge"></span>
                        </h5>
                        <span class="fs-7 text-muted table-subtitle">MCX Commodities Sector Dashboard Table</span>
                    </div>

                    <div class="master-table-wrapper" id="commoditiesTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th" style="vertical-align: middle;">Commodity</th>
                                    <th>🔥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📈 DOW Breakouts (15M)</th>
                                    <th>⚔️ EMA Crossover (5M)</th>
                                    <th>📊 Bollinger Band (15M)</th>
                                    <th>📉 RSI Value (15M)</th>
                                    <th>📉 RSI Status (15M)</th>
                                    <th>🎯 DMI Crossover</th>
                                    <th>🎯 ADX Value (15M)</th>
                                    <th>🎯 ADX Trend (15M)</th>
                                    <th style="vertical-align: middle;">📊 Select Chart</th>
                                </tr>
                            </thead>
                            <tbody id="commoditiesTableBody">
                                <tr><td colspan="12" class="text-center text-muted loading-cell">Scanning MCX Commodities Live Data <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <h5 class="fw-bold text-info mb-0 table-heading" style="cursor: pointer; display: flex; align-items: center; gap: 8px;" onclick="toggleTable('giftNiftyTableWrapper', 'giftNiftyToggleIcon')">
                            <span id="giftNiftyToggleIcon">▼</span> <span>🌍 Gift Nifty &amp; Key Sectors</span>
                            <span id="giftNiftyStatsBadge" class="fs-6 fw-normal text-warning ms-1 stats-badge"></span>
                        </h5>
                        <span class="fs-7 text-muted table-subtitle">Gift Nifty Dashboard Table</span>
                    </div>

                    <div class="master-table-wrapper" id="giftNiftyTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th" style="vertical-align: middle;">Index / Sector</th>
                                    <th>🔥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📈 DOW Breakouts (15M)</th>
                                    <th>⚔️ EMA Crossover (5M)</th>
                                    <th>📊 Bollinger Band (15M)</th>
                                    <th>📉 RSI Value (15M)</th>
                                    <th>📉 RSI Status (15M)</th>
                                    <th>🎯 DMI Crossover</th>
                                    <th>🎯 ADX Value (15M)</th>
                                    <th>🎯 ADX Trend (15M)</th>
                                    <th style="vertical-align: middle;">📊 Select Chart</th>
                                </tr>
                            </thead>
                            <tbody id="giftNiftyTableBody">
                                <tr><td colspan="12" class="text-center text-muted loading-cell">Scanning Gift Nifty Live Market Data <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <h5 class="fw-bold text-info mb-0 table-heading" style="cursor: pointer; display: flex; align-items: center; gap: 8px;" onclick="toggleTable('finNiftyTableWrapper', 'finNiftyToggleIcon')">
                            <span id="finNiftyToggleIcon">▼</span> <span>💳 Fin Nifty Stocks Live Market</span>
                            <span id="finNiftyStatsBadge" class="fs-6 fw-normal text-warning ms-1 stats-badge"></span>
                        </h5>
                        <span class="fs-7 text-muted table-subtitle">Financial Sector Dashboard Table</span>
                    </div>

                    <div class="master-table-wrapper" id="finNiftyTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th" style="vertical-align: middle;">Stock</th>
                                    <th>🔥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📈 DOW Breakouts (15M)</th>
                                    <th>⚔️ EMA Crossover (5M)</th>
                                    <th>📊 Bollinger Band (15M)</th>
                                    <th>📉 RSI Value (15M)</th>
                                    <th>📉 RSI Status (15M)</th>
                                    <th>🎯 DMI Crossover</th>
                                    <th>🎯 ADX Value (15M)</th>
                                    <th>🎯 ADX Trend (15M)</th>
                                    <th style="vertical-align: middle;">📊 Select Chart</th>
                                </tr>
                            </thead>
                            <tbody id="finNiftyTableBody">
                                <tr><td colspan="12" class="text-center text-muted loading-cell">Scanning Fin Nifty Live Market Data <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>

<button class="gemini-chat-btn" onclick="toggleGeminiChat()" title="Gemini AI Assistant">✨</button>
<div class="gemini-chat-window" id="geminiChatWindow">
    <div class="chat-header">
        <span>✨ Gemini AI Assistant</span>
        <button class="btn btn-sm btn-close btn-close-white" onclick="toggleGeminiChat()"></button>
    </div>
    <div class="chat-body" id="chatBody">
        <div class="chat-msg msg-gemini">Namaskar! Mi tumcha Gemini AI assistant ahe. Tumhi mala konthayhi prakaracha prashan vicharu shakta!</div>
    </div>
    <div class="chat-footer">
        <input type="text" id="chatInput" class="form-control form-control-sm" placeholder="Ask Gemini..." onkeypress="handleChatKey(event)">
        <button class="btn btn-primary btn-sm" onclick="sendChatMessage()">Send</button>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let watchlist = JSON.parse(localStorage.getItem('user_watchlist')) || [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "JSWSTEEL",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "BAJFINANCE", "HCLTECH",
    "ADANIENT", "TATASTEEL", "POWERGRID", "NTPC", "GRASIM", "BAJAJFINSV", "WIPRO", "INDUSINDBK", "ONGC", "COALINDIA",
    "BPCL", "HEROMOTOCO", "EICHERMOT", "DIVISLAB", "BRITANNIA", "TECHM", "NESTLEIND", "CIPLA", "APOLLOHOSP", "TATACONSUM",
    "SBILIFE", "HDFCLIFE", "BAJAJ-AUTO", "HINDALCO", "ULTRACEMCO", "DRREDDY", "ADANIPORTS", "SHRIRAMFIN", "TRENT", "M&M"
];

const stockLotSizes = {
    "NIFTY": 25, "BANKNIFTY": 15, "FINNIFTY": 25, "RELIANCE": 250, "TCS": 175, "HDFCBANK": 550,
    "ICICIBANK": 700, "SBIN": 750, "INFY": 400, "AXISBANK": 625, "KOTAKBANK": 400, "ITC": 1600,
    "BHARTIARTL": 475, "LT": 150, "BAJFINANCE": 125, "MARUTI": 50, "SUNPHARMA": 350, "TITAN": 175,
    "TATASTEEL": 5500, "WIPRO": 1500, "ONGC": 2875, "NTPC": 1500, "POWERGRID": 2400, "COALINDIA": 2100,
    "ASIANPAINT": 300, "HCLTECH": 350, "ADANIENT": 300, "ADANIPORTS": 400, "BAJAJFINSV": 500,
    "BAJAJ-AUTO": 75, "CIPLA": 350, "DRREDDY": 125, "GRASIM": 250, "HINDALCO": 1075, "HINDUNILVR": 300,
    "INDUSINDBK": 500, "M&M": 350, "NESTLEIND": 200, "TECHM": 600, "ULTRACEMCO": 100, "BRITANNIA": 200,
    "EICHERMOT": 175, "HEROMOTOCO": 150, "SHRIRAMFIN": 300, "TRENT": 150, "APOLLOHOSP": 125,
    "HDFCLIFE": 1100, "SBILIFE": 750, "TATACONSUM": 600, "JSWSTEEL": 675
};

const TABLE_TARGETS = [
    { type: 'nifty50',     body: 'niftyTableBody',      badge: 'niftyStatsBadge',      label: 'Nifty 50' },
    { type: 'banknifty',   body: 'bankNiftyTableBody',  badge: 'bankNiftyStatsBadge',  label: 'Bank Nifty' },
    { type: 'commodities', body: 'commoditiesTableBody',badge: 'commoditiesStatsBadge',label: 'Commodities' },
    { type: 'giftnifty',   body: 'giftNiftyTableBody',  badge: 'giftNiftyStatsBadge',  label: 'Gift Nifty' },
    { type: 'finnifty',    body: 'finNiftyTableBody',   badge: 'finNiftyStatsBadge',   label: 'Fin Nifty' }
];

let countdownTimer = 60;
let warmupRetry = null;

window.addEventListener('DOMContentLoaded', () => {
    let savedTheme = localStorage.getItem('app_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);

    renderWatchlist();
    fetchAllTables();
    fetchCurrencies();

    // Five card-stacked tables make for an endless page on a phone, so only the
    // headline Nifty 50 table stays open; the rest are one tap away.
    if (isMobile()) {
        [['bankNiftyTableWrapper','bankNiftyToggleIcon'],
         ['commoditiesTableWrapper','commoditiesToggleIcon'],
         ['giftNiftyTableWrapper','giftNiftyToggleIcon'],
         ['finNiftyTableWrapper','finNiftyToggleIcon']].forEach(p => toggleTable(p[0], p[1]));
    }

    setInterval(() => {
        let now = new Date();

        let optTime = { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
        let optDate = { timeZone: 'Asia/Kolkata', weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        document.getElementById('liveClockDisplay').innerText = now.toLocaleTimeString('en-US', optTime);
        document.getElementById('liveDateDisplay').innerText = now.toLocaleDateString('en-GB', optDate);

        document.getElementById('usClock').innerText = now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        document.getElementById('usDate').innerText = now.toLocaleDateString('en-GB', { timeZone: 'America/New_York', weekday: 'short', month: 'short', day: 'numeric' });

        document.getElementById('cnClock').innerText = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Shanghai', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        document.getElementById('cnDate').innerText = now.toLocaleDateString('en-GB', { timeZone: 'Asia/Shanghai', weekday: 'short', month: 'short', day: 'numeric' });

        document.getElementById('ruClock').innerText = now.toLocaleTimeString('en-US', { timeZone: 'Europe/Moscow', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        document.getElementById('ruDate').innerText = now.toLocaleDateString('en-GB', { timeZone: 'Europe/Moscow', weekday: 'short', month: 'short', day: 'numeric' });

        document.getElementById('caClock').innerText = now.toLocaleTimeString('en-US', { timeZone: 'America/Toronto', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        document.getElementById('caDate').innerText = now.toLocaleDateString('en-GB', { timeZone: 'America/Toronto', weekday: 'short', month: 'short', day: 'numeric' });

        countdownTimer--;
        if (countdownTimer <= 0) {
            countdownTimer = 60;
            fetchAllTables();
            fetchCurrencies();
        }
        let timerBadge = document.getElementById('globalRefreshTimer');
        if(timerBadge) timerBadge.innerText = `${countdownTimer}s`;

    }, 1000);
});

function openGlobalModal() {
    let myModal = new bootstrap.Modal(document.getElementById('globalModal'));
    myModal.show();
}

async function fetchCurrencies() {
    try {
        let res = await fetch('/get_currency_rate');
        let data = await res.json();
        if(data.inr) document.getElementById('usdInrDisplay').innerText = `USD/INR: ₹${data.inr}`;
        if(data.cny) document.getElementById('cnCurr').innerText = `USD/CNY: ¥${data.cny}`;
        if(data.rub) document.getElementById('ruCurr').innerText = `USD/RUB: ₽${data.rub}`;
        if(data.cad) document.getElementById('caCurr').innerText = `USD/CAD: $${data.cad}`;
    } catch(e) {}
}

function toggleTable(wrapperId, iconId) {
    let wrapper = document.getElementById(wrapperId);
    let icon = document.getElementById(iconId);
    if (wrapper.style.display === "none") {
        wrapper.style.display = "block";
        icon.innerText = "▼";
    } else {
        wrapper.style.display = "none";
        icon.innerText = "▶";
    }
}

function toggleTheme() {
    let currentTheme = document.documentElement.getAttribute('data-theme');
    let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('app_theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    let icon = document.getElementById('themeIcon');
    let text = document.getElementById('themeText');
    if(theme === 'dark') {
        icon.innerText = '🌙';
        text.innerText = 'Dark Mode';
    } else {
        icon.innerText = '☀️';
        text.innerText = 'Light Mode';
    }
}

function tvSymbolFor(symbol) {
    if(symbol === "GOLD") return "MCX:GOLD1!";
    if(symbol === "GOLDM") return "MCX:GOLDM1!";
    if(symbol === "SILVER") return "MCX:SILVER1!";
    if(symbol === "SILVERM") return "MCX:SILVERM1!";
    if(symbol === "CRUDEOIL") return "MCX:CRUDEOIL1!";
    if(symbol === "CRUDEOILM") return "MCX:CRUDEOILM1!";
    if(symbol === "NATURALGAS") return "MCX:NATURALGAS1!";
    if(symbol === "COPPER") return "MCX:COPPER1!";
    if(symbol === "NIFTY") return "NSE:NIFTY";
    if(symbol === "BANKNIFTY") return "NSE:BANKNIFTY";
    if(symbol === "USDINR") return "FX_IDC:USDINR";
    return `NSE:${symbol}`;
}

function openChart(selectElement, symbol) {
    let val = selectElement.value;
    if(!val) return;
    let url = "";
    if(val === "tradingview") {
        url = `https://in.tradingview.com/chart/?symbol=${tvSymbolFor(symbol)}`;
    } else if(val === "groww") {
        url = `https://groww.in/stocks/nse-${symbol.toLowerCase()}`;
    }
    if(url) window.open(url, '_blank');
    selectElement.value = "";
}

function openIndicatorChart(symbol) {
    scanStock(symbol);
    window.open(`https://in.tradingview.com/chart/?symbol=${tvSymbolFor(symbol)}`, '_blank');
}

function toggleGeminiChat() {
    let win = document.getElementById('geminiChatWindow');
    win.style.display = (win.style.display === "flex") ? "none" : "flex";
}

function handleChatKey(e) {
    if(e.key === 'Enter') sendChatMessage();
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function sendChatMessage() {
    let input = document.getElementById('chatInput');
    let text = input.value.trim();
    if(!text) return;

    let body = document.getElementById('chatBody');
    body.innerHTML += `<div class="chat-msg msg-user">${escapeHtml(text)}</div>`;
    input.value = "";
    body.scrollTop = body.scrollHeight;

    try {
        let res = await fetch(`/gemini_chat?message=${encodeURIComponent(text)}`);
        let data = await res.json();
        body.innerHTML += `<div class="chat-msg msg-gemini">${escapeHtml(data.reply)}</div>`;
        body.scrollTop = body.scrollHeight;
    } catch(err) {
        body.innerHTML += `<div class="chat-msg msg-gemini text-danger">Error connecting to assistant.</div>`;
    }
}

function loadingRow(label) {
    return `<tr><td colspan="12" class="text-center text-muted loading-cell">${label} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>`;
}

async function fetchAllTables() {
    let warming = false;

    for (const t of TABLE_TARGETS) {
        try {
            let res = await fetch(`/get_master_table_data?type=${t.type}`);
            let data = await res.json();
            let body = document.getElementById(t.body);
            let badge = document.getElementById(t.badge);

            if (data.rows && data.rows.length > 0) {
                body.innerHTML = data.rows.join("");
                if (data.stats) {
                    badge.innerHTML = `(1H: 🟢 Up: ${data.stats.up_count} (${data.stats.up_pct}%) | 🔴 Down: ${data.stats.down_count} (${data.stats.down_pct}%))`;
                }
            } else if (data.status === 'warming') {
                warming = true;
                body.innerHTML = loadingRow(data.message || `Fetching ${t.label} live data`);
            } else {
                body.innerHTML = `<tr><td colspan="12" class="text-center text-muted loading-cell">${data.message || 'No active data found.'}</td></tr>`;
            }
        } catch(e) {}
    }

    if (TABLE_TARGETS.length) {
        try {
            let res = await fetch('/get_movers');
            let data = await res.json();
            if (data.movers && data.movers.length) renderTicker(data.movers);
        } catch(e) {}
    }

    // The first request after a cold start lands while the background refresh is still
    // running; poll quickly until it finishes instead of waiting a full minute.
    if (warmupRetry) clearTimeout(warmupRetry);
    if (warming) warmupRetry = setTimeout(fetchAllTables, 5000);

    countdownTimer = 60;
    renderWatchlist();
}

function renderTicker(movers) {
    let strip = document.getElementById('tickerStrip');
    strip.innerHTML = movers.map(mv => {
        if (mv.pct >= 0) {
            return `<div class="ticker-item" onclick="scanStock('${mv.symbol}')" title="Click to scan ${mv.symbol}">
                <span class="ticker-rocket rocket-bull">🚀</span>
                <span class="ticker-ribbon ribbon-bull">${mv.symbol} : +${mv.pct}% ▲</span></div>`;
        }
        return `<div class="ticker-item" onclick="scanStock('${mv.symbol}')" title="Click to scan ${mv.symbol}">
            <span class="ticker-ribbon ribbon-bear">${mv.symbol} : ${mv.pct}% ▼</span>
            <span class="ticker-rocket rocket-bear">🔻</span></div>`;
    }).join("");
}

function updateGauge(trend, score) {
    let needle = document.getElementById('gaugeNeedle');
    let title = document.getElementById('gaugeTitle');
    let desc = document.getElementById('gaugeDesc');

    let angle = (score / 100) * 90;
    needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;

    title.innerText = trend;
    if(score > 30) {
        title.className = "fw-bold mt-2 mb-1 text-success";
        desc.innerText = "Strong Bullish trend with robust momentum.";
    } else if(score > 0) {
        title.className = "fw-bold mt-2 mb-1 text-success";
        desc.innerText = "Mild Bullish trend with a normal relative strength.";
    } else if(score < -30) {
        title.className = "fw-bold mt-2 mb-1 text-danger";
        desc.innerText = "Strong Bearish trend with downward pressure.";
    } else if(score < 0) {
        title.className = "fw-bold mt-2 mb-1 text-danger";
        desc.innerText = "Mild Bearish trend with selling pressure.";
    } else {
        title.className = "fw-bold mt-2 mb-1 text-warning";
        desc.innerText = "Sideways or Neutral market momentum.";
    }
}

function isMobile() {
    return window.matchMedia('(max-width: 900px)').matches;
}

function closeMobileSidebar() {
    document.getElementById('sidebarContainer').classList.remove('mobile-open');
    document.getElementById('sidebarBackdrop').classList.remove('show');
}

function toggleSidebar() {
    let sidebar = document.getElementById('sidebarContainer');

    // On a phone the sidebar is an off-canvas drawer, not a shrinkable column.
    if (isMobile()) {
        let open = sidebar.classList.toggle('mobile-open');
        document.getElementById('sidebarBackdrop').classList.toggle('show', open);
        return;
    }

    let mainContent = document.getElementById('mainContentContainer');
    let toggleBtn = document.querySelector('.sidebar-toggle-btn');

    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');

    toggleBtn.innerHTML = sidebar.classList.contains('collapsed') ? '&raquo;' : '&laquo;';
}

window.addEventListener('resize', () => { if (!isMobile()) closeMobileSidebar(); });

function toggleOptionCalculator() {
    let body = document.getElementById('optionCalcBody');
    body.style.display = (body.style.display === "none" || body.style.display === "") ? "block" : "none";
}

async function loadOptionChainForStock(stockSymbol) {
    document.getElementById('activeStockLabel').innerText = `Active: ${stockSymbol}`;

    let lotSize = stockLotSizes[stockSymbol] || 25;
    document.getElementById('calcLot').value = lotSize;

    let container = document.getElementById('chainTableContainer');
    container.style.display = "block";
    container.innerHTML = `<div class='text-center fs-7 text-muted p-1'>Fetching Strikes...</div>`;

    try {
        let response = await fetch(`/get_strike_chain?symbol=${encodeURIComponent(stockSymbol)}`);
        let data = await response.json();

        if(data.error) {
            container.innerHTML = `<div class='text-center text-danger fs-7 p-1'>${data.error}</div>`;
            return;
        }

        let html = `<table class="chain-table">
            <tr><th>CE (₹)</th><th>Strike (Spot: ₹${data.current_price})</th><th>PE (₹)</th></tr>`;

        data.chain.forEach(row => {
            let isAtm = row.is_atm ? "atm-row" : "";
            let atmMark = row.is_atm ? " 🎯" : "";
            html += `<tr class="chain-row ${isAtm}">
                <td><span class="call-btn" onclick="selectOption('${stockSymbol}', ${row.strike}, 'CE', ${row.ce_price})">${row.ce_price}</span></td>
                <td><b>${row.strike}${atmMark}</b></td>
                <td><span class="put-btn" onclick="selectOption('${stockSymbol}', ${row.strike}, 'PE', ${row.pe_price})">${row.pe_price}</span></td>
            </tr>`;
        });
        html += `</table>`;
        container.innerHTML = html;
    } catch(e) {
        container.innerHTML = `<div class='text-center text-danger fs-7 p-1'>Could not load strikes.</div>`;
    }
}

function selectOption(symbol, strike, type, price) {
    document.getElementById('selectedOptionName').value = `${symbol} ${strike} ${type}`;
    document.getElementById('calcEntry').value = price;
}

function calculateOption() {
    let type = document.getElementById('calcType').value;
    let entry = parseFloat(document.getElementById('calcEntry').value);
    let lot = parseInt(document.getElementById('calcLot').value);
    let points = parseFloat(document.getElementById('calcPoints').value);

    if(isNaN(entry) || isNaN(lot) || isNaN(points)) {
        alert("Please select a strike and fill live points!");
        return;
    }

    let totalInvested = entry * lot;
    let netProfit = (type === "BUY") ? (points * lot) : ((entry - (entry + points)) * lot);
    let colorClass = netProfit >= 0 ? "text-success" : "text-danger";
    let signPrefix = netProfit >= 0 ? "+₹ " : "-₹ ";

    document.getElementById('buyingPriceChapter').style.display = "block";
    document.getElementById('chapterInvestedVal').innerText = `₹ ${totalInvested.toFixed(2)} (Entry ₹${entry} × Lot ${lot})`;

    document.getElementById('profitChapter').style.display = "block";
    document.getElementById('chapterResultText').className = `fw-bold ${colorClass}`;
    document.getElementById('chapterResultText').innerText = `${signPrefix}${Math.abs(netProfit).toFixed(2)}`;
}

async function renderWatchlist() {
    let container = document.getElementById('watchlistContainer');
    let statuses = {};
    try {
        let res = await fetch(`/get_status_bulk?symbols=${encodeURIComponent(watchlist.join(','))}`);
        statuses = await res.json();
    } catch(e) {}

    container.innerHTML = "";
    for(let stock of watchlist) {
        let s = statuses[stock] || { trend: 'Sideways', daily_change: 0, hourly_trend: '--' };
        let trendHtml = s.trend === 'Bullish' ? `<span class="bull">▲ Bull</span>`
                      : s.trend === 'Bearish' ? `<span class="bear">▼ Bear</span>`
                      : `<span class="flat">▶ Flat</span>`;
        let dailyClass = s.daily_change >= 0 ? "text-success" : "text-danger";
        let dailySign = s.daily_change >= 0 ? "+" : "";

        let div = document.createElement('div');
        div.className = "watchlist-item";
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b>${stock}</b>
                ${trendHtml}
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8;">
                <span class="${dailyClass}">Daily: ${dailySign}${s.daily_change}%</span>
                <span class="text-info">1H: ${s.hourly_trend}</span>
            </div>
        `;
        div.onclick = () => {
            document.getElementById('stockSymbol').value = stock;
            scanStock(stock);
            loadOptionChainForStock(stock);
        };
        container.appendChild(div);
    }
}

function addToWatchlist() {
    let val = document.getElementById('newStockInput').value.trim().toUpperCase();
    if(val && !watchlist.includes(val)) {
        watchlist.push(val);
        localStorage.setItem('user_watchlist', JSON.stringify(watchlist));
        document.getElementById('newStockInput').value = "";
        renderWatchlist();
    }
}

async function scanStock(presetSymbol = null) {
    let inputVal = presetSymbol ? presetSymbol : document.getElementById('stockSymbol').value.trim().toUpperCase();
    if(!inputVal) { alert("Please enter or select a stock symbol"); return; }

    document.getElementById('stockSymbol').value = inputVal;
    let timeframe = document.getElementById('timeframeSelect').value;

    if (isMobile()) {
        closeMobileSidebar();
    } else {
        let sidebar = document.getElementById('sidebarContainer');
        if(!sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            document.getElementById('mainContentContainer').classList.add('expanded');
            document.querySelector('.sidebar-toggle-btn').innerHTML = '&raquo;';
        }
    }

    try {
        let response = await fetch(`/get_signals?symbol=${encodeURIComponent(inputVal)}&interval=${timeframe}`);
        let data = await response.json();

        if(data.error) { alert("Error: " + data.error); return; }

        document.getElementById('stockName').innerText = `${data.name} (${inputVal}) - Timeframe: ${timeframe.toUpperCase()}`;
        document.getElementById('stockPrice').innerText = "₹ " + data.price;
        document.getElementById('emaValues').innerHTML = `20 EMA: ₹${data.ema_20}<br>50 EMA: ₹${data.ema_50}`;
        document.getElementById('swingLevels').innerHTML = `SH: ₹${data.swing_high}<br>SL: ₹${data.swing_low}`;
        document.getElementById('volumeStatus').innerText = data.volume_status;

        let dowBox = document.getElementById('dowSignalBox');
        if(data.dow_signal === "BUY") {
            dowBox.innerHTML = `<span class="badge-buy">DOW BUY BREAKOUT</span><br><br><b>Time: ${data.dow_time}</b><br>${data.dow_message}`;
        } else if(data.dow_signal === "SELL") {
            dowBox.innerHTML = `<span class="badge-sell">DOW SELL BREAKDOWN</span><br><br><b>Time: ${data.dow_time}</b><br>${data.dow_message}`;
        } else {
            dowBox.innerHTML = `<span class="text-warning"><b>Dow Status: Wait / No Breakout</b></span><br><br>${data.dow_message}`;
        }

        let emaBox = document.getElementById('emaSignalBox');
        if(data.ema_signal === "BUY") {
            emaBox.innerHTML = `<span class="badge-buy">UP SIDE BREAKOUT / GOLDEN CROSSOVER</span><br>Last Crossover Date (${timeframe.toUpperCase()}): <b>${data.last_cross_date}</b>`;
        } else if(data.ema_signal === "SELL") {
            emaBox.innerHTML = `<span class="badge-sell">DOWN SIDE BREAKDOWN / DEATH CROSSOVER</span><br>Last Crossover Date (${timeframe.toUpperCase()}): <b>${data.last_cross_date}</b>`;
        } else {
            emaBox.innerHTML = `<span class="text-muted">Last Crossover Date (${timeframe.toUpperCase()}): <b>${data.last_cross_date}</b></span>`;
        }

        updateGauge(data.gauge_trend, data.gauge_score);
        document.getElementById('resultCard').style.display = "flex";
        loadOptionChainForStock(inputVal);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch(e) {
        alert("Could not scan " + inputVal + ". Please try again.");
    }
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/healthz")
def healthz():
    snap = SNAPSHOT
    return jsonify({
        "ok": True,
        "status": snap["status"],
        "symbols": len(snap["metrics"]),
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
        "rows": table["rows"],
        "stats": table["stats"],
        "status": snap["status"],
        "message": snap["message"],
        "updated_at": snap["updated_at"],
    })


@app.route("/get_movers")
def get_movers():
    """Top gainers and losers for the header ticker strip."""
    metrics = SNAPSHOT["metrics"]
    scored = []
    for sym in NIFTY50_STOCKS:
        m = metrics.get(sym)
        if not m or not m["prev_close"]:
            continue
        pct = round((m["curr_price"] - m["prev_close"]) / m["prev_close"] * 100, 2)
        scored.append({"symbol": sym, "pct": pct})

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
    symbols = [s.strip().upper() for s in raw.split(",") if s.strip()]
    metrics = SNAPSHOT["metrics"]

    out = {}
    for sym in symbols:
        m = metrics.get(sym)
        if not m or not m["prev_close"]:
            out[sym] = {"trend": "Sideways", "daily_change": 0.0, "hourly_trend": "--"}
            continue
        change = round((m["curr_price"] - m["prev_close"]) / m["prev_close"] * 100, 2)
        out[sym] = {
            "trend": "Bullish" if change > 0 else ("Bearish" if change < 0 else "Sideways"),
            "daily_change": change,
            "hourly_trend": m["hourly_trend"],
        }
    return jsonify(out)


@app.route("/get_status")
def get_status():
    sym = request.args.get("symbol", "").upper()
    m = SNAPSHOT["metrics"].get(sym)
    if not m or not m["prev_close"]:
        return jsonify({"trend": "Sideways", "daily_change": 0.0, "hourly_trend": "--"})
    change = round((m["curr_price"] - m["prev_close"]) / m["prev_close"] * 100, 2)
    return jsonify({
        "trend": "Bullish" if change > 0 else ("Bearish" if change < 0 else "Sideways"),
        "daily_change": change,
        "hourly_trend": m["hourly_trend"],
    })


@app.route("/get_strike_chain")
def get_strike_chain():
    query = request.args.get("symbol", "RELIANCE").upper()
    try:
        m = SNAPSHOT["metrics"].get(query)
        if m:
            current_price = m["curr_price"]
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
        chain_data = []

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

            chain_data.append({"strike": stk, "ce_price": ce_p, "pe_price": pe_p, "is_atm": is_atm})

        return jsonify({"chain": chain_data, "current_price": round(current_price, 2)})
    except Exception as exc:
        log.error("strike chain failed for %s: %s", query, exc)
        return jsonify({"error": "Could not generate strike chain."})


@app.route("/get_signals")
def get_signals():
    symbol = request.args.get("symbol", "RELIANCE")
    interval = request.args.get("interval", "15m")
    try:
        stock = yf.Ticker(get_ticker_symbol(symbol))

        period = {"5m": "5d", "15m": "1mo", "1h": "3mo", "1d": "1y"}.get(interval, "1mo")
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
        volume_status_text = f"{'High' if is_high_volume else 'Normal'} ({int(current_volume)})"

        try:
            short_name = stock.info.get("shortName", symbol) or symbol
        except Exception:
            short_name = symbol

        dow_signal, dow_time = "WAIT", "N/A"
        if current_high > swing_high and is_high_volume and current_price > ema_20:
            dow_signal = "BUY"
            dow_message = f"Valid Setup! Price broke Previous Swing High of <b>₹{swing_high}</b> with high volume & above 20 EMA."
            dow_time = format_ist_time(df.index[-1])
        elif current_low < swing_low and is_high_volume and current_price < ema_20:
            dow_signal = "SELL"
            dow_message = f"Valid Setup! Price broke Previous Swing Low of <b>₹{swing_low}</b> with high volume & below 20 EMA."
            dow_time = format_ist_time(df.index[-1])
        else:
            dow_message = f"No Dow breakout matching criteria. Previous Swing High: ₹{swing_high}, Previous Swing Low: ₹{swing_low}."

        ema_signal = "WAIT"
        if prev_ema_20 <= prev_ema_50 and ema_20 > ema_50: ema_signal = "BUY"
        elif prev_ema_20 >= prev_ema_50 and ema_20 < ema_50: ema_signal = "SELL"

        m = SNAPSHOT["metrics"].get(symbol.upper())
        if m and m["prev_close"]:
            pct_change = (m["curr_price"] - m["prev_close"]) / m["prev_close"] * 100
        else:
            pct_change = 0.0

        gauge_score = max(-100, min(100, int(pct_change * 30)))
        if gauge_score > 25: gauge_trend = "Bullish"
        elif gauge_score > 0: gauge_trend = "Mild Bullish"
        elif gauge_score < -25: gauge_trend = "Bearish"
        elif gauge_score < 0: gauge_trend = "Mild Bearish"
        else: gauge_trend = "Neutral"

        return jsonify({
            "name": short_name, "price": current_price, "ema_20": ema_20, "ema_50": ema_50,
            "swing_high": swing_high, "swing_low": swing_low, "volume_status": volume_status_text,
            "dow_signal": dow_signal, "dow_message": dow_message, "dow_time": dow_time,
            "ema_signal": ema_signal, "last_cross_date": last_cross_date,
            "gauge_trend": gauge_trend, "gauge_score": gauge_score,
        })
    except Exception as exc:
        log.error("get_signals failed for %s: %s: %s", symbol, type(exc).__name__, exc)
        return jsonify({"error": "Could not scan this symbol right now."})


@app.route("/gemini_chat")
def gemini_chat():
    msg = request.args.get("message", "")
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
