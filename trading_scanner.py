"""Ultimate Pro Trading Terminal - live NSE/MCX multi-indicator analytics.

Architecture: one background thread batch-downloads every timeframe for the whole
symbol universe, computes all indicators once, and publishes an immutable snapshot.
Every HTTP handler reads that snapshot, so page requests never touch Yahoo Finance
and cannot block or time out on it.
"""

import os
import re
import csv
import time
import logging
import threading
from io import StringIO
from datetime import datetime

from flask import Flask, jsonify, render_template, request, Response, abort
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scanner")

app = Flask(__name__)

APP_VERSION = "v4.0-terminal"
IST = pytz.timezone("Asia/Kolkata")
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "90"))

# Symbols only ever contain these characters (BAJAJ-AUTO, M&M, ^NSEI, INR=X).
SYMBOL_RE = re.compile(r"^[A-Z0-9&^.=\-]{1,20}$")
INTERVALS = ("5m", "15m", "1h", "1d")

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


# --------------------------------------------------------------------------- #
# Universe
# --------------------------------------------------------------------------- #

NIFTY50_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "JSWSTEEL",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "BAJFINANCE", "HCLTECH", "JIOFIN",
    "ADANIENT", "TATASTEEL", "POWERGRID", "NTPC", "GRASIM", "BAJAJFINSV", "WIPRO", "INDUSINDBK", "ONGC", "COALINDIA",
    "BPCL", "HEROMOTOCO", "EICHERMOT", "DIVISLAB", "BRITANNIA", "TECHM", "NESTLEIND", "CIPLA", "APOLLOHOSP", "TATACONSUM",
    "SBILIFE", "HDFCLIFE", "BAJAJ-AUTO", "HINDALCO", "ULTRACEMCO", "DRREDDY", "ADANIPORTS", "SHRIRAMFIN", "TRENT", "M&M",
]

BANKNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK",
    "BANKBARODA", "PNB", "IDFCFIRSTB", "AUBANK", "FEDERALBNK", "BANDHANBNK",
]

COMMODITIES_STOCKS = ["GOLD", "GOLDM", "SILVER", "SILVERM", "CRUDEOIL", "CRUDEOILM", "NATURALGAS", "COPPER"]

GIFTNIFTY_STOCKS = ["NIFTY", "BANKNIFTY", "USDINR"]

FINNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BAJFINANCE",
    "SHRIRAMFIN", "SBILIFE", "HDFCLIFE", "CHOLAFIN",
]

TABLES = {
    "nifty50": NIFTY50_STOCKS,
    "banknifty": BANKNIFTY_STOCKS,
    "finnifty": FINNIFTY_STOCKS,
    "commodities": COMMODITIES_STOCKS,
    "giftnifty": GIFTNIFTY_STOCKS,
}

TABLE_LABELS = {
    "nifty50": "Nifty 50",
    "banknifty": "Bank Nifty",
    "finnifty": "Fin Nifty",
    "commodities": "Commodities",
    "giftnifty": "Gift Nifty",
}

# Headline indices shown as cards. Kept separate from the scanned universe because
# they are quoted, not screened.
HEADLINE_INDICES = [
    ("NIFTY 50", "^NSEI"),
    ("BANK NIFTY", "^NSEBANK"),
    ("FIN NIFTY", "NIFTY_FIN_SERVICE.NS"),
    ("INDIA VIX", "^INDIAVIX"),
]

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
    "HDFCLIFE": 1100, "SBILIFE": 750, "TATACONSUM": 600, "JSWSTEEL": 675, "JIOFIN": 2350,
}

TICKER_OVERRIDES = {
    "NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "USDINR": "INR=X", "M&M": "M&M.NS",
    "GOLD": "GC=F", "GOLDM": "GC=F", "SILVER": "SI=F", "SILVERM": "SI=F",
    "CRUDEOIL": "CL=F", "CRUDEOILM": "CL=F", "NATURALGAS": "NG=F", "COPPER": "HG=F",
}


def get_ticker_symbol(query):
    query = query.upper()
    if query in TICKER_OVERRIDES:
        return TICKER_OVERRIDES[query]
    if query.endswith((".NS", "=F", "=X")) or query.startswith("^"):
        return query
    return query + ".NS"


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
        return "--"


UNIVERSE = []
for _syms in TABLES.values():
    for _s in _syms:
        if _s not in UNIVERSE:
            UNIVERSE.append(_s)

SYMBOL_TO_TICKER = {s: get_ticker_symbol(s) for s in UNIVERSE}
INDEX_TICKERS = {name: ticker for name, ticker in HEADLINE_INDICES}
UNIQUE_TICKERS = sorted(
    set(SYMBOL_TO_TICKER.values()) | set(FX_TICKERS.values()) | set(INDEX_TICKERS.values())
)

