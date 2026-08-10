from flask import Flask, jsonify, render_template_string, request, Response
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os
import re

try:
    from google import genai
except ImportError:
    genai = None

app = Flask(__name__)

# Initialize Gemini Client with API Key from environment
gemini_client = None
try:
    if genai:
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            gemini_client = genai.Client(api_key=api_key)
except Exception:
    gemini_client = None

NIFTY50_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "LTIM",
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

GIFTNIFTY_STOCKS = [
    "NIFTY", "BANKNIFTY", "USDINR"
]

FINNIFTY_STOCKS = [
    "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BAJFINANCE", "SHRIRAMFIN", "SBILIFE", "HDFCLIFE", "CHOLAFIN"
]

HTML_PAGE = """<!DOCTYPE html>
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
        }

        body { background-color: var(--bg-color); color: var(--text-color); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; transition: background 0.3s, color 0.3s; }
        .sidebar { height: 100vh; position: fixed; top: 0; left: 0; width: 310px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border-color); padding: 15px; display: flex; flex-direction: column; z-index: 100; overflow-y: auto; transition: width 0.3s ease; }
        .sidebar.collapsed { width: 85px; padding: 10px 5px; }
        .sidebar.collapsed .watchlist-scroll-container, .sidebar.collapsed .calc-panel-sidebar, .sidebar.collapsed h5, .sidebar.collapsed .input-group { display: none !important; }
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
        .master-table-wrapper { width: 100%; overflow-x: auto; max-height: 550px; overflow-y: auto; position: relative; }
        .master-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: center; }
        .master-table th, .master-table td { border: 1px solid var(--section-border); padding: 10px 6px; white-space: nowrap; color: var(--text-color); }
        .master-table th { background-color: var(--table-head-bg); font-weight: bold; position: sticky; top: 0; z-index: 10; }
        .symbol-col { text-align: left !important; padding-left: 12px !important; position: sticky; left: 0; background-color: var(--card-bg); z-index: 5; }
        .master-table tbody tr:hover { background-color: var(--row-hover-bg) !important; }
        .badge-bull { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-bear { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .watchlist-item { padding: 8px 10px; margin-bottom: 6px; background: var(--card-bg); border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); font-size: 0.85rem; transition: 0.2s; display: flex; flex-direction: column; gap: 2px; }
        .watchlist-item:hover { border-color: #3b82f6; }
        .bull { color: #34d399; font-weight: bold; }
        .bear { color: #f87171; font-weight: bold; }
        .flat { color: #fbbf24; font-weight: bold; }
        .theme-toggle-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 6px 12px; border-radius: 16px; font-weight: bold; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.2s; width: 100%; justify-content: center; margin-bottom: 6px; }
        .theme-toggle-btn:hover { border-color: #3b82f6; }
        .sidebar-toggle-btn { background: var(--border-color); color: var(--text-color); border: none; border-radius: 4px; font-size: 0.75rem; padding: 2px 6px; cursor: pointer; float: right; }
        .sidebar-toggle-btn:hover { background: #3b82f6; color: #fff; }
    </style>
</head>
<body>
<div class="sidebar shadow-sm" id="sidebarContainer">
    <div class="d-flex justify-content-between align-items-center mb-2">
        <h5 class="fw-bold text-info mb-0">Scanner</h5>
        <button class="sidebar-toggle-btn" onclick="toggleSidebar()">☰</button>
    </div>
    <div class="input-group input-group-sm mb-2">
        <input type="text" id="newStockInput" class="form-control" placeholder="Add Symbol">
        <button class="btn btn-primary" onclick="addToWatchlist()">Add</button>
    </div>
    <div class="watchlist-scroll-container" id="watchlistContainer"></div>
    <button class="theme-toggle-btn" onclick="toggleTheme()">
        <span id="themeIcon">🌙</span> <span id="themeText">Dark Mode</span>
    </button>
</div>

<div class="main-content" id="mainContentContainer">
    <div class="container-fluid">
        <div class="top-nav">
            <div class="d-flex gap-2 overflow-x-auto align-items-center">
                <a href="https://in.tradingview.com" target="_blank" class="broker-btn">TradingView</a>
                <a href="https://groww.in" target="_blank" class="broker-btn">Groww</a>
                <a href="https://kite.zerodha.com" target="_blank" class="broker-btn">Kite</a>
                <a href="https://www.angelone.in" target="_blank" class="broker-btn">Angel One</a>
                <a href="https://upstox.com" target="_blank" class="broker-btn">Upstox</a>
            </div>
            <div class="d-flex align-items-center gap-2">
                <div class="live-widget-box" title="Market Time">
                    <span id="liveClockDisplay" class="fw-bold text-info">--:--:--</span>
                    <span id="liveDateDisplay" class="text-warning">--/--/----</span>
                </div>
            </div>
        </div>

        <div class="text-center mb-2">
            <h2 class="fw-bold text-info">ULTIMATE PRO TRADING SCANNER</h2>
            <p class="text-muted small">Advanced Live Market Multi-Indicator Analytics</p>
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

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <h5 class="fw-bold text-info mb-3">📊 Nifty 50 Stocks Live Market</h5>
                    <div class="master-table-wrapper" id="niftyTableWrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th">Stock</th>
                                    <th>💥 Big Candle (15M)</th>
                                    <th>⚡ MACD Crossover (1H)</th>
                                    <th>📉 DOW Breakouts (15M)</th>
                                    <th>➡️ EMA Crossover (5M)</th>
                                    <th>📊 RSI Value (15M)</th>
                                </tr>
                            </thead>
                            <tbody id="niftyTableBody">
                                <tr><td colspan="6" class="text-center text-muted">Scanning Nifty 50 Live Market Data...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let watchlist = JSON.parse(localStorage.getItem('user_watchlist')) || ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"];

window.addEventListener('DOMContentLoaded', () => {
    let savedTheme = localStorage.getItem('app_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
    renderWatchlist();
    fetchAllTables();

    setInterval(() => {
        let now = new Date();
        let optTime = { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
        let optDate = { timeZone: 'Asia/Kolkata', weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        document.getElementById('liveClockDisplay').innerText = now.toLocaleTimeString('en-US', optTime);
        document.getElementById('liveDateDisplay').innerText = now.toLocaleDateString('en-GB', optDate);
        fetchAllTables();
    }, 60000);
});

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

function toggleSidebar() {
    let sidebar = document.getElementById('sidebarContainer');
    let mainContent = document.getElementById('mainContentContainer');
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

async function renderWatchlist() {
    let container = document.getElementById('watchlistContainer');
    container.innerHTML = "";
    for(let stock of watchlist) {
        let div = document.createElement('div');
        div.className = "watchlist-item";
        div.innerHTML = `<div><b>${stock}</b><br><span style="font-size:0.75rem; color:#94a3b8;">--</span></div>`;
        div.onclick = () => {
            document.getElementById('stockSymbol').value = stock;
            scanStock();
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

async function scanStock() {
    let inputVal = document.getElementById('stockSymbol').value.trim().toUpperCase();
    if(!inputVal) { alert("Please enter a stock symbol"); return; }

    let response = await fetch(`/get_signals?symbol=${encodeURIComponent(inputVal)}&interval=15m`);
    let data = await response.json();

    if(data.error) { alert("Error: " + data.error); return; }
    alert(`Stock: ${data.name}\nPrice: ₹${data.price}\nEMA 20: ₹${data.ema_20}\nEMA 50: ₹${data.ema_50}`);
}

async function fetchAllTables() {
    try {
        let res = await fetch('/get_master_table_data?type=nifty50');
        let data = await res.json();
        document.getElementById('niftyTableBody').innerHTML = data.rows.length > 0 ? data.rows.join("") : "<tr><td colspan='6' class='text-center text-muted'>No data found</td></tr>";
    } catch(e) {}
}
</script>
</body>
</html>"""

