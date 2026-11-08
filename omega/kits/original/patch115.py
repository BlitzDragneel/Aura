"""v6.5.115: the declutter of v6.5.114 on every other kept page, and badges that no longer wrap badly on phones.
Layout only; every card, number and control is still in the app; CREED's engine is byte-identical.
 1. Risk Guard, Market Read, Market Intelligence, Live Market Data, CREED Scanner, Journal, Positioning Desk, Futures,
    Growth & Routine, Brain, Autopilot and Settings each get one "About this page" dropdown (closed) holding the page's
    long introduction. Primary information stays open: the Risk Guard and Market Read cards, the market lists, the
    clock, the Futures leverage warning, the paper accounts, the Brain's reasoning and dashboard, the Autopilot deck.
    Secondary detail becomes closed dropdowns: Intelligence (moving together, positioning, patterns, activity, markets
    to watch), Live data (the live-data test, data sources), Scanner (alerts, learning, what OMEGA is missing, markets to
    watch), Brain (You x OMEGA, Claude council, evidence ledger), Autopilot (what OMEGA was taught, revalidation, log,
    market regimes), Growth (daily routine), Settings (signal webhooks and alerts, moved below the preferences).
    Duplicate headers go (Journal, Growth and Settings keep one title; their subtitles move to About).
 2. Phones: the status line's "TD 1/800", clock session chips, pills and grade tags stay on one line; long evidence chips
    (es-chip) become tidy rounded blocks instead of breaking mid-pill; in Heaven they use the text font.
 3. Install OMEGA on phone and computer: on http(s) the real manifest.json next to the app (icons, start_url; served by the
    board site with service-worker.js) replaces the icon-less inline manifest when it answers (fetch, no-store); the inline one
    stays on file:// or when the file is missing (CREED's start-up code that writes it stays byte-identical, so this runs
    after it). "Install OMEGA" in Settings and More: the browser's install prompt where offered (beforeinstallprompt),
    otherwise instructions for Android Chrome, iPhone Safari and Chrome/Edge on Windows/Mac. The browser bar colour follows
    the theme (#F7F8FC in Heaven, light for Light/Paper, dark for dark themes).
usage: python3 patch115.py <v6.5.114> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()

TAG = re.compile(r'<(/?)(div|section|details|p|aside|main|nav|header|ul|ol|table)\b[^>]*?>', re.I)


def elem_end(i):
    """end index of the balanced element that starts at s[i]"""
    d = 0
    for m in TAG.finditer(s, i):
        d += -1 if m.group(1) else 1
        if d == 0:
            return m.end()
    raise AssertionError('unbalanced at %d' % i)


def page_range(p):
    a = s.index('<div id="page-%s" class="page' % p)
    b = elem_end(a)
    return a, b


def start_of(p, text, opener):
    """start of the nearest opening tag `opener` before `text`, inside page p"""
    a, b = page_range(p)
    k = s.index(text, a); assert k < b and s.count(text, a, b) == 1, (p, text)
    j = s.rindex(opener, a, k); return j


def fold(p, text, label, opener='<section class="lower-grid"', open_=False):
    global s
    j = start_of(p, text, opener); e = elem_end(j)
    s = s[:j] + '<details class="hv-fold hv-box hv-sec"' + (' open' if open_ else '') + '><summary class="hv-sum">' + label + '</summary>' + s[j:e] + '</details>' + s[e:]


def cut(p, text, opener):
    global s
    j = start_of(p, text, opener); e = elem_end(j); blk = s[j:e]; s = s[:j] + s[e:]; return blk


def about(p, body):
    global s
    a, b = page_range(p); assert s.count('class="om-about"', a, b) == 0, p
    e = s.rindex('</div>', a, b)
    s = s[:e] + '\n      <details class="om-about"><summary>About this page</summary><div class="om-about-body">\n' + body.strip() + '\n      </div></details>\n    ' + s[e:]


def sub(p):   # the banner subtitle as plain text
    a, b = page_range(p); m = re.search(r'creed-banner-title">(.*?)</h2>', s[a:b], re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).replace('— ', '').strip() if m else ''


# ── Market Intelligence ──
intro = cut('intel', 'OMEGA Intelligence is a separate product from CREE', '<p class="hint"')
for t, l in [('How markets are moving together', 'How markets are moving together'), ('Positioning — funding, open interest, liquidations', 'Positioning: funding, open interest, liquidations'),
             ('Patterns — what is happening, and what followed before', 'Patterns: what is happening, and what followed before'), ('>Activity<', 'Activity'), ('>Markets to watch<', 'Markets to watch')]:
    fold('intel', t, l)
about('intel', '<p>' + sub('intel').capitalize() + '.</p>\n' + intro)

# ── Live Market Data ──
for t, l in [('Does any of it predict anything?', 'Does any of it predict anything? The live-data test'), ('>Data sources<', 'Data sources')]:
    fold('flow', t, l)
about('flow', '<p>' + sub('flow').capitalize() + '. Each reading is stored and later checked against what price did next; the live-data test below says whether any of it has predicted anything yet.</p>')

# ── CREED Scanner ──
intro = cut('radar', 'This is part of CREED.', '<p class="hint"')
for t, l in [('Alerts this session', 'Alerts this session'), ('What the radar is learning', 'What the radar is learning'), ('What OMEGA says it is missing', 'What OMEGA says it is missing'), ('>Markets to watch<', 'Markets to watch')]:
    fold('radar', t, l)
about('radar', intro)

# ── Brain ──
a, b = page_range('brain'); k = s.index('<p class="hint"', a); assert k < s.index('class="jv-2"', a)
e = elem_end(k); intro = s[k:e]; s = s[:k] + s[e:]
for t, l in [('<h3>You × OMEGA', 'You × OMEGA: does your judgement add value?'), ('<h3>Claude council', 'Claude council: analyst, adversary, audited by code'), ('<h3>Evidence ledger', 'Evidence ledger: every conclusion, auditable')]:
    fold('brain', t, l, opener='<section class="bd-card')
about('brain', intro)

# ── Autopilot ──
intro = cut('auto', 'Part of OMEGA Intelligence, independent of CREED.', '<p class="hint"')
for t, l in [('Revalidation &mdash; conditions suspended by live results', 'Revalidation: conditions suspended by live results'), ('What OMEGA was taught &mdash; and whether it held up', 'What OMEGA was taught, and whether it held up'), ('Autopilot log</h2>', 'Autopilot log')]:
    fold('auto', t, l)
fold('auto', 'id="rgPanel"', 'Market regimes now', opener='<section class="bd-card rg-card"')
about('auto', '<p>' + sub('auto').capitalize() + '.</p>\n' + intro)

# ── Growth & Routine, Journal, Settings: one title, subtitle to About ──
def strip_sub(p):
    global s
    a, b = page_range(p); m = re.search(r'\n\s*<p class="page-sub">(.*?)</p>', s[a:b], re.S); assert m, p
    s = s[:a] + s[a:b].replace(m.group(0), '', 1) + s[b:]; return m.group(1)
g = strip_sub('growth'); fold('growth', 'id="routineMerged"', 'Daily routine: a simple order for a disciplined session')
about('growth', '<p>' + g + '</p><p>Your edge, growth projection, risk of ruin and discipline score unlock after 5 logged trades.</p>')
about('journal', '<p>' + strip_sub('journal') + '</p>')
st = strip_sub('settings')
alerts = cut('settings', '📡 Signal Webhooks &amp; Alerts', '<div class="card"')
a, b = page_range('settings'); e = elem_end(s.index('<div class="settings-page-body"', a))
s = s[:e] + '\n      <details class="hv-fold hv-box hv-sec"><summary class="hv-sum">Signal webhooks and alerts</summary>' + alerts + '</details>' + s[e:]
about('settings', '<p>' + st + ' Keys and the Live API token stay on this device and never go into a backup.</p>')

# ── pages whose content is one module: About only ──
about('rguard', '<p>' + sub('rguard').capitalize() + '. The rules: 0.5% of the account a trade, at most 2 open, stop after &minus;2% in a day or &minus;5% in a week. The Growth Bot follows them on paper from 100 USDT; &ldquo;Before a real trade&rdquo; checks a trade against them; the monthly review shows how they held.</p>')
about('mread', '<p>' + sub('mread').capitalize() + '. Today&rsquo;s plan is grade C: a written plan followed on paper, not a tested edge. Liquidity marks show where stops and resting orders sit; place a stop beyond the obvious level, not on it.</p>')
about('posdesk', '<p>' + sub('posdesk').capitalize() + '. Funding, open interest, long/short ratios and liquidations, with what seven years of data say about them. Measured: crowd positioning did not predict direction (E30); it describes risk, not a signal.</p>')
about('futures', '<p>' + sub('futures').capitalize() + '. The paper account replays OMEGA&rsquo;s own trades at your margin and leverage, with fees and funding. The leverage warning above stays: in the tests 2&times; already liquidated and 40&times; liquidated about 60% of trades.</p>')


# ── 3. Install OMEGA (phone and computer) ──
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


# browser bar colour: light themes light, dark themes dark
rep("mt.setAttribute('content', t === 'heaven' ? '#F6F8FC' : '#0A0D12');",
    "mt.setAttribute('content', t === 'heaven' ? '#F7F8FC' : t === 'light' ? '#F4F6FA' : t === 'paper' ? '#EDE8DC' : '#0A0D12');")
rep('<meta name="theme-color" content="#0A0D12">', '<meta name="theme-color" content="#F7F8FC">')
rep("onclick=\"navigate('about')\">About OMEGA — how everything works</button></p>\n",
    "onclick=\"navigate('about')\">About OMEGA — how everything works</button>\n"
    "            <button class=\"btn-ghost\" type=\"button\" id=\"setInstallBtn\" onclick=\"OMEGA_INSTALL.open()\">Install OMEGA on this device</button></p>\n"
    "          <div id=\"installBox\" class=\"om-card\" style=\"display:none;margin:12px 0 0;\"></div>\n")
rep("<span class=\"sb-icon\">ⓘ</span> About OMEGA</li>\n",
    "<span class=\"sb-icon\">ⓘ</span> About OMEGA</li>\n      <li id=\"sbInstall\" onclick=\"OMEGA_INSTALL.open()\"><span class=\"sb-icon\">⤓</span> Install OMEGA</li>\n")
IJS = r"""<script>/* ═══ INSTALL OMEGA (v6.5.115) ═══
   The board site serves a real manifest.json (icons, start_url) and service-worker.js next to this file. CREED's start-up
   code swaps the manifest link for an inline blob without icons; that module stays byte-identical, so instead, on http(s),
   this puts the real file back when manifest.json answers (fetch, cache no-store). The blob stays only on file:// or when
   the file is missing. "Install OMEGA" (Settings and More) uses the browser's install prompt where offered, otherwise
   short instructions per device. */
