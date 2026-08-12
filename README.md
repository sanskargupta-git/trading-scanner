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

## 4. Pages ka explanation

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

## 5. Architecture — simple explanation

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

## 6. Tech stack

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

## 7. Local setup — step by step

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

## 8. Environment variables

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

## 9. Gemini API key setup (optional)

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

## 10. Run commands (summary)

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

## 11. Railway deployment

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

## 12. Folder structure

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

## 13. Troubleshooting

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

## 14. Security notes

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

## 15. Financial disclaimer

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
