# E94 — BTC holding: combinations judged against buy-and-hold on Sharpe AND drawdown (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Builds on E84 (vol-managed, FAIL luck) and E85 (trend/vol controller, FAIL as edge,
3–7× smaller drawdowns). Daily UTC, exposure decided at the close of day d, held over d+1. Costs: BTC 0.10% of turnover +
funding on the BTC exposure; gold leg = PAXG (0.10% per side of turnover, no funding; PAXG data ends 2026-10-31, so all
FINAL numbers stop there for every candidate). Rebalance: daily for signals, weights drift otherwise; mixes rebalanced
on the first day of each month.
## Candidates (8)
H1 BTC buy-and-hold (benchmark). H2 E85 controller (cited, recomputed). H3 BTC 200-day MA: long when close > SMA200, else
cash. H4 H3 with exposure × min(1, 40%/σ20_ann). H5 static 50/50 BTC/gold (monthly). H6 inverse-vol BTC/gold (weights ∝
1/σ60, monthly). H7 H6 with the BTC leg moved to gold when BTC < SMA200. H8 H7 with total exposure scaled by
min(1, 20%/portfolio σ60).
## Judgement
For each: Sharpe, CAGR, max drawdown, NW t of daily excess over cash 0%. Selection in DISCOVERY (2020–23; mixes from
2020-09): the highest Sharpe among candidates whose max drawdown ≤ 60% of H1's. PASS (holding): in VALIDATION and FINAL,
Sharpe > H1 Sharpe AND max drawdown ≤ 75% of H1's, and positive return in FINAL. Luck/timing check: for H3/H4/H7/H8 the
SMA signal circularly shifted (≥ 180 days, 200 shifts) — the real Sharpe gain over the shifted version must be ≥ 95th
pct for the TIMING to count as an edge; mixes without timing (H5/H6) are allocations, reported as such (no timing claim).
Honesty note fixed in advance: lower drawdown usually comes with lower return; both are reported.
