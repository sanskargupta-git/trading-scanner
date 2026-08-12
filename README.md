# 📊 Ultimate Pro Trading Terminal

Ek personal trading analytics dashboard jisme Nifty 50, Bank Nifty, Fin Nifty, MCX commodities
aur indices — sab ek hi jagah pe monitor kar sakte ho.

> ⚠️ Ye ek **learning aur research project** hai. Ye koi trading advice nahi deta, koi order place
> nahi karta, aur profit ka koi guarantee nahi hai. Prices delayed hain.

---

## 1. Project kya hai?

Normally market dekhne ke liye 10 alag-alag chart tabs kholne padte hain — ek me RSI, ek me MACD,
ek me price. Har baar sab manually check karna padta hai.

Ye project wahi kaam ek screen pe kar deta hai. Ye Yahoo Finance se **real market data** laata hai,
uspe standard technical indicators calculate karta hai, aur sab kuch ek clean terminal-style
dashboard me dikha deta hai.

Koi fake data nahi hai — jo bhi number dikhta hai wo actual market data se calculate hota hai.

---

## 2. Ye kya karta hai?

- **67 symbols** ka live data track karta hai (50 Nifty stocks + Bank Nifty + Fin Nifty + commodities + indices)
- Har symbol pe **10 technical indicators** calculate karta hai
- Har symbol ko ek **Signal Score** deta hai (−7 se +7 tak) — kitne indicators bullish hain minus kitne bearish
- Har **90 second** me background me data refresh karta hai
- Bullish/bearish setups ko rank karke top 5 dikhata hai
- Market ka overall mood dikhata hai (kitne stocks up, kitne down)

---

## 3. Main features

| Feature | Kya karta hai |
|---|---|
| 📈 **10 indicators** | Big Candle, MACD, DOW Breakout, EMA Crossover, Bollinger Band, RSI, RSI Trend, DMI, ADX, ADX Trend |
| 🎯 **Signal Score** | Sab indicators ka summary ek number me — turant pata chal jaata hai stock ka bias |
| 🔍 **Screener** | Bias se filter karo, score/RSI/ADX se sort karo, CSV download karo |
| 🔥 **Heatmap** | Poora market ek screen pe rangeen tiles me |
| ⭐ **Watchlist** | Apne stocks save karo (browser me save hota hai) |
| 🧮 **Options Lab** | Strike ladder aur P&L calculator |
| ✨ **AI Assistant** | Gemini ko actual scanner numbers milte hain, wo unhe simple language me samjhata hai |
| 🌗 **Dark / Light** | Dono theme, choice save ho jaati hai |
| 📱 **Mobile ready** | Phone pe tables automatically cards ban jaate hain |
| 📊 **Live status** | Market open/closed, data kitna purana hai, next refresh kab hai |

---

## 4. Main indicators

Har symbol pe ye 10 indicators calculate hote hain. Formulas standard hain — koi custom
"secret strategy" nahi hai.

| Indicator | Timeframe | Kya dekhta hai |
|---|---|---|
| 🔥 **Big Candle** | 15M | Candle ka range last 10 candles ke average se 1.5× bada hai ya nahi |
| ⚡ **MACD** | 1H | 12/26 EMA ka difference vs uske 9-period signal line se |
| 📈 **DOW Breakout** | 15M | Price ne pichhle 6 bars ka high toda (BUY) ya low toda (SELL) |
| ⚔️ **EMA Crossover** | 5M | 20 EMA, 50 EMA ke upar hai (Golden) ya neeche (Death) |
| 📊 **Bollinger Band** | 15M | Price upper band (20 SMA + 2 std dev) tak pahuncha ya nahi |
| 📉 **RSI** | 15M | 14-period RSI. 30 se neeche oversold, 70 se upar overbought |
| 📉 **RSI Trend** | 15M | RSI pichhli candle se badha ya ghata |
| 🎯 **DMI** | 15M | +DI, −DI se aage hai (bullish) ya peeche |
| 🎯 **ADX** | 15M | Trend ki strength. 25 se upar matlab trend mazboot hai |
| 🎯 **ADX Trend** | 15M | ADX badh raha hai ya ghat raha hai |

