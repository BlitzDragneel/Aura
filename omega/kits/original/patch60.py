"""v6.5.60: the BTC trend benchmark (another assistant's frozen 'BTC 14-day momentum + 18% volatility target'), run exactly as
written plus funding, judged forward only; the desk links to it. Nothing else changes."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
def swap(start, new):
    global s
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
swap('<script>/* ═══ POSITIONING DESK (v6.5.58', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
rep('</body>', open('btctrend.js', encoding='utf-8').read() + '\n</body>')
rep('      <div id="harvestCard"></div>\n', '      <div id="harvestCard"></div>\n      <div id="btctrendCard"></div>\n')
rep("'carryxs','harvest',", "'carryxs','harvest','btctrend',")
rep("omega_harvest_v1:1,", "omega_harvest_v1:1, omega_btctrend_v1:1,")
rep("harvestRule: safe(function(){ return window.OMEGA_HARVEST ? window.OMEGA_HARVEST.report() : null; }) || null,",
    "harvestRule: safe(function(){ return window.OMEGA_HARVEST ? window.OMEGA_HARVEST.report() : null; }) || null, btcTrend: safe(function(){ return window.OMEGA_BTCTREND ? window.OMEGA_BTCTREND.report() : null; }) || null,")
rep("trend (+39%, z 1.58, \\u221265%) failed.' } ];", "trend (+39%, z 1.58, \\u221265%) failed. Later, another assistant\\u2019s BTC rule (14-day trend + 18% volatility target) on every fresh coin: +14% a year, z 1.60 against 2.33, failed; it runs as a forward benchmark only.' } ];")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.59 (?:\u00b7|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['\u00b7', '\\u00b7']: s = s.replace('v6.5.59 ' + sep + ' build ' + old + ' UTC', 'v6.5.60 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.60 \u00b7 build' in s and 'v6.5.59 \u00b7 build' not in s and 'v6.5.59 \\u00b7 build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
