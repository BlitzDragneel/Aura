# OMEGA — update, 26 Oct 2026 (early UTC). Read after OMEGA_UPDATE_2026-10-26.md.

## E25's owed data check: PASSED (the plan's own check, on the final4 files)
324 final4 coins against the archive, 3,896,831 hours: median difference 0, 99.9th percentile 0. 66 hours differ by >0.1%, 58 of
them in one hour (2024-10-28 21:00 UTC, many coins at once: a one-hour glitch between Binance's API and its archive; the next
hour agrees). E25 stands. Not in E25's universe: DODO, LUNA, and three Chinese-named coins (excluded by addendum A's A–Z rule,
written before any data). Dead coins inside final4 (flat zero-volume candles): FTT, RAY, SC, and partly DGB, GLMR, RAD.

## E26 many small seats: FAILED (run once)
Plan + addendum A (9e0a6e06…; minimum order 5 USDT for every coin since exchangeInfo is unreachable; seats sized each Monday;
a seat reserved at the order; random accounts copy the real timeline in random coins). Data: archive 2020-11 → 2026-10-18,
903 coins traded from 2021, 163 delisted (old archive fingerprint 81d4e339…). 290,653 H1 signals, 69,775 filled.
| arm | 100 USDT → | trades | beats random | max drawdown | years with a gain | verdict |
|---|---|---|---|---|---|---|
| A 5 USDT seats, ≤20 | 943 | 15,038 | 100% | −56% (peak 1,448 Mar 2024 → 639 Jun 2026) | 4 of 6 | FAIL |
| B 10 USDT seats, ≤10 | 1,189 | 8,622 | 100% | −59% (1,512 Mar 2024 → 612 Aug 2024) | 4 of 6 | FAIL |
- 2021 made most of it (A: 100 → 641; trades +2.1% on average). Since 2022 trades average +0.1–0.4%; 2026 is negative
  (A −0.04%, B −0.16% a trade). Without BTC and ETH: 1,022 and 1,207 (no change in the verdict).
- The −10% stop closed 20–21% of trades. A clue for a future written test (does the stop cut the rebounds?), not a conclusion.
- Random accounts copy the real account's seat sizes, which grew large, so many of them go below zero: "beats 100%" is about
  coin choice, not a sign the account is safe.
- Result: E26_result.json (md5 ee7e5e91…), scripts e26_run.py, e26_account.py.
What it means: H1's per-trade edge is real (E22, E25) but as a 100 USDT account it has been far too rough, and it has faded
since 2021. Both apps now say so and keep it on paper.

## Apps
- **Original v6.5.99** (omega-v6_5-47.html): the panic card reports E26. v6.5.98 added the panic-bounce watch; full check in
  OMEGA_v6_5_98_CHANGES.md.
- **Prime:** Evidence lists E26 as failed; the verdict says paper only. Suites 16/16 and 10/10.

## E27 CPI: waiting for the release dates
bls.gov refuses the sandbox ("Access Denied", 403). BTC and ETH are in creed15 part 1, so creed15 part 2 is not needed.
Needed from Maro: the BLS CPI release archive page, saved from a phone browser.

## Still owed
exchangeInfo (only to report E26's minimum-order share); research files watch16.py, partB_fresh.json, round12_final.json,
round17.json (4 suites of the original).
