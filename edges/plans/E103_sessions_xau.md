# E103 — Gold session clock effects (day)
Common rules E100. Weekdays only (Mon–Fri local New York). Windows (local clocks via zoneinfo, 1h bars, entry at the
window's first bar open, exit at its last bar close):
  ASIA = 09:00 → 15:00 Tokyo; LONDON = 08:00 → 12:00 London; NYAM = 08:00 → 12:00 New York (handoff window);
  NYPM = 12:00 → 17:00 New York; OUTUS = 17:00 NY → 08:00 NY next day (crosses rollover: 1 night financing; this is the
  E3/E5 "outside US hours" split — contaminated, labelled); OPEN_TK = 09:00–10:00 Tokyo; OPEN_LDN = 08:00–09:00 London;
  OPEN_NY = 09:00–10:00 New York (contains the 09:30 equity open).
Directions long and short → 16 variants. Data PAXG_1h (search), GC_1h (FINAL secondary).
Luck null: every calendar day's 24 hourly PAXG returns circularly rotated by an independent random offset (keeps each
day's drift and volatility, destroys clock alignment); 200 replicates of the whole grid; real best t vs 95th pct.
Control in FINAL: the same window length placed at random clock hours on the same days (200 draws), real mean ≥ 95th pct.
