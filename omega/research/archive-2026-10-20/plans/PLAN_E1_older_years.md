# PLAN E1 — one-shot test of the three frozen setups on years they have never seen
Written 2026-10-20, before any 2021–2023 result for these rules was computed.

Data: omega_history_final4_a–d (125 older Binance USD-M perpetuals, hourly, funding), signals from 2021-01-01 00:00 UTC to
2023-12-31 23:00 UTC (bars from 2020-11-19 serve as warm-up). The 199 young coins did not exist then.

Rules, exactly as frozen (engine3.py, true fixed risk, no minimum-order rounding):
- A: 72-hour breakout, US hours (13:00–20:00 UTC bars), volume ≥ 2× the 168-hour median; 5-unit method (5 × 0.2, bank 60% at
  +1R with stop to entry, add 0.2 at each +1R up to 3, trail 3 ATR, 168 h).
- B: momentum burst, US hours (3σ, 3× volume, close in the top/bottom 40%); pyramid (add 1 unit each +1R up to 3, trail 3 ATR, 168 h).
- C: the new method on A's entry: limit 0.5 ATR back (6 h), stop 3 ATR, no adding, half at +1R, trail 3 ATR, 168 h.
Common: liquidity ≥ $5M a day (480 h), listed ≥ 820 h, stop 2 ATR (A, B) / 3 ATR (C), costs 0.10% a side, funding hourly,
one market at a time, strongest signal first, 100 USDT, 1% risk.

Pass (each setup on its own): the account ends above 100 AND beats at least 95% of 100 coin-flip-direction accounts.
Reported whatever the result. No rule is changed after this run.
