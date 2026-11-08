// v6.5.113 + v6.5.114: Heaven theme (default, one-time switch, other choices kept, light charts, readable contrast), the
// About OMEGA page (menu, Settings button, every section, evidence numbers), and the declutter (Home folds, Charts scan fold,
// evidence clamps that keep the text in the page, one "About this page" per main page). Server mocked (tools/livemock.js).
// usage: HARNESS=tools node s113_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const T114 = /v6\.5\.1(1[4-9]|[2-9]\d) · build/.test(html);
ok(/v6\.5\.1(1[3-9]|[2-9]\d) · build/.test(html), 'build v6.5.113 or later');
ok(/<option value="heaven" selected>Heaven \(default\)<\/option>\s*<option value="neonglow">Neon Glow<\/option>\s*<option value="dark">Dark \(classic\)<\/option>/.test(html), 'Heaven first and selected; Neon Glow and Dark still offered');
ok(!/<link[^>]+href="https:\/\/(?!fonts\.googleapis\.com)[^"]+"[^>]*stylesheet/.test(html) && (html.match(/<script src="https:/g) || []).length === 1, 'no new CDN: one external script (the chart library), no new stylesheet host');
function L(h){ const c = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(x => x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
function cr(a, b){ const x = L(a), y = L(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
function hex(rgb){ const m = rgb.match(/\d+/g); return '#' + m.slice(0, 3).map(n => (+n).toString(16).padStart(2, '0')).join(''); }
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(prep){ const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue(); if(M.handle(r)) return;
      return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, prep || null);
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); return { ctx, pg, errs }; }
  const th = pg => pg.evaluate(() => ({ t:document.documentElement.getAttribute('data-theme'), sel:document.getElementById('setTheme').value, flag:localStorage.getItem('omega_heaven113') }));
  // fresh browser
  let { ctx, pg, errs } = await open();
  const f = await pg.evaluate(() => { const cs = getComputedStyle(document.body), card = document.querySelector('#page-command .card'), h = getComputedStyle(document.querySelector('.mobile-header') || document.body);
    return { t:document.documentElement.getAttribute('data-theme'), text:cs.color, card:card ? getComputedStyle(card).backgroundColor : '', dim:getComputedStyle(document.documentElement).getPropertyValue('--text-dim').trim(), gold:getComputedStyle(document.documentElement).getPropertyValue('--gold').trim(), head:h.backgroundColor, meta:document.querySelector('meta[name="theme-color"]').content }; });
  ok(f.t === 'heaven' && /255, 255, 255/.test(f.card) && /^#F[67]F8FC$/.test(f.meta), 'fresh browser: Heaven on, white cards, light browser bar', f);
  ok(cr(hex(f.text), '#FFFFFF') >= 7 && cr(f.dim, '#FFFFFF') >= 4.5 && cr(f.dim, '#F3F5FA') >= 4.5 && cr(f.gold, '#FFFFFF') >= 4.5, 'contrast (WCAG AA): text, secondary text and the accent on white and pearl', { text:cr(hex(f.text), '#FFFFFF'), dim:cr(f.dim, '#FFFFFF'), gold:cr(f.gold, '#FFFFFF') });
  const ch = await pg.evaluate(() => { const c = (window.OMEGA_CHARTUX ? window.OMEGA_CHARTUX.charts() : [])[0]; if(!c && !window.LightweightCharts) return { none:true }; const host = document.createElement('div'); host.style.cssText = 'width:300px;height:200px'; document.body.appendChild(host);
    const k = window.LightweightCharts.createChart(host, { layout:{ background:{ color:'#0A0D12' } } }); return { bg:k.options().layout.background.color }; });
  ok(ch.none || ch.bg === '#FFFFFF', 'charts made in Heaven get a white background', ch);
  await pg.evaluate(() => navigate('about')); await pg.waitForTimeout(600);
  const ab = await pg.evaluate(() => { const p = document.getElementById('page-about'); return { act:p.classList.contains('active'), n:p.querySelectorAll('details.ab-sec').length, open:p.querySelectorAll('details.ab-sec[open]').length,
    sums:Array.from(p.querySelectorAll('details.ab-sec>summary')).map(s => s.textContent), all:p.textContent, link:!!p.querySelector('a[href="https://omega-board.onrender.com"]'), ver:document.getElementById('aboutVersion').textContent,
    menu:!!document.querySelector('.sidebar-menu li[data-page="about"]'), set:!!document.getElementById('setAboutBtn') }; });
  ok(ab.act && ab.n === 10 && ab.open === 0 && ab.menu && ab.set && ab.link && /v6\.5\.1\d\d/.test(ab.ver), 'About OMEGA: 10 dropdown sections, closed; reachable from the menu (More) and Settings; progress board linked', { n:ab.n, sums:ab.sums });
  ok(['What OMEGA is', 'Every page', 'Signals, grades', 'The bots', 'Data sources', 'Live API', 'Academy', 'Risk and leverage', 'Privacy and backups', 'progress board'].every(k => ab.sums.some(s => s.indexOf(k) > -1)), 'sections: what it is, pages, signals, bots, data, Live API, Academy, risk, privacy, board');
  ok(/324 untouched coins/.test(ab.all) && /t 4\.54/.test(ab.all) && /49% of the time against 50%/.test(ab.all) && /−0\.118R/.test(ab.all) && /2× already liquidates/.test(ab.all) && /40× liquidates about 60%/.test(ab.all) &&
    /Swissquote/.test(ab.all) && /Yahoo/.test(ab.all) && /Deribit/.test(ab.all) && /Twelve Data/.test(ab.all) && /OKX/.test(ab.all) && /laptop Station/.test(ab.all) && /never written into a backup/.test(ab.all) && /Grade C/.test(ab.all),
    'the evidence: climax A on 324 coins, panic B t 4.54, CREED coin flip 49% vs 50% and −0.118R, leverage (2× liquidates, 40× ~60%), every data source, the Station, token never in backups');
  await pg.click('#page-about details.ab-sec:nth-child(3) > summary'); await pg.waitForTimeout(200);
  ok(await pg.evaluate(() => document.querySelector('#page-about details.ab-sec:nth-child(3)').open && document.querySelector('#page-about details.ab-sec:nth-child(3)').innerText.length > 500), 'a section opens with a tap');
  if(T114){
    await pg.evaluate(() => navigate('command')); await pg.waitForTimeout(800);
    const hm = await pg.evaluate(() => { const p = document.getElementById('page-command'), f = Array.from(p.querySelectorAll('details.cmd-card'));
      return { n:f.length, open:f.filter(d => d.open).map(d => d.querySelector('h3').textContent), first:Array.from(p.children).filter(e => e.offsetHeight > 0).slice(0, 3).map(e => e.id || e.className), about:p.querySelectorAll('details.om-about').length, prod:!!p.querySelector('details.om-about .cmd-products') }; });
    ok(hm.n === 8 && hm.open.length === 2 && hm.about === 1 && hm.prod && hm.first[1] === 'cmdFive', 'Home: hero, then the verdict; 8 detail cards as dropdowns (2 open); the explainer cards in "About this page"', hm);
    await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(1500);
    const an = await pg.evaluate(() => { const p = document.getElementById('page-analysis'), w = p.querySelector('details.wl-room'); return { wl:!!w && !w.open, cards:document.querySelectorAll('#wlGrid .wl-card, #wlGrid > *').length, last:!!p.querySelector('#truthBody'), about:p.querySelectorAll('details.om-about').length }; });
    ok(an.wl && an.last && an.about === 1, 'Charts: the scan of every market is a closed dropdown; one "About this page"', an);
    await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2500);
    const sg = await pg.evaluate(() => { const c = document.getElementById('climaxSigBody'); const k = c.firstElementChild; return { cl:c.classList.contains('hv-clamp'), h:k.offsetHeight, full:k.scrollHeight, txt:c.innerText.length, about:document.querySelectorAll('#page-osig details.om-about').length }; });
    ok(sg.cl && sg.h <= 440 && sg.full > sg.h && sg.txt > 800 && sg.about === 1, 'Signals: the climax card shows its first screen, the full evidence text stays in the page', sg);
    await pg.evaluate(() => { const c = document.getElementById('climaxSigBody'), r = c.getBoundingClientRect(); c.scrollIntoView(); });
    await pg.waitForTimeout(200); const box = await pg.evaluate(() => { const r = document.getElementById('climaxSigBody').getBoundingClientRect(); return { x:r.left + r.width / 2, y:r.bottom - 20 }; });
    await pg.mouse.click(box.x, box.y); await pg.waitForTimeout(200);
    ok(await pg.evaluate(() => { const c = document.getElementById('climaxSigBody'); return c.classList.contains('hv-open') && c.offsetHeight >= c.scrollHeight - 2; }), 'tapping "Show the full evidence" opens the whole card');
    await pg.evaluate(() => navigate('bot')); await pg.waitForTimeout(1200);
    const bt = await pg.evaluate(() => { const p = document.getElementById('page-bot'); return { hdr:Array.from(p.querySelectorAll('.page-title')).filter(e => e.offsetHeight > 0 && /Trading Bots/.test(e.textContent)).length, paper:p.querySelectorAll('.paper-banner').length, fold:!!p.querySelector('details.hv-fold #omegaBotCard'), about:p.querySelectorAll('details.om-about').length }; });
    ok(bt.hdr === 0 && bt.paper === 1 && bt.fold && bt.about === 1, 'Bots: no duplicate header, one paper notice, in-app bot details folded, "About this page"', bt);
  }
  ok(!errs.length, 'no page errors in Heaven', errs); await ctx.close();
  // a browser on Neon Glow moves to Heaven once; picking Neon Glow again sticks
  ({ ctx, pg, errs } = await open({ omega_settings_v3:JSON.stringify({ setTheme:'neonglow' }), omega_neon108:'1' }));
  ok((await th(pg)).t === 'heaven', 'saved Neon Glow: moved to Heaven once', await th(pg));
  await pg.evaluate(() => { const t = document.getElementById('setTheme'); t.value = 'neonglow'; t.dispatchEvent(new Event('change')); }); await pg.reload(); await pg.waitForTimeout(2500);
  ok((await th(pg)).t === 'neonglow', 'choosing Neon Glow again after the switch sticks', await th(pg)); await ctx.close();
  ({ ctx, pg, errs } = await open({ omega_settings_v3:JSON.stringify({ setTheme:'dark' }) }));
  ok((await th(pg)).t === 'heaven', 'saved Dark (old default, never switched): moved to Heaven', await th(pg)); await ctx.close();
  ({ ctx, pg, errs } = await open({ omega_settings_v3:JSON.stringify({ setTheme:'ocean' }), omega_neon108:'1' }));
  ok((await th(pg)).t === 'ocean', 'any other chosen theme (Ocean) is kept', await th(pg));
  await pg.evaluate(() => { document.getElementById('setTheme').value = 'dark'; document.getElementById('setTheme').dispatchEvent(new Event('change')); }); await pg.reload(); await pg.waitForTimeout(2500);
  ok((await th(pg)).t === null && !errs.length, 'Dark (classic) still selectable and sticks; no page errors', await th(pg)); await ctx.close();
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
