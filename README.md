# 📊 Ultimate Pro Trading Terminal

> ## 📖 Kaunsi file padhni hai?
>
> | Aapko kya chahiye? | File |
> |---|---|
> | 🔧 **Project install karna hai** (ye file) | **README.md** — Hinglish |
> | 🔧 **Project install karaycha aahe** | **[README_MINGLISH.md](README_MINGLISH.md)** — Marathi + English |
> | 🖥️ **Website kaise use kare, samajhna hai** | **[USER_GUIDE.md](USER_GUIDE.md)** — Hinglish |
> | 🖥️ **Website kashi vaparaychi, samjun ghyaycha aahe** | **[USER_GUIDE_MINGLISH.md](USER_GUIDE_MINGLISH.md)** — Marathi + English |
>
> **Agar aap sirf website use karna chahte ho** (install nahi karna), to seedha
> **[USER_GUIDE.md](USER_GUIDE.md)** kholo — usme har page, har colour aur har
> indicator bilkul simple bhasha me samjhaya gaya hai.

---

> ### ⚡ SUPER QUICK START (Windows)
> 1. ZIP ko **Extract** karo
> 2. Folder ke andar **`START.bat`** pe double-click karo
> 3. Browser me kholo → **http://localhost:5000**
>
> **Manual (koi bhi OS):**
> ```
> python -m venv venv
> venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
> pip install -r requirements.txt
> python trading_scanner.py
> ```
> Pehli baar table bharne me **10–15 second** lagte hain. Ye normal hai.

---

## 📑 Index

