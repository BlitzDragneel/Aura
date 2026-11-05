# PLAN E33 — forced deleveraging on 60 coins it has never been run on (written 2026-10-27 before any of their metrics data)
ORIGIN: E30 L4 on 10 coins: an hour where price fell ≥ 5% AND open interest fell ≥ 1% (positions forced out) → long for 4 hours.
Discovery 2020-09 → 2023: +75 bp a trade (t 1.80); 2024: +83 bp, but only 72 events (t 0.99). Same direction as the panic
bounce (E22/E25), too rare on 10 coins to judge.
RULE (frozen, exactly E30's pick): at the close of hour h, if the hour's log return ≤ −5% (ln) and open interest at the end of
hour h is ≥ 1% below the end of hour h−1 → buy at the close of h, sell at the close of h+4. Non-overlapping per coin.
Costs 0.20% round trip (as E30); funding ignored (4-hour hold, as E30).
DATA: the 60 coins in E33_coins.json (E29 + E31 lists, none used by E30), Binance archive futures metrics (5-minute open interest)
2023-10-01 → 2026-09-30, hourly klines from the E26 archive data (volume-0 candles missing).
COMPARISON (reported, not pass/fail): the same ≥ 5% falls WITHOUT an OI drop of ≥ 1% (does the forced-selling signature add
anything over the fall itself?); and the result per year and per coin.
PASS: weekly t ≥ 2.0, net mean > 0, positive in 2024, 2025 and 2026 (each with ≥ 20 events). Run once.
If it passes: Grade B beside H1/H3 (the same family), with a forward record. If it fails: recorded with the reason.