# One batched download per timeframe covers the entire universe.
FRAME_SPECS = {
    "1d": ("6mo", "1d"),
    "15m": ("5d", "15m"),
    "1h": ("1mo", "1h"),
    "5m": ("5d", "5m"),
}

# Startup sanity: a wrong count or a duplicate silently corrupts every page.
assert len(NIFTY50_STOCKS) == 50, f"Nifty 50 must hold 50 symbols, found {len(NIFTY50_STOCKS)}"
for _name, _lst in TABLES.items():
    assert len(_lst) == len(set(_lst)), f"duplicate symbol in {_name}"
    for _s in _lst:
        assert SYMBOL_RE.match(_s), f"invalid symbol {_s!r} in {_name}"


# --------------------------------------------------------------------------- #
# Market clock
# --------------------------------------------------------------------------- #

def market_status():
    """NSE cash session in IST. Yahoo data is delayed, so nothing here claims to
    be a real-time exchange feed."""
    now = datetime.now(IST)
    minutes = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        return {"state": "CLOSED", "label": "Market Closed", "detail": "Weekend", "open": False}
    if 540 <= minutes < 555:
        return {"state": "PRE", "label": "Pre-Market", "detail": "09:00 - 09:15 IST", "open": False}
    if 555 <= minutes < 930:
        return {"state": "OPEN", "label": "Market Open", "detail": "09:15 - 15:30 IST", "open": True}
    if 930 <= minutes < 960:
        return {"state": "POST", "label": "Post-Market", "detail": "15:30 - 16:00 IST", "open": False}
    return {"state": "CLOSED", "label": "Market Closed", "detail": "Opens 09:15 IST", "open": False}


# --------------------------------------------------------------------------- #
# Data engine
# --------------------------------------------------------------------------- #

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
            df = data[ticker] if multi else data
            if multi and ticker not in available:
                continue
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


def _num(value, digits=2):
    """Never let a NaN or an infinity escape into a page."""
    try:
        f = float(value)
        return round(f, digits) if np.isfinite(f) else None
    except (TypeError, ValueError):
        return None


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


def compute_detail(df):
    """Per-timeframe levels for the analysis page. Computed once during the refresh
    so /get_signals never has to call Yahoo."""
    if df is None or len(df) < 10:
        return None

    close = df["Close"]
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    # Vectorised crossover scan rather than a row-by-row loop over the history.
    above = ema20 > ema50
    crossings = df.index[above != above.shift(1)][1:]

    ema_signal = "WAIT"
    if len(ema20) > 1:
        prev_above = bool(above.iloc[-2])
        now_above = bool(above.iloc[-1])
        if now_above and not prev_above:
            ema_signal = "BUY"
        elif prev_above and not now_above:
            ema_signal = "SELL"

    swing_high = _num(df["High"].iloc[-6:-1].max()) if len(df) >= 6 else _num(close.iloc[-1])
    swing_low = _num(df["Low"].iloc[-6:-1].min()) if len(df) >= 6 else _num(close.iloc[-1])

    volume_status, high_volume = "--", False
    if "Volume" in df.columns:
        current_volume = _num(df["Volume"].iloc[-1], 0)
        avg_volume = _num(df["Volume"].rolling(window=10).mean().iloc[-1], 0) if len(df) >= 10 else None
        if current_volume and current_volume > 0:
            high_volume = bool(avg_volume and current_volume > 1.2 * avg_volume)
            volume_status = f"{'High' if high_volume else 'Normal'} ({int(current_volume):,})"

    price = _num(close.iloc[-1])
    e20 = _num(ema20.iloc[-1])
    dow_signal = "WAIT"
    if price is not None and e20 is not None and swing_high is not None and swing_low is not None:
        if _num(df["High"].iloc[-1]) > swing_high and high_volume and price > e20:
            dow_signal = "BUY"
        elif _num(df["Low"].iloc[-1]) < swing_low and high_volume and price < e20:
            dow_signal = "SELL"

    return {
        "price": price,
        "ema_20": e20,
        "ema_50": _num(ema50.iloc[-1]),
        "swing_high": swing_high,
        "swing_low": swing_low,
        "volume_status": volume_status,
        "last_cross": format_ist_time(crossings[-1]) if len(crossings) else "--",
        "ema_signal": ema_signal,
        "dow_signal": dow_signal,
        "bars": int(len(df)),
    }


