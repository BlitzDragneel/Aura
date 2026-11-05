"""Synthetic markets + the research engine's E22 H1/H3 trades, for Prime's parity check (s_prime_panic_test.js)."""
import json, sys, numpy as np
sys.path[:0] = ['/home/claude/omega/recorder/tests']
import reference_e22 as R
from synth import market
dfs = {f"C{i}USDT": market(i, 2400) for i in range(12)}
ref = {k: R.prep(d) for k, d in dfs.items()}; br = R.breadth_of(ref.values())
out = dict(markets={}, trades={})
for k, d in dfs.items():
    e = d.dropna(); out['markets'][k] = [[int(h), float(r.hi), float(r.lo), float(r.c)] for h, r in e.iterrows()]
for name, spec in (("H1", dict(mode="limit", q=10, k=2, W=3)), ("H3", dict(mode="taker", q=5, b=20))):
    tr = []
    for k, P in ref.items():
        tr += [[k, int(h), round(float(r), 9)] for h, r in R.run(P, R.masks(P, spec, br), spec['mode'], 0, 10**9, min_age=720, k=spec.get('k'), W=spec.get('W'))]
    out['trades'][name] = sorted(tr)
json.dump(out, open('parity.json', 'w')); print({k: len(v) for k, v in out['trades'].items()})
