# E107 — Intraday momentum in gold (Gao, Han, Li, Zhou 2018 style): early return predicts the late-session return
Common rules E100. PAXG_1h weekdays (New York clock). First-window return F ∈ {17:00 NY prev → 09:00 NY; 08:00 → 10:00 NY}.
Late window L ∈ {12:00 → 13:00 NY (to COMEX settlement 13:30); 12:00 → 14:00; 13:00 → 16:00}. FOLLOW (sign F) or FADE.
2 × 3 × 2 = 12 variants. Luck null: F from a random other day (200 replicates). FINAL secondary GC_1h.
