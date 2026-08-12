/* Shared behaviour for every page: theme, clocks, currency, chart links,
   the data-freshness badge and the Gemini assistant. */

function isMobile() {
    return window.matchMedia('(max-width: 900px)').matches;
}

function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* ---------- Theme ---------- */
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('app_theme', next);
    updateThemeButton(next);
    if (window.onThemeChange) window.onThemeChange(next);
}

function updateThemeButton(theme) {
    const icon = document.getElementById('themeIcon');
    const text = document.getElementById('themeText');
    if (!icon || !text) return;
    icon.innerText = theme === 'dark' ? '🌙' : '☀️';
    text.innerText = theme === 'dark' ? 'Dark' : 'Light';
}

/* ---------- Clocks and currency ---------- */
const CLOCKS = [
    ['inClock', 'inDate', 'Asia/Kolkata'],
    ['usClock', 'usDate', 'America/New_York'],
    ['cnClock', 'cnDate', 'Asia/Shanghai'],
    ['ruClock', 'ruDate', 'Europe/Moscow'],
    ['caClock', 'caDate', 'America/Toronto']
];

function tickClocks() {
    const now = new Date();
    const head = document.getElementById('liveClockDisplay');
    if (head) {
        head.innerText = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    }
    CLOCKS.forEach(([clockId, dateId, tz]) => {
        const c = document.getElementById(clockId);
        const d = document.getElementById(dateId);
        if (c) c.innerText = now.toLocaleTimeString('en-US', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        if (d) d.innerText = now.toLocaleDateString('en-GB', { timeZone: tz, weekday: 'short', month: 'short', day: 'numeric' });
    });
}

function openGlobalModal() {
    new bootstrap.Modal(document.getElementById('globalModal')).show();
}

async function fetchCurrencies() {
    try {
        const data = await (await fetch('/get_currency_rate')).json();
        const set = (id, text) => { const el = document.getElementById(id); if (el) el.innerText = text; };
        if (data.inr) { set('usdInrDisplay', `USD/INR: ₹${data.inr}`); set('inCurr', `USD/INR: ₹${data.inr}`); }
        if (data.cny) set('cnCurr', `USD/CNY: ¥${data.cny}`);
        if (data.rub) set('ruCurr', `USD/RUB: ₽${data.rub}`);
        if (data.cad) set('caCurr', `USD/CAD: $${data.cad}`);
    } catch (e) { /* the badge keeps its last value */ }
}

/* ---------- Data freshness ---------- */
let lastUpdatedAt = 0;

function noteUpdatedAt(epochSeconds) {
    if (epochSeconds) lastUpdatedAt = epochSeconds;
}

function renderDataAge() {
    const badge = document.getElementById('dataAgeBadge');
    if (!badge) return;
    if (!lastUpdatedAt) { badge.innerText = 'loading…'; return; }
    const age = Math.max(0, Math.round(Date.now() / 1000 - lastUpdatedAt));
    badge.innerText = age < 60 ? `updated ${age}s ago` : `updated ${Math.floor(age / 60)}m ago`;
    badge.classList.toggle('stale', age > 240);
}

/* ---------- Chart links ---------- */
function tvSymbolFor(symbol) {
    const mcx = {
        GOLD: 'MCX:GOLD1!', GOLDM: 'MCX:GOLDM1!', SILVER: 'MCX:SILVER1!', SILVERM: 'MCX:SILVERM1!',
        CRUDEOIL: 'MCX:CRUDEOIL1!', CRUDEOILM: 'MCX:CRUDEOILM1!', NATURALGAS: 'MCX:NATURALGAS1!',
        COPPER: 'MCX:COPPER1!', NIFTY: 'NSE:NIFTY', BANKNIFTY: 'NSE:BANKNIFTY', USDINR: 'FX_IDC:USDINR'
    };
    return mcx[symbol] || `NSE:${symbol}`;
}

function openChart(selectElement, symbol) {
    const val = selectElement.value;
    if (!val) return;
    let url = '';
    if (val === 'tradingview') url = `https://in.tradingview.com/chart/?symbol=${tvSymbolFor(symbol)}`;
    else if (val === 'groww') url = `https://groww.in/stocks/nse-${symbol.toLowerCase()}`;
    if (url) window.open(url, '_blank');
    selectElement.value = '';
}

function openTradingView(symbol) {
    window.open(`https://in.tradingview.com/chart/?symbol=${tvSymbolFor(symbol)}`, '_blank');
}

/* Dashboard overrides this to also load the scan panel. */
function openIndicatorChart(symbol) {
    if (typeof window.scanStock === 'function') window.scanStock(symbol);
    openTradingView(symbol);
}

/* ---------- Gemini assistant ---------- */
function toggleGeminiChat() {
    const win = document.getElementById('geminiChatWindow');
    win.style.display = (win.style.display === 'flex') ? 'none' : 'flex';
}

function handleChatKey(e) {
    if (e.key === 'Enter') sendChatMessage();
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    const body = document.getElementById('chatBody');
    body.innerHTML += `<div class="chat-msg msg-user">${escapeHtml(text)}</div>`;
    input.value = '';
    body.scrollTop = body.scrollHeight;

    try {
        const data = await (await fetch(`/gemini_chat?message=${encodeURIComponent(text)}`)).json();
        body.innerHTML += `<div class="chat-msg msg-gemini">${escapeHtml(data.reply)}</div>`;
    } catch (err) {
        body.innerHTML += `<div class="chat-msg msg-gemini text-danger">Error connecting to assistant.</div>`;
    }
    body.scrollTop = body.scrollHeight;
}

/* ---------- Boot ---------- */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('app_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);

    tickClocks();
    fetchCurrencies();
    setInterval(tickClocks, 1000);
    setInterval(renderDataAge, 1000);
    setInterval(fetchCurrencies, 120000);
});
