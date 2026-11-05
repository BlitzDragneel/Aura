# OMEGA v6.5.97 — one accuracy fix (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.97 · build 2026-10-25 10:47 UTC. Made with `python3 patch97.py <v6.5.96 build> <new build>`.

## Fixed
- **The data check skipped a market that could not be read,** so it could report "Everything checked is live and consistent" while a feed was failing. A failed read now counts as a problem: "could not be read (reason)". This is the same fix as in OMEGA Prime. Nothing else changed.

## Verification
- **s97:** a failed read is a problem, and a healthy market still passes.
- **All 31 suites pass** (s49…s97). s93, s89 and s87 need 130 s, s92 90 s and s70 60 s.
- **Other checks:** 115 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline shows 0 page errors and 0 console errors.
- **Not run on a real phone.**

## The two apps compared
Same browser, same fake exchange, phone-sized screen, first 30 seconds:

| | OMEGA v6.5.97 | OMEGA Prime |
|---|---|---|
| File size | 4,403 KB | 137 KB |
| Script blocks | 115 | 11 |
| Load to first screen | 530 ms | 70 ms |
| Network requests | 484 | 77 |
| Memory (JS heap) | 30 MB | 2 MB |
| Page elements | 10,297 | 408 |
| Pages | 28 | 5 |
| Autopilot jobs | 42 | 6 |
