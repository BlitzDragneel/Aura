# PLAN E26 — "many small seats": H1 on a 100 USDT account, sized to Binance's minimum (written before running)
Written 2026-10-25, before E25's data has been downloaded. Lesson from E23/E24: two big seats turn the panic bounce's fat left tail
into ruin; many small seats should keep the average and shrink the ruin.

SIGNALS: E22 H1 exactly as in PLAN E25 (limit 2σ below, 3 hours to fill, 24-hour hold), 0.12% round trip + 0.03% funding per
trade; coins listed 30+ days. Run ONLY if H1 passes E25.
ACCOUNT: 100 USDT start, 1× (notional = margin), no compounding of seat size within a week; seat size reset each Monday.
ARMS (m = 2): A = seats of 5 USDT notional (up to 20 open); B = seats of 10 USDT notional (up to 10 open).
- A signal takes a seat only if one is free AND the coin's minimum order (from exchangeInfo at test time; coins whose minimum is
  above the seat are skipped) fits. Signals in the same hour are taken in order of the deepest 24-hour return first.
- DISASTER STOP: −10% from the fill; if a candle's low reaches it, exit at the stop (or at the candle's open if it opened below)
  with 0.10% extra slippage — the same stop as E24.
- Delisting: as in E25 (last close, −5% haircut).
DATA: the delisted-inclusive universe from E25, 2021-01-01 → 2026-10-18.
CAVEAT, stated now: the surviving coins in this window were already used by E22–E24, so this is NOT a clean out-of-sample test.
It can fail H1's sizing, but a pass only earns "supporting evidence"; confirmation is the forward paper record (in Prime and the
recorder) at 50 trades.
TEST, run ONCE: each arm against 500 accounts with the same seats and rules taking random entries (same hours, random coins
with data). PASS per arm (α halved): ends above ≥ 97.5% of random accounts, above 100, max drawdown < 35%, and gains in at
least 5 of the 6 calendar years. Reported whatever happens, with the equity curve, the drawdown, and signals skipped for lack of
a seat or minimum size.
