# E105 — The CME daily break (17:00–18:00 Chicago) gap / reopen behaviour (day)
Common rules E100. The CFD/futures market is shut 17:00–18:00 CT; PAXG trades through it, so the PAXG move during that
hour is the gap a futures trader sees at the reopen. Signal G = PAXG return 17:00 → 18:00 CT (Mon–Thu evenings; the
Sunday reopen = weekend gap fade already FAILED in E3 and is excluded; Friday has no reopen).
Trade from 18:00 CT: FADE (−sign G) or FOLLOW (sign G), hold 1, 2 or 4 h; filter all gaps or |G| > 1× the trailing 20-day
std of that hour's moves → 12 variants. Data PAXG_1h search; FINAL secondary = GC_1h real reopen gaps (open of the first
bar after the break vs last close before it) with the same rule.
Costs: stress matters here (CFD spreads widen at rollover) — the stress result is required > 0 for grade A.
Luck null: same grid with G taken from a random other hour of the same evening (200 replicates).
