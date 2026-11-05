# PLAN E26 — addendum D (written 2026-10-26 before any account simulation; E25 passed, so E26 runs)
1. MINIMUM ORDER: exchangeInfo cannot be read from Claude's sandbox (Binance answers 451) and does not list delisted coins.
   Assumption, stated as one: every coin accepts a 5 USDT order, except BTCUSDT and ETHUSDT, which are skipped (their minimum
   has been higher). To be checked against exchangeInfo when Maro sends it; the share of signals affected is reported.
2. SEATS: seat notional is fixed (A 5 USDT, B 10 USDT). The number of seats = floor(equity at Monday 00:00 UTC / seat),
   at most 20 (A) or 10 (B), recomputed each Monday; at least 1 while equity ≥ one seat. Equity below one seat = ruin.
3. DISASTER STOP −10% from the entry, checked from the FILL candle on (conservative: a fill candle whose low is already
   10% below the limit is stopped there); exit at the stop, or at the open of the candle that opened below it; 0.10% extra.
4. COSTS: 0.12% + 0.03% funding per trade; delisting/gap exits as E25 (5% against).
5. ACCOUNTING: P&L is booked at each exit; drawdown measured on booked equity (open trades at cost).
6. RANDOM ACCOUNTS (500): every real signal that FILLED is replaced by a random coin with a traded candle in that hour (not
   BTC/ETH, not one already held in that account), bought at that hour's close, held 24 hours, with the same stop, costs,
   delisting rule, seats and ordering. Data: the joined archive 2020-11 → 2026-10 (hourly_all), signals 2021-01-01 → 2026-10-18.
7. PASS per arm (α halved): ends above ≥ 97.5% of the random accounts, above 100, max drawdown < 35%, and gains in at least
   5 of the 6 calendar years 2021–2026 (2026 to 18 Oct). As written in PLAN E26.
