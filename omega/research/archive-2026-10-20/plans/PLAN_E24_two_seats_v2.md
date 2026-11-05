# PLAN E24 — Two Seats v2: rank for the bounce, cap the crash (written before running)
Written 2026-10-25 after E23 failed (ranked account 100 → 16, beaten by every random account). Exploration of E23's data showed
the ranking features raise the average bounce AND the share of catastrophic trades (deepest falls: 4.8% of trades lost >20%;
worst −93%); with two big seats one such trade ruins the account. Fresh data: the perpetuals of the final4 files from
2021-01-01 to 2023-12-31, never used for this rule family. Same signals as E23 (H1: bottom-10% 24-hour fall, limit 2σ below,
3 hours to fill, 24-hour hold, 0.12% + funding 0.03%); coins listed 30+ days; 100 USDT; at most 2 seats; seat = 10% of equity.
NEW: a disaster stop at −10% from the entry: if a candle's low reaches it, exit at the stop (or at that candle's open if it
opened below the stop) with 0.10% extra slippage.
ARMS: A = E23's ranking (deeper fall + bigger volume surge + more liquid, ranks summed within the hour);
      B = the inverse ranking (the same score, lowest first: the calmest panics).
TEST, run ONCE: each arm against 500 accounts with the same rules picking at random. PASS (per arm, 2 arms so α halved):
ends above at least 97.5% of the random accounts, above 100, and gains in each of 2021, 2022 and 2023. Reported whatever happens.
