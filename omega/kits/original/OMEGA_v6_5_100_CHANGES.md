# OMEGA v6.5.100 — "Why signals are rare": the research record E22–E28 (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.100 · build 2026-10-26 13:03 UTC. Made with `python3 patch100.py <v6.5.99 build> <new build>`
(reads research100.js from its own folder).

## New
A card under the panic-bounce card on the **Signals** and **Edge Lab** pages. It says plainly why signals are rare:
OMEGA only signals when a rule that passed a fair test fires, and **no rule that trades every day has passed (9,240 tried, E28)**.
- PASSED: panic bounce H1/H3 (E22, E25), with E25's numbers and the Grade B caveats.
- FAILED: H1 as a 100 USDT account (E26: drawdowns 56%/59%, gains in 4 of 6 years).
- FAILED: the daily-trading search (E28) — small coins over big and funding carry (worked 2021–22, about zero or below in 2024);
  next-day direction (costs win); daily dip-buying limit orders (deep dips come on 28% of days; forced daily it is market
  risk, and random coins did as well); hour-of-day timing (moves 0.03–0.09%, costs 0.12–0.20%).
- The next ideas not yet run. Stacked rows, readable on a phone (checked on screenshots).

## Tests
- New **s100** (3): the card on both pages, under the panic card, with E25/E26/E28's results; no overflow on phone or computer; no errors.
- **Test fixes (no app change):** s84–s97 checked the build number with a pattern that stopped at 99; widened to accept 100+.
  s98's panic check asserted "only the planted coins" — wrong at some hours, because the test's synthetic coins can genuinely
  dip into their own bottom 10%; it now asserts every planted coin is flagged and every flagged coin is really below its line.
- Results on v6.5.100: 31 of 35 suites pass in full (s49…s100). s67, s69, s79 and one s77 check still need the research files
  missing from the bundle. 28-page crawl: 0 page errors, 0 console errors. 117 script blocks, 0 syntax errors. Phone guard clean.
- **Not run on a real phone.**
