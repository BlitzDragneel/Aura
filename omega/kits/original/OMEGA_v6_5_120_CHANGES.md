# OMEGA v6.5.120 — Signal Auditor
- New page **Signal Auditor** (menu under Signals, a line on Home, the command palette; bottom bar and Home's 8 cards unchanged).
- **Log a signal:** paste the message and who sent it → `POST /auditor/parse` (OMEGA Live API) reads it and stamps the
  server's time; saved on the device (`omega_auditor_v1`). A message that is not a signal is refused with the reason.
- **Score all:** `POST /auditor/score` → per signal: status (waiting for entry / not filled / running / closed), fill, and
  outcome, pips and R for both styles (all at TP1, ladder); summary for all signals and per provider (average R, win rate,
  pips, never filled, no stop, losing run, drawdown) and the verdict line. Results survive a reload.
- **Delete** only while the status is "waiting for entry" (rule 2 of `edges/auditor/RULES.md`); enforced in code, not only by
  hiding the button.
- **Risk check:** balance, market, side, lots → `POST /auditor/risk`: cost per move/pip, the move that equals the balance,
  typical recent moves for scale.
- No token: says how to connect; logging disabled. Information only.
- Tests: new s120 (19/19). Harness `tools/livemock.js` gained `/auditor/*`. Build `python3 patch120.py <v6.5.119> <out>`.
- All suites on the v6.5.120 build: s102 (PREV = v6.5.117) s108–s113 s115–s120 s58 s78 s89 s91–s99.
