# OMEGA v6.5.49 — on top of v6.5.48: the Strategy Workshop (workshop.js) and one table of everything the Autopilot researches.
import sys, time
f, wsf, out = sys.argv[1], sys.argv[2], sys.argv[3]; s = open(f, encoding='utf-8').read(); ws = open(wsf, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, ('anchor count', n, count, old[:120]); s = s.replace(old, new)
rep("  var RESEARCH_JOBS = ['lab','backtests','explore','portfolio','edge',", "  var RESEARCH_JOBS = ['lab','backtests','explore','portfolio','workshop','edge',")
rep("omega_candidates_v1:1, omega_xs_v1:1,", "omega_candidates_v1:1, omega_xs_v1:1, omega_workshop_v1:1,")
rep("      threeApproaches: safe(function(){ return threeApproaches(R); }) || null,", "      workshop: safe(function(){ return window.OMEGA_WORKSHOP ? window.OMEGA_WORKSHOP.report() : null; }) || null, threeApproaches: safe(function(){ return threeApproaches(R); }) || null,")
i = s.rindex('</body>'); s = s[:i] + ws + '\n' + s[i:]
st = sys.argv[4] if len(sys.argv) > 4 else time.strftime('%Y-%m-%d %H:%M', time.gmtime())
import re
old = re.search(r'v6\.5\.48 (·|\\u00b7) build [0-9-]+ [0-9:]+ UTC', s).group(0); stamp = old.split(' build ')[1]
for sep in ('·', '\\u00b7'):
    o = 'v6.5.48 ' + sep + ' build ' + stamp; assert s.count(o) >= 1, o; s = s.replace(o, 'v6.5.49 ' + sep + ' build ' + st + ' UTC'.replace(' UTC UTC', ' UTC'))
open(out, 'w', encoding='utf-8').write(s); print('v6.5.49 written to', out)
