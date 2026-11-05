"""v6.5.82: audit and trim. Removes what is finished or failed (the capitulation watch; the research downloads whose data
has been collected and used; the failed carry card and its Autopilot job), corrects statements the later rounds made out of
date, puts the climax reversal's signals on the OMEGA Signals page, and fixes the knowledge's early round labels.
Code of everything removed stays in the build kit."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)
def drop(marker):
    global s
    i = s.index('<script>/* ═══ ' + marker); j = s.index('</script>', i) + len('</script>')
    while j < len(s) and s[j] == '\n': j += 1
    s = s[:i] + s[j:]
# 1. finished or failed modules
for m in ('CAPITULATION WATCH', 'FUTURES DATA FOR RESEARCH, THE REST IN ONE RUN', 'ROUND 14 FINAL TEST DATA', 'CREED RESEARCH DATA', 'BYBIT FUNDING FOR RESEARCH', 'UNTOUCHED COINS FOR THE FINAL TEST', 'FOREX HISTORY FOR RESEARCH'):
    drop(m)
# 2. the older research downloads keep their coin lists (other modules read them) but no longer add buttons
rep("  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 30) clearInterval(iv); }, 1000);\n  window.OMEGA_LONGEXPORT",
    "  /* v6.5.82: the download button is retired (data collected; round 5 used it) */\n  window.OMEGA_LONGEXPORT")
for nm in ('OMEGA_FRESHEXPORT', 'OMEGA_FRESH2EXPORT'):
    rep("  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 40) clearInterval(iv); }, 1000);\n  window." + nm,
        "  /* v6.5.82: the download button is retired (data collected and used); the coin list stays for the stores that read it */\n  window." + nm)
# 3. the failed carry rule: no card, no Autopilot job (its data helpers stay: the harvest and others use them)
rep("function render(){ var host = el('carryxsCard'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'carryxsCard'; pg.insertBefore(host, pg.firstChild); }",
    "function render(){ var old = el('carryxsCard'); if(old && old.parentNode) old.parentNode.removeChild(old); return; /* v6.5.82: card retired (failed both untouched tests; recorded in the research record) */ var host = el('carryxsCard'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'carryxsCard'; pg.insertBefore(host, pg.firstChild); }")
rep("function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'carryxs'; })) return true;",
    "function register(){ return true; /* v6.5.82: no Autopilot job for a retired rule */ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'carryxs'; })) return true;")
rep('      <div id="carryxsCard"></div>\n', '')
# 4. statements later rounds made out of date
rep("Outside research, ' + esc(REC.date) + ' \\u2014 the funding harvest passed untouched tests three times; in round 12 it passed again only when paired with RSI(5) dip-buying",
    "Research record, rounds 1\\u201318 \\u2014 what passed: the funding harvest (rounds 7, 8 and 10; with dip-buying in round 12) and the climax reversal (round 16). Everything else failed")
rep("Now a frozen paper strategy (the card at the top of this page).'", "It then failed both untouched tests (rounds 5 and 7): not an edge.'")
rep("Funding harvest \\u2014 the one idea that passed untouched tests, three times", "Funding harvest \\u2014 passed untouched tests in rounds 7, 8 and 10")
rep("Funding harvest (harvest-30d, and its 10-coin version from round 8): the one idea that passed untouched tests, three times", "Funding harvest (harvest-30d, and its 10-coin version from round 8): passed untouched tests in rounds 7, 8 and 10")
rep("Only one thing passed an untouched test: being paid for supplying leverage.", "Until round 16 only one thing had passed an untouched test: being paid for supplying leverage. (Round 16\\u2019s climax reversal, buying a flush as buyers step in, was the second.)")
rep("The funding harvest is the only thing that kept working, because it is a payment for a service, not a forecast.", "The funding harvest kept working because it is a payment for a service, not a forecast (round 16 later added one direction rule, the climax reversal).")
rep("There is no OMEGA strategy yet, and that is the honest answer.</b> It is built only from ideas that pass every test below; none has.",
    "The phone\\u2019s own Research Lab has not produced a rule that holds on unseen data, so this panel stays empty.</b> The rules that passed the full research run elsewhere: the funding harvest (above) and the climax reversal (Edge Lab and OMEGA Signals).")
# 5. OMEGA Signals: the climax reversal's signals first
rep('      <p class="hint"><b>Part of OMEGA Intelligence, independent of CREED.</b> A signal appears only when a condition the Research Lab rated',
    '      <div id="climaxSigBody"></div>\n      <p class="hint"><b>Below: the phone Research Lab\'s own signals.</b> <b>Part of OMEGA Intelligence, independent of CREED.</b> A signal appears only when a condition the Research Lab rated')
# 6. updated climax module and knowledge
i = s.index('<script>/* ═══ CLIMAX REVERSAL'); j = s.index('</script>', i) + len('</script>'); s = s[:i] + open('climax.js', encoding='utf-8').read().rstrip('\n') + s[j:]
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.81 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.81 ' + sep + ' build ' + old + ' UTC', 'v6.5.82 ' + sep + ' build ' + now + ' UTC')
for gone in ('window.OMEGA_CAPWATCH =', 'window.OMEGA_FUTEXPORT =', 'window.OMEGA_FINAL4EXPORT =', 'window.OMEGA_CREED15EXPORT =', 'window.OMEGA_BYBITEXPORT =', 'window.OMEGA_FINAL3EXPORT =', 'window.OMEGA_FXEXPORT ='): assert gone not in s, gone
assert 'v6.5.82 · build' in s and 'climaxSigBody' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now, '| size', len(s), 'chars')
