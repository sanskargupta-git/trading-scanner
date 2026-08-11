from flask import Flask, jsonify, render_template_string, request, Response
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os
import re

# Optional: Gemini integration (non-blocking)
gemini_client = None
try:
    from google import genai
    api_key = os.environ.get('GEMINI_API_KEY', "AQ.Ab8RN6KjbYOc2SwKTrLYkvrx3EH9RUglyFKE6vq9pkURcZmUHw")
    gemini_client = genai.Client(api_key=api_key)
except ImportError:
    pass
except Exception:
    pass

app = Flask(__name__)
app.config['VERSION'] = "v1.5-daily-macd"

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
        .badge-bull { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .badge-bear { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.72rem; }
        .symbol-link { color: #38bdf8; text-decoration: none; font-weight: bold; cursor: pointer; }
        .symbol-link:hover { text-decoration: underline; }
        .chart-select { background: var(--input-bg); color: var(--text-color); border: 1px solid var(--border-color); font-size: 0.72rem; padding: 3px 6px; border-radius: 4px; cursor: pointer; }
        .chart-select:hover { border-color: #38bdf8; }
    </style>
</head>
<body>
<div class="sidebar shadow-sm" id="sidebarContainer">
    <h5 class="fw-bold text-info mb-0">Scanner</h5>
    <div class="watchlist-scroll-container" id="watchlistContainer"></div>
</div>

<div class="main-content" id="mainContentContainer">
    <div class="container-fluid">
        <div class="text-center mb-4">
            <h2 class="fw-bold text-info">ULTIMATE PRO TRADING SCANNER</h2>
            <p class="text-muted small">Advanced Live Market Multi-Indicator Analytics</p>
        </div>

        <div class="card p-3 shadow-sm mb-4">
            <div class="row g-3 align-items-center">
                <div class="col-md-8">
                    <label class="form-label fw-bold text-muted">Stock Symbol:</label>
                    <input type="text" id="stockSymbol" class="form-control" placeholder="e.g. RELIANCE">
                </div>
                <div class="col-md-4 d-flex align-items-end">
                    <button class="btn btn-primary w-100 fw-bold" onclick="scanStock()">Scan Stock</button>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-md-12">
                <div class="card p-3 shadow-sm">
                    <h5 class="fw-bold text-info mb-3">📊 Nifty 50 Stocks Live Market</h5>
                    <div class="master-table-wrapper">
                        <table class="master-table">
                            <thead>
                                <tr>
                                    <th class="symbol-th">Stock</th>
                                    <th>⚡ MACD Status</th>
                                    <th>📊 Chart</th>
                                </tr>
                            </thead>
                            <tbody id="niftyTableBody">
                                <tr><td colspan="3" class="text-center text-muted">Loading data...</td></tr>
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
window.addEventListener('DOMContentLoaded', () => {
    fetchAllTables();
});

function openChart(symbol, source) {
    let tvSymbol = `NSE:${symbol}`;
    let url = source === 'tv' ? `https://in.tradingview.com/chart/?symbol=${tvSymbol}` : `https://groww.in/stocks/nse-${symbol.toLowerCase()}`;
    window.open(url, '_blank');
}

async function fetchAllTables() {
    try {
        let res = await fetch('/get_master_table_data?type=nifty50');
        let data = await res.json();
        document.getElementById('niftyTableBody').innerHTML = data.rows.length > 0 ? data.rows.join("") : "<tr><td colspan='3' class='text-center text-muted'>No data</td></tr>";
    } catch(e) {
        document.getElementById('niftyTableBody').innerHTML = "<tr><td colspan='3' class='text-center text-danger'>Error loading data</td></tr>";
    }
}

async function scanStock() {
    let symbol = document.getElementById('stockSymbol').value.trim().toUpperCase();
    if(!symbol) { alert("Enter stock symbol"); return; }
    alert(`Scanning ${symbol}...`);
}
</script>
</body>
</html>
"""

def get_ticker_symbol(query):
    query = query.upper()
    if query == "NIFTY": return "^NSEI"
    elif query == "BANKNIFTY": return "^NSEBANK"
    elif query == "USDINR": return "INR=X"
    elif query == "M&M": return "M-M.NS"
    elif query.endswith(".NS") or query.startswith("^") or query.endswith("=X"): return query
    else: return query + ".NS"

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/get_master_table_data')
def get_master_table_data():
    table_type = request.args.get('type', 'nifty50')

    if table_type == 'banknifty': stock_list = BANKNIFTY_STOCKS
    elif table_type == 'commodities': stock_list = COMMODITIES_STOCKS
    elif table_type == 'giftnifty': stock_list = GIFTNIFTY_STOCKS
    elif table_type == 'finnifty': stock_list = FINNIFTY_STOCKS
    else: stock_list = NIFTY50_STOCKS

    rows = []
    up_count = 0
    down_count = 0

    for sym in stock_list:
        try:
            ticker_sym = get_ticker_symbol(sym)
            stock = yf.Ticker(ticker_sym)
            df = stock.history(period="5d", interval="1d")

            if df.empty or len(df) < 2:
                rows.append(f"<tr><td class='symbol-col'>{sym}</td><td>--</td><td><select class='chart-select' onchange='openChart(\"{sym}\", this.value)'><option value=''>📊</option><option value='tv'>TradingView</option><option value='groww'>Groww</option></select></td></tr>")
                continue

            curr_price = round(float(df['Close'].iloc[-1]), 2)
            prev_price = round(float(df['Close'].iloc[-2]), 2)
            daily_pct = round(((curr_price - prev_price) / prev_price) * 100, 2)
            pct_color = "text-success" if daily_pct >= 0 else "text-danger"
            pct_sign = "+" if daily_pct >= 0 else ""

            macd_status = "--"
            try:
                df_macd = stock.history(period="60d", interval="1d")
                if not df_macd.empty and len(df_macd) >= 26:
                    ema12 = df_macd['Close'].ewm(span=12, adjust=False).mean()
                    ema26 = df_macd['Close'].ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    signal = macd.ewm(span=9, adjust=False).mean()

                    if macd.iloc[-1] > signal.iloc[-1]:
                        macd_status = "<span class='badge-bull'>✓ Bullish</span>"
                        up_count += 1
                    else:
                        macd_status = "<span class='badge-bear'>✗ Bearish</span>"
                        down_count += 1
            except Exception as macd_err:
                app.logger.error(f"MACD failed for {sym}: {type(macd_err).__name__}: {macd_err}")

            row_html = f"<tr><td class='symbol-col'><span class='symbol-link' onclick=\"document.getElementById('stockSymbol').value='{sym}'; scanStock();\">{sym}</span><br><span style='font-size:0.75rem;'><span class='fw-bold text-success'>₹{curr_price}</span> <span class='{pct_color} fw-bold'>{pct_sign}{daily_pct}%</span></span></td><td>{macd_status}</td><td><select class='chart-select' onchange='openChart(\"{sym}\", this.value)'><option value=''>📊</option><option value='tv'>TradingView</option><option value='groww'>Groww</option></select></td></tr>"
            rows.append(row_html)
        except Exception as e:
            rows.append(f"<tr><td class='symbol-col'>{sym}</td><td>Error</td><td><select class='chart-select' onchange='openChart(\"{sym}\", this.value)'><option value=''>📊</option><option value='tv'>TV</option></select></td></tr>")

    stats = {"up_count": up_count, "down_count": down_count, "up_pct": 0, "down_pct": 0}
    return jsonify({"rows": rows, "stats": stats})

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

        return jsonify({
            "name": symbol,
            "price": current_price,
            "ema_20": ema_20,
            "ema_50": ema_50,
            "swing_high": current_price * 1.05,
            "swing_low": current_price * 0.95,
            "volume_status": "Normal",
            "dow_signal": "WAIT",
            "dow_message": "Analyzing...",
            "dow_time": "N/A",
            "ema_signal": "WAIT",
            "last_cross_date": "N/A",
            "gauge_trend": "Neutral",
            "gauge_score": 0
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
