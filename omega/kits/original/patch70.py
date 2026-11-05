"""v6.5.70: the Edge Lab. OMEGA looks for edges by itself on ground research has not tested: built-in knowledge of every
rule already tested (never re-tested), a wide daily store of 291 coins filled from the phone, the round-12 engine with 38
base rules (reproducing the research code), an explorer of untested rule × condition × exit combinations and new families,
a shadow book tracked forward, and promotion to EDGE only on forward weeks. PLAN13."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
final3 = json.load(open('final3_list.json'))
wide = open('widestore.js', encoding='utf-8').read().replace('__FINAL3__', json.dumps(final3))
lib = open('edgelib.js', encoding='utf-8').read()
lab = open('edgelab.js', encoding='utf-8').read().replace('__KNOWLEDGE__', open('knowledge.min.json', encoding='utf-8').read().strip())
assert '__FINAL3__' not in wide and '__KNOWLEDGE__' not in lab
rep('</body>', wide.rstrip('\n') + '\n' + lib.rstrip('\n') + '\n' + lab.rstrip('\n') + '\n</body>')
rep("""      <li data-page="posdesk" onclick="navigate('posdesk')"><span class="sb-icon">⇅</span> Positioning Desk</li>\n""",
    """      <li data-page="posdesk" onclick="navigate('posdesk')"><span class="sb-icon">⇅</span> Positioning Desk</li>\n      <li data-page="edgelab" onclick="navigate('edgelab')"><span class="sb-icon">✦</span> Edge Lab</li>\n""")
page = """    <div id="page-edgelab" class="page">
      <div class="creed-banner intel-banner">
        <div class="creed-banner-glow"></div>
        <div class="creed-banner-main">
          <div class="creed-banner-kicker">Ω EDGE LAB · PAPER ONLY</div>
          <h2 class="creed-banner-title">Edge Lab <span>— OMEGA looks for what research has not tested</span></h2>
          <div class="creed-banner-flow"><i>Built-in knowledge</i><b>→</b><i>Untested candidates</i><b>→</b><i>Half A, then half B</i><b>→</b><i>Forward weeks</i><b>→</b><i>EDGE</i></div>
        </div>
      </div>
      <div id="edgelabBody"><p class="hint">Loading…</p></div>
    </div>
"""
rep('    <div id="page-ostrat" class="page">\n', page + '    <div id="page-ostrat" class="page">\n')
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','posdesk','ostrat',", "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','posdesk','edgelab','ostrat',")
rep("positioning: safe(function(){ return window.OMEGA_POSDESK ? window.OMEGA_POSDESK.report() : null; }) || null,",
    "positioning: safe(function(){ return window.OMEGA_POSDESK ? window.OMEGA_POSDESK.report() : null; }) || null, edgeLab: safe(function(){ return window.OMEGA_EDGELAB ? window.OMEGA_EDGELAB.report() : null; }) || null,")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.69 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.69 ' + sep + ' build ' + old + ' UTC', 'v6.5.70 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.70 · build' in s and 'v6.5.69 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now, 'size', len(s))
