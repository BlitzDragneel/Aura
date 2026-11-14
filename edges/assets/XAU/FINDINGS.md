# XAU — findings (from edges/RESULTS.md, research of 14 Nov 2026)

Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

## Gold (XAU) bot — E100–E115: nothing passed on any horizon (day, swing, hold)
Common rules `plans/E100_common_xau.md` (md5 78d284f7…). Code `edges/assets/XAU/code/`. Numbers
`edges/results/E101…E115_result.json` plus `E101_perp_description.json`; md5s in `assets/XAU/code/plan_md5.json`.
304 gold variants are logged in attempts.jsonl; 24 are empty rows from a first E114 run with a timestamp bug, rerun.
Costs: CFD 0.02%/side plus 6.5%/yr financing per NY rollover (stress 2×); daily rules 0.05% of turnover. Periods per the
brief. Day rules were searched on PAXG 2020–23 (hourly correlation with GC 0.984) and checked on GC 1h 2026.
Not available: Dukascopy (not attempted); BLS calendars answer 403, so CPI/NFP/PPI were skipped. FOMC dates come from
federalreserve.gov. Fetched: PAXG 15m, Binance XAUUSDT perp 15m/1h + funding, Yahoo DXY/^IRX/^TNX (`code/fetch_xau.py`).
**`edges/assets/XAU/FINDINGS.md` could not be created: this agent's file tool refuses new .md report files. This section
is the full findings, and the lead should copy it there.**

**E101 handoff re-run** (account %, 10k, 25 risk/trade, 6 bp/side):
| family | handoff Sep–Oct 26 | re-run, same sample (perp 15m) | PAXG 2025-01→26-10 | GC 1h 2026 |
|---|---|---|---|---|
| price-only model | 71 tr −0.71% | 14 tr −0.35% | 236 tr −4.9% (at CFD 2 bp: +5.5 bp/tr, t 1.52) | 25 tr −2.0% |
| break-even/side | ≈5.2 bp | 5.3 bp (14 tr) | 4.7 bp | <0 |
| breakout | 433 −36.3% | 272 −24.2% | 2,962 −255% | 299 −8.9% |
| compression | 118 −13.8% | 152 −14.5% | 1,646 −142% | 140 −4.3% |
| accepted retest | 82 −5.3% | 217 −19.5% | 2,298 −190% | 232 −6.2% |
| failed auction | 100 −8.2% | 97 −8.0% | 979 −89% | 75 −1.1% |
In NY 08–12 the model made +0.09% on 2 trades vs a constant short on the same bars −0.24%. Shorting every 08:00 NY lost
(−1.3% perp, −52% PAXG), so the claim that "constant short beat the model" is not reproduced. Weekend windows were flat
73.9% (perp) / 59.9% (PAXG) vs 82.8% claimed. The movement watch BEAT its vol/clock control on 15m (log loss 0.453 vs
0.476 perp, 0.510 vs 0.537 PAXG; large-move rate 21.8% → 38.4% in watch windows) but not on GC 1h (0.433 vs 0.411).
Perp vs futures (11 months, too short to judge): ρ 0.984; it trades 0.42% below GC; 29% of its hours fall in the CME
closure, with volatility 9 vs 35 bp/h; funding is paid every 4 h, about **+12.7%/yr paid by longs**.

