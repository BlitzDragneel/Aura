// v6.5.110: OMEGA Academy (contract omega/academy/CONTRACT.md) and the first-run tutorial. The server is mocked with route()
// using the contract's shapes: GET /academy/catalog, POST /academy/unlock, GET /academy/lesson/{id} (X-Academy-Token).
// usage: node s110_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
ok(/v6\.5\.1(1\d|[2-9]\d) · build/.test(html), 'build v6.5.110 or later');
const m = /<script type="application\/json" id="omegaAcademyData">([\s\S]*?)<\/script>/.exec(html); let D = null; try{ D = JSON.parse(m[1]); }catch(e){}
const flat = D ? [].concat(...D.modules.map(x => x.lessons)) : [];
ok(D && flat.length && flat.every(l => l.free ? typeof l.body_md === 'string' : !('body_md' in l) && !('quiz' in l)), 'embedded data: free lessons have bodies, premium lessons have none', D && flat.filter(l => !l.free && l.body_md).map(l => l.id));
ok(D && D.pricing && 'checkout_url' in D.pricing, 'pricing embedded');
const PREM = 'PREMIUM-SECRET-TEXT-' + Date.now();
const CAT = { title:'OMEGA Academy — Test', version:'1.0', disclaimer:'Education, not advice.', pricing:{ launch_price:49, regular_price:97, checkout_url:'' }, modules:[
  { id:'m01', title:'Start here', summary:'S', free:true, lessons:[
    { id:'m01-l01', title:'Welcome', minutes:5, free:true, key_points:['Risk first'], quiz:[{ q:'Two plus two?', options:['3', '4'], answer:1, why:'Arithmetic.' }],
      body_md:'# Hello\n\nSome **bold** and *it* and `code`.\n\n- one\n- two\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n<img src=x onerror="window.__xss=1"> <script>window.__xss=2</script> [bad](javascript:window.__xss=3) [good](https://example.com)' }] },
  { id:'m03', title:'Reading charts', summary:'C', free:false, lessons:[{ id:'m03-l01', title:'Preview', minutes:4, free:true, body_md:'Preview text', key_points:[], quiz:[] }, { id:'m03-l02', title:'Locked one', minutes:6, free:false }] }] };
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(opts){ opts = opts || {}; const ctx = await b.newContext({ viewport:{ width:412, height:915 } }), seen = { unlock:[], lesson:[] };
    await ctx.route('**/*', async r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue();
      const j = (st, x) => r.fulfill({ status:st, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
      if(/\/academy\//.test(u.pathname)){ if(opts.offline) return r.abort();
        if(u.pathname === '/academy/catalog') return j(200, opts.checkout ? Object.assign({}, CAT, { pricing:Object.assign({}, CAT.pricing, { checkout_url:opts.checkout }) }) : CAT);
        if(u.pathname === '/academy/unlock'){ const body = JSON.parse(r.request().postData() || '{}'); seen.unlock.push(body); return body.license_key === 'GOOD-KEY' ? j(200, { ok:true, token:'tok123', via:'key list' }) : j(403, { detail:'this license key was not found' }); }
        const lm = /^\/academy\/lesson\/(.+)$/.exec(u.pathname); if(lm){ const t = r.request().headers()['x-academy-token']; seen.lesson.push({ id:lm[1], t });
          return t === 'tok123' ? j(200, { module:'m03', id:lm[1], title:'Locked one', body_md:PREM, key_points:['kp'], quiz:[] }) : j(402, { detail:'this lesson is part of the full course' }); } }
      return j(200, []); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    if(opts.prep){ await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(opts.prep); }
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(opts.wait || 4000); return { ctx, pg, errs, seen }; }
  // 1. first run: the tutorial card shows on Home, steps work, skip stores the flag; no premium text in the page
  let { ctx, pg, errs, seen } = await open({ prep:() => localStorage.clear() });
  const t1 = await pg.evaluate(() => { const c = document.getElementById('omegaTour'); return { on:!!c, inHome:!!(c && c.closest('#page-command')), txt:c ? c.innerText : '' }; });
  ok(t1.on && t1.inHome && /step 1 of 6/i.test(t1.txt), 'first run: the tutorial (6 steps) opens at the top of Home', t1);
  await pg.click('#omegaTour [data-t="next"]'); await pg.click('#omegaTour [data-t="show"]'); await pg.waitForTimeout(500);
  const t2 = await pg.evaluate(() => ({ step:document.getElementById('omegaTour').innerText.slice(0, 60), active:document.querySelector('.page.active').id, inPage:!!document.querySelector('.page.active #omegaTour') }));
  ok(/step 2/i.test(t2.step) && t2.active === 'page-analysis' && t2.inPage, '"Show me" opens the step’s page (Charts) and the card follows', t2);
  await pg.click('#omegaTour [data-t="skip"]'); await pg.waitForTimeout(200);
  ok(await pg.evaluate(() => !document.getElementById('omegaTour') && !!JSON.parse(localStorage.getItem('omega_tutorial_v1') || 'null')), 'skip closes it and remembers');
  // 2. Academy from the bottom bar: catalog from the (mocked) server, coming-soon price
  const nav = await pg.evaluate(() => Array.from(document.querySelectorAll('.omega-bottomnav button span')).map(s => s.textContent));
  ok(JSON.stringify(nav) === JSON.stringify(['Home', 'Charts', 'Signals', 'CREED', 'Bots', 'Academy', 'More']), 'bottom bar: Home / Charts / Signals / CREED / Bots / Academy / More', nav);
  await pg.evaluate(() => document.querySelector('.omega-bottomnav button[data-go="academy"]').click()); await pg.waitForTimeout(1500);   // DOM click: the offline self-test banner (no chart CDN here) covers the bar
  let a = await pg.evaluate(() => ({ t:document.getElementById('acadBody').innerText, src:window.OMEGA_ACADEMY.state().src, buy:(document.querySelector('.ac-buy') || {}).textContent, dis:(document.querySelector('.ac-buy') || {}).disabled }));
  ok(a.src === 'server' && /OMEGA Academy — Test/i.test(a.t) && /0 of 3 lessons/.test(a.t) && /Disclaimer|Please read/i.test(a.t), 'Academy lists modules with progress from the server catalog', a.t.slice(0, 300));
  ok(/Coming soon — launch price \$49, regular \$97/.test(a.buy) && a.dis === true, 'empty checkout_url: "Coming soon — launch price $49, regular $97"', a.buy);
  // 3. lesson reader: safe markdown, key points, quiz with explanation, progress
  await pg.click('[data-ac-open="m01-l01"]'); await pg.waitForTimeout(300);
  const r = await pg.evaluate(() => { const md = document.querySelector('.ac-md'); return { h:md.innerHTML, xss:window.__xss, img:md.querySelectorAll('img,script').length, links:Array.from(md.querySelectorAll('a')).map(x => x.getAttribute('href')),
    kp:(document.querySelector('.ac-kp') || {}).innerText, tbl:md.querySelectorAll('table td').length, li:md.querySelectorAll('ul li').length }; });
  ok(!r.xss && r.img === 0 && /&lt;img/.test(r.h) && JSON.stringify(r.links) === JSON.stringify(['https://example.com']) && /<b>bold<\/b>/.test(r.h) && /<code>code<\/code>/.test(r.h) && r.tbl === 2 && r.li === 2,
    'markdown: escaped first (no tags, no javascript: link), then headings/bold/code/lists/tables/https links', r);
  ok(/Risk first/.test(r.kp), 'key points shown');
  await pg.click('input[name="acq0"][value="0"]'); await pg.click('[data-ac="check"]');
  let q = await pg.evaluate(() => ({ why:document.querySelector('.ac-why').innerText, p:window.OMEGA_ACADEMY.progress() }));
  ok(/Not quite/.test(q.why) && /Arithmetic/.test(q.why) && q.p.quiz['m01-l01'].score === 0, 'quiz: wrong answer explained, score saved', q);
  await pg.click('input[name="acq0"][value="1"]'); await pg.click('[data-ac="check"]'); await pg.click('[data-ac="done"]');
  q = await pg.evaluate(() => JSON.parse(localStorage.getItem('omega_academy_v1')));
  ok(q.quiz['m01-l01'].score === 1 && q.done['m01-l01'] && q.last === 'm01-l01', 'progress saved in omega_academy_v1 (quiz, done, last)', q);
  // 4. premium: locked, wrong key refused, right key unlocks, lesson fetched with the token header
  await pg.click('[data-ac="back"]'); await pg.click('[data-ac-open="m03-l02"]'); await pg.waitForTimeout(300);
  ok(/part of the full course/.test(await pg.evaluate(() => document.getElementById('acadBody').innerText)) && !seen.lesson.length, 'premium lesson locked without a token (nothing fetched)');
  await pg.click('[data-ac="key"]'); await pg.fill('#acKeyInput', 'BAD'); await pg.click('[data-ac="unlock"]'); await pg.waitForTimeout(500);
  ok(/this license key was not found/.test(await pg.evaluate(() => document.getElementById('acadBody').innerText)), 'wrong key: the server’s reason is shown');
  await pg.click('[data-ac="key"]').catch(() => {}); if(!await pg.$('#acKeyInput')) await pg.click('[data-ac="key"]');
  await pg.fill('#acKeyInput', 'GOOD-KEY'); await pg.click('[data-ac="unlock"]'); await pg.waitForTimeout(800);
  const u = await pg.evaluate(() => ({ t:document.getElementById('acadBody').innerText, tok:JSON.parse(localStorage.getItem('omega_academy_v1')).token }));
  ok(u.tok === 'tok123' && seen.unlock.some(x => x.license_key === 'GOOD-KEY') && new RegExp(PREM).test(u.t) && seen.lesson.some(x => x.id === 'm03-l02' && x.t === 'tok123'),
    'right key: POST /academy/unlock → token kept; the lesson comes from /academy/lesson/{id} with X-Academy-Token', { tok:u.tok, lesson:seen.lesson });
  ok(!new RegExp(PREM).test(await pg.evaluate(() => document.documentElement.outerHTML.replace(document.getElementById('acadBody').outerHTML, ''))) && !/PREMIUM-SECRET/.test(html), 'premium text lives only in the reader, never in the file');
  ok(!errs.length, 'no page errors', errs); await ctx.close();
  // 5. checkout link when the product exists; settings server URL; tutorial reopen from Settings
  ({ ctx, pg, errs } = await open({ checkout:'https://maro.gumroad.com/l/omega', prep:() => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); } }));
  ok(!(await pg.$('#omegaTour')), 'tutorial not shown again after it was finished');
  await pg.evaluate(() => navigate('academy')); await pg.waitForTimeout(1500);
  const lk = await pg.evaluate(() => { const x = document.querySelector('a.ac-buy'); return x ? { href:x.href, t:x.textContent, rel:x.rel } : null; });
  ok(lk && lk.href === 'https://maro.gumroad.com/l/omega' && /Unlock the full course — \$49/.test(lk.t) && /noopener/.test(lk.rel), '"Unlock the full course" opens the checkout URL', lk);
  await pg.evaluate(() => { navigate('settings'); switchSettings('data'); }); await pg.waitForTimeout(300);
  const dv = await pg.inputValue('#acadServerInput');
  await pg.fill('#acadServerInput', 'javascript:alert(1)'); await pg.click('#acadServerSave');
  const bad = await pg.evaluate(() => ({ m:document.getElementById('acadServerMsg').textContent, s:localStorage.getItem('omega_academy_server') }));
  await pg.fill('#acadServerInput', 'https://example.org/'); await pg.click('#acadServerSave');
  const good = await pg.evaluate(() => ({ s:localStorage.getItem('omega_academy_server'), u:window.OMEGA_ACADEMY.server() }));
  ok(dv === 'https://omega-live-api.onrender.com' && /Not saved/.test(bad.m) && !bad.s && good.s === 'https://example.org' && good.u === 'https://example.org', 'Settings > Data: server URL defaults to the Live API, only https is accepted', { dv, bad, good });
  await pg.click('#acadTourOpen'); await pg.waitForTimeout(300);
  ok(await pg.evaluate(() => !!document.querySelector('#page-command.active #omegaTour')), 'Settings reopens the tutorial on Home');
  await pg.evaluate(() => window.OMEGA_ACADEMY.tour.close('test')); await ctx.close();
  // 6. offline: bundled free lessons
  ({ ctx, pg, errs } = await open({ offline:true, prep:() => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); } }));
  await pg.evaluate(() => navigate('academy')); await pg.waitForTimeout(2500);
  const off = await pg.evaluate(() => ({ src:window.OMEGA_ACADEMY.state().src, t:document.getElementById('acadBody').innerText, n:document.querySelectorAll('[data-ac-open]').length }));
  ok(off.src === 'bundled' && /Built-in free lessons/.test(off.t) && off.n >= 1, 'offline: the free lessons built into the app are shown', { src:off.src, n:off.n });
  const firstFree = flat.find(l => l.free); await pg.click('[data-ac-open="' + firstFree.id + '"]'); await pg.waitForTimeout(300);
  ok(await pg.evaluate(() => (document.querySelector('.ac-md') || {}).innerText.length > 50), 'offline: a bundled lesson opens and reads');
  ok(!errs.length, 'no page errors offline', errs); await ctx.close();
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
