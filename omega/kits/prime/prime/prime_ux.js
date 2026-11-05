<script>/* ═══ PRIME UX — data health, the rule book by grade, back button (5 Nov 2026) ═══
   Display only: reads the watches' state, never changes a rule, a threshold, a ticket or a trade.
   1. Data health: if the hourly scans could not reach the market, Today says so instead of "Stand aside" (which would claim
      that the rules were checked), and the "data live" chip appears only when the data check really read a feed.
   2. The rule book: every rule Prime knows, grouped by grade (A, B, C), one line each with its live state. Rules that the
      research adds to edges/approved.json are embedded at build time (window.PRIME_EDGES, by patch_prime_ux.py) and appear
      here and in Evidence under their grade, without new pages or cards. Prime watches only the rules it has code for; the
      others say where their signals come from.
   3. Back button: each page gets its own address (#today, #signals…), so Android's back returns to the previous page. */
(function(){
  'use strict';
  var H = 3600e3, EDGES = Array.isArray(window.PRIME_EDGES) ? window.PRIME_EDGES : [];
  var BUILTIN = { climax:1, climax_a:1, climax_reversal:1, panic_h1:1, panic_h3:1, h1:1, h3:1, dplan:1, daily_plan:1 };
  function spec(ids){ for(var i = 0; i < EDGES.length; i++){ if(EDGES[i] && ids.indexOf(String(EDGES[i].id).toLowerCase()) >= 0) return EDGES[i]; } return null; }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function job(id){ var O = window.OMEGA_OPERATOR, s = O && O.state().jobs; return (s && s[id]) || {}; }
  function hhmm(ms){ return new Date(ms).toISOString().slice(11, 16) + ' UTC'; }
  // ── 1. data health ──
  function failed(id){ var s = job(id); return !!(s.last && /^Problem/.test(s.result || '')); }
  function noData(){ return (typeof navigator !== 'undefined' && navigator.onLine === false) || (failed('climax') && failed('panic')); }
  function unchecked(){ return !job('climax').last && !job('panic').last; }
  function checked(){ var a = job('climax'), b = job('panic'), t = Math.max(a.last || 0, b.last || 0);
    if(!t) return 'signals not checked yet'; if(noData()) return 'no market data since ' + hhmm(t); return 'signals checked ' + hhmm(t); }
  function ordersNote(){ return noData() ? '<p class="ev-warn" style="margin:0 0 10px">No market data: “No order to place” below means only that no signal was found before the connection failed. Orders already placed still follow their sell times.</p>' : ''; }
  // ── 2. the rule book ──
  var GRADE = { A:'Grade A · passed a fair test', B:'Grade B · passed, not yet confirmed', C:'Grade C · unproven, paper only' };
  function builtins(){ var C = window.OMEGA_CLIMAX ? window.OMEGA_CLIMAX.state().trades.filter(function(t){ return t.status === 'open'; }).length : 0;
    var P = window.OMEGA_PANIC ? window.OMEGA_PANIC.live() : [], h1 = P.filter(function(t){ return t.rule === 'H1'; }).length, h3 = P.length - h1;
    var D = window.OMEGA_DPLAN && window.OMEGA_DPLAN.state().S;
    return [{ grade:'A', name:'Climax reversal', plan:'round 16', where:'climaxBody', live:C, tickets:true, spec:spec(['climax', 'climax_a', 'climax_reversal']) },
      { grade:'B', name:'Panic bounce H1', plan:'E22, E25', where:'panicBody', live:h1, tickets:true, spec:spec(['panic_h1', 'h1']) },
      { grade:'B', name:'Market-wide panic H3', plan:'E22, E25', where:'panicBody', live:h3, tickets:true, spec:spec(['panic_h3', 'h3']) },
      { grade:'C', name:'Daily Plan', plan:'E16', where:'dplanBody', live:null, tickets:false, note:D ? 'a plan per coin, followed on paper' : 'not read yet' }]; }
  function extras(){ return EDGES.filter(function(e){ return e && e.id && !BUILTIN[String(e.id).toLowerCase()] && /^[ABC]$/.test(e.grade); }); }
  function state(r){ if(r.live == null) return '<span class="rb-st">' + esc(r.note || '') + '</span>';
    if(noData()) return '<span class="rb-st off">no data</span>';
    return r.live ? '<span class="rb-st on">' + r.live + ' live</span>' : '<span class="rb-st">quiet</span>'; }
  function rulebook(){ var rows = builtins(), ex = extras(), h = '<div class="card rb"><h3 class="dp-h">The rule book</h3><p class="hint" style="margin:0 0 6px">Every rule Prime knows, by grade. Tickets come only from grades A and B.</p>';
    ['A', 'B', 'C'].forEach(function(g){ var R = rows.filter(function(r){ return r.grade === g; }), E = ex.filter(function(e){ return e.grade === g; }); if(!R.length && !E.length) return;
      h += '<div class="rb-g"><div class="rb-gh g' + g + '">' + GRADE[g] + '</div>';
      R.forEach(function(r){ h += '<a class="rb-row" href="#signals" data-rb="' + r.where + '"><b>' + esc(r.name) + '</b><span class="hint">' + esc(r.plan) + (r.tickets ? ' · tickets' : ' · no tickets') + (r.spec && r.spec.status ? ' · bots: ' + esc(r.spec.status) : '') + '</span>' + state(r) + '</a>'; });
      if(E.length) h += '<details class="rb-more"><summary>' + E.length + ' more tested rule' + (E.length === 1 ? '' : 's') + ' from the research (not watched in Prime yet)</summary>' + E.map(function(e){
          return '<div class="rb-row x"><b>' + esc(e.name || e.id) + '</b><span class="hint">' + esc([e.plan, e.tf, e.status, e.max_leverage ? 'max ' + e.max_leverage + '×' : ''].filter(Boolean).join(' · ')) + '</span><span class="rb-st">signals: Live API / bots</span></div>'; }).join('') + '</details>';
      h += '</div>'; });
    return h + (EDGES.length ? '<p class="hint" style="margin:6px 0 0">Research list embedded ' + esc(window.PRIME_EDGES_AT || '') + ' from edges/approved.json.</p>' : '') + '</div>'; }
  function renderRulebook(){ var b = document.getElementById('rulebookBody'); if(!b) return; b.innerHTML = rulebook();
    Array.prototype.forEach.call(b.querySelectorAll('[data-rb]'), function(a){ a.onclick = function(ev){ ev.preventDefault(); var t = document.getElementById(a.getAttribute('data-rb')); if(t) t.scrollIntoView({ behavior:'smooth', block:'start' }); }; }); }
  function evidenceExtras(){ var ex = extras(); if(!ex.length) return '';
    return '<div class="card"><h3 class="dp-h">Added by the research (edges/approved.json)</h3><ul class="ledger" style="list-style:none;padding:0">' + ex.map(function(e){
      return '<li><span class="tag pass">PASSED · ' + esc(e.grade) + '</span><b>' + esc(e.name || e.id) + '</b><br><span class="hint">' + esc([e.plan, e.tf, 'status ' + (e.status || 'paper'), e.max_leverage ? 'highest safe leverage ' + e.max_leverage + '×' : '', e.evidence].filter(Boolean).join(' · ')) + '</span></li>'; }).join('') + '</ul></div>'; }
  // ── 3. pages with their own address, for the back button ──
  window.addEventListener('popstate', function(){ var p = (location.hash || '#today').slice(1); if(document.getElementById('page-' + p) && window.PRIME_UI) window.PRIME_UI.show(p, true); });
  var css = document.createElement('style'); css.id = 'uxCss';
  css.textContent = '.rb-g{margin:8px 0 2px}.rb-gh{font:700 12px system-ui;letter-spacing:.04em;margin:0 0 2px}.rb-gh.gA{color:var(--bull)}.rb-gh.gB{color:var(--amber)}.rb-gh.gC{color:var(--text-dim)}' +
    '.rb-row{display:grid;grid-template-columns:1fr auto;gap:0 10px;align-items:center;min-height:44px;padding:6px 2px;border-bottom:1px solid var(--border);color:inherit;text-decoration:none}.rb-row .hint{grid-column:1}.rb-row b{grid-column:1;font-size:14.5px}.rb-row .rb-st{grid-column:2;grid-row:1/span 2}' +
    '.rb-st{font:600 12px system-ui;color:var(--text-dim);border:1px solid var(--border);border-radius:999px;padding:3px 9px;white-space:nowrap}.rb-st.on{color:#fff;background:var(--bull);border-color:var(--bull)}.rb-st.off{color:var(--bear);border-color:var(--bear)}' +
    '.rb-more summary{cursor:pointer;min-height:44px;display:flex;align-items:center;font-size:13.5px;color:var(--ink)}';
  document.head.appendChild(css);
  window.PRIME_UX = { noData:noData, ordersNote:ordersNote, unchecked:unchecked, checked:checked, rulebook:rulebook, renderRulebook:renderRulebook, evidenceExtras:evidenceExtras, extras:extras };
  if(window.PRIME_UI) window.PRIME_UI.show('today', true);
})();
</script>