/* Screener: pull the raw indicator snapshot once, filter and sort it in the browser
   so every chip toggle is instant. */

let allStocks = [];

const PREDICATES = {
    macd_bull: s => s.macd === 'bull',
    macd_bear: s => s.macd === 'bear',
    dow_buy: s => s.dow === 'buy',
    dow_sell: s => s.dow === 'sell',
    ema_golden: s => s.ema === 'golden',
    ema_death: s => s.ema === 'death',
    bb_up: s => s.bb === 'up',
    bb_down: s => s.bb === 'down',
    dmi_bull: s => s.dmi === 'bull',
    dmi_bear: s => s.dmi === 'bear',
    candle_bull: s => s.big_candle === 'bull',
    candle_bear: s => s.big_candle === 'bear',
    rsi_oversold: s => s.rsi !== null && s.rsi < 30,
    rsi_overbought: s => s.rsi !== null && s.rsi > 70,
    adx_strong: s => s.adx !== null && s.adx > 25,
    up_today: s => s.pct > 0,
    down_today: s => s.pct < 0
};

const SORTERS = {
    score: (a, b) => b.score - a.score || b.pct - a.pct,
    pct_desc: (a, b) => b.pct - a.pct,
    pct_asc: (a, b) => a.pct - b.pct,
    rsi_asc: (a, b) => (a.rsi ?? 999) - (b.rsi ?? 999),
    rsi_desc: (a, b) => (b.rsi ?? -1) - (a.rsi ?? -1),
    symbol: (a, b) => a.symbol.localeCompare(b.symbol)
};

const CELL = {
    big_candle: { bull: ['badge-bull', '▲ Big Bull'], bear: ['badge-bear', '▼ Big Bear'], normal: ['text-muted', 'Normal'] },
    macd: { bull: ['badge-bull', '▲ Bullish'], bear: ['badge-bear', '▼ Bearish'] },
    dow: { buy: ['badge-buy', 'BUY'], sell: ['badge-sell', 'SELL'], wait: ['text-muted', 'WAIT'] },
    ema: { golden: ['badge-golden', 'Golden'], death: ['badge-death', 'Death'] },
    bb: { up: ['badge-bull', '▲ Up'], down: ['badge-bear', '▼ Down'] },
    dmi: { bull: ['badge-bull', 'Bullish Cross'], bear: ['badge-bear', 'Bearish Cross'] }
};

function cell(field, value) {
    const map = CELL[field];
    if (!map || value === null || !(value in map)) return '-';
    const [cls, text] = map[value];
    return `<span class="${cls}">${text}</span>`;
}

function scorePill(score) {
    const cls = score >= 4 ? 'score-strong-bull'
        : score >= 1 ? 'score-bull'
            : score <= -4 ? 'score-strong-bear'
                : score <= -1 ? 'score-bear' : 'score-neutral';
    return `<span class="score-pill ${cls}">${score > 0 ? '+' : ''}${score}</span>`;
}

function activeFilters() {
    return [...document.querySelectorAll('[data-f]')].filter(c => c.checked).map(c => c.dataset.f);
}

function currentResults() {
    const filters = activeFilters();
    const mode = document.getElementById('matchSelect').value;
    const needle = document.getElementById('symbolSearch').value.trim().toUpperCase();

    let rows = allStocks.filter(s => {
        if (needle && !s.symbol.includes(needle)) return false;
        if (!filters.length) return true;
        return mode === 'all'
            ? filters.every(f => PREDICATES[f](s))
            : filters.some(f => PREDICATES[f](s));
    });

    return rows.sort(SORTERS[document.getElementById('sortSelect').value] || SORTERS.score);
}

function applyFilters() {
    document.querySelectorAll('.filter-chip').forEach(chip => {
        const box = chip.querySelector('input');
        if (box) chip.classList.toggle('active', box.checked);
    });

    const rows = currentResults();
    const body = document.getElementById('screenerBody');
    document.getElementById('resultCount').innerText = `— ${rows.length} of ${allStocks.length}`;

    if (!rows.length) {
        body.innerHTML = `<tr><td colspan="11" class="empty-state">No stock matches these filters right now. Try "Any selected filter" or clear a few chips.</td></tr>`;
        return;
    }

    body.innerHTML = rows.map(s => {
        const pctClass = s.pct >= 0 ? 'text-success' : 'text-danger';
        const sign = s.pct >= 0 ? '+' : '';
        return `<tr>
            <td class="symbol-col">
                <div class="d-flex justify-content-between align-items-center gap-2">
                    <span class="symbol-link" onclick="openTradingView('${s.symbol}')">${s.symbol}</span>
                    <span class="fw-bold text-success" style="font-size:0.8rem;">₹${s.price}</span>
                </div>
                <div style="font-size:0.72rem;" class="${pctClass} fw-bold">Daily: ${sign}${s.pct}%</div>
            </td>
            <td data-label="Score">${scorePill(s.score)}</td>
            <td data-label="Big Candle">${cell('big_candle', s.big_candle)}</td>
            <td data-label="MACD">${cell('macd', s.macd)}</td>
            <td data-label="DOW">${cell('dow', s.dow)}</td>
            <td data-label="EMA">${cell('ema', s.ema)}</td>
            <td data-label="Bollinger">${cell('bb', s.bb)}</td>
            <td data-label="RSI">${s.rsi ?? '-'}</td>
            <td data-label="DMI">${cell('dmi', s.dmi)}</td>
            <td data-label="ADX">${s.adx ?? '-'}</td>
            <td class="chart-col">
                <select class="chart-select" onchange="openChart(this, '${s.symbol}')">
                    <option value="" selected disabled>Select Chart</option>
                    <option value="tradingview">TradingView</option>
                    <option value="groww">Groww Chart</option>
                </select>
            </td>
        </tr>`;
    }).join('');
}

function clearFilters() {
    document.querySelectorAll('[data-f]').forEach(c => { c.checked = false; });
    document.getElementById('symbolSearch').value = '';
    applyFilters();
}

function downloadResults() {
    const rows = currentResults();
    const cols = ['symbol', 'price', 'pct', 'score', 'big_candle', 'macd', 'dow', 'ema', 'bb', 'rsi', 'dmi', 'adx'];
    const csv = [cols.join(',')]
        .concat(rows.map(r => cols.map(c => r[c] === null ? '' : r[c]).join(',')))
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
        noteUpdatedAt(data.updated_at);

        if (!data.stocks.length && data.status === 'warming') {
            document.getElementById('screenerBody').innerHTML =
                `<tr><td colspan="11" class="text-center text-muted loading-cell">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>`;
            setTimeout(loadStocks, 5000);
            return;
        }
        allStocks = data.stocks;
        applyFilters();
    } catch (e) {
        document.getElementById('screenerBody').innerHTML =
            `<tr><td colspan="11" class="empty-state">Could not load the scan. Retrying…</td></tr>`;
        setTimeout(loadStocks, 8000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    setInterval(loadStocks, 60000);
});
