# OMEGA v6.5.95 — a tidier Analysis scanner (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.95 · build 2026-10-22 20:33 UTC. Made with `python3 patch95.py <v6.5.94 build> <new build>`.

## Changed
- **The "Every market, one engine" scanner** on the Analysis page now shows the markets that have a reading first, in its usual order.
- **Unread markets are folded into one compact card** ("N not read yet", or "waiting their turn" while scanning) listing their names as small chips. Before, there were up to 60 full-size empty cards: about 3,200 px of scrolling, now one 396 px card.
- **Cards with data are unchanged:** same function, same content, same "In depth" button.

## Verification
- **s95 (2 checks):** the version, and the data card function unchanged; in a browser, the 60 unread markets fold into one card of 60 names, with no overflow and no page errors.
- **All 29 suites pass** (s49…s95). s93, s89 and s87 need a 130-second timeout.
- **Other checks:** 114 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
