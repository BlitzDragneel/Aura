"""v6.5.95: the Analysis scanner shows markets with a reading first and folds the unread ones into one compact card of names,
instead of up to 60 empty cards. Cards with data are unchanged."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
rep("if(g) g.innerHTML = shown.length ? shown.map(card).join('') : '<p class=\"hint\">Nothing matches this filter.</p>';",
    "if(g){ var withData = shown.filter(function(x){ return results[x]; }), none = shown.filter(function(x){ return !results[x]; });   // v6.5.95: unread markets folded into one card\n"
    "      g.innerHTML = shown.length ? withData.map(card).join('') + (none.length ? '<div class=\"wl-card dim wl-unread\"><div class=\"wl-top\"><b>' + none.length + ' ' + (scanning ? 'waiting their turn' : 'not read yet') + '</b><span class=\"wl-v\">' + (scanning ? 'scanning…' : 'Scan now, or the Autopilot reads them') + '</span></div><p style=\"display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 0;\">' + none.map(function(x){ return '<span style=\"font-size:11px;padding:2px 7px;border:1px solid var(--border);border-radius:999px;color:var(--text-dim);\">' + esc(x) + '</span>'; }).join('') + '</p></div>' : '') : '<p class=\"hint\">Nothing matches this filter.</p>'; }")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.94 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.94 ' + sep + ' build ' + old + ' UTC', 'v6.5.95 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.95 · build' in s and 'wl-unread' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