def get_ticker_symbol(query):
    query = query.upper()
    if query == "NIFTY": return "^NSEI"
    elif query == "BANKNIFTY": return "^NSEBANK"
    elif query == "USDINR": return "INR=X"
    elif query == "M&M": return "M-M.NS"
    elif query.endswith(".NS") or query.startswith("^") or query.endswith("=F") or query.endswith("=X"):
        return query
    else:
        return query + ".NS"

def format_ist_time(raw_time):
    try:
        if hasattr(raw_time, 'tzinfo') and raw_time.tzinfo is not None:
            ist_tz = pytz.timezone('Asia/Kolkata')
            local_dt = raw_time.astimezone(ist_tz)
            return local_dt.strftime('%d/%m %H:%M')
        else:
            return pd.to_datetime(raw_time).strftime('%d/%m %H:%M')
    except:
        return str(raw_time)

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/get_currency_rate')
def get_currency_rate():
    try:
        inr_t = yf.Ticker("INR=X")
        inr = round(float(inr_t.history(period="1d")['Close'].iloc[-1]), 2) if not inr_t.history(period="1d").empty else 83.50
        return jsonify({"inr": inr})
    except:
        return jsonify({"inr": 83.50})

@app.route('/get_master_table_data')
def get_master_table_data():
    table_type = request.args.get('type', 'nifty50')

    if table_type == 'nifty50':
        stock_list = NIFTY50_STOCKS[:10]
    else:
        stock_list = NIFTY50_STOCKS[:10]

    rows = []
    for sym in stock_list:
        try:
            ticker_sym = get_ticker_symbol(sym)
            stock = yf.Ticker(ticker_sym)
            df = stock.history(period="5d", interval="1d")
            if df.empty or len(df) < 1:
                continue

            curr_price = round(float(df['Close'].iloc[-1]), 2)
            row_html = f"<tr><td class='symbol-col'>{sym} (₹{curr_price})</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>"
            rows.append(row_html)
        except:
            continue

    return jsonify({"rows": rows, "stats": {"up_count": 0, "down_count": 0, "up_pct": 0, "down_pct": 0}})

@app.route('/get_signals')
def get_signals():
    symbol = request.args.get('symbol', 'RELIANCE')
    try:
        ticker_symbol = get_ticker_symbol(symbol)
        stock = yf.Ticker(ticker_symbol)

        df = stock.history(period="60d", interval="1d")
        if df.empty or len(df) < 10:
            return jsonify({"error": "Insufficient data"})

        current_price = round(df['Close'].iloc[-1], 2)
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        ema_20 = round(df['EMA_20'].iloc[-1], 2)
        ema_50 = round(df['EMA_50'].iloc[-1], 2)

        try:
            short_name = stock.info.get('shortName', symbol)
        except:
            short_name = symbol

        return jsonify({
            "name": short_name, "price": current_price, "ema_20": ema_20, "ema_50": ema_50,
            "swing_high": current_price, "swing_low": current_price, "volume_status": "Normal",
            "dow_signal": "WAIT", "ema_signal": "WAIT"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
