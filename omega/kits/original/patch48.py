# OMEGA v6.5.48 — on top of v6.5.47. Two measurement faults in CREED's history replay, found on her 13–17 Oct exports.
#  1. CREED's as-taught walk moves the stop to breakeven INSIDE the setup object it is given (walkExit sets p.stop =
#     p.entry once price reaches +1R). Everything measured after it on the same object then used that moved stop:
#     "entered when shown" (rd), "a limit at the level" (limitAfterShown), the lens, and so the Avoid list and every
#     "as it could be taken" figure. For every setup that later reached +1R, the "when shown" trade got a stop AT the
#     entry: either dropped as untradeable (price below a long's "stop") or given a tiny risk, so costs became huge in R;
#     the limit test returned no fill at all (risk 0). The as-taught result itself was never affected. Fix: the original
#     stop is restored right after that walk. Replay version 9; figures from earlier replays are not used for "as it could
#     be taken" until each market is replayed again.
#  2. Replays made under different cost settings were added together. Her 17 Oct report: SOL and XRP (replayed after
#     the others) carry ~10x the costs per setup of the same setups on 13 Oct, with the same gross result. Each replay
#     now records the cost it used; a market is replayed again when the cost setting changes; and a crypto round-trip
#     cost above 0.5% gets a plain check next to the input (Binance's taker fee is about 0.1% a side).
import sys
f, out = sys.argv[1], sys.argv[2]; s = open(f, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, ('anchor count', n, count, old[:120]); s = s.replace(old, new)
# 1. restore the stop
rep("            var ex = C.walkExit(p, wpx, { beAtR:1 });   // CREED as taught;",
    "            var ex = C.walkExit(p, wpx, { beAtR:1 }); p.stop = lv.stop; p.beMoved = false;   // v6.5.48: that walk moves p's stop to breakeven; restored for every measure after it // CREED as taught;")
rep("    var out = { v:8, lens:", "    var out = { v:9, costKey:replayCostKey(sym, srcLab), lens:")
rep("|| (prev.v || 0) < 8; });   // v6.5.35:", "|| (prev.v || 0) < 9 || (prev.costKey || '') !== replayCostKey(sym, (sm && sm.src) || ''); });   // v6.5.48: version 9, or the cost setting changed // v6.5.35:")
# the cost key helper, next to nextReplayMarket
i = s.index("  function nextReplayMarket(){")
s = s[:i] + "  function replayCostKey(sym, src){ try{ var c = window.OMEGA_LAB.costIn(sym, src || '', 1); return isFinite(c) ? String(Math.round(c*1e7)/1e7) : ''; }catch(e){ return ''; } }   // v6.5.48: the cost (per unit of price) a replay used\n" + s[i:]
# as-taken figures only from v9 replays
rep("var x = ch[sym] || chs[sym]; if(!x || (x.v || 0) < 7) return; var dT = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection, tk = x.takeMarket || x.takeable;",
    "var x = ch[sym] || chs[sym]; if(!x || (x.v || 0) < 9) return; var dT = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection, tk = x.takeMarket || x.takeable;")
rep("    Object.keys(ch).forEach(function(k){ var x = ch[k]; if(!x || (x.v || 0) < 7) return; var d0 = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection;",
    "    Object.keys(ch).forEach(function(k){ var x = ch[k]; if(!x || (x.v || 0) < 9) return; var d0 = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection;")
rep("return x && (x.v || 0) >= 7 && Array.isArray(x.lens) && x.lens.length; }).sort();", "return x && (x.v || 0) >= 9 && Array.isArray(x.lens) && x.lens.length; }).sort();")
# 2b. cost input check
rep("    ['cryptoPct','forexPips','jpyPips','goldUsd'].forEach(function(k){ var i = el('mindCost_'+k), v = i ? parseFloat(i.value) : NaN; costs[k] = (isFinite(v) && v >= 0) ? v : null; });",
    "    ['cryptoPct','forexPips','jpyPips','goldUsd'].forEach(function(k){ var i = el('mindCost_'+k), v = i ? parseFloat(i.value) : NaN; costs[k] = (isFinite(v) && v >= 0) ? v : null; });\n"
    "    try{ var cw = el('mindCostWarn'); if(!cw){ var ci = el('mindCost_cryptoPct'); if(ci && ci.parentNode && ci.parentNode.parentNode){ cw = document.createElement('p'); cw.id = 'mindCostWarn'; cw.className = 'hint'; ci.parentNode.parentNode.appendChild(cw); } }   // v6.5.48\n"
    "      if(cw) cw.textContent = costs.cryptoPct != null && costs.cryptoPct > 0.5 ? 'Check: you entered ' + costs.cryptoPct + '% round trip for crypto. Binance\\u2019s taker fee is about 0.1% a side (0.2% round trip on spot, 0.1% on futures); ' + costs.cryptoPct + '% is ' + Math.round(costs.cryptoPct/0.1) + ' times the futures figure. It changes every backtest and replay, which run again with it.' : ''; }catch(eW){}")
# version label
import time
st = sys.argv[3] if len(sys.argv) > 3 else time.strftime('%Y-%m-%d %H:%M', time.gmtime())
for sep in ('\u00b7', '\\u00b7'):
    old = 'v6.5.47 ' + sep + ' build 2026-10-16 10:33 UTC'; assert s.count(old) >= 1, old; s = s.replace(old, 'v6.5.48 ' + sep + ' build ' + st + ' UTC')
open(out, 'w', encoding='utf-8').write(s); print('v6.5.48 written to', out)
