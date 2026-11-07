"""(5 Nov 2026) UX layer for OMEGA Prime: turns the tickets build (made by patch_prime_panic.py) into the UX build.
Display only: no rule, threshold, ticket or trade changes (the climax, panic-bounce and ticket script blocks stay byte-identical;
the script asserts it). Changes:
  - Today: "Your orders" directly under the verdict (the market dial and the five coins move below the tickets);
    an honest verdict when the scans could not reach the market ("No market data", not "Stand aside"), "Checking the market…"
    before the first scan; the "data live" chip only when a feed was really read; when the signals were last checked;
    a Grade C plan drawn as a paper card with "Not an order" (tickets come only from tested rules).
  - Signals: the rule book (every rule by grade, its live state), including the rules the research adds to edges/approved.json.
  - Evidence: the ledger grouped as passed, being measured, failed, with counts; rules from edges/approved.json listed.
  - Every page has its own address (#today, #signals, ...) so Android's back button returns to the previous page.
  - Readability: gold text darkened to pass WCAG AA (4.13 -> 5.46:1), dial labels 3.6 -> 5.6:1, tap targets >= 44 px,
    small print 12.5 -> 13 px.
Usage:
  python3 patch_prime_ux.py tickets.html out.html [edges/approved.json]   full UX patch
  python3 patch_prime_ux.py ux.html out.html edges/approved.json          on a UX build: refresh only the embedded rule list
Full chain: omega-prime-base-25oct.html -> patch_prime_panic.py -> patch_prime_ux.py -> omega-prime.html"""
import sys, json, re, os, datetime
src, dst = sys.argv[1], sys.argv[2]
edges_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'edges', 'approved.json')
here = os.path.dirname(os.path.abspath(__file__))
h = open(src, encoding='utf-8').read()

def edges_block():
    rows = []
    if os.path.exists(edges_path):
        raw = json.load(open(edges_path, encoding='utf-8'))
        raw = raw.get('rules', raw.get('approved', [])) if isinstance(raw, dict) else raw
        keep = ('id', 'name', 'grade', 'plan', 'tf', 'status', 'max_leverage', 'margin_usdt', 'evidence')
        for r in raw if isinstance(raw, list) else []:
            if isinstance(r, dict) and r.get('id') and str(r.get('grade', '')).upper() in ('A', 'B', 'C'):
                x = {k: r[k] for k in keep if k in r and isinstance(r[k], (str, int, float))}; x['grade'] = str(r['grade']).upper(); rows.append(x)
    at = datetime.date.today().isoformat() if rows else ''
    js = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
    return ('<script>/* ═══ PRIME EDGES — rules that passed the research protocol (edges/approved.json), embedded at build time ═══ */\n'
            'window.PRIME_EDGES = ' + js + '; window.PRIME_EDGES_AT = ' + json.dumps(at) + ';\n</script>'), len(rows)

EB = re.compile(r'<script>/\* ═══ PRIME EDGES .*?</script>', re.S)
if 'PRIME UX —' in h:                       # already a UX build: refresh the embedded rule list only
    blk, n = edges_block(); assert len(EB.findall(h)) == 1; h = EB.sub(lambda m: blk, h)
    open(dst, 'w', encoding='utf-8').write(h); print(dst, len(h.encode()), 'bytes · rules embedded:', n); sys.exit(0)

def block(name):
    m = re.search(r'<script>/\* ═══ ' + re.escape(name) + r'.*?</script>', h, re.S); assert m, name; return m.group(0)
frozen = {n: block(n) for n in ('PRIME CLIMAX WATCH', 'PRIME PANIC-BOUNCE WATCH', 'PRIME TRADE TICKETS', 'PRIME AUTOPILOT')}

