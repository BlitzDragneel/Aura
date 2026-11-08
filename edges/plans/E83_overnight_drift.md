# E83 — US index overnight drift: buy the close, sell the next open (lead, 8 Nov 2026)
**Why:** a documented anomaly (most US equity gains arrive overnight, close→open; the day session adds ~0). A true
daily strategy, tradeable at Exness as index CFDs (US500/USTEC/US30/US2000) or with ETFs.
**Data:** Yahoo daily OHLC + dividends for SPY, QQQ, IWM, DIA, 2000-01 → 2026-11 (/home/user/data/stocks).
Overnight return = open_t / close_{t-1} − 1 (+ dividend / close_{t-1} on ex-dates). Intraday = close/open − 1 (benchmark).
**Variants (counted, 12):** 4 ETFs × {every night; Mon–Thu nights only (no weekends); only after a down day (close < open)}.
**Costs (two models, both reported, CFD is the one judged):**
- CFD: spread 0.015% round trip + financing 6.5%/yr ÷ 360 per calendar night held (Fri→Mon = 3 nights).
- ETF: 0.02% round trip, no financing (needs a broker that trades the auction prices).
**Periods:** DISCOVERY 2000–2015 picks the best variant by t (daily returns, Newey–West 5 lags); VALIDATION 2016–2020;
FINAL 2021-01 → 2026-11, judged once. Pass: FINAL mean > 0 after CFD costs with t ≥ 2, VALIDATION > 0 with t ≥ 1.5,
≥ 60% of years positive; also report max drawdown and the same leg during the day (intraday) for contrast.
