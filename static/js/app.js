/* Shared behaviour for every page: theme, live status strip, global search,
   chart links and the AI assistant. */

const SYMBOL_PATTERN = /^[A-Z0-9&^.=\-]{1,20}$/;

function isMobile() { return window.matchMedia('(max-width: 860px)').matches; }

function escapeHtml(str) {
    return String(str ?? '').replace(/[&<>"']/g, c =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* Never print nan / undefined / null into the UI. */
function fmt(value, digits = 2, suffix = '') {
    if (value === null || value === undefined || value === '' || Number.isNaN(value)) return '--';
    if (typeof value === 'number') {
        if (!Number.isFinite(value)) return '--';
        return value.toFixed(digits) + suffix;
    }
    return escapeHtml(value) + suffix;
}

function fmtPct(value) {
    if (value === null || value === undefined || !Number.isFinite(value)) return '--';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

function pctClass(value) {
    if (value === null || value === undefined || !Number.isFinite(value)) return 'text-muted';
    return value >= 0 ? 'text-success' : 'text-danger';
}

const BAND_CLASS = {
    'strong-bull': 'score-strong-bull', 'bull': 'score-bull', 'neutral': 'score-neutral',
    'bear': 'score-bear', 'strong-bear': 'score-strong-bear'
};

function scorePill(score, band) {
    if (score === null || score === undefined) return '<span class="text-muted">--</span>';
    const cls = BAND_CLASS[band?.key] || 'score-neutral';
    return `<span class="score-pill ${cls}" title="${escapeHtml(band?.label || '')}">${score > 0 ? '+' : ''}${score}</span>`;
}

const CELL_MAP = {
    big_candle: { bull: ['badge-bull', '▲ Big Bull'], bear: ['badge-bear', '▼ Big Bear'], normal: ['text-muted', 'Normal'] },
    macd: { bull: ['badge-bull', '▲ Bullish'], bear: ['badge-bear', '▼ Bearish'] },
    dow: { buy: ['badge-buy', 'BUY'], sell: ['badge-sell', 'SELL'], wait: ['text-muted', 'WAIT'] },
    ema: { golden: ['badge-golden', 'Golden'], death: ['badge-death', 'Death'] },
    bb: { up: ['badge-bull', '▲ Up'], down: ['badge-bear', '▼ Down'] },
    rsi_trend: { up: ['badge-bull', 'Uptick'], down: ['badge-bear', 'Downtick'], flat: ['text-warning', 'Flat'] },
    dmi: { bull: ['badge-bull', 'Bullish Cross'], bear: ['badge-bear', 'Bearish Cross'] },
    adx_trend: { up: ['badge-bull', 'Uptick'], down: ['badge-bear', 'Downtick'], flat: ['text-warning', 'Flat'] }
};

function cell(field, value) {
    const map = CELL_MAP[field];
    if (!map || value === null || value === undefined || !(value in map)) return '<span class="text-muted">--</span>';
    const [cls, text] = map[value];
    return `<span class="${cls}">${text}</span>`;
}

/* ---------- Theme ---------- */
function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('app_theme', next);
    updateThemeButton(next);
    if (window.onThemeChange) window.onThemeChange(next);
}

function updateThemeButton(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) icon.innerText = theme === 'dark' ? '🌙' : '☀️';
}

/* ---------- Live status strip ---------- */
let META = null;
let metaFetchedAtMs = 0;

function applyMeta(meta) {
    if (!meta) return;
    META = meta;
    metaFetchedAtMs = Date.now();
    renderStatusStrip();
}

function renderStatusStrip() {
    if (!META) return;

    const dot = document.getElementById('statusDot');
    const state = document.getElementById('marketState');
    const detail = document.getElementById('marketDetail');
    const mkt = META.market || {};

    if (dot) dot.className = 'dot ' + (META.stale ? 'stale' : (mkt.state || 'closed').toLowerCase());
    if (state) state.innerText = mkt.label || '--';
    if (detail) detail.innerText = mkt.detail ? `· ${mkt.detail}` : '';

    // Age advances between polls so the strip never looks frozen.
    const drift = (Date.now() - metaFetchedAtMs) / 1000;
    const age = META.age_seconds === null || META.age_seconds === undefined ? null : META.age_seconds + drift;

    const updated = document.getElementById('lastUpdated');
    if (updated) {
        updated.innerText = META.updated_at
            ? new Date(META.updated_at * 1000).toLocaleTimeString('en-GB', { timeZone: 'Asia/Kolkata', hour12: false })
            : '--:--:--';
    }

    const ageEl = document.getElementById('dataAge');
    if (ageEl) ageEl.innerText = age === null ? '--' : `${Math.max(0, Math.round(age))}s`;

    const nextEl = document.getElementById('nextRefresh');
    if (nextEl) {
        const next = age === null ? null : Math.max(0, Math.round((META.refresh_seconds || 90) - age));
        nextEl.innerText = next === null ? '--' : (next === 0 ? 'updating…' : `${next}s`);
    }

    const banner = document.getElementById('staleBanner');
    if (banner) {
        if (META.stale && META.message) {
            banner.textContent = `⚠ ${META.message}`;
            banner.hidden = false;
        } else if (META.status === 'warming') {
            banner.textContent = '⟳ Updating market data…';
            banner.hidden = false;
        } else {
            banner.hidden = true;
        }
    }
}

async function refreshMeta() {
    try {
        applyMeta(await (await fetch('/api/meta')).json());
    } catch (e) { /* keep the last known status */ }
}

async function fetchCurrencies() {
    try {
        const fx = await (await fetch('/get_currency_rate')).json();
        const el = document.getElementById('fxStrip');
        if (el && fx.inr) el.innerHTML = `USD/INR <b class="mono">₹${fx.inr}</b>`;
    } catch (e) { /* leave the placeholder */ }
}

/* ---------- Chart / navigation helpers ---------- */
function tvSymbolFor(symbol) {
    const map = {
        GOLD: 'MCX:GOLD1!', GOLDM: 'MCX:GOLDM1!', SILVER: 'MCX:SILVER1!', SILVERM: 'MCX:SILVERM1!',
        CRUDEOIL: 'MCX:CRUDEOIL1!', CRUDEOILM: 'MCX:CRUDEOILM1!', NATURALGAS: 'MCX:NATURALGAS1!',
        COPPER: 'MCX:COPPER1!', NIFTY: 'NSE:NIFTY', BANKNIFTY: 'NSE:BANKNIFTY', USDINR: 'FX_IDC:USDINR'
    };
    return map[symbol] || `NSE:${symbol}`;
}

function openStock(symbol) {
    if (!SYMBOL_PATTERN.test(symbol)) return;
    window.location.href = `/stock/${encodeURIComponent(symbol)}`;
}

function openTradingView(symbol) {
    window.open(`https://in.tradingview.com/chart/?symbol=${tvSymbolFor(symbol)}`, '_blank', 'noopener');
}

function openChart(selectElement, symbol) {
    const val = selectElement.value;
    selectElement.value = '';
    if (!val) return;
    if (val === 'analysis') return openStock(symbol);
    if (val === 'tradingview') return openTradingView(symbol);
    if (val === 'groww') window.open(`https://groww.in/stocks/nse-${symbol.toLowerCase()}`, '_blank', 'noopener');
}

/* ---------- Global search ---------- */
let searchTimer = null;
let searchIndex = -1;

function initSearch() {
    const input = document.getElementById('globalSearch');
    const box = document.getElementById('searchResults');
    if (!input || !box) return;

    const close = () => { box.classList.remove('show'); input.setAttribute('aria-expanded', 'false'); searchIndex = -1; };

    input.addEventListener('input', () => {
        clearTimeout(searchTimer);
        const q = input.value.trim();
        if (!q) return close();
        searchTimer = setTimeout(async () => {
            try {
                const data = await (await fetch(`/api/search?q=${encodeURIComponent(q)}`)).json();
                if (!data.results.length) {
                    box.innerHTML = `<div class="search-empty">No matching symbol in the scanner.</div>`;
                } else {
                    box.innerHTML = data.results.map((r, i) =>
                        `<div class="search-item" role="option" data-sym="${escapeHtml(r.symbol)}" data-i="${i}">
                            <b>${escapeHtml(r.symbol)}</b><span class="search-kind">${escapeHtml(r.kind)}</span>
                        </div>`).join('');
                    box.querySelectorAll('.search-item').forEach(el =>
                        el.addEventListener('click', () => openStock(el.dataset.sym)));
                }
                box.classList.add('show');
                input.setAttribute('aria-expanded', 'true');
                searchIndex = -1;
            } catch (e) { close(); }
        }, 160);
    });

    input.addEventListener('keydown', e => {
        const items = [...box.querySelectorAll('.search-item')];
        if (e.key === 'Escape') return close();
        if (!items.length) {
            // Allow a direct jump when the typed symbol is already valid.
            if (e.key === 'Enter' && SYMBOL_PATTERN.test(input.value.trim().toUpperCase())) {
                openStock(input.value.trim().toUpperCase());
            }
            return;
        }
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            searchIndex = e.key === 'ArrowDown'
                ? (searchIndex + 1) % items.length
                : (searchIndex - 1 + items.length) % items.length;
            items.forEach((el, i) => el.classList.toggle('active', i === searchIndex));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            openStock(items[Math.max(0, searchIndex)].dataset.sym);
        }
    });

    document.addEventListener('click', e => {
        if (!input.contains(e.target) && !box.contains(e.target)) close();
    });
}

/* ---------- AI assistant ---------- */
function toggleGeminiChat() {
    const win = document.getElementById('geminiChatWindow');
    win.style.display = (win.style.display === 'flex') ? 'none' : 'flex';
    if (win.style.display === 'flex') document.getElementById('chatInput').focus();
}

function handleChatKey(e) { if (e.key === 'Enter') sendChatMessage(); }

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    const body = document.getElementById('chatBody');
    body.innerHTML += `<div class="chat-msg msg-user">${escapeHtml(text)}</div>`;
    input.value = '';
    body.scrollTop = body.scrollHeight;

    const pending = document.createElement('div');
    pending.className = 'chat-msg msg-gemini';
    pending.innerHTML = 'Thinking <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span>';
    body.appendChild(pending);
    body.scrollTop = body.scrollHeight;

    try {
        const data = await (await fetch(`/gemini_chat?message=${encodeURIComponent(text)}`)).json();
        pending.textContent = data.reply;
    } catch (err) {
        pending.className = 'chat-msg msg-gemini text-danger';
        pending.textContent = 'Could not reach the assistant. The scanner itself is unaffected.';
    }
    body.scrollTop = body.scrollHeight;
}

/* ---------- Boot ---------- */
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('app_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeButton(saved);

    initSearch();
    refreshMeta();
    fetchCurrencies();
    setInterval(renderStatusStrip, 1000);
    setInterval(refreshMeta, 15000);
    setInterval(fetchCurrencies, 120000);
});
