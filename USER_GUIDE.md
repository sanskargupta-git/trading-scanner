# 📊 Ultimate Pro Trading Terminal
## Simple User Guide

> **Ye guide un logon ke liye hai jo website use karna chahte hain.**
> Coding ya technical knowledge ki bilkul zaroorat nahi hai.
> Sab kuch bilkul simple bhasha me samjhaya gaya hai.

> ## 📖 Doosri files
>
> | Chahiye | File |
> |---|---|
> | 🖥️ **Website guide (Marathi)** | **[USER_GUIDE_MINGLISH.md](USER_GUIDE_MINGLISH.md)** |
> | 🔧 **Install karna hai (Hinglish)** | **[README.md](README.md)** |
> | 🔧 **Install karaycha aahe (Marathi)** | **[README_MINGLISH.md](README_MINGLISH.md)** |

---

## 🙏 Sabse pehle — ye padh lo

Ye website **market ko samajhne aur different stocks ko compare karne** ke liye banayi gayi hai.
Isme aap **Nifty 50, Bank Nifty, commodities aur individual stocks** ko ek hi jagah dekh sakte ho —
har stock ke liye alag-alag app kholne ki zaroorat nahi.

> ### ⚠️ Zaroori baat
>
> **Ye website sirf information aur learning ke liye hai.
> Ye guaranteed profit ya investment advice nahi deti.**
>
> - Yahan jo bhi green/red dikhta hai wo **buy/sell ka order nahi** hai
> - Koi bhi indicator future **predict nahi** kar sakta
> - Paisa lagane se pehle apne broker ka actual data zaroor dekho
> - Nuksan ya faayda — dono ki zimmedari aapki apni hai

Agar aapko trading ka bilkul bhi experience nahi hai, to is website ko **seekhne ka tool**
samjho — market kaise chalta hai, alag-alag numbers ka kya matlab hota hai, ye samajhne ke liye.

---

## 📑 Is guide me kya-kya hai

