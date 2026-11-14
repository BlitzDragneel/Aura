# E97 — BTC+gold allocation on an untouched earlier period, 2014–2019 (holding) (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. HONESTY NOTE: E94 (2020–26) chose H2 (fails: FINAL return −0.2%/yr), while the
inverse-volatility BTC/gold mix H6 beat BTC buy-and-hold on Sharpe and drawdown in 2024 and 2025–26 without being chosen.
H6 is therefore selected AFTER seeing 2024–26. This plan tests H6, unchanged, on 2014-01-01 → 2019-12-31, a period no
BTC bot plan has used (perp data start 2020), as its single FINAL.
Data: BTC daily PriceUSD from the CoinMetrics community API (fetched now, saved to
/home/user/data/coinmetrics/btc_price_long.parquet; spot reference price, no perp, so no funding); gold = GC=F daily
closes (/home/user/data/metals/GC_1d.parquet), aligned by calendar date, weekends/holidays carried forward (no return).
Rule H6 exactly as E94: weights ∝ 1/σ60 (annualised std of 60 daily log returns, BTC √365, gold √365 on the carried
series), set on the first day of each month, daily rebalance to the targets, 0.10% of turnover per leg.
Information rows (not judged): H7 (BTC leg → gold below BTC SMA200), H2 (E85 controller), 50/50.
PASS (H6, 2014–2019): Sharpe > BTC buy-and-hold Sharpe AND max drawdown ≤ 75% of buy-and-hold's AND total return > 0,
AND positive return in ≥ 4 of the 6 calendar years. Also reported for 2014–16 and 2017–19 separately.
If it passes: grade B (selected after seeing 2024–26, confirmed once on untouched 2014–19), status paper, max_leverage 1.
