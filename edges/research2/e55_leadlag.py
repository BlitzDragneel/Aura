"""E55 BTC->alt lead-lag at 5m/15m (plan edges/plans/E55_leadlag_5m.md)."""
import sys, json, os
sys.path.insert(0, "/home/user/Aura")
import numpy as np, pandas as pd
from edges.lib import bt

PLAN = "edges/plans/E55_leadlag_5m.md"
MD5 = bt.register_plan(os.path.join(bt.ROOT, "plans/E55_leadlag_5m.md")) if "--reg" in sys.argv else \
    __import__("hashlib").md5(open(os.path.join(bt.ROOT, "plans/E55_leadlag_5m.md"), "rb").read()).hexdigest()
SCR = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/research2"
SYMS = sorted(os.path.basename(f)[:-8] for f in __import__("glob").glob(f"{bt.DATA}/5m/*.parquet"))
ALTS = [s for s in SYMS if s != "BTCUSDT"]


def build(tf):
    P = bt.panel(SYMS, "5m", fields=("o", "h", "l", "c", "qv"))
    if tf == "15m":
        P = {"o": P["o"].resample("15min").first(), "h": P["h"].resample("15min").max(),
             "l": P["l"].resample("15min").min(), "c": P["c"].resample("15min").last(),
             "qv": P["qv"].resample("15min").sum(min_count=1)}
    N = 288 if tf == "5m" else 96
    r = np.log(P["c"]).diff()
    rb = r["BTCUSDT"]
    sig = rb.rolling(N, min_periods=N // 2).std().shift(1)
    var = rb.rolling(N, min_periods=N // 2).var().shift(1)
    beta = r[ALTS].rolling(N, min_periods=N // 2).cov(rb).shift(1).div(var, axis=0)
    qv24 = P["qv"][ALTS].rolling(N, min_periods=N // 2).sum().shift(1)
    return P, r, rb, sig, beta, qv24


def trades_for(P, r, rb, beta, qv24, trig_idx, h, filt, with_mae=False):
    """trig_idx: integer positions of trigger bars (sorted, non-overlap enforced here)."""
    n = len(rb)
    keep, last = [], -10 ** 9
    for i in trig_idx:
        if i - last >= h and i + h < n:
            keep.append(i); last = i
    keep = np.array(keep, dtype=int)
    if len(keep) == 0:
        return pd.DataFrame(columns=["time", "sym", "net", "gross"])
    O, C = P["o"][ALTS].values, P["c"][ALTS].values
    side = np.sign(rb.values[keep])[:, None]
    ent = O[keep + 1]; ext = C[keep + h]
    gross = side * (ext / ent - 1)
    cost = bt.round_trip_cost(qv24.values[keep])
    ok = np.isfinite(gross) & np.isfinite(cost)
    if filt == "lag":
        e = r[ALTS].values[keep] - beta.values[keep] * rb.values[keep][:, None]
        lag = (e * side) < (-0.5 * np.abs(beta.values[keep]) * np.abs(rb.values[keep])[:, None])
        ok &= lag
    net = gross - cost
    tt = np.repeat(rb.index.values[keep][:, None], len(ALTS), 1)
    ss = np.tile(np.array(ALTS)[None, :], (len(keep), 1))
    df = pd.DataFrame(dict(time=pd.to_datetime(tt[ok], utc=True), sym=ss[ok], net=net[ok], gross=gross[ok]))
    if with_mae:
        Hh, Ll = P["h"][ALTS].values, P["l"][ALTS].values
        mae = np.full(gross.shape, np.nan)
        for j, i in enumerate(keep):
            lo = np.nanmin(Ll[i + 1:i + h + 1], 0) / ent[j] - 1
            hi = np.nanmax(Hh[i + 1:i + h + 1], 0) / ent[j] - 1
            mae[j] = np.where(side[j] > 0, lo, -hi)
        df["mae"] = mae[ok]
        bar = (rb.index[1] - rb.index[0])
        df["exit_time"] = df.time + bar * (h + 1)
    return df


def weakest(df, years):
    m = [df[df.time.dt.year == y].net.mean() for y in years]
    return np.nanmin(m) if all(np.isfinite(m)) else -np.inf


def main():
    out = {"plan": PLAN, "md5": MD5, "variants": []}
    D0, D1 = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC")
    rng = np.random.default_rng(55)
    real_best, null_best = -np.inf, np.full(200, -np.inf)
    store = {}
    for tf in ("5m", "15m"):
        P, r, rb, sig, beta, qv24 = build(tf)
        idx = rb.index
        disc = (idx >= D0) & (idx < D1)
        for k in (2, 3, 4):
            trig = np.where((np.abs(rb.values) > k * sig.values) & np.isfinite(sig.values))[0]
            trig_d = trig[disc[trig]]
            dpos = np.where(disc)[0]
            for filt in ("all", "lag"):
                for h in (1, 3, 6, 12):
                    name = f"{tf}_k{k}_{filt}_h{h}"
                    tr = trades_for(P, r, rb, beta, qv24, trig_d, h, filt)
                    s = bt.summarize(tr, name); s["gross_bp"] = round(tr.gross.mean() * 1e4, 2) if len(tr) else None
                    w = weakest(tr, (2022, 2023)); s["weakest_year_bp"] = round(w * 1e4, 2)
                    bt.log_attempt(MD5, name, "discovery", s)
                    out["variants"].append(s)
                    elig = s.get("t_week", 0) >= 2 and w > 0
                    store[name] = (tf, k, filt, h, elig, w)
                    real_best = max(real_best, w)
                    for b in range(200):
                        rt = np.sort(rng.choice(dpos, size=len(trig_d), replace=False))
                        nt = trades_for(P, r, rb, beta, qv24, rt, h, filt)
                        null_best[b] = max(null_best[b], weakest(nt, (2022, 2023)) if len(nt) else -np.inf)
                    print(name, s["n"], s["gross_bp"], s["mean_bp"], s["t_week"], s["weakest_year_bp"], flush=True)
        del P, r, beta, qv24
    out["luck"] = dict(real_best_weakest_bp=round(real_best * 1e4, 2),
                       null_p95_bp=round(float(np.percentile(null_best, 95)) * 1e4, 2),
                       pct=float((null_best < real_best).mean()))
    elig = sorted([(v[5], n) for n, v in store.items() if v[4]], reverse=True)[:3]
    out["eligible_promoted"] = [n for _, n in elig]
    json.dump(out, open(f"{SCR}/e55_disc.json", "w"), indent=1, default=str)
    print("LUCK", out["luck"], "PROMOTED", out["eligible_promoted"])


if __name__ == "__main__":
    main()
