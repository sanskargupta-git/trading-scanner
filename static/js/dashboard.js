/* Dashboard page: watchlist drawer, five live tables, scan panel, option calculator. */

let watchlist = JSON.parse(localStorage.getItem('user_watchlist')) || window.DEFAULT_WATCHLIST || [];

const TABLE_TARGETS = [
    { type: 'nifty50', body: 'niftyTableBody', badge: 'niftyTableStatsBadge', label: 'Nifty 50' },
    { type: 'banknifty', body: 'bankNiftyTableBody', badge: 'bankNiftyTableStatsBadge', label: 'Bank Nifty' },
    { type: 'commodities', body: 'commoditiesTableBody', badge: 'commoditiesTableStatsBadge', label: 'Commodities' },
    { type: 'giftnifty', body: 'giftNiftyTableBody', badge: 'giftNiftyTableStatsBadge', label: 'Gift Nifty' },
    { type: 'finnifty', body: 'finNiftyTableBody', badge: 'finNiftyTableStatsBadge', label: 'Fin Nifty' }
];

let warmupRetry = null;

/* ---------- Sidebar drawer ---------- */
function closeMobileSidebar() {
    document.getElementById('sidebarContainer').classList.remove('mobile-open');
    document.getElementById('sidebarBackdrop').classList.remove('show');
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebarContainer');

    // On a phone the sidebar is an off-canvas drawer, not a shrinkable column.
    if (isMobile()) {
        const open = sidebar.classList.toggle('mobile-open');
        document.getElementById('sidebarBackdrop').classList.toggle('show', open);
        return;
    }

    sidebar.classList.toggle('collapsed');
    document.getElementById('mainContentContainer').classList.toggle('expanded');
    document.querySelector('.sidebar-toggle-btn').innerHTML =
        sidebar.classList.contains('collapsed') ? '&raquo;' : '&laquo;';
}

window.addEventListener('resize', () => { if (!isMobile()) closeMobileSidebar(); });

function toggleTable(wrapperId, iconId) {
    const wrapper = document.getElementById(wrapperId);
    const icon = document.getElementById(iconId);
    const hidden = wrapper.style.display === 'none';
    wrapper.style.display = hidden ? 'block' : 'none';
    icon.innerText = hidden ? '▼' : '▶';
}

/* ---------- Tables ---------- */
function loadingRow(label) {
    return `<tr><td colspan="12" class="text-center text-muted loading-cell">${escapeHtml(label)} <span class="spinner-dot"></span><span class="spinner-dot"></span><span class="spinner-dot"></span></td></tr>`;
}

async function fetchAllTables() {
    let warming = false;

    for (const t of TABLE_TARGETS) {
        try {
            const data = await (await fetch(`/get_master_table_data?type=${t.type}`)).json();
            const body = document.getElementById(t.body);
            const badge = document.getElementById(t.badge);
            noteUpdatedAt(data.updated_at);

            if (data.rows && data.rows.length > 0) {
                body.innerHTML = data.rows.join('');
                if (badge && data.stats) {
                    badge.innerHTML = `(1H: 🟢 Up: ${data.stats.up_count} (${data.stats.up_pct}%) | 🔴 Down: ${data.stats.down_count} (${data.stats.down_pct}%))`;
                }
            } else if (data.status === 'warming') {
                warming = true;
                body.innerHTML = loadingRow(data.message || `Fetching ${t.label} live data`);
            } else {
                body.innerHTML = `<tr><td colspan="12" class="text-center text-muted loading-cell">${escapeHtml(data.message || 'No active data found.')}</td></tr>`;
            }
        } catch (e) { /* keep whatever the table already shows */ }
    }

    try {
        const data = await (await fetch('/get_movers')).json();
        if (data.movers && data.movers.length) renderTicker(data.movers);
    } catch (e) { /* ticker keeps its placeholder */ }

    // The first request after a cold start lands while the background refresh is
    // still running; poll quickly until it finishes instead of waiting a full minute.
    if (warmupRetry) clearTimeout(warmupRetry);
    if (warming) warmupRetry = setTimeout(fetchAllTables, 5000);

    const search = document.getElementById('tableSearch');
    if (search && search.value) filterNiftyTable(search.value);

    renderWatchlist();
}

