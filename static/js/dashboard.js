/* Dashboard: index cards, market pulse, top setups, watchlist and the segment tables. */

const TABLES = [
    { type: 'nifty50', dom: 'nifty' },
    { type: 'banknifty', dom: 'bankNifty' },
    { type: 'finnifty', dom: 'finNifty' },
    { type: 'commodities', dom: 'commodities' },
    { type: 'giftnifty', dom: 'giftNifty' }
];

let warmupRetry = null;

function toggleTable(wrapId, caretId) {
    const wrap = document.getElementById(wrapId);
    const caret = document.getElementById(caretId);
    const hidden = wrap.style.display === 'none';
    wrap.style.display = hidden ? 'block' : 'none';
    caret.classList.toggle('closed', !hidden);
}

function filterTable(query) {
    const needle = query.trim().toUpperCase();
    document.querySelectorAll('#niftyBody tr').forEach(row => {
        const link = row.querySelector('.symbol-link');
        if (!link) return;
        row.classList.toggle('filtered-out', needle !== '' && !link.textContent.includes(needle));
    });
}

/* ---------- Index cards ---------- */
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
    } catch (e) { /* cards keep their skeletons */ }
}

/* ---------- Market pulse and setups ---------- */
function setupRow(s) {
    return `<a class="setup-row" href="/stock/${encodeURIComponent(s.symbol)}">
        <div>
            <div class="setup-sym">${escapeHtml(s.symbol)}</div>
            <div class="setup-meta">RSI ${fmt(s.rsi, 1)} · ADX ${fmt(s.adx, 1)}</div>
        </div>
        <div class="mono ${pctClass(s.pct)}" style="font-weight:700">${fmtPct(s.pct)}</div>
        <div>${scorePill(s.score, s.band)}</div>
    </a>`;
}

async function loadPulse() {
    try {
        const d = await (await fetch('/api/pulse')).json();
        applyMeta(d);

        if (!d.ready) {
            if (warmupRetry) clearTimeout(warmupRetry);
            warmupRetry = setTimeout(loadPulse, 5000);
            return;
        }

        document.getElementById('pulseGrid').innerHTML = `
            <div class="stat-tile"><div class="stat-label">Bullish</div>
                <div class="stat-value text-success">${d.bullish}</div>
                <div class="stat-note">${d.advancing} advancing</div></div>
            <div class="stat-tile"><div class="stat-label">Bearish</div>
                <div class="stat-value text-danger">${d.bearish}</div>
                <div class="stat-note">${d.declining} declining</div></div>
            <div class="stat-tile"><div class="stat-label">Neutral</div>
                <div class="stat-value">${d.neutral}</div>
                <div class="stat-note">score 0</div></div>
            <div class="stat-tile"><div class="stat-label">Top Gainer</div>
                <div class="stat-value text-success">${escapeHtml(d.top_gainer.symbol)}</div>
                <div class="stat-note">${fmtPct(d.top_gainer.pct)} · ₹${fmt(d.top_gainer.price)}</div></div>
            <div class="stat-tile"><div class="stat-label">Top Loser</div>
                <div class="stat-value text-danger">${escapeHtml(d.top_loser.symbol)}</div>
                <div class="stat-note">${fmtPct(d.top_loser.pct)} · ₹${fmt(d.top_loser.price)}</div></div>`;

        document.getElementById('topBullish').innerHTML =
            d.top_bullish.length ? d.top_bullish.map(setupRow).join('')
                : '<div class="empty-state">No bullish setups right now.</div>';
        document.getElementById('topBearish').innerHTML =
            d.top_bearish.length ? d.top_bearish.map(setupRow).join('')
                : '<div class="empty-state">No bearish setups right now.</div>';
    } catch (e) { /* keep previous values */ }
}

/* ---------- Watchlist strip ---------- */
function readWatchlist() {
    try {
        const raw = JSON.parse(localStorage.getItem('user_watchlist'));
        if (Array.isArray(raw) && raw.length) return raw;
    } catch (e) { /* fall through to the default */ }
    return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN'];
}

async function loadWatchlist() {
    const list = readWatchlist().slice(0, 12);
    const grid = document.getElementById('dashWatchlist');
    try {
        const data = await (await fetch(`/get_status_bulk?symbols=${encodeURIComponent(list.join(','))}`)).json();
        grid.innerHTML = list.map(sym => {
            const s = data[sym] || { available: false };
            if (!s.available) {
                return `<div class="wl-card"><a class="wl-sym" href="/stock/${encodeURIComponent(sym)}">${escapeHtml(sym)}</a>
                    <div class="wl-price text-muted">--</div>
                    <div class="mkt-meta"><span>Data unavailable</span></div></div>`;
            }
            return `<div class="wl-card">
                <a class="wl-sym" href="/stock/${encodeURIComponent(sym)}">${escapeHtml(sym)}</a>
                <div class="wl-price mono">₹${fmt(s.price)}</div>
                <div class="mkt-meta">
                    <span class="${pctClass(s.daily_change)}">${fmtPct(s.daily_change)}</span>
                    <span>${scorePill(s.score, s.band)}</span>
                </div></div>`;
        }).join('');
    } catch (e) {
        grid.innerHTML = '<div class="error-state">Could not load the watchlist.</div>';
    }
}

/* ---------- Segment tables ---------- */
async function loadTables() {
    let warming = false;

    for (const t of TABLES) {
        try {
            const data = await (await fetch(`/get_master_table_data?type=${t.type}`)).json();
            applyMeta(data);
            const body = document.getElementById(`${t.dom}Body`);
            const stats = document.getElementById(`${t.dom}Stats`);

            if (data.rows && data.rows.length) {
                body.innerHTML = data.rows.join('');
                if (stats && data.stats) {
                    stats.innerHTML = `${data.stats.up_count} bullish · ${data.stats.down_count} bearish`;
                }
            } else if (data.status === 'warming') {
                warming = true;
                body.innerHTML = `<tr><td colspan="12" class="loading-cell">${escapeHtml(data.message)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>`;
            } else {
                body.innerHTML = `<tr><td colspan="12" class="empty-state"><span class="big">📭</span>Data unavailable for this segment.</td></tr>`;
            }
        } catch (e) { /* keep whatever the table already shows */ }
    }

    // The first request after a cold start lands while the background refresh is
    // still running; poll quickly until it finishes instead of waiting a full minute.
    if (warming) {
        if (warmupRetry) clearTimeout(warmupRetry);
        warmupRetry = setTimeout(loadAll, 5000);
    }

    const search = document.getElementById('tableSearch');
    if (search && search.value) filterTable(search.value);
}

function loadAll() {
    loadIndices();
    loadPulse();
    loadWatchlist();
    loadTables();
}

document.addEventListener('DOMContentLoaded', () => {
    loadAll();
    setInterval(loadAll, 60000);
});
