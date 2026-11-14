"""v6.5.117: never give a negative-edge setup a positive size.
The Brain's betSize (v6.2) floored a negative ¼-Kelly at 0.25x base risk ("math saying no edge is information"), so a
signal whose own estimate said "no edge" still read "Suggested size: 0.25x base risk". Now: Kelly <= 0 -> size 0x and the
signal says not to size it; positive edges keep the old clamps [0.25x, 2x] and the volatility scale. The Analysis panel's
kellyFraction() already returned 0 for a negative edge; no other sizing path used betSize. Prompted by an external audit
(OMEGA-HANDOFF, 12-14 Nov 2026: "never force positive sizing on negative Kelly"). CREED's engine is byte-identical.
usage: python3 patch117.py <v6.5.116> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:100])
    s = s.replace(a, b)

rep("  // practice), fraction second (the estimation-error buffer), caps always. Negative\n"
    "  // Kelly floors at 0.25× with the reason stated — math saying \"no edge\" is information.\n",
    "  // practice), fraction second (the estimation-error buffer), caps always. v6.5.117: a\n"
    "  // negative Kelly sizes 0× (no trade) — math saying \"no edge\" must never become a positive size.\n")
rep("    var kellyMult = fStar <= 0 ? 0.25 : Math.max(0.25, Math.min(2, fq / baseFrac));",
    "    var kellyMult = fStar <= 0 ? 0 : Math.max(0.25, Math.min(2, fq / baseFrac));")
rep("    var mult = Math.max(0.25, Math.min(2, kellyMult * volMult));",
    "    var mult = fStar <= 0 ? 0 : Math.max(0.25, Math.min(2, kellyMult * volMult));")
rep("floored at 0.25×; the math says this cell has no edge'",
    "size 0×: the math says this cell has no edge, so do not trade it'")
# signal text: say plainly when the size is zero
rep("          sig.rationale += ' \\ud83c\\udfb2 Suggested size: '+_bsz.mult+'\\u00d7 base risk ('+_bsz.why+').';",
    "          sig.rationale += _bsz.mult > 0 ? ' \\ud83c\\udfb2 Suggested size: '+_bsz.mult+'\\u00d7 base risk ('+_bsz.why+').'\n"
    "                                         : ' \\ud83c\\udfb2 Suggested size: none \\u2014 '+_bsz.why+'.';")
# self-test: 0 is valid exactly when the edge is negative
rep("      if(!(bs.mult >= 0.25 && bs.mult <= 2)) return FAIL('mult outside clamps: '+bs.mult);",
    "      if(bs.negativeEdge ? bs.mult !== 0 : !(bs.mult >= 0.25 && bs.mult <= 2)) return FAIL('mult outside clamps: '+bs.mult);")

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.116 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.116 ' + sep + ' build ' + o + ' UTC', 'v6.5.117 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.117 · build' in s and 'v6.5.116 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
