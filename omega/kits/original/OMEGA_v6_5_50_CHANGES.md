# OMEGA v6.5.50 — export the price history for research

Builds on v6.5.49. VERIFIED in Node (round trip of the file) and in headless Chromium (button, download, file decodes).

## New
OMEGA Strategy → Report for review → **Export price history for research**: hourly bars of every stored market
(open, high, low, close, volume, taker-buy share), built from the same stored history the Research Lab reads,
gzip-compressed. Prices only: no keys, no journal, no settings (checked before saving). About 0.25 MB per market for
3 years; roughly 10 MB for 40 markets.

Format `omega-history` v1: per market, times as hours since 1970 (first absolute, then differences), prices as
integers in units of 10^-dp (close: first absolute, then differences; open, high and low as distances from the close),
volume to 4 significant figures, taker-buy share in thousandths. A decoder is `omega_history.py`.

VERIFIED: 3 markets decode back to the app's own hourly bars, times exact and prices within 2×10⁻⁵ of price;
in Chromium, 3 synthetic markets × 3 years exported to a 0.8 MB file that decodes in Python.

## Not changed
Everything else, including v6.5.48's replay fix and v6.5.49's workshop.

## Tests
`s50_test.js` (4 checks, Node with `smoke.js` and `fake_idb.js`).
