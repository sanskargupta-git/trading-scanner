/* Stock analysis: indicator grid, per-timeframe levels and a technical summary
   derived strictly from the values the scanner already computed. */

const SYMBOL = document.getElementById('stockRoot').dataset.symbol;
let stock = null;
let timeframe = '15m';

const INDICATORS = [
    ['big_candle', 'Big Candle', '15M'],
    ['macd', 'MACD Crossover', '1H'],
    ['dow', 'DOW Breakout', '15M'],
    ['ema', 'EMA Crossover', '5M'],
    ['bb', 'Bollinger Band', '15M'],
    ['rsi_trend', 'RSI Trend', '15M'],
    ['dmi', 'DMI Crossover', '15M'],
    ['adx_trend', 'ADX Trend', '15M']
];

function setTimeframe(tf) {
    timeframe = tf;
    document.querySelectorAll('#tfTabs .pill').forEach(p => p.classList.toggle('active', p.dataset.tf === tf));
    document.getElementById('tfLabel').innerText = tf.toUpperCase();
    renderLevels();
}

/* ---------- Watchlist ---------- */
function readWatchlist() {
    try {
        const raw = JSON.parse(localStorage.getItem('user_watchlist'));
        if (Array.isArray(raw)) return raw;
    } catch (e) { /* ignore malformed storage */ }
    return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN'];
}

function renderWatchButton() {
    const btn = document.getElementById('wlToggle');
    const has = readWatchlist().includes(SYMBOL);
    btn.innerText = has ? '✓ In Watchlist' : '+ Watchlist';
    btn.classList.toggle('active', has);
}

function toggleWatch() {
    const list = readWatchlist();
    const i = list.indexOf(SYMBOL);
    if (i >= 0) list.splice(i, 1); else list.push(SYMBOL);
    localStorage.setItem('user_watchlist', JSON.stringify(list));
    renderWatchButton();
}

/* ---------- Rendering ---------- */
function renderHero() {
    document.getElementById('sName').innerText = stock.symbol;
    document.getElementById('sPrice').innerText =
        stock.price === null ? '--' : `₹${stock.price.toLocaleString('en-IN')}`;

    const change = document.getElementById('sChange');
    change.className = `stock-change ${pctClass(stock.pct)}`;
    const move = (stock.pct !== null && stock.price !== null && stock.prev_close !== null)
        ? ` (${stock.pct >= 0 ? '+' : ''}${(stock.price - stock.prev_close).toFixed(2)})` : '';
    change.innerText = `${fmtPct(stock.pct)}${move} today`;

    document.getElementById('sBand').innerHTML = scorePill(stock.score, stock.band) +
        ` <span class="text-muted" style="font-size:.78rem">${escapeHtml(stock.band?.label || '')}</span>`;
    document.getElementById('tvLink').href =
        `https://in.tradingview.com/chart/?symbol=${tvSymbolFor(stock.symbol)}`;
}

function renderIndicators() {
    const cells = INDICATORS.map(([key, name, tf]) => `
        <div class="ind-cell">
            <div class="d-flex justify-content-between align-items-center">
                <span class="ind-name">${name}</span><span class="ind-tf">${tf}</span>
            </div>
            <div class="ind-value">${cell(key, stock[key])}</div>
        </div>`).join('');

    const values = `
        <div class="ind-cell">
            <div class="d-flex justify-content-between align-items-center">
                <span class="ind-name">RSI Value</span><span class="ind-tf">15M</span>
            </div>
            <div class="ind-value mono">${fmt(stock.rsi, 1)}</div>
        </div>
        <div class="ind-cell">
            <div class="d-flex justify-content-between align-items-center">
                <span class="ind-name">ADX Value</span><span class="ind-tf">15M</span>
            </div>
            <div class="ind-value mono">${fmt(stock.adx, 1)}</div>
        </div>`;

    document.getElementById('indGrid').innerHTML = cells + values;
}

