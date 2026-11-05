import sys, json, time, itertools, os, pickle; sys.path.insert(0,'/home/claude/edge')
import numpy as np, engine3 as G, engine2 as E
COMP = dict(
  entry=[('mkt', dict(entry_mode=0)), ('retest', dict(entry_mode=1, retest_off=0.5, retest_wait=6))],
  stop=[('s1.5', dict(stop_k=1.5)), ('s2', dict(stop_k=2.0)), ('s3', dict(stop_k=3.0))],
  add=[('noadd', dict()), ('addstrength', dict(add_mode=1, add_size=1.0, add_max=2, add_R=1.0)), ('addpullback', dict(init=2/3, add_mode=2, add_size=2/3, add_max=1))],
  out=[('noout', dict()), ('half1R', dict(sc1_frac=0.5, sc1_R=1.0)), ('thirds', dict(sc1_frac=1/3, sc1_R=1.0, sc2_frac=0.5, sc2_R=2.0))],
  exit=[('tgt3', dict(tgt_R=3.0)), ('chand3', dict(trail_mode=1, trail_k=3.0)), ('tighten', dict(trail_mode=2, trail_k=3.0, trail_min=1.5)), ('ema20', dict(ema_exit=1))],
  time=[('t168', dict(max_bars=168)), ('noprog6', dict(noprog_bars=6, noprog_R=0.5, max_bars=168)), ('t48', dict(max_bars=48))],
  protect=[('noprot', dict()), ('be1', dict(be_R=1.0, be_to=0.0)), ('lock', dict(lock1_R=1.5, lock1_to=0.25, lock2_R=3.0, lock2_to=1.5))])
NAMES = list(COMP)
def combos(): return list(itertools.product(*[COMP[k] for k in NAMES]))
def stats(book, R, xh, valid):
    a = valid & (book.hr < E.SPLIT_H); b = valid & (book.hr >= E.SPLIT_H)
    out = dict(mA=float(np.mean(R[a])) if a.any() else None, mB=float(np.mean(R[b])) if b.any() else None, nA=int(a.sum()), nB=int(b.sum()))
    # weekly-clustered t on the 2nd half (all signals)
    wk = (book.hr[b]//168); s = np.bincount(wk - wk.min(), weights=R[b]) if b.any() else np.zeros(1); s = s[np.bincount(wk - wk.min()) > 0] if b.any() else s
    out['tB'] = float(s.mean()/s.std()*np.sqrt(len(s))) if len(s) > 3 and s.std() > 0 else None
    for lab, t0, t1 in [('A', E.START_H, E.SPLIT_H), ('B', E.SPLIT_H, 10**9)]:
        eq, dd, n, _ = book.acct(R, xh, valid, t0, t1, 0.01); out['acc' + lab] = float(eq); out['dd' + lab] = float(dd); out['n' + lab + 'acc'] = int(n)
    return out
if __name__ == '__main__':
    entries = sys.argv[1].split(','); budget = float(sys.argv[2]); path = 'grid3.jsonl'
    done = set()
    if os.path.exists(path):
        for l in open(path): r = json.loads(l); done.add((r['entry'], tuple(r['combo'])))
    t0 = time.time(); bars = G.Bars(); print('bars', round(time.time() - t0), 's', flush=True)
    for spec in entries:
        ent, flt = spec.split(':')
        if all((spec, tuple(c[0] for c in cmb)) in done for cmb in combos()): continue
        bk = G.Book(ent, flt, bars)
        with open(path, 'a') as f:
            for cmb in combos():
                key = (spec, tuple(c[0] for c in cmb))
                if key in done: continue
                kw = {}; [kw.update(c[1]) for c in cmb]
                R, xh, valid = bk.run(G.P(**kw)); st = stats(bk, R, xh, valid)
                f.write(json.dumps(dict(entry=spec, combo=[c[0] for c in cmb], **st)) + '\n'); f.flush(); done.add(key)
                if time.time() - t0 > budget: print('paused', spec, len([d for d in done if d[0] == spec]), 'of', len(combos()), round(time.time() - t0), 's'); sys.exit(0)
        print('finished', spec, round(time.time() - t0), 's')