R = [
 # shell: orders under the verdict, the rule book on Signals
 ('<div id="todayBody"></div><div id="ticketsBody"></div><div id="evBody"></div>', '<div id="todayBody"></div><div id="ordersNote"></div><div id="ticketsBody"></div><div id="todayMore"></div><div id="evBody"></div>'),
 ('<div id="climaxBody"></div><div id="panicBody"></div><div id="dplanBody"></div>', '<div id="rulebookBody"></div><div id="climaxBody"></div><div id="panicBody"></div><div id="dplanBody"></div>'),
 # contrast and tap targets
 ('--gold:#a8701a;', '--gold:#8f5e12;'),
 ('input,select{font:inherit;}', 'input,select{font:inherit;}\n'
  '/* UX 5 Nov 2026: tap targets >= 44 px, readable small print, grade C as paper, no-data verdict, grouped ledger */\n'
  'main .btn,main .btn-outline,#ticketsBody .tk-btn{min-height:44px;} #ticketsBody .tk-btn{padding:10px 16px;font-size:14px;margin:2px 6px 2px 0;}\n'
  'main .mr-tabs button{min-height:44px;min-width:44px;} #ticketsBody input{min-height:44px;} main .sw{min-height:44px;} main .sw input{width:24px;height:24px;}\n'
  'main .hint{font-size:13px;} .bar button{font-size:12px;min-height:56px;} .tag{font-size:12px;}\n'
  '.verdict.gc{background:var(--panel);color:var(--ink);border:2px dashed var(--ink);box-shadow:none;} .verdict.gc .v{font-size:25px;color:var(--ink);} .verdict.gc.short .v{color:var(--bear);} .verdict.gc.long .v{color:var(--bull);} .verdict.gc .chips span{border-color:var(--border);}\n'
  '.gc-note{margin-top:8px;font:600 13.5px system-ui;color:var(--bear);}\n'
  '.verdict.nodata{background:repeating-linear-gradient(135deg,#283043 0 14px,#1c2230 14px 28px);} .verdict.nodata .v{color:#e4dfd2;}\n'
  '.lg-sum{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 6px;} .lg-sum button{min-height:44px;border:1px solid var(--border);background:var(--paper);border-radius:999px;padding:6px 14px;font:600 13px system-ui;color:var(--ink);cursor:pointer;}\n'
  '.lg-h{font:700 12.5px system-ui;letter-spacing:.08em;text-transform:uppercase;margin:16px 0 2px;color:var(--text-dim);}'),
 # the dial's labels: anchored away from the arc (the selected segment's thick stroke hid "Depressed"/"Booming"), in a wider frame
 ("'<text x=\"' + (cx + (r + 22)*Math.cos(am)).toFixed(1) + '\" y=\"' + (cy - (r + 22)*Math.sin(am) + 4).toFixed(1) + '\" text-anchor=\"middle\" style=\"font:600 11px system-ui;fill:'",
  "'<text x=\"' + (cx + (r + 16)*Math.cos(am)).toFixed(1) + '\" y=\"' + (cy - (r + 16)*Math.sin(am) + 4).toFixed(1) + '\" text-anchor=\"' + (Math.cos(am) < -0.3 ? 'end' : Math.cos(am) > 0.3 ? 'start' : 'middle') + '\" style=\"font:600 12px system-ui;fill:'"),
 ('.dial{width:100%;max-width:340px;', '.dial{width:100%;max-width:420px;'),
 ('<svg class="dial" viewBox="0 0 340 176"', '<svg class="dial" viewBox="-44 0 428 176"'),
 # the dial's labels: #8a8577 (3.6:1) -> #6a675c (5.6:1)
 (": '#8a8577') + '\">' + lab[k]", ": '#6a675c') + '\">' + lab[k]"),
 # verdict: honest when there is no data; the scan not yet run
 ("    return { cls:'wait', k:'Today', v:'Stand aside'",
  "    if(ctx.noData) return { cls:'wait nodata', k:'No market data', v:'Cannot check today', w:'Prime could not reach Binance on its last scans, so it does not know whether a tested rule fired. This is not a stand-aside: it is unknown. Check the connection (Binance refuses some networks), then reopen. Do not trade from this screen until the data returns.' };\n"
  "    if(ctx.unchecked) return { cls:'wait', k:'Today', v:'Checking the market…', w:'The first scan of the 40 most-traded coins starts a few seconds after opening; the verdict follows it.' };\n"
  "    return { cls:'wait', k:'Today', v:'Stand aside'"),
 ("return { cls:p.side, k:'Grade C plan", "return { cls:p.side + ' gc', k:'Grade C plan"),
 ("panicLive:PB, plans:plans, limits:L })", "panicLive:PB, plans:plans, limits:L, noData:window.PRIME_UX ? window.PRIME_UX.noData() : false, unchecked:window.PRIME_UX ? window.PRIME_UX.unchecked() : false })"),
 ("esc(V.w) + '</div><div class=\"chips\">", "esc(V.w) + '</div>' + (/ gc/.test(V.cls) ? '<div class=\"gc-note\">Not an order. Prime writes tickets only for rules that passed a fair test; this plan is followed on paper.</div>' : '') + '<div class=\"chips\">"),
 ("' data problem(s)' : 'data live') + '</span>' : '')", "' data problem(s)' : (T.reads && T.reads.length ? 'data live' : 'data not read')) + '</span>' : '') + (window.PRIME_UX ? '<span>' + window.PRIME_UX.checked() + '</span>' : '')"),
 # Today: the verdict, then the orders, then the market
 ("h += '<div class=\"grid2\"><div class=\"card\"><h3 class=\"dp-h\">The market</h3>'", "h += '<!--more--><div class=\"grid2\"><div class=\"card\"><h3 class=\"dp-h\">The market</h3>'"),
 ("  // ── navigation ──\n", "  // ── navigation ──\n  function paintToday(){ var s = today().split('<!--more-->'), m = el('todayMore'); el('todayBody').innerHTML = s[0]; if(el('ordersNote')) el('ordersNote').innerHTML = window.PRIME_UX ? window.PRIME_UX.ordersNote() : ''; if(m) m.innerHTML = s[1] || ''; else el('todayBody').innerHTML += (s[1] || ''); }\n"
  "  function pushPage(p){ try{ if(location.hash === '#' + p) return; if(!history.state) history.replaceState({ p:p }, '', '#' + p); else history.pushState({ p:p }, '', '#' + p); }catch(e){} }\n"),
 ("function show(p){ cur = p;", "function show(p, noPush){ cur = p;"),
 ("window.scrollTo(0, 0); }", "window.scrollTo(0, 0); if(!noPush) pushPage(p); }"),
 ("if(window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); }", "if(window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); if(window.PRIME_UX) window.PRIME_UX.renderRulebook(); }"),
 ("el('evidenceBody').innerHTML = evidence();", "el('evidenceBody').innerHTML = evidence() + (window.PRIME_UX ? window.PRIME_UX.evidenceExtras() : '');"),
 ("renderSettings(); if(cur === 'today') el('todayBody').innerHTML = today(); }", "renderSettings(); if(cur === 'today') paintToday(); if(cur === 'signals' && window.PRIME_UX) window.PRIME_UX.renderRulebook(); }"),
 # Evidence: passed, being measured, failed — each with a count and a jump button
 ("<ul class=\"ledger\" style=\"list-style:none;padding:0\">' + LEDGER.map(function(r){",
  "' + '<div class=\"lg-sum\">' + ['pass', 'run', 'fail'].map(function(g){ return '<button type=\"button\" onclick=\"document.getElementById(\\'lg-' + g + '\\').scrollIntoView({behavior:\\'smooth\\'})\">' + LEDGER.filter(function(r){ return r[0] === g; }).length + ' ' + { pass:'passed', run:'being measured', fail:'failed' }[g] + '</button>'; }).join('') + '</div>' + "
  "['pass', 'run', 'fail'].map(function(g){ return '<h4 class=\"lg-h\" id=\"lg-' + g + '\">' + { pass:'Passed a fair test', run:'Being measured', fail:'Failed (kept on record)' }[g] + '</h4><ul class=\"ledger\" style=\"list-style:none;padding:0\">' + LEDGER.filter(function(r){ return r[0] === g; }).map(function(r){"),
 ("</li>'; }).join('') + '</ul>' +\n      '<p class=\"dp-p\"><b>Being measured", "</li>'; }).join('') + '</ul>'; }).join('') +\n      '<p class=\"dp-p\"><b>Being measured"),
]
for a, b in R:
    n = h.count(a); assert n >= 1, ('missing', a[:80])
    assert n == 1, ('not unique', a[:80], n); h = h.replace(a, b)
assert h.count("el('todayBody').innerHTML = today()") == 2; h = h.replace("el('todayBody').innerHTML = today()", 'paintToday()')
# the UX module and the embedded rule list go after the ticket module
tk = frozen['PRIME TRADE TICKETS']; blk, n = edges_block(); ux = open(os.path.join(here, 'prime_ux.js'), encoding='utf-8').read().strip()
assert h.count(tk) == 1; h = h.replace(tk, tk + '\n' + blk + '\n' + ux)
for k, v in frozen.items(): assert block(k) == v, 'trading block changed: ' + k
open(dst, 'w', encoding='utf-8').write(h); print(dst, len(h.encode()), 'bytes · trading blocks byte-identical · rules embedded:', n)