---

## 5. Signal Score kya hai?

Ye sab indicators ka ek **summary number** hai — alag strategy nahi.

7 indicators dekhe jaate hain (Big Candle, MACD, DOW, EMA, Bollinger, RSI Trend, DMI).
Har bullish signal pe **+1**, har bearish pe **−1**. Total −7 se +7 tak aata hai.

| Score | Band | Matlab |
|---|---|---|
| +4 aur upar | 🟢 **STRONG BULLISH** | Zyadatar indicators bullish hain |
| +1 se +3 | 🟢 **BULLISH** | Bullish side pe jhukav hai |
| 0 | ⚪ **NEUTRAL** | Mixed signals |
| −1 se −3 | 🔴 **BEARISH** | Bearish side pe jhukav hai |
| −4 aur neeche | 🔴 **STRONG BEARISH** | Zyadatar indicators bearish hain |

> ⚠️ Score sirf batata hai ki **abhi kitne indicators agree kar rahe hain**. Ye future
> predict nahi karta aur na hi koi buy/sell signal hai.

---

## 6. Pages ka explanation

| Page | URL | Kya milega |
|---|---|---|
| **Dashboard** | `/` | Index cards (Nifty, Bank Nifty, Fin Nifty, India VIX), Market Pulse, top 5 bullish/bearish setups, watchlist, aur sab segment tables |
| **Screener** | `/screener` | Sab stocks ek table me — bias filter, 6 sorting options, search, CSV export |
| **Heatmap** | `/heatmap` | Har stock ek tile. Colour daily %, signal score ya RSI se. Tile pe click karo → analysis khulega |
| **Stock Analysis** | `/stock/RELIANCE` | Ek stock ki poori detail — indicator grid, timeframe levels (5M/15M/1H/1D), technical summary |
| **Watchlist** | `/watchlist` | Apne symbols add/remove karo, live price aur score dekho |
| **Markets** | `/markets` | Sab segments + currencies card grid me |
| **Options Lab** | `/options` | Strike ladder + P&L calculator (lot size, quantity, entry, exit) |
| **About** | `/about` | Har indicator ka matlab, architecture, tech stack |

---

## 7. Architecture — simple explanation

**Problem:** Agar har page load pe har stock ka data alag-alag mangwaayein, to 50 stocks × 5 timeframes
= **250+ requests**. Isse page hamesha timeout ho jaata hai aur Yahoo block kar deta hai.

**Solution:** Background worker + snapshot cache.

```
        ┌──────────────────────────────────────┐
        │   Background Thread (har 90 sec)     │
        │                                      │
        │   4 batch requests  ──►  Yahoo       │
        │   (5M, 15M, 1H, 1D — sab symbols)    │
        │              │                       │
        │              ▼                       │
        │   Indicators calculate               │
        │              │                       │
        │              ▼                       │
        │        SNAPSHOT (memory)             │
        └──────────────┬───────────────────────┘
                       │  (sirf padhta hai)
        ┌──────────────▼───────────────────────┐
        │   Browser  ──►  Flask  ──►  Snapshot │
        │   Response time: ~20 milliseconds    │
        └──────────────────────────────────────┘
```

Iska matlab:
- **250+ requests → 4 requests** per cycle
- Page kabhi Yahoo ka wait nahi karta, isliye kabhi timeout nahi hota
- Agar Yahoo fail ho jaaye, to purana data screen pe rehta hai aur **STALE** mark ho jaata hai —
  dashboard blank nahi hota

---

## 8. Tech stack

