# OMEGA — update, 26 Oct 2026 (evening UTC). Read after OMEGA_UPDATE_2026-10-26c.md.

## Files received this time
| File | sha256 / md5 | What happened |
|---|---|---|
| omega-watch-2026-10-19-to-2026-10-26 | sha256 d374b74f… | E13 NOT RUN: 0 minute rows (live streams delivered nothing). Recorder fixed in v6.5.101. |
| omega-history-metals-fx1h-2026-10-23 | sha256 c6da26a6… | E15 RUN ONCE: all five forex majors FAIL. |
| omega-history-gold1h-2026-10-20 | md5 e8bbca3b… | Already used (E2, E3, E14's gold path). Nothing new to run. |
| omega-bybit-funding-final/new/seen-2026-10-19 (seen twice) | md5 2f255178…, 9ef85e1e…, 7a5de5d8… | Already used (Rounds 15 and 18: Bybit did not raise the funding yield; failed the final). Nothing new to run. |

## E15 — forex majors hour by hour: FAIL ×5 (plans/E15_result.json, plans/e15_run.py)
Eleven rules each (E14's code, unchanged), 0.015% a side, the pick = highest weekly t before 2024, judged on 2024 → 2026-10-23:
EURUSD S1 (t before +0.41 → after −1.24) · GBPUSD R6 (+0.08 → −1.75) · USDJPY S1 (+1.33 → never fired after 2024) ·
AUDUSD R4 (+0.64 → −0.55) · USDCAD S1 (+1.39 → never fired). No rule was even promising before 2024.
Note: E14's scripts carry a 2.40 pass line from an older plan; E15 used its own plan's 2.33 (it made no difference).

## E13 — Market Watch: NOT RUN (0 qualifying days); addendum B (718a5295…) fixes how backup minutes count before any
## qualifying data exists: qualification and Q1/Q3/Q4 use stream minutes only; Q2 may add backup minutes, judged stream-only.

## What to do on the device for E13 (Market Watch)
1. Install v6.5.101. Open Market Watch, start recording, and look at the three feed pills after a minute.
2. If they say "blocked", "connected but no data" or "reconnecting": the streams are not reaching the device. Try another
   network (Wi-Fi vs mobile data), the PC instead of the phone, and a browser without a blocker or VPN. The backup will
   fill prices and volumes either way, and the next export's `diag` will say what happened.
3. E13 still needs 5 days with the live streams working (liquidations come only from the stream).

## Apps
- Original v6.5.101 (omega-v6_5-47.html): see OMEGA_v6_5_101_CHANGES.md.
- Prime: Evidence lists E15 as failed and E13 as waiting, with the reason. Suites 16/16, 10/10.
