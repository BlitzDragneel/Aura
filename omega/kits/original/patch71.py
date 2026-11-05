"""v6.5.71: round 14 so far, honest CREED numbers, two research downloads.
- CREED history replay v10: setups shown on time (the only ones whose quoted entry could be taken) measured on their own,
  with breakeven-off and three-tier variants; they lead the CREED history card, the signal list's replay line and the
  scoreboard. Every market is replayed again.
- CREED Backtest: entry 'when shown' (default) or 'as taught' (acceptance close even when shown later; counts hindsight).
- Downloads: the round-14 final-test data (hourly perpetuals of untouched coins) and 15-minute CREED research data.
- Research record and built-in knowledge: round 14 so far and the CREED finding."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)

# ── CREED history replay v10 ──
rep("var out = { v:9, costKey:", "var out = { v:10, costKey:")
rep("(prev.v || 0) < 9 ||", "(prev.v || 0) < 10 ||")
rep("out.takeMarket = splitK('rd', 'cd'); out.takeLimit = splitK('rl', 'cl');",
    "out.takeMarket = splitK('rd', 'cd'); out.takeLimit = splitK('rl', 'cl');\n"
    "    // v6.5.71: shown on time = set up and shown on the same 15-minute close, so the quoted entry is a price a trader could take.\n"
    "    // The rest of \"as taught\" is shown later but priced at the earlier close (hindsight). On your 13 Oct replays: +0.015R a\n"
    "    // trade before costs over 2,497 on-time setups, against +0.47R for the hindsight headline.\n"
    "    var onT = trades.filter(function(x){ return x.lag === 0; });\n"
    "    out.onTime = { n:onT.length, share: trades.length ? onT.length/trades.length : null, all:sumK(onT, 'r', 'c'), early:sumK(onT.filter(function(x){ return x.t < out.cut; }), 'r', 'c'), late:sumK(onT.filter(function(x){ return x.t >= out.cut; }), 'r', 'c'),\n"
    "      beOff:sumK(onT, 'nb', 'c'), tiers:sumK(onT, 'tr', 'c'), reach1: onT.length ? onT.filter(function(x){ return x.tr != null && x.tr > -0.999; }).length/onT.length : null };")
rep("Object.keys(ch).forEach(function(k){ var x = ch[k]; if(!x || (x.v || 0) < 9) return; var d0 = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection;",
    "var on = { mk:0, n:0, R:0, net:0, ln:0, lnet:0, nbN:0, nb:0, trN:0, tr:0 };\n"
    "    Object.keys(ch).forEach(function(k){ var x = ch[k]; if(!x || (x.v || 0) < 9) return; var oT = x.onTime; if(oT && oT.all && oT.all.n){ on.mk++; on.n += oT.all.n; on.R += oT.all.R; on.net += oT.all.net; if(oT.late){ on.ln += oT.late.n; on.lnet += oT.late.net; } if(oT.beOff && oT.beOff.n){ on.nbN += oT.beOff.n; on.nb += oT.beOff.net; } if(oT.tiers && oT.tiers.n){ on.trN += oT.tiers.n; on.tr += oT.tiers.net; } }\n"
    "      var d0 = x.whatIf && x.whatIf.detect && x.whatIf.detect.atDetection;")
rep("return { markets:mk, market:{ n:a.n, avg: a.n ? a.net/a.n : null, lateN:a.ln, late: a.ln ? a.lnet/a.ln : null }, limit:",
    "return { onTime:{ markets:on.mk, n:on.n, gross: on.n ? on.R/on.n : null, avg: on.n ? on.net/on.n : null, lateN:on.ln, late: on.ln ? on.lnet/on.ln : null, beOff: on.nbN ? on.nb/on.nbN : null, tiers: on.trN ? on.tr/on.trN : null }, markets:mk, market:{ n:a.n, avg: a.n ? a.net/a.n : null, lateN:a.ln, late: a.ln ? a.lnet/a.ln : null }, limit:")
rep("var staleNote = truthNote + (stale ?",
    "var r2 = function(v){ return v == null || !isFinite(v) ? '\\u2014' : (v >= 0 ? '+' : '') + Number(v).toFixed(2) + 'R'; }, oT = cvT && cvT.onTime;\n"
    "      if(oT && oT.n) truthNote = '<p class=\"hint\" style=\"margin:0 0 8px;color:var(--text);\"><b>CREED\\u2019s honest record: setups shown on time</b> (set up and shown on the same 15-minute close, so the entry could really be taken): <b>' + r2(oT.avg) + ' a trade after costs</b> (' + r2(oT.gross) + ' before) over ' + oT.n + ' setups on ' + oT.markets + ' markets' + (oT.lateN ? '; ' + r2(oT.late) + ' on the later part' : '') + '. With three take-profit tiers: ' + r2(oT.tiers) + '; with breakeven off: ' + r2(oT.beOff) + '. A different exit cannot create an edge the entry does not have.</p>' + truthNote;\n"
    "      var staleNote = truthNote + (stale ?")
rep("<div><span>Total</span><b class=\"'+(tot.R>=0?'bull':'bear')+'\">'+(tot.n ? sgn(tot.R) : '\\u2014')+'</b></div></div>'",
    "<div><span>Total as taught (counts hindsight)</span><b class=\"'+(tot.R>=0?'bull':'bear')+'\">'+(tot.n ? sgn(tot.R) : '\\u2014')+'</b></div><div><span>Shown on time, a trade after costs</span><b>'+(oT && oT.n ? r2(oT.avg) : '\\u2014')+'</b></div></div>'")
# the signal list and the scoreboard use on-time figures where a market has them
rep("function creedRecord(sym){ var h = lsGet('omega_creed_history_v1', {}), x = h[sym]; if(!x || !x.ready || !x.ready.n) return null;",
    "function creedRecord(sym){ var h = lsGet('omega_creed_history_v1', {}), x = h[sym]; if(!x || !x.ready || !x.ready.n) return null;\n"
    "    if(x.onTime && x.onTime.all && x.onTime.all.n) return { n:x.onTime.all.n, avg:x.onTime.all.netAvg, late: x.onTime.late && x.onTime.late.n ? { n:x.onTime.late.n, avg:x.onTime.late.netAvg } : null, years:x.years, onTime:true };   // v6.5.71")
rep("record: rec ? 'Replay on '+(rec.years ? rec.years.toFixed(1)+' yrs' : 'stored history')+': '+rec.n+' setups, '+sgn(rec.avg)+' a setup'+",
    "record: rec ? 'Replay on '+(rec.years ? rec.years.toFixed(1)+' yrs' : 'stored history')+': '+rec.n+(rec.onTime ? ' setups shown on time, ' : ' setups as taught (counts hindsight), ')+sgn(rec.avg)+' a setup'+(rec.onTime ? ' after costs' : '')+")
rep("record: rec ? 'Replay: '+rec.n+' setups, '+sgn(rec.avg)+' a setup' :",
    "record: rec ? 'Replay: '+rec.n+(rec.onTime ? ' setups shown on time, ' : ' setups as taught (counts hindsight), ')+sgn(rec.avg)+' a setup'+(rec.onTime ? ' after costs' : '') :")
rep("var ch = lsGet('omega_creed_history_v1', {}), cn = 0, cs = 0; Object.keys(ch).forEach(function(k){ var x = ch[k]; if(x && x.ready && x.ready.n){ cn += x.ready.n; cs += (x.ready.netAvg != null ? x.ready.netAvg : x.ready.avg)*x.ready.n; } }); if(cn){ p.creedN = cn; p.creedR = cs/cn; }",
    "var ch = lsGet('omega_creed_history_v1', {}), cn = 0, cs = 0; Object.keys(ch).forEach(function(k){ var x = ch[k], o = x && x.onTime && x.onTime.all; if(o && o.n){ cn += o.n; cs += o.netAvg*o.n; } }); if(cn){ p.creedN = cn; p.creedR = cs/cn; }   // v6.5.71: setups shown on time only")
rep("{ k:'creedR', label:'CREED replayed on stored history, average a setup after costs',", "{ k:'creedR', label:'CREED replayed on stored history, a setup shown on time, after costs',")

# ── CREED Backtest: entry when shown (default) or as taught ──
rep("<div class=\"sim-field\"><label>Breakeven trigger (R)</label><input type=\"number\" id=\"creedBtBeAtR\" value=\"1\" min=\"0.1\" max=\"10\" step=\"0.1\" /></div>",
    "<div class=\"sim-field\"><label>Breakeven trigger (R)</label><input type=\"number\" id=\"creedBtBeAtR\" value=\"1\" min=\"0.1\" max=\"10\" step=\"0.1\" /></div>\n"
    "          <div class=\"sim-field\" style=\"flex:1 1 100%;\"><label for=\"creedBtEntryWhen\">Entry</label><select id=\"creedBtEntryWhen\" title=\"About 2 in 3 CREED setups appear hours after the candle whose close is quoted as the entry. Entering when shown is what you could really do; the replays show the 'as taught' entry counts hindsight.\"><option value=\"shown\">When CREED shows the setup (that candle&rsquo;s close) &mdash; what you could really take</option><option value=\"taught\">At the acceptance close even when shown later (as taught; counts hindsight)</option></select></div>")
rep("      tiers: tiersOn(),\n      beAtR: Math.max(0.1, btNum('creedBtBeAtR', 1))\n    };",
    "      tiers: tiersOn(),\n      beAtR: Math.max(0.1, btNum('creedBtBeAtR', 1)),\n"
    "      entryWhen: (function(){ var c = el('creedBtEntryWhen'); return c && c.value === 'taught' ? 'taught' : 'shown'; })()   // v6.5.71\n    };")
rep("            var slipEntry = creedSlippage(a.levels.entry, a.direction, bar, cfg.slippagePct, BT.rng);\n            var riskDist  = Math.abs(slipEntry - a.levels.stop);\n            if(riskDist > 0){",
    "            // v6.5.71: a setup shown after its acceptance candle is entered at the close it is shown on (unless 'as taught' is chosen)\n"
    "            var lateBars = (a.acceptance && a.acceptance.at != null) ? (m15Slice.length - 1 - a.acceptance.at) : 0, entryPx = a.levels.entry;\n"
    "            if(cfg.entryWhen === 'shown' && lateBars > 0){ entryPx = +bar.c; var okLate = a.direction === 'long' ? (entryPx > a.levels.stop && entryPx < a.levels.target) : (entryPx < a.levels.stop && entryPx > a.levels.target); if(!okLate){ BT.skippedLate = (BT.skippedLate || 0) + 1; entryPx = NaN; } }\n"
    "            var slipEntry = isFinite(entryPx) ? creedSlippage(entryPx, a.direction, bar, cfg.slippagePct, BT.rng) : NaN;\n            var riskDist  = Math.abs(slipEntry - a.levels.stop);\n            if(riskDist > 0){")
rep("'. Seed ' + seed + ', risk ' + cfg.riskPct + '%, commission ' + cfg.commission + '%, slippage ' + cfg.slippagePct + '%' +",
    "'. Seed ' + seed + ', ' + btEntryText() + ', risk ' + cfg.riskPct + '%, commission ' + cfg.commission + '%, slippage ' + cfg.slippagePct + '%' +")
rep("    BT.tradedEvents = {};\n    BT.skippedRepeats = 0;\n", "    BT.tradedEvents = {};\n    BT.skippedRepeats = 0;\n    BT.entryWhen = cfg.entryWhen; BT.skippedLate = 0;   // v6.5.71\n")
rep("  async function runBacktest(){\n    if(BT.running) return;",
    "  function btEntryText(){ return 'entry ' + (BT.entryWhen === 'taught' ? 'as taught (counts hindsight)' : 'when shown' + (BT.skippedLate ? ' (' + BT.skippedLate + ' shown after price had passed the stop or target, skipped)' : '')); }   // v6.5.71\n  async function runBacktest(){\n    if(BT.running) return;")
rep("btStatus('Backtest complete \\u2014 '+closed+' trade'+(closed===1?'':'s')+', final equity '+fmt(BT.equity,2)+' \\u00b7 seed '+seed);",
    "btStatus('Backtest complete \\u2014 '+closed+' trade'+(closed===1?'':'s')+', final equity '+fmt(BT.equity,2)+' \\u00b7 seed '+seed+' \\u00b7 '+btEntryText());")

# ── research downloads ──
i = s.index('<script>/* ═══ FUTURES DATA FOR RESEARCH'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('final4export.js', encoding='utf-8').read().rstrip('\n') + '\n' + open('creed15export.js', encoding='utf-8').read().rstrip('\n') + s[j:]

# ── research record and built-in knowledge ──
m = re.search(r"\{ round:'12', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + (",\n    { round:'14', tried:'Hourly rules on perpetuals (a coin\\u2019s capitulation hour, the market\\u2019s capitulation, premium extremes, hourly reversal, short-squeeze fades), listing age, and a walk-forward machine-learning model across 165 coins; screened on 25 coins, validated on 140', "
  "result:'1 rule passed validation: buying a coin after a fall of 5+ of its own hourly standard deviations while its perpetual trades at an unusual discount, held 12 hours (+19% a year over the market on 140 coins, z 3.04). Its final test needs untouched hourly data (the download below). The model across coins made +37.8% a year over the market on 125 untouched coins (z 2.89) but missed the strict bar of 3.29, so it is judged on new weeks. Everything else failed.' },\n"
  "    { round:'CREED', tried:'Your CREED replays (25 markets, 6,989 setups, Oct 2023 \\u2013 Oct 2026) split by when each setup appears', "
  "result:'Setups shown on time made +0.015R a trade before costs and \\u22120.085R after (2,497 setups): no edge. The +0.47R headline came from setups shown hours later but priced at the earlier close. Three take-profit tiers (+0.001R) and breakeven off (+0.057R) change nothing.' } ];") + s[m.end():]
k0 = s.index('var KN = '); k1 = s.index('\n', k0); line = s[k0:k1]; assert line.endswith(';'), line[-40:]
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.70 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.70 ' + sep + ' build ' + old + ' UTC', 'v6.5.71 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.71 · build' in s and 'v6.5.70 · build' not in s and s.count('OMEGA_FINAL4EXPORT = ') == 1 and s.count('OMEGA_CREED15EXPORT = ') == 1 and "round:'14'" in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
