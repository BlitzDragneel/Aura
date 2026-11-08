"""v6.5.110: OMEGA Academy page and a first-run tutorial (contract: omega/academy/CONTRACT.md). CREED's engine is byte-identical.
 1. Academy page (bottom bar and menu): module list with progress, lesson reader (safe markdown: everything is HTML-escaped
    first, then a small markdown subset is converted; no raw HTML from content), key points, quizzes with explanations,
    "mark complete", progress in localStorage omega_academy_v1 ({done, quiz, token, last}).
    The catalog comes from {server}/academy/catalog; offline (or before the server answers) the FREE lessons embedded at build
    time are shown. Premium lessons are fetched from {server}/academy/lesson/{id} with the X-Academy-Token header and are
    never embedded. "Unlock the full course" opens pricing.json's checkout_url (https only); while it is empty the button
    says "Coming soon — launch price $49, regular $97". "I have a license key" posts {license_key} to {server}/academy/unlock
    and keeps the returned token.
 2. Settings > Data & Keys: Academy server URL (default https://omega-live-api.onrender.com; https only, or http://localhost
    for testing) and "Open the tutorial".
 3. Tutorial: 6 steps (Home verdict, a chart, mark-up, CREED and OMEGA signals read honestly, Risk Guard and bots, the
    Academy). It is a card at the top of the page (not a blocking overlay), shown once on first run (flag omega_tutorial_v1),
    skippable, re-opened from Settings and from the Academy page; "Show me" opens the page the step is about.
 Re-runnable: the embedded free lessons and pricing live in <script type="application/json" id="omegaAcademyData">.
 Run on a build that already has the Academy and only that block (and the build time) is refreshed:
     python3 patch110.py <v6.5.109 or v6.5.110 build> <out> [course.json] [pricing.json]
 (defaults: ../../academy/course.json and ../../academy/pricing.json next to this kit). Premium lesson bodies are stripped
 here, whatever the course file holds.
"""
import sys, os, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '..', '..', 'academy', 'course.json')
PRICING = sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, '..', '..', 'academy', 'pricing.json')
s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)


# ── the embedded data: outline + FREE lessons only ──
def free_of(mo, le): return bool(le.get('free', mo.get('free', False)))
if os.path.exists(COURSE):
    c = json.load(open(COURSE, encoding='utf-8'))
    mods = []
    for mo in c.get('modules', []):
        les = []
        for le in mo.get('lessons', []):
            it = {k: le.get(k) for k in ('id', 'title', 'minutes')}; it['free'] = free_of(mo, le)
            if it['free']: it.update({k: le.get(k) for k in ('body_md', 'key_points', 'quiz')})
            les.append(it)
        mods.append({'id': mo.get('id'), 'title': mo.get('title'), 'summary': mo.get('summary'), 'free': bool(mo.get('free')), 'lessons': les})
    data = {'title': c.get('title'), 'version': c.get('version'), 'updated': c.get('updated'), 'disclaimer': c.get('disclaimer'), 'modules': mods, 'bundled': True}
else:
    data = {'title': 'OMEGA Academy — Trade with evidence', 'version': '0', 'updated': '', 'bundled': True, 'placeholder': True,
            'disclaimer': 'Education, not financial advice. Trading carries a high risk of losing money; leverage can lose your whole deposit quickly.',
            'modules': [{'id': 'm01', 'title': 'Start here', 'summary': 'The course is being written. Connect to the server (Settings > Data & Keys) to load it.', 'free': True,
                         'lessons': [{'id': 'm01-l01', 'title': 'Welcome', 'minutes': 2, 'free': True,
                                      'body_md': '# Welcome\n\nThe full course text is not bundled in this build yet. When the app can reach the Academy server, the lessons load from there.',
                                      'key_points': ['Risk first.', 'Test an idea before trusting it.'], 'quiz': []}]}]}
pricing = json.load(open(PRICING, encoding='utf-8')) if os.path.exists(PRICING) else {'launch_price': 49, 'regular_price': 97, 'checkout_url': ''}
data['pricing'] = {k: pricing.get(k) for k in ('currency', 'launch_price', 'regular_price', 'label', 'checkout_url')}
for mo in data['modules']:
    for le in mo['lessons']:
        assert le['free'] or 'body_md' not in le, 'premium lesson body would be embedded: ' + str(le.get('id'))