function renderTicker(movers) {
    document.getElementById('tickerStrip').innerHTML = movers.map(mv => {
        if (mv.pct >= 0) {
            return `<div class="ticker-item" onclick="scanStock('${mv.symbol}')" title="Scan ${mv.symbol}">
                <span class="ticker-rocket rocket-bull">🚀</span>
                <span class="ticker-ribbon ribbon-bull">${mv.symbol} : +${mv.pct}% ▲</span></div>`;
        }
        return `<div class="ticker-item" onclick="scanStock('${mv.symbol}')" title="Scan ${mv.symbol}">
            <span class="ticker-ribbon ribbon-bear">${mv.symbol} : ${mv.pct}% ▼</span>
            <span class="ticker-rocket rocket-bear">🔻</span></div>`;
    }).join('');
}

function filterNiftyTable(query) {
    const needle = query.trim().toUpperCase();
    document.querySelectorAll('#niftyTableBody tr').forEach(row => {
        const link = row.querySelector('.symbol-link');
        if (!link) return;
        row.classList.toggle('filtered-out', needle !== '' && !link.innerText.includes(needle));
    });
}

/* ---------- Watchlist ---------- */
async function renderWatchlist() {
    const container = document.getElementById('watchlistContainer');
    if (!container) return;

    let statuses = {};
    try {
        statuses = await (await fetch(`/get_status_bulk?symbols=${encodeURIComponent(watchlist.join(','))}`)).json();
    } catch (e) { /* fall back to placeholder rows */ }

    container.innerHTML = '';
    for (const stock of watchlist) {
        const s = statuses[stock] || { trend: 'Sideways', daily_change: 0, hourly_trend: '--' };
        const trendHtml = s.trend === 'Bullish' ? '<span class="bull">▲ Bull</span>'
            : s.trend === 'Bearish' ? '<span class="bear">▼ Bear</span>'
                : '<span class="flat">▶ Flat</span>';
        const dailyClass = s.daily_change >= 0 ? 'text-success' : 'text-danger';
        const dailySign = s.daily_change >= 0 ? '+' : '';

        const div = document.createElement('div');
        div.className = 'watchlist-item';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b>${escapeHtml(stock)}</b>
                ${trendHtml}
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.75rem;">
                <span class="${dailyClass}">Daily: ${dailySign}${s.daily_change}%</span>
                <span class="text-info">1H: ${escapeHtml(s.hourly_trend)}</span>
            </div>`;
        div.onclick = () => {
            document.getElementById('stockSymbol').value = stock;
            scanStock(stock);
            loadOptionChainForStock(stock);
        };
        container.appendChild(div);
    }
}

function addToWatchlist() {
    const input = document.getElementById('newStockInput');
    const val = input.value.trim().toUpperCase();
    if (!val || !/^[A-Z0-9&.\-]{1,20}$/.test(val)) { alert('Enter a valid symbol, e.g. RELIANCE'); return; }
    if (!watchlist.includes(val)) {
        watchlist.push(val);
        localStorage.setItem('user_watchlist', JSON.stringify(watchlist));
        input.value = '';
        renderWatchlist();
    }
}

/* ---------- Option calculator ---------- */
function toggleOptionCalculator() {
    const body = document.getElementById('optionCalcBody');
    body.style.display = (body.style.display === 'none' || body.style.display === '') ? 'block' : 'none';
}

async function loadOptionChainForStock(stockSymbol) {
    document.getElementById('activeStockLabel').innerText = `Active: ${stockSymbol}`;
    document.getElementById('calcLot').value = (window.LOT_SIZES || {})[stockSymbol] || 25;

    const container = document.getElementById('chainTableContainer');
    container.style.display = 'block';
    container.innerHTML = `<div class='text-center fs-7 text-muted p-1'>Fetching Strikes...</div>`;

    try {
        const data = await (await fetch(`/get_strike_chain?symbol=${encodeURIComponent(stockSymbol)}`)).json();
        if (data.error) {
            container.innerHTML = `<div class='text-center text-danger fs-7 p-1'>${escapeHtml(data.error)}</div>`;
            return;
        }
        if (data.lot_size) document.getElementById('calcLot').value = data.lot_size;

        let html = `<table class="chain-table"><tr><th>CE (₹)</th><th>Strike (Spot: ₹${data.current_price})</th><th>PE (₹)</th></tr>`;
        data.chain.forEach(row => {
            const atm = row.is_atm ? 'atm-row' : '';
            const mark = row.is_atm ? ' 🎯' : '';
            html += `<tr class="chain-row ${atm}">
                <td><span class="call-btn" onclick="selectOption('${stockSymbol}', ${row.strike}, 'CE', ${row.ce_price})">${row.ce_price}</span></td>
                <td><b>${row.strike}${mark}</b></td>
                <td><span class="put-btn" onclick="selectOption('${stockSymbol}', ${row.strike}, 'PE', ${row.pe_price})">${row.pe_price}</span></td>
            </tr>`;
        });
        container.innerHTML = html + '</table>';
    } catch (e) {
        container.innerHTML = `<div class='text-center text-danger fs-7 p-1'>Could not load strikes.</div>`;
    }
}

function selectOption(symbol, strike, type, price) {
    document.getElementById('selectedOptionName').value = `${symbol} ${strike} ${type}`;
    document.getElementById('calcEntry').value = price;
}

function calculateOption() {
    const type = document.getElementById('calcType').value;
    const entry = parseFloat(document.getElementById('calcEntry').value);
    const lot = parseInt(document.getElementById('calcLot').value, 10);
    const points = parseFloat(document.getElementById('calcPoints').value);

    if (isNaN(entry) || isNaN(lot) || isNaN(points)) {
        alert('Please select a strike and fill live points!');
        return;
    }

    const totalInvested = entry * lot;
    const netProfit = (type === 'BUY') ? (points * lot) : (-points * lot);
    const colorClass = netProfit >= 0 ? 'text-success' : 'text-danger';
    const sign = netProfit >= 0 ? '+₹ ' : '-₹ ';

    document.getElementById('buyingPriceChapter').style.display = 'block';
    document.getElementById('chapterInvestedVal').innerText = `₹ ${totalInvested.toFixed(2)} (Entry ₹${entry} × Lot ${lot})`;

    document.getElementById('profitChapter').style.display = 'block';
    document.getElementById('chapterResultText').className = `fw-bold ${colorClass}`;
    document.getElementById('chapterResultText').innerText = `${sign}${Math.abs(netProfit).toFixed(2)}`;
}

/* ---------- Scan panel ---------- */
function updateGauge(trend, score) {
    const needle = document.getElementById('gaugeNeedle');
    const title = document.getElementById('gaugeTitle');
    const desc = document.getElementById('gaugeDesc');

    needle.style.transform = `translateX(-50%) rotate(${(score / 100) * 90}deg)`;
    title.innerText = trend;

    if (score > 30) { title.className = 'fw-bold mt-2 mb-1 text-success'; desc.innerText = 'Strong Bullish trend with robust momentum.'; }
    else if (score > 0) { title.className = 'fw-bold mt-2 mb-1 text-success'; desc.innerText = 'Mild Bullish trend with normal relative strength.'; }
    else if (score < -30) { title.className = 'fw-bold mt-2 mb-1 text-danger'; desc.innerText = 'Strong Bearish trend with downward pressure.'; }
    else if (score < 0) { title.className = 'fw-bold mt-2 mb-1 text-danger'; desc.innerText = 'Mild Bearish trend with selling pressure.'; }
    else { title.className = 'fw-bold mt-2 mb-1 text-warning'; desc.innerText = 'Sideways or Neutral market momentum.'; }
}

async function scanStock(presetSymbol = null) {
    const inputVal = presetSymbol ? presetSymbol : document.getElementById('stockSymbol').value.trim().toUpperCase();
    if (!inputVal) { alert('Please enter or select a stock symbol'); return; }

    document.getElementById('stockSymbol').value = inputVal;
    const timeframe = document.getElementById('timeframeSelect').value;

    if (isMobile()) {
        closeMobileSidebar();
    } else {
        const sidebar = document.getElementById('sidebarContainer');
        if (!sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            document.getElementById('mainContentContainer').classList.add('expanded');
            document.querySelector('.sidebar-toggle-btn').innerHTML = '&raquo;';
        }
    }

    try {
        const data = await (await fetch(`/get_signals?symbol=${encodeURIComponent(inputVal)}&interval=${timeframe}`)).json();
        if (data.error) { alert('Error: ' + data.error); return; }

        document.getElementById('stockName').innerText = `${data.name} (${inputVal}) - Timeframe: ${timeframe.toUpperCase()}`;
        document.getElementById('stockPrice').innerText = '₹ ' + data.price;
        document.getElementById('emaValues').innerHTML = `20 EMA: ₹${data.ema_20}<br>50 EMA: ₹${data.ema_50}`;
        document.getElementById('swingLevels').innerHTML = `SH: ₹${data.swing_high}<br>SL: ₹${data.swing_low}`;
        document.getElementById('volumeStatus').innerText = data.volume_status;

        const dowBox = document.getElementById('dowSignalBox');
        if (data.dow_signal === 'BUY') {
            dowBox.innerHTML = `<span class="badge-buy">DOW BUY BREAKOUT</span><br><br><b>Time: ${data.dow_time}</b><br>${data.dow_message}`;
        } else if (data.dow_signal === 'SELL') {
            dowBox.innerHTML = `<span class="badge-sell">DOW SELL BREAKDOWN</span><br><br><b>Time: ${data.dow_time}</b><br>${data.dow_message}`;
        } else {
            dowBox.innerHTML = `<span class="text-warning"><b>Dow Status: Wait / No Breakout</b></span><br><br>${data.dow_message}`;
        }

        const emaBox = document.getElementById('emaSignalBox');
        const tf = timeframe.toUpperCase();
        if (data.ema_signal === 'BUY') {
            emaBox.innerHTML = `<span class="badge-buy">UP SIDE BREAKOUT / GOLDEN CROSSOVER</span><br>Last Crossover (${tf}): <b>${data.last_cross_date}</b>`;
        } else if (data.ema_signal === 'SELL') {
            emaBox.innerHTML = `<span class="badge-sell">DOWN SIDE BREAKDOWN / DEATH CROSSOVER</span><br>Last Crossover (${tf}): <b>${data.last_cross_date}</b>`;
        } else {
            emaBox.innerHTML = `<span class="text-muted">Last Crossover (${tf}): <b>${data.last_cross_date}</b></span>`;
        }

        updateGauge(data.gauge_trend, data.gauge_score);
        document.getElementById('resultCard').style.display = 'flex';
        loadOptionChainForStock(inputVal);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
        alert('Could not scan ' + inputVal + '. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchAllTables();
    setInterval(fetchAllTables, 60000);

    // Five card-stacked tables make for an endless page on a phone, so only the
    // headline Nifty 50 table stays open; the rest are one tap away.
    if (isMobile()) {
        ['bankNiftyTable', 'commoditiesTable', 'giftNiftyTable', 'finNiftyTable']
            .forEach(dom => toggleTable(dom + 'Wrapper', dom + 'ToggleIcon'));
    }
});
