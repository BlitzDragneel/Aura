# OMEGA v6.5.48 — CREED's "as it could be taken" figures were measured with the wrong stop

Builds on v6.5.47. VERIFIED = run against the app in Node (the verification harness) on four random-walk histories, and the whole app crawled in headless Chromium (21 pages, no page errors, no overflow).

## Faults found and fixed
| Where | What it showed | Why it was wrong | Now |
|---|---|---|---|
| CREED history replay: "entered when shown", "a limit at the level", the lens, the Avoid list's CREED line, the Strategy board's CREED rows | e.g. "CREED entered at the close it is shown on loses" (-0.26R to -0.42R a setup on her replays) | CREED's as-taught walk moves the stop to breakeven **inside the setup object it is given**. Every measure run after it on the same object used that moved stop. For every setup that later reached +1R, the "when shown" trade got a stop at the entry: dropped as untradeable, or given a tiny risk so costs became huge in R; the limit test returned no fill. The as-taught figure itself was never affected. | The original stop is restored right after that walk. VERIFIED on random walks (no edge, so the truth is about minus the costs): entered when shown, v6.5.47 read -0.38R to -0.66R a setup, v6.5.48 -0.05R to -0.48R; limit at the level, v6.5.47 -0.24R to -0.73R on fewer fills, v6.5.48 0.00R to -0.45R on 24–58% more fills. CREED as taught: identical, every trade. |
| CREED history replays added together | Her 17 Oct report: SOL and XRP carry about 10× the costs per setup of the same setups on 13 Oct (SOL 33.5R → 346.8R), with the same gross result | Replays made under different cost settings were summed as if alike; nothing recorded which cost each used | Each replay records the cost it used; a market is replayed again when the cost setting changes. A crypto round-trip cost above 0.5% gets a plain check next to the input. |

Replay version 9: every market is replayed again (about 20 minutes each while the app is open). Until then, the "as it could be taken" figures, the lens and the Avoid list's CREED line use only version-9 replays.

## Not changed
CREED's method (sweeps, acceptance, entry, stop, target) is byte-identical to the course build. The live trackers, the desk and the paper bots (v6.5.37, .43, .44) build their own position objects and were not affected.

## Tests
`s48_test.js` (Node; needs `smoke.js` and `fake_idb.js` from the verification bundle; `HARNESS=<folder> node s48_test.js omega-v6_5-47.html omega-v6_5-48.html`): 6 checks, output in `s48_output.txt`.