def score_band(score):
    """Present the existing -7..+7 signal count as five readable bands."""
    if score >= 4: return {"key": "strong-bull", "label": "STRONG BULLISH"}
    if score >= 1: return {"key": "bull", "label": "BULLISH"}
    if score <= -4: return {"key": "strong-bear", "label": "STRONG BEARISH"}
    if score <= -1: return {"key": "bear", "label": "BEARISH"}
    return {"key": "neutral", "label": "NEUTRAL"}


def compute_metrics(sym, frames_by_interval, inr_rate):
    """Every indicator for one symbol, as plain values the pages can render or filter."""
    ticker = SYMBOL_TO_TICKER.get(sym) or get_ticker_symbol(sym)
    daily = frames_by_interval.get("1d", {}).get(ticker)
    if daily is None or daily.empty:
        return None

    price = _num(daily["Close"].iloc[-1])
    prev_close = _num(daily["Close"].iloc[-2]) if len(daily) >= 2 else price
    if price is None or prev_close is None or price <= 0:
        return None

    if sym in COMMODITIES_STOCKS:
        price = _num(_commodity_price(sym, price, inr_rate))
        prev_close = _num(_commodity_price(sym, prev_close, inr_rate))

    m = {
        "symbol": sym,
        "price": price,
        "prev_close": prev_close,
        "pct": _num((price - prev_close) / prev_close * 100) if prev_close else 0.0,
        "big_candle": None, "macd": None, "dow": None, "ema": None, "bb": None,
        "rsi": None, "rsi_trend": None, "dmi": None, "adx": None, "adx_trend": None,
        "bull_15m": False, "hourly_trend": "Sideways", "score": 0,
    }

    df15 = _pick(frames_by_interval, ticker, "15m")
    if df15 is not None and len(df15) >= 30:
        close, high, low, open_ = df15["Close"], df15["High"], df15["Low"], df15["Open"]
        cp = _num(close.iloc[-1])

        candle_range = _num(high.iloc[-1] - low.iloc[-1])
        avg_range = _num((high - low).rolling(window=10).mean().iloc[-1])
        if candle_range and avg_range and candle_range >= 1.5 * avg_range:
            m["big_candle"] = "bull" if cp > _num(open_.iloc[-1]) else "bear"
        else:
            m["big_candle"] = "normal"

        swing_high = _num(high.iloc[-7:-1].max())
        swing_low = _num(low.iloc[-7:-1].min())
        if cp is not None and swing_high is not None and swing_low is not None:
            m["dow"] = "buy" if cp > swing_high else ("sell" if cp < swing_low else "wait")

        bb_up = close.rolling(window=20).mean() + close.rolling(window=20).std() * 2
        upper = _num(bb_up.iloc[-1])
        if upper is not None and cp is not None:
            m["bb"] = "up" if cp >= upper * 0.995 else "down"

        rsi = _rsi(close)
        curr_rsi, prev_rsi = _num(rsi.iloc[-1], 1), (_num(rsi.iloc[-2], 1) if len(rsi) >= 2 else None)
        if curr_rsi is not None:
            m["rsi"] = curr_rsi
            if prev_rsi is not None:
                m["rsi_trend"] = "up" if curr_rsi > prev_rsi else ("down" if curr_rsi < prev_rsi else "flat")

        plus_di, minus_di, adx = _adx(df15)
        p_di, m_di = _num(plus_di.iloc[-1]), _num(minus_di.iloc[-1])
        if p_di is not None and m_di is not None:
            m["dmi"] = "bull" if p_di >= m_di else "bear"
        curr_adx = _num(adx.iloc[-1], 1)
        prev_adx = _num(adx.iloc[-2], 1) if len(adx) >= 2 else None
        if curr_adx is not None:
            m["adx"] = curr_adx
            if prev_adx is not None:
                m["adx_trend"] = "up" if curr_adx > prev_adx else ("down" if curr_adx < prev_adx else "flat")

        ema15 = _num(close.ewm(span=20, adjust=False).mean().iloc[-1])
        m["bull_15m"] = bool(cp is not None and ema15 is not None and cp >= ema15)

    df1h = _pick(frames_by_interval, ticker, "1h")
    if df1h is not None and len(df1h) >= 30:
        close = df1h["Close"]
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_v, sig_v = _num(macd.iloc[-1], 4), _num(signal.iloc[-1], 4)
        if macd_v is not None and sig_v is not None:
            m["macd"] = "bull" if macd_v >= sig_v else "bear"

        ema20 = _num(close.ewm(span=20, adjust=False).mean().iloc[-1])
        last = _num(close.iloc[-1])
        if ema20 and last:
            if last > ema20 * 1.001:
                m["hourly_trend"] = "Bull"
            elif last < ema20 * 0.999:
                m["hourly_trend"] = "Bear"

    df5m = _pick(frames_by_interval, ticker, "5m")
    if df5m is not None and len(df5m) >= 30:
        close = df5m["Close"]
        e20 = _num(close.ewm(span=20, adjust=False).mean().iloc[-1])
        e50 = _num(close.ewm(span=50, adjust=False).mean().iloc[-1])
        if e20 is not None and e50 is not None:
            m["ema"] = "golden" if e20 >= e50 else "death"

    # Net signal count drives the screener ranking and the score band.
    bulls = {"big_candle": "bull", "macd": "bull", "dow": "buy", "ema": "golden",
             "bb": "up", "rsi_trend": "up", "dmi": "bull"}
    bears = {"big_candle": "bear", "macd": "bear", "dow": "sell", "ema": "death",
             "bb": "down", "rsi_trend": "down", "dmi": "bear"}
    m["score"] = sum(1 for k, v in bulls.items() if m[k] == v) - sum(1 for k, v in bears.items() if m[k] == v)
    m["band"] = score_band(m["score"])

    m["detail"] = {}
    for interval in INTERVALS:
        frame = frames_by_interval.get(interval, {}).get(ticker)
        detail = compute_detail(frame)
        if detail:
            m["detail"][interval] = detail
    return m


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #

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
        return "<span class='text-muted'>--</span>"
    cls, text = BADGES[field][value]
    if cls.startswith("text-"):
        return f"<span class='{cls}'>{text}</span>"
    return f"<span class='{cls} clickable-badge' onclick=\"openStock('{sym}')\">{text}</span>"


