"""E90 BTC 15m quiet-window maker mean reversion (plans/E90_btc_quiet_maker_reversion.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from numba import njit
from libbtc import *  # noqa
MD5 = "194861965aaf7f08b5af3cde78921be0"


@njit(cache=True)
def sim(o, h, l, c, a, gate, k, H):
    n = len(c); out = np.empty((n // 2 + 1, 7)); m = 0; t = 0
    while t < n - H - 2:
        if not gate[t] or not (a[t] > 0) or not (c[t] > 0):
            t += 1; continue
        j = t + 1
        if not (h[j] > 0):
            t += 1; continue
        bl = c[t] - k * a[t]; sl = c[t] + k * a[t]
        fb = l[j] < bl; fs = h[j] > sl
        if not fb and not fs:
            t += 1; continue
        if fb and fs:
            # adverse case: take the side whose close-to-entry move is worse
            s = 1 if (c[j] / bl - 1) < -(c[j] / sl - 1) else -1
        else:
            s = 1 if fb else -1
        e = bl if s > 0 else sl
        x = j + H; px = c[x]; mk = 0.0; worst = 0.0; ok = True
        for q in range(j, j + H + 1):
            if not (l[q] == l[q]):
                ok = False; break
            adv = (l[q] / e - 1) if s > 0 else -(h[q] / e - 1)
            if adv < worst:
                worst = adv
            if q > j and ((s > 0 and h[q] > c[t]) or (s < 0 and l[q] < c[t])):
                x = q; px = c[t]; mk = 1.0; break
        if ok and px > 0:
            out[m, 0] = j; out[m, 1] = x; out[m, 2] = s; out[m, 3] = e; out[m, 4] = px; out[m, 5] = worst; out[m, 6] = mk
            m += 1
        t = x + 1
    return out[:m]


def to_tr(rows, d):
    idx = d.index; bar = idx[1] - idx[0]
    tr = pd.DataFrame({"time": idx[rows[:, 0].astype(int)], "exit_time": idx[rows[:, 1].astype(int)] + bar,
                       "side": rows[:, 2].astype(int), "entry": rows[:, 3], "exit": rows[:, 4], "mae": rows[:, 5],
                       "maker_exit": rows[:, 6] > 0})
    tr["sym"] = SYM
    tr["gross"] = tr.side * (tr.exit / tr.entry - 1)
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    tr["net"] = tr.gross - MAKER_SIDE - np.where(tr.maker_exit, MAKER_SIDE, TAKER_SIDE) - tr.fund
    return tr


def main():
    d = bars("15m")
    a = atr(d)
    natr = a / d.c
    pct = natr.rolling(960, min_periods=480).rank(pct=True).values
    hr = d.index.hour.values
    okhr = ~((hr >= 13) & (hr <= 16))
    o, h, l, c, av = (d[x].values for x in "ohlc") + (a.values,) if False else (d.o.values, d.h.values, d.l.values, d.c.values, a.values)
    gates = {q: (np.nan_to_num(pct, nan=1) <= q) & okhr for q in (0.2, 0.4)}
    def grid(G, info=True):
        out = {}
        for k in (0.5, 1.0):
            for q in (0.2, 0.4):
                for H in (4, 16):
                    out[f"k{k} q{q} H{H}"] = to_tr(sim(o, h, l, c, av, G[q], k, H), d)
        return out
    real = grid(gates)
    info = {f"NOGATE k{k} H16": to_tr(sim(o, h, l, c, av, np.isfinite(pct), k, 16), d) for k in (0.5, 1.0)}
    rng = np.random.default_rng(90)
    pool = np.where((d.index < "2024-01-01") & np.isfinite(pct))[0]
    nulls = []
    for i in range(200):
        G = {}
        for q, g in gates.items():
            gg = np.zeros(len(g), dtype=np.bool_)
            gg[rng.choice(pool, int(g[pool].sum()), replace=False)] = True
            G[q] = gg
        r = grid(G)
        ts = [fast_t(per(t, P5)["discovery"]) for t in r.values() if len(per(t, P5)["discovery"]) >= 100 and per(t, P5)["discovery"].net.mean() > 0]
        nulls.append(max(ts) if ts else 0.0)
    out = judge(MD5, "E90", real, nulls, P5, nmin=100, years_need=2, final_info=True)
    out["info_no_gate"] = {k: {p: summ(x) for p, x in per(t, P5).items()} for k, t in info.items()}
    for k, t in info.items():
        bt.log_attempt(MD5, k, "discovery", summ(per(t, P5)["discovery"]))
    json.dump(out, open(f"{ROOT}/edges/results/E90_result.json", "w"), indent=1, default=str)
    for k, v in sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9)):
        print(f"{k:16s}", v.get("mean_bp"), v.get("t_week"), v.get("n"), v.get("win"), v.get("years"))
    for k, v in out["info_no_gate"].items():
        print(k, v["discovery"]["mean_bp"], v["discovery"]["t_week"], v["discovery"]["n"])
    print({k: v for k, v in out.items() if k not in ("discovery", "info_no_gate")})


if __name__ == "__main__":
    main()
