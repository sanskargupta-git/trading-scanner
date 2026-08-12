/* Stock analysis: indicator grid, per-timeframe levels and a technical summary
   derived strictly from the values the scanner already computed. */

const SYMBOL = document.getElementById('stockRoot').dataset.symbol;
let stock = null;
let timeframe = '15m';

/* field, label, requested timeframe group */
const INDICATORS = [
    ['big_candle', 'Big Candle', '15m'],
    ['macd', 'MACD Crossover', '1h'],
    ['dow', 'DOW Breakout', '15m'],
    ['ema', 'EMA Crossover', '5m'],
    ['bb', 'Bollinger Band', '15m'],
    ['rsi_trend', 'RSI Trend', '15m'],
    ['dmi', 'DMI Crossover', '15m'],
    ['adx_trend', 'ADX Trend', '15m']
];

const TF_LABEL = { '5m': '5M', '15m': '15M', '1h': '1H', '1d': 'Daily' };

/* Never label a daily value as if it were intraday: say what was requested and
   what actually arrived. */
function tfTag(requested) {
    const used = stock && stock.tf ? stock.tf[requested] : null;
    if (!used) {
        return `<span class="ind-tf tf-none" title="No data for this timeframe">unavailable</span>`;
    }
    if (used === requested) {
        return `<span class="ind-tf">${TF_LABEL[requested]}</span>`;
    }
    return `<span class="ind-tf tf-fallback"
                  title="${TF_LABEL[requested]} requested — Yahoo did not return enough intraday bars, so ${TF_LABEL[used]} data was used">
                ${TF_LABEL[requested]} req · ${TF_LABEL[used]} fallback</span>`;
}

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

/* Market status, data age and freshness, right under the price. */
function renderHeroMeta(meta) {
    const mkt = meta.market || {};
    const age = meta.age_seconds === null || meta.age_seconds === undefined
        ? '--' : `${Math.round(meta.age_seconds)}s`;
    const freshness = meta.status !== 'ok' ? ['DATA UNAVAILABLE', 'chip-warn']
        : meta.stale ? ['STALE DATA', 'chip-warn'] : ['FRESH DATA', 'chip-ok'];

    document.getElementById('sMeta').innerHTML = `
        <span class="chip"><span class="dot ${(mkt.state || 'closed').toLowerCase()}"></span>${escapeHtml(mkt.label || '--')}</span>
        <span class="chip ${freshness[1]}">${freshness[0]}</span>
        <span class="chip">Updated ${age} ago</span>`;
}

function renderIndicators() {
    const cells = INDICATORS.map(([key, name, tf]) => `
        <div class="ind-cell">
            <div class="ind-head"><span class="ind-name">${name}</span>${tfTag(tf)}</div>
            <div class="ind-value">${cell(key, stock[key])}</div>
        </div>`).join('');

    const values = `
        <div class="ind-cell">
            <div class="ind-head"><span class="ind-name">RSI Value</span>${tfTag('15m')}</div>
            <div class="ind-value mono">${fmt(stock.rsi, 1)}</div>
        </div>
        <div class="ind-cell">
            <div class="ind-head"><span class="ind-name">ADX Value</span>${tfTag('15m')}</div>
            <div class="ind-value mono">${fmt(stock.adx, 1)}</div>
        </div>`;

    document.getElementById('indGrid').innerHTML = cells + values;

    const groups = stock.tf || {};
    const fell = Object.entries(groups).filter(([req, used]) => used && used !== req);
    const missing = Object.entries(groups).filter(([, used]) => !used);
    const note = document.getElementById('tfNote');
    if (fell.length || missing.length) {
        const parts = [];
        if (fell.length) parts.push(`${fell.map(([r]) => TF_LABEL[r]).join(', ')} unavailable from the provider — daily bars used instead`);
        if (missing.length) parts.push(`${missing.map(([r]) => TF_LABEL[r]).join(', ')} could not be computed`);
        note.innerHTML = `⚠ ${parts.join('. ')}.`;
        note.hidden = false;
    } else {
        note.hidden = true;
    }
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

    /* Bollinger bandwidth: band spread relative to the middle band. */
    let volatility = 'Not available', volClass = 'text-muted';
    if (stock.bb_width !== null && stock.bb_width !== undefined) {
        const label = stock.bb_width > 6 ? 'Expanded' : stock.bb_width < 3 ? 'Compressed' : 'Normal';
        volatility = `Band width ${stock.bb_width.toFixed(2)}% — ${label}`;
        volClass = stock.bb_width > 6 ? 'text-warning' : 'text-muted';
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
        <div class="summary-row"><span class="summary-key">Volatility</span>
            <span class="summary-val ${volClass}">${volatility}</span></div>
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
        renderHeroMeta(data);
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
