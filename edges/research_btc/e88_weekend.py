"""E88 weekend / CME gap / Asia range on BTC 1h (plans/E88_btc_weekend_cme.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
MD5 = "4acf1760cbf2c5f9d31bd43bb763046f"


def mk(d, rows, entry_cost, cost_x):
    if not rows:
        return pd.DataFrame(columns=["time", "exit_time", "side", "net", "sym", "mae"])
    tr = pd.DataFrame(rows, columns=["e", "x", "side", "entry", "exit", "mae", "maker_exit"])
    idx = d.index
    tr["time"] = idx[tr.e.values]; tr["exit_time"] = idx[tr.x.values] + pd.Timedelta("1h")
    tr["sym"] = SYM
    tr["gross"] = tr.side * (tr.exit / tr.entry - 1)
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    xc = np.where(tr.maker_exit, MAKER_SIDE, TAKER_SIDE)
    tr["net"] = tr.gross - entry_cost - xc - tr.fund
    return tr


def events(d, shift):
    vt = d.index + pd.Timedelta(hours=shift)
    ct = vt.tz_convert("America/Chicago")
    fri = np.where((ct.dayofweek == 4) & (ct.hour == 15) & (ct.minute == 0))[0]      # bar ending 16:00 CT
    reo = np.where((ct.dayofweek == 6) & (ct.hour == 17))[0]                        # bar starting 17:00 CT
    mon = np.where((vt.dayofweek == 0) & (vt.hour == 0))[0]
    return vt, fri, reo, mon


def grid(d, shift=0):
    o, h, l, c = (d[k].values for k in "ohlc")
    n = len(d)
    vt, fri, reo, mon = events(d, shift)
    out = {}
    pairs = []
    for f in fri:
        k = np.searchsorted(reo, f + 1)
        if k < len(reo) and reo[k] - f < 60:
            pairs.append((f, reo[k]))
    # 1. CME gap fill
    for g in (0.005, 0.01, 0.02):
        for H in (24, 72):
            rows = []; busy = -1
            for f, r in pairs:
                if r <= busy or r + H >= n or not (c[f] > 0 and o[r] > 0):
                    continue
                gap = o[r] / c[f] - 1
                if abs(gap) < g:
                    continue
                s = -1 if gap > 0 else 1
                tp = c[f]; x = r + H - 1; px = c[x]; mk_ = False; worst = 0.0
                for j in range(r, r + H):
                    if not (h[j] > 0):
                        continue
                    worst = min(worst, (l[j] / o[r] - 1) if s > 0 else -(h[j] / o[r] - 1))
                    if j > r and ((s > 0 and h[j] > tp) or (s < 0 and l[j] < tp)):
                        x = j; px = tp; mk_ = True; break
                if not (px > 0):
                    continue
                rows.append((r, x, s, o[r], px, worst, mk_)); busy = x
            out[f"GAP g{g} H{H}"] = mk(d, rows, TAKER_SIDE, None)
    # 2. weekend hold
    for s in (1, -1):
        rows = []
        for f, r in pairs:
            if f + 1 < n and o[f + 1] > 0 and o[r] > 0:
                rows.append((f + 1, r - 1, s, o[f + 1], o[r], np.nan, False))
        out[f"WEEKEND {'LONG' if s>0 else 'SHORT'}"] = mk(d, rows, TAKER_SIDE, None)
    # 3. Monday follow/fade
    for mode in (1, -1):
        for H in (8, 24):
            rows = []
            for m in mon:
                k = np.searchsorted(fri, m) - 1
                if k < 0 or m - fri[k] > 72 or m + H >= n:
                    continue
                f = fri[k]
                if not (c[f] > 0 and o[m] > 0 and c[m + H - 1] > 0):
                    continue
                wm = o[m] / c[f] - 1
                if wm == 0:
                    continue
                s = int(mode * np.sign(wm))
                lo = np.nanmin(l[m:m + H]); hi = np.nanmax(h[m:m + H])
                rows.append((m, m + H - 1, s, o[m], c[m + H - 1], (lo / o[m] - 1) if s > 0 else -(hi / o[m] - 1), False))
            out[f"MONDAY {'FOLLOW' if mode>0 else 'FADE'} H{H}"] = mk(d, rows, TAKER_SIDE, None)
    # 4. Asia range breakout (virtual clock hours)
    hr = vt.hour.values; dow = vt.dayofweek.values
    starts = np.where((hr == 0) & (dow < 5))[0]
    for mode in ("FOLLOW", "FADE"):
        rows = []
        for s0 in starts:
            if s0 + 20 >= n:
                continue
            hh = h[s0:s0 + 8]; ll = l[s0:s0 + 8]
            if np.isnan(hh).any():
                continue
            top, bot = hh.max(), ll.min(); w = top - bot; mid = (top + bot) / 2
            for j in range(s0 + 8, s0 + 19):
                if c[j] > top or c[j] < bot:
                    up = c[j] > top
                    s = (1 if up else -1) * (1 if mode == "FOLLOW" else -1)
                    e = j + 1; xend = s0 + 19
                    if e > xend or not (o[e] > 0):
                        break
                    st = mid if mode == "FOLLOW" else ((top + w) if up else (bot - w))
                    x = xend; px = c[xend]; worst = 0.0
                    for q in range(e, xend + 1):
                        if q > e and ((s > 0 and o[q] <= st) or (s < 0 and o[q] >= st)):
                            x = q; px = o[q]; break
                        if (s > 0 and l[q] <= st) or (s < 0 and h[q] >= st):
                            x = q; px = st; worst = min(worst, s * (st / o[e] - 1)); break
                        worst = min(worst, (l[q] / o[e] - 1) if s > 0 else -(h[q] / o[e] - 1))
                    if px > 0:
                        rows.append((e, x, s, o[e], px, worst, False))
                    break
        out[f"ASIA {mode}"] = mk(d, rows, TAKER_SIDE, None)
    return out


def main():
    d = bars("1h")
    real = grid(d, 0)
    rng = np.random.default_rng(88)
    shifts = rng.choice(np.arange(12, 157), 150, replace=True)
    nulls = []
    for i, s in enumerate(shifts):
        g = grid(d, int(s))
        ts = []
        for t in g.values():
            dd = per(t, P1)["discovery"]
            if len(dd) >= 100 and dd.net.mean() > 0:
                ts.append(fast_t(dd))
        nulls.append(max(ts) if ts else 0.0)
        if i % 25 == 0:
            print(i, flush=True)
    out = judge(MD5, "E88", real, nulls, P1, nmin=100, years_need=3, final_info=True)
    out["all_variants_validation_final_info"] = {k: {p: summ(x) for p, x in per(t, P1).items() if p != "discovery"} for k, t in real.items()}
    json.dump(out, open(f"{ROOT}/edges/results/E88_result.json", "w"), indent=1, default=str)
    for k, v in sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9)):
        print(f"{k:22s}", v.get("mean_bp"), v.get("t_week"), v.get("n"), v.get("years"))
    print({k: v for k, v in out.items() if k not in ("discovery", "all_variants_validation_final_info")})


if __name__ == "__main__":
    main()
