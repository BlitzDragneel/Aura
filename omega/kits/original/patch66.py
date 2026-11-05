"""v6.5.66: download one futures file on its own (and save-again links), because a phone can drop a download the app
hands it; the accessibility self-check no longer warns when it runs before page setup."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
i = s.index('<script>/* ═══ FUTURES DATA FOR RESEARCH, THE REST IN ONE RUN (v6.5.65)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('futexport.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# accessibility pass: always runs at setup (even if an earlier setup step throws), and the self-check can run it itself
rep("    applyDisplay(); applyAccount(); omegaPersoRender();\n    a11yPass();\n",
    "    try{ applyDisplay(); applyAccount(); omegaPersoRender(); } finally { a11yPass(); }\n")
rep("  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(init, 400); });\n  else setTimeout(init, 400);\n})();",
    "  window.__omegaA11yRun = a11yPass;   // v6.5.66: the self-check runs it if it has not run yet (a busy phone can delay setup)\n"
    "  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(init, 400); });\n  else setTimeout(init, 400);\n})();")
rep("      if(!a) return WARN('a11y pass has not run yet (init timing) — will run within 1s of load');",
    "      if(!a && typeof window.__omegaA11yRun === 'function'){ try{ window.__omegaA11yRun(); }catch(e){} a = window.__omegaA11y; }\n"
    "      if(!a) return WARN('a11y pass has not run yet (init timing) — will run within 1s of load');")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.65 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.65 ' + sep + ' build ' + old + ' UTC', 'v6.5.66 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.66 · build' in s and 'v6.5.65 · build' not in s and s.count('one file on its own, v6.5.66') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
