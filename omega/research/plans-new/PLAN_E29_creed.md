# PLAN E29 — CREED: why it loses, and one candidate fix judged on coins CREED has never seen
Written 2026-10-26 after the loss anatomy on the 20 creed15 coins (2020 → Oct 2026, CREED's own app code, on-time setups)
and BEFORE any data for the test coins has been downloaded or looked at.

WHAT THE ANATOMY FOUND (design data, already used by CREED research before):
- As taught: 5,053 on-time setups, +0.003R before costs, −0.118R after (costs 0.121R a trade; stops median 1.23% of price,
  ≈ 0.9× one hour's range). Exits: 51% stop, 38% breakeven scratch, 11% target at ~4.7R.
- No direction skill: +1R before the stop 48.9% (coin flip 50%), +2R 32.4% (random walk 33.3%), target 17.6% (17.3%).
  With no skill, no exit rule can help before costs (every exit variant tried in rounds 14–19 failed for this reason).
- 99% of ready setups are sweeps of the 1-hour pullback zone (coin flip in every context and era). The textbook sweep of a
  4-hour battlefield edge is almost always rejected by CREED's reward-to-risk gates (766 of 1,520 on 5 coins), and when
  accepted the REVERSAL fails more often than not: ready 32.7% (n 52), counter-trend 39.3% (n 295; 40.7% / 37.5% by era),
  gate-rejected 46.9% (n 2,370).
- 60% of the setups CREED shows are late (acceptance bars earlier): their displayed entry is not tradable.

THE CANDIDATE (C1, "edge continuation"): at a CREED event where a 4-hour battlefield edge (level kind 'lq') is swept and
accepted back inside AGAINST the 4-hour trend (CREED's verdict 'counter-trend'), on time (acceptance on the decision bar),
trade the OPPOSITE of CREED's direction (the trend side) at the acceptance close, with a symmetric bracket: stop and target
both 1R away, R = CREED's own risk distance (entry to its stop). Win = the trend side reaches +1R before −1R (from the replay
path: CREED's stop touched before its +1R); a bar touching both counts as a loss. Costs 0.06% a side.
Design result (20 coins): 1 − 0.393 = 60.7% wins, n 295, before costs ≈ +0.21R a trade.

TEST: CREED's own engine (the app, unchanged) replayed on 15-minute SPOT candles from Binance's archive (data.binance.vision,
spot/monthly/klines/<SYM>/15m), for the 40 USDT spot pairs with the highest dollar volume over 2023-01 → 2026-09 that are NOT
among CREED's 25 studied coins and not stablecoins/wrapped/leveraged tokens; Jan 2021 → Sep 2026 (whatever each coin has).
The symbol list is fixed and fingerprinted (md5) before any candle is downloaded. Run ONCE.
PASS: ≥ 60 C1 trades; win rate > 50% with a one-sided binomial p ≤ 0.05 (trades clustered by UTC day count once per day);
net average R (wins +1, losses −1, minus costs in R) > 0; and positive in both halves (2021–2023, 2024–2026).
ALSO REPORTED (not pass/fail): CREED as taught on the test coins (does the coin-flip finding replicate?), and the textbook
'ready' battlefield-edge reversals.
If C1 passes: it goes into the app as a paper-only CREED mode, grade B (passed one fair test), with a forward record.
If it fails: CREED's sweep-and-acceptance has no usable information on crypto 15-minute data, said plainly in the app.
