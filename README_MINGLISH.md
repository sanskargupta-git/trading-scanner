# 📊 Ultimate Pro Trading Terminal
## Installation Guide (Marathi + English)

> ## 📖 Konti file vaachaychi?
>
> | Tumhala kaay pahije? | File |
> |---|---|
> | 🔧 **Project install karaycha aahe** (hi file) | **README_MINGLISH.md** — Marathi |
> | 🔧 **Project install karna hai** | **[README.md](README.md)** — Hinglish |
> | 🖥️ **Website kashi vaparaychi te samjun ghyaycha aahe** | **[USER_GUIDE_MINGLISH.md](USER_GUIDE_MINGLISH.md)** — Marathi |
> | 🖥️ **Website kaise use kare samajhna hai** | **[USER_GUIDE.md](USER_GUIDE.md)** — Hinglish |
>
> Tumhala fakt website vaparaychi asel (install nahi karaychi), tar direct
> **[USER_GUIDE_MINGLISH.md](USER_GUIDE_MINGLISH.md)** ughada.

---

> ### ⚡ SUPER QUICK START (Windows)
> 1. ZIP file **extract** kara
> 2. Folder madhe **`START.bat`** var double-click kara
> 3. Browser madhe ughada → **http://localhost:5000**
>
> **Manual (konatyahi OS var):**
> ```
> python -m venv venv
> venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
> pip install -r requirements.txt
> python trading_scanner.py
> ```
> Pahilya vela table bharayla **10–15 second** lagtat. He normal aahe.

---

## 📑 Index

