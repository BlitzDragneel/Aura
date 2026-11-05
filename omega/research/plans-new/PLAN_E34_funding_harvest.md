# PLAN E34 — funding harvest, delta-neutral (written 2026-11-01 before any result of this rule)
IDEA: buy a coin on Binance SPOT and short the same quantity on its USDT-M PERPETUAL. Price moves cancel; the short collects
funding when funding is positive (paid every 8 h). An earlier OMEGA round found such a harvest passed, but its income faded
since 2025. This plan measures what it pays NOW, with full costs, before any bot is built on it.
DATA: Binance archive: funding rates (every payment) and daily perp closes, 903 USDT perpetuals incl. delisted (E28 panel);
spot availability from the archive's spot listing (a coin qualifies only if a USDT spot pair exists). Basis (spot vs perp price
difference) is not in the data: assumed to start and end at zero; stated as a limit.
UNIVERSE each day: top 100 by 30-day dollar volume (E28's universe), with a USDT spot pair, listed 60+ days.
RULE: every R days, rank by trailing L-day average funding; hold the top k with average funding above a minimum m (annualized),
equal notional, until the next rebalance; a coin kept across a rebalance costs nothing; a coin that leaves pays exit costs.
COSTS (taker, conservative): spot 0.10% + perp 0.05% a side, plus 0.05% slippage per leg and side → 0.50% per round trip of
the pair (entry + exit). Delisting: 5% penalty on the pair. CAPITAL: spot notional + perp margin at 1× = 2 × notional, so the
yield per unit of capital is half the funding collected (reported also at 2× perp leverage: capital 1.5 × notional).
GRID (discovery only): k ∈ {1, 3, 5}, L ∈ {3, 7, 14} days, R ∈ {7, 30} days, m ∈ {10%, 20%} a year = 36 variants; luck check:
the same grid with the funding ranks shuffled across coins each rebalance.
STAGES: DISCOVERY 2021-01-01 → 2024-12-31 (best weekly t picks ONE variant); FINAL 2025-01-01 → 2026-09-30, once.
PASS: final net yield on capital (1×) ≥ 4% a year, weekly t ≥ 2.0, positive in 2025 and 2026, worst 30-day stretch ≥ −3%.
ALSO REPORTED: the last 90 days (what a day pays now on 100 USDT); the share of days the chosen coins' funding was negative.
If it passes, the Bridge gets a funding-harvest bot (testnet first). If it fails, the bot is built as a MONITOR only (shows the
live yield, places nothing) and the result is recorded.