| Plan | Horizon | Idea | Var. | Discovery best | Luck (real vs null p95) | Verdict |
|---|---|---|---|---|---|---|
| E102 | day | FOMC follow/fade 4 h | 4 | follow 60 m +14 bp, t 1.49 (26 ev.); 2024 +13 (8), 2025–26 +30 (16) | — | FAIL (t, events) |
| E103 | day | sessions Asia/London/NY, opens, outside-US | 16 | OUTUS long +0.7 bp, t 0.38 | 0.38 vs 0.13 | FAIL (nothing ≥ cost) |
| E104 | day | London fix 10:30/15:00 | 16 | AM fade −1.0 bp (gross +3) | −0.4 vs 0.29 | FAIL |
| E105 | day | CME break gap fade/follow | 12 | fade big gaps 2 h +1.2, t 0.58 | 0.58 vs 0.12 | FAIL |
| E106 | day | session range breakout, vol gate, maker fade | 20 | maker fade −0.4 (gross +3.6) | not needed | FAIL |
| E107 | day | intraday momentum | 12 | all < 0 | — | FAIL |
| E114 | day | hourly panic bounce / spike fade | 24 | spike-fade limit k3 H12 +20 bp, t 1.89 | 1.89 vs 3.41 | FAIL (luck) |
| E108 | swing | TSMOM 5–250 d, vol 10%, CFD-financed | 12 | 250 d long/flat, NW t 1.97 | 1.97 vs 1.85 | FAIL (t < 2) |
| E109 | swing | post-shock drift/reversal | 32 | 3σ down, follow 1 d +33 bp, t 1.87 | 1.87 vs 2.43 | FAIL (luck) |
| E110 | swing | DXY trend / 10y yields | 10 | DXY < MA200 long/flat, t 0.92 | 0.92 vs 1.77 | FAIL |
| E111 | hold | 8 trend/vol controllers + E85 | 9 | none beats B&H AND matched vol-only in 2016–20 and 2021–26 | only 12-1 mom ok | FAIL |
| E112 | hold | seasonality (months, Aug–Feb, TOM, weekday) | 5 | best-6 months on−off t 2.52 | 2.52 vs 3.46 | FAIL (reverses 2016–20) |
| E113 | hold | vol-managed gold (contaminated: E85/E111 control) | 2 | excess Sharpe 0.62 vs B&H 0.49 | 0.13 vs 0.08 gain ✔ | not a pass (2016–20 0.76 < 0.79) |
| E115 | hold | rotation gold/silver/cash | 3 | worse than gold in all periods | fails | FAIL |
Disclosure: the hold plans (E111/E112/E113/E115) and E102 report every registered variant in validation/FINAL by design.
None was selected from those numbers and none passed.

Holding, unfunded, cash in T-bills — Sharpe / CAGR / max DD for 2000–15 | 2016–20 | 2021–26:
- **buy & hold:** 0.57/9.3%/−44% | 0.86/12.4%/−17% | 0.75/13.0%/−27%.
- **via CFD swap 6.5%:** 0.21/2.3%/−58% | 0.42/5.2%/−25% | 0.40/5.8%/−31%.
- **vol-only 10%:** 0.78/7.3%/−29% | 0.87/8.3%/−13% | 1.04/10.2%/−13%.
- **E85:** 0.70/4.8%/−23% | 0.68/5.0%/−11% | 1.10/8.5%/−8%.

**Best-evidence rules (all LABELLED NOT PASSED, paper-watch only, nothing in approved.json, no strategy file):**
- *Day:*
  - Long gold outside US hours (17:00 → 08:00 NY): +0.7 / +7.4 / +5.8 bp (PAXG), +5.4 bp (GC 2026); t never ≥ 2, and the
    split was already seen in E3/E5.
  - The 15m price-only model: positive only if costs stay ≤ ~4.7 bp/side.
  - FOMC 1-hour follow: few events.
  - Gross intraday edges are 0–4 bp against a 4 bp CFD round trip: gold day-trading is a cost problem.
- *Swing:* 12-month trend, long/flat with a 10% vol target (t 1.97). The 6.5%/yr CFD financing is the main drag.
- *Hold:* vol-managed gold, min(1, 10%/max(vol20, vol60)) with cash in T-bills (E113).
  - It halves drawdowns (−13% vs −27% in 2021–26) and raises Sharpe in 2000–15 and 2021–26; luck check ok; whole-sample
    bootstrap p = 0.052.
  - It misses 2016–20 and is contaminated, so it is a drawdown limiter, not an edge. It gives up CAGR in bull runs
    (10.2% vs 13.0%).
  - Hold gold unfunded: CFD swaps and perp funding (≈ 6.5–12.7%/yr) eat most of gold's long-run return.
- *Leverage:* nothing passed, so there is no table. 20× (≈ −4.5% liquidation) and 40× (≈ −2%) are liquidated by ordinary
  bad gold days.