def render_row(m):
    sym = m["symbol"]
    pct = m["pct"] if m["pct"] is not None else 0.0
    pct_class = "text-success" if pct >= 0 else "text-danger"
    pct_sign = "+" if pct >= 0 else ""
    trend_badge = ("<span class='badge-bull mini-badge'>15M Bull</span>" if m["bull_15m"]
                   else "<span class='badge-bear mini-badge'>15M Bear</span>")

    rsi_cell = f"<span class='clickable-badge' onclick=\"openStock('{sym}')\">{m['rsi']}</span>" if m["rsi"] is not None else "<span class='text-muted'>--</span>"
    adx_cell = f"<span class='clickable-badge' onclick=\"openStock('{sym}')\">{m['adx']}</span>" if m["adx"] is not None else "<span class='text-muted'>--</span>"

    return f"""
    <tr>
        <td class="symbol-col">
            <div class="d-flex justify-content-between align-items-center gap-2">
                <a href="/stock/{sym}" class='symbol-link'>{sym}</a>
                <span class="price-tag">₹{m['price']}</span>
                {trend_badge}
            </div>
            <div class='row-sub {pct_class}'>Daily: {pct_sign}{pct}%</div>
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
            <select class="chart-select" onchange="openChart(this, '{sym}')" aria-label="Open chart for {sym}">
                <option value="" selected disabled>Select Chart</option>
                <option value="analysis">Stock Analysis</option>
                <option value="tradingview">TradingView</option>
                <option value="groww">Groww Chart</option>
            </select>
        </td>
    </tr>
    """


# --------------------------------------------------------------------------- #
# Snapshot store
# --------------------------------------------------------------------------- #

def _empty_snapshot():
    return {
        "tables": {t: {"rows": [], "stats": {"up_count": 0, "down_count": 0, "neutral_count": 0,
                                             "up_pct": 0, "down_pct": 0}} for t in TABLES},
        "metrics": {}, "indices": [], "fx": dict(FX_DEFAULTS),
        "updated_at": 0, "status": "warming", "stale": False,
        "message": "Fetching live market data...", "refresh_seconds": REFRESH_SECONDS,
    }


