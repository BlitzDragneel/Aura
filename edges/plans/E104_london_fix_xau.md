# E104 — London gold price auctions (LBMA AM 10:30, PM 15:00 London time)
Common rules E100. PAXG_15m (fix times exact on 15m bars; zoneinfo Europe/London). For fix time F:
  PRE_L: long from F−60 min to F; PRE_S: short F−60 → F; POST_L / POST_S: F → F+60;
  FADE60 / FADE120: trade against the sign of the F−60 → F move from F for 60 / 120 min;
  FOLLOW60 / FOLLOW120: with that sign.  8 rules × {AM, PM} = 16 variants. Weekdays only.
Luck null: the same 8 rules anchored at every other 15-minute clock time between 07:00 and 17:00 London that is not
within 60 min of a fix (each anchor = one null grid); real best t vs 95th percentile of the null grids' best t.
FINAL control: rule at random non-fix anchors (200 draws) — real ≥ 95th pct. GC 1h cannot resolve 10:30 (secondary FINAL
only for PM-fix rules using the 15:00 London bar boundary).
