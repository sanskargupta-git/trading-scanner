/* Options Lab: analytical strike ladder plus a validated P&L calculator.
   Every premium here is an estimate derived from spot, never an exchange quote. */

let currentSymbol = null;

function showError(id, message) {
    const el = document.getElementById(id);
    el.textContent = message;
    el.classList.toggle('show', Boolean(message));
}

/* ---------- Underlying ---------- */
async function loadUnderlying() {
    const raw = document.getElementById('underlying').value.trim().toUpperCase();
    if (!raw) return showError('underlyingError', 'Enter a symbol first.');
    if (!SYMBOL_PATTERN.test(raw)) return showError('underlyingError', 'That does not look like a valid symbol.');
    showError('underlyingError', '');

    const box = document.getElementById('chainBox');
    box.innerHTML = '<div class="loading-cell">Building ladder <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></div>';

    try {
        const res = await fetch(`/get_strike_chain?symbol=${encodeURIComponent(raw)}`);
        const data = await res.json();

        if (!res.ok || data.error) {
            box.innerHTML = `<div class="error-state">${escapeHtml(data.error || 'Could not load this symbol.')}</div>`;
            document.getElementById('spotPrice').innerText = '--';
            document.getElementById('spotChange').innerText = '--';
            return;
        }

        currentSymbol = data.symbol;
        document.getElementById('spotPrice').innerText = `₹${fmt(data.current_price)}`;
        document.getElementById('lotSizeView').innerText = data.lot_size;
        document.getElementById('lotSize').value = data.lot_size;

        // Daily move comes from the same snapshot the rest of the terminal uses.
        try {
            const st = await (await fetch(`/get_status_bulk?symbols=${encodeURIComponent(currentSymbol)}`)).json();
            const s = st[currentSymbol];
            const el = document.getElementById('spotChange');
            if (s && s.available) {
                el.innerHTML = `<span class="${pctClass(s.daily_change)}">${fmtPct(s.daily_change)} today</span>`;
            } else {
                el.innerText = 'Daily move unavailable';
            }
        } catch (e) { /* leave the note as-is */ }

        renderChain(data);
        calculate();
    } catch (e) {
        box.innerHTML = '<div class="error-state">Could not reach the server.</div>';
    }
}

function renderChain(data) {
    const rows = data.chain.map(r => `
        <tr class="chain-row ${r.is_atm ? 'atm-row' : ''}">
            <td><span class="call-btn" onclick="pickStrike(${r.strike}, 'CE', ${r.ce_price})">${r.ce_price}</span></td>
            <td><b class="mono">${r.strike}</b>${r.is_atm ? ' <span class="text-warning" style="font-size:.68rem">ATM</span>' : ''}</td>
            <td><span class="put-btn" onclick="pickStrike(${r.strike}, 'PE', ${r.pe_price})">${r.pe_price}</span></td>
        </tr>`).join('');

    document.getElementById('chainBox').innerHTML = `
        <table class="chain-table">
            <thead><tr><th>CE est. ₹</th><th>Strike · spot ₹${fmt(data.current_price)}</th><th>PE est. ₹</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

function pickStrike(strike, type, premium) {
    document.getElementById('contractName').value = `${currentSymbol} ${strike} ${type} (estimated)`;
    document.getElementById('entryPrice').value = premium;
    calculate();
}

/* ---------- P&L ---------- */
function calculate() {
    const side = document.getElementById('side').value;
    const lotSize = parseInt(document.getElementById('lotSize').value, 10);
    const lots = parseInt(document.getElementById('qtyLots').value, 10);
    const entry = parseFloat(document.getElementById('entryPrice').value);
    const exit = parseFloat(document.getElementById('exitPrice').value);

    const set = (id, text, cls) => {
        const el = document.getElementById(id);
        el.innerText = text;
        if (cls !== undefined) el.className = el.className.replace(/\b(text-success|text-danger|text-muted)\b/g, '') + ' ' + cls;
    };

    if (!Number.isFinite(lotSize) || lotSize < 1) return showError('calcError', 'Lot size must be a positive whole number.');
    if (!Number.isFinite(lots) || lots < 1) return showError('calcError', 'Quantity must be at least 1 lot.');
    if (Number.isFinite(entry) && entry < 0) return showError('calcError', 'Entry premium cannot be negative.');
    if (Number.isFinite(exit) && exit < 0) return showError('calcError', 'Exit premium cannot be negative.');
    showError('calcError', '');

    const qty = lotSize * lots;
    set('totalQty', qty.toLocaleString('en-IN'));

    if (!Number.isFinite(entry)) {
        set('capital', '--'); set('pnl', '--', 'text-muted'); set('pnlPct', '--');
        return;
    }

    const capital = entry * qty;
    document.getElementById('capital').innerText = `₹${capital.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    document.getElementById('capitalNote').innerText =
        side === 'BUY' ? 'premium paid' : 'premium received (margin will differ)';

    if (!Number.isFinite(exit)) {
        set('pnl', '--', 'text-muted'); set('pnlPct', '--');
        return;
    }

    // Long profits when the premium rises; short profits when it falls.
    const pnl = (side === 'BUY' ? (exit - entry) : (entry - exit)) * qty;
    const pct = capital > 0 ? (pnl / capital) * 100 : 0;
    const cls = pnl >= 0 ? 'text-success' : 'text-danger';

    const pnlEl = document.getElementById('pnl');
    pnlEl.className = `pnl-value mono ${cls}`;
    pnlEl.innerText = `${pnl >= 0 ? '+' : '-'}₹${Math.abs(pnl).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;

    const pctEl = document.getElementById('pnlPct');
    pctEl.className = `stat-value mono ${cls}`;
    pctEl.innerText = `${pnl >= 0 ? '+' : ''}${pct.toFixed(2)}%`;
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const preset = (params.get('symbol') || '').toUpperCase();
    if (preset && SYMBOL_PATTERN.test(preset)) document.getElementById('underlying').value = preset;
    loadUnderlying();
});
