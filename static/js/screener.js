/* Screener: fetch the raw snapshot once, filter and sort in the browser so every
   control responds instantly. */

let allStocks = [];
let bias = 'all';

const SORTERS = {
    score: m => m.score ?? 0,
    pct: m => m.pct ?? 0,
    rsi: m => m.rsi ?? -1,
    adx: m => m.adx ?? -1,
    price: m => m.price ?? 0,
    symbol: m => m.symbol
};

function setBias(btn) {
    bias = btn.dataset.bias;
    document.querySelectorAll('#biasFilters .pill').forEach(p => p.classList.toggle('active', p === btn));
    render();
}

function resetAll() {
    bias = 'all';
    document.querySelectorAll('#biasFilters .pill').forEach(p =>
        p.classList.toggle('active', p.dataset.bias === 'all'));
    document.getElementById('symbolSearch').value = '';
    document.getElementById('sortSelect').value = 'score';
    document.getElementById('sortDir').value = 'desc';
    render();
}

function currentResults() {
    const needle = document.getElementById('symbolSearch').value.trim().toUpperCase();
    const key = document.getElementById('sortSelect').value;
    const dir = document.getElementById('sortDir').value === 'asc' ? 1 : -1;

    const rows = allStocks.filter(m => {
        if (needle && !m.symbol.includes(needle)) return false;
        if (bias !== 'all' && m.band?.key !== bias) return false;
        return true;
    });

    const get = SORTERS[key] || SORTERS.score;
    return rows.sort((a, b) => {
        const x = get(a), y = get(b);
        if (typeof x === 'string') return dir * x.localeCompare(y);
        return dir * (x - y);
    });
}

function render() {
    const rows = currentResults();
    const body = document.getElementById('screenerBody');
    document.getElementById('resultCount').innerText = `${rows.length} of ${allStocks.length} symbols`;

    if (!rows.length) {
        body.innerHTML = `<tr><td colspan="14" class="empty-state"><span class="big">🔍</span>
            No symbol matches these filters. Try a different bias or clear the search.</td></tr>`;
        return;
    }

    body.innerHTML = rows.map(m => `<tr>
        <td class="symbol-col">
            <div class="d-flex justify-content-between align-items-center gap-2">
                <a class="symbol-link" href="/stock/${encodeURIComponent(m.symbol)}">${escapeHtml(m.symbol)}</a>
                <span class="price-tag mono">₹${fmt(m.price)}</span>
            </div>
            <div class="row-sub ${pctClass(m.pct)}">Daily: ${fmtPct(m.pct)}</div>
        </td>
        <td data-label="Score">${scorePill(m.score, m.band)}</td>
        <td data-label="Big Candle">${cell('big_candle', m.big_candle)}</td>
        <td data-label="MACD 1H">${cell('macd', m.macd)}</td>
        <td data-label="DOW 15M">${cell('dow', m.dow)}</td>
        <td data-label="EMA 5M">${cell('ema', m.ema)}</td>
        <td data-label="Bollinger">${cell('bb', m.bb)}</td>
        <td data-label="RSI" class="mono">${fmt(m.rsi, 1)}</td>
        <td data-label="RSI Trend">${cell('rsi_trend', m.rsi_trend)}</td>
        <td data-label="DMI">${cell('dmi', m.dmi)}</td>
        <td data-label="ADX" class="mono">${fmt(m.adx, 1)}</td>
        <td data-label="ADX Trend">${cell('adx_trend', m.adx_trend)}</td>
        <td data-label="Hourly Trend">${escapeHtml(m.hourly_trend || '--')}</td>
        <td class="chart-col">
            <select class="chart-select" onchange="openChart(this, '${escapeHtml(m.symbol)}')" aria-label="Open chart">
                <option value="" selected disabled>Select</option>
                <option value="analysis">Stock Analysis</option>
                <option value="tradingview">TradingView</option>
                <option value="groww">Groww</option>
            </select>
        </td>
    </tr>`).join('');
}

function downloadResults() {
    const rows = currentResults();
    if (!rows.length) return;
    const cols = ['symbol', 'price', 'pct', 'score', 'big_candle', 'macd', 'dow', 'ema', 'bb',
                  'rsi', 'rsi_trend', 'dmi', 'adx', 'adx_trend', 'hourly_trend'];
    const csv = [cols.join(',')]
        .concat(rows.map(r => cols.map(c => r[c] === null || r[c] === undefined ? '' : r[c]).join(',')))
        .join('\n');

    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'screener-results.csv';
    a.click();
    URL.revokeObjectURL(url);
}

async function loadStocks() {
    const universe = document.getElementById('universeSelect').value;
    try {
        const data = await (await fetch(`/api/stocks?type=${universe}`)).json();
        applyMeta(data);
        if (!data.stocks.length && data.status === 'warming') {
            document.getElementById('screenerBody').innerHTML =
                `<tr><td colspan="14" class="loading-cell">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>`;
            setTimeout(loadStocks, 5000);
            return;
        }
        allStocks = data.stocks;
        render();
    } catch (e) {
        document.getElementById('screenerBody').innerHTML =
            `<tr><td colspan="14" class="error-state">Could not load the scan. Retrying…</td></tr>`;
        setTimeout(loadStocks, 8000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    setInterval(loadStocks, 60000);
});