| Section | Kya milega |
|---|---|
| [Website kholne ke baad](#-website-kholne-ke-baad) | Sabse pehle kya dikhega |
| [Upar ki patti](#-upar-ki-patti-status-bar) | Market status, data kitna purana hai |
| [Colours ka matlab](#-colours-ka-matlab) | Green, Red, Yellow, Grey |
| [Signal Score](#-signal-score-kya-hai) | Ek number me poora summary |
| [Indicators simple bhasha me](#-indicators--bilkul-simple-bhasha-me) | Har indicator ka aasan matlab |
| [Page-by-page guide](#-page-by-page-guide) | Har page kaise use kare |
| [Data status](#-data-status--fresh-stale-unavailable) | FRESH / STALE / UNAVAILABLE |
| [Timeframe fallback](#-timeframe-fallback-ka-matlab) | "Requested / Using" kyun likha aata hai |
| [CSV download](#-csv-download-kaise-kare) | Excel me data nikalna |
| [Mobile pe](#-mobile-phone-pe-kaise-chalta-hai) | Phone pe use karna |
| [Common questions](#-common-questions-faq) | 15 sawaal-jawab |
| [Safety](#-safety--responsible-use) | Zimmedari se use karna |

---

## 🏠 Website kholne ke baad

Jaise hi aap website khologe, sabse upar **4 bade box** dikhenge:

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  NIFTY 50    │  BANK NIFTY  │  FIN NIFTY   │  INDIA VIX   │
│  24,471.70   │  57,446.25   │  26,903.35   │    11.86     │
│  -0.46%      │  -0.42%      │  +1.31%      │   -3.18%     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

Har box me **teen cheezein** hoti hain:
1. **Naam** (upar) — kaunsa index hai
2. **Number** (beech me) — abhi ki value
3. **Percentage** (neeche) — aaj kitna upar/neeche gaya

Percentage **green** ho to aaj badha hai, **red** ho to aaj gira hai.

---

### 📈 NIFTY 50 kya hai?

**Nifty 50 India ki 50 badi companies ka ek group hai.**

Socho aise: agar aap India ki 50 sabse badi companies — Reliance, TCS, HDFC Bank, Infosys
wagairah — ko ek saath dekhna chaho, to har ek ko alag-alag dekhna padega. Bahut mushkil.

Isliye ek **average jaisa number** banaya gaya hai — usko Nifty 50 kehte hain.

- Nifty **upar** ja raha hai → matlab zyadatar badi companies aaj achha kar rahi hain
- Nifty **neeche** ja raha hai → matlab zyadatar companies aaj gir rahi hain

> 💡 Ye market ka "overall mood" batata hai.

---

### 🏦 BANK NIFTY kya hai?

**Bank Nifty sirf banking sector ke bade stocks ka index hai.**

Jaise Nifty 50 poore market ka mood batata hai, waise hi Bank Nifty sirf **banks ka mood**
batata hai — HDFC Bank, ICICI Bank, SBI, Axis Bank wagairah.

Kabhi-kabhi poora market girta hai par banks badhte hain, ya ulta. Isliye alag se dekhte hain.

---

### 💳 FIN NIFTY kya hai?

**Fin Nifty financial companies ka index hai.**

Isme banks to hain hi, saath me **insurance companies (SBI Life, HDFC Life),
NBFC (Bajaj Finance, Shriram Finance)** jaisi financial companies bhi hain.

Matlab Bank Nifty se thoda bada group — poora "paise ka business" karne wala sector.

---

### 😰 INDIA VIX kya hai?

**India VIX market me kitna dar (fear) aur uncertainty hai, wo batata hai.**

Isko "fear index" bhi kehte hain. Simple tarike se samjho:

- VIX **kam** hai → market shaant hai, log relaxed hain
- VIX **zyada** hai → market me ghabrahat hai, log nervous hain, badi movement ho sakti hai

> ⚠️ **Dhyaan do:** VIX ka number **prediction nahi** hai. Ye sirf batata hai ki abhi market me
> kitni uncertainty hai. Iska matlab ye nahi ki market girega ya badhega — sirf ye ki
> **movement badi ho sakti hai**.
>
> Is website me VIX ke liye koi "khatra" ya "safe" ka level nahi diya gaya, kyunki aisa koi
> fixed rule nahi hota.

---

## 🕐 Upar ki patti (Status Bar)

Bade boxes ke bilkul upar ek patli patti hoti hai. Isme kaafi kaam ki cheezein hoti hain:

```
● Market Closed · Opens 09:15 IST | Last updated 14:23:05 | Data age 12s | Next refresh 78s
```

| Kya likha hai | Matlab |
|---|---|
| **● Market Closed** | Abhi market band hai (bayein taraf ka dot bhi colour badalta hai) |
| **Opens 09:15 IST** | Market kab khulega |
| **Last updated 14:23:05** | Data aakhri baar kis time aaya tha |
| **Data age 12s** | Data 12 second purana hai |
| **Next refresh 78s** | 78 second baad naya data aayega |

---

### 🚦 Market Status ka matlab

| Dikhega | Matlab | Time (IST) |
|---|---|---|
| 🟢 **Market Open** | Market chal raha hai, prices live badal rahe hain | 09:15 – 15:30 |
| 🟡 **Pre-Market** | Market khulne wala hai, thodi der me | 09:00 – 09:15 |
| 🟠 **Post-Market** | Market abhi-abhi band hua hai | 15:30 – 16:00 |
| 🔴 **Market Closed** | Market band hai (raat, subah, ya weekend) | Baaki time + Sat/Sun |

> ### ⚠️ Ek important limitation
>
> Ye website **sirf time aur din** dekh kar market status batati hai.
> **Isme exchange ki holiday list nahi hai.**
>
> Matlab agar kisi din **Diwali, Holi ya koi aur market holiday** ho, to website "Market Open"
> dikha sakti hai jabki actually market band hoga.
>
> Isliye **actual holiday NSE ki website ya apne broker se hi confirm karo.**

---

## 🎨 Colours ka matlab

Poori website me colours ka ek hi matlab hai. Ek baar samajh lo, sab jagah kaam aayega:

| Colour | Matlab | Example |
|---|---|---|
| 🟢 **Green** | Positive / bullish indication — cheez upar ki taraf ja rahi hai | `▲ Bullish`, `+2.34%`, `Golden` |
| 🔴 **Red** | Negative / bearish indication — cheez neeche ki taraf ja rahi hai | `▼ Bearish`, `-1.20%`, `Death` |
| 🟡 **Yellow** | Neutral / clear nahi hai — koi direction nahi bata raha | `Flat` |
| ⚪ **Grey** | Data available nahi hai, ya kuch khaas nahi ho raha | `--`, `Normal`, `WAIT` |

> ### 🚨 Ye sabse important baat hai
>
> **Green ka matlab "buy karo" NAHI hai.
> Red ka matlab "sell karo" NAHI hai.**
>
> Green sirf itna batata hai ki *us ek indicator ke hisaab se* recent movement upar ki taraf
> thi. Bas itna. Wo aage bhi upar hi jaayega — iski **koi guarantee nahi** hai.
>
> Market me green ke baad turant red bhi aa sakta hai. Colour ko **information** samjho,
> **order** nahi.

---

## 🎯 Signal Score kya hai?

Ye website har stock ko ek **number** deti hai — usko Signal Score kehte hain.

### Ye kaam kaise karta hai?

Website har stock pe **7 alag-alag cheezein** check karti hai (MACD, RSI, EMA wagairah — inke
baare me neeche detail me padhoge).

- Har cheez agar **positive** direction dikhaye → **+1**
- Har cheez agar **negative** direction dikhaye → **−1**

Sab jodne ke baad jo number aata hai wo Signal Score hai. Ye **−7 se +7** ke beech rehta hai.

### Score ka matlab

| Score | Kya likha aayega | Simple matlab |
|---|---|---|
| **+4 ya zyada** | 🟢 STRONG BULLISH | Zyadatar indicators positive direction dikha rahe hain |
| **+1 se +3** | 🟢 BULLISH | Thoda positive jhukav hai |
| **0** | ⚪ NEUTRAL | Mixed hai — kuch positive, kuch negative |
| **−1 se −3** | 🔴 BEARISH | Thoda negative jhukav hai |
| **−4 ya kam** | 🔴 STRONG BEARISH | Zyadatar indicators negative direction dikha rahe hain |

### Example se samjho

Maan lo RELIANCE ka score **+5** hai. Iska matlab:

> "Abhi jo 7 cheezein check ki gayi hain, unme se zyadatar positive direction dikha rahi hain."

**Iska matlab ye NAHI hai:**
- ❌ "RELIANCE badhega"
- ❌ "RELIANCE kharido"
- ❌ "Ye safe hai"

**Iska matlab sirf ye hai:**
- ✅ "Abhi ke available data me indicators aapas me agree kar rahe hain"

> ### ⚠️ Signal Score ek SUMMARY hai, PREDICTION nahi
>
> Ye sirf batata hai ki **abhi kitne indicators ek hi direction me hain**.
> Ye future ka koi guarantee nahi deta. 7 me se 7 indicators positive hone ke baad bhi
> stock gir sakta hai — ye market me normal baat hai.

---

## 📚 Indicators — bilkul simple bhasha me

Ye website har stock pe **10 indicators** dikhaati hai. Ghabrao mat — ek-ek karke sab simple
bhasha me samjhaate hain.

> **"Indicator" kya hota hai?**
> Indicator ek calculation hai jo purane price data se banta hai. Ye batata hai ki
> *ab tak kya hua*. Ye ye nahi batata ki *aage kya hoga*.
>
> Jaise gaadi ka speedometer batata hai ki aap abhi kitni speed pe ho — par ye nahi batata
> ki 10 minute baad kitni speed hogi.

---

### 1️⃣ 🔥 Big Candle

**Ye kya hai?**
Har thodi der me stock ka price upar-neeche hota hai. Us movement ko "candle" kehte hain.
Big Candle check karta hai ki ye movement **normal se bahut zyada badi** to nahi thi.

**Simple matlab:**
Agar last 15 minute me stock me achanak badi movement hui hai, to ye "Big Candle" dikhata hai.
Matlab kuch important ho raha hai — koi news, koi badi buying/selling.

| Dikhega | Matlab |
|---|---|
| 🟢 **▲ Big Bull** | Badi movement hui, aur upar ki taraf thi |
| 🔴 **▼ Big Bear** | Badi movement hui, aur neeche ki taraf thi |
| ⚪ **Normal** | Koi khaas badi movement nahi hui |

> ⚠️ **Warning:** Badi movement ka matlab ye nahi ki wo continue rahegi. Kabhi-kabhi badi
> movement ke turant baad ulta bhi ho jaata hai.

---

### 2️⃣ ⚡ MACD

**Ye kya hai?**
MACD stock ki movement ki **strength aur direction** samajhne ke liye use hota hai.
Ye do alag-alag "average prices" ko compare karta hai — ek fast, ek slow.

**Simple matlab:**
Socho aap ek gaadi chala rahe ho. MACD batata hai ki aap **tez ho rahe ho ya dheeme**.

| Dikhega | Matlab |
|---|---|
| 🟢 **▲ Bullish** | Recent movement positive ho sakti hai |
| 🔴 **▼ Bearish** | Recent movement negative ho sakti hai |
| ⚪ **--** | Data available nahi hai |

> ⚠️ **Warning:** MACD future guarantee nahi karta. Ye sirf batata hai ki **ab tak** kya hua.

---

### 3️⃣ 📈 DOW Breakout

**Ye kya hai?**
Ye check karta hai ki stock ne apni **pichhli height ko cross kiya** ya apne **pichhle low
ko tod diya**.

**Simple matlab:**
Socho ek stock pichhle kuch ghanton se ₹100 tak hi jaa raha tha, aur wapas gir jaata tha.
Ab agar wo ₹100 cross kar gaya — to ye "breakout" hai. Kuch naya ho raha hai.

| Dikhega | Matlab |
|---|---|
| 🟢 **BUY** | Stock ne pichhla high cross kiya |
| 🔴 **SELL** | Stock ne pichhla low tod diya |
| ⚪ **WAIT** | Abhi kuch nahi hua, range me hi hai |

> ⚠️ **Warning:** Yahan **"BUY" ka matlab kharidne ka order nahi hai!** Ye sirf ek technical
> word hai jo batata hai ki price ne upar ki taraf ek level cross kiya. Kai baar breakout
> ke turant baad price wapas gir jaata hai (isko "false breakout" kehte hain).

---

### 4️⃣ ⚔️ EMA Crossover

**Ye kya hai?**
EMA matlab "average price". Ye do average compare karta hai — ek **short time** ka
(20 candles), ek **lamba time** ka (50 candles).

**Simple matlab:**
Agar recent average, purane average se **upar** nikal jaaye — matlab abhi ka trend purane
trend se behtar hai. Isko **"Golden"** kehte hain.
Ulta ho to **"Death"** kehte hain.

| Dikhega | Matlab |
|---|---|
| 🟢 **Golden** | Recent average, purane average se upar hai |
| 🔴 **Death** | Recent average, purane average se neeche hai |

> ⚠️ **Warning:** Naam dara dene wale hain ("Golden", "Death") par ye sirf technical terms
> hain. "Death" ka matlab company dubne wali hai — aisa **bilkul nahi** hai.

---

### 5️⃣ 📊 Bollinger Band

**Ye kya hai?**
Ye stock ke price ke aas-paas ek **upar aur neeche ki line** banata hai. Normally price
in dono lines ke beech me rehta hai.

**Simple matlab:**
Socho ek road hai jiske dono taraf boundary hai. Bollinger Band batata hai ki gaadi
(price) boundary ke paas pahunch gayi hai ya beech me hai.

| Dikhega | Matlab |
|---|---|
| 🟢 **▲ Up** | Price upar wali line ke paas pahunch gaya hai |
| 🔴 **▼ Down** | Price upar wali line se door hai |

> ⚠️ **Warning:** Upar wali line touch karne ka matlab "abhi girega" ya "aur badhega" —
> dono me se kuch bhi ho sakta hai. Ye sirf position batata hai.

---

### 6️⃣ 📉 RSI (number)

**Ye kya hai?**
RSI ek number hai **0 se 100** ke beech. Ye batata hai ki stock **haal hi me zyada
kharida gaya** hai ya **zyada becha gaya** hai.

**Simple matlab:**
Socho ek dukan pe koi cheez bahut zyada bik rahi hai — stock bhi waise hi "overheated"
ho sakta hai.

| RSI number | Kya kehte hain | Simple matlab |
|---|---|---|
| **70 se upar** | Overbought | Haal hi me bahut kharida gaya hai |
| **30 se 70** | Neutral zone | Normal hai |
| **30 se neeche** | Oversold | Haal hi me bahut becha gaya hai |

> ⚠️ **Warning:** Ye sabse zyada galat samjha jaane wala indicator hai.
> **"Overbought" ka matlab "abhi girega" nahi hai** — stock RSI 80 pe rehte hue bhi hafton
> tak badh sakta hai. Waise hi "Oversold" ka matlab "abhi badhega" nahi hai.

---

### 7️⃣ 📉 RSI Trend

**Ye kya hai?**
RSI ka number pichhli baar se **badha ya ghata**, bas ye batata hai.

| Dikhega | Matlab |
|---|---|
| 🟢 **Uptick** | RSI badh raha hai |
| 🔴 **Downtick** | RSI ghat raha hai |
| 🟡 **Flat** | RSI same hai |

> ⚠️ **Warning:** Ye bahut chhoti si movement bhi dikha deta hai. Akela dekh kar koi
> conclusion mat nikalo.

---

### 8️⃣ 🎯 DMI

**Ye kya hai?**
DMI compare karta hai ki **upar ki movement zyada hai ya neeche ki**.

**Simple matlab:**
Rassa-kashi (tug of war) socho — ek taraf kharidne wale, dusri taraf bechne wale.
DMI batata hai ki abhi kaun aage hai.

| Dikhega | Matlab |
|---|---|
| 🟢 **Bullish Cross** | Upar ki movement zyada strong hai |
| 🔴 **Bearish Cross** | Neeche ki movement zyada strong hai |

> ⚠️ **Warning:** Ye sirf abhi ki position batata hai. Rassa-kashi me dono taraf ka zor
> kabhi bhi badal sakta hai.

---

### 9️⃣ 🎯 ADX (number)

**Ye kya hai?**
ADX batata hai ki jo bhi movement chal rahi hai, wo **kitni mazboot** hai.
Ye **direction nahi** batata — sirf **strength** batata hai.

**Simple matlab:**
- ADX **kam** (20 se neeche) → movement kamzor hai, stock idhar-udhar ghoom raha hai
- ADX **zyada** (25 se upar) → movement me dum hai, ek clear direction chal raha hai

| ADX number | Simple matlab |
|---|---|
| **25 se upar** | Trend me dum hai |
| **20 se 25** | Trend ban raha hai |
| **20 se neeche** | Kamzor / koi clear trend nahi |

> ⚠️ **Warning:** ADX zyada hone ka matlab "achha" nahi hai — trend **neeche ki taraf** bhi
> strong ho sakta hai! Direction ke liye dusre indicators dekhne padte hain.

---

### 🔟 🎯 ADX Trend

**Ye kya hai?**
ADX ka number badh raha hai ya ghat raha hai.

| Dikhega | Matlab |
|---|---|
| 🟢 **Uptick** | Trend aur mazboot ho raha hai |
| 🔴 **Downtick** | Trend kamzor ho raha hai |
| 🟡 **Flat** | Same hai |

> ⚠️ **Warning:** Yahan bhi green ka matlab "achha" nahi — sirf "trend strong ho raha hai".

---

> ## 🧠 Sabse zaroori baat — sab indicators ke baare me
>
> Ye saare indicators **purane price data se bante hain**. Matlab ye sab batate hain ki
> **ab tak kya hua**. Inme se koi bhi **future nahi bata sakta**.
>
> Isliye:
> - Kabhi ek indicator dekh kar decision mat lo
> - 7 me se 7 green hone ke baad bhi stock gir sakta hai
> - Ye "signals" nahi, sirf "information" hai

---

## 🗺️ Page-by-page guide

Website me **8 pages** hain. Upar navigation bar me sabke button hain.

---

### 🏠 Dashboard

Ye **home page** hai — yahan sabse zyada important cheezein ek saath dikhti hain.

**Yahan kya milega (upar se neeche):**

1. **4 index boxes** — Nifty 50, Bank Nifty, Fin Nifty, India VIX
2. **Market Pulse** — poore market ka mood:
   - Kitne stocks **Bullish** hain
   - Kitne **Bearish**
   - Kitne **Neutral**
   - **Top Gainer** — aaj sabse zyada badhne wala stock
   - **Top Loser** — aaj sabse zyada girne wala stock
3. **Top Bullish Setups** — 5 stocks jinka score sabse zyada hai
4. **Top Bearish Setups** — 5 stocks jinka score sabse kam hai
5. **My Watchlist** — aapke save kiye hue stocks
6. **Tables** — Nifty 50, Bank Nifty, Fin Nifty, Commodities, Gift Nifty

**Tips:**
- Kisi bhi stock ke naam pe click karo → uska poora analysis khulega
- Table ke heading pe click karo → table chhup/khul jaayega
- Nifty 50 table ke upar ek search box hai — us table me stock dhoondhne ke liye

---

### 🔍 Screener

**Screener me aap 50 stocks ko ek saath compare kar sakte ho.**

Ye page ek badi table hai jisme har stock ki saari information ek line me dikhti hai.

**Kaise use kare:**

**1. Universe choose karo** — kaun se stocks dekhne hain
```
Nifty 50 / Bank Nifty / Fin Nifty / Commodities / Gift Nifty / Everything
```

**2. Filter lagao** — signal bias se
```
All  |  Strong Bullish  |  Bullish  |  Neutral  |  Bearish  |  Strong Bearish
```

> **Example:** Sirf bullish stocks dekhne hain to **Bullish** filter choose karo.
> Turant sirf wahi stocks dikhenge.

**3. Sort karo** — kis hisaab se order lagana hai
```
Signal Score / Daily % / RSI / ADX / Price / Symbol A-Z
```
Saath me **High → Low** ya **Low → High** bhi choose kar sakte ho.
Jis column pe sorting chal rahi hai uske naam ke aage ▲ ya ▼ dikhega.

**4. Search karo** — koi specific stock dhoondhna ho to search box me naam type karo

**5. Result count dekho** — upar likha aayega:
```
Showing 23 of 50 stocks
```
Matlab 50 me se 23 stocks aapke filter pe fit ho rahe hain.

**6. CSV download** — ⬇ Export CSV button se saara data Excel me nikal sakte ho

---

### 🔥 Heatmap

**Har company ek rangeen box (tile) me dikhti hai.**

Ye page ek nazar me poora market dikhata hai. Har tile me:
- Company ka naam
- Aaj ka percentage
- Price
- Signal band (STRONG BULLISH wagairah)

**Colour ka matlab:**

| Colour | Matlab |
|---|---|
| 🟢 **Gehra green** | Aaj achha khaasa upar gaya |
| 🟢 Halka green | Thoda upar gaya |
| ⚪ Grey | Lagbhag same hai |
| 🔴 Halka red | Thoda neeche gaya |
| 🔴 **Gehra red** | Aaj achha khaasa neeche gaya |

**Colour badal bhi sakte ho** — upar dropdown se:
- **Colour by daily %** — aaj ki movement se (default)
- **Colour by signal score** — score se
- **Colour by RSI** — RSI se

**Stock pe click karne se Stock Analysis page khul jaata hai.**

> Tiles sab ek hi size ke hote hain aur aaj ki movement ke hisaab se order me lage hote hain
> (sabse zyada badhne wala pehle). Company ka size ya market cap yahan use **nahi** hota.

---

### 📊 Stock Analysis

**Ye ek stock ki poori detail dikhata hai.** Sabse detailed page yahi hai.

**Kaise kholein:**
1. Upar right side me **search box** me stock ka naam type karo (jaise `RELIANCE`)
2. Suggestion list me se click karo
3. **Ya** kisi bhi page pe stock ke naam pe click kar do

**Yahan kya milega:**

**Upar (hero section):**
- **Stock ka naam** — jaise RELIANCE
- **Signal Score aur Band** — jaise `+5 STRONG BULLISH`
- **Current Price** — jaise ₹1,323.90
- **Daily %** — aaj kitna upar/neeche
- **Market status, data fresh hai ya nahi, data kitna purana hai**

**Indicator Grid:**
Saare 10 indicators ek grid me. Har box me indicator ka naam, uska **timeframe**, aur value.

**Timeframe buttons (5M, 15M, 1H, 1D):**

| Button | Matlab |
|---|---|
| **5M** | 5 minute ki movement |
| **15M** | 15 minute ki movement |
| **1H** | 1 ghante ki movement |
| **1D** | Poore din (daily) ki movement |

Chhota timeframe = zyada detail par zyada shor (noise)
Bada timeframe = kam detail par zyada clear picture

**Timeframe Levels:**
Us timeframe ke important numbers — EMA 20, EMA 50, swing high, swing low, volume wagairah.

**Technical Summary:**
Sab kuch ek jagah simple bhasha me:
- **Trend** — Bullish / Bearish / Neutral
- **Momentum** — Positive / Negative
- **Strength** — ADX ke hisaab se
- **Volatility** — kitna utaar-chadhaav hai
- **RSI** — number aur uska matlab
- **Signals Agreeing** — kitne indicators aapas me agree kar rahe hain

**Data Status:**
Market status, last updated time, data age, data fresh hai ya stale.

**Buttons:**
- **Open TradingView ↗** — proper chart dekhne ke liye (nayi tab me khulega)
- **+ Watchlist** — is stock ko apni watchlist me daalne ke liye

---

### ⭐ Watchlist

**Jo stocks baar-baar dekhne hain, unko Watchlist me save karo.**

**Stock add karna:**
1. `/watchlist` page kholo
2. Box me stock ka naam type karo (jaise `WIPRO`)
3. **Add** button dabao

**Ya:** Kisi bhi stock ke Analysis page pe **+ Watchlist** button dabao.

**Stock hataana:**
Us stock ke card me upar-right corner me **✕** dabao.

**Search karna:**
Filter box me type karo — sirf matching stocks dikhenge.

**Stock kholna:**
Card me stock ke naam pe click karo → Analysis page khul jaayega.

**Har card me dikhega:**
Symbol, Price, Daily %, Signal Score, Trend, aur data kitna purana hai.

> ### 💾 Watchlist kahan save hoti hai?
>
> Aapki watchlist **usi browser me, usi computer pe** save hoti hai jahan aapne banayi hai.
>
> Iska matlab:
> - Doosre computer pe khologe → watchlist nahi dikhegi
> - Doosre browser me khologe (Chrome se Firefox) → nahi dikhegi
> - Mobile pe khologe → alag watchlist hogi
> - Browser ka data/history clear karoge → **watchlist chali jaayegi**
>
> Ye kisi account me save nahi hoti. Agar list chali jaaye to **↺ Reset to default**
> se default list wapas aa jaati hai.

---

### 🌍 Markets

**Saare market segments ek jagah, card format me.**

Yahan milega:

| Section | Kya hai |
|---|---|
| **Headline Indices** | Nifty 50, Bank Nifty, Fin Nifty, India VIX |
| **Nifty 50** | 50 badi companies |
| **Bank Nifty** | Banking sector |
| **Fin Nifty** | Financial sector |
| **Commodities (MCX)** | Gold, Silver, Crude Oil, Natural Gas, Copper |
| **Gift Nifty & Indices** | Index instruments |
| **Currencies** | USD/INR, USD/CNY, USD/RUB, USD/CAD |

Har card pe click karo → us stock ka Analysis khul jaayega.
Har section pe ⬇ CSV button bhi hai.

> ### ⚠️ Commodities ke prices ke baare me
>
> Gold, Silver, Crude ke prices Yahoo se **US dollar** me aate hain. Website unko current
> USD/INR rate laga kar rupees me convert karti hai.
>
> Isliye ye prices **approximate** hain — actual MCX ke rate se thode alag ho sakte hain.
> Actual trading ke liye MCX ya apne broker ka rate hi dekho.

---

### 🧮 Options Lab

> ## 🚨 SABSE PEHLE YE PADHO
>
> **Ye page ek CALCULATOR hai. Ye live option chain NAHI hai.**
>
> Jo premium prices (CE/PE ke numbers) yahan dikhte hain, wo website ne
> **spot price se calculate** kiye hain. Ye:
>
> - ❌ Exchange ke **real prices nahi** hain
> - ❌ Real **bid/ask nahi** hain
> - ❌ Real **IV (Implied Volatility) nahi** hai
> - ❌ Real **Greeks (Delta, Theta) nahi** hain
>
> Page pe har jagah **ESTIMATED / ANALYTICAL** likha hua hai — yahi iska matlab hai.
>
> **Actual option trading ke liye apne broker ka real option chain hi dekho.**

**Phir ye page kis kaam ka hai?**

Ye samajhne ke liye ki **"agar premium X se Y ho jaaye to kitna profit/loss hoga"**.
Matlab position sizing aur calculation practice ke liye.

**Kaise use kare:**

**1. Underlying choose karo** — kis stock ka option (jaise RELIANCE), phir **Load** dabao

**2. Spot Price dekho** — us stock ka current price

**3. Strike ladder se ek strike pe click karo** — CE (green) ya PE (red) number pe

**4. Details bharo:**

| Field | Matlab |
|---|---|
| **Side** | Buyer (Long) ya Seller (Short) |
| **Lot Size** | Ek lot me kitne shares (auto aa jaata hai) |
| **Quantity (lots)** | Kitne lot lene hain |
| **Entry Premium** | Kis price pe liya |
| **Exit Premium** | Kis price pe becha |

**5. Result dekho:** Total Quantity, Capital Outlay, Estimated P&L, P&L %

---

#### 📝 Simple example

Maan lo:

```
Side           = Buyer (Long)
Entry Premium  = ₹70
Exit Premium   = ₹100
Lot Size       = 250
Quantity       = 1 lot
```

**Calculation:**

```
Difference     = ₹100 − ₹70  = ₹30
Total Quantity = 250 × 1      = 250
Estimated P&L  = ₹30 × 250    = ₹7,500  ✅
Capital lagaya = ₹70 × 250    = ₹17,500
P&L %          = 7,500 ÷ 17,500 × 100 = 42.86%
```

> ### ⚠️ Is calculation me kya SHAMIL NAHI hai
>
> - ❌ Brokerage (broker ki fees)
> - ❌ STT (Securities Transaction Tax)
> - ❌ Exchange charges
> - ❌ GST
> - ❌ Stamp duty
>
> Real trading me ye sab kat te hain, to actual profit **isse kam** hoga.
>
> Aur agar aap **Seller (Short)** ho, to jo "Capital Outlay" dikhta hai wo aapko mila hua
> premium hai — wo **margin nahi** hai jo aapka broker block karega. Margin usually
> bahut zyada hota hai.

---

### ✨ AI Assistant (Gemini)

Website ke **bottom-right corner** me ek ✨ button hai. Uspe click karo to chat window khulega.

**Kya pooch sakte ho:**
```
explain RELIANCE
analyse TCS
HDFCBANK ke bare me batao
```

**Ye kaam kaise karta hai:**
Jab aap kisi stock ka naam lete ho, website us stock ke **actual current numbers**
(price, MACD, RSI, ADX, score) AI ko bhejti hai. AI unhi numbers ko simple bhasha me
samjhaata hai.

> ### ⚠️ AI ke baare me zaroori baatein
>
> - **AI galat ho sakta hai.** Chat window ke neeche hamesha likha rehta hai:
>   *"AI-generated explanation is informational and may contain errors."*
> - **AI ko financial advice mat samjho**
> - AI ko sirf wahi numbers milte hain jo website ke paas hain — wo apne se koi price
>   ya number nahi bana sakta
> - Agar koi data available nahi hai to AI bata dega ki available nahi hai

**Agar AI kaam na kare:**
Agar aapko message mile ki *"The AI assistant is not configured"* — matlab AI feature
setup nahi hai. **Ye bilkul normal hai.** Baaki poori website normal chalti rahegi —
saare pages, saare indicators, sab kuch.

---

### ℹ️ About

Is page pe technical detail hai — har indicator ka formula, architecture, tech stack.
Agar aap detail me jaana chahte ho to ye padho.

---

## 📶 Data Status — FRESH, STALE, UNAVAILABLE

Website hamesha saaf-saaf batati hai ki data kitna bharosemand hai.

| Status | Matlab | Kya karna chahiye |
|---|---|---|
| 🟢 **FRESH DATA** | Data abhi-abhi aaya hai, sab theek hai | Normal use karo |
| 🟡 **STALE DATA** | Last update fail hua, purana data dikha rahe hain | Thoda ruko, apne aap theek ho jaayega |
| 🟡 **DATA UNAVAILABLE** | Abhi data aa hi nahi raha | Internet check karo, ya thodi der baad try karo |

### "Stale" ka matlab kya hai?

**Stale matlab: website ke paas last successful data hai, lekin latest update abhi nahi aaya.**

Aisa kyun hota hai? Kabhi-kabhi data dene wali service (Yahoo Finance) thodi der ke liye
jawab nahi deti — internet slow ho, ya unka server busy ho.

**Aise waqt website do cheezein kar sakti thi:**

1. ❌ Screen khali kar deti — sab kuch gayab
2. ✅ **Purana data dikhati rehti aur saaf bata deti ki ye purana hai**

Website **doosra tarika** use karti hai. Upar yellow patti aa jaati hai:

```
⚠ Stale data - last successful update 180s ago
```

> ### 💡 Ye behtar kyun hai?
>
> Kyunki **purana data, jhoothe data se hamesha behtar hai.**
>
> Agar website 3 minute purana price dikha rahi hai aur aapko **bata bhi rahi hai** ki ye
> 3 minute purana hai — to aap samajh-boojh kar decision le sakte ho.
>
> Par agar wo koi number bana kar dikha de, to aapko pata hi nahi chalega ki wo galat hai.
> **Isliye ye website kabhi number banati nahi.**

Website apne aap retry karti rehti hai. Usually 1–2 minute me data wapas FRESH ho jaata hai.

---

## ⏱️ Timeframe fallback ka matlab

Kabhi-kabhi Stock Analysis page pe aapko aisa dikhega:

```
Requested: 15M
Using: Daily fallback
```

**Iska matlab kya hai?**

Website ne 15-minute ka data maanga tha, par data dene wali service ne wo nahi diya.
To website ne **daily (poore din ka) data** use kar liya.

**Aur sabse important baat:** website ne aapko **bata diya**.

> ### 💡 Ye kyun important hai?
>
> Socho agar website 15M likh kar chupchaap daily ka data dikha deti. Aap samajhte ki
> ye pichhle 15 minute ki movement hai, jabki wo actually poore din ki movement hai.
> **Bilkul galat samajh baithte.**
>
> Isliye website saaf-saaf likh deti hai ki maanga kya tha aur mila kya. Ye **error nahi hai** —
> ye honesty hai.

Tables (Dashboard, Screener) me aisi value ke aage ek chhota **`D`** likha aata hai.
Mouse le jaao to poori baat dikh jaayegi.

Aur agar data bilkul hi na mile, to **`--`** dikhta hai — matlab "data available nahi hai".

---

## 📥 CSV download kaise kare

### CSV file kya hoti hai?

CSV ek simple file hoti hai jisme table ka data hota hai. Isko **Excel** ya **Google Sheets**
me khol sakte ho — bilkul normal table ki tarah dikhega.

Faayda: aap apne hisaab se sort kar sakte ho, calculations kar sakte ho, ya record rakh sakte ho.

### Kahan se download kare

| Page | Button kahan hai |
|---|---|
| **Dashboard** | Har table ke heading ke right side me — **⬇ CSV** |
| **Markets** | Har section ke right side me — **⬇ CSV** |
| **Screener** | Upar right side me — **⬇ Export CSV** (jo filter lagaya hai wahi data aayega) |

### Excel me kaise kholein

1. Button pe click karo — file download ho jaayegi (usually **Downloads** folder me)
2. File pe **double-click** karo — Excel me khul jaayegi
3. Agar Excel install nahi hai to [Google Sheets](https://sheets.google.com) pe jaao →
   **File → Import → Upload** → file select karo

### CSV me kya hoga

Symbol, Price, Daily %, Signal Score, aur saare indicators — har stock ki ek row.

---

## 📱 Mobile phone pe kaise chalta hai

**Haan, website phone pe bilkul chalti hai.** Kuch install karne ki zaroorat nahi —
bas browser me link kholo.

**Phone pe kya alag hota hai:**

| Cheez | Phone pe |
|---|---|
| **Tables** | Badi table ki jagah har stock ka apna **card** ban jaata hai — side me scroll nahi karna padta |
| **Navigation** | Upar wale buttons side me scroll ho jaate hain |
| **Search** | Upar search box waise hi kaam karta hai |
| **Watchlist** | Poori tarah kaam karti hai (par phone ki watchlist alag hogi — computer wali se separate) |
| **Stock Analysis** | Saare indicators do-do ke jode me dikhte hain |
| **Heatmap** | Chhote tiles me, par sab dikhte hain |

**Tip:** Browser me website ko **bookmark** kar lo, ya "Add to Home Screen" karo —
phir app ki tarah ek click me khul jaayegi.

---

## ❓ Common Questions (FAQ)

### 1. Ye website buy/sell signal deti hai?

**Nahi.** Ye website sirf **information** dikhati hai — prices, indicators, calculations.
"BUY" aur "SELL" jaise words jo dikhte hain wo **technical terms** hain (matlab price ne
koi level cross kiya), **order nahi**.

Kya kharidna hai ya bechna hai — ye decision poori tarah aapka hai.

---

### 2. Data live hai?

**Nahi, data delayed hai.** Ye data Yahoo Finance se aata hai, jo exchange ka live feed nahi
hai. Isliye website kahin bhi "LIVE" nahi likhti.

Uske badle wo saaf-saaf **"Data age 42s"** likhti hai — matlab data 42 second purana hai.
Isse aapko hamesha pata rehta hai.

---

### 3. Data kitna delayed ho sakta hai?

Data har **90 second** me refresh hota hai. Uske upar Yahoo ka apna delay bhi hota hai.

Upar patti me hamesha exact age dikhta hai. Agar STALE dikh raha hai to zyada purana ho
sakta hai — wahan bhi exact time likha hota hai.

---

### 4. Green ka matlab buy karna hai?

**Bilkul nahi.** 🚫

Green sirf itna batata hai ki *us ek indicator ke hisaab se* recent movement upar ki taraf
thi. Wo aage bhi upar jaayega — iski koi guarantee nahi.

Market me green ke turant baad red bhi aa sakta hai.

---

### 5. Red ka matlab sell karna hai?

**Nahi.** Red sirf batata hai ki recent movement neeche ki taraf thi.

Kai baar red ke baad stock wapas upar chala jaata hai. Red ko "information" samjho,
"warning" ya "order" nahi.

---

### 6. Signal Score kya hai?

7 indicators me se kitne positive direction dikha rahe hain, uska summary number hai.
**−7 se +7** tak. Zyada number = zyada indicators agree kar rahe hain.

Par ye **prediction nahi** hai — sirf abhi ki position ka summary hai.
[Detail me padho](#-signal-score-kya-hai)

---

### 7. MACD kya hai?

MACD stock ki movement ki strength aur direction samajhne ke liye ek calculation hai.
Green matlab recent movement positive ho sakti hai, red matlab negative.

Ye future guarantee nahi karta. [Detail me padho](#2️⃣--macd)

---

### 8. RSI kya hai?

RSI ek number hai 0 se 100 ke beech. Ye batata hai ki stock haal hi me zyada kharida gaya
hai (70+) ya zyada becha gaya (30 se kam).

**Dhyaan do:** "Overbought" ka matlab "abhi girega" **nahi** hota.
[Detail me padho](#6️⃣--rsi-number)

---

### 9. Options Lab real option chain hai?

**Nahi.** 🚫 Ye ek **calculator** hai. Jo premium numbers dikhte hain wo website ne
spot price se calculate kiye hain — exchange ke real prices nahi hain.

Real option trading ke liye apne broker ka actual chain hi dekho.
[Detail me padho](#-options-lab)

---

### 10. Gemini (AI) zaroori hai?

**Bilkul nahi.** AI assistant ek **optional** feature hai.

Agar wo configured nahi hai to sirf chat button kaam nahi karega. **Baaki poori website
bilkul normal chalegi** — saare pages, saare indicators, watchlist, options, sab kuch.

---

### 11. Data update hone me time kyun lagta hai?

Website **ek saath 68 symbols** ka data laati hai. Agar har stock ke liye alag request
bhejti to 250+ requests jaate — server slow ho jaata aur data dene wali service block
kar deti.

Isliye website **ek baar me sab ka data laati hai** aur memory me rakh leti hai. Isi wajah
se pages turant khulte hain (milliseconds me), par pehli baar 10–15 second lagte hain.

---

### 12. `--` kyun dikh raha hai?

`--` ka matlab hai **"is cheez ka data available nahi hai"**.

Website ke paas do option the:
1. ❌ Koi number bana kar dikha dena
2. ✅ **Saaf bata dena ki data nahi hai**

Website **doosra** tarika use karti hai. Isliye `--` dekh kar ghabrao mat — ye honesty hai.
Aksar agle refresh me data aa jaata hai.

---

### 13. Market closed hone par data purana kyun lagta hai?

Kyunki market band hone ke baad **prices badalte hi nahi**. Jo last price tha wahi rehta hai.

Weekend pe ya raat me aapko wahi numbers dikhenge jo market band hone ke waqt the —
ye bilkul normal hai, koi problem nahi.

---

### 14. Mobile pe chalega?

**Haan, poori tarah.** Phone pe tables automatically **cards** ban jaate hain taaki side me
scroll na karna pade. Search, watchlist, stock analysis — sab kaam karta hai.
[Detail me padho](#-mobile-phone-pe-kaise-chalta-hai)

---

### 15. Watchlist save hoti hai?

**Haan, par sirf usi browser me jahan aapne banayi hai.**

- Doosre computer/phone pe nahi dikhegi
- Doosre browser me nahi dikhegi
- Browser ka data clear karoge to chali jaayegi

Ye kisi account me save nahi hoti. [Detail me padho](#-watchlist)

---

## 🛡️ Safety / Responsible Use

> ### Please ye zaroor padho

**1. Website ka purpose market information aur learning hai.**
Ye aapko market samajhne me madad karti hai. Ye aapko batati nahi ki kya kharidna hai.

**2. Decision lene se pehle actual broker/exchange data verify karo.**
Yahan ka data delayed hai. Real paisa lagane se pehle apne broker ka live data dekho.

**3. Apne paiso ka risk khud samjho.**
Market me paisa lagane me nuksan ho sakta hai. Utna hi lagao jitna aap kho sakte ho.

**4. Past ya current indicator future result guarantee nahi karta.**
Saare indicators purane data se bante hain. Koi bhi indicator — chahe kitna bhi strong lage —
future nahi bata sakta.

**5. Kisi ek number pe bharosa mat karo.**
Signal Score +7 hone ke baad bhi stock gir sakta hai. Ye normal hai.

**6. Agar naye ho to pehle seekho.**
Bina samjhe paisa mat lagao. Pehle chhote amount se, ya sirf observe karke seekho.

**7. Kisi ki tips pe andha bharosa mat karo** — is website ki bhi nahi.
Ye ek tool hai, guru nahi.

---

<div align="center">

### 📌 Yaad rakhne wali baat

**Ye website aapko market ki INFORMATION deti hai.
Ye aapko ADVICE nahi deti.**

Green ≠ Buy · Red ≠ Sell · Score ≠ Guarantee

---

Koi confusion ho to is guide ko dobara padh lo.
Install karne ke liye → **[README.md](README.md)**

*Happy learning! 📈*

</div>
