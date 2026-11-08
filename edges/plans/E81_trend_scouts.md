# E81 — UpScout / DownScout: can technical features predict real up/down moves and trend turns? (lead, 8 Nov 2026)
Model and labels fixed in edges/scouts/model.py before scoring (LightGBM, ~40 technical features, horizon 24 h;
up_move: forward 24 h return >= +1 sigma24; turn_up: 12-bar MA slope flips from <= 0 to > 0 with >= +0.5 sigma24; mirrors
for down). 30 liquid coins, hourly, every 3rd hour sampled. One configuration, no tuning: train 2020–23 -> score 2024;
train 2020–24 -> score 2025–26 (judged once).
Pass for a scout: 2025–26 AUC >= 0.55 and Brier skill > 0, AND the tradeable check (top-2% probability, 24 h hold,
taker costs) mean > 0 with t >= 2 in 2025–26 and > 0 in 2024. Otherwise it runs as a forward-scored predictor only.
