"""v6.5.120: Signal Auditor: check a signal provider against real prices. CREED's engine is byte-identical.
 New page "Signal Auditor" (menu under Signals, a line on Home, the command palette; bottom bar unchanged):
  - paste a signal message (+ who sent it) -> POST /auditor/parse on the OMEGA Live API reads it and stamps it with the
    SERVER's time; the signal is saved on this device (localStorage omega_auditor_v1) with that logged time;
  - "Score all" -> POST /auditor/score: per signal the status (waiting for entry, not filled, running, closed), fill,
    outcome, pips and R for both styles (everything at TP1 / ladder), then the summary per provider and the verdict line;
  - a signal can be deleted only while its status is "waiting for entry" (rule 2 of edges/auditor/RULES.md: nothing
    leaves the score once it filled);
  - a small risk check (balance + symbol + side + lots) -> POST /auditor/risk: how far price can move before the balance
    is gone, against typical recent moves.
 The page needs the Live API token; without it it says so. Information only: nothing here places an order.
usage: python3 patch120.py <v6.5.119> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


PAGE = '''    <div id="page-auditor" class="page">
      <header class="om-head"><h2>Signal Auditor</h2><p>Paste every signal a provider sends, the moment it arrives. OMEGA stamps it with the time it was logged and later scores it against real prices: wins, losses and orders that never filled all count.</p></header>
      <div id="auditorBody"></div>
      <details class="om-about"><summary>About this page</summary><div class="om-about-body">
        <p><b>Why log first.</b> A recap posted after the week cannot be checked; a signal logged before the move can. A signal counts from the moment it was logged here (the server&rsquo;s clock), never from a time someone claims later.</p>
        <p><b>How it is scored.</b> &ldquo;Now&rdquo; signals fill at the next minute&rsquo;s open; a price away from the market fills only if price trades there (24 hours, otherwise NOT FILLED). After the fill each minute is checked stop first: if the stop and a target sit inside the same minute it counts as the stop. Two styles are scored: everything closed at the first target (TP1), and equal parts at each target with the stop moved to entry after TP1 (ladder). A typical retail spread is charged once. Maximum hold 48 hours.</p>
        <p><b>R</b> is the result in units of the risk (entry to stop): +1R wins what was risked, &minus;1R loses it. A signal without a stop cannot be measured in R; it is still scored in pips and flagged.</p>
        <p><b>Nothing disappears.</b> A signal can be deleted only while it is still waiting for its entry. About 30 closed signals with stops are needed before the numbers mean anything, 50 or more to trust them.</p>
        <p>Signals are kept on this device; the Live API only reads and scores them. Information only: OMEGA places no orders from this page.</p>
      </div></details>
    </div>
'''
rep('    <div id="page-about" class="page">\n', PAGE + '    <div id="page-about" class="page">\n')
rep('''      <li data-page="radar" onclick="navigate('radar')"><span class="sb-icon">◎</span> CREED Scanner <span class="sb-badge" id="sbBadge-radar"></span></li>\n''',
    '''      <li data-page="radar" onclick="navigate('radar')"><span class="sb-icon">◎</span> CREED Scanner <span class="sb-badge" id="sbBadge-radar"></span></li>\n      <li data-page="auditor" onclick="navigate('auditor')"><span class="sb-icon">✓</span> Signal Auditor</li>\n''')
rep("'academy','forex','about','desks'];   // v6.5.119: Desks", "'academy','forex','about','desks','auditor'];   // v6.5.119: Desks; v6.5.120: Signal Auditor")
rep("      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_DESKS) window.OMEGA_DESKS.onShow(); });\n",
    "      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_DESKS) window.OMEGA_DESKS.onShow(); });\n"
    "      drawSafe(p, function(){ if(p === 'auditor' && window.OMEGA_AUDITOR) window.OMEGA_AUDITOR.onShow(); });\n")
rep("['desks','Desks (Bitcoin, Gold, Silver)'],", "['desks','Desks (Bitcoin, Gold, Silver)'],['auditor','Signal Auditor'],")
rep('      <div id="homeDesks" class="dk-home"></div>\n', '      <div id="homeDesks" class="dk-home"></div>\n      <div id="homeAuditor"></div>\n')

CSS = r'''<style id="auditorCss">/* v6.5.120: Signal Auditor (theme variables only) */
.sa-form{display:grid;gap:8px}.sa-form textarea,.sa-form input,.sa-form select{width:100%;box-sizing:border-box;background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:9px 10px;color:var(--text);font:inherit;font-size:14px}
.sa-form textarea{min-height:76px;resize:vertical}.sa-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.sa-row>*{flex:1 1 110px;min-width:0}.sa-row>button{flex:0 0 auto}
.sa-msg{font-size:12.5px;color:var(--text-dim);margin:6px 0 0;line-height:1.5}.sa-msg.bad{color:var(--bear)}.sa-msg.good{color:var(--bull)}
.sa-verdict{font-size:15px;color:var(--text);line-height:1.5;margin:0 0 8px}.sa-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:8px 0}@media(max-width:560px){.sa-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.sa-stats div{background:var(--panel2);border-radius:10px;padding:8px 10px;min-width:0}.sa-stats b{display:block;font-size:15px;color:var(--text)}.sa-stats span{font-size:11px;color:var(--text-dim)}
.sa-sig{border-top:1px solid var(--border);padding:10px 0}.sa-sig:first-child{border-top:0}.sa-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start;flex-wrap:wrap}
.sa-top b{color:var(--text);font-size:14px}.sa-sub{font-size:12px;color:var(--text-dim);line-height:1.5;overflow-wrap:anywhere}.sa-res{font-size:13px;color:var(--text);margin:4px 0 0;line-height:1.5}
.sa-st{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;border:1px solid var(--border);color:var(--text-dim);white-space:nowrap}
.sa-st.closed{color:var(--text)}.sa-st.running{color:var(--gold);border-color:var(--gold)}.sa-st.waiting{color:var(--amber);border-color:var(--amber)}.sa-st.error{color:var(--bear);border-color:var(--bear)}
.sa-win{color:var(--bull);font-weight:600}.sa-loss{color:var(--bear);font-weight:600}.sa-flag{color:var(--amber)}.sa-sig details{margin-top:4px}.sa-sig summary{cursor:pointer;font-size:12px;color:var(--text-dim)}
.sa-del{padding:4px 10px!important;font-size:12px!important}.sa-home{display:flex;justify-content:space-between;align-items:center;gap:10px;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:10px 14px;margin:0 0 14px;font-size:13px;color:var(--text-dim)}
.sa-home b{color:var(--text)}.sa-home .btn-outline{padding:5px 12px;font-size:12px;white-space:nowrap}
</style>
'''
JS = r'''<script>/* ═══ SIGNAL AUDITOR (v6.5.120) ═══
   The log lives on this device (omega_auditor_v1) with the server's logged time; the OMEGA Live API reads messages
   (/auditor/parse), scores them against real prices (/auditor/score) and checks account risk (/auditor/risk).
   Rules: edges/auditor/RULES.md. Information only. */
(function(){
  'use strict';
  var KEY = 'omega_auditor_v1', TOK = 'omega_live_token', MAX = 300;
  var S = (function(){ try{ return JSON.parse(localStorage.getItem(KEY) || 'null') || {}; }catch(e){ return {}; } })();
  S.signals = Array.isArray(S.signals) ? S.signals : []; S.results = S.results || {}; S.scoredAt = S.scoredAt || 0; S.summary = S.summary || null; S.by = S.by || null; S.provider = S.provider || '';
  var UI = { msg:'', bad:false, busy:false, risk:null, riskMsg:'', draft:'', rb:'', rl:'', rs:'XAUUSD', rd:'buy' };
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function L(){ return window.OMEGA_LAPI; }
  function on(){ return !!(L() && L().on()); }
  function when(t){ var d = new Date(+t); return isFinite(d) ? d.toLocaleString([], { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }) : '—'; }
  function n(x, d){ x = +x; return isFinite(x) ? x.toFixed(d == null ? 1 : d) : '—'; }
  function sg(x, d, u){ x = +x; return isFinite(x) ? '<span class="' + (x > 0 ? 'sa-win' : x < 0 ? 'sa-loss' : '') + '">' + (x > 0 ? '+' : '') + x.toFixed(d) + (u || '') + '</span>' : '—'; }
  async function post(path, body){ var t = ''; try{ t = String(localStorage.getItem(TOK) || '').trim(); }catch(e){} if(!t) throw new Error('the Live API token is missing (Settings > Data & Keys)');
    var c = typeof AbortController !== 'undefined' ? new AbortController() : null, tm = setTimeout(function(){ try{ c && c.abort(); }catch(e){} }, 90000), r;
    try{ r = await fetch(L().server() + path, { method:'POST', headers:{ 'Content-Type':'application/json', 'Accept':'application/json', 'Authorization':'Bearer ' + t }, body:JSON.stringify(body), signal:c ? c.signal : undefined }); }
    catch(e){ throw new Error(e && e.name === 'AbortError' ? 'the server did not answer in time (a sleeping server takes about a minute to wake)' : 'the server could not be reached'); }
    finally{ clearTimeout(tm); }
    var j = null; try{ j = await r.json(); }catch(e){}
    if(r.status === 401) throw new Error('the Live API token is missing or wrong (Settings > Data & Keys)');
    if(!r.ok) throw new Error(j && j.detail ? (typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)).slice(0, 200) : 'HTTP ' + r.status);
    return j; }
  function say(t, bad){ UI.msg = t; UI.bad = !!bad; }
  function keep(){ var a = el('saText'), p = el('saProv'); if(a) UI.draft = a.value; if(p) S.provider = p.value.trim().slice(0, 60);
    ['rb:saBal', 'rl:saLots', 'rs:saSym', 'rd:saSide'].forEach(function(x){ var k = x.split(':'), e = el(k[1]); if(e) UI[k[0]] = e.value; }); }
  // ── actions ──
  async function add(){ keep(); var text = UI.draft.trim(); if(!text){ say('Paste the signal message first.', true); return draw(); }
    if(S.signals.length >= MAX){ say('The log is full (' + MAX + ' signals).', true); return draw(); }
    UI.busy = true; say('Reading the message…'); draw();
    try{ var j = await post('/auditor/parse', { text:text, provider:S.provider }), sig = j.signal; sig.id = 'sa' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      sig.problems = j.problems || []; S.signals.unshift(sig); save(); UI.draft = '';
      say('Logged ' + sig.symbol + ' ' + sig.side + ' at ' + when(sig.logged_ms) + ' (server time). It will be scored from that moment.' + (sig.problems.length ? ' Note: ' + sig.problems.join('; ') + '.' : '')); }
    catch(e){ say('Not logged: ' + (e && e.message || e), true); }
    UI.busy = false; draw(); }
  async function scoreAll(){ keep(); if(!S.signals.length){ say('Nothing to score yet.', true); return draw(); }
    UI.busy = true; say('Scoring ' + S.signals.length + ' signal(s) against real prices…'); draw();
    try{ var sent = S.signals.slice(), j = await post('/auditor/score', { signals:sent.map(function(x){ return { id:x.id, symbol:x.symbol, side:x.side, logged_ms:x.logged_ms, entry:x.entry, entry_hi:x.entry_hi, stop:x.stop, targets:x.targets, provider:x.provider, note:x.note, claimed_pips:x.claimed_pips }; }) });
      (j.scored || []).forEach(function(r, i){ if(sent[i]) S.results[sent[i].id] = r; }); S.summary = j.summary || null; S.by = j.by_provider || null; S.scoredAt = Date.now(); save();
      say('Scored ' + (j.scored || []).length + ' signal(s).'); }
    catch(e){ say('Not scored: ' + (e && e.message || e), true); }
    UI.busy = false; draw(); }
  function canDelete(id){ var r = S.results[id]; return !!(r && r.status === 'waiting for entry'); }
  function del(id){ keep(); if(!canDelete(id)){ say('Only a signal still waiting for its entry can be deleted: once it fills, it stays in the score.', true); return draw(); }
    S.signals = S.signals.filter(function(x){ return x.id !== id; }); delete S.results[id]; save(); say('Deleted (it had not filled).'); draw(); }
  async function risk(){ keep(); var bal = +UI.rb, lots = +UI.rl; if(!(bal > 0) || !(lots > 0)){ UI.riskMsg = 'Enter the balance and the lot size.'; UI.risk = null; return draw(); }
    UI.riskMsg = 'Checking…'; draw();
    try{ UI.risk = await post('/auditor/risk', { balance:bal, positions:[{ symbol:UI.rs, side:UI.rd, lots:lots }] }); UI.riskMsg = ''; }
    catch(e){ UI.risk = null; UI.riskMsg = 'No answer: ' + (e && e.message || e); }
    draw(); }
  // ── drawing ──
  function statusTag(r){ var st = r ? r.status : 'not scored yet', c = /closed/.test(st) ? 'closed' : /running/.test(st) ? 'running' : /waiting|not scored|no data/.test(st) ? 'waiting' : /error/.test(st) ? 'error' : ''; return '<span class="sa-st ' + c + '">' + esc(st) + '</span>'; }
  function style(name, x){ if(!x) return ''; return '<b>' + name + ':</b> ' + esc(x.outcome) + ' · ' + sg(x.pips, 1, ' pips') + (x.R != null ? ' · ' + sg(x.R, 2, 'R') : ' · <span class="sa-flag">no R (no stop)</span>'); }
  function sigRow(x){ var r = S.results[x.id], probs = (r && r.problems) || x.problems || [];
    var plan = (x.entry != null ? 'entry ' + x.entry + (x.entry_hi != null ? '–' + x.entry_hi : '') : 'entry now (market)') + ' · stop ' + (x.stop != null ? x.stop : '<span class="sa-flag">none</span>') + ' · targets ' + ((x.targets || []).join(' / ') || 'none');
    var res = '';
    if(r && r.status === 'error') res = '<p class="sa-res sa-loss">Could not be scored: ' + esc(r.error) + '</p>';
    else if(r && r.fill != null) res = '<p class="sa-res">Filled ' + esc(when(r.fill_ms)) + ' at ' + esc(r.fill) + (r.risk_pips != null ? ' · risk ' + n(r.risk_pips) + ' pips' : '') + '<br>' + style('All at TP1', r.tp1) + '<br>' + style('Ladder', r.ladder) + '</p>';
    else if(r && r.status === 'not filled') res = '<p class="sa-res">The entry price was never reached within the fill window: counted as not filled.</p>';
    else if(r && r.status === 'waiting for entry') res = '<p class="sa-res">Price has not reached the entry yet.</p>';
    else if(r && r.status === 'no data yet') res = '<p class="sa-res">No price data after the logged time yet (market closed or too soon).</p>';
    return '<div class="sa-sig" data-said="' + esc(x.id) + '"><div class="sa-top"><div><b>' + esc(x.symbol) + ' ' + esc(String(x.side).toUpperCase()) + '</b> <span class="sa-sub">· ' + esc(x.provider || 'unnamed provider') + '</span><div class="sa-sub">Logged ' + esc(when(x.logged_ms)) + ' · ' + plan + '</div></div>' +
      '<div class="sa-row" style="flex:0 0 auto">' + statusTag(r) + (canDelete(x.id) ? '<button class="btn-ghost sa-del" type="button" data-sadel="' + esc(x.id) + '">Delete</button>' : '') + '</div></div>' + res +
      (probs.length ? '<div class="sa-sub sa-flag">' + probs.map(esc).join('; ') + '</div>' : '') +
      '<details><summary>The message</summary><div class="sa-sub">' + esc(x.note) + '</div></details></div>'; }
  function sumCard(title, m){ if(!m) return ''; var t = m.tp1 || {}, l = m.ladder || {};
    return '<div class="om-card"><div class="om-ch"><h3>' + esc(title) + '</h3><span class="om-tag">' + esc(m.logged) + ' logged · ' + esc(m.closed) + ' closed</span></div><p class="sa-verdict">' + esc(m.verdict || '') + '</p>' +
      '<div class="sa-stats"><div><b>' + (t.n ? sg(t.avg_R, 2, 'R') : '—') + '</b><span>average per signal, all at TP1 (' + (t.n || 0) + ' with a stop)</span></div><div><b>' + (t.win_rate != null ? Math.round(t.win_rate * 100) + '%' : '—') + '</b><span>won, all at TP1</span></div>' +
      '<div><b>' + sg(t.pips_scored, 1, '') + '</b><span>pips, all at TP1</span></div><div><b>' + sg(l.pips_scored, 1, '') + '</b><span>pips, ladder' + (l.avg_R != null ? ' (' + (l.avg_R > 0 ? '+' : '') + n(l.avg_R, 2) + 'R avg)' : '') + '</span></div></div>' +
      '<p class="sa-msg">' + esc(m.not_filled) + ' never filled · ' + esc(m.running) + ' still open or waiting · ' + esc(m.no_stop) + ' without a stop' + (t.max_losing_streak != null ? ' · longest losing run ' + esc(t.max_losing_streak) + (t.max_drawdown_pct != null ? ' · worst drawdown ' + n(t.max_drawdown_pct) + '% at ' + esc(t.risk_pct) + '% risk a trade' : '') : '') +
      (m.claimed_vs_scored ? ' · claimed ' + n(m.claimed_vs_scored.claimed_pips) + ' pips vs scored ' + n(m.claimed_vs_scored.scored_pips_tp1) : '') + '.</p></div>'; }
  function riskHtml(){ var R = UI.risk, out = ''; if(R && R.by_symbol) out = R.by_symbol.map(function(x){ return '<p class="sa-res"><b>' + esc(x.symbol) + ' ' + esc(x.net_direction) + ':</b> every 1.00 the price moves against you costs $' + n(x.usd_per_1_move, 2) + ' ($' + n(x.usd_per_pip, 2) + ' a pip). A move of <b>' + esc(x.move_to_lose_balance) + '</b> (' + esc(x.pips_to_lose_balance) + ' pips) against you equals the whole balance of $' + n(R.balance, 2) + '.' + (x.plain ? '<br><span class="sa-sub">For scale: ' + esc(x.plain) + '.</span>' : '') + '</p>'; }).join('');
    return '<div class="om-card"><div class="om-ch"><h3>Risk check</h3><span class="om-tag">before you copy a signal</span></div><p class="sa-msg" style="margin:0 0 8px">How far can price move against a position before the whole balance is gone?</p>' +
      '<div class="sa-form"><div class="sa-row"><input id="saBal" type="number" inputmode="decimal" min="0" step="any" placeholder="Balance, USD" aria-label="Balance in US dollars" value="' + esc(UI.rb) + '">' +
      '<select id="saSym" aria-label="Market">' + ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'NAS100', 'BTCUSD'].map(function(q){ return '<option' + (q === UI.rs ? ' selected' : '') + '>' + q + '</option>'; }).join('') + '</select>' +
      '<select id="saSide" aria-label="Side"><option value="buy"' + (UI.rd === 'buy' ? ' selected' : '') + '>Buy</option><option value="sell"' + (UI.rd === 'sell' ? ' selected' : '') + '>Sell</option></select>' +
      '<input id="saLots" type="number" inputmode="decimal" min="0" step="any" placeholder="Lots (e.g. 0.05)" aria-label="Lots" value="' + esc(UI.rl) + '"><button class="btn-outline" type="button" data-sarisk="1">Check</button></div></div>' +
      (UI.riskMsg ? '<p class="sa-msg' + (/No answer|Enter/.test(UI.riskMsg) ? ' bad' : '') + '">' + esc(UI.riskMsg) + '</p>' : '') + out + '</div>'; }
  function draw(){ var host = el('auditorBody'); if(host){ var out = '';
      if(!on()) out += '<div class="om-card om-empty"><b style="color:var(--text)">Connect the OMEGA Live API to log and score signals.</b><br>Add the token in Settings &rsaquo; Data &amp; Keys. Signals already logged stay on this device.<br><button class="btn-outline" type="button" data-saset="1">Open Settings</button></div>';
      out += '<div class="om-card"><div class="om-ch"><h3>Log a signal</h3><span class="om-tag">' + S.signals.length + ' logged</span></div><div class="sa-form">' +
        '<textarea id="saText" placeholder="Paste the message exactly as it arrived, e.g. XAUUSD BUY NOW 4105 SL 4095 TP1 4110 TP2 4120" aria-label="Signal message">' + esc(UI.draft) + '</textarea>' +
        '<div class="sa-row"><input id="saProv" type="text" maxlength="60" placeholder="Who sent it (provider or channel)" aria-label="Provider" value="' + esc(S.provider) + '"><button class="btn" type="button" data-saadd="1"' + (UI.busy || !on() ? ' disabled' : '') + '>Log it now</button>' +
        '<button class="btn-outline" type="button" data-sascore="1"' + (UI.busy || !on() || !S.signals.length ? ' disabled' : '') + '>Score all</button></div></div>' +
        (UI.msg ? '<p class="sa-msg ' + (UI.bad ? 'bad' : 'good') + '" id="saMsg">' + esc(UI.msg) + '</p>' : '') + '<p class="sa-msg">Log each signal when it arrives: it is scored from the logged time, so a signal typed in after the move proves nothing.</p></div>';
      if(S.summary){ out += sumCard('All signals', S.summary); var ks = Object.keys(S.by || {}); if(ks.length > 1 || (ks.length === 1 && ks[0] !== 'unnamed')) out += '<details class="dk-fold"' + (ks.length <= 3 ? ' open' : '') + '><summary>By provider <span>' + ks.length + '</span></summary><div>' + ks.map(function(k){ return sumCard(k, S.by[k]); }).join('') + '</div></details>'; }
      out += '<div class="om-card"><div class="om-ch"><h3>The log</h3><span class="om-tag">' + (S.scoredAt ? 'scored ' + esc(when(S.scoredAt)) : 'not scored yet') + '</span></div>' + (S.signals.length ? S.signals.map(sigRow).join('') : '<p class="sa-msg" style="margin:0">No signals logged yet.</p>') +
        '<p class="sa-msg">A signal can be deleted only while it is waiting for its entry. Once it fills, it stays: losses count too.</p></div>';
      out += riskHtml(); host.innerHTML = out; }
    home(); }
  function home(){ var h = el('homeAuditor'); if(!h) return; var m = S.summary;
    h.innerHTML = '<div class="sa-home"><span><b>Signal Auditor</b> · ' + (S.signals.length ? S.signals.length + ' signal(s) logged' + (m ? ', ' + m.closed + ' closed' + (m.tp1 && m.tp1.n ? ', average ' + (m.tp1.avg_R > 0 ? '+' : '') + n(m.tp1.avg_R, 2) + 'R' : '') : ', not scored yet') : 'check a signal provider against real prices') + '</span><button class="btn-outline" type="button" data-sago="1">Open</button></div>'; }
  document.addEventListener('click', function(e){ var t = e.target && e.target.closest ? e.target.closest('[data-saadd],[data-sascore],[data-sadel],[data-sarisk],[data-saset],[data-sago]') : null; if(!t) return;
    if(t.hasAttribute('data-saadd')) add(); else if(t.hasAttribute('data-sascore')) scoreAll(); else if(t.hasAttribute('data-sadel')) del(t.getAttribute('data-sadel')); else if(t.hasAttribute('data-sarisk')) risk();
    else if(t.hasAttribute('data-sago')) window.navigate('auditor'); else { window.navigate('settings'); try{ window.switchSettings && window.switchSettings('data'); }catch(x){} } });
  function onShow(){ draw(); }
  var prevAfter = window.__omegaAfterNav;
  window.__omegaAfterNav = function(p){ try{ if(typeof prevAfter === 'function') prevAfter(p); }catch(e){} if(p === 'command') setTimeout(home, 30); };
  function boot(){ home(); if(el('page-auditor') && el('page-auditor').classList.contains('active')) draw(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(boot, 0); }); else setTimeout(boot, 0);
  window.OMEGA_AUDITOR = { onShow:onShow, draw:draw, add:add, scoreAll:scoreAll, del:del, canDelete:canDelete, risk:risk, state:function(){ return S; } };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.119 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.119 ' + sep + ' build ' + o + ' UTC', 'v6.5.120 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.120 · build' in s and 'v6.5.119 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
