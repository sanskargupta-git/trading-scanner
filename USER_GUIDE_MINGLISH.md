# 📊 Ultimate Pro Trading Terminal
## Sopa User Guide (Marathi + English)

> **Ha guide tya lokan sathi aahe je website vaparu ichhitat.**
> Coding kinva technical knowledge chi agdi garaj nahi.
> Sagla kahi agdi sopya bhashet samjavla aahe.

> ## 📖 Itar files
>
> | Pahije | File |
> |---|---|
> | 🖥️ **Website guide (Hinglish)** | **[USER_GUIDE.md](USER_GUIDE.md)** |
> | 🔧 **Install karaycha aahe (Marathi)** | **[README_MINGLISH.md](README_MINGLISH.md)** |
> | 🔧 **Install karna hai (Hinglish)** | **[README.md](README.md)** |

---

## 🙏 Sagat aadhi — he vaachaa

Ha dashboard **market data ekach thikani baghayla madat karto**. Yat tumhi
**Nifty 50, Bank Nifty, commodities ani vegvegle stocks** ekach jagi baghu shakta —
pratyek stock sathi vegli app ughadaychi garaj nahi.

> ### ⚠️ Mahatvachi goshta
>
> **Hi website fakt mahiti ani shiknya sathi aahe.
> Hi guaranteed profit kinva investment advice det nahi.**
>
> - Ithe je green/red disto to **buy/sell cha order nahi** aahe
> - Kuthlahi indicator future **sangu shakat nahi**
> - Paise lavnya adhi tumchya broker cha kharokhar cha data nakki baghaa
> - Nuksan kinva fayda — donhi chi jababdari tumchi swatachi aahe

Tumhala trading cha agdi anubhav nasel tar ya website la **shiknyacha tool** samjaa —
market kasa chalto, vegvegle numbers cha kaay artha asto, he samjun ghenya sathi.

---

## 📑 Ya guide madhe kaay aahe

