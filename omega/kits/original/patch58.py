"""v6.5.58: the Positioning Desk, a new page for the new approach (crowding map, market state against its history, carry at the size
you choose, the fresh-coin test). The carry module shares its loaded data. Nothing trades; CREED unchanged."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
# carry module (now shares its data)
i = s.index('<script>/* ═══ FUNDING CARRY, WEEKLY (v6.5.55'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('carryxs.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# the desk module
desk = open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip())
assert '__STATIC__' not in desk
rep('</body>', desk + '\n</body>')
# sidebar entry and page
rep("""      <li data-page="brain" onclick="navigate('brain')"><span class="sb-icon">✺</span> Brain</li>\n""",
    """      <li data-page="brain" onclick="navigate('brain')"><span class="sb-icon">✺</span> Brain</li>\n      <li class="sb-tier">Positioning — the new approach</li>\n      <li data-page="posdesk" onclick="navigate('posdesk')"><span class="sb-icon">⇅</span> Positioning Desk</li>\n""")
page = """    <div id="page-posdesk" class="page">
      <div class="creed-banner intel-banner">
        <div class="creed-banner-glow"></div>
        <div class="creed-banner-main">
          <div class="creed-banner-kicker">Ω POSITIONING DESK · PAPER ONLY</div>
          <h2 class="creed-banner-title">Positioning Desk <span>— who is crowded, who pays whom, and how hard it can fall</span></h2>
          <div class="creed-banner-flow"><i>Funding</i><b>→</b><i>Crowding map</i><b>→</b><i>Carry at your size</i><b>→</b><i>Judged on unseen data</i></div>
        </div>
      </div>
      <div id="posdeskBody"><p class="hint">Loading…</p></div>
    </div>
"""
rep('    <div id="page-ostrat" class="page">\n', page + '    <div id="page-ostrat" class="page">\n')
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','ostrat',", "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','posdesk','ostrat',")
rep("carryRule: safe(function(){ return window.OMEGA_CARRYXS ? window.OMEGA_CARRYXS.report() : null; }) || null,",
    "carryRule: safe(function(){ return window.OMEGA_CARRYXS ? window.OMEGA_CARRYXS.report() : null; }) || null, positioning: safe(function(){ return window.OMEGA_POSDESK ? window.OMEGA_POSDESK.report() : null; }) || null,")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.57 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.57 ' + sep + ' build ' + old + ' UTC', 'v6.5.58 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.58 · build' in s and 'v6.5.57 · build' not in s and 'v6.5.57 \\u00b7 build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
