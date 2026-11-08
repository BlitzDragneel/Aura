// v6.5.115: the declutter on every other kept page (one "About this page", secondary sections folded and closed, primary
// information open, no duplicate headers) and phone-safe badges (TD counter and clock chips on one line, evidence chips as blocks).
// usage: HARNESS=tools node s115_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
ok(/v6\.5\.1(1[5-9]|[2-9]\d) · build/.test(html), 'build v6.5.115 or later');
const PAGES = { rguard:['rguardBody', 'truthRgBody', 'reviewBody'], mread:['dplanBody', 'evBody', 'mreadBody'], intel:['clockBody', 'intelGrid', 'intelStatus'], flow:['flowMsg'], radar:['radarGrid', 'radarStatus'],
  journal:[], posdesk:['posdeskBody'], futures:['futLevTruth', 'perpAccount'], growth:['growthEmpty'], brain:['brainDash', 'rzOut', 'predictBody'].slice(0, 1), auto:['autoDeck'], settings:['setTrading'] };
const FOLDS = { intel:5, flow:2, radar:4, brain:3, auto:4, growth:1, settings:1 };
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(); const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue(); if(M.handle(r)) return;
    return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(() => localStorage.setItem('omega_tutorial_v1', '{"done":1}'));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
  for(const [p, prim] of Object.entries(PAGES)){ await pg.evaluate(x => navigate(x), p); await pg.waitForTimeout(900);
    const r = await pg.evaluate(([p, prim]) => { const e = document.getElementById('page-' + p), ab = e.querySelectorAll('details.om-about'), f = e.querySelectorAll('details.hv-sec');
      return { about:ab.length, aboutClosed:ab.length === 1 && !ab[0].open, aboutText:ab[0] ? ab[0].textContent.length : 0, folds:f.length, closed:Array.from(f).every(d => !d.open),
        prim:prim.filter(id => { const x = document.getElementById(id); return !x || x.closest('details:not([open])'); }),
        titles:Array.from(e.querySelectorAll('.page-title, .creed-banner-title')).filter(t => t.offsetHeight > 0 && !t.closest('details:not([open])')).length, subs:Array.from(e.querySelectorAll('.page-sub')).filter(t => t.offsetHeight > 0 && !t.closest('details:not([open])')).length }; }, [p, prim]);
    ok(r.about === 1 && r.aboutClosed && r.aboutText > 80 && r.folds === (FOLDS[p] || 0) && r.closed && !r.prim.length && r.titles <= 1 && r.subs === 0,
      p + ': one closed "About this page"; ' + (FOLDS[p] || 0) + ' secondary section(s) folded and closed; primary information open; one title, no duplicate subtitle', r); }
  await pg.evaluate(() => navigate('futures')); await pg.waitForTimeout(500);
  ok(await pg.evaluate(() => { const w = document.getElementById('futLevTruth'); return w.offsetHeight > 100 && /Leverage/.test(w.innerText); }), 'Futures: the leverage warning stays visible');
  await pg.evaluate(() => navigate('intel')); await pg.waitForTimeout(500); await pg.click('#page-intel details.hv-sec > summary');
  ok(await pg.evaluate(() => { const d = document.querySelector('#page-intel details.hv-sec'); return d.open && d.innerText.length > 40; }), 'a folded section opens with a tap and shows its content');
  await pg.evaluate(() => navigate('settings')); await pg.waitForTimeout(500);
  ok(await pg.evaluate(() => { const a = document.querySelector('#page-settings details.hv-sec'), body = document.querySelector('.settings-page-body'); return !!a && /webhook/i.test(a.textContent) && !!(body.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING); }),
    'Settings: signal webhooks and alerts folded below the preferences');
  await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2000);
  const bd = await pg.evaluate(() => { const td = document.querySelector('.ost-td'), ck = document.querySelector('.omega-clock .ck-sess'), ch = document.querySelector('#climaxSigBody .es-chip');
    const one = e => !e || e.getClientRects().length === 1; return { td:one(td) && (!td || getComputedStyle(td).whiteSpace === 'nowrap'), ck:one(ck), chip:!ch || (getComputedStyle(ch).display === 'inline-block' && ch.getClientRects().length === 1), wide:document.documentElement.scrollWidth > window.innerWidth + 1 }; });
  ok(bd.td && bd.ck && bd.chip && !bd.wide, 'phone: TD counter and clock chip on one line, evidence chips as one block each, no sideways overflow', bd);
  ok(!errs.length, 'no page errors', errs);
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
