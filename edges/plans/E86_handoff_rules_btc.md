# E86 — External-handoff rule families re-run on BTC 15m, 2022 → Nov 2026 (BTC bot, 14 Nov 2026)

Common rules: `E86_common_btc.md`. Owner asked that every handoff test be re-run on BTC over the full history.
The handoff's code is lost; where it gave definitions they are used, otherwise the simplest reading below is FIXED
here before any run (one configuration per family; no tuning).

## Trade engine (handoff definitions)
15m BTCUSDT bars (from 5m). Signal at the close of bar i. "Entry one full bar later" = market entry at the OPEN of bar
i+2 (the bar i+1 is skipped entirely). ATR14 = Wilder ATR over 14 bars known at the signal close. Stop = entry ∓ 2×ATR,
target = entry ± 6×ATR, max hold 16 bars (4 h) → exit at the close of the 16th bar after entry. If a bar touches both
stop and target: stop first. A gap through the stop exits at that bar's open (adverse gap). No overlap: a new signal is
ignored while a trade from the same family is open. Costs taker both sides (0.07% per side) + funding (common rules).
Handoff-style account metric also reported: risk 0.25% of a 10,000 account per trade (size = 25 / stop distance, capped
at 1× notional), 6 bp and 12 bp per side, so the Sep–Oct 2026 window can be compared with its table.

## Families (long and short unless stated)
1. Price breakout: close(i) > max(high of the prior 16 bars) → long; close < min(low of prior 16) → short.
2. Compression: ATR14/close at bar i in the lowest 20% of its trailing 960 bars (10 days) at some bar in the prior 8,
   and close(i) breaks the prior 16-bar range as in 1.
3. Compression + confirmation: as 2, and bar i+1 also closes beyond the broken level (entry then at the open of i+3).
4. Accepted retest: a 16-bar breakout (as 1) happened in the prior 8 bars at level Lv; bar i trades back to within
   0.25 ATR of Lv (low ≤ Lv + 0.25 ATR for longs) and closes beyond Lv on the breakout side → trade the breakout side.
5. Failed auction (brief definition): bar i's high exceeds the prior 16 bars' high by ≥ 0.1 ATR, close back below that
   high, range(i) ≥ 1.5 ATR, close location (c−l)/(h−l) ≤ 0.4 → short; mirror for lows (close location ≥ 0.6) → long.
Spot-led / spot-confirmed and OI/flow variants: NOT re-run (no 15m spot or OI history here — stated, not invented).

## Control
Random-entry control per family: same number of trades per period, same long/short mix, entries at random 15m bar
opens, identical stop/target/hold engine, 200 draws; report the family mean vs the control's 95th percentile.

## Judgement
Each family judged by the common pass mark (FINAL t ≥ 2, VALIDATION t ≥ 1.5, ≥ 60% years positive, beats control).
Also reported: Sep 1 – Oct 31 2026 window vs the handoff's numbers (BTC price breakout 383 trades −29.6%, compression
137 −14.6%, compression+conf 16 −1.61%, accepted retest 96 −8.14%, failed auction unconfirmed 94 −4.63%).
Five attempts logged (one per family, period "all").
