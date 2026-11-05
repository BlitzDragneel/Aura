"""v6.5.73: round 14's model across coins, frozen, enters the Edge Lab's shadow book (judged on weeks after 18 Oct 2026)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
BLEND = "    if(cand.kind === 'blend'){ var g = new Float64Array(G.T), c = new Float64Array(G.T); cand.parts.forEach(function(p){ var R = run(G, p[0], opt); for(var t=0; t<G.T; t++){ g[t] += p[1]*R.gross[t]; c[t] += p[1]*R.cost[t]; } }); return { gross:g, cost:c }; }\n"
MODEL = BLEND + "    if(cand.kind === 'model'){ var XM = window.OMEGA_XSMODEL; if(!XM) throw new Error('the model module is missing'); var SM = XM.scores(G, cand.from), WM = xsWeights(G, function(j){ return SM[j]; }, 'LS', false), RM = wRun(G, WM); if(opt.wantW) RM.W = WM; return RM; }   // v6.5.73: round 14's frozen model\n"
rep(BLEND, MODEL)
OLD = "origin:'rounds 7, 8 and 10 (three untouched tests)' } };"
rep(OLD, "origin:'rounds 7, 8 and 10 (three untouched tests)' },\n    'research: model across coins (round 14)':{ cand:{ kind:'model', from:Date.UTC(2026, 9, 11)/DAY, key:'model across coins (round 14)' }, origin:'round 14: +37.8% a year over the market on 125 untouched coins (z 2.89), below the strict bar of 3.29; judged only on new weeks' } };")
i = s.index('<script>/* ═══ CAPITULATION WATCH'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('xsmodel.js', encoding='utf-8').read().rstrip('\n') + s[j:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.72 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.72 ' + sep + ' build ' + old + ' UTC', 'v6.5.73 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.73 · build' in s and 'v6.5.72 · build' not in s and s.count('window.OMEGA_XSMODEL = ') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