| Layer | Kya use hua |
|---|---|
| Backend | **Python 3**, **Flask** |
| Market data | **yfinance** (Yahoo Finance) |
| Calculations | **Pandas**, **NumPy** |
| Frontend | Plain **JavaScript**, **Bootstrap 5**, custom CSS |
| AI | **Google Gemini** (optional) |
| Server | **Gunicorn** |
| Deploy | **Docker**, Railway |

Koi frontend build step nahi hai (na React, na npm). Sirf templates, CSS aur vanilla JS — taaki
poora project easily padha ja sake.

---

## 9. Local setup — step by step

### Step 1: Python install karo

[python.org/downloads](https://www.python.org/downloads/) se download karo.

> **Windows pe important:** install karte waqt **"Add Python to PATH"** wala checkbox zaroor tick karna.

Check karo ki install ho gaya:

```bash
python --version
```

`Python 3.11.x` jaisa kuch dikhna chahiye (3.9 ya usse upar chalega).

### Step 2: ZIP extract karo

ZIP ko right-click → **Extract All**. Ek folder banega `TradingScanner`.

### Step 3: Terminal us folder me kholo

**Windows:** folder ke andar address bar me `cmd` type karke Enter dabao.

**Mac / Linux:**
```bash
cd path/to/TradingScanner
```

### Step 4: Virtual environment banao (recommended)

Isse project ke packages tumhare system Python se alag rahenge.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Activate hone ke baad terminal me `(venv)` dikhne lagega.

### Step 5: Requirements install karo

```bash
pip install -r requirements.txt
```

Pehli baar 1–2 minute lagega.

### Step 6: Project run karo

```bash
python trading_scanner.py
```

**Ya Windows pe shortcut:** `START.bat` pe double-click kar do — wo khud dependencies install karke app chalu kar dega.

### Step 7: Browser kholo

```
http://localhost:5000
```

> ⏳ **Pehli baar 10–15 second lagenge.** Background worker pehla data fetch kar raha hota hai.
> Tab tak "Updating market data…" dikhega. Ye normal hai — page apne aap bhar jaayega.

### Step 8: Band karne ke liye

Terminal me **Ctrl + C** dabao.

---

## 10. START.bat (Windows shortcut)

Agar terminal se comfortable nahi ho, to bas `START.bat` pe **double-click** kar do.

Ye khud:
1. Check karta hai ki Python installed hai ya nahi (nahi hai to clear message deta hai)
2. `requirements.txt` se saare packages install karta hai
3. App start kar deta hai

Uske baad browser me `http://localhost:5000` khol lo. Band karne ke liye us window me **Ctrl + C**.

---

## 11. Environment variables

Sab optional hain — bina kisi config ke bhi project chalega.

| Variable | Default | Kaam |
|---|---|---|
| `PORT` | `5000` | Konse port pe chalega |
| `REFRESH_SECONDS` | `90` | Kitne second baad data refresh hoga |
| `GEMINI_API_KEY` | *(empty)* | AI assistant ke liye |

Set karne ke liye `.env.example` ko copy karke `.env` banao:

**Windows:** `copy .env.example .env`
**Mac/Linux:** `cp .env.example .env`

> 🔒 `.env` file `.gitignore` me hai — ye kabhi Git me commit nahi hogi. Apni key kabhi bhi
> directly code me mat likhna.

---

## 12. Gemini API key setup (optional)

AI assistant ke bina bhi **poora dashboard normally chalta hai**. Assistant sirf ek extra feature hai.

Agar enable karna hai:

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) pe jao
2. Google account se login karo
3. **Create API Key** pe click karo
4. Key copy karo

**Local pe set karna:**

Windows (cmd):
```bash
set GEMINI_API_KEY=your_key_here
python trading_scanner.py
```

Mac / Linux:
```bash
export GEMINI_API_KEY=your_key_here
python trading_scanner.py
```

Ya `.env` file me daal do:
```
GEMINI_API_KEY=your_key_here
```

