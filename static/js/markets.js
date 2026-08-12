/* Markets: every segment rendered as a card grid from the cached snapshot. */

const SEGMENTS = ['nifty50', 'banknifty', 'finnifty', 'commodities', 'giftnifty'];
const FX_LABELS = { inr: ['USD / INR', '₹'], cny: ['USD / CNY', '¥'], rub: ['USD / RUB', '₽'], cad: ['USD / CAD', '$'] };

function marketCard(m, status) {
    return `<a class="mkt-card" href="/stock/${encodeURIComponent(m.symbol)}">
        <div class="d-flex justify-content-between align-items-center gap-2">
            <span class="mkt-sym">${escapeHtml(m.symbol)}</span>
            ${scorePill(m.score, m.band)}
        </div>
        <div class="mkt-price mono">₹${fmt(m.price)}</div>
        <div class="mkt-meta">
            <span class="${pctClass(m.pct)}">${fmtPct(m.pct)}</span>
            <span>1H ${escapeHtml(m.hourly_trend || '--')}</span>
        </div>
        <div class="mkt-meta"><span>${escapeHtml(status)}</span></div>
    </a>`;
}

async function loadIndices() {
    try {
        const data = await (await fetch('/api/indices')).json();
        applyMeta(data);

        document.getElementById('indexGrid').innerHTML = data.indices.map(ix => {
            const dir = ix.pct === null ? '' : (ix.pct >= 0 ? 'up' : 'down');
            return `<div class="index-card ${dir}">
                <div class="index-label">${escapeHtml(ix.label)}</div>
                <div class="index-price mono">${ix.price === null ? '--' : ix.price.toLocaleString('en-IN')}</div>
                <div class="index-change ${pctClass(ix.pct)}">${fmtPct(ix.pct)}</div>
            </div>`;
        }).join('');

        document.getElementById('fxGrid').innerHTML = Object.entries(FX_LABELS).map(([key, [label, sign]]) => `
            <div class="mkt-card" style="cursor:default">
                <div class="mkt-sym">${label}</div>
                <div class="mkt-price mono">${sign}${fmt(data.fx[key])}</div>
                <div class="mkt-meta"><span>Reference rate</span></div>
            </div>`).join('');
    } catch (e) {
        document.getElementById('indexGrid').innerHTML =
            '<div class="error-state" style="grid-column:1/-1">Could not load indices.</div>';
    }
}

async function loadSegment(key, status) {
    const grid = document.getElementById(`${key}Grid`);
    try {
        const data = await (await fetch(`/api/stocks?type=${key}`)).json();
        applyMeta(data);

        if (!data.stocks.length) {
            grid.innerHTML = data.status === 'warming'
                ? `<div class="loading-cell" style="grid-column:1/-1">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></div>`
                : `<div class="empty-state" style="grid-column:1/-1">Data unavailable for this segment.</div>`;
            if (data.status === 'warming') setTimeout(() => loadSegment(key, status), 5000);
            return;
        }

        const up = data.stocks.filter(s => (s.pct ?? 0) > 0).length;
        document.getElementById(`${key}Sub`).innerText =
            `${data.stocks.length} symbols · ${up} advancing`;
        grid.innerHTML = data.stocks.map(m => marketCard(m, status)).join('');
    } catch (e) {
        grid.innerHTML = '<div class="error-state" style="grid-column:1/-1">Could not load this segment.</div>';
    }
}

async function loadAll() {
    await loadIndices();
    const status = (META && META.market) ? META.market.label : 'Market status unknown';
    SEGMENTS.forEach(key => loadSegment(key, status));
}

document.addEventListener('DOMContentLoaded', () => {
    loadAll();
    setInterval(loadAll, 60000);
});
