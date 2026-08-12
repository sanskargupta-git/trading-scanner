/* Heatmap: one tile per symbol, coloured by whichever metric is selected. */

let heatStocks = [];

/* Ramp between two RGB anchors; t is clamped to 0..1. */
function mix(from, to, t) {
    t = Math.max(0, Math.min(1, t));
    return `rgb(${from.map((c, i) => Math.round(c + (to[i] - c) * t)).join(',')})`;
}

const NEUTRAL = [42, 48, 60];
const GREEN = [24, 140, 86];
const RED = [176, 48, 56];
const AMBER = [168, 122, 26];

/* Daily moves mostly sit inside +/-3%, so that is the range worth resolving. */
const pctColour = p => (p ?? 0) >= 0 ? mix(NEUTRAL, GREEN, (p ?? 0) / 3) : mix(NEUTRAL, RED, -(p ?? 0) / 3);
const scoreColour = s => (s ?? 0) >= 0 ? mix(NEUTRAL, GREEN, (s ?? 0) / 5) : mix(NEUTRAL, RED, -(s ?? 0) / 5);

function rsiColour(rsi) {
    if (rsi === null || rsi === undefined) return `rgb(${NEUTRAL.join(',')})`;
    if (rsi > 70) return mix(AMBER, RED, (rsi - 70) / 30);
    if (rsi < 30) return mix(AMBER, GREEN, (30 - rsi) / 30);
    return mix(NEUTRAL, AMBER, Math.abs(rsi - 50) / 20);
}

function tileColour(m, mode) {
    if (mode === 'score') return scoreColour(m.score);
    if (mode === 'rsi') return rsiColour(m.rsi);
    return pctColour(m.pct);
}

function tileCaption(m, mode) {
    if (mode === 'score') return `${(m.score ?? 0) > 0 ? '+' : ''}${m.score ?? '--'}`;
    if (mode === 'rsi') return m.rsi === null || m.rsi === undefined ? '--' : m.rsi.toFixed(1);
    return fmtPct(m.pct);
}

const LEGENDS = {
    pct: [['-3%', pctColour(-3)], ['0%', pctColour(0)], ['+3%', pctColour(3)]],
    score: [['-5', scoreColour(-5)], ['0', scoreColour(0)], ['+5', scoreColour(5)]],
    rsi: [['<30 oversold', rsiColour(20)], ['50', rsiColour(50)], ['>70 overbought', rsiColour(80)]]
};

function renderHeatmap() {
    const mode = document.getElementById('colourSelect').value;

    document.getElementById('legendRow').innerHTML = LEGENDS[mode]
        .map(([label, colour]) => `<span><span class="legend-swatch" style="background:${colour}"></span> ${label}</span>`)
        .join('');

    const grid = document.getElementById('heatGrid');
    const summary = document.getElementById('heatSummary');

    if (!heatStocks.length) {
        grid.innerHTML = `<div class="empty-state"><span class="big">📭</span>No data available yet.</div>`;
        summary.innerHTML = '';
        return;
    }

    const up = heatStocks.filter(s => (s.pct ?? 0) > 0).length;
    const down = heatStocks.filter(s => (s.pct ?? 0) < 0).length;
    const avg = heatStocks.reduce((a, s) => a + (s.pct ?? 0), 0) / heatStocks.length;
    const bull = heatStocks.filter(s => (s.score ?? 0) > 0).length;

    summary.innerHTML = `
        <div class="stat-tile"><div class="stat-label">Advancing</div><div class="stat-value text-success">${up}</div></div>
        <div class="stat-tile"><div class="stat-label">Declining</div><div class="stat-value text-danger">${down}</div></div>
        <div class="stat-tile"><div class="stat-label">Unchanged</div><div class="stat-value">${heatStocks.length - up - down}</div></div>
        <div class="stat-tile"><div class="stat-label">Average Move</div>
            <div class="stat-value ${pctClass(avg)}">${fmtPct(avg)}</div></div>
        <div class="stat-tile"><div class="stat-label">Bullish Bias</div><div class="stat-value">${bull}/${heatStocks.length}</div></div>`;

    const sorted = [...heatStocks].sort((a, b) => (b.pct ?? 0) - (a.pct ?? 0));
    grid.innerHTML = sorted.map(m => `
        <a class="heat-tile" style="background:${tileColour(m, mode)}"
           href="/stock/${encodeURIComponent(m.symbol)}"
           title="${escapeHtml(m.symbol)} · ₹${fmt(m.price)} · ${fmtPct(m.pct)} · ${escapeHtml(m.band?.label || '')}">
            <div class="heat-sym">${escapeHtml(m.symbol)}</div>
            <div class="heat-pct">${tileCaption(m, mode)}</div>
            <div class="heat-price">₹${fmt(m.price)}</div>
            <div class="heat-bias">${escapeHtml(m.band?.label || '')}</div>
        </a>`).join('');
}

async function loadHeatmap() {
    const universe = document.getElementById('universeSelect').value;
    try {
        const data = await (await fetch(`/api/stocks?type=${universe}`)).json();
        applyMeta(data);
        if (!data.stocks.length && data.status === 'warming') {
            document.getElementById('heatGrid').innerHTML =
                `<div class="loading-cell">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></div>`;
            setTimeout(loadHeatmap, 5000);
            return;
        }
        heatStocks = data.stocks;
        renderHeatmap();
    } catch (e) {
        document.getElementById('heatGrid').innerHTML =
            `<div class="error-state">Could not load prices. Retrying…</div>`;
        setTimeout(loadHeatmap, 8000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadHeatmap();
    setInterval(loadHeatmap, 60000);
});
