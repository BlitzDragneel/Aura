# OMEGA v6.5.50 — on top of v6.5.49: export the stored price history for research (histexport.js).
import sys, time, re
f, js, out = sys.argv[1], sys.argv[2], sys.argv[3]; s = open(f, encoding='utf-8').read(); add = open(js, encoding='utf-8').read()
i = s.rindex('</body>'); s = s[:i] + add + '\n' + s[i:]
st = sys.argv[4] if len(sys.argv) > 4 else time.strftime('%Y-%m-%d %H:%M', time.gmtime())
old = re.search(r'v6\.5\.49 (·|\\u00b7) build [0-9-]+ [0-9:]+ UTC', s).group(0); stamp = old.split(' build ')[1]
for sep in ('·', '\\u00b7'):
    o = 'v6.5.49 ' + sep + ' build ' + stamp; assert s.count(o) >= 1, o; s = s.replace(o, 'v6.5.50 ' + sep + ' build ' + st + ' UTC')
open(out, 'w', encoding='utf-8').write(s); print('v6.5.50 written to', out)