| Section | Kaay milel |
|---|---|
| [Website ughadlya nantar](#-website-ughadlya-nantar) | Sagat aadhi kaay disel |
| [Varchi patti](#-varchi-patti-status-bar) | Market status, data kiti juna aahe |
| [Colours cha artha](#-colours-cha-artha) | Green, Red, Yellow, Grey |
| [Signal Score](#-signal-score-mhanje-kaay) | Ekach number madhe purna summary |
| [Indicators sopya bhashet](#-indicators--agdi-sopya-bhashet) | Pratyek indicator cha sopa artha |
| [Page-by-page guide](#-page-by-page-guide) | Pratyek page kasa vaparaycha |
| [Data status](#-data-status--fresh-stale-unavailable) | FRESH / STALE / UNAVAILABLE |
| [Timeframe fallback](#-timeframe-fallback-cha-artha) | "Requested / Using" ka lihilela yeta |
| [CSV download](#-csv-download-kasa-karaycha) | Excel madhe data kaadhna |
| [Mobile var](#-mobile-var-kasa-chalto) | Phone var vaparna |
| [Common questions](#-common-questions-faq) | 15 prashna-uttare |
| [Safety](#-safety--responsible-use) | Jababdarine vaparna |

---

## 🏠 Website ughadlya nantar

Website ughadlya barobar sagat var **4 mothe box** distil:

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  NIFTY 50    │  BANK NIFTY  │  FIN NIFTY   │  INDIA VIX   │
│  24,471.70   │  57,446.25   │  26,903.35   │    11.86     │
│  -0.46%      │  -0.42%      │  +1.31%      │   -3.18%     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

Pratyek box madhe **tin goshti** astat:
1. **Naav** (var) — konta index aahe
2. **Number** (madhe) — aata chi value
3. **Percentage** (khali) — aaj kiti var/khali gela

Percentage **green** asel tar aaj vaadhla aahe, **red** asel tar aaj padla aahe.

---

### 📈 NIFTY 50 mhanje kaay?

**Nifty 50 madhe India madhlya major 50 companies cha index asto.**

Asa samjaa: India chya 50 sagat mothya companies — Reliance, TCS, HDFC Bank, Infosys
vagaire — la ekatra baghaycha asel tar pratyek la vegla baghava lagel. Khup kathin.

Mhanun ek **average sarkha number** banavla aahe — tyala Nifty 50 mhantat.

- Nifty **var** jat asel → mhanje bahutek mothya companies aaj changla karat aahet
- Nifty **khali** jat asel → mhanje bahutek companies aaj padat aahet

> 💡 He market cha "overall mood" sangto.

---

### 🏦 BANK NIFTY mhanje kaay?

**Bank Nifty madhe fakt banking sector chya mothya stocks cha index asto.**

Jasa Nifty 50 purna market cha mood sangto, tasach Bank Nifty fakt **bankanchya mood**
sangto — HDFC Bank, ICICI Bank, SBI, Axis Bank vagaire.

Kahi vela purna market padta pan banks vaadhtat, kinva ulta. Mhanun vegla baghtat.

---

### 💳 FIN NIFTY mhanje kaay?

**Fin Nifty madhe financial companies cha index asto.**

Yat banks tar aahetach, sobat **insurance companies (SBI Life, HDFC Life),
NBFC (Bajaj Finance, Shriram Finance)** ashya financial companies pan aahet.

Mhanje Bank Nifty peksha thoda motha group — purna "paishancha vyavsaay" karnara sector.

---

### 😰 INDIA VIX mhanje kaay?

**India VIX market madhe kiti bhiti (fear) ani anischitta aahe te sangto.**

Yala "fear index" pan mhantat. Sopya paddhatine samjaa:

- VIX **kami** asel → market shant aahe, log relaxed aahet
- VIX **jasta** asel → market madhe ghabrat aahe, mothi movement hou shakte

> ⚠️ **Laksha dyaa:** VIX cha number **prediction nahi** aahe. To fakt sangto ki aata market
> madhe kiti anischitta aahe. Yacha artha asa nahi ki market padel kinva vaadhel — fakt
> evdach ki **movement mothi asu shakte**.
>
> Ya website madhe VIX sathi kuthlahi "dhoka" kinva "safe" level dila nahi, karan asa
> kuthlahi fixed niyam nasto.

---

## 🕐 Varchi patti (Status Bar)

Mothya box chya agdi var ek patli patti aste. Yat khup upyogi goshti astat:

```
● Market Closed · Opens 09:15 IST | Last updated 14:23:05 | Data age 12s | Next refresh 78s
```

| Kaay lihilela aahe | Artha |
|---|---|
| **● Market Closed** | Aata market band aahe |
| **Opens 09:15 IST** | Market kevha ughadel |
| **Last updated 14:23:05** | Data shevatcha konatya velela ala hota |
| **Data age 12s** | Data 12 second juna aahe |
| **Next refresh 78s** | 78 second nantar nava data yeil |

---

### 🚦 Market Status cha artha

| Disel | Artha | Vel (IST) |
|---|---|---|
| 🟢 **Market Open** | Market chalu aahe, prices badalat aahet | 09:15 – 15:30 |
| 🟡 **Pre-Market** | Market ughadnyachya aadhi cha vel | 09:00 – 09:15 |
| 🟠 **Post-Market** | Market ata-ata band zala aahe | 15:30 – 16:00 |
| 🔴 **Market Closed** | Market band aahe (ratri, sakali, kinva weekend) | Baaki vel + Sat/Sun |

> ### ⚠️ Ek mahatvachi limitation
>
> Hi website **fakt vel ani divas** baghun market status sangte.
> **Yat exchange chi holiday list nahi aahe.**
>
> Mhanje ekhadya divshi **Diwali, Holi kinva dusri market holiday** asel, tar website
> "Market Open" dakhavu shakte jari kharokhar market band asel.
>
> Mhanun **kharokhar chi holiday NSE chya website varun kinva tumchya broker kadun confirm kara.**

---

## 🎨 Colours cha artha

Purna website madhe colours cha ekach artha aahe. Ekda samjun ghetla ki sagli kade kaami yeil:

| Colour | Artha | Udaharan |
|---|---|---|
| 🟢 **Green** | Positive / bullish indication — goshta var chya dishene jat aahe | `▲ Bullish`, `+2.34%`, `Golden` |
| 🔴 **Red** | Negative / bearish indication — goshta khali chya dishene jat aahe | `▼ Bearish`, `-1.20%`, `Death` |
| 🟡 **Yellow** | Neutral / spashta nahi — kuthlihi disha sangat nahi | `Flat` |
| ⚪ **Grey** | Data uplabdh nahi, kinva khaas kahi hot nahi | `--`, `Normal`, `WAIT` |

> ### 🚨 Hi sagat mahatvachi goshta aahe
>
> **Green mhanje "buy kara" ASA NAHI.
> Red mhanje "sell kara" ASA NAHI.**
>
> Green fakt evdach sangto ki *tya ekhadya indicator chya hishobane* recent movement var
> chya dishene hoti. Bas evdach. To pudhe pan var jaail — yachi **kuthlihi guarantee nahi**.
>
> Market madhe green nantar lagech red pan yeu shakto. Colour la **mahiti** samjaa,
> **order** nahi.

---

## 🎯 Signal Score mhanje kaay?

Hi website pratyek stock la ek **number** dete — tyala Signal Score mhantat.

### He kasa kaam karta?

Website pratyek stock var **7 vegvegli goshti** check karte (MACD, RSI, EMA vagaire —
yanchya baddal khali detail madhe vaachaal).

- Pratyek goshta **positive** disha dakhavli tar → **+1**
- Pratyek goshta **negative** disha dakhavli tar → **−1**

Sagla jodlya nantar jo number yeto to Signal Score aahe. To **−7 te +7** chya madhe rahto.

### Score cha artha

| Score | Kaay lihilela yeil | Sopa artha |
|---|---|---|
| **+4 kinva jasta** | 🟢 STRONG BULLISH | Bahutek indicators positive disha dakhavat aahet |
| **+1 te +3** | 🟢 BULLISH | Thoda positive kal aahe |
| **0** | ⚪ NEUTRAL | Mixed aahe — kahi positive, kahi negative |
| **−1 te −3** | 🔴 BEARISH | Thoda negative kal aahe |
| **−4 kinva kami** | 🔴 STRONG BEARISH | Bahutek indicators negative disha dakhavat aahet |

### Udaharan ne samjun ghyaa

Samjaa RELIANCE cha score **+5** aahe. Yacha artha:

> "Aata jya 7 goshti check kelya aahet, tyatlya bahutek positive disha dakhavat aahet."

**Yacha artha ASA NAHI:**
- ❌ "RELIANCE vaadhel"
- ❌ "RELIANCE ghyaa"
- ❌ "He safe aahe"

**Yacha artha fakt evdach:**
- ✅ "Aata chya uplabdh data madhe indicators ekamekan sobat sahamat aahet"

> ### ⚠️ Signal Score ek SUMMARY aahe, PREDICTION nahi
>
> To fakt sangto ki **aata kiti indicators ekach dishene aahet**. To future chi kuthlihi
> guarantee det nahi. 7 pैki 7 indicators positive aslya nantar pan stock padu shakto —
> he market madhe normal aahe.

---

## 📚 Indicators — agdi sopya bhashet

Hi website pratyek stock var **10 indicators** dakhavte. Ghabru naka — ek-ek karun sagle
sopya bhashet samjavto.

> **"Indicator" mhanje kaay?**
> Indicator ek calculation aahe je junya price data pasun banta. To sangto ki
> **aatta paryant kaay zala**. To he sangat nahi ki *pudhe kaay hoil*.
>
> Jasa gaadi cha speedometer sangto ki tumhi aata kiti speed var aahat — pan to he sangat
> nahi ki 10 minute nantar kiti speed asel.

---

### 1️⃣ 🔥 Big Candle

**He kaay aahe?**
Dar thodya velane stock cha price var-khali hoto. Tya movement la "candle" mhantat.
Big Candle check karto ki hi movement **normal peksha khup mothi** tar nahi na.

**Sopa artha:**
Shevatchya 15 minute madhe stock madhe achanak mothi movement zali asel, tar he
"Big Candle" dakhavto. Mhanje kahi tari mahatvacha hot aahe.

| Disel | Artha |
|---|---|
| 🟢 **▲ Big Bull** | Mothi movement zali, ani var chya dishene hoti |
| 🔴 **▼ Big Bear** | Mothi movement zali, ani khali chya dishene hoti |
| ⚪ **Normal** | Kuthlihi khaas mothi movement zali nahi |

> ⚠️ **Warning:** Mothi movement cha artha asa nahi ki ti chalu rahil. Kahi vela mothya
> movement nantar lagech ultach hota.

---

### 2️⃣ ⚡ MACD

**He kaay aahe?**
MACD stock chya movement chi **strength ani disha** samjun ghenya sathi vaparla jato.
To don vegvegle "average prices" compare karto — ek fast, ek slow.

**Sopa artha:**
Samjaa tumhi gaadi chalvat aahat. MACD sangto ki tumhi **veg ghet aahat ki mand hot aahat**.

| Disel | Artha |
|---|---|
| 🟢 **▲ Bullish** | Recent movement positive asu shakte |
| 🔴 **▼ Bearish** | Recent movement negative asu shakte |
| ⚪ **--** | Data uplabdh nahi |

> ⚠️ **Warning:** MACD future chi guarantee det nahi. To fakt sangto ki **aatta paryant** kaay zala.

---

### 3️⃣ 📈 DOW Breakout

**He kaay aahe?**
He check karto ki stock ne aapli **magchi height cross keli** ka, kinva aapla **magcha low
todla** ka.

**Sopa artha:**
Samjaa ek stock magchya kahi tasan pasun ₹100 paryantach jat hota, ani parat padat hota.
Aata to ₹100 cross zala — mhanje he "breakout" aahe. Kahi tari nava hot aahe.

| Disel | Artha |
|---|---|
| 🟢 **BUY** | Stock ne magcha high cross kela |
| 🔴 **SELL** | Stock ne magcha low todla |
| ⚪ **WAIT** | Aata kahi zala nahi, range madhech aahe |

> ⚠️ **Warning:** Ithe **"BUY" cha artha kharedi cha order nahi!** Ha fakt ek technical
> shabd aahe jo sangto ki price ne var chya dishene ek level cross kela. Kai vela breakout
> nantar lagech price parat padto (yala "false breakout" mhantat).

---

### 4️⃣ ⚔️ EMA Crossover

**He kaay aahe?**
EMA mhanje "average price". He don average compare karta — ek **short time** cha
(20 candles), ek **motha time** cha (50 candles).

**Sopa artha:**
Recent average, junya average peksha **var** gela — mhanje aata cha trend junya trend
peksha changla aahe. Yala **"Golden"** mhantat. Ulta zala tar **"Death"** mhantat.

| Disel | Artha |
|---|---|
| 🟢 **Golden** | Recent average, junya average peksha var aahe |
| 🔴 **Death** | Recent average, junya average peksha khali aahe |

> ⚠️ **Warning:** Naav ghabravnare aahet ("Golden", "Death") pan he fakt technical terms
> aahet. "Death" cha artha company budnar aahe — asa **agdi nahi**.

---

### 5️⃣ 📊 Bollinger Band

**He kaay aahe?**
He stock chya price chya aas-pas ek **var ani khali chi line** banavta. Saadharanpane
price ya donhi lines chya madhe rahto.

**Sopa artha:**
Samjaa ek road aahe jyachya donhi bajula boundary aahe. Bollinger Band sangto ki gaadi
(price) boundary javal pochli aahe ki madhech aahe.

| Disel | Artha |
|---|---|
| 🟢 **▲ Up** | Price var chya line javal pochla aahe |
| 🔴 **▼ Down** | Price var chya line pasun lamb aahe |

> ⚠️ **Warning:** Var chi line touch kelyacha artha "aata padel" kinva "aajun vaadhel" —
> donhi paiki kahi hi hou shakta.

---

### 6️⃣ 📉 RSI (number)

**He kaay aahe?**
RSI ek number aahe **0 te 100** chya madhe. To sangto ki stock **aalikde jasta ghetla
gela** aahe ki **jasta viklā gela** aahe.

**Sopa artha:**
Samjaa ekhadya dukanat ek vastu khup jasta vikat aahe — stock pan tasach "overheated"
hou shakto.

| RSI number | Kaay mhantat | Sopa artha |
|---|---|---|
| **70 chya var** | Overbought | Aalikde khup ghetla gela aahe |
| **30 te 70** | Neutral zone | Normal aahe |
| **30 chya khali** | Oversold | Aalikde khup viklā gela aahe |

> ⚠️ **Warning:** Ha sagat jasta chukicha samajla janara indicator aahe.
> **"Overbought" cha artha "aata padel" asa nahi** — stock RSI 80 var rahun pan
> aathavdyanpasun vaadhu shakto. Tasach "Oversold" cha artha "aata vaadhel" asa nahi.

---

### 7️⃣ 📉 RSI Trend

**He kaay aahe?**
RSI cha number magchya velepeksha **vaadhla ki kami zala**, fakt evdach sangto.

| Disel | Artha |
|---|---|
| 🟢 **Uptick** | RSI vaadhat aahe |
| 🔴 **Downtick** | RSI kami hot aahe |
| 🟡 **Flat** | RSI tasach aahe |

> ⚠️ **Warning:** He khup lahan movement pan dakhavto. Ekta baghun kuthlahi nishkarsh kaadhu naka.

---

### 8️⃣ 🎯 DMI

**He kaay aahe?**
DMI compare karto ki **var chi movement jasta aahe ki khali chi**.

**Sopa artha:**
Rassi-khech (tug of war) samjaa — ek baju kharedi karnare, dusri baju viknare.
DMI sangto ki aata kon pudhe aahe.

| Disel | Artha |
|---|---|
| 🟢 **Bullish Cross** | Var chi movement jasta strong aahe |
| 🔴 **Bearish Cross** | Khali chi movement jasta strong aahe |

> ⚠️ **Warning:** He fakt aata chi position sangto. Rassi-khech madhe donhi bajucha jor
> kevhahi badlu shakto.

---

### 9️⃣ 🎯 ADX (number)

**He kaay aahe?**
ADX sangto ki je kahi movement chalu aahe, ti **kiti majboot** aahe.
To **disha sangat nahi** — fakt **strength** sangto.

**Sopa artha:**
- ADX **kami** (20 chya khali) → movement kamjor aahe, stock ikde-tikde firat aahe
- ADX **jasta** (25 chya var) → movement madhe dam aahe, ek spashta disha chalu aahe

| ADX number | Sopa artha |
|---|---|
| **25 chya var** | Trend madhe dam aahe |
| **20 te 25** | Trend tayar hot aahe |
| **20 chya khali** | Kamjor / kuthlahi spashta trend nahi |

> ⚠️ **Warning:** ADX jasta asnyacha artha "changla" asa nahi — trend **khali chya dishene**
> pan strong asu shakto! Disha sathi dusre indicators baghave lagtat.

---

### 🔟 🎯 ADX Trend

**He kaay aahe?**
ADX cha number vaadhat aahe ki kami hot aahe.

| Disel | Artha |
|---|---|
| 🟢 **Uptick** | Trend aajun majboot hot aahe |
| 🔴 **Downtick** | Trend kamjor hot aahe |
| 🟡 **Flat** | Tasach aahe |

> ⚠️ **Warning:** Ithe pan green cha artha "changla" nahi — fakt "trend strong hot aahe".

---

> ## 🧠 Sagat mahatvachi goshta — sagle indicators baddal
>
> He sagle indicators **junya price data pasun bantat**. Mhanje he sagle sangtat ki
> **aatta paryant kaay zala**. Yatla kuthlahi **future sangu shakat nahi**.
>
> Mhanun:
> - Kadhihi ek indicator baghun decision gheu naka
> - 7 paiki 7 green aslya nantar pan stock padu shakto
> - He "signals" nahit, fakt "mahiti" aahe

---

## 🗺️ Page-by-page guide

Website madhe **8 pages** aahet. Var navigation bar madhe sagle button aahet.

---

### 🏠 Dashboard

He **home page** aahe — ithe sagat jasta mahatvachya goshti ekatra distat.

**Ithe kaay milel (varun khali):**

1. **4 index box** — Nifty 50, Bank Nifty, Fin Nifty, India VIX
2. **Market Pulse** — purna market cha mood:
   - Kiti stocks **Bullish** aahet
   - Kiti **Bearish**
   - Kiti **Neutral**
   - **Top Gainer** — aaj sagat jasta vaadhnara stock
   - **Top Loser** — aaj sagat jasta padnara stock
3. **Top Bullish Setups** — 5 stocks jyancha score sagat jasta aahe
4. **Top Bearish Setups** — 5 stocks jyancha score sagat kami aahe
5. **My Watchlist** — tumhi save kelele stocks
6. **Tables** — Nifty 50, Bank Nifty, Fin Nifty, Commodities, Gift Nifty

**Tips:**
- Kuthlyahi stock chya naavavar click kela ki tyacha purna analysis ughadel
- Table chya heading var click kela ki table lapel/ughadel
- Nifty 50 table chya var ek search box aahe — tya table madhe stock shodhaayla

---

### 🔍 Screener

**Screener madhe tumhi 50 stocks ekatra compare karu shakta.**

He page ek mothi table aahe jyat pratyek stock chi sagli mahiti ekach line madhe disate.

**Kasa vaparaycha:**

**1. Universe nivada** — konte stocks baghaayche
```
Nifty 50 / Bank Nifty / Fin Nifty / Commodities / Gift Nifty / Everything
```

**2. Filter lavaa** — signal bias ne
```
All  |  Strong Bullish  |  Bullish  |  Neutral  |  Bearish  |  Strong Bearish
```

> **Udaharan:** Fakt bullish stocks baghaayche astil tar **Bullish** filter nivadaa.
> Lagech fakt tech stocks distil.

**3. Sort kara** — konatya hishobane order lavaycha
```
Signal Score / Daily % / RSI / ADX / Price / Symbol A-Z
```
Sobat **High → Low** kinva **Low → High** pan nivadu shakta.
Jya column var sorting chalu aahe tyachya naavachya pudhe ▲ kinva ▼ disel.

**4. Search kara** — ekhada specific stock shodhaycha asel tar search box madhe naav taipa

**5. Result count baghaa** — var lihilela yeil:
```
Showing 23 of 50 stocks
```
Mhanje 50 paiki 23 stocks tumchya filter var basat aahet.

**6. CSV download** — ⬇ Export CSV button ne sagla data Excel madhe kaadhu shakta

---

### 🔥 Heatmap

**Pratyek company ekhadya rangit box (tile) madhe disate.**

He page eka najret purna market dakhavto. Pratyek tile madhe:
- Company cha naav
- Aaj cha percentage
- Price
- Signal band (STRONG BULLISH vagaire)

**Colour cha artha:**

| Colour | Artha |
|---|---|
| 🟢 **Gadha green** | Aaj changla var gela |
| 🟢 Fikat green | Thoda var gela |
| ⚪ Grey | Jvaljval tasach aahe |
| 🔴 Fikat red | Thoda khali gela |
| 🔴 **Gadha red** | Aaj changla khali gela |

**Colour badalu pan shakta** — var dropdown madhun:
- **Colour by daily %** — aaj chya movement ne (default)
- **Colour by signal score** — score ne
- **Colour by RSI** — RSI ne

**Stock var click kela ki Stock Analysis page ughadel.**

> Tiles sagle ekach size che astat ani aaj chya movement chya hishobane order madhe
> lavlele astat. Company cha size kinva market cap ithe vaparat **nahi**.

---

### 📊 Stock Analysis

**He ekhadya stock chi purna detail dakhavta.** Sagat detailed page hech aahe.

**Kasa ughadaycha:**
1. Var ujvya bajula **search box** madhe stock cha naav taipa (jasa `RELIANCE`)
2. Suggestion list madhun click kara
3. **Kinva** kuthlyahi page var stock chya naavavar click kara

**Ithe kaay milel:**

**Var (hero section):**
- **Stock cha naav** — jasa RELIANCE
- **Signal Score ani Band** — jasa `+5 STRONG BULLISH`
- **Current Price** — jasa ₹1,323.90
- **Daily %** — aaj kiti var/khali
- **Market status, data fresh aahe ka, data kiti juna aahe**

**Indicator Grid:**
Sagle 10 indicators ek grid madhe. Pratyek box madhe indicator cha naav, tyacha
**timeframe**, ani value.

**Timeframe buttons (5M, 15M, 1H, 1D):**

| Button | Artha |
|---|---|
| **5M** | 5 minute chi movement |
| **15M** | 15 minute chi movement |
| **1H** | 1 tasa chi movement |
| **1D** | Purna divsa chi (daily) movement |

Lahan timeframe = jasta detail pan jasta gongat (noise)
Motha timeframe = kami detail pan jasta spashta picture

**Timeframe Levels:**
Tya timeframe che mahatvache numbers — EMA 20, EMA 50, swing high, swing low, volume.

**Technical Summary:**
Sagla kahi ekach jagi sopya bhashet:
- **Trend** — Bullish / Bearish / Neutral
- **Momentum** — Positive / Negative
- **Strength** — ADX chya hishobane
- **Volatility** — kiti chad-utar aahe
- **RSI** — number ani tyacha artha
- **Signals Agreeing** — kiti indicators ekamekan sobat sahamat aahet

**Buttons:**
- **Open TradingView ↗** — chart baghaayla (navya tab madhe ughadel)
- **+ Watchlist** — ha stock tumchya watchlist madhe taakaayla

---

### ⭐ Watchlist

**Je stocks parat-parat baghaayche astil te Watchlist madhe save kara.**

**Stock add karna:**
1. `/watchlist` page ughadaa
2. Box madhe stock cha naav taipa (jasa `WIPRO`)
3. **Add** button dabaa

**Kinva:** Kuthlyahi stock chya Analysis page var **+ Watchlist** button dabaa.

**Stock kaadhna:**
Tya stock chya card madhe var-ujvya konyat **✕** dabaa.

**Search karna:**
Filter box madhe taipa — fakt matching stocks distil.

**Stock ughadna:**
Card madhe stock chya naavavar click kara → Analysis page ughadel.

**Pratyek card madhe disel:**
Symbol, Price, Daily %, Signal Score, Trend, ani data kiti juna aahe.

> ### 💾 Watchlist kuthe save hote?
>
> Tumchi watchlist **tyach browser madhe, tyach computer var** save hote jithe tumhi
> banavli aahe.
>
> Mhanje:
> - Dusrya computer var ughadli tar watchlist disnar nahi
> - Dusrya browser madhe ughadli (Chrome varun Firefox) → disnar nahi
> - Mobile var ughadli tar vegli watchlist asel
> - Browser cha data/history clear kela tar **watchlist jail**
>
> Hi kuthlyahi account madhe save hot nahi. List geli tar **↺ Reset to default**
> ne default list parat yete.

---

### 🌍 Markets

**Sagle market segments ekach jagi, card format madhe.**

Ithe milel:

| Section | Kaay aahe |
|---|---|
| **Headline Indices** | Nifty 50, Bank Nifty, Fin Nifty, India VIX |
| **Nifty 50** | 50 mothya companies |
| **Bank Nifty** | Banking sector |
| **Fin Nifty** | Financial sector |
| **Commodities (MCX)** | Gold, Silver, Crude Oil, Natural Gas, Copper |
| **Gift Nifty & Indices** | Index instruments |
| **Currencies** | USD/INR, USD/CNY, USD/RUB, USD/CAD |

Pratyek card var click kara → tya stock cha Analysis ughadel.

> ### ⚠️ Commodities chya prices baddal
>
> Gold, Silver, Crude che prices Yahoo varun **US dollar** madhe yetat. Website tyanna
> sadhya chya USD/INR rate ne rupaye madhe convert karte.
>
> Mhanun he prices **approximate** aahet — kharokhar chya MCX rate peksha thode vegle
> asu shaktat. Kharokhar chya trading sathi MCX kinva tumchya broker cha rate ch baghaa.

---

### 🧮 Options Lab

> ## 🚨 SAGAT AADHI HE VAACHAA
>
> **He page ek CALCULATOR aahe. He live option chain NAHI aahe.**
>
> Je premium prices (CE/PE che numbers) ithe distat, te website ne **spot price varun
> calculate** kele aahet. He:
>
> - ❌ Exchange che **khare prices nahit**
> - ❌ Khare **bid/ask nahit**
> - ❌ Khare **IV (Implied Volatility) nahi**
> - ❌ Khare **Greeks (Delta, Theta) nahit**
>
> Page var sagli kade **ESTIMATED / ANALYTICAL** lihilela aahe — hach tyacha artha aahe.
>
> **Kharokhar chya option trading sathi tumchya broker cha kharokhar cha option chain ch baghaa.**

**Mag he page kashacha upyog?**

He samjun ghenya sathi ki **"premium X varun Y zala tar kiti profit/loss hoil"**.
Mhanje position sizing ani calculation practice sathi.

**Kasa vaparaycha:**

**1. Underlying nivada** — konatya stock cha option (jasa RELIANCE), mag **Load** dabaa

**2. Spot Price baghaa** — tya stock cha current price

**3. Strike ladder madhun ek strike var click kara** — CE (green) kinva PE (red) number var

**4. Details bhara:**

| Field | Artha |
|---|---|
| **Side** | Buyer (Long) kinva Seller (Short) |
| **Lot Size** | Ek lot madhe kiti shares (apoap yeta) |
| **Quantity (lots)** | Kiti lot ghyaayche |
| **Entry Premium** | Konatya price la ghetla |
| **Exit Premium** | Konatya price la viklā |

**5. Result baghaa:** Total Quantity, Capital Outlay, Estimated P&L, P&L %

---

#### 📝 Sopa udaharan

Samjaa:

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
Capital lavla  = ₹70 × 250    = ₹17,500
P&L %          = 7,500 ÷ 17,500 × 100 = 42.86%
```

> ### ⚠️ Ya calculation madhe kaay SAMAVISHTA NAHI
>
> - ❌ Brokerage (broker chi fees)
> - ❌ STT (Securities Transaction Tax)
> - ❌ Exchange charges
> - ❌ GST
> - ❌ Stamp duty
>
> Kharokhar chya trading madhe he sagle katat, mhanun kharokhar cha profit **yapeksha kami** asel.
>
> Ani tumhi **Seller (Short)** asaal tar jo "Capital Outlay" disto to tumhala milalela
> premium aahe — to **margin nahi** jo tumcha broker block karel.

---

### ✨ AI Assistant (Gemini)

Website chya **khalchya ujvya konyat** ek ✨ button aahe. Tyavar click kela ki chat window ughadel.

**Kaay vicharu shakta:**
```
explain RELIANCE
analyse TCS
HDFCBANK baddal sanga
```

**He kasa kaam karta:**
Jevha tumhi ekhadya stock cha naav gheta, website tya stock che **kharokhar che aata che
numbers** (price, MACD, RSI, ADX, score) AI la pathvte. AI tyach numbers la sopya bhashet
samjavto.

> ### ⚠️ AI baddal mahatvachya goshti
>
> - **AI chukicha asu shakto.** Chat window chya khali nehami lihilela asto:
>   *"AI-generated explanation is informational and may contain errors."*
> - **AI la financial advice samju naka**
> - AI la fakt tech numbers miltat je website kade aahet — to swatah kuthlahi price
>   kinva number banvu shakat nahi

**AI kaam nahi kela tar:**
Tumhala message ala ki *"The AI assistant is not configured"* — mhanje AI feature setup
nahi. **He purnpane normal aahe.** Baaki purna website normal chalel.

---

### ℹ️ About

Ya page var technical detail aahe — pratyek indicator cha formula, architecture, tech stack.

---

## 📶 Data Status — FRESH, STALE, UNAVAILABLE

Website nehami spashta sangte ki data kiti vishwasarha aahe.

| Status | Artha | Kaay karava |
|---|---|---|
| 🟢 **FRESH DATA** | Data ata-ata ala aahe, sagla theek aahe | Normal vaparaa |
| 🟡 **STALE DATA** | Last update fail zala, juna data dakhavat aahot | Thoda thambaa, apoap theek hoil |
| 🟡 **DATA UNAVAILABLE** | Aata data yetach nahi | Internet check kara, kinva thodya velane try kara |

### "Stale" cha artha kaay?

**Stale mhanje: website kade last successful data aahe, pan latest update ajun ala nahi.**

Asa ka hota? Kahi vela data denari service (Yahoo Finance) thodya velasathi uttar det nahi.

**Ashya veli website don goshti karu shakli asti:**

1. ❌ Screen rikami karun taakli asti — sagla gayab
2. ✅ **Juna data dakhavat rahili ani spashta sangitla ki ha juna aahe**

Website **dusra marg** vaparte. Var yellow patti yete:

```
⚠ Stale data - last successful update 180s ago
```

> ### 💡 He changla ka aahe?
>
> Karan **juna data, khotya data peksha nehami changla aahe.**
>
> Website 3 minute juna price dakhavat asel ani tumhala **sangat pan asel** ki ha 3 minute
> juna aahe — tar tumhi samjun-ujhun decision gheu shakta.
>
> Pan ti ekhada number banvun dakhavla, tar tumhala kalnarach nahi ki to chukicha aahe.
> **Mhanun hi website kadhihi number banavat nahi.**

---

## ⏱️ Timeframe fallback cha artha

Kahi vela Stock Analysis page var tumhala asa disel:

```
Requested: 15M
Using: Daily fallback
```

**Yacha artha kaay?**

Website ne 15-minute cha data magitla hota, pan data denari service ne to dila nahi.
Mhanun website ne **daily (purna divsa cha) data** vaparla.

**Ani sagat mahatvachi goshta:** website ne tumhala **sangitla**.

> ### 💡 He ka mahatvacha aahe?
>
> Samjaa website 15M lihun gupchup daily cha data dakhavla asta. Tumhi samajla asta ki
> hi magchya 15 minute chi movement aahe, jari kharokhar ti purna divsa chi movement aahe.
> **Agdi chukicha samajla asta.**
>
> Mhanun website spashta lihite ki magitla kaay hota ani milala kaay. He **error nahi** —
> hi pramanikta aahe.

Tables madhe ashya value chya pudhe ek lahan **`D`** lihilela yeto. Mouse nela ki
purna goshta disel.

Ani data agdi milala nahi tar **`--`** disto — mhanje "data uplabdh nahi".

---

## 📥 CSV download kasa karaycha

### CSV file mhanje kaay?

CSV ek sadhi file aste jyat table cha data asto. Ti **Excel** kinva **Google Sheets**
madhe ughadu shakta — agdi normal table sarkhi disel.

Fayda: tumhi tumchya hishobane sort karu shakta, calculations karu shakta.

### Kuthun download karaycha

| Page | Button kuthe aahe |
|---|---|
| **Dashboard** | Pratyek table chya heading chya ujvya bajula — **⬇ CSV** |
| **Markets** | Pratyek section chya ujvya bajula — **⬇ CSV** |
| **Screener** | Var ujvya bajula — **⬇ Export CSV** (jo filter lavla aahe tocha data yeil) |

### Excel madhe kasa ughadaycha

1. Button var click kara — file download hoil (saadharanpane **Downloads** folder madhe)
2. File var **double-click** kara — Excel madhe ughadel
3. Excel install nasel tar [Google Sheets](https://sheets.google.com) var ja →
   **File → Import → Upload** → file select kara

---

## 📱 Mobile var kasa chalto

**Ho, website phone var agdi chalte.** Kahi install karaychi garaj nahi —
fakt browser madhe link ughadaa.

**Phone var kaay vegla hota:**

| Goshta | Phone var |
|---|---|
| **Tables** | Mothya table chya aivaji pratyek stock cha swatacha **card** banto — bajula scroll karava lagat nahi |
| **Navigation** | Var che buttons bajula scroll hotat |
| **Search** | Var cha search box tasach kaam karto |
| **Watchlist** | Purnpane kaam karte (pan phone chi watchlist vegli asel) |
| **Stock Analysis** | Sagle indicators don-don chya jodit distat |
| **Heatmap** | Lahan tiles madhe, pan sagle distat |

**Tip:** Browser madhe website la **bookmark** kara, kinva "Add to Home Screen" kara —
mag app sarkha ek click madhe ughadel.

---

## ❓ Common Questions (FAQ)

### 1. Hi website buy/sell signal dete ka?

**Nahi.** Hi website fakt **mahiti** dakhavte — prices, indicators, calculations.
"BUY" ani "SELL" sarkhe shabd je distat te **technical terms** aahet, **order nahi**.

Kaay ghyaayacha kinva vikaycha — ha decision purnpane tumcha aahe.

---

### 2. Data live aahe ka?

**Nahi, data delayed aahe.** Ha data Yahoo Finance varun yeto, jo exchange cha live feed
nahi aahe. Mhanun website kuthehi "LIVE" lihit nahi.

Tyachya aivaji ti spashta **"Data age 42s"** lihite — mhanje data 42 second juna aahe.

---

### 3. Data kiti delayed asu shakto?

Data dar **90 second** la refresh hoto. Tyachya var Yahoo cha swatacha delay pan asto.

Var chya patti madhe nehami exact age disto.

---

### 4. Green cha artha buy karna aahe ka?

**Agdi nahi.** 🚫

Green fakt evdach sangto ki *tya ekhadya indicator chya hishobane* recent movement var
chya dishene hoti. To pudhe pan var jaail — yachi kuthlihi guarantee nahi.

Market madhe green nantar lagech red pan yeu shakto.

---

### 5. Red cha artha sell karna aahe ka?

**Nahi.** Red fakt sangto ki recent movement khali chya dishene hoti.

Kai vela red nantar stock parat var jato. Red la "mahiti" samjaa, "order" nahi.

---

### 6. Signal Score mhanje kaay?

7 indicators paiki kiti positive disha dakhavat aahet, tyacha summary number aahe.
**−7 te +7** paryant. Jasta number = jasta indicators sahamat aahet.

Pan he **prediction nahi** aahe.
[Detail madhe vaachaa](#-signal-score-mhanje-kaay)

---

### 7. MACD mhanje kaay?

MACD stock chya movement chi strength ani disha samjun ghenya sathi ek calculation aahe.
Green mhanje recent movement positive asu shakte, red mhanje negative.

To future chi guarantee det nahi. [Detail madhe vaachaa](#2️⃣--macd)

---

### 8. RSI mhanje kaay?

RSI ek number aahe 0 te 100 chya madhe. To sangto ki stock aalikde jasta ghetla gela
aahe (70+) ki jasta viklā gela (30 chya khali).

**Laksha dyaa:** "Overbought" cha artha "aata padel" asa **nasto**.
[Detail madhe vaachaa](#6️⃣--rsi-number)

---

### 9. Options Lab khara option chain aahe ka?

**Nahi.** 🚫 He ek **calculator** aahe. Je premium numbers distat te website ne
spot price varun calculate kele aahet — exchange che khare prices nahit.

Kharokhar chya option trading sathi tumchya broker cha kharokhar cha chain ch baghaa.
[Detail madhe vaachaa](#-options-lab)

---

### 10. Gemini (AI) garjeche aahe ka?

**Agdi nahi.** AI assistant ek **optional** feature aahe.

To configured nasel tar fakt chat button kaam karnar nahi. **Baaki purna website
agdi normal chalel** — sagle pages, sagle indicators, watchlist, options, sagla kahi.

---

### 11. Data update honyala vel ka lagto?

Website **ekach veli 68 symbols** cha data aante. Pratyek stock sathi vegli request pathvli
asti tar 250+ requests gele aste — server slow zala asta ani data denari service block keli asti.

Mhanun website **ekda madhe sagla data aante** ani memory madhe thevte. Yamulech pages
lagech ughadtat, pan pahilya vela 10–15 second lagtat.

---

### 12. `--` ka disat aahe?

`--` cha artha aahe **"ya goshticha data uplabdh nahi"**.

Website kade don paryay hote:
1. ❌ Ekhada number banvun dakhavna
2. ✅ **Spashta sangna ki data nahi**

Website **dusra** marg vaparte. Mhanun `--` baghun ghabru naka — hi pramanikta aahe.

---

### 13. Market closed aslyavar data juna ka vatto?

Karan market band zalyavar **prices badaltach nahit**. Jo last price hota tocha rahto.

Weekend la kinva ratri tumhala tech numbers distil je market band hotana hote —
he agdi normal aahe.

---

### 14. Mobile var chalel ka?

**Ho, purnpane.** Phone var tables apoap **cards** bantat jenekarun bajula scroll karava
lagat nahi. Search, watchlist, stock analysis — sagla kaam karta.
[Detail madhe vaachaa](#-mobile-var-kasa-chalto)

---

### 15. Watchlist save hote ka?

**Ho, pan fakt tyach browser madhe jithe tumhi banavli aahe.**

- Dusrya computer/phone var disnar nahi
- Dusrya browser madhe disnar nahi
- Browser cha data clear kela tar jail

Hi kuthlyahi account madhe save hot nahi. [Detail madhe vaachaa](#-watchlist)

---

## 🛡️ Safety / Responsible Use

> ### Krupaya he nakki vaachaa

**1. Website cha uddesh market mahiti ani shikane aahe.**
Ti tumhala market samjun ghyaayla madat karte. Ti tumhala sangat nahi ki kaay ghyaayacha.

**2. Decision ghenya adhi kharokhar cha broker/exchange data verify kara.**
Ithla data delayed aahe. Khare paise lavnya adhi tumchya broker cha live data baghaa.

**3. Tumchya paishancha risk swatah samjun ghyaa.**
Market madhe paise lavnyat nuksan hou shakta. Tevdech lavaa jevde tumhi gamavu shakta.

**4. Past kinva current indicator future result chi guarantee det nahi.**
Sagle indicators junya data pasun bantat. Kuthlahi indicator future sangu shakat nahi.

**5. Kuthlyahi ekach number var vishwas thevu naka.**
Signal Score +7 aslya nantar pan stock padu shakto. He normal aahe.

**6. Tumhi nave asaal tar aadhi shikaa.**
Na samjun paise lavu naka. Aadhi lahan amount ne, kinva fakt baghun shikaa.

**7. Kunachyahi tips var andhala vishwas thevu naka** — ya website var pan nahi.
He ek tool aahe, guru nahi.

---

<div align="center">

### 📌 Lakshat thevnyachi goshta

**Hi website tumhala market chi MAHITI dete.
Ti tumhala ADVICE det nahi.**

Green ≠ Buy · Red ≠ Sell · Score ≠ Guarantee

---

Kahi confusion asel tar ha guide parat vaachaa.
Install karnya sathi → **[README_MINGLISH.md](README_MINGLISH.md)**

*Shubhechha! 📈*

</div>