function renderLevels() {
    const grid = document.getElementById('levelGrid');
    const d = stock && stock.detail ? stock.detail[timeframe] : null;
    if (!d) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
            No ${timeframe.toUpperCase()} history available for this symbol.</div>`;
        return;
    }
    grid.innerHTML = `
        <div class="stat-tile"><div class="stat-label">EMA 20</div><div class="stat-value mono">${fmt(d.ema_20)}</div></div>
        <div class="stat-tile"><div class="stat-label">EMA 50</div><div class="stat-value mono">${fmt(d.ema_50)}</div></div>
        <div class="stat-tile"><div class="stat-label">Swing High</div><div class="stat-value mono">${fmt(d.swing_high)}</div></div>
        <div class="stat-tile"><div class="stat-label">Swing Low</div><div class="stat-value mono">${fmt(d.swing_low)}</div></div>
        <div class="stat-tile"><div class="stat-label">Volume</div>
            <div class="stat-value" style="font-size:.9rem">${escapeHtml(d.volume_status)}</div></div>
        <div class="stat-tile"><div class="stat-label">EMA Signal</div>
            <div class="stat-value" style="font-size:.9rem">${escapeHtml(d.ema_signal)}</div>
            <div class="stat-note">last cross ${escapeHtml(d.last_cross)}</div></div>
        <div class="stat-tile"><div class="stat-label">DOW Signal</div>
            <div class="stat-value" style="font-size:.9rem">${escapeHtml(d.dow_signal)}</div></div>
        <div class="stat-tile"><div class="stat-label">Bars Analysed</div>
            <div class="stat-value mono">${d.bars}</div></div>`;
}

/* Every line below restates an existing indicator value; nothing is inferred
   beyond what the scanner already computed. */
function renderSummary() {
    const trend = stock.score > 0 ? 'Bullish' : stock.score < 0 ? 'Bearish' : 'Neutral';
    const trendClass = stock.score > 0 ? 'text-success' : stock.score < 0 ? 'text-danger' : 'text-muted';

    let momentum = 'Not available', momentumClass = 'text-muted';
    if (stock.macd === 'bull') { momentum = 'Positive (MACD above signal)'; momentumClass = 'text-success'; }
    else if (stock.macd === 'bear') { momentum = 'Negative (MACD below signal)'; momentumClass = 'text-danger'; }

    let strength = 'Not available', strengthClass = 'text-muted';
    if (stock.adx !== null && stock.adx !== undefined) {
        const label = stock.adx > 25 ? 'Trending' : stock.adx > 20 ? 'Developing' : 'Weak / ranging';
        strength = `ADX ${stock.adx.toFixed(1)} — ${label}`;
        strengthClass = stock.adx > 25 ? 'text-success' : 'text-warning';
    }

    let rsiState = 'Not available', rsiClass = 'text-muted';
    if (stock.rsi !== null && stock.rsi !== undefined) {
        const label = stock.rsi > 70 ? 'Overbought' : stock.rsi < 30 ? 'Oversold' : 'Neutral zone';
        rsiState = `${stock.rsi.toFixed(1)} — ${label}`;
        rsiClass = stock.rsi > 70 ? 'text-danger' : stock.rsi < 30 ? 'text-success' : 'text-muted';
    }

    const checks = [
        stock.big_candle === 'bull', stock.macd === 'bull', stock.dow === 'buy',
        stock.ema === 'golden', stock.bb === 'up', stock.rsi_trend === 'up', stock.dmi === 'bull'
    ];
    const agree = checks.filter(Boolean).length;

    document.getElementById('summaryBox').innerHTML = `
        <div class="summary-row"><span class="summary-key">Trend</span>
            <span class="summary-val ${trendClass}">${trend}</span></div>
        <div class="summary-row"><span class="summary-key">Momentum</span>
            <span class="summary-val ${momentumClass}">${momentum}</span></div>
        <div class="summary-row"><span class="summary-key">Strength</span>
            <span class="summary-val ${strengthClass}">${strength}</span></div>
        <div class="summary-row"><span class="summary-key">RSI</span>
            <span class="summary-val ${rsiClass}">${rsiState}</span></div>
        <div class="summary-row"><span class="summary-key">Hourly Trend</span>
            <span class="summary-val">${escapeHtml(stock.hourly_trend || '--')}</span></div>
        <div class="summary-row"><span class="summary-key">Signals Agreeing</span>
            <span class="summary-val">${agree} bullish / ${checks.length - agree} other</span></div>
        <p class="text-muted mt-3 mb-0" style="font-size:.73rem">
            Derived only from the indicator values above. This is analysis, not investment advice.</p>`;
}

function renderDataStatus(meta, source) {
    const mkt = meta.market || {};
    const updated = meta.updated_at
        ? new Date(meta.updated_at * 1000).toLocaleTimeString('en-GB', { timeZone: 'Asia/Kolkata', hour12: false })
        : '--';
    document.getElementById('dataStatusBox').innerHTML = `
        <div class="summary-row"><span class="summary-key">Market Status</span>
            <span class="summary-val">${escapeHtml(mkt.label || '--')}</span></div>
        <div class="summary-row"><span class="summary-key">Last Updated</span>
            <span class="summary-val mono">${updated}</span></div>
        <div class="summary-row"><span class="summary-key">Data Age</span>
            <span class="summary-val mono">${meta.age_seconds === null ? '--' : Math.round(meta.age_seconds) + 's'}</span></div>
        <div class="summary-row"><span class="summary-key">Data Status</span>
            <span class="summary-val ${meta.stale ? 'text-warning' : 'text-success'}">${meta.stale ? 'STALE' : 'FRESH'}</span></div>
        <div class="summary-row"><span class="summary-key">Source</span>
            <span class="summary-val">${source === 'snapshot' ? 'Cached snapshot' : 'Live fetch'}</span></div>
        <p class="text-muted mt-2 mb-0" style="font-size:.73rem">Prices are delayed Yahoo Finance data.</p>`;
}

async function load() {
    try {
        const res = await fetch(`/api/stock/${encodeURIComponent(SYMBOL)}`);
        const data = await res.json();

        if (!res.ok || data.error) {
            document.getElementById('stockError').hidden = false;
            document.getElementById('stockErrorText').innerText = data.error || 'Could not load this symbol.';
            if (res.status === 503) setTimeout(load, 5000);
            return;
        }

        document.getElementById('stockError').hidden = true;
        stock = data.stock;
        applyMeta(data);

        const src = document.getElementById('sSource');
        if (data.source === 'live') { src.hidden = false; src.innerText = 'Off-universe symbol'; }

        renderHero();
        renderIndicators();
        renderLevels();
        renderSummary();
        renderDataStatus(data, data.source);
    } catch (e) {
        document.getElementById('stockError').hidden = false;
        document.getElementById('stockErrorText').innerText = 'Could not reach the server. Retrying…';
        setTimeout(load, 8000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    renderWatchButton();
    load();
    setInterval(load, 60000);
});
