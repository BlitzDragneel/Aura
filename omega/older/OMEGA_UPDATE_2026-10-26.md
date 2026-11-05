# OMEGA — update, 26 Oct 2026 (UTC). Read after OMEGA_UPDATE_2026-10-25c.md.

## E25 survivorship: PASSED (run once, 25 Oct 23:5x UTC)
Plans: E25 + addendum A (46e5707c…), B (8bce5ba6…: volume-0 candles are missing), C (2736f630…: stand-in data check,
side-report lists E25_exclusions.json 29ff87d9…). Script e25_run.py; result E25_result.json.
- Data check (addendum C): bdesk40 fixture (from the app's final4 exports) vs the archive: 97.5% of hours found, closes
  identical (median, 99th percentile and maximum difference 0). SCUSDT was flat with zero volume in both (a dead coin), so it is
  excluded by addendum B. The plan's full check against the final4 files is still owed; if it fails, this result is VOID.
- Universe: 883 USDT perpetuals traded 2024-01-01 → 2026-10-18, 143 of them delisted. Bar: weekly t ≥ 1.96 (2 tests).
| | trades | net a trade | weekly t | 2024 / 2025 / 2026 | survivors only | delisted coins only |
|---|---|---|---|---|---|---|
| H1 | 51,099 | +0.317% | 4.54 | +0.45 / +0.03 / +0.49% | +0.377% (t 4.85) | −0.039% (t 2.85) |
| H3 | 50,377 | +0.297% | 4.08 | +0.32 / +0.15 / +0.43% | +0.327% (t 4.19) | +0.119% (t 2.00) |
- Without stablecoin and non-crypto contracts: H1 +0.335% (t 4.63), H3 +0.304% (t 4.13).
- Tails, the real caveat: without the best 5% of trades H1 loses 0.70% a trade and H3 0.67%; the worst single trades lost
  77–93% (ESPORTS, RAVE, OM in April 2025, PUMP, H, DEXE…). 3.4% of H1 trades were on coins delisted within 90 days.
- H1's 2025 was barely positive (+0.03%).
- Finding for E22 itself: the app's final4 files contain dead coins' flat zero-volume candles (SCUSDT). They make no H1 trades
  (a limit below a flat price never fills) but can count in H3's breadth. E25 is the cleaner test.
Verdict: H1 and H3 stay Grade B (passed two fair tests; a forward record still to confirm). The tails say: many small seats.

## OMEGA Prime
Evidence now shows E25 passed and E26 being measured; the panic card says the survivorship test passed. Suites: panic 16/16,
original 10/10.

## E26 many small seats: unblocked by E25, waiting for two things
1. The 2020-11 → 2023-09 archive (downloading in Claude's sandbox).
2. Each coin's minimum order: the plan reads it from exchangeInfo, which Claude cannot reach (451). Maro can save
   https://fapi.binance.com/fapi/v1/exchangeInfo from a phone browser and upload it. Delisted coins are not in it, so an
   addendum must say what minimum they get, BEFORE the run.

## Uploaded this session
omega-v6_5-47__3_.html = v6.5.91 (22 Oct), an older build than the current v6.5.97. Not used.