# Readers take this reference without locking; the refresh thread swaps it wholesale.
SNAPSHOT = _empty_snapshot()


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
            fx[name] = _num(df["Close"].iloc[-1]) or FX_DEFAULTS[name]

    indices = []
    for label, ticker in HEADLINE_INDICES:
        df = daily_frames.get(ticker)
        if df is None or df.empty:
            indices.append({"label": label, "price": None, "pct": None})
            continue
        price = _num(df["Close"].iloc[-1])
        prev = _num(df["Close"].iloc[-2]) if len(df) >= 2 else price
        pct = _num((price - prev) / prev * 100) if price and prev else None
        indices.append({"label": label, "price": price, "pct": pct})

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
        rows, up_count, down_count, neutral = [], 0, 0, 0
        for sym in syms:
            m = metrics.get(sym)
            if not m:
                continue
            rows.append(render_row(m))
            if m["macd"] == "bull":
                up_count += 1
            elif m["macd"] == "bear":
                down_count += 1
            else:
                neutral += 1
        scanned = up_count + down_count
        tables[table_type] = {
            "rows": rows,
            "stats": {
                "up_count": up_count, "down_count": down_count, "neutral_count": neutral,
                "up_pct": round(up_count / scanned * 100, 1) if scanned else 0,
                "down_pct": round(down_count / scanned * 100, 1) if scanned else 0,
            },
        }

    global SNAPSHOT
    SNAPSHOT = {
        "tables": tables, "metrics": metrics, "indices": indices, "fx": fx,
        "updated_at": time.time(), "status": "ok", "stale": False, "message": "",
        "refresh_seconds": REFRESH_SECONDS,
    }
    log.info("snapshot built in %.1fs - %d symbols priced", time.time() - started, len(metrics))


def mark_stale(reason):
    """A failed refresh must never wipe a working dashboard - keep the last good
    data and flag it as stale instead."""
    global SNAPSHOT
    snap = dict(SNAPSHOT)
    snap["stale"] = True
    if snap["status"] == "ok":
        age = int(time.time() - snap["updated_at"])
        snap["message"] = f"Stale data - last successful update {age}s ago"
    else:
        snap["message"] = reason
    SNAPSHOT = snap


def refresh_loop():
    failures = 0
    while True:
        try:
            build_snapshot()
            failures = 0
        except Exception as exc:
            failures += 1
            log.error("refresh failed (%d in a row): %s: %s", failures, type(exc).__name__, exc)
            mark_stale("Market data provider is not responding. Retrying...")
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


# Symbols outside the scanned universe (custom watchlist entries) are the only case
# that genuinely needs a live fetch. Cache them so a page reload does not refetch.
_ADHOC_TTL = 300
_adhoc_cache = {}
_adhoc_lock = threading.Lock()


def adhoc_metrics(sym, intervals=INTERVALS):
    """`intervals` keeps the cost proportional to the need: a strike ladder only
    wants spot, so it asks for the daily frame alone instead of all four."""
    now = time.time()
    cache_key = (sym, tuple(intervals))
    with _adhoc_lock:
        hit = _adhoc_cache.get(cache_key)
        if hit and now - hit[0] < _ADHOC_TTL:
            return hit[1]

    ticker = get_ticker_symbol(sym)
    wanted = set(intervals) | {"1d"}
    frames = {}
    for key, (period, interval) in FRAME_SPECS.items():
        frames[key] = batch_history([ticker], period, interval) if key in wanted else {}
    try:
        original = SYMBOL_TO_TICKER.get(sym)
        SYMBOL_TO_TICKER[sym] = ticker
        result = compute_metrics(sym, frames, SNAPSHOT["fx"]["inr"])
        if original is None:
            SYMBOL_TO_TICKER.pop(sym, None)
    except Exception as exc:
        log.error("adhoc metrics failed for %s: %s", sym, exc)
        result = None

    with _adhoc_lock:
        _adhoc_cache[cache_key] = (now, result)
        if len(_adhoc_cache) > 200:
            _adhoc_cache.clear()
    return result


def lookup_metrics(sym, intervals=INTERVALS):
    """Snapshot first; only reach out to Yahoo for symbols we do not scan."""
    m = SNAPSHOT["metrics"].get(sym)
    return m if m else adhoc_metrics(sym, intervals)


def snapshot_meta(snap=None):
    snap = snap or SNAPSHOT
    age = round(time.time() - snap["updated_at"], 1) if snap["updated_at"] else None
    return {
        "status": snap["status"],
        "stale": snap["stale"],
        "message": snap["message"],
        "updated_at": snap["updated_at"],
        "age_seconds": age,
        "refresh_seconds": snap["refresh_seconds"],
        "next_refresh_in": max(0, round(snap["refresh_seconds"] - age)) if age is not None else None,
        "symbols": len(snap["metrics"]),
        "market": market_status(),
    }


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

@app.after_request
def set_security_headers(response):
    # Inline handlers are used throughout the markup, so script-src still needs
    # 'unsafe-inline'; everything else is locked to this origin plus the CDN.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    return response


@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, title="Page not found",
                           detail="That page does not exist.", **page_context("")), 404


@app.errorhandler(500)
def server_error(exc):
    # Log the detail, show the visitor nothing but a friendly message.
    log.error("unhandled error: %s", exc)
    return render_template("error.html", code=500, title="Something went wrong",
                           detail="The server hit an unexpected error. Try again in a moment.",
                           **page_context("")), 500


