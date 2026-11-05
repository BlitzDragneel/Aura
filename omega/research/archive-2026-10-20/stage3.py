import sys; sys.path.insert(0,'/home/claude/edge')
from engine import *
import json, pickle
top5 = json.load(open('top5.json'))
M = {
 'M0 stop + 5R target (baseline)':        dict(tgt_R=5.0, max_bars=168),
 'M1 trailing stop 3 ATR':                dict(tgt_R=0.0, trail_atr=3.0, max_bars=168),
 'M2 breakeven at +1R':                   dict(tgt_R=5.0, be_R=1.0, max_bars=168),
 'M3 close 60% at +1R, trail the rest':   dict(tgt_R=0.0, sc_frac=0.6, sc_R=1.0, be_R=1.0, trail_atr=3.0, max_bars=168),
 'M4 pyramid: add each +1R (max 3)':      dict(tgt_R=0.0, pyr_R=1.0, pyr_max=3, trail_atr=3.0, max_bars=168),
 'M5 your method: close 60% + pyramid':   dict(tgt_R=0.0, sc_frac=0.6, sc_R=1.0, pyr_R=1.0, pyr_max=3, trail_atr=3.0, max_bars=168),
 'M6 pyramid + breakeven':                dict(tgt_R=0.0, pyr_R=1.0, pyr_max=3, be_R=1.0, trail_atr=3.0, max_bars=168),
 'M7 tight stop 1 ATR, 5R target':        dict(stop_atr=1.0, tgt_R=5.0, max_bars=168),
}
out = {}
for s in top5:
    for m, kw in M.items():
        T = run(s, **kw); out[(s, m)] = T
        r = summ(T); print(f"{s[:3]} {m:40s} 1st {r['first'][1]:+.3f}R | 2nd {r['second'][1]:+.3f}R ±{r['second'][2]:.3f} | wins {r['second'][3]*100:3.0f}% | n {r['second'][0]}", flush=True)
pickle.dump(out, open('stage3.pkl','wb'))
