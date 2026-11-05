"""Assemble OMEGA Prime (omega-prime.html) from its shell, its own core, and six tested modules taken from the original build.
The modules' storage is switched to PRIME_LS (prefix "prime:"); research-only sections are removed from them."""
import re, json, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/b83/omega-v6_5-96.html'
s = open(SRC, encoding='utf-8').read()
def module(head):
    i = s.index('<script>/* ═══ ' + head); j = s.index('</script>', i) + len('</script>'); return s[i:j]
mods = [module('MARKET READ (v6.5.89)'), module('DAILY PLAN (v6.5.91)'), module('RISK GUARD AND GROWTH BOT'), module('MARKET COCKPIT (v6.5.93)'), module('DATA CHECK AND BASELINES (v6.5.96)'), module('EVENTS AND MONTHLY REVIEW (v6.5.94)')]
out = []
for m in mods:
    n = m.count('localStorage.'); m = m.replace('localStorage.', 'PRIME_LS.'); assert 'localStorage' not in m.replace('PRIME_LS', ''), 'storage left'
    out.append((m, n))
mread, dplan, rguard, cockpit, truth, review = [x[0] for x in out]
# research-only sections out
mread, k1 = re.subn(r"    var D = checkDays\(\); var good = .*?\n    h \+= '<div class=\"mr-sec\"><h4>Market Watch recording \(for plan E13\)</h4>.*?\n", "    h += '</div>';\n", mread, flags=re.S)
rguard, k2 = re.subn(r"    h \+= '<div class=\"dp-card\"><h3 class=\"dp-h\">Research exports \(automatic\)</h3>.*?</p></div>';\n", '', rguard)
assert k1 == 1 and k2 == 1, (k1, k2)
# accuracy fix: a market that could not be read is a problem, not something to skip
old = "Object.keys(reads || {}).forEach(function(sym){ var A = reads[sym]; if(!A || A.err) return;"
assert truth.count(old) == 1
truth = truth.replace(old, "Object.keys(reads || {}).forEach(function(sym){ var A = reads[sym]; if(!A) return; if(A.err){ out.push({ sym:sym, ok:false, issues:['could not be read (' + A.err + ')'], prem:null, candleAge:null }); return; }")
# the official event calendar from the Market Clock
mc = module('MARKET CLOCK (v6.5.79)')
cpi = re.search(r'"cpi":(\[[^\]]*\])', mc).group(1); fomc = re.search(r'"fomc":(\[[^\]]*\])', mc).group(1)
clock = ("<script>/* ═══ PRIME EVENT CALENDAR — official dates carried over from the original build's Market Clock (v6.5.79): US CPI from the BLS\n"
         "   release schedule (08:30 ET), FOMC statements from the Federal Reserve calendar (14:00 ET; 2027 tentative). ═══ */\n"
         "window.OMEGA_MARKETCLOCK = { DATA:{ cpi:" + cpi + ", fomc:" + fomc + " } };\n</script>")
shell = open('prime_shell.html', encoding='utf-8').read(); pre = open('prime_pre.js', encoding='utf-8').read(); post = open('prime_post.js', encoding='utf-8').read(); panic = open('prime_panic.js', encoding='utf-8').read()
core = '\n'.join([pre, clock, mread, dplan, rguard, cockpit, truth, review, post, panic])
html = shell.replace('<!--CORE-->', core)
assert html.count('<!--CORE-->') == 0 and 'window.OMEGA_CLIMAX = ' in html and 'window.OMEGA_RGUARD = ' in html and 'window.OMEGA_PANIC = ' in html
open('omega-prime.html', 'w', encoding='utf-8').write(html)
print('omega-prime.html', len(html), 'bytes | storage calls switched:', [x[1] for x in out], '| CPI dates', cpi.count('Z"'), '| FOMC dates', fomc.count('Z"'))
