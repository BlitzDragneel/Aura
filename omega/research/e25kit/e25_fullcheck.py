import sys, pickle, json, numpy as np
sys.path.insert(0, '/home/claude/omega/research'); from load import load
D = pickle.load(open('hourly_e25.pkl', 'rb')); per = {}; diffs = []; found = total = 0; missing_coins = []
for part in ['final4_a', 'final4_b', 'final4_c', 'final4_d', 'final4_young']:
    d, ms = load(part); tf = int(d.get('tf', 60))
    for m in ms:
        s = m['sym']; hrs = (m['t']*tf*60)//3600; c = m['c']; sel = hrs >= 471144      # archive window starts 2023-10-01
        hrs, c = hrs[sel], c[sel]; total += len(c)
        if s not in D: missing_coins.append(s); continue
        A = D[s]; idx = {int(h): i for i, h in enumerate(A['h'])}
        dd = [abs(c[k]/A['c'][idx[int(h)]] - 1) for k, h in enumerate(hrs) if int(h) in idx and A['v'][idx[int(h)]] > 0 and c[k] > 0]
        found += len(dd); diffs += dd; per[s] = (len(dd), len(c), float(np.median(dd)) if dd else None, float(np.max(dd)) if dd else None)
d = np.array(diffs)
print(f'coins in final4: {len(per) + len(missing_coins)}; not in the archive: {missing_coins}')
print(f'hours compared {found} of {total} ({found/total:.1%}); median |diff| {np.median(d)*100:.6f}%; 99th pct {np.percentile(d,99)*100:.5f}%; 99.9th {np.percentile(d,99.9)*100:.4f}%; max {d.max()*100:.3f}%')
bad = sorted(((v[3], k) for k, v in per.items() if v[3] is not None and v[3] > 0.001), reverse=True)[:10]
print('coins with any hour off by >0.1%:', len([1 for k, v in per.items() if v[3] is not None and v[3] > 0.001]), bad[:5])
low = [(k, v[0], v[1]) for k, v in per.items() if v[1] and v[0] < 0.9*v[1]]
print('coins with <90% of their hours matched (mostly zero-volume hours in the archive):', len(low), low[:8])
ok = np.median(d) < 1e-4
print('PLAN E25 DATA CHECK:', 'PASS' if ok else 'FAIL — E25 VOID')
json.dump(dict(found=found, total=total, median=float(np.median(d)), p99=float(np.percentile(d, 99)), max=float(d.max()), missing=missing_coins, low=low, passed=bool(ok)), open('E25_fullcheck.json', 'w'))
