"""v6.5.68: a download of every Binance coin no research round has used (daily, for round 12's final test) and the
harvest card's order list for the week (open / close / keep, with amounts; placed by you, never by OMEGA)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def swap(start, new):
    global s
    assert s.count(start) == 1, start
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
swap('<script>/* ═══ FUNDING HARVEST (v6.5.59', open('harvest.js', encoding='utf-8').read())
i = s.index('<script>/* ═══ FUTURES DATA FOR RESEARCH, THE REST IN ONE RUN'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('untouchedexport.js', encoding='utf-8').read().rstrip('\n') + s[j:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.67 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.67 ' + sep + ' build ' + old + ' UTC', 'v6.5.68 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.68 · build' in s and 'v6.5.67 · build' not in s and s.count('UNTOUCHED COINS FOR THE FINAL TEST (v6.5.68)') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
