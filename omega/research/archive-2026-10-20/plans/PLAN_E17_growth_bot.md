# PLAN E17 — can the app's signals grow 100 USDT under managed risk? (the Growth Bot, v6.5.92)
Written 2026-10-22 before the bot exists. A paper account of 100 USDT, forward only (from its first run), that takes every new
climax-watch trade (grade A) and every new Daily Plan paper trade (grade C) as they appear, under the Risk Guard's rules:
0.5% of equity risked per trade (1% after 30 trades), at most 2 open, no new trades after a 2% loss in a UTC day or a 5% loss
in a week, paused for review at 20% below its peak. Climax trades have no stop, so their risk is counted against a 10% adverse
move (notional = risk ÷ 10%); Daily Plan trades risk the distance to their stop. Results come from the signals' own records
(net of their costs); the bot never changes a signal.
Judged once after 26 weeks or 50 bot trades: grows if equity ends above 100 with weekly t ≥ 1.65. Reported whatever happens.
