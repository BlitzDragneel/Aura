# OMEGA — update, 25 Oct 2026 (night). Read after OMEGA_UPDATE_2026-10-25b.md.

## Network
data.binance.vision and its file list (s3-ap-northeast-1.amazonaws.com) now work from Claude's sandbox. The live API
(fapi.binance.com) answers 451: Binance refuses the sandbox's region. Live data comes from the recorder or the apps.

## E25 survivorship: data ready, NOT run
- Plans: E25 addendum A 46e5707cf03ed50abde96e23a37a1912 (before any listing), addendum B 8bce5ba68c92cd21b058303a571d9991
  (after the coverage check, before any returns).
- Universe: 907 USDT perpetual folders in the archive (sorted list md5 cc602eabe741d1aec6d1b16468b1ed48); hourly files
  2023-10 → 2026-10-18 downloaded (566 MB; data fingerprint b0cc408e2a5e1afc4ecd11f1c2f02713). 0 listed files missing.
- FINDING: after a delisting the archive keeps writing flat, volume-0 candles at the last price (WAVES: last trade 2024-06-11,
  flat to 2026-10-18). Addendum B: volume-0 candles are missing; delisted = last traded hour before 2026-10-11.
  Result: 883 coins traded from 2024-01-01; 143 delisted (2024: 30, 2025: 47, 2026: 66); 740 still trading.
- Waiting for: the final4 files, for the data check the plan requires before the run. Scripts and coverage in e25kit/.

## OMEGA Prime: Grade B panic bounce (omega-prime.html)
- New Signals card: H1 and H3 on the 40 most-traded coins, a gauge of the share of coins in panic, open orders and trades,
  and a forward record. Today raises Grade B between Grade A and Grade C, labelled unconfirmed, with small seats (5–10 USDT).
  Evidence lists H1/H3 with caveats, E18–E24 as failed, E25 as measuring.
- The app's rules give exactly the research engine's trades (125 H1, 69 H3 on synthetic data). s_prime_panic_test.js 16/16,
  s_prime_test.js 10/10. Not run on a real phone or against the real Binance.

## Recorder 1.0.1
Volume-0 candles are treated as missing in /panic, /signals and /export/history; the export lists each coin's last traded
hour. 14 tests (the new one fails without the fix: a dead coin's flat candles moved the panic share from 0.111 to 0.125).

## Original build
Unchanged (v6.5.97). 27 of 31 suites pass; s67, s69, s79 and one s77 check need 4 research files missing from the bundle.
