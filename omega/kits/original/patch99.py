"""v6.5.99: plan E26's result in the panic-bounce card. H1 run as a 100 USDT account of small seats FAILED (drawdowns of
56–59%, gains in 4 of 6 years), so the card no longer suggests sizing it that way. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
pairs = [
 ('<script>/* ═══ PANIC BOUNCE (v6.5.98) — ', '<script>/* ═══ PANIC BOUNCE (v6.5.98, v6.5.99) — '),
 ("""   lost 77–93%: many small seats, never one big one. Breadth here counts the 40 watched coins (the test used every perpetual).""",
  """   lost 77–93%. Run as a 100 USDT account of 5 or 10 USDT seats with a −10% stop (E26, 2021 → Oct 2026, v6.5.99): FAILED,
   drawdowns of 56–59% and gains in 4 of 6 years; 2021 made most of it and since 2022 the trades average +0.1–0.4% (2026
   negative). So it stays a paper record. Breadth here counts the 40 watched coins (the test used every perpetual)."""),
 ("""So: many small seats (5–10 USDT each on a 100 USDT account), never one big one. Plan E26 tests exactly that.</p>""",
  """<b>Plan E26 ran it as a 100 USDT account of small seats (5 or 10 USDT, −10% stop), 2021 → Oct 2026: it FAILED.</b> It ended at 943 and 1,189 and beat random coins at the same hours easily, but fell 56% and 59% from its peak and gained in only 4 of 6 years; 2021 made most of it, and since 2022 the trades average +0.1–0.4% (2026 negative). Keep it on paper.</p>"""),
]
for a, b in pairs: assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.98 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.98 ' + sep + ' build ' + o + ' UTC', 'v6.5.99 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.99 · build' in s and 'v6.5.98 · build' not in s and 'it FAILED' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