DATA_JS = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
DATA_BLOCK = '<script type="application/json" id="omegaAcademyData">' + DATA_JS + '</script>'
nfree = sum(1 for mo in data['modules'] for le in mo['lessons'] if le['free'])

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
if 'id="omegaAcademyData"' in s:   # refresh only
    m = re.search(r'<script type="application/json" id="omegaAcademyData">.*?</script>', s, re.S); assert m
    s = s.replace(m.group(0), DATA_BLOCK, 1)
    o = re.search(r'v6\.5\.(1\d\d) (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s)
    for sep in ['·', '\\u00b7']: s = s.replace('v6.5.' + o.group(1) + ' ' + sep + ' build ' + o.group(2) + ' UTC', 'v6.5.' + o.group(1) + ' ' + sep + ' build ' + now + ' UTC')
    open(dst, 'w', encoding='utf-8').write(s); print('refreshed academy data in', dst, now, 'free lessons', nfree); sys.exit(0)

# ── page ──
PAGE = '''    <div id="page-academy" class="page">
      <div class="creed-banner intel-banner">
        <div class="creed-banner-glow"></div>
        <div class="creed-banner-main">
          <div class="creed-banner-kicker">★ OMEGA · ACADEMY</div>
          <h2 class="creed-banner-title">Academy <span>— trade with evidence: risk first, then test before you trust</span></h2>
          <div class="creed-banner-flow"><i>Learn</i><b>→</b><i>Check yourself</i><b>→</b><i>Practise on paper</i><b>→</b><i>Test before trusting</i></div>
        </div>
      </div>
      <div id="acadBody"><p class="hint">Loading the course…</p></div>
    </div>
'''
rep('    <div id="page-settings" class="page">', PAGE + '    <div id="page-settings" class="page">')

SETTINGS = '''      <div class="card" id="setAcademyCard" style="margin-bottom:12px;">
        <h2 style="color:var(--gold);">Academy server and tutorial</h2>
        <div class="settings-grid"><div class="field"><label>Academy server (OMEGA Live API)</label>
          <input type="url" id="acadServerInput" placeholder="https://omega-live-api.onrender.com" /></div></div>
        <div class="journal-actions" style="margin-top:8px;"><button class="btn-ghost" type="button" id="acadServerSave">Save server</button>
          <button class="btn-ghost" type="button" id="acadTourOpen">Open the tutorial</button></div>
        <p class="hint" id="acadServerMsg" style="margin-bottom:0;">Lessons, unlocking and premium lessons come from this address. Free lessons are also built into the app for offline reading.</p>
      </div>
'''
rep('    <div class="set-pane" id="setData">\n', '    <div class="set-pane" id="setData">\n' + SETTINGS)

rep("  function syncBottomNav(page){\n", "  function syncBottomNav(page){\n    try{ if(typeof window.__omegaAfterNav === 'function') window.__omegaAfterNav(page); }catch(e){}   // v6.5.110: Academy + tutorial\n")

JS = r'''<script>/* ═══ OMEGA ACADEMY + TUTORIAL (v6.5.110) — contract: omega/academy/CONTRACT.md ═══
   Lessons are text from the course file or the server: every character is HTML-escaped first, then a small markdown
   subset (headings, bold, italic, code, lists, tables, quotes, rules, https links) is turned into tags. Premium lesson
   text only ever arrives from {server}/academy/lesson/{id} with a token; none is built into the app. */
(function(){
  'use strict';
  var KEY = 'omega_academy_v1', SKEY = 'omega_academy_server', TKEY = 'omega_tutorial_v1', DEF = 'https://omega-live-api.onrender.com';
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function lsGet(k, d){ try{ var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function prog(){ var p = lsGet(KEY, null); if(!p || typeof p !== 'object') p = {}; p.done = p.done || {}; p.quiz = p.quiz || {}; return p; }
  function saveProg(p){ lsSet(KEY, p); }
  function okServer(u){ return /^https:\/\/[a-z0-9.-]+(:\d+)?(\/[^\s"'<>]*)?$/i.test(u) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/[^\s"'<>]*)?$/i.test(u); }
  function server(){ var u = ''; try{ u = localStorage.getItem(SKEY) || ''; }catch(e){} u = String(u).trim().replace(/\/+$/, ''); return okServer(u) ? u : DEF; }
  var bundled = null; try{ bundled = JSON.parse(el('omegaAcademyData').textContent); }catch(e){ bundled = { modules:[], pricing:{} }; }
  var st = { cat:bundled, src:'bundled', fetching:false, tried:0, open:null, lesson:null, err:'', msg:'', premium:{}, keyBox:false };

  // ── safe markdown: escape first, then a small subset ──
  function inline(t){   // t is already escaped
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    t = t.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, '$1<i>$2</i>');
    t = t.replace(/\[([^\]]+)\]\((https:\/\/[^\s)]+)\)/g, function(m, a, h){ return '<a href="' + h.replace(/"/g, '&quot;') + '" target="_blank" rel="noopener noreferrer">' + a + '</a>'; });
    return t; }
  function md(src){
    var L = esc(String(src || '')).replace(/\r/g, '').split('\n'), out = [], i = 0, para = [];
    function flush(){ if(para.length){ out.push('<p>' + inline(para.join(' ')) + '</p>'); para = []; } }
    while(i < L.length){ var l = L[i], m;
      if(/^```/.test(l)){ flush(); var code = []; i++; while(i < L.length && !/^```/.test(L[i])){ code.push(L[i]); i++; } i++; out.push('<pre class="ac-pre">' + code.join('\n') + '</pre>'); continue; }
      if((m = /^(#{1,4})\s+(.*)$/.exec(l))){ flush(); var h = Math.min(6, m[1].length + 2); out.push('<h' + h + ' class="ac-h">' + inline(m[2]) + '</h' + h + '>'); i++; continue; }
      if(/^\s*(-{3,}|\*{3,})\s*$/.test(l)){ flush(); out.push('<hr>'); i++; continue; }
      if(/^\s*\|.*\|\s*$/.test(l)){ flush(); var rows = []; while(i < L.length && /^\s*\|.*\|\s*$/.test(L[i])){ rows.push(L[i]); i++; }
        var cells = function(r){ return r.trim().replace(/^\||\|$/g, '').split('|').map(function(c){ return c.trim(); }); };
        var head = cells(rows[0]), body = rows.slice(1).filter(function(r){ return !/^\s*\|[\s:|-]+\|\s*$/.test(r); });
        out.push('<div class="ac-tw"><table class="ac-t"><tr>' + head.map(function(c){ return '<th>' + inline(c) + '</th>'; }).join('') + '</tr>' +
          body.map(function(r){ return '<tr>' + cells(r).map(function(c){ return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></div>'); continue; }
      if(/^\s*([-*+]|\d+[.)])\s+/.test(l)){ flush(); var ol = /^\s*\d/.test(l), items = [];
        while(i < L.length && /^\s*([-*+]|\d+[.)])\s+/.test(L[i])){ items.push(L[i].replace(/^\s*([-*+]|\d+[.)])\s+/, '')); i++;
          while(i < L.length && /^\s{2,}\S/.test(L[i]) && !/^\s*([-*+]|\d+[.)])\s+/.test(L[i])){ items[items.length - 1] += ' ' + L[i].trim(); i++; } }
        out.push((ol ? '<ol>' : '<ul>') + items.map(function(x){ return '<li>' + inline(x) + '</li>'; }).join('') + (ol ? '</ol>' : '</ul>')); continue; }
      if(/^&gt;\s?/.test(l)){ flush(); var q = []; while(i < L.length && /^&gt;\s?/.test(L[i])){ q.push(L[i].replace(/^&gt;\s?/, '')); i++; } out.push('<blockquote class="ac-q">' + inline(q.join(' ')) + '</blockquote>'); continue; }
      if(!l.trim()){ flush(); i++; continue; }
      para.push(l.trim()); i++; }
    flush(); return out.join('\n'); }

  // ── server ──
  function fetchT(url, opt, ms){ var c = typeof AbortController !== 'undefined' ? new AbortController() : null; opt = opt || {}; if(c) opt.signal = c.signal;
    var t = setTimeout(function(){ try{ c && c.abort(); }catch(e){} }, ms || 15000);
    return fetch(url, opt).finally(function(){ clearTimeout(t); }); }
  async function detail(r){ try{ var j = await r.json(); return (j && (j.detail || j.error || j.message)) || ('HTTP ' + r.status); }catch(e){ return 'HTTP ' + r.status; } }
  async function loadCatalog(force){ if(st.fetching || (!force && st.src === 'server')) return; st.fetching = true; st.tried = Date.now(); render();
    try{ var r = await fetchT(server() + '/academy/catalog', { headers:{ 'Accept':'application/json' } }, 20000); if(!r.ok) throw new Error(await detail(r));
      var j = await r.json(); if(!j || !Array.isArray(j.modules) || !j.modules.length) throw new Error('the server has no course yet');
      if(!j.pricing || typeof j.pricing !== 'object') j.pricing = bundled.pricing || {}; st.cat = j; st.src = 'server'; st.err = ''; }
    catch(e){ st.err = 'Server not reached (' + (e && e.name === 'AbortError' ? 'timed out — a sleeping server takes about a minute to wake' : (e && e.message || e)) + '). Showing the free lessons built into the app.'; }
    st.fetching = false; render(); }
  function find(id){ var mods = st.cat.modules || []; for(var a=0;a<mods.length;a++) for(var b=0;b<(mods[a].lessons||[]).length;b++) if(mods[a].lessons[b].id === id) return { mo:mods[a], le:mods[a].lessons[b], mi:a, li:b }; return null; }
  function bundledLesson(id){ var mods = bundled.modules || []; for(var a=0;a<mods.length;a++) for(var b=0;b<(mods[a].lessons||[]).length;b++) if(mods[a].lessons[b].id === id) return mods[a].lessons[b]; return null; }
  async function loadPremium(id){ var p = prog(); if(!p.token) return; st.premium[id] = { loading:true }; render();
    try{ var r = await fetchT(server() + '/academy/lesson/' + encodeURIComponent(id), { headers:{ 'X-Academy-Token':p.token, 'Accept':'application/json' } }, 25000);
      if(r.status === 402 || r.status === 401){ st.premium[id] = { err:'Your unlock is no longer valid (' + await detail(r) + '). Enter your license key again.' }; }
      else if(!r.ok) st.premium[id] = { err:await detail(r) };
      else { var j = await r.json(); st.premium[id] = { lesson:j }; } }
    catch(e){ st.premium[id] = { err:'Could not reach the server: ' + (e && e.message || e) }; }
    render(); }
  async function unlock(key){ key = String(key || '').trim(); if(!key){ st.msg = 'Enter the license key from your purchase email.'; render(); return; }
    st.msg = 'Checking your key…'; render();
    try{ var r = await fetchT(server() + '/academy/unlock', { method:'POST', headers:{ 'Content-Type':'application/json', 'Accept':'application/json' }, body:JSON.stringify({ license_key:key }) }, 30000);
      if(!r.ok){ st.msg = 'Not unlocked: ' + await detail(r); render(); return; }
      var j = await r.json(); if(!j || !j.ok || !j.token){ st.msg = 'Not unlocked: the server gave no token.'; render(); return; }
      var p = prog(); p.token = String(j.token).slice(0, 2000); p.unlockedAt = Date.now(); saveProg(p); st.premium = {}; st.keyBox = false; st.msg = 'Unlocked — the full course is open on this device. Thank you!'; }
    catch(e){ st.msg = 'Could not reach the server: ' + (e && e.message || e); }
    render(); }

  // ── page ──
  function money(n){ return n == null || n === '' ? '' : '$' + n; }
  function priceBox(){ var P = (st.cat && st.cat.pricing) || bundled.pricing || {}, p = prog(), url = String(P.checkout_url || '').trim();
    if(p.token) return '<div class="ac-unlock ok"><b>Full course unlocked on this device.</b> <button class="btn-ghost" type="button" data-ac="relock">Remove the unlock</button></div>';
    var buy = /^https:\/\/[^\s"'<>]+$/.test(url) ? '<a class="btn-primary ac-buy" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">Unlock the full course — ' + esc(money(P.launch_price)) + (P.regular_price ? ' <s>' + esc(money(P.regular_price)) + '</s>' : '') + '</a>'
      : '<button class="btn-primary ac-buy" type="button" disabled>Coming soon — launch price ' + esc(money(P.launch_price || 49)) + ', regular ' + esc(money(P.regular_price || 97)) + '</button>';
    return '<div class="ac-unlock">' + buy + ' <button class="btn-outline" type="button" data-ac="key">I have a license key</button>' +
      (st.keyBox ? '<div class="ac-key"><input type="text" id="acKeyInput" placeholder="License key from your purchase email" autocomplete="off"> <button class="btn" type="button" data-ac="unlock">Unlock</button></div>' : '') +
      '<p class="hint" style="margin:6px 0 0;">' + esc(P.label || 'Full OMEGA Academy: lifetime access and all updates') + '. One payment; the key arrives by email.</p></div>'; }
  function counts(mo){ var p = prog(), n = (mo.lessons || []).length, d = (mo.lessons || []).filter(function(l){ return p.done[l.id]; }).length; return { n:n, d:d }; }
  function listHtml(){ var C = st.cat, p = prog(), mods = C.modules || [], all = 0, done = 0;
    mods.forEach(function(m){ var c = counts(m); all += c.n; done += c.d; });
    var pct = all ? Math.round(100*done/all) : 0, cont = p.last && find(p.last);
    return '<div class="card ac-head"><h2 style="color:var(--gold);margin-top:0;">' + esc(C.title || 'OMEGA Academy') + '</h2>' +
      '<div class="ac-bar"><i style="width:' + pct + '%"></i></div><p class="hint" style="margin:6px 0;">' + done + ' of ' + all + ' lessons done (' + pct + '%). ' +
      (st.src === 'server' ? 'Course loaded from the server.' : (st.fetching ? 'Loading the latest course from the server…' : 'Built-in free lessons' + (st.err ? ' — ' + esc(st.err) : '.'))) + '</p>' +
      '<div class="journal-actions">' + (cont ? '<button class="btn" type="button" data-ac-open="' + esc(p.last) + '">Continue: ' + esc(cont.le.title) + '</button>' : '') +
      '<button class="btn-ghost" type="button" data-ac="tour">Tutorial: how to use OMEGA</button>' + (st.src !== 'server' ? '<button class="btn-ghost" type="button" data-ac="reload">Try the server again</button>' : '') + '</div>' +
      priceBox() + (st.msg ? '<p class="hint ac-msg">' + esc(st.msg) + '</p>' : '') + '</div>' +
      (C.disclaimer ? '<p class="hint ac-disc"><b>Please read:</b> ' + esc(C.disclaimer) + '</p>' : '') +
      mods.map(function(m, mi){ var c = counts(m);
        return '<div class="card ac-mod"><div class="ac-mh"><b>' + (mi + 1) + '. ' + esc(m.title) + '</b><span class="ac-chip">' + c.d + '/' + c.n + '</span></div>' +
          (m.summary ? '<p class="hint" style="margin:4px 0 8px;">' + esc(m.summary) + '</p>' : '') +
          '<div class="ac-bar sm"><i style="width:' + (c.n ? Math.round(100*c.d/c.n) : 0) + '%"></i></div><ol class="ac-ls">' + (m.lessons || []).map(function(l){
            var lock = !l.free && !p.token, q = p.quiz[l.id];
            return '<li><button type="button" class="ac-l' + (p.done[l.id] ? ' done' : '') + '" data-ac-open="' + esc(l.id) + '"><span>' + (p.done[l.id] ? '✓ ' : lock ? '🔒 ' : '') + esc(l.title) + '</span><em>' +
              (l.minutes ? esc(l.minutes) + ' min' : '') + (l.free && !m.free ? ' · free preview' : '') + (q ? ' · quiz ' + q.score + '/' + q.total : '') + '</em></button></li>'; }).join('') + '</ol></div>'; }).join(''); }
  function lessonHtml(id){ var f = find(id); if(!f) return '<p class="hint">Lesson not found.</p>';
    var p = prog(), le = f.le, body = le.body_md != null ? le : null, pr = st.premium[id];
    if(!body && !le.free && pr && pr.lesson) body = pr.lesson;
    if(!body && le.free){ body = bundledLesson(id); }
    var flat = []; (st.cat.modules || []).forEach(function(m){ (m.lessons || []).forEach(function(l){ flat.push(l.id); }); });
    var k = flat.indexOf(id), prev = flat[k - 1], next = flat[k + 1];
    var h = '<div class="card ac-reader"><div class="journal-actions"><button class="btn-ghost" type="button" data-ac="back">← All modules</button></div>' +
      '<p class="hint" style="margin:6px 0 0;">Module ' + (f.mi + 1) + ' · ' + esc(f.mo.title) + (le.minutes ? ' · ' + esc(le.minutes) + ' min' : '') + '</p><h2 class="ac-title">' + esc(le.title) + '</h2>' +
      (st.cat.disclaimer ? '<p class="hint ac-disc">' + esc(st.cat.disclaimer) + '</p>' : '');
    if(!body){
      if(!le.free && !p.token) h += '<div class="ac-lock"><b>🔒 This lesson is part of the full course.</b><p class="hint">The free lessons (modules 1 and 2 and the first lesson of every module) are open to everyone.</p>' + priceBox() + (st.msg ? '<p class="hint ac-msg">' + esc(st.msg) + '</p>' : '') + '</div>';
      else if(pr && pr.loading) h += '<p class="hint">Loading the lesson…</p>';
      else if(pr && pr.err) h += '<p class="hint" style="color:var(--bear);">' + esc(pr.err) + '</p><button class="btn" type="button" data-ac="retry">Try again</button>' + (/valid|license/i.test(pr.err) ? priceBox() : '');
      else { h += '<p class="hint">Loading the lesson…</p>'; setTimeout(function(){ loadPremium(id); }, 0); }
    } else {
      h += '<div class="ac-md">' + md(body.body_md) + '</div>';
      var kp = Array.isArray(body.key_points) ? body.key_points : [];
      if(kp.length) h += '<div class="ac-kp"><h3 class="ac-h">Key points</h3><ul>' + kp.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
      var qz = Array.isArray(body.quiz) ? body.quiz : [];
      if(qz.length) h += '<div class="ac-quiz"><h3 class="ac-h">Check yourself</h3>' + qz.map(function(q, qi){
        return '<div class="ac-qq" data-qi="' + qi + '"><p><b>' + (qi + 1) + '.</b> ' + esc(q.q) + '</p>' + (q.options || []).map(function(o, oi){
          return '<label class="ac-opt"><input type="radio" name="acq' + qi + '" value="' + oi + '"> ' + esc(o) + '</label>'; }).join('') + '<div class="ac-why"></div></div>'; }).join('') +
        '<button class="btn" type="button" data-ac="check">Check my answers</button> <span class="hint" id="acQuizMsg">' + (p.quiz[id] ? 'Last score: ' + p.quiz[id].score + '/' + p.quiz[id].total : '') + '</span></div>';
      h += '<div class="journal-actions" style="margin-top:12px;">' + (p.done[id] ? '<span class="ac-chip ok">✓ Done</span>' : '<button class="btn-primary" type="button" data-ac="done">Mark lesson complete</button>') + '</div>';
    }
    h += '<div class="journal-actions ac-nav">' + (prev ? '<button class="btn-ghost" type="button" data-ac-open="' + esc(prev) + '">← Previous</button>' : '') + (next ? '<button class="btn-outline" type="button" data-ac-open="' + esc(next) + '">Next lesson →</button>' : '') + '</div></div>';
    return h; }
  function css(){ if(el('acadCss')) return; var c = document.createElement('style'); c.id = 'acadCss';
    c.textContent = '.ac-bar{height:8px;border-radius:6px;background:var(--panel2);overflow:hidden;border:1px solid var(--border)}.ac-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--gold),var(--bull))}.ac-bar.sm{height:5px}' +
      '.ac-mh{display:flex;justify-content:space-between;align-items:center;gap:8px}.ac-chip{font-size:11px;padding:2px 8px;border-radius:10px;border:1px solid var(--border);color:var(--text-dim)}.ac-chip.ok{color:var(--bull);border-color:var(--bull)}' +
      '.ac-mod{margin-top:12px}.ac-ls{margin:8px 0 0;padding-left:20px}.ac-ls li{margin:4px 0}.ac-l{width:100%;display:flex;justify-content:space-between;gap:8px;text-align:left;background:var(--panel2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:9px 10px;cursor:pointer;font:inherit;min-height:44px}' +
      '.ac-l em{font-style:normal;color:var(--text-dim);font-size:11px;white-space:nowrap}.ac-l.done span{color:var(--bull)}.ac-unlock{margin-top:10px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.ac-unlock .hint{flex-basis:100%}.ac-unlock.ok{color:var(--bull)}' +
      '.ac-buy{text-decoration:none;display:inline-block}.ac-key{flex-basis:100%;display:flex;gap:8px}.ac-key input{flex:1;min-width:0}.ac-msg{color:var(--gold)}.ac-disc{font-size:11px;border-left:3px solid var(--amber,#c90);padding-left:8px}' +
      '.ac-title{margin:4px 0 8px}.ac-md{line-height:1.6;overflow-wrap:anywhere}.ac-md p{margin:8px 0}.ac-h{margin:16px 0 6px}.ac-pre{white-space:pre-wrap;background:var(--panel2);padding:8px;border-radius:6px;font-size:12px;overflow-x:auto}' +
      '.ac-tw{overflow-x:auto}.ac-t{border-collapse:collapse;font-size:12px;margin:8px 0}.ac-t th,.ac-t td{border:1px solid var(--border);padding:4px 6px;text-align:left}.ac-q{border-left:3px solid var(--gold);margin:8px 0;padding:4px 10px;color:var(--text-dim)}' +
      '.ac-kp{margin-top:12px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;background:var(--panel2)}.ac-qq{margin:10px 0;padding:8px 10px;border:1px solid var(--border);border-radius:8px}.ac-opt{display:flex;gap:8px;align-items:flex-start;padding:6px 0;cursor:pointer}.ac-opt input{width:auto;margin-top:3px}' +
      '.ac-why{font-size:12px;margin-top:4px}.ac-why.ok{color:var(--bull)}.ac-why.no{color:var(--bear)}.ac-nav{margin-top:14px;justify-content:space-between}.ac-lock{padding:10px;border:1px dashed var(--border);border-radius:8px}' +
      '.om-tour{position:relative;margin:0 0 14px;padding:14px 14px 12px;border:1px solid var(--gold);border-radius:12px;background:var(--panel)}.om-tour h3{margin:2px 0 6px}.om-tour .tstep{font-size:11px;color:var(--text-dim);letter-spacing:.08em;text-transform:uppercase}' +
      '.om-tour .tdots{display:flex;gap:4px;margin:8px 0}.om-tour .tdots i{width:18px;height:4px;border-radius:2px;background:var(--border)}.om-tour .tdots i.on{background:var(--gold)}';
    document.head.appendChild(c); }
  function render(){ var host = el('acadBody'); if(!host) return; css();
    host.innerHTML = st.open ? lessonHtml(st.open) : listHtml(); wire(host); }
  function openLesson(id){ var f = find(id); if(!f) return; st.open = id; st.msg = ''; var p = prog(); p.last = id; saveProg(p); render(); try{ el('page-academy').scrollIntoView({ block:'start' }); window.scrollTo(0, 0); }catch(e){} }
  function wire(host){
    Array.prototype.forEach.call(host.querySelectorAll('[data-ac-open]'), function(b){ b.onclick = function(){ openLesson(b.getAttribute('data-ac-open')); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-ac]'), function(b){ b.onclick = function(){ var k = b.getAttribute('data-ac'), p = prog();
      if(k === 'back'){ st.open = null; st.msg = ''; render(); }
      else if(k === 'key'){ st.keyBox = !st.keyBox; render(); var i = el('acKeyInput'); if(i) i.focus(); }
      else if(k === 'unlock'){ unlock((el('acKeyInput') || {}).value); }
      else if(k === 'relock'){ if(confirm('Remove the unlock from this device? You can enter your key again at any time.')){ delete p.token; saveProg(p); st.premium = {}; render(); } }
      else if(k === 'reload'){ loadCatalog(true); }
      else if(k === 'retry'){ delete st.premium[st.open]; render(); }
      else if(k === 'tour'){ TOUR.open(true); }
      else if(k === 'done'){ p.done[st.open] = Date.now(); saveProg(p); render(); }
      else if(k === 'check'){ var f = find(st.open), body = f && (f.le.body_md != null ? f.le : (st.premium[st.open] || {}).lesson || bundledLesson(st.open)); if(!body) return;
        var qz = body.quiz || [], score = 0, answered = 0;
        Array.prototype.forEach.call(host.querySelectorAll('.ac-qq'), function(d){ var qi = +d.getAttribute('data-qi'), q = qz[qi], s = d.querySelector('input:checked'), w = d.querySelector('.ac-why'); if(!q || !w) return;
          if(!s){ w.className = 'ac-why'; w.textContent = 'Pick an answer.'; return; } answered++; var good = +s.value === +q.answer; if(good) score++;
          w.className = 'ac-why ' + (good ? 'ok' : 'no'); w.textContent = (good ? '✓ Right. ' : '✗ Not quite — the answer is “' + (q.options || [])[q.answer] + '”. ') + (q.why || ''); });
        var m = el('acQuizMsg'); if(answered === qz.length){ p.quiz[st.open] = { score:score, total:qz.length, at:Date.now() }; saveProg(p); if(m) m.textContent = 'Score: ' + score + '/' + qz.length + (score === qz.length ? ' — well done.' : ' — read the explanations, then try again.'); }
        else if(m) m.textContent = 'Answer every question first.'; } }; }); }
  function onShow(){ render(); if(st.src !== 'server' && !st.fetching && Date.now() - st.tried > 60e3) loadCatalog(false); }

  // ── tutorial: a card at the top of the page, never a blocking overlay ──
  var STEPS = [
    { t:'Home: read the verdict first', p:'command', x:'Home answers five questions from what the app actually holds: what is happening, what is actionable, what needs you. A strong bias with no permission is a reason to wait, not to trade.' },
    { t:'Open a chart', p:'analysis', x:'Charts (Analysis) shows one market in depth: candles, volume, the cockpit with levels and the order book. Pick a market at the top and read structure before indicators.' },
    { t:'Use the mark-up', p:'mread', x:'Market Read marks where liquidity sits (stops above and below, resting orders, who is crowded). Use it to place your stop beyond the obvious level, not on it.' },
    { t:'Read CREED and OMEGA signals honestly', p:'osig', x:'Signals carry grades: climax reversal A (passed fair tests), panic bounce B (passed, not yet confirmed), Daily Plan C (a plan, not a tested edge). CREED measured about a coin flip after costs — treat it as structure, not a promise.' },
    { t:'Risk Guard and the bots', p:'rguard', x:'Risk Guard sets the rules: 0.5% a trade, 2 open at most, −2% a day and −5% a week stop trading. The Growth Bot follows them on paper; the Bots page shows every bot. Nothing here places real orders.' },
    { t:'Learn in the Academy', p:'academy', x:'The Academy teaches markets, chart reading, risk first, and how to test an idea before trusting it. Modules 1 and 2 are free. You can reopen this tutorial from the Academy or Settings.' }];
  var TOUR = (function(){ var i = 0, on = false;
    function card(){ var c = el('omegaTour'); if(!c){ c = document.createElement('div'); c.id = 'omegaTour'; c.className = 'om-tour'; c.setAttribute('role', 'region'); c.setAttribute('aria-label', 'Tutorial'); } return c; }
    function place(){ if(!on) return; var pg = document.querySelector('.page.active') || el('page-command'); if(!pg) return; var c = card(); css();
      var S = STEPS[i]; c.innerHTML = '<div class="tstep">Tutorial · step ' + (i + 1) + ' of ' + STEPS.length + '</div><h3>' + esc(S.t) + '</h3><p class="hint" style="margin:0;color:var(--text);">' + esc(S.x) + '</p>' +
        '<div class="tdots">' + STEPS.map(function(_, k){ return '<i class="' + (k <= i ? 'on' : '') + '"></i>'; }).join('') + '</div>' +
        '<div class="journal-actions"><button class="btn-outline" type="button" data-t="show">Show me</button>' + (i ? '<button class="btn-ghost" type="button" data-t="prev">Back</button>' : '') +
        (i < STEPS.length - 1 ? '<button class="btn" type="button" data-t="next">Next</button>' : '<button class="btn-primary" type="button" data-t="end">Finish</button>') + '<button class="btn-ghost" type="button" data-t="skip">Skip the tutorial</button></div>';
      if(c.parentNode !== pg) pg.insertBefore(c, pg.firstChild);
      Array.prototype.forEach.call(c.querySelectorAll('[data-t]'), function(b){ b.onclick = function(){ var k = b.getAttribute('data-t');
        if(k === 'next'){ i = Math.min(STEPS.length - 1, i + 1); place(); } else if(k === 'prev'){ i = Math.max(0, i - 1); place(); }
        else if(k === 'show'){ if(el('page-' + STEPS[i].p)) window.navigate(STEPS[i].p); setTimeout(place, 80); try{ window.scrollTo(0, 0); }catch(e){} }
        else close(k); }; }); }
    function close(why){ on = false; var c = el('omegaTour'); if(c && c.parentNode) c.parentNode.removeChild(c); lsSet(TKEY, { done:Date.now(), how:why || 'closed' }); }
    function open(fromStart){ on = true; if(fromStart) i = 0; place(); try{ window.scrollTo(0, 0); }catch(e){} }
    return { open:open, close:close, place:place, isOpen:function(){ return on; }, step:function(){ return i; }, STEPS:STEPS }; })();

  // ── settings ──
  function wireSettings(){ var inp = el('acadServerInput'), sv = el('acadServerSave'), to = el('acadTourOpen'), msg = el('acadServerMsg'); if(!inp) return;
    var cur = ''; try{ cur = localStorage.getItem(SKEY) || ''; }catch(e){} inp.value = cur || DEF;
    if(sv) sv.onclick = function(){ var u = String(inp.value || '').trim().replace(/\/+$/, '');
      if(!u || u === DEF){ try{ localStorage.removeItem(SKEY); }catch(e){} inp.value = DEF; if(msg) msg.textContent = 'Using the default server: ' + DEF; }
      else if(!okServer(u)){ if(msg) msg.textContent = 'Not saved: the address must start with https:// (or http://localhost for testing).'; return; }
      else { try{ localStorage.setItem(SKEY, u); }catch(e){} if(msg) msg.textContent = 'Saved. The Academy now uses ' + u; }
      st.src = 'bundled'; st.cat = bundled; st.tried = 0; st.premium = {}; };
    if(to) to.onclick = function(){ window.navigate('command'); TOUR.open(true); }; }

  // every navigation (menu, bottom bar, palette, links) ends in the Command navigator's syncBottomNav, which calls this
  window.__omegaAfterNav = function(p){ if(p === 'academy') setTimeout(onShow, 30); if(TOUR.isOpen()) setTimeout(TOUR.place, 40); };
  function boot(){ wireSettings(); if(el('page-academy') && el('page-academy').classList.contains('active')) onShow();
    if(!lsGet(TKEY, null)) setTimeout(function(){ if(!lsGet(TKEY, null)) TOUR.open(true); }, 2500); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else setTimeout(boot, 0);
  window.OMEGA_ACADEMY = { render:render, onShow:onShow, md:md, esc:esc, load:loadCatalog, open:openLesson, unlock:unlock, server:server, state:function(){ return st; }, progress:prog, tour:TOUR, KEY:KEY };
})();
</script>
'''
rep('</body>', DATA_BLOCK + '\n' + JS + '</body>')

o = re.search(r'v6\.5\.109 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.109 ' + sep + ' build ' + o + ' UTC', 'v6.5.110 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.110 · build' in s and 'v6.5.109 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'free lessons embedded', nfree, 'size', len(s.encode('utf-8')))