(function(){
  'use strict';
  var deferred = null, installed = false, real = null;
  function el(id){ return document.getElementById(id); }
  function web(){ return /^https?:$/.test(location.protocol); }
  function standalone(){ try{ return installed || window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true; }catch(e){ return installed; } }
  window.addEventListener('beforeinstallprompt', function(e){ e.preventDefault(); deferred = e; draw(); });
  window.addEventListener('appinstalled', function(){ installed = true; deferred = null; draw(); });
  async function realManifest(){ if(!web()) return false;
    try{ var r = await fetch('manifest.json', { cache:'no-store' }); if(!r.ok) throw new Error('HTTP ' + r.status); await r.json(); real = true;
      var link = document.querySelector('link[rel="manifest"]'); if(!link){ link = document.createElement('link'); link.rel = 'manifest'; document.head.appendChild(link); }
      if(!/manifest\.json(\?|$)/.test(link.getAttribute('href') || '')){ var old = link.href; link.setAttribute('href', 'manifest.json'); if(/^blob:/.test(old)) try{ URL.revokeObjectURL(old); }catch(e){} }
      return true; }catch(e){ real = false; return false; } }
  function draw(){ var b = el('installBox'); if(!b || b.style.display === 'none') return;
    var h = '<div class="om-ch"><h3>Install OMEGA</h3>' + (standalone() ? '<span class="om-tag live">Installed</span>' : '') + '</div>';
    if(standalone()) h += '<p class="om-meta" style="margin:0">OMEGA is running as an installed app on this device.</p>';
    else {
      if(deferred) h += '<p class="om-meta" style="margin:0 0 10px">This browser can install OMEGA as an app: its own icon and window, and it opens offline.</p><div class="journal-actions"><button class="btn-primary" type="button" id="installNow">Install now</button></div>';
      if(!web()) h += '<p class="om-meta" style="margin:0 0 10px">This copy was opened from a file. Open OMEGA from its web address (https) to install it.</p>';
      h += '<ul class="om-meta" id="installHow" style="margin:10px 0 0;padding-left:18px;line-height:1.7"><li><b>Android, Chrome:</b> menu &#8942; &rarr; <b>Install app</b>.</li>' +
        '<li><b>iPhone or iPad, Safari:</b> Share &rarr; <b>Add to Home Screen</b>.</li><li><b>Windows or Mac, Chrome or Edge:</b> the install icon in the address bar.</li></ul>'; }
    b.innerHTML = h; var n = el('installNow');
    if(n) n.onclick = async function(){ var d = deferred; if(!d) return; deferred = null; try{ d.prompt(); var c = await d.userChoice; if(c && c.outcome === 'accepted') installed = true; }catch(e){} draw(); }; }
  function open(){ if(window.navigate) window.navigate('settings'); var b = el('installBox'); if(!b) return; b.style.display = '';
    draw(); setTimeout(function(){ try{ b.scrollIntoView({ block:'center' }); }catch(e){} }, 80); }
  function boot(){ realManifest(); window.addEventListener('load', function(){ setTimeout(realManifest, 400); }); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  window.OMEGA_INSTALL = { open:open, draw:draw, realManifest:realManifest, state:function(){ return { prompt:!!deferred, installed:standalone(), real:real, web:web() }; } };
})();
</script>
"""
s = s.replace('</body>', IJS + '</body>', 1)

CSS = r'''<style id="tidy115Css">/* v6.5.115: folded sections everywhere; badges that keep their shape on phones */
.hv-sec{margin:0 0 14px}.hv-sec .lower-grid,.hv-sec>.bd-card,.hv-sec>.card{margin:10px 0 0!important}
.hv-sec .lower-grid>.card,.hv-sec>.bd-card,.hv-sec>.card{border:0!important;box-shadow:none!important;padding:0!important;background:none!important}
.hv-sec .lower-grid>.card>h2:first-child,.hv-sec>.bd-card>h3:first-child,.hv-sec>.card>h2:first-child{display:none}
.hv-sec .rg-card #rgPanel{margin-top:0}.hv-sec .page-header{display:none}
.ost-td{white-space:nowrap;flex:none}.ost-need,.omega-clock .ck-sess,.rd-pill,.tb-grade,.tb-warn,.om-tag,.ac-chip,.pt-badge{white-space:nowrap}
.es-chip{display:inline-block;max-width:100%;box-sizing:border-box;line-height:1.45;border-radius:12px;white-space:normal;vertical-align:middle}
html[data-theme="heaven"] .es-chip{font-family:'Inter',system-ui,sans-serif;font-size:12px;font-weight:600;letter-spacing:.01em;padding:4px 10px}
html[data-theme="heaven"] .ost-td{font-size:11px}
@media (max-width:520px){.omega-clock{row-gap:4px}.ost-main{font-size:12px}}
</style>
'''
s = s.replace('</body>', CSS + '</body>', 1)

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.114 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.114 ' + sep + ' build ' + o + ' UTC', 'v6.5.115 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.115 · build' in s and 'v6.5.114 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'size', len(s.encode('utf-8')))