| # | Section | # | Section |
|---|---|---|---|
| 1 | [Project Intro](#1-project-intro) | 14 | [Railway Deployment](#14-railway-deployment) |
| 2 | [Important Disclaimer](#2-important-disclaimer) | 15 | [Health Check](#15-health-check) |
| 3 | [Features](#3-features) | 16 | [Troubleshooting](#16-troubleshooting) |
| 4 | [How The Project Works](#4-how-the-project-works) | 17 | [Data Limitations](#17-data-limitations) |
| 5 | [System Requirements](#5-system-requirements) | 18 | [Options Limitation](#18-options-limitation) |
| 6 | [Easiest Way To Run — Windows](#6-easiest-way-to-run--windows) | 19 | [Security](#19-security) |
| 7 | [Windows Manual Setup](#7-windows-manual-setup) | 20 | [Folder Structure](#20-folder-structure) |
| 8 | [macOS Setup](#8-macos-setup) | 21 | [API Overview](#21-api-overview) |
| 9 | [Linux Setup](#9-linux-setup) | 22 | [Development Guide](#22-development-guide) |
| 10 | [Gemini Setup (Optional)](#10-gemini-setup--optional) | 23 | [How To Customize](#23-how-to-customize) |
| 11 | [.env Setup](#11-env-setup) | 24 | [Known Limitations](#24-known-limitations) |
| 12 | [START.bat Explanation](#12-startbat-explanation) | 25 | [Project Information](#25-project-information) |
| 13 | [Docker Setup](#13-docker-setup) | 26 | [Final Quick Start](#26-final-quick-start) |

---

## 1. Project Intro

Ye ek **personal trading analytics dashboard** hai jisme Nifty 50, Bank Nifty, Fin Nifty,
Commodities aur dusre market segments ko ek jagah monitor kar sakte ho.

**Problem kya thi?**
Market analyse karne ke liye normally 10 alag-alag chart tabs kholne padte hain — ek me RSI dekho,
ek me MACD, ek me price. Har stock ke liye ye repeat karo. Bahut time waste hota hai.

**Ye project kya karta hai?**
Yahoo Finance se **real market data** laata hai, uspe standard technical indicators calculate karta
hai, aur sab kuch ek clean terminal-style dashboard me dikha deta hai. Total **68 symbols** track
hote hain aur har **90 second** me data automatically refresh hota rehta hai.

Koi fake data nahi hai. Jo bhi number screen pe dikhta hai wo actual market data se calculate hota
hai. Agar kisi cheez ka data nahi milta to project `--` dikhata hai — **number bana kar nahi dikhata**.

---

## 2. Important Disclaimer

> ### ⚠️ Ye padhna zaroori hai

- 📚 Ye project **sirf education aur research** ke liye hai
- ❌ Ye **investment advice nahi** hai
- ❌ Koi **buy/sell recommendation nahi** hai
- ❌ **Profit ka koi guarantee nahi** hai
- ⚠️ **Technical signals galat ho sakte hain** — koi bhi indicator future predict nahi karta
- ⏱️ **Market data delayed hai** (Yahoo Finance), live exchange feed nahi hai
- 🧮 Options Lab ke premiums **estimated** hain, real exchange quotes nahi

Koi bhi trading decision lene se pehle apne broker ke actual data se verify karo.
Market me paisa lagane ka risk poori tarah tumhara hai.

---

## 3. Features

### Pages

| Page | URL | Kya milega |
|---|---|---|
| **Dashboard** | `/` | Index cards (Nifty 50, Bank Nifty, Fin Nifty, India VIX), Market Pulse (kitne bullish/bearish/neutral, top gainer/loser), Top 5 Bullish aur Top 5 Bearish setups, tumhari watchlist, aur saare segment tables |
| **Screener** | `/screener` | Saare stocks ek table me — signal bias se filter, 6 tarah se sort, symbol search, CSV export. Live count: "Showing 23 of 50 stocks" |
| **Heatmap** | `/heatmap` | Har stock ek rangeen tile. Colour daily %, signal score ya RSI se choose kar sakte ho. Tile pe click karo → Stock Analysis khulega |
| **Stock Analysis** | `/stock/RELIANCE` | Ek stock ki poori detail — price, score band, market status, data age, 10-indicator grid (har cell pe timeframe likha), timeframe levels (5M/15M/1H/1D), Technical Summary |
| **Watchlist** | `/watchlist` | Apne symbols add/remove karo, search karo, live price + score + data age dekho. Browser me save hota hai |
| **Markets** | `/markets` | Saare segments (Nifty 50, Bank Nifty, Fin Nifty, Commodities, Gift Nifty) + currencies card grid me |
| **Options Lab** | `/options` | Strike ladder + P&L calculator (side, lot size, quantity, entry, exit) |
| **About** | `/about` | Har indicator ka matlab, architecture, tech stack, security notes |

### Indicators

Har symbol pe ye **10 indicators** calculate hote hain. Formulas standard hain — koi custom
"secret strategy" nahi hai.

| Indicator | Timeframe | Kya dekhta hai |
|---|---|---|
| 🔥 **Big Candle** | 15M | Candle ka high-low range last 10 candles ke average se 1.5× bada hai? Close > open ho to Bullish |
| ⚡ **MACD** | 1H | 12 aur 26 period EMA ka difference, uske apne 9-period signal line se compare |
| 📈 **DOW Breakout** | 15M | Price ne pichhle 6 bars ka high toda (BUY) ya low toda (SELL) |
| ⚔️ **EMA Crossover** | 5M | 20 EMA, 50 EMA ke upar hai (Golden) ya neeche (Death) |
| 📊 **Bollinger Band** | 15M | Price upper band (20 SMA + 2 standard deviation) tak pahuncha ya nahi |
| 📉 **RSI** | 15M | 14-period Relative Strength Index. 30 se neeche oversold, 70 se upar overbought |
| 📉 **RSI Trend** | 15M | RSI pichhli candle se badha (Uptick) ya ghata (Downtick) |
| 🎯 **DMI** | 15M | +DI, −DI se aage hai (Bullish Cross) ya peeche (Bearish Cross) |
| 🎯 **ADX** | 15M | Trend ki strength. 25 se upar matlab trend me dum hai |
| 🎯 **ADX Trend** | 15M | ADX badh raha hai ya ghat raha hai |

### Signal Score

Ye sab indicators ka **summary number** hai — alag strategy nahi.

7 indicators dekhe jaate hain (Big Candle, MACD, DOW, EMA, Bollinger, RSI Trend, DMI).
Har bullish signal pe **+1**, har bearish pe **−1**. Total **−7 se +7** tak.

| Score | Band |
|---|---|
| +4 aur upar | 🟢 **STRONG BULLISH** |
| +1 se +3 | 🟢 **BULLISH** |
| 0 | ⚪ **NEUTRAL** |
| −1 se −3 | 🔴 **BEARISH** |
| −4 aur neeche | 🔴 **STRONG BEARISH** |

> Score sirf batata hai ki **abhi kitne indicators aapas me agree kar rahe hain**.
> Ye future predict nahi karta aur na hi koi buy/sell signal hai.

### Aur bhi

| Feature | Detail |
|---|---|
| ✨ **Gemini AI Assistant** | **Optional.** Enable karo to "explain RELIANCE" poochne pe usko RELIANCE ke actual current numbers (price, MACD, RSI, ADX, score) bheje jaate hain aur wo unhe simple language me samjhata hai. Apne se koi number nahi banata. Key na ho to baaki sab normal chalta hai |
| 📥 **CSV Export** | Har segment table pe aur Screener pe CSV download button |
| 📊 **Data Status** | Har page pe top bar me: market open/closed, last updated time, data age, next refresh countdown. Refresh fail ho to **STALE DATA** banner |
| ⏱️ **Timeframe honesty** | Agar 15M data na mile aur daily use karna pade, to saaf likha aata hai `Requested: 15M / Using: Daily fallback` |
| 🔍 **Global Search** | Top bar me symbol search, keyboard se navigate (↑↓ / Enter / Escape) |
| 🌗 **Dark / Light theme** | Dono, choice browser me save ho jaati hai |
| 📱 **Mobile support** | 390px tak. Phone pe wide tables automatically **cards** ban jaate hain, koi side-scroll nahi |

---

## 4. How The Project Works

```
   Yahoo Finance (market data)
              │
              ▼
   ┌──────────────────────────────────────────┐
   │  BACKGROUND DATA ENGINE                  │
   │  (ek thread, har 90 second)              │
   │                                          │
   │  Batch Fetch: sirf 4 requests            │
   │  (5M, 15M, 1H, 1D — saare 70 tickers)    │
   │              │                           │
   │              ▼                           │
   │  Technical Indicators calculate          │
   │  (har symbol ke liye ek baar)            │
   │              │                           │
   │              ▼                           │
   │  SNAPSHOT CACHE (memory me)              │
   └──────────────┬───────────────────────────┘
                  │  (handlers sirf padhte hain)
                  ▼
   ┌──────────────────────────────────────────┐
   │  Flask API  →  Frontend (browser)        │
   │  Response time: ~10-20 milliseconds      │
   └──────────────────────────────────────────┘
```

### Ye architecture kyun hai?

**Seedha tarika (jo kaam nahi karta):** har page load pe har stock ka data alag mangwao.
50 stocks × 5 timeframes = **250+ sequential requests**. Result:
- Page hamesha timeout ho jaata hai
- Yahoo rate-limit karke block kar deta hai
- Har visitor pura load dobara banata hai

**Isliye:** ek background thread har 90 second me **4 batch requests** me poore universe ka data
laata hai, ek baar indicators calculate karta hai, aur memory me snapshot rakh deta hai.

> ### 🔑 Important rule
> **Normal page request kabhi Yahoo ko directly hit nahi karta.**
> Har page aur API sirf snapshot padhta hai. Isliye response 10–20ms me aata hai aur
> page kabhi Yahoo ka wait nahi karta.

Sirf ek exception hai: agar tum aisa symbol khologe jo scanned universe me nahi hai
(jaise `/stock/DMART`), to uska data on-demand fetch hota hai aur 5 minute cache hota hai.
Page pe "Off-universe symbol" badge dikh jaata hai.

**Agar refresh fail ho jaye:** purana valid snapshot screen pe rehta hai aur **STALE DATA**
mark ho jaata hai. Dashboard blank nahi hota.

---

## 5. System Requirements

| Cheez | Requirement |
|---|---|
| **OS** | Windows, macOS ya Linux — teeno chalte hain |
| **Python** | **3.11 ya usse naya recommended.** Yahi verified hai: Docker image `python:3.11-slim` use karta hai, aur local testing Python 3.13 pe hui hai. `requirements.txt` ka floor 3.9 hai to 3.9/3.10 pe bhi install ho jaana chahiye — par maine test nahi kiya |
| **Internet** | **Zaroori hai.** Market data internet se aata hai. Offline chalayoge to tables khali rahenge |
| **Browser** | Koi bhi modern browser — Chrome, Edge, Firefox, Safari. Internet Explorer support nahi hai |
| **RAM** | Normal use me kuch sau MB. Koi khaas requirement nahi — jo bhi computer Python chala sakta hai wo kaafi hai |
| **Disk** | Project khud ~70 KB. Dependencies (pandas, numpy, yfinance) ~300–400 MB le sakti hain |

---

## 6. Easiest Way To Run — Windows

### STEP 1 — ZIP download karo
Jo ZIP mila hai usko apne computer pe save karo (Downloads folder me hi theek hai).

### STEP 2 — ZIP extract karo
ZIP file pe **right-click** → **Extract All...** → **Extract**

Ek folder banega: **`UltimateProTradingTerminal`**

### STEP 3 — Folder kholo
Us folder ke andar jao. Tumhe `trading_scanner.py`, `START.bat`, `templates`, `static`
wagairah dikhenge.

### STEP 4 — START.bat pe double-click karo

Bas. Ek black window (Command Prompt) khulegi aur ye khud kar dega:
1. Check karega Python installed hai ya nahi
2. `requirements.txt` se saare packages install karega
3. Project start kar dega

> **Pehli baar 1–2 minute lag sakte hain** kyunki packages download ho rahe hote hain.
> Ghabrana nahi, window band mat karna.

### STEP 5 — Browser kholo

```
http://localhost:5000
```

> ⏳ **Pehle 10–15 second** tak "Updating market data…" dikhega. Background engine pehla
> snapshot bana raha hota hai. Page apne aap bhar jaayega — refresh karne ki zaroorat nahi.

### Band karne ke liye

Us black window me **`Ctrl + C`** dabao. Ya window band kar do.

### Agar START.bat kaam na kare

Manual setup use karo — [Section 7](#7-windows-manual-setup) dekho.

---

## 7. Windows Manual Setup

Command Prompt kholo project folder me (folder ke address bar me `cmd` type karke Enter dabao).

**Step 1 — Python check karo**
```cmd
python --version
```
`Python 3.11.x` ya usse naya dikhna chahiye.
Agar "not recognized" aaye to [python.org](https://www.python.org/downloads/) se install karo —
aur install karte waqt **"Add Python to PATH"** checkbox **zaroor tick** karna.

**Step 2 — Virtual environment banao**
```cmd
python -m venv venv
```
(Isse project ke packages tumhare system Python se alag rahenge — safe rehta hai.)

**Step 3 — Activate karo**
```cmd
venv\Scripts\activate
```
Ab terminal me line ke shuru me `(venv)` dikhne lagega.

**Step 4 — Packages install karo**
```cmd
pip install -r requirements.txt
```

**Step 5 — Project chalao**
```cmd
python trading_scanner.py
```

**Step 6 — Browser kholo**
```
http://localhost:5000
```

**Band karne ke liye:** `Ctrl + C`

---

## 8. macOS Setup

Terminal kholo aur project folder me jao (`cd ` type karke folder ko drag-drop kar do).

```bash
# 1. Python check
python3 --version

# 2. Virtual environment
python3 -m venv venv

# 3. Activate
source venv/bin/activate

# 4. Packages install
pip install -r requirements.txt

# 5. Run
python3 trading_scanner.py
```

Phir browser me kholo:
```
http://localhost:5000
```

**Band karne ke liye:** `Ctrl + C`

> ⚠️ **Mac pe port 5000 ka issue:** macOS ka AirPlay Receiver bhi port 5000 use karta hai.
> Agar error aaye to alag port pe chalao:
> ```bash
> PORT=5050 python3 trading_scanner.py
> ```
> Phir `http://localhost:5050` kholo.

---

## 9. Linux Setup

```bash
# 1. Python check
python3 --version

# 2. Agar venv module nahi hai (Ubuntu/Debian pe kabhi-kabhi alag se aata hai)
sudo apt install python3-venv python3-pip

# 3. Virtual environment banao
python3 -m venv venv

# 4. Activate karo
source venv/bin/activate

# 5. Packages install
pip install -r requirements.txt

# 6. Run
python3 trading_scanner.py
```

Browser me kholo: `http://localhost:5000`

**Deactivate karne ke liye** (venv se bahar aane ke liye):
```bash
deactivate
```

**Production style (gunicorn se):**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 8 --timeout 120 trading_scanner:app
```

> ⚠️ **Hamesha `--workers 1` rakhna.** Cache aur background thread process ki memory me
> rehte hain. Zyada workers ka matlab har worker apna alag data fetch karega — Yahoo pe
> load multiply ho jaayega.

---

## 10. Gemini Setup — OPTIONAL

> ### ✅ Gemini bilkul optional hai
> Iske bina bhi **poora dashboard normally chalta hai** — saare pages, scanner, stock analysis,
> watchlist, options, sab kuch. Assistant sirf ek extra feature hai. Key na ho to assistant
> politely bata deta hai ki configure nahi hai, aur baaki app pe koi asar nahi padta.

### API key kaise banayein

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) pe jao
2. Google account se login karo
3. **Create API Key** pe click karo
4. Key copy kar lo

### Key set karne ka tarika

**Windows CMD:**
```cmd
set GEMINI_API_KEY=your_key_here
python trading_scanner.py
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your_key_here"
python trading_scanner.py
```

**macOS / Linux:**
```bash
export GEMINI_API_KEY=your_key_here
python3 trading_scanner.py
```

**Ya `.env` file me** (sabse aasan — [Section 11](#11-env-setup) dekho):
```
GEMINI_API_KEY=your_key_here
```

### Assistant kaam kaise karta hai

Jab tum `explain RELIANCE` ya `analyse TCS` poochte ho, to server pehle apne snapshot se us
symbol ke **actual current numbers** nikaalta hai — price, daily %, signal score, MACD, EMA,
DOW, Bollinger, RSI, ADX, hourly trend — aur wo Gemini ko bhejta hai. Prompt me clearly likha
hota hai ki **sirf yahi numbers explain karo, apne se koi number mat banao**. Agar koi metric
available nahi hai to wo "not available" bolta hai.

Chat window ke neeche hamesha ye line dikhti hai:
> *AI-generated explanation is informational and may contain errors.*

> 🔒 **Apni API key kisi ko mat do aur kabhi Git me commit mat karo.**

---

## 11. .env Setup

Sabse aasan tarika settings dene ka.

**Step 1 — `.env.example` ko copy karke `.env` banao**

Windows:
```cmd
copy .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

**Step 2 — `.env` ko Notepad ya kisi bhi text editor me kholo aur edit karo**

### Supported variables

Ye teen hi variables code me actually padhe jaate hain — aur teeno **optional** hain:

| Variable | Default | Kya karta hai |
|---|---|---|
| `PORT` | `5000` | Konse port pe app chalega. Agar 5000 busy hai to `5050` kar do |
| `REFRESH_SECONDS` | `90` | Kitne second baad background engine data refresh karega. **Isse bahut chhota mat karna** — Yahoo rate-limit kar dega |
| `GEMINI_API_KEY` | *(khali)* | AI assistant enable karta hai. Khali chhod do to assistant off rehta hai, baaki sab chalta hai |

Example `.env`:
```
PORT=5000
REFRESH_SECONDS=90
GEMINI_API_KEY=
```

> 🔒 `.env` file `.gitignore` me hai — ye kabhi Git me commit nahi hogi.
> Apni key kabhi bhi seedha code me mat likhna.

---

## 12. START.bat Explanation

`START.bat` ek Windows shortcut hai. Double-click karne pe ye exactly **teen kaam** karta hai:

1. **Python check** — `python --version` chala kar dekhta hai ki Python installed aur PATH me
   hai ya nahi. Nahi hai to clear message deta hai ki python.org se install karo aur
   "Add Python to PATH" tick karo, phir ruk jaata hai
2. **Dependencies install** — `python -m pip install -r requirements.txt` chalata hai.
   Fail ho to internet connection check karne ko bolta hai
3. **App start** — `python trading_scanner.py` chala deta hai aur batata hai ki
   `http://localhost:5000` kholo

> ### ⚠️ Ek baat clear kar doon
> **START.bat virtual environment (venv) nahi banata.** Ye packages tumhare current Python
> me hi install karta hai. Agar tum apne system Python ko saaf rakhna chahte ho, to
> [Section 7](#7-windows-manual-setup) wala manual setup use karo jisme venv banta hai.

---

## 13. Docker Setup

Project me `Dockerfile` already hai (base image: `python:3.11-slim`).

**Build karo:**
```bash
docker build -t ultimate-pro-trading-terminal .
```

**Run karo:**
```bash
docker run -p 5000:5000 ultimate-pro-trading-terminal
```

Browser me kholo:
```
http://localhost:5000
```

**Environment variables ke saath:**
```bash
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key_here \
  -e REFRESH_SECONDS=90 \
  ultimate-pro-trading-terminal
```

**Ya `.env` file se:**
```bash
docker run -p 5000:5000 --env-file .env ultimate-pro-trading-terminal
```

Container ke andar app gunicorn se chalta hai — 1 worker, 8 threads, 120s timeout.
`PORT` env variable se bind port change kar sakte ho.

---

## 14. Railway Deployment

Railway pe deploy karna aasan hai kyunki `Dockerfile` already ready hai.

**Step 1 — Code GitHub pe push karo**
```bash
git init
git add .
git commit -m "Ultimate Pro Trading Terminal"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

> 🔒 Push karne se pehle confirm kar lo ki `.env` commit nahi ho rahi. `.gitignore` me
> already hai, par ek baar `git status` se check kar lena.

**Step 2 — Railway project banao**
[railway.app](https://railway.app) pe jaao → **New Project** → **Deploy from GitHub repo**
→ apna repo select karo.

**Step 3 — Dockerfile detection**
Railway khud `Dockerfile` detect kar lega aur usse build karega. Koi extra config nahi chahiye.

**Step 4 — Environment variables (optional)**
Project → **Variables** tab → **New Variable**:
- `GEMINI_API_KEY` = tumhari key (agar assistant chahiye)
- `REFRESH_SECONDS` = `90` (default hi theek hai)

**Step 5 — PORT ka dhyaan**
`PORT` **Railway khud set karta hai**. Isko manually mat daalna. Dockerfile ka start command
`${PORT:-5000}` use karta hai, to ye apne aap handle ho jaata hai.

**Step 6 — Deploy check karo**
Build ke baad Railway ek public URL dega. Us URL pe `/healthz` kholo — agar `"status": "ok"`
aa raha hai to sab theek hai. Pehle 10–15 second `"warming"` dikh sakta hai.

**Step 7 — Redeploy**
`main` branch pe push karte hi Railway apne aap dobara deploy kar deta hai.

---

## 15. Health Check

Deployment theek chal raha hai ya nahi, ye check karne ke liye:

```
http://localhost:5000/healthz
```

Response aisa aata hai:

```json
{
  "ok": true,
  "status": "ok",
  "stale": false,
  "message": "",
  "symbols": 68,
  "age_seconds": 12.4,
  "updated_at": 1786568078.7,
  "refresh_seconds": 90,
  "next_refresh_in": 78,
  "market": {
    "state": "CLOSED",
    "label": "Market Closed",
    "detail": "Opens 09:15 IST",
    "open": false
  }
}
```

### Field ka matlab

| Field | Matlab |
|---|---|
| `ok` | Server response de raha hai |
| `status` | `warming` = pehla data aa raha hai · `ok` = data ready hai |
| `stale` | `true` = last refresh fail hua, purana data dikh raha hai |
| `message` | Stale ya warming hone pe user-facing message |
| `symbols` | Kitne symbols ka data snapshot me hai (poora hone pe **68**) |
| `age_seconds` | Data kitne second purana hai |
| `updated_at` | Last successful refresh ka Unix timestamp |
| `refresh_seconds` | Refresh interval (default 90) |
| `next_refresh_in` | Agla refresh kitne second me |
| `market.state` | `PRE` / `OPEN` / `POST` / `CLOSED` |
| `market.label` | Human-readable market status |

Ek aur endpoint version batata hai:
```
http://localhost:5000/version
```
```json
{"version": "v4.1-terminal", "yfinance": "1.5.2"}
```

---

## 16. Troubleshooting

### ❓ "python is not recognized" / Python not found

Python installed nahi hai ya PATH me nahi hai.
- [python.org/downloads](https://www.python.org/downloads/) se install karo
- Install karte waqt **"Add Python to PATH"** checkbox **zaroor tick** karo
- Install ke baad Command Prompt **band karke dobara kholo**
- Windows pe `py --version` bhi try kar sakte ho

### ❓ "pip is not recognized"

```cmd
python -m pip --version
```
Ye chal jaaye to `pip` ki jagah hamesha `python -m pip` use karo:
```cmd
python -m pip install -r requirements.txt
```

### ❓ "ModuleNotFoundError: No module named 'flask'"

Packages install nahi hue, ya venv activate nahi hai.
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```
Terminal me `(venv)` dikh raha hai? Nahi dikh raha to activate nahi hua.

### ❓ requirements install hone me error aa raha hai

- Internet connection check karo
- pip upgrade karo: `python -m pip install --upgrade pip`
- Agar Python 3.9/3.10 pe ho aur error aa raha hai, to Python 3.11+ install karke try karo
- Company/college network pe firewall block kar sakta hai — mobile hotspot pe try karo

### ❓ "Port 5000 is already in use"

Koi aur program us port pe chal raha hai (Mac pe aksar AirPlay).

Windows:
```cmd
set PORT=5050 && python trading_scanner.py
```
Mac / Linux:
```bash
PORT=5050 python3 trading_scanner.py
```
Phir `http://localhost:5050` kholo.

### ❓ Dashboard khali hai / "Updating market data…" dikha raha hai

**Pehle 10–15 second ye normal hai** — background engine pehla snapshot bana raha hai.

Agar 1 minute se zyada ho jaye:
- Internet connection check karo
- `http://localhost:5000/healthz` kholo aur `status` dekho
- Terminal window me error messages dekho

### ❓ "STALE DATA" banner aa raha hai

Ek refresh fail hua hai. Ye **by design** hai — purana data screen pe rehta hai taaki dashboard
blank na ho, aur project apne aap retry karta rehta hai. Usually 1–2 minute me theek ho jaata hai.

Agar baar-baar aa raha hai to Yahoo temporarily rate-limit kar raha ho sakta hai. Thoda ruk jao.

### ❓ Kuch stocks me `--` dikh raha hai

Us symbol ka data provider se nahi aaya. `--` ka matlab hai **"data available nahi"** —
project galat number banane ki jagah honestly `--` dikhata hai.

### ❓ Indicator me "Requested: 15M / Using: Daily fallback" likha aa raha hai

Yahoo ne us symbol ka 15-minute data nahi diya, isliye daily bars use hue. Ye **jaan-boojh kar
dikhaya** jaata hai taaki tumhe pata rahe number kis timeframe ka hai. Ye error nahi hai.

### ❓ AI assistant "not configured" bol raha hai

`GEMINI_API_KEY` set nahi hai. **Ye bilkul normal hai** — baaki poora app chalta rahega.
Enable karna ho to [Section 10](#10-gemini-setup--optional) dekho.

### ❓ Yahoo Finance ka data hi nahi aa raha

- Internet check karo
- Weekend ya holiday pe intraday data purana ho sakta hai
- Kabhi-kabhi Yahoo temporarily block karta hai — 5–10 minute baad try karo
- VPN on hai to off karke dekho

### ❓ Docker build fail ho raha hai

- Docker Desktop chal raha hai? Check karo
- `docker build` project folder ke andar se hi chalao (jahan `Dockerfile` hai)
- Purana cache clear karo: `docker build --no-cache -t ultimate-pro-trading-terminal .`

### ❓ Railway pe app start nahi ho raha

- Railway ka **Deploy Logs** tab kholo, wahan actual error dikhta hai
- `PORT` variable manually set mat karo — Railway khud karta hai
- Build ke baad 15–20 second do, phir `/healthz` check karo
- Dockerfile repo ke root me hona chahiye

---

## 17. Data Limitations

Ye project honest rehne ki koshish karta hai. Ye cheezein jaanna zaroori hai:

**1. Data source aur delay**
Data **Yahoo Finance** se aata hai — ye exchange ka live feed **nahi** hai, delayed data hai.
Isliye app kahin bhi "LIVE" claim nahi karta. Uske badle top bar me **data age** dikhata hai
(jaise "Data age 42s") taaki tumhe hamesha pata rahe data kitna purana hai.

**2. Intraday availability badalti rehti hai**
Yahoo hamesha 5M/15M/1H data nahi deta — kabhi kam bars aate hain, kabhi bilkul nahi.

**3. Timeframe fallback (chhupaya nahi jaata)**
Agar requested intraday timeframe nahi milta, to indicator **daily bars** se calculate hota hai.
Par ye kabhi chhupaya nahi jaata. Stock Analysis page pe har cell pe saaf likha aata hai:

```
Requested: 15M
Using: Daily fallback
```

Upar ek banner bhi aata hai, aur dashboard/screener tables me us value pe ek chhota
hover-able `D` marker aata hai.

**4. Data unavailable**
Agar kisi symbol ka data hi nahi mila, to `--` dikhta hai. **Koi number bana kar nahi dikhaya
jaata.** `NaN`, `null`, `undefined` kahin nahi aayega.

**5. Stale data handling**
Refresh fail hone pe purana valid snapshot screen pe rehta hai aur yellow banner aata hai:
`STALE DATA — last successful update 180s ago`. Dashboard blank nahi hota.

**6. Market holidays**
App market status sirf **time aur weekday** se decide karta hai (NSE session: 09:15–15:30 IST,
Mon–Fri). Ismein **NSE holiday calendar nahi hai** — to kisi holiday pe "Market Open" dikh sakta
hai jabki actually exchange band ho. Reliable holiday source project me include nahi kiya gaya.

**7. Universe ke bahar ke symbols**
Jo symbol scanned list me nahi hai (jaise DMART), uska data on-demand fetch hota hai —
pehli baar 1–3 second lagte hain, phir 5 minute cache rehta hai. Page pe
"Off-universe symbol" badge dikh jaata hai.

**8. Commodity prices approximate hain**
MCX commodities (Gold, Silver, Crude) ke prices Yahoo ke USD futures se live USD/INR rate
laga kar convert kiye jaate hain. Ye **approximate** hain — actual MCX quotes se thoda alag ho
sakte hain.

---

## 18. Options Limitation

> ## ⚠️ Options Lab ke premiums REAL NAHI HAIN
>
> Ye baat bilkul clear honi chahiye.

Options Lab spot price aur strike distance se ek **analytical estimate** banata hai.

**Ye kya NAHI hai:**

| ❌ | Nahi hai |
|---|---|
| ❌ | Live option-chain data |
| ❌ | Real bid / ask prices |
| ❌ | Real Implied Volatility (IV) |
| ❌ | Real Greeks (Delta, Gamma, Theta, Vega) |
| ❌ | Time decay ka calculation |
| ❌ | Broker ya exchange ka koi quote |

**Ye kya HAI:**

| ✅ | Hai |
|---|---|
| ✅ | Position sizing samajhne ka tool |
| ✅ | "Agar premium X se Y ho jaaye to kitna banega/jaayega" ka calculator |
| ✅ | Lot size × quantity ka simple math |

Page pe har jagah **`ESTIMATED / ANALYTICAL`** label lagaya gaya hai, aur API response me bhi
`"estimated": true` flag aata hai.

P&L calculation me **brokerage, STT, exchange fees, GST aur stamp duty shamil nahi** hai.
Short position ke liye jo "capital outlay" dikhta hai wo premium received hai — wo margin
**nahi** hai jo tumhara broker block karega.

**Real trading se pehle apne broker ka actual option chain zaroor dekho.**

---

## 19. Security

Is project me security ka dhyaan rakha gaya hai:

### Kya kiya gaya hai

- ✅ **Code me koi API key ya secret hardcoded nahi hai.** Gemini key sirf `GEMINI_API_KEY`
  environment variable se aati hai — koi hardcoded fallback nahi hai
- ✅ `.env` file `.gitignore` me hai, kabhi commit nahi hogi
- ✅ Key ki value kabhi log me print nahi hoti
- ✅ Har HTTP response pe security headers: Content-Security-Policy, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- ✅ Symbol input strict pattern se validate hota hai data layer tak pahunchne se pehle
- ✅ Saara dynamic text escape hota hai DOM me daalne se pehle (XSS protection)
- ✅ Error hone pe user ko stack trace nahi dikhta — sirf server log me jaata hai

### Tum kya dhyaan rakho

- 🔑 **Apni API key kisi ko share mat karo** — screenshot me bhi nahi
- 🔑 **`.env` file kabhi commit mat karo** aur na hi ZIP me bhejo
- 🔑 **ZIP share karne se pehle** check kar lo ki usme `.env` nahi hai
- 🔑 **Agar galti se koi key leak ho jaye** — sirf file se hataana **kaafi nahi** hai.
  Wo Git history me reh jaati hai. Us key ko provider ke dashboard se **turant revoke
  karke nayi banao**

---

## 20. Folder Structure

```
UltimateProTradingTerminal/
│
├── trading_scanner.py       # Poora backend: data engine, indicators, saare routes
│
├── templates/               # HTML pages (Jinja2)
│   ├── base.html            # Common layout: nav, status bar, AI assistant, footer
│   ├── dashboard.html       # Dashboard page
│   ├── screener.html        # Screener page
│   ├── heatmap.html         # Heatmap page
│   ├── stock.html           # Stock Analysis page
│   ├── watchlist.html       # Watchlist page
│   ├── markets.html         # Markets page
│   ├── options.html         # Options Lab page
│   ├── about.html           # About page
│   └── error.html           # 404 / 500 error page
│
├── static/
│   ├── css/
│   │   └── app.css          # Saari styling: dark + light theme, mobile layout
│   └── js/
│       ├── app.js           # Shared: theme, status strip, global search, assistant
│       ├── dashboard.js     # Dashboard logic
│       ├── screener.js      # Screener filters, sorting, CSV
│       ├── heatmap.js       # Heatmap tiles aur colours
│       ├── stock.js         # Stock Analysis rendering
│       ├── watchlist.js     # Watchlist add/remove/persist
│       ├── markets.js       # Markets page
│       └── options.js       # Options Lab calculator
│
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build (python:3.11-slim + gunicorn)
├── Procfile                 # Process definition (gunicorn command)
├── START.bat                # Windows one-click start
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── PROJECT_INFO.txt         # Short project summary
└── README.md                # Ye file
```

---

## 21. API Overview

Ye saare endpoints actually code me maujood hain. Browser me directly khol kar dekh sakte ho.

### Pages

| Endpoint | Purpose |
|---|---|
| `GET /` | Dashboard |
| `GET /screener` | Screener page |
| `GET /heatmap` | Heatmap page |
| `GET /stock/<SYMBOL>` | Stock Analysis page (jaise `/stock/RELIANCE`) |
| `GET /watchlist` | Watchlist page |
| `GET /markets` | Markets page |
| `GET /options` | Options Lab page |
| `GET /about` | About page |

### Data APIs

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Snapshot status, symbol count, data age, market status |
| `GET /version` | App version aur yfinance version |
| `GET /api/meta` | Sirf snapshot metadata (status, age, next refresh, market) |
| `GET /api/stocks?type=nifty50` | Raw indicator values (JSON). `type` = `nifty50`, `banknifty`, `finnifty`, `commodities`, `giftnifty`, `all` |
| `GET /api/stock/<SYMBOL>` | Ek symbol ki poori detail + timeframe levels |
| `GET /api/indices` | Headline indices (Nifty, Bank Nifty, Fin Nifty, India VIX) + currency rates |
| `GET /api/pulse` | Market breadth + top 5 bullish/bearish setups |
| `GET /api/search?q=REL` | Symbol suggestions (sirf allowed list se) |
| `GET /get_master_table_data?type=nifty50` | Dashboard table ke rendered rows + stats |
| `GET /get_status_bulk?symbols=RELIANCE,TCS` | Ek saath kai symbols ka status (watchlist ke liye) |
| `GET /get_signals?symbol=RELIANCE&interval=15m` | Ek symbol ke levels (EMA, swing, volume, crossover) |
| `GET /get_strike_chain?symbol=RELIANCE` | Analytical strike ladder (estimated premiums) |
| `GET /get_movers` | Top gainers aur losers |
| `GET /get_currency_rate` | USD/INR, CNY, RUB, CAD rates |
| `GET /export.csv?type=nifty50` | Segment ka CSV download |
| `GET /gemini_chat?message=explain+RELIANCE` | AI assistant (key set ho to) |

---

## 22. Development Guide

Agar tum code padhna ya modify karna chahte ho:

### Backend logic — `trading_scanner.py`

Poora backend ek hi file me hai, clearly sections me divided:

| Section | Kya milega |
|---|---|
| **Universe** | Symbol lists (`NIFTY50_STOCKS`, `BANKNIFTY_STOCKS` wagairah), ticker mapping, lot sizes |
| **Market clock** | `market_status()` — NSE session logic |
| **Data engine** | `batch_history()` — batch download; `_pick()` — timeframe fallback logic |
| **Indicators** | `compute_metrics()` — saare indicators yahan calculate hote hain. `_rsi()`, `_adx()` helper functions |
| **Rendering** | `render_row()`, `badge()`, `tf_flag()` — HTML rows banate hain |
| **Snapshot store** | `build_snapshot()`, `refresh_loop()`, `mark_stale()` — cache aur background thread |
| **HTTP** | Saare `@app.route` handlers |

### Kahan kya hai

| Cheez | Location |
|---|---|
| **Market data fetch** | `batch_history()` — sirf yahi function Yahoo se baat karta hai |
| **Indicators calculate** | `compute_metrics()` aur `compute_detail()` |
| **Snapshot / cache** | `SNAPSHOT` global dict + `build_snapshot()` + `refresh_loop()` thread |
| **Timeframe fallback** | `_pick()` return karta hai `(frame, interval_actually_used)` |
| **Signal Score** | `compute_metrics()` ke end me; bands `score_band()` me |
| **Templates** | `templates/` — `base.html` common layout hai, baaki usko extend karte hain |
| **CSS** | `static/css/app.css` — ek hi file, tokens (CSS variables) se dono theme chalte hain |
| **Shared JS** | `static/js/app.js` — theme, status strip, search, assistant, formatting helpers |
| **Page JS** | `static/js/<page>.js` — har page ka apna script |

### Important patterns

- **Snapshot immutable hai** — `build_snapshot()` ek naya dict banata hai aur `SNAPSHOT`
  ko wholesale replace kar deta hai. Readers ko lock nahi chahiye
- **`_num()` helper** har numeric value ko finite-check karta hai, taaki NaN kabhi UI tak na pahunche
- **`escapeHtml()`** frontend me har dynamic text pe lagta hai
- **`clean_symbol()`** backend me har symbol input validate karta hai

---

## 23. How To Customize

### Refresh interval badalna

`.env` file me:
```
REFRESH_SECONDS=120
```
> ⚠️ Isse **60 se kam mat karna** — Yahoo rate-limit kar dega aur data aana band ho jaayega.

### Theme badalna

App me hi top-right corner me 🌙 / ☀️ button hai. Choice browser me save ho jaati hai.

Colours change karne ho to `static/css/app.css` ke top me CSS variables hain:
```css
:root[data-theme="dark"] {
    --bg: #0b0d11;
    --accent: #4c8dff;
    --bull: #2fbf71;
    --bear: #f0555f;
    ...
}
```
Bas ye values badal do — poore app me apply ho jaayega.

### Watchlist badalna

App me hi `/watchlist` page pe add/remove kar sakte ho. Browser ke localStorage me save hota hai.

Default list badalni ho to `static/js/watchlist.js` me:
```javascript
const DEFAULT_LIST = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN'];
```

### Symbols add/remove karna

`trading_scanner.py` me lists hain:
```python
NIFTY50_STOCKS = [...]
BANKNIFTY_STOCKS = [...]
FINNIFTY_STOCKS = [...]
COMMODITIES_STOCKS = [...]
```

> ⚠️ **Dhyaan rakho:** `NIFTY50_STOCKS` me **exactly 50 symbols** hone chahiye — app start hote
> hi ek assertion check karta hai aur galat count pe app chalega hi nahi. Ye jaan-boojh kar
> rakha hai taaki galti pakdi jaaye.

Naya symbol add karne se pehle confirm kar lo ki Yahoo pe wo ticker exist karta hai
(Indian stocks ke liye `.NS` suffix lagta hai — code khud laga deta hai).

### Naya page add karna

1. `templates/` me naya HTML banao jo `base.html` ko extend kare
2. `static/js/` me uska script banao
3. `trading_scanner.py` me ek `@app.route` add karo
4. `templates/base.html` ke nav `links` list me entry add karo

### Gemini configuration

Model change karna ho to `trading_scanner.py` me `gemini_chat()` function me:
```python
model="gemini-2.5-flash"
```

> 🔒 **Key kabhi code me mat likhna.** Hamesha `.env` ya environment variable use karo.

---

## 24. Known Limitations

Honest list — ye cheezein project abhi nahi karta:

1. **Data delayed hai** — Yahoo Finance ka delayed data, exchange ka live feed nahi
2. **Market holiday calendar nahi hai** — status sirf time aur weekday se decide hota hai,
   to NSE holiday pe "Market Open" dikh sakta hai
3. **Options premiums estimated hain** — koi IV nahi, koi Greeks nahi, koi real chain nahi
4. **Timeframe fallback hota hai** — intraday data na mile to daily use hota hai
   (par ye hamesha UI me dikhaya jaata hai, chhupaya nahi jaata)
5. **CSP me `unsafe-inline` hai** — markup me inline `onclick` handlers use hote hain.
   Baaki har CSP directive strict hai
6. **Watchlist sirf browser me save hoti hai** — devices ya browsers ke beech sync nahi hoti
7. **Off-universe symbols slow hain** — pehli baar 1–3 second lagte hain (live fetch), phir 5 min cache
8. **Single worker zaroori hai** — cache process memory me hai, multiple workers duplicate
   fetching karenge
9. **Rate limiting nahi hai** — personal use ke liye theek hai, public multi-user deployment
   ke liye add karna padega
10. **Commodity prices approximate hain** — USD futures se USD/INR laga kar convert kiye jaate hain
11. **Koi database nahi hai** — sab kuch memory me hai, restart pe snapshot dobara banta hai
    (10–15 second)
12. **Historical charts nahi hain** — charts ke liye TradingView / Groww ke links diye gaye hain

---

## 25. Project Information

| | |
|---|---|
| **Project Name** | Ultimate Pro Trading Terminal |
| **Version** | `v4.1-terminal` |
| **Purpose** | Personal Trading Analytics / Education / Research |
| **Symbols tracked** | 68 (50 Nifty 50 + Bank Nifty + Fin Nifty + Commodities + Indices) |
| **Pages** | 8 |
| **Indicators** | 10 per symbol + Signal Score |
| **Refresh interval** | 90 seconds (configurable) |
| **Data source** | Yahoo Finance (delayed) via `yfinance` |
| **Backend** | Python 3, Flask, Gunicorn |
| **Computation** | Pandas, NumPy |
| **Frontend** | Vanilla JavaScript, Bootstrap 5, custom CSS (koi build step nahi) |
| **AI** | Google Gemini (optional) |
| **Deployment** | Docker, Railway |

---

## 26. Final Quick Start

### 🪟 WINDOWS (sabse aasan)

```
1. ZIP extract karo
2. START.bat pe double-click karo
3. Browser me kholo: http://localhost:5000
```

### 💻 MANUAL (Windows)

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python trading_scanner.py
```

### 🍎 MANUAL (macOS / Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 trading_scanner.py
```

### 🐳 DOCKER

```bash
docker build -t ultimate-pro-trading-terminal .
docker run -p 5000:5000 ultimate-pro-trading-terminal
```

**Phir browser me:** http://localhost:5000
**Band karne ke liye:** `Ctrl + C`
**Pehli baar 10–15 second lagenge** — background engine data laa raha hota hai.

---

<div align="center">

**Made for learning.** 🚀

Code padho, tod-phod karo, seekho — sab kuch `trading_scanner.py` aur `static/js/` me
clearly likha hua hai.

*Ye investment advice nahi hai. Trading risk tumhara apna hai.*

</div>
