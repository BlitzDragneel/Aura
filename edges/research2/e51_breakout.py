"""E51 Donchian breakout + ATR trailing stop, 4h, 10 majors (plan edges/plans/E51_breakout_4h.md)."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, numba
from edges.lib import bt
import lib2

MD5 = hashlib.md5(open(os.path.join(bt.ROOT, "plans/E51_breakout_4h.md"), "rb").read()).hexdigest()
COINS = "BTCUSDT ETHUSDT BNBUSDT XRPUSDT ADAUSDT LINKUSDT LTCUSDT DOTUSDT BCHUSDT SOLUSDT".split()
OUT = f"{lib2.SCR}/e51"; os.makedirs(OUT, exist_ok=True)


@numba.njit
def sim(o, h, l, c, atr, sig, N2, k, exitmode, reverse):
    """sig[i] in {+1,-1,0} decided at close of bar i -> enter at o[i+1].
    exitmode 0: ATR trail (k), 1: channel N2. Returns arrays (entry_idx, exit_idx, side, entry_px, exit_px, mae)."""
    T = len(c)
    E = np.empty(T, np.int64); X = np.empty(T, np.int64); S = np.empty(T, np.int64)
    EP = np.empty(T); XP = np.empty(T); MAE = np.empty(T)
    n = 0
    pos = 0; ei = 0; ep = 0.0; best = 0.0; worst = 0.0
    pending = 0
    i = 0
    while i < T - 1:
        # open of bar i+1 handled at top of next iteration via pending
        j = i + 1
        if pending != 0:
            if pos != 0:  # reversal exit at open
                E[n] = ei; X[n] = j; S[n] = pos; EP[n] = ep; XP[n] = o[j]; MAE[n] = worst; n += 1
                pos = 0
            if o[j] == o[j]:
                pos = pending; ei = j; ep = o[j]; best = c[j] if c[j] == c[j] else ep; worst = 0.0
            pending = 0
            # mae on entry bar
        if pos != 0:
            if l[j] == l[j]:
                adv = (l[j] / ep - 1) if pos > 0 else -(h[j] / ep - 1)
                if adv < worst:
                    worst = adv
            exited = False
            if exitmode == 0 and j > ei:
                stop = best - k * atr[j - 1] if pos > 0 else best + k * atr[j - 1]
                if pos > 0 and l[j] <= stop:
                    px = min(stop, o[j]); exited = True
                elif pos < 0 and h[j] >= stop:
                    px = max(stop, o[j]); exited = True
                if exited:
                    E[n] = ei; X[n] = j; S[n] = pos; EP[n] = ep; XP[n] = px; MAE[n] = worst; n += 1
                    pos = 0
            if pos != 0 and c[j] == c[j]:
                if pos > 0 and c[j] > best:
                    best = c[j]
                if pos < 0 and c[j] < best:
                    best = c[j]
                if exitmode == 1 and j >= N2:
                    lo = np.inf; hi = -np.inf
                    for q in range(j - N2, j):
                        if l[q] < lo: lo = l[q]
                        if h[q] > hi: hi = h[q]
                    if (pos > 0 and c[j] < lo) or (pos < 0 and c[j] > hi):
                        if j + 1 < T:
                            E[n] = ei; X[n] = j + 1; S[n] = pos; EP[n] = ep; XP[n] = o[j + 1]; MAE[n] = worst; n += 1
                            pos = 0
        # new signal at close of bar j
        s = sig[j]
        if s != 0 and j + 1 < T:
            if pos == 0:
                pending = s
            elif reverse and s != pos:
                pending = s
        i = j
    return E[:n], X[:n], S[:n], EP[:n], XP[:n], MAE[:n]


def load():
    P = lib2.trim(lib2.h4())
    D = {f: P[f][COINS].astype(float) for f in ("o", "h", "l", "c", "qv")}
    D["qv24"] = D["qv"].rolling(6, min_periods=1).sum()
    tr = pd.concat([D["h"] - D["l"], (D["h"] - D["c"].shift()).abs(), (D["l"] - D["c"].shift()).abs()]).groupby(level=0).max()
    D["atr"] = tr.reindex(D["c"].index).rolling(20, min_periods=20).mean()
    F = lib2.fund_bars(COINS, "4h").reindex(index=D["c"].index, columns=COINS).fillna(0.0)
    D["f4cum"] = F.cumsum()
    return D


def signals(D, N, direction):
    hi = D["h"].rolling(N).max().shift(1); lo = D["l"].rolling(N).min().shift(1)
    s = (D["c"] > hi).astype(int) - (D["c"] < lo).astype(int)
    if direction == "long":
        s = s.clip(lower=0)
    elif direction == "short":
        s = s.clip(upper=0)
    return s


def trades(D, sig, N, ex, rev, sym_list=COINS):
    """sig: DataFrame or dict sym -> int ndarray."""
    out = []
    idx = D["c"].index
    if "_arr" not in D:
        D["_arr"] = {s: [np.ascontiguousarray(D[f][s].values) for f in ("o", "h", "l", "c", "atr")] for s in COINS}
        D["_q"] = {s: D["qv24"][s].values for s in COINS}
        D["_f"] = {s: D["f4cum"][s].values for s in COINS}
    for s in sym_list:
        sg = sig[s].values if hasattr(sig, "columns") else sig[s]
        k = ex if ex != "ch" else 0.0
        E, X, S, EP, XP, MAE = sim(*D["_arr"][s], sg.astype(np.int64), max(N // 2, 2), float(k), 1 if ex == "ch" else 0, rev)
        if len(E) == 0:
            continue
        gross = S * (XP / EP - 1)
        cost = bt.round_trip_cost(D["_q"][s][np.maximum(E - 1, 0)])
        fc = D["_f"][s]
        fund = -S * (fc[X - 1] - np.where(E > 0, fc[np.maximum(E - 1, 0)], 0.0))   # 4h bars E..X-1 held
        out.append(pd.DataFrame(dict(time=idx[E], exit_time=idx[X], sym=s, side=S, gross=gross, cost=cost, fund=fund,
                                     net=gross - cost + fund, mae=MAE)))
    if not out:
        return pd.DataFrame(columns=["time", "exit_time", "sym", "side", "net", "mae"])
    t = pd.concat(out, ignore_index=True)
    return t[t.net.notna()]


def weakest(t, years=(2020, 2021, 2022, 2023)):
    m = [t[t.time.dt.year == y].net.mean() for y in years]
    return min(m) if all(x == x for x in m) else -np.inf


def disc(t):
    return t[(t.time >= "2020-01-01") & (t.time < "2024-01-01")]


GRID = [(N, ex, dr) for N in (20, 55, 100, 200) for ex in (2.0, 3.0, 5.0, "ch") for dr in ("long", "short", "both")]


def main():
    D = load()
    res = dict(plan="E51_breakout_4h", md5=MD5, variants=[])
    rng = np.random.default_rng(51)
    NNULL = int(os.environ.get("NNULL", 200))
    null_best = np.full(NNULL, -np.inf)
    idx = D["c"].index
    dmask = (idx >= "2020-01-01") & (idx < "2024-01-01")
    for N, ex, dr in GRID:
        name = f"N{N}_x{ex}_{dr}"
        sig = signals(D, N, dr)
        t = trades(D, sig, N, ex, dr == "both")
        td = disc(t)
        st = bt.summarize(td, name); st["weakest_year_bp"] = round(weakest(td) * 1e4, 2)
        st["gross_bp"] = round(td.gross.mean() * 1e4, 2) if len(td) else None
        bt.log_attempt(MD5, name, "discovery", st)
        res["variants"].append(st)
        print(name, st["n"], st.get("gross_bp"), st.get("mean_bp"), st.get("t_week"), st["weakest_year_bp"], flush=True)
        # null: same number of discovery entries per coin at random bars, direction mix like real
        sd = sig[dmask]
        T = len(idx)
        for b in range(NNULL):
            ns = {}
            for s in COINS:
                arr = np.zeros(T, np.int64)
                n_ent = int((td.sym == s).sum())
                if n_ent:
                    nz = sd[s].values[sd[s].values != 0]
                    pos = np.where(dmask & D["c"][s].notna().values)[0]
                    pick = rng.choice(pos, size=min(n_ent, len(pos)), replace=False)
                    pl = (nz > 0).mean() if len(nz) else 0.5
                    arr[pick] = np.where(rng.random(len(pick)) < pl, 1, -1)
                ns[s] = arr
            nt = disc(trades(D, ns, N, ex, False))
            null_best[b] = max(null_best[b], weakest(nt))
    res["null_best_weakest_bp"] = [round(x * 1e4, 2) for x in null_best]
    json.dump(res, open(f"{OUT}/disc.json", "w"), indent=1, default=str)
    print("LUCK p95", np.percentile(null_best, 95) * 1e4)


if __name__ == "__main__":
    main()