def page_context(active):
    return {"active": active, "version": APP_VERSION, "table_labels": TABLE_LABELS}


@app.route("/")
def home():
    return render_template("dashboard.html", **page_context("dashboard"))


@app.route("/screener")
def screener():
    return render_template("screener.html", **page_context("screener"))


@app.route("/heatmap")
def heatmap():
    return render_template("heatmap.html", **page_context("heatmap"))


@app.route("/watchlist")
def watchlist():
    return render_template("watchlist.html", **page_context("watchlist"))


@app.route("/markets")
def markets():
    return render_template("markets.html", **page_context("markets"))


@app.route("/options")
def options_lab():
    return render_template("options.html", **page_context("options"), lot_sizes=LOT_SIZES,
                           symbols=sorted(UNIVERSE))


@app.route("/stock/")
@app.route("/stock/<path:symbol>")
def stock_page(symbol="RELIANCE"):
    sym = clean_symbol(symbol)
    if not sym:
        abort(404)
    return render_template("stock.html", **page_context("stock"), symbol=sym)


@app.route("/about")
def about():
    return render_template("about.html", **page_context("about"),
                           refresh_seconds=REFRESH_SECONDS, universe=len(UNIVERSE),
                           nifty_count=len(NIFTY50_STOCKS))


@app.route("/healthz")
def healthz():
    meta = snapshot_meta()
    return jsonify({"ok": True, **meta})


@app.route("/version")
def version():
    return jsonify({"version": APP_VERSION, "yfinance": getattr(yf, "__version__", "unknown")})


@app.route("/api/meta")
def api_meta():
    return jsonify(snapshot_meta())


@app.route("/api/search")
def api_search():
    """Suggestions come from the allowed universe only - never free text."""
    q = (request.args.get("q", "") or "").strip().upper()[:20]
    if not q:
        return jsonify({"results": []})
    pool = [(s, "stock") for s in UNIVERSE] + [(label, "index") for label, _ in HEADLINE_INDICES]
    starts = [{"symbol": s, "kind": k} for s, k in pool if s.startswith(q)]
    contains = [{"symbol": s, "kind": k} for s, k in pool if q in s and not s.startswith(q)]
    return jsonify({"results": (starts + contains)[:10]})


@app.route("/get_master_table_data")
def get_master_table_data():
    table_type = request.args.get("type", "nifty50")
    if table_type not in TABLES:
        table_type = "nifty50"
    snap = SNAPSHOT
    table = snap["tables"].get(table_type, {"rows": [], "stats": {}})
    return jsonify({"rows": table["rows"], "stats": table["stats"], **snapshot_meta(snap)})


@app.route("/api/stocks")
def api_stocks():
    """Raw indicator values - screener, heatmap, watchlist and dashboard read this."""
    table_type = request.args.get("type", "nifty50")
    snap = SNAPSHOT
    syms = UNIVERSE if table_type == "all" else TABLES.get(table_type, NIFTY50_STOCKS)
    stocks = []
    for s in syms:
        m = snap["metrics"].get(s)
        if m:
            slim = {k: v for k, v in m.items() if k != "detail"}
            stocks.append(slim)
    return jsonify({"stocks": stocks, **snapshot_meta(snap)})


@app.route("/api/indices")
def api_indices():
    snap = SNAPSHOT
    return jsonify({"indices": snap["indices"], "fx": snap["fx"], **snapshot_meta(snap)})


@app.route("/api/pulse")
def api_pulse():
    """Market breadth plus the strongest setups in either direction."""
    snap = SNAPSHOT
    rows = [snap["metrics"][s] for s in NIFTY50_STOCKS if s in snap["metrics"]]
    if not rows:
        return jsonify({"ready": False, **snapshot_meta(snap)})

    by_score = sorted(rows, key=lambda m: (m["score"], m["pct"] or 0), reverse=True)
    by_pct = sorted(rows, key=lambda m: m["pct"] or 0, reverse=True)
    slim = lambda m: {"symbol": m["symbol"], "price": m["price"], "pct": m["pct"],
                      "score": m["score"], "band": m["band"], "rsi": m["rsi"], "adx": m["adx"]}

    return jsonify({
        "ready": True,
        "bullish": sum(1 for m in rows if m["score"] > 0),
        "bearish": sum(1 for m in rows if m["score"] < 0),
        "neutral": sum(1 for m in rows if m["score"] == 0),
        "advancing": sum(1 for m in rows if (m["pct"] or 0) > 0),
        "declining": sum(1 for m in rows if (m["pct"] or 0) < 0),
        "top_gainer": slim(by_pct[0]),
        "top_loser": slim(by_pct[-1]),
        "top_bullish": [slim(m) for m in by_score[:5]],
        "top_bearish": [slim(m) for m in reversed(by_score[-5:])],
        **snapshot_meta(snap),
    })


