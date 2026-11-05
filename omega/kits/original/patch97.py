"""v6.5.97: one accuracy fix. The data check skipped a market that could not be read and could still report "all live";
a failed read now counts as a problem (the same fix as OMEGA Prime). Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
old = "Object.keys(reads || {}).forEach(function(sym){ var A = reads[sym]; if(!A || A.err) return;"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "Object.keys(reads || {}).forEach(function(sym){ var A = reads[sym]; if(!A) return; if(A.err){ out.push({ sym:sym, ok:false, issues:['could not be read (' + A.err + ')'], prem:null, candleAge:null }); return; }   // v6.5.97: a failed read is a problem, not something to skip")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.96 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.96 ' + sep + ' build ' + o + ' UTC', 'v6.5.97 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.97 · build' in s and "could not be read (' + A.err + ')'" in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