| # | Section | # | Section |
|---|---|---|---|
| 1 | [Project kaay aahe](#1-project-kaay-aahe) | 9 | [Gemini setup (optional)](#9-gemini-setup--optional) |
| 2 | [Disclaimer](#2-important-disclaimer) | 10 | [.env setup](#10-env-setup) |
| 3 | [Computer madhe kaay pahije](#3-computer-madhe-kaay-pahije) | 11 | [START.bat kaay karto](#11-startbat-nakki-kaay-karto) |
| 4 | [Sopa marg — Windows](#4-sagat-sopa-marg--windows) | 12 | [Docker setup](#12-docker-setup) |
| 5 | [Windows manual setup](#5-windows-manual-setup) | 13 | [Railway deployment](#13-railway-deployment) |
| 6 | [macOS setup](#6-macos-setup) | 14 | [Health check](#14-health-check) |
| 7 | [Linux setup](#7-linux-setup) | 15 | [Troubleshooting](#15-troubleshooting) |
| 8 | [Project kasa chaalto](#8-project-kasa-chaalto) | 16 | [Security ani limitations](#16-security) |

---

## 1. Project kaay aahe

He ek **personal trading analytics dashboard** aahe jyat tumhi Nifty 50, Bank Nifty,
Fin Nifty, Commodities ani dusre market segments ekach thikani baghu shakta.

**Problem kaay hoti?**
Market baghayla saathi saadharan pane 10 vegveglya chart tabs ughadavya lagtat — ekat RSI,
ekat MACD, ekat price. Pratyek stock sathi he parat parat karava lagta. Khup vel jato.

**Ha project kaay karto?**
Yahoo Finance madhun **kharokhar cha market data** aanto, tyavar standard technical indicators
calculate karto, ani sagla ekach clean terminal-style dashboard madhe dakhavto. Ekun
**68 symbols** track hotat ani dar **90 second** la data apoap refresh hoto.

Kuthlahi fake data nahi aahe. Screen var jo number disto to kharokhar chya market data pasun
calculate hoto. Ekhadya cha data nahi milala tar project `--` dakhavto — **number banavun
dakhavat nahi**.

---

## 2. Important Disclaimer

> ### ⚠️ He vaachnech garjeche aahe

- 📚 Ha project **fakt education ani research** sathi aahe
- ❌ He **investment advice nahi** aahe
- ❌ Kuthlahi **buy/sell recommendation nahi** aahe
- ❌ **Profit chi kuthlihi guarantee nahi** aahe
- ⚠️ **Technical signals chukiche asu shaktat** — kuthlahi indicator future sangu shakat nahi
- ⏱️ **Market data delayed aahe** (Yahoo Finance), live exchange feed nahi aahe
- 🧮 Options Lab che premiums **estimated** aahet, khare exchange quotes nahi

Kuthlahi trading decision ghenya adhi tumchya broker cha kharokhar cha data check kara.
Market madhe paise lavnyacha risk purnpane tumcha aahe.

---

## 3. Computer madhe kaay pahije

| Kaay | Kiti pahije |
|---|---|
| **OS** | Windows, macOS kinva Linux — tinhi chaltat |
| **Python** | **3.11 kinva tya pudhcha recommended.** Hech verified aahe: Docker image `python:3.11-slim` vaparto, ani local testing Python 3.13 var zali aahe. `requirements.txt` cha floor 3.9 aahe, mhanun 3.9/3.10 var pan install honyachi shakyata aahe — pan mi test kela nahi |
| **Internet** | **Garjeche aahe.** Market data internet varun yeto. Offline chalvala tar tables rikamech rahtil |
| **Browser** | Konatahi modern browser — Chrome, Edge, Firefox, Safari. Internet Explorer support nahi |
| **RAM** | Sadharan vaparat kahi shambhar MB. Kuthlihi khaas requirement nahi — jo computer Python chalvu shakto to purese aahe |
| **Disk** | Project swatah ~75 KB. Dependencies (pandas, numpy, yfinance) ~300–400 MB gheu shaktat |

---

## 4. Sagat sopa marg — Windows

Hi application tumchya computer var run karaychi asel tar first ZIP extract kara.

### STEP 1 — ZIP download kara
Milalelya ZIP file la tumchya computer var save kara (Downloads folder madhech theek aahe).

### STEP 2 — ZIP extract kara
ZIP file var **right-click** → **Extract All...** → **Extract**

Ek folder tayar hoil: **`UltimateProTradingTerminal`**

### STEP 3 — Folder ughada
Tya folder chya aat ja. Tumhala `trading_scanner.py`, `START.bat`, `templates`, `static`
he sagla disel.

### STEP 4 — START.bat var double-click kara

Windows asel tar **START.bat var double-click kara**. Basa, evdach.

Ek kali window (Command Prompt) ughadel ani ti apoap he karel:
1. Python install aahe ka te check karel
2. `requirements.txt` madhun sagle packages install karel
3. Project suru karel

> **First time dependencies install hone mule 1-2 minutes lagoo shaktat.**
> Ghabru naka, window band karu naka.

### STEP 5 — Browser ughada

```
http://localhost:5000
```

> ⏳ **Pahile 10–15 second** "Updating market data…" disel. Background engine pahila
> snapshot tayar karat asto. Page apoap bharel — refresh karaychi garaj nahi.

### Band karaycha asel tar

Tya kali window madhe **`Ctrl + C`** dabaa. Kinva window band kara.

### START.bat kaam nahi kela tar

Manual setup vaparaa — [Section 5](#5-windows-manual-setup) baghaa.

---

## 5. Windows manual setup

Project folder madhe Command Prompt ughadaa (folder chya address bar madhe `cmd` type
karun Enter dabaa).

**Step 1 — Python check kara**
```cmd
python --version
```
`Python 3.11.x` kinva tya pudhcha disla pahije.
"not recognized" ala tar [python.org](https://www.python.org/downloads/) varun install kara —
ani install kartana **"Add Python to PATH"** checkbox **nakki tick kara**.

**Step 2 — Virtual environment banvaa**
```cmd
python -m venv venv
```
(Yamule project che packages tumchya system Python pasun vegle rahtil — safe asta.)

**Step 3 — Activate kara**
```cmd
venv\Scripts\activate
```
Aata terminal madhe line chya survatila `(venv)` disayla lagel.

**Step 4 — Packages install kara**
```cmd
pip install -r requirements.txt
```

**Step 5 — Project chalvaa**
```cmd
python trading_scanner.py
```

**Step 6 — Browser ughadaa**
```
http://localhost:5000
```

**Band karaycha asel tar:** `Ctrl + C`

---

## 6. macOS setup

Terminal ughadaa ani project folder madhe ja (`cd ` type karun folder drag-drop kara).

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

Mag browser madhe ughadaa:
```
http://localhost:5000
```

**Band karaycha asel tar:** `Ctrl + C`

> ⚠️ **Mac var port 5000 cha issue:** macOS cha AirPlay Receiver pan port 5000 vaparto.
> Error ala tar vegdya port var chalvaa:
> ```bash
> PORT=5050 python3 trading_scanner.py
> ```
> Mag `http://localhost:5050` ughadaa.

---

## 7. Linux setup

```bash
# 1. Python check
python3 --version

# 2. venv module nasel tar (Ubuntu/Debian var kahi vela vegla yeto)
sudo apt install python3-venv python3-pip

# 3. Virtual environment banvaa
python3 -m venv venv

# 4. Activate kara
source venv/bin/activate

# 5. Packages install
pip install -r requirements.txt

# 6. Run
python3 trading_scanner.py
```

Browser madhe ughadaa: `http://localhost:5000`

**Deactivate karaycha asel tar** (venv madhun baher yeaayla):
```bash
deactivate
```

**Production style (gunicorn ne):**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 8 --timeout 120 trading_scanner:app
```

> ⚠️ **Nehami `--workers 1` thevaa.** Cache ani background thread process chya memory madhe
> astat. Jasta workers cha artha pratyek worker swatacha vegla data aanel — Yahoo var
> load vaadhel.

---

## 8. Project kasa chaalto

```
   Yahoo Finance (market data)
              │
              ▼
   ┌──────────────────────────────────────────┐
   │  BACKGROUND DATA ENGINE                  │
   │  (ek thread, dar 90 second)              │
   │                                          │
   │  Batch Fetch: fakt 4 requests            │
   │  (5M, 15M, 1H, 1D — sagle 70 tickers)    │
   │              │                           │
   │              ▼                           │
   │  Technical Indicators calculate          │
   │              │                           │
   │              ▼                           │
   │  SNAPSHOT CACHE (memory madhe)           │
   └──────────────┬───────────────────────────┘
                  │  (handlers fakt vaachtat)
                  ▼
   ┌──────────────────────────────────────────┐
   │  Flask API  →  Frontend (browser)        │
   │  Response time: ~10-20 milliseconds      │
   └──────────────────────────────────────────┘
```

### Hi architecture ka aahe?

**Sadha marg (jo kaam karat nahi):** pratyek page load la pratyek stock cha data vegla
manvaa. 50 stocks × 5 timeframes = **250+ requests**. Parinaam:
- Page nehami timeout hoto
- Yahoo rate-limit karun block karto
- Pratyek visitor purna load parat tayar karto

**Mhanun:** ek background thread dar 90 second la **4 batch requests** madhe purna universe
cha data aanto, ekda indicators calculate karto, ani memory madhe snapshot thevto.

> ### 🔑 Mahatvacha niyam
> **Sadha page request kadhihi Yahoo la direct hit karat nahi.**
> Pratyek page ani API fakt snapshot vaachta. Mhanunach response 10–20ms madhe yeto.

**Refresh fail zala tar:** juna valid snapshot screen var rahto ani **STALE DATA** mark hoto.
Dashboard rikama hot nahi.

---

## 9. Gemini setup — OPTIONAL

> ### ✅ Gemini purnpane optional aahe
> Yashivay pan **purna dashboard normal chalto** — sagle pages, scanner, stock analysis,
> watchlist, options, sagla kahi. Assistant fakt ek extra feature aahe.

### API key kashi banvaychi

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) var ja
2. Google account ne login kara
3. **Create API Key** var click kara
4. Key copy kara

### Key set karaycha marg

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

**Kinva `.env` file madhe** (sagat sopa — [Section 10](#10-env-setup) baghaa):
```
GEMINI_API_KEY=your_key_here
```

### Assistant kasa kaam karto

Jevha tumhi `explain RELIANCE` vicharta, tevha server aadhi swatachya snapshot madhun tya
symbol che **kharokhar che aata che numbers** kaadhto — price, daily %, signal score, MACD,
EMA, DOW, Bollinger, RSI, ADX — ani te Gemini la pathvto. Prompt madhe spashta lihilela asta
ki **fakt hech numbers explain kara, swatah kuthla number banvu naka**.

Chat window chya khali nehami hi line disate:
> *AI-generated explanation is informational and may contain errors.*

> 🔒 **Tumchi API key kunala pan deu naka ani Git madhe commit karu naka.**

---

## 10. .env setup

Settings denyacha sagat sopa marg.

**Step 1 — `.env.example` copy karun `.env` banvaa**

Windows:
```cmd
copy .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

**Step 2 — `.env` Notepad kinva konatyahi text editor madhe ughadun edit kara**

### Supported variables

He tinach variables code madhe kharokhar vaachle jatat — ani tinhi **optional** aahet:

| Variable | Default | Kaay karta |
|---|---|---|
| `PORT` | `5000` | Konatya port var app chalel. 5000 busy asel tar `5050` kara |
| `REFRESH_SECONDS` | `90` | Kiti second nantar background engine data refresh karel. **Khup lahan karu naka** — Yahoo rate-limit karel |
| `GEMINI_API_KEY` | *(rikama)* | AI assistant enable karta. Rikama thevla tar assistant band rahto, baaki sagla chalto |

Example `.env`:
```
PORT=5000
REFRESH_SECONDS=90
GEMINI_API_KEY=
```

> 🔒 `.env` file `.gitignore` madhe aahe — ti kadhihi Git madhe commit honar nahi.
> Tumchi key kadhihi direct code madhe lihu naka.

---

## 11. START.bat nakki kaay karto

`START.bat` ek Windows shortcut aahe. Double-click kelyavar to nakki **tin kama** karto:

1. **Python check** — `python --version` chalvun baghto ki Python install ani PATH madhe aahe ka.
   Nasel tar spashta message deto ki python.org varun install kara ani "Add Python to PATH"
   tick kara, mag thambto
2. **Dependencies install** — `python -m pip install -r requirements.txt` chalvto.
   Fail zala tar internet connection check karayla sangto
3. **App start** — `python trading_scanner.py` chalvto ani sangto ki
   `http://localhost:5000` ughadaa

> ### ⚠️ Ek goshta spashta karto
> **START.bat virtual environment (venv) banvat nahi.** To packages tumchya sadhya chya
> Python madhech install karto. Tumhala tumcha system Python swachh thevaycha asel tar
> [Section 5](#5-windows-manual-setup) cha manual setup vaparaa jyat venv banto.

---

## 12. Docker setup

Project madhe `Dockerfile` aadhich aahe (base image: `python:3.11-slim`).

**Build kara:**
```bash
docker build -t ultimate-pro-trading-terminal .
```

**Run kara:**
```bash
docker run -p 5000:5000 ultimate-pro-trading-terminal
```

Browser madhe ughadaa:
```
http://localhost:5000
```

**Environment variables sobat:**
```bash
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key_here \
  -e REFRESH_SECONDS=90 \
  ultimate-pro-trading-terminal
```

**Kinva `.env` file ne:**
```bash
docker run -p 5000:5000 --env-file .env ultimate-pro-trading-terminal
```

Container chya aat app gunicorn ne chalto — 1 worker, 8 threads, 120s timeout.

---

## 13. Railway deployment

Railway var deploy karna sopa aahe karan `Dockerfile` aadhich tayar aahe.

**Step 1 — Code GitHub var push kara**
```bash
git init
git add .
git commit -m "Ultimate Pro Trading Terminal"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

> 🔒 Push karnya adhi confirm kara ki `.env` commit hot nahi. `.gitignore` madhe aadhich
> aahe, pan ekda `git status` ne check kara.

**Step 2 — Railway project banvaa**
[railway.app](https://railway.app) var ja → **New Project** → **Deploy from GitHub repo**
→ tumcha repo select kara.

**Step 3 — Dockerfile detection**
Railway swatah `Dockerfile` detect karel ani tyane build karel. Extra config lagat nahi.

**Step 4 — Environment variables (optional)**
Project → **Variables** tab → **New Variable**:
- `GEMINI_API_KEY` = tumchi key (assistant pahije asel tar)
- `REFRESH_SECONDS` = `90` (default barobar aahe)

**Step 5 — PORT cha laksha**
`PORT` **Railway swatah set karta**. He manual takū naka. Dockerfile cha start command
`${PORT:-5000}` vaparto, mhanun he apoap handle hota.

**Step 6 — Deploy check kara**
Build nantar Railway ek public URL deil. Tya URL var `/healthz` ughadaa — `"status": "ok"`
yet asel tar sagla theek aahe.

**Step 7 — Redeploy**
`main` branch var push kelya varach Railway apoap parat deploy karta.

---

## 14. Health check

Deployment barobar chalu aahe ka he check karnyasathi:

```
http://localhost:5000/healthz
```

Response asa yeto:

```json
{
  "ok": true,
  "status": "ok",
  "stale": false,
  "symbols": 68,
  "age_seconds": 12.4,
  "refresh_seconds": 90,
  "next_refresh_in": 78,
  "market": { "state": "CLOSED", "label": "Market Closed" }
}
```

| Field | Artha |
|---|---|
| `ok` | Server response det aahe |
| `status` | `warming` = pahila data yet aahe · `ok` = data tayar aahe |
| `stale` | `true` = last refresh fail zala, juna data disat aahe |
| `symbols` | Kiti symbols cha data snapshot madhe aahe (purna zalyavar **68**) |
| `age_seconds` | Data kiti second juna aahe |
| `refresh_seconds` | Refresh interval (default 90) |
| `next_refresh_in` | Pudhcha refresh kiti second madhe |
| `market.state` | `PRE` / `OPEN` / `POST` / `CLOSED` |

Version baghayla:
```
http://localhost:5000/version
```

---

## 15. Troubleshooting

### ❓ "python is not recognized" / Python sapadat nahi

Python install nahi kinva PATH madhe nahi.
- [python.org/downloads](https://www.python.org/downloads/) varun install kara
- Install kartana **"Add Python to PATH"** checkbox **nakki tick kara**
- Install nantar Command Prompt **band karun parat ughadaa**
- Windows var `py --version` pan try kara

### ❓ "pip is not recognized"

```cmd
python -m pip --version
```
He chalala tar `pip` chya aivaji nehami `python -m pip` vaparaa.

### ❓ "ModuleNotFoundError: No module named 'flask'"

Packages install nahi zale, kinva venv activate nahi.
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```
Terminal madhe `(venv)` disat aahe ka? Nasel tar activate zala nahi.

### ❓ requirements install hotana error yeto

- Internet connection check kara
- pip upgrade kara: `python -m pip install --upgrade pip`
- Python 3.9/3.10 var asal ani error yet asel tar Python 3.11+ install karun baghaa
- Office/college network var firewall block karu shakto — mobile hotspot var try kara

### ❓ "Port 5000 is already in use"

Dusra program tya port var chalat aahe (Mac var bahutek AirPlay).

Windows:
```cmd
set PORT=5050 && python trading_scanner.py
```
Mac / Linux:
```bash
PORT=5050 python3 trading_scanner.py
```

### ❓ Dashboard rikama aahe / "Updating market data…" disat aahe

**Pahile 10–15 second he normal aahe** — background engine pahila snapshot tayar karat aahe.

1 minute peksha jasta zala tar:
- Internet connection check kara
- `http://localhost:5000/healthz` ughadun `status` baghaa
- Terminal window madhe error baghaa

### ❓ "STALE DATA" banner yet aahe

Ek refresh fail zala aahe. He **muddam** asa design kela aahe — juna data screen var rahto
jenekarun dashboard rikama honar nahi, ani project apoap parat try karat rahto.
Saadharan 1–2 minute madhe theek hota.

### ❓ Kahi stocks madhe `--` disat aahe

Tya symbol cha data provider kadun ala nahi. `--` cha artha **"data uplabdh nahi"** —
project chukicha number banvnya aivaji pramanikpane `--` dakhavto.

### ❓ "Requested: 15M / Using: Daily fallback" asa lihilela yeto

Yahoo ne tya symbol cha 15-minute data dila nahi, mhanun daily bars vaparle. He **muddam
dakhavla** jata jenekarun tumhala kalel ki number konatya timeframe cha aahe. Ha error nahi.

### ❓ AI assistant "not configured" mhanto

`GEMINI_API_KEY` set nahi. **He purnpane normal aahe** — baaki purna app chalat rahil.

### ❓ Yahoo Finance cha data yet nahi

- Internet check kara
- Weekend kinva holiday la intraday data juna asu shakto
- Kahi vela Yahoo tatpurta block karto — 5–10 minute nantar try kara
- VPN on asel tar off karun baghaa

### ❓ Docker build fail hoto

- Docker Desktop chalu aahe ka? Check kara
- `docker build` project folder chya aatunach chalvaa (jithe `Dockerfile` aahe)
- Juna cache clear kara: `docker build --no-cache -t ultimate-pro-trading-terminal .`

### ❓ Railway var app suru hot nahi

- Railway cha **Deploy Logs** tab ughadaa, tithe kharokhar cha error disto
- `PORT` variable manual set karu naka — Railway swatah karta
- Build nantar 15–20 second dyaa, mag `/healthz` check kara
- Dockerfile repo chya root madhe pahije

---

## 16. Security

### Kaay kela gela aahe

- ✅ **Code madhe kuthlihi API key kinva secret hardcoded nahi.** Gemini key fakt
  `GEMINI_API_KEY` environment variable madhun yete — kuthlahi hardcoded fallback nahi
- ✅ `.env` file `.gitignore` madhe aahe, kadhihi commit honar nahi
- ✅ Key chi value kadhihi log madhe print hot nahi
- ✅ Pratyek HTTP response var security headers: Content-Security-Policy, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- ✅ Symbol input strict pattern ne validate hoto
- ✅ Sagla dynamic text escape hoto DOM madhe taknya adhi (XSS protection)
- ✅ Error ala tar user la stack trace disat nahi — fakt server log madhe jato

### Tumhi kaay laksha thevaa

- 🔑 **Tumchi API key kunala share karu naka** — screenshot madhe pan nahi
- 🔑 **`.env` file kadhihi commit karu naka** ani ZIP madhe pathvu naka
- 🔑 **ZIP share karnya adhi** check kara ki tyat `.env` nahi
- 🔑 **Chukun key leak zali tar** — fakt file madhun kaadhna **purese nahi**. Ti Git history
  madhe rahte. Tya key la provider chya dashboard varun **lagech revoke karun navi banvaa**

---

## 📋 Known Limitations

Pramanik yaadi — ya goshti project sadhya karat nahi:

1. **Data delayed aahe** — Yahoo Finance cha delayed data, exchange cha live feed nahi
2. **Market holiday calendar nahi** — status fakt vel ani divas varun tharto, mhanun
   NSE holiday la "Market Open" disu shakta
3. **Options premiums estimated aahet** — IV nahi, Greeks nahi, khara chain nahi
4. **Timeframe fallback hoto** — intraday data nasel tar daily vaparla jato
   (pan he nehami UI madhe dakhavla jata, lapavla jat nahi)
5. **CSP madhe `unsafe-inline` aahe** — markup madhe inline `onclick` handlers vaparle aahet
6. **Watchlist fakt browser madhe save hote** — devices madhe sync hot nahi
7. **Off-universe symbols slow aahet** — pahilya vela 1–3 second, mag 5 min cache
8. **Single worker garjeche aahe** — cache process memory madhe aahe
9. **Rate limiting nahi** — personal vaparasathi theek, public deployment sathi add karava lagel
10. **Commodity prices approximate aahet** — USD futures varun USD/INR laavun convert kele jatat
11. **Database nahi** — sagla memory madhe, restart var snapshot parat banto (10–15 second)
12. **Historical charts nahit** — charts sathi TradingView / Groww che links dile aahet

---

## 📁 Folder Structure

```
UltimateProTradingTerminal/
├── trading_scanner.py       # Purna backend: data engine, indicators, sagle routes
├── templates/               # HTML pages (base, dashboard, screener, heatmap,
│                            #   stock, watchlist, markets, options, about, error)
├── static/
│   ├── css/app.css          # Sagli styling: dark + light theme, mobile layout
│   └── js/                  # app.js (shared) + pratyek page cha script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build (python:3.11-slim + gunicorn)
├── Procfile                 # Process definition
├── START.bat                # Windows one-click start
├── .env.example             # Environment variable template
├── .gitignore
├── PROJECT_INFO.txt
├── README.md                # Installation guide (Hinglish)
├── README_MINGLISH.md       # Hi file (Marathi)
├── USER_GUIDE.md            # Website vaparaycha guide (Hinglish)
└── USER_GUIDE_MINGLISH.md   # Website vaparaycha guide (Marathi)
```

---

## ⚡ Final Quick Start

### 🪟 WINDOWS (sagat sopa)
```
1. ZIP extract kara
2. START.bat var double-click kara
3. Browser madhe ughadaa: http://localhost:5000
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

**Mag browser madhe:** http://localhost:5000
**Band karayla:** `Ctrl + C`
**Pahilya vela 10–15 second lagtil** — background engine data aanat asto.

---

<div align="center">

**Shikanya sathi banavla aahe.** 🚀

Website kashi vaparaychi te samjun ghyaycha asel tar →
**[USER_GUIDE_MINGLISH.md](USER_GUIDE_MINGLISH.md)**

*He investment advice nahi aahe. Trading cha risk tumcha swatacha aahe.*

</div>
