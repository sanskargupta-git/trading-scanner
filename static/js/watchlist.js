/* Watchlist: persisted in localStorage, priced from the cached snapshot in one
   bulk request rather than one request per symbol. */

const DEFAULT_LIST = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN'];
let list = [];
let statuses = {};

function readWatchlist() {
    try {
        const raw = JSON.parse(localStorage.getItem('user_watchlist'));
        if (Array.isArray(raw)) return raw.filter(s => SYMBOL_PATTERN.test(s));
    } catch (e) { /* ignore malformed storage */ }
    return [...DEFAULT_LIST];
}

function save() {
    localStorage.setItem('user_watchlist', JSON.stringify(list));
}

function showError(message) {
    const el = document.getElementById('addError');
    el.textContent = message;
    el.classList.toggle('show', Boolean(message));
}

function addSymbol() {
    const input = document.getElementById('addSymbol');
    const val = input.value.trim().toUpperCase();

    if (!val) return showError('Enter a symbol first.');
    if (!SYMBOL_PATTERN.test(val)) return showError('Symbols use letters, digits and - & ^ . = only.');
    if (list.includes(val)) return showError(`${val} is already in your watchlist.`);
    if (list.length >= 60) return showError('Watchlist is limited to 60 symbols.');

    list.push(val);
    save();
    input.value = '';
    showError('');
    load();
}

function removeSymbol(sym) {
    list = list.filter(s => s !== sym);
    save();
    render();
}

function clearWatchlist() {
    list = [];
    save();
    render();
}

function resetWatchlist() {
    list = [...DEFAULT_LIST];
    save();
    load();
}

function render() {
    const needle = document.getElementById('wlSearch').value.trim().toUpperCase();
    const shown = list.filter(s => !needle || s.includes(needle));
    const grid = document.getElementById('wlGrid');
    document.getElementById('wlCount').innerText = `${shown.length} of ${list.length}`;

    if (!list.length) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><span class="big">⭐</span>
            Your watchlist is empty. Add a symbol above, or reset to the default list.</div>`;
        return;
    }
    if (!shown.length) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><span class="big">🔍</span>
            No saved symbol matches that filter.</div>`;
        return;
    }

    grid.innerHTML = shown.map(sym => {
        const s = statuses[sym];
        if (!s || !s.available) {
            return `<div class="wl-card">
                <button class="wl-remove" onclick="removeSymbol('${escapeHtml(sym)}')" aria-label="Remove ${escapeHtml(sym)}">✕</button>
                <a class="wl-sym" href="/stock/${encodeURIComponent(sym)}">${escapeHtml(sym)}</a>
                <div class="wl-price text-muted">--</div>
                <div class="mkt-meta"><span>Data unavailable</span></div>
            </div>`;
        }
        return `<div class="wl-card">
            <button class="wl-remove" onclick="removeSymbol('${escapeHtml(sym)}')" aria-label="Remove ${escapeHtml(sym)}">✕</button>
            <a class="wl-sym" href="/stock/${encodeURIComponent(sym)}">${escapeHtml(sym)}</a>
            <div class="wl-price mono">₹${fmt(s.price)}</div>
            <div class="mkt-meta">
                <span class="${pctClass(s.daily_change)}">${fmtPct(s.daily_change)}</span>
                <span>${scorePill(s.score, s.band)}</span>
            </div>
            <div class="mkt-meta">
                <span>Trend ${escapeHtml(s.trend)}</span>
                <span>1H ${escapeHtml(s.hourly_trend)}</span>
            </div>
        </div>`;
    }).join('');
}

async function load() {
    list = readWatchlist();
    if (!list.length) return render();
    try {
        const res = await fetch(`/get_status_bulk?symbols=${encodeURIComponent(list.join(','))}`);
        statuses = await res.json();
    } catch (e) {
        statuses = {};
    }
    render();
}

document.addEventListener('DOMContentLoaded', () => {
    load();
    setInterval(load, 60000);
});
