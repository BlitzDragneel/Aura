"""(+ trade tickets on Today, 28 Oct) Turns the 25 Oct Prime (omega-prime.html, md5 85d94f81…) into the Grade B version: adds prime_panic.js after the core and
applies the verdict, ledger, Signals and style changes (the same ones made in prime_post.js and prime_shell.html, which
build_prime.py uses for a full rebuild). Usage: python3 patch_prime_panic.py old.html new.html"""
import sys
src, dst = sys.argv[1], sys.argv[2]
h = open(src, encoding='utf-8').read()
po, pn = open('prime_post.js.orig', encoding='utf-8').read(), open('prime_post.js', encoding='utf-8').read()
panic = open('prime_panic.js', encoding='utf-8').read()
tickets = open('prime_tickets.js', encoding='utf-8').read()
assert h.count(po.strip()) == 1, 'not the expected Prime'
h = h.replace(po.strip(), pn.strip() + '\n' + panic.strip() + '\n' + tickets.strip())
for a, b in [('<p class="pg-sub">Grade A: the one rule that passed a fair test. Grade C: the Daily Plan, unproven and followed on paper.</p><div id="climaxBody"></div><div id="dplanBody"></div>',
              '<p class="pg-sub">Grade A: passed a fair test (climax). Grade B: passed a fair test, not yet confirmed (panic bounce). Grade C: the Daily Plan, unproven and followed on paper.</p><div id="climaxBody"></div><div id="panicBody"></div><div id="dplanBody"></div>'),
             ('<section class="page" id="page-today"><div id="todayBody"></div><div id="evBody"></div></section>', '<section class="page" id="page-today"><div id="todayBody"></div><div id="ticketsBody"></div><div id="evBody"></div></section>'),
             ('.verdict.a .v{color:#ffe08a;}', '.verdict.a .v{color:#ffe08a;} .verdict.b .v{color:#f6c58a;}\n.pgauge{width:100%;max-width:420px;height:auto;display:block;margin:2px 0 10px;}')]:
    assert h.count(a) == 1; h = h.replace(a, b)
open(dst, 'w', encoding='utf-8').write(h); print(dst, len(h), 'bytes')