@app.route("/api/stock/<path:symbol>")
def api_stock(symbol):
    sym = clean_symbol(symbol)
    if not sym:
        return jsonify({"error": "Invalid symbol."}), 400

    snap = SNAPSHOT
    m = snap["metrics"].get(sym)
    source = "snapshot"
    if not m:
        if snap["status"] != "ok":
            return jsonify({"error": "Market data is still loading.", **snapshot_meta(snap)}), 503
        m = adhoc_metrics(sym)
        source = "live"
    if not m:
        return jsonify({"error": f"No market data available for {sym}."}), 404

    return jsonify({"stock": m, "source": source, "lot_size": LOT_SIZES.get(sym),
                    "in_universe": sym in SNAPSHOT["metrics"], **snapshot_meta(snap)})


@app.route("/get_signals")
def get_signals():
    """Kept for compatibility; now served from the snapshot instead of a live fetch."""
    sym = clean_symbol(request.args.get("symbol", "RELIANCE"))
    if not sym:
        return jsonify({"error": "Invalid symbol."}), 400
    interval = request.args.get("interval", "15m")
    if interval not in INTERVALS:
        interval = "15m"

    m = lookup_metrics(sym)
    if not m:
        return jsonify({"error": f"No market data available for {sym}."}), 404

    detail = (m.get("detail") or {}).get(interval) or (m.get("detail") or {}).get("1d")
    if not detail:
        return jsonify({"error": f"No {interval} history available for {sym}."}), 404

    pct = m["pct"] or 0.0
    gauge_score = max(-100, min(100, int(pct * 30)))
    if gauge_score > 25: gauge_trend = "Bullish"
    elif gauge_score > 0: gauge_trend = "Mild Bullish"
    elif gauge_score < -25: gauge_trend = "Bearish"
    elif gauge_score < 0: gauge_trend = "Mild Bearish"
    else: gauge_trend = "Neutral"

    return jsonify({
        "name": sym, "symbol": sym, "price": m["price"], "pct": pct,
        "ema_20": detail["ema_20"], "ema_50": detail["ema_50"],
        "swing_high": detail["swing_high"], "swing_low": detail["swing_low"],
        "volume_status": detail["volume_status"], "last_cross_date": detail["last_cross"],
        "dow_signal": detail["dow_signal"], "ema_signal": detail["ema_signal"],
        "interval": interval, "bars": detail["bars"],
        "gauge_trend": gauge_trend, "gauge_score": gauge_score,
        **snapshot_meta(),
    })


@app.route("/get_movers")
def get_movers():
    metrics = SNAPSHOT["metrics"]
    scored = [{"symbol": s, "pct": metrics[s]["pct"] or 0} for s in NIFTY50_STOCKS if s in metrics]
    scored.sort(key=lambda x: x["pct"], reverse=True)
    movers = scored[:2] + scored[-2:] if len(scored) >= 4 else scored
    return jsonify({"movers": movers})


@app.route("/get_currency_rate")
def get_currency_rate():
    return jsonify(SNAPSHOT["fx"])


@app.route("/get_status_bulk")
def get_status_bulk():
    """One request for a whole watchlist, served from the cached snapshot."""
    raw = request.args.get("symbols", "")
    out = {}
    for part in raw.split(",")[:120]:
        sym = clean_symbol(part)
        if not sym:
            continue
        m = SNAPSHOT["metrics"].get(sym)
        if not m:
            out[sym] = {"available": False, "trend": "--", "daily_change": None,
                        "hourly_trend": "--", "price": None, "score": None, "band": None}
            continue
        pct = m["pct"] or 0
        out[sym] = {
            "available": True, "price": m["price"], "daily_change": pct,
            "trend": "Bullish" if pct > 0 else ("Bearish" if pct < 0 else "Sideways"),
            "hourly_trend": m["hourly_trend"], "score": m["score"], "band": m["band"],
        }
    return jsonify(out)


