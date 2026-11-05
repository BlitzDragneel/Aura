"""v6.5.106: corrections from the bugs/misinformation audit (audits/bugs/BUG_REPORT.md). Text and one Brain note only;
CREED's engine and every rule's logic are unchanged.
 1. Funding harvest: E34 (Nov 2026, delta-neutral harvest on 2025-26: -17% a year, worst 30 days -33%) is now shown on the
    harvest card, the Round 12 winners card (half of it is the harvest), the research-record heading, the "being paid for
    supplying leverage" lesson and the two Autopilot job labels, which still called it "the rule that passed".
 2. "Why signals are rare": its footer listed BTC/ETH timing and H1/H3 on every perpetual as "not yet run"; both were run
    (E28 round 5; E25/E26 on 883-903 perpetuals). Now: the ideas the handover lists as untested (on-chain flows, options).
 3. "Move the stop to breakeven: the rest is risk-free" (signal card, Simulation plan) -> a breakeven stop limits the loss
    but gaps, slippage, fees and funding can still cost money (the app's own stop note says a stop is not a guaranteed exit).
 4. The Brain gets one pinned correction note about E34 (once, flag omega_e34_note_v1), so its older pinned harvest notes
    are not the last word.
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)

E34 = 'E34 (Nov 2026): run again as a delta-neutral harvest on 2025\\u201326, it FAILED: \\u221217% a year, worst 30 days \\u221233% (one coin\\u2019s funding flipped: \\u221264.6% in a month)'

# 1. funding harvest
rep("Funding harvest \\u2014 passed untouched tests in rounds 7, 8 and 10</h2>",
    "Funding harvest \\u2014 passed untouched tests in rounds 7, 8 and 10; FAILED on 2025\\u201326 (E34)</h2>")
rep("WAIT:['Paper · passed its untouched test · forward record starts at Sunday 18 Oct’s close','bull']",
    "WAIT:['Paper · failed its 2025\\u201326 test (E34) · kept as a record','warn']")
A = "      '<p class=\"hint\" style=\"margin-top:8px;\">Not a bet on direction. Each Sunday close it <b>holds a coin and shorts the same coin’s perpetual</b>"
rep(A, "      '<p class=\"hint\" id=\"harvestE34\" style=\"margin-top:8px;color:var(--bear);\"><b>Read this first. " + E34 + ".</b> Most months nothing paid enough; when something did it earned 1\\u20133% a month, and one flip erased it. The rounds below were measured on 2020\\u20132026 data dominated by 2021; the recent years were thin or negative. Keep it as a record on paper; do not trade it.</p>' +\n" + A)
rep("label:'Funding harvest (the rule that passed its untouched test)'",
    "label:'Funding harvest (record only: passed rounds 7, 8, 10; failed E34 on 2025\\u201326)'")
rep("label:'Round 12 winners (harvest + dip-buying)'",
    "label:'Round 12 winners (harvest + dip-buying; the harvest half failed E34)'")
rep("Paper · passed on 125 untouched coins · forward record starts at Sunday 18 Oct’s close</span></div>",
    "Paper · passed on 125 untouched coins (to Oct 2026) · its harvest half failed E34</span></div>")
B = "      '<p class=\"hint\">' + esc(Z.failedFinal) + '</p><p class=\"hint\" style=\"color:var(--amber);\"><b>Read it the right way:</b> ' + esc(Z.caution) + '</p>';"
rep(B, B[:-1] + " +\n      '<p class=\"hint\" id=\"r12E34\" style=\"color:var(--bear);\"><b>Half of each winner is the funding harvest.</b> " + E34 + ". Keep it on paper.</p>';")
rep("and the climax reversal (round 16). Everything else failed</h2>",
    "and the climax reversal (round 16); the harvest then FAILED on 2025\\u201326 (E34, \\u221217% a year). Everything else failed</h2>")
rep("What a coin\\u2019s crowd does is not a law; being paid for supplying leverage is.",
    "What a coin\\u2019s crowd does is not a law; being paid for supplying leverage held up longer, until E34 (Nov 2026) found it lost 17% a year in 2025\\u201326.")

# 2. stale "next ideas"
rep("Next ideas not yet run: BTC/ETH timing from market-wide funding and breadth; H1/H3 on every perpetual, not only the 40 most-traded (more coins, more panics).",
    "Both of the earlier “next ideas” have been run: BTC/ETH timing from market-wide gauges (E28 round 5, failed) and H1/H3 on every perpetual (E25, E26). Not yet tested: on-chain flows and options data (new data, not more passes over the same candles).")

# 3. "risk-free"
rep("Immediately move your stop to breakeven — the rest of the trade is now risk-free.",
    "Immediately move your stop to breakeven — that limits the rest of the trade’s loss, but gaps, slippage, fees and funding can still cost money (a stop is not a guaranteed exit).")
rep("move the stop to breakeven — the standard way to make the remainder risk-free while letting it run.",
    "move the stop to breakeven — the standard way to cut the remainder’s risk while letting it run (not risk-free: gaps, slippage and fees still apply).")

# 4. one pinned Brain correction
NOTE = """<script>/* ═══ E34 CORRECTION NOTE (v6.5.106) — one pinned Brain note so older pinned harvest notes are not the last word ═══ */
(function(){
  'use strict';
  var FLAG = 'omega_e34_note_v1', n = 0;
  function go(){ try{ if(localStorage.getItem(FLAG)) return true; var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return false;
      B.feedObservation({ pinned:true, strat:'omega', tf:'1w', symbol:'*', text:'Correction (E34, Nov 2026): the funding harvest (spot long + perpetual short) that passed rounds 7, 8, 10 and 12 FAILED when run on 2025\\u201326: \\u221217% a year, worst 30 days \\u221233%; one coin\\u2019s funding flipped (\\u221264.6% in a month). Small steady income with a rare blow-up. Record only, not a strategy to trade.' });
      localStorage.setItem(FLAG, '1'); return true; }catch(e){ return true; } }
  if(!go()){ var iv = setInterval(function(){ if(go() || ++n > 30) clearInterval(iv); }, 2000); }
})();
</script>
"""
rep("<script>/* ═══ WHY SIGNALS ARE RARE", NOTE + "<script>/* ═══ WHY SIGNALS ARE RARE")

# build stamp
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.105 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.105 ' + sep + ' build ' + o + ' UTC', 'v6.5.106 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.106 · build' in s and 'v6.5.105 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
