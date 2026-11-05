import numpy as np, json, sys
sys.argv = ['x', 'real']
src = open('search28_r3.py').read().split("out = open(")[0].replace("D = range(a - 40, b)", "D = range(E.STAGES['discovery'][0] - 40, E.STAGES['final'][1])")
exec(src)
P = {'V1': (lambda: band(SIG['D fund1 0.5 + size 0.5'], 10, 3)), 'V2': (lambda: band(SIG['A fund1 0.75 + size 0.25'], 10, 3)),
     'V3': (lambda: rebal_every(SIG['A fund1 0.75 + size 0.25'], 10, 14)), 'V4': (lambda: rebal_every(SIG['C fund7'], 10, 14)), 'V5': (lambda: band(SIG['B size'], 10, 2))}
RES = {}
for k, f in P.items():
    W = f(); PP = E.pnl(W); dsc, val = E.evaluate(PP, 'discovery'), E.evaluate(PP, 'validation')
    RES[k] = dict(discovery=dsc, validation=val, passed=bool(val['mean_bp'] > 0 and val['t'] >= 2.0 and np.sign(val['mean_bp']) == np.sign(dsc['mean_bp'])))
    np.save(f'W_{k}.npy', W)
    print(k, f"disc net {dsc['mean_bp']:+.1f} t {dsc['t']:.2f} | 2024 net {val['mean_bp']:+.1f} gross {val['gross_bp']:+.1f} cost {val['cost_bp']:.1f} fund {val['fund_bp']:+.1f} t {val['t']:.2f} dd {val['maxdd']*100:.0f}% L {val['long_bp']:+.1f} S {val['short_bp']:+.1f} →", 'PASS' if RES[k]['passed'] else 'fail', flush=True)
json.dump(RES, open('E28_validation.json', 'w'), indent=1)
