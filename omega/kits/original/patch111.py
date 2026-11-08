"""v6.5.111: slimmer Brain page. The Brain ENGINE (OMEGA_BRAIN: evaluate, betSize, recommend, feedObservation...) is
unchanged; the in-app bots and Signals keep using it. Only research tooling leaves the page, because research now runs
outside the app (edges/ in the repo, the progress board https://omega-board.onrender.com):
 - the Hypothesis registry with its "Export research package" button (their scripts already skip a missing element).
Kept: Reason about a market, What it has learned, You x OMEGA, Claude council, Evidence ledger, Prediction scorecard,
range/tail forecasts, situation timeline. A one-line pointer to the progress board replaces the registry.
usage: python3 patch111.py <v6.5.110> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()
a = s.index('      <section class="bd-card"><h3>Hypothesis registry')
b = s.index('      <section class="bd-card"><h3>Evidence ledger')
assert 0 < b - a < 2000, b - a
s = s[:a] + ('      <p class="hint" style="margin:0 0 12px;">Research ideas, tests and their verdicts now live on the '
             '<a href="https://omega-board.onrender.com" target="_blank" rel="noopener">progress board</a>.</p>\n') + s[b:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.110 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.110 ' + sep + ' build ' + o + ' UTC', 'v6.5.111 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.111 · build' in s and 'Hypothesis registry' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
