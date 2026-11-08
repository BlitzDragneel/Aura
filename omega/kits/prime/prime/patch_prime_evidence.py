"""Prime evidence update (8 Nov 2026), applied after patch_prime_ux.py. Ledger rows only: no trading code changes.
 1. The old 'Funding harvest: pass' row contradicted its own E34 row (audits/bugs/BUG_REPORT.md P1): now a fail row.
 2. The November round (E37–E80, edges/RESULTS.md): 34 plans, about 1,500 counted variants, none passed; added as rows,
    with the watch-list items and the measured leverage result.
usage: python3 patch_prime_evidence.py <prime built by patch_prime_ux.py> <out>
"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:100])
    s = s.replace(a, b)


rep("    ['pass', 'Funding harvest', 'Passed, but its income has faded since 2025. Not used here.'],\n",
    "    ['fail', 'Funding harvest (rounds 7, 8, 10, 12; then E34)', 'Passed untouched tests on 2020–26 data carried by 2021; run again "
    "on 2025–26 as a delta-neutral harvest (E34) it lost 17% a year (worst 30 days −33%, one funding flip −64.6% in a month). Not used here.'],\n")

ROWS = [
    ("fail", "Panic bounce on 5m, 15m and 4h; climax on 15m and 4h (E37–E42)",
     "The panic bounce exists on 5m/15m (beat luck 2022–23, about 5 trades a day) but 2025–26 is +3 to +32 bp a trade, t 0.1–1.05, "
     "and negative without the best 5%. At 4h a random dip-buy does as well. Climax at 15m/4h: nothing. 5m/15m panic kept on paper watch."),
    ("fail", "Intraday timing: funding windows, US open, turn of month, 5m wick spikes (E43–E46)",
     "No funding-window variant was positive; the US-open fade had t 1.73 in discovery; turn of month +358 bp in 2020–23 collapsed to "
     "−37 bp in 2024 and −292 bp in 2025–26."),
    ("fail", "Trend following, breakouts, weekly momentum, ALT/BTC trend, funding as a contrarian signal, BTC→alt lead-lag (E50–E55)",
     "512 variants. Trend on BTC/ETH earned no more than a time-shifted signal (luck 70th percentile); breakouts did worse than random "
     "entries with the same stop; weekly cross-section was a 2020–22 effect (a short squeeze wiped the book in Apr 2026); lead-lag is "
     "gone by the next bar."),
    ("fail", "New data: Fear & Greed, options DVOL, Coinbase premium, perp premium, taker flow, on-chain flows, BTC-or-cash regime (E63–E70)",
     "160 variants on 7 new data sources. None passed. Perp trading 0.3% under its index (E66) and the panic bounce only when DVOL is "
     "high (E68) were strong in 2025 and faded in 2026: paper watch only."),
    ("fail", "Exit lab: take-profit, stop, trailing stop, hold time on climax and H1 (E80)",
     "480 exit designs. H1's best exit is its own 24-hour hold; every stop or take-profit made it worse. Climax with a quick +2% "
     "take-profit looked better in 2020–23 but lost in 2024 and 2025–26. The original exits stay."),
    ("fail", "Leverage 2× to 40× on every rule tested (Nov 2026)",
     "At 5% of the account per trade, 2× already liquidates on every rule; 20× and 40× wipe the account out (30–60% of trades touch "
     "the liquidation price first). The highest safe leverage measured is 1×."),
    ("run", "The passed rules re-measured on 923 coins (Nov 2026)",
     "Panic bounce H1 +127 bp a trade in 2020–23, +33 bp in 2024, +19 bp in 2025–26 (t 0.6); climax +136 / +126 / +109 bp (t 0.8). "
     "Still positive, no longer significant: the forward ticket record (50 closed tickets) decides."),
]
anchor = "    ['fail', 'Funding harvest, delta-neutral (E34)'"
assert s.count(anchor) == 1
esc = lambda t: t.replace("\\", "\\\\").replace("'", "\\'")
block = "".join(f"    ['{g}', '{esc(n)}', '{esc(d)}'],\n" for g, n, d in ROWS)
s = s.replace(anchor, block + anchor)
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst)
