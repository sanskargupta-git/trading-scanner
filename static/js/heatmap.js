/* Heatmap: one tile per symbol, coloured by whichever metric is selected. */

let heatStocks = [];

/* Ramp between two RGB anchors. `t` is clamped to 0..1. */
function mix(from, to, t) {
    t = Math.max(0, Math.min(1, t));
    return `rgb(${from.map((c, i) => Math.round(c + (to[i] - c) * t)).join(',')})`;
}

const NEUTRAL = [51, 65, 85];
const GREEN = [16, 160, 96];
const RED = [200, 48, 48];
const AMBER = [190, 130, 20];

/* Daily moves are mostly inside +/-3%, so that is the range worth resolving. */
function pctColour(pct) {
    return pct >= 0 ? mix(NEUTRAL, GREEN, pct / 3) : mix(NEUTRAL, RED, -pct / 3);
}

function scoreColour(score) {
    return score >= 0 ? mix(NEUTRAL, GREEN, score / 5) : mix(NEUTRAL, RED, -score / 5);
}

function rsiColour(rsi) {
    if (rsi === null) return `rgb(${NEUTRAL.join(',')})`;
    if (rsi > 70) return mix(AMBER, RED, (rsi - 70) / 30);      // overbought
    if (rsi < 30) return mix(AMBER, GREEN, (30 - rsi) / 30);    // oversold
    return mix(NEUTRAL, AMBER, Math.abs(rsi - 50) / 20);
}

function tileColour(stock, mode) {
    if (mode === 'score') return scoreColour(stock.score);
    if (mode === 'rsi') return rsiColour(stock.rsi);
    return pctColour(stock.pct);
}

function tileCaption(stock, mode) {
    if (mode === 'score') return `${stock.score > 0 ? '+' : ''}${stock.score} signals`;
    if (mode === 'rsi') return stock.rsi === null ? 'RSI --' : `RSI ${stock.rsi}`;
    return `${stock.pct >= 0 ? '+' : ''}${stock.pct}%`;
}

const LEGENDS = {
    pct: [['-3%', pctColour(-3)], ['0%', pctColour(0)], ['+3%', pctColour(3)]],
    score: [['-5', scoreColour(-5)], ['0', scoreColour(0)], ['+5', scoreColour(5)]],
    rsi: [['<30 oversold', rsiColour(20)], ['50', rsiColour(50)], ['>70 overbought', rsiColour(80)]]
};

function renderLegend(mode) {
    document.getElementById('legendRow').innerHTML = LEGENDS[mode]
        .map(([label, colour]) => `<span><span class="legend-swatch" style="background:${colour}"></span> ${label}</span>`)
        .join('');
}

function renderSummary() {
    const up = heatStocks.filter(s => s.pct > 0).length;
    const down = heatStocks.filter(s => s.pct < 0).length;
    const flat = heatStocks.length - up - down;
    const avg = heatStocks.length
        ? (heatStocks.reduce((a, s) => a + s.pct, 0) / heatStocks.length).toFixed(2)
        : '0.00';
    const avgClass = avg >= 0 ? 'text-success' : 'text-danger';

    document.getElementById('marketSummary').innerHTML =
        `🟢 <b>${up}</b> advancing &nbsp;·&nbsp; 🔴 <b>${down}</b> declining &nbsp;·&nbsp; ⚪ <b>${flat}</b> flat ` +
        `&nbsp;·&nbsp; average move <b class="${avgClass}">${avg >= 0 ? '+' : ''}${avg}%</b>`;
}

function renderHeatmap() {
    const mode = document.getElementById('colourSelect').value;
    renderLegend(mode);
    renderSummary();

    const grid = document.getElementById('heatGrid');
    if (!heatStocks.length) {
        grid.innerHTML = `<div class="empty-state">No data available yet.</div>`;
        return;
    }

    const sorted = [...heatStocks].sort((a, b) => b.pct - a.pct);
    grid.innerHTML = sorted.map(s => `
        <div class="heat-tile" style="background:${tileColour(s, mode)}"
             onclick="openTradingView('${s.symbol}')" title="${s.symbol} · ₹${s.price} · ${s.pct}%">
            <div class="heat-sym">${s.symbol}</div>
            <div class="heat-pct">${tileCaption(s, mode)}</div>
            <div class="heat-price">₹${s.price}</div>
        </div>`).join('');
}

async function loadHeatmap() {
    const universe = document.getElementById('universeSelect').value;
    try {
        const data = await (await fetch(`/api/stocks?type=${universe}`)).json();
        noteUpdatedAt(data.updated_at);

        if (!data.stocks.length && data.status === 'warming') {
            document.getElementById('heatGrid').innerHTML =
                `<div class="text-muted loading-cell">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></div>`;
            setTimeout(loadHeatmap, 5000);
            return;
        }
        heatStocks = data.stocks;
        renderHeatmap();
    } catch (e) {
        document.getElementById('heatGrid').innerHTML = `<div class="empty-state">Could not load prices. Retrying…</div>`;
        setTimeout(loadHeatmap, 8000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadHeatmap();
    setInterval(loadHeatmap, 60000);
});