@app.route("/get_strike_chain")
def get_strike_chain():
    """Analytical strike ladder derived from spot. Clearly not an exchange chain."""
    sym = clean_symbol(request.args.get("symbol", "RELIANCE"))
    if not sym:
        return jsonify({"error": "Invalid symbol."}), 400

    # A ladder only needs spot, so an unknown symbol costs one daily download.
    m = lookup_metrics(sym, intervals=("1d",))
    if not m or not m["price"]:
        return jsonify({"error": f"No spot price available for {sym}."}), 404
    current_price = m["price"]

    if sym == "NIFTY": step = 50
    elif sym == "BANKNIFTY": step = 100
    elif current_price > 5000: step = 100
    elif current_price > 2000: step = 50
    elif current_price > 500: step = 20
    else: step = 10

    atm = int(round(current_price / step) * step)
    chain = []
    for i in range(-3, 4):
        strike = atm + i * step
        is_atm = strike == atm
        diff = strike - current_price
        if is_atm:
            ce = pe = round(step * 0.4, 2)
        elif strike < current_price:
            ce = round(abs(diff) + step * 0.3, 2)
            pe = round(max(2.5, step * 0.4 - abs(diff) * 0.2), 2)
        else:
            ce = round(max(2.5, step * 0.4 - abs(diff) * 0.2), 2)
            pe = round(abs(diff) + step * 0.3, 2)
        chain.append({"strike": strike, "ce_price": ce, "pe_price": pe, "is_atm": is_atm})

    return jsonify({
        "symbol": sym, "chain": chain, "current_price": current_price,
        "lot_size": LOT_SIZES.get(sym, 25), "estimated": True,
        "note": "Premiums are analytical estimates derived from spot and strike distance, not exchange quotes.",
    })


@app.route("/export.csv")
def export_csv():
    table_type = request.args.get("type", "nifty50")
    syms = UNIVERSE if table_type == "all" else TABLES.get(table_type, NIFTY50_STOCKS)
    metrics = SNAPSHOT["metrics"]

    buf = StringIO()
    cols = ["symbol", "price", "pct", "score", "big_candle", "macd", "dow", "ema", "bb",
            "rsi", "rsi_trend", "dmi", "adx", "adx_trend", "hourly_trend"]
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    for s in syms:
        if s in metrics:
            writer.writerow({c: ("" if metrics[s].get(c) is None else metrics[s].get(c)) for c in cols})

    label = TABLE_LABELS.get(table_type, table_type).replace(" ", "-").lower()
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=scanner-{label}.csv"})


@app.route("/gemini_chat")
def gemini_chat():
    """The assistant is given the current scanner numbers so it explains real data
    instead of guessing at prices."""
    msg = (request.args.get("message", "") or "").strip()[:1000]
    if not msg:
        return jsonify({"reply": "Ask me about any stock in the scanner, for example: explain RELIANCE."})
    if not gemini_client:
        return jsonify({"reply": "The AI assistant is not configured on this deployment. "
                                 "Set GEMINI_API_KEY to enable it - everything else keeps working."})

    # Pull metrics for any scanned symbol the user mentioned.
    mentioned = [s for s in UNIVERSE if re.search(rf"\b{re.escape(s)}\b", msg.upper())][:3]
    context_lines = []
    for sym in mentioned:
        m = SNAPSHOT["metrics"].get(sym)
        if not m:
            continue
        context_lines.append(
            f"{sym}: price Rs{m['price']}, daily {m['pct']}%, signal score {m['score']} "
            f"({m['band']['label']}), MACD(1H) {m['macd'] or 'n/a'}, EMA(5M) {m['ema'] or 'n/a'}, "
            f"DOW(15M) {m['dow'] or 'n/a'}, Bollinger {m['bb'] or 'n/a'}, RSI {m['rsi'] or 'n/a'}, "
            f"ADX {m['adx'] or 'n/a'}, hourly trend {m['hourly_trend']}"
        )

    if context_lines:
        prompt = (
            "You are a market analytics assistant embedded in a technical scanner.\n"
            "Explain ONLY the indicator values given below. Never invent prices or numbers "
            "that are not listed. If something is not in the data, say it is not available.\n"
            "Keep it under 150 words, plain language, and end with a one-line reminder that "
            "this is analysis, not investment advice.\n\n"
            "CURRENT SCANNER DATA (delayed):\n" + "\n".join(context_lines) +
            f"\n\nUSER QUESTION: {msg}"
        )
    else:
        prompt = (
            "You are a market analytics assistant inside a technical scanner. You have no live "
            "price data for this question, so do not state any specific prices or levels. "
            "Answer conceptually in under 150 words.\n\n"
            f"USER QUESTION: {msg}"
        )

    try:
        response = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return jsonify({"reply": response.text if response and response.text
                        else "I could not generate a reply just now.",
                        "context_symbols": mentioned})
    except Exception as exc:
        log.error("gemini chat failed: %s", exc)
        return jsonify({"reply": "The assistant is unavailable right now. The scanner itself is unaffected."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, threaded=True)