Assistant ko scanner ke **actual numbers** milte hain. `explain RELIANCE` poocho to wo RELIANCE ka
real price, MACD, RSI, ADX aur score dekh kar samjhaayega — apne se koi number nahi banayega.

---

## 13. Run commands (summary)

```bash
# Development (simple)
python trading_scanner.py

# Production (gunicorn — Linux/Mac)
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 8 --timeout 120 trading_scanner:app

# Docker
docker build -t trading-terminal .
docker run -p 5000:5000 trading-terminal
```

> ⚠️ **Hamesha `--workers 1` rakhna.** Cache aur background thread process memory me rehte hain.
> Zyada workers ka matlab har worker apna alag data fetch karega — Yahoo pe load multiply ho jaayega.

---

## 14. Railway deployment

1. Code ko GitHub pe push karo
2. [railway.app](https://railway.app) pe **New Project → Deploy from GitHub repo**
3. Railway khud `Dockerfile` detect kar lega
4. Optional: **Variables** tab me `GEMINI_API_KEY` add kar do
5. Deploy hone ke baad `/healthz` kholke check karo

`/healthz` aisa response dega:
```json
{"ok": true, "status": "ok", "symbols": 68, "age_seconds": 12.4, "stale": false}
```

`PORT` Railway khud set karta hai — usko manually mat chhedo.

---

## 15. Folder structure

```
TradingScanner/
├── trading_scanner.py      # Poora backend: data engine + indicators + routes
├── templates/              # HTML pages
│   ├── base.html           # Common layout (nav, status bar, assistant)
│   ├── dashboard.html
│   ├── screener.html
│   ├── heatmap.html
│   ├── stock.html
│   ├── watchlist.html
│   ├── markets.html
│   ├── options.html
│   ├── about.html
│   └── error.html
├── static/
│   ├── css/app.css         # Saari styling (dark + light + mobile)
│   └── js/
│       ├── app.js          # Shared: theme, search, status bar, assistant
│       ├── dashboard.js
│       ├── screener.js
│       ├── heatmap.js
│       ├── stock.js
│       ├── watchlist.js
│       ├── markets.js
│       └── options.js
├── requirements.txt
├── Dockerfile
├── Procfile
├── START.bat               # Windows one-click start
├── .env.example
├── .gitignore
├── PROJECT_INFO.txt
└── README.md
```

---

## 16. Troubleshooting

**❓ Table khali hai / "Updating market data…" dikha raha hai**
Pehle 10–15 second normal hain. Agar 1 minute se zyada ho jaaye, internet check karo.
`/healthz` kholke dekho `status` kya keh raha hai.

**❓ `ModuleNotFoundError: No module named 'flask'`**
Requirements install nahi hue, ya venv activate nahi hai.
```bash
pip install -r requirements.txt
```

**❓ `python` command nahi mil raha (Windows)**
Python PATH me nahi hai. Python dobara install karo aur "Add Python to PATH" tick karo.
Ya `py` try karo: `py trading_scanner.py`

**❓ Port 5000 already in use**
```bash
# Windows
set PORT=5050 && python trading_scanner.py
# Mac/Linux
PORT=5050 python trading_scanner.py
```
Mac pe 5000 AirPlay use karta hai — 5050 use kar lo.

**❓ Kuch stocks me `--` dikh raha hai**
Us symbol ka data Yahoo se nahi aaya. `--` ka matlab hai "data available nahi" —
project galat number banane ki jagah honestly `--` dikhata hai.

**❓ AI assistant "not configured" bol raha hai**
`GEMINI_API_KEY` set nahi hai. Ye normal hai — baaki sab kuch chalta rahega.

**❓ STALE DATA banner aa raha hai**
Ek refresh fail hua hai. Purana data screen pe hai aur project apne aap retry kar raha hai.
Ye by design hai — dashboard blank nahi hota.

---

## 17. Data limitations (padhna zaroori hai)

Ye project honest rehne ki koshish karta hai. Jo cheezein ye **nahi** kar sakta:

**1. Data delayed hai**
Yahoo Finance se data aata hai, jo exchange ka live feed nahi hai. Isliye app kahin bhi
"LIVE" claim nahi karta — sirf "Data age 42s" dikhata hai taaki tumhe pata rahe data kitna purana hai.

**2. Timeframe fallback**
Kabhi-kabhi Yahoo 15M ya 5M ka intraday data nahi deta. Aise waqt project **daily bars** use
karta hai — par isko chhupata nahi. Stock Analysis page pe saaf likha aata hai:

```
15M req · Daily fallback
```

Aur upar ek banner bhi aata hai. Matlab tumhe hamesha pata rahega ki number kis timeframe ka hai.

**3. Data unavailable**
Agar kisi symbol ka data hi nahi mila, to app `--` dikhata hai. **Koi number bana kar nahi
dikhata.** `NaN`, `undefined`, `null` kahin nahi aayega.

**4. Stale data**
Agar refresh fail ho jaye, to purana data screen pe rehta hai aur upar yellow banner aata hai:
`STALE DATA — last successful update 180s ago`. Dashboard blank nahi hota.

**5. Market holidays**
App sirf time aur weekday dekh kar market status batata hai. NSE holiday list isme nahi hai —
to holiday pe "Market Open" dikh sakta hai jabki actually band ho.

---

## 18. Options ka estimate limitation

⚠️ **Options Lab ke premiums real nahi hain.**

Options Lab spot price aur strike distance se ek **analytical estimate** banata hai. Ye:

- ❌ Real exchange option-chain quotes **nahi** hain
- ❌ Real bid/ask **nahi** hain
- ❌ Implied volatility, Greeks, time decay **use nahi karte**
- ✅ Sirf position sizing aur "agar premium X se Y ho jaye to kitna banega/jayega" samajhne ke liye hai

Page pe har jagah `ESTIMATED / ANALYTICAL` likha hai. P&L me brokerage, STT, GST, stamp duty
bhi shamil nahi hai. Real trading se pehle apne broker ka actual chain dekho.

---

## 19. Security notes

- ✅ Code me **koi API key ya secret nahi** hai. Gemini key sirf `GEMINI_API_KEY` environment
  variable se aati hai — koi hardcoded fallback nahi
- ✅ `.env` gitignored hai
- ✅ Har response pe security headers: Content-Security-Policy, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- ✅ Symbol input strict pattern se validate hota hai data layer tak pahunchne se pehle
- ✅ Sab dynamic text escape hota hai DOM me daalne se pehle (XSS protection)
- ✅ Error hone pe user ko stack trace nahi dikhta — sirf server log me jaata hai

> 🔑 Agar tumne kabhi galti se koi API key commit kar di ho, to sirf file se hataana kaafi
> **nahi** hai — wo Git history me reh jaati hai. Us key ko provider ke dashboard se
> **revoke karke nayi banao**.

---

## 20. Financial disclaimer

Ye project **sirf education aur research** ke liye hai.

- ❌ Ye investment advice **nahi** hai
- ❌ Koi buy/sell recommendation **nahi** hai
- ❌ Signals "100% accurate" **nahi** hain — koi bhi technical indicator future predict nahi karta
- ❌ Profit ka koi guarantee **nahi** hai
- ⚠️ Prices **delayed** hain (Yahoo Finance), live exchange feed nahi hai
- ⚠️ Option premiums **estimated/analytical** hain — real exchange option-chain quotes nahi hain

Koi bhi trading decision lene se pehle apne broker ke real data se verify karo. Market me
paisa lagane ka risk poori tarah tumhara hai.

---

**Made for learning.** Agar koi bug mile ya improvement idea ho, code padho — sab kuch
`trading_scanner.py` aur `static/js/` me clearly likha hua hai. 🚀
