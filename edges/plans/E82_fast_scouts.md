# E82 — Fast scouts on 15-minute candles (lead, 8 Nov 2026)
Owner's request: trend changes inside an hour must not be missed. Same model, features and labels as E81
(edges/scouts/model.py), counted in 15m bars built from the 5m files; horizon 16 bars = 4 h; 30 liquid coins, every 4th bar.
One configuration: train 2022–23 -> score 2024; train 2022–24 -> score 2025–26 (judged once). Pass mark as E81
(AUC >= 0.55, Brier skill > 0, top-2% trades after costs > 0 with t >= 2 in 2025–26 and > 0 in 2024).
Whatever the verdict, the fast scouts run live as forward-scored information (every 15 minutes) and feed no bot.
