"""E161 mass search (plan edges/plans/E161_mass_search.md)."""
import json, sys, time, warnings
import numpy as np, pandas as pd
from edges.lib import bt
warnings.filterwarnings("ignore")
PLAN = sys.argv[1]
N_RULES = 50_000
HOLDS = (1, 4, 12, 24)
PER = dict(disc=("2020-01-01", "2023-01-01"), val=("2023-01-01", "2024-01-01"), final=("2024-01-01", "2027-01-01"))


def conditions(d, fund=None):
    c, h, l, v = d.c, d.h, d.l, d.v
    disc = (d.index >= PER["disc"][0]) & (d.index < PER["disc"][1])
    C = {}
    def q(x, name, lo=0.2, hi=0.8):
        a, b = x[disc].quantile(lo), x[disc].quantile(hi)
        C[f"{name}_low"], C[f"{name}_high"] = x <= a, x >= b
    lr = np.log(c).diff()
    for k in (1, 4, 24, 72, 168):
        q(c / c.shift(k) - 1, f"r{k}")
    dlt = c.diff(); up = dlt.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-dlt.clip(upper=0)).ewm(alpha=1 / 14).mean()
    rsi = 100 - 100 / (1 + up / dn); C["rsi_lt30"], C["rsi_gt70"] = rsi < 30, rsi > 70
    for n in (20, 50, 200):
        sma = c.rolling(n).mean(); C[f"above_sma{n}"], C[f"below_sma{n}"] = c > sma, c < sma
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atrp = (tr.rolling(14).mean() / c).rolling(24 * 30, min_periods=24 * 5).rank(pct=True)
    C["vol_high"], C["vol_low"] = atrp >= 2 / 3, atrp <= 1 / 3
    hr = pd.Series(d.index.hour, index=d.index)
    C["asia"], C["london"], C["ny"], C["late"] = hr < 7, (hr >= 7) & (hr < 13), (hr >= 13) & (hr < 21), hr >= 21
    wd = pd.Series(d.index.weekday, index=d.index)
    C["monday"], C["friday"], C["weekend"] = wd == 0, wd == 4, wd >= 5
    pos = (c - l.rolling(24).min()) / (h.rolling(24).max() - l.rolling(24).min())
    C["range_top"], C["range_bottom"] = pos >= 0.8, pos <= 0.2
    vz = (np.log1p(v) - np.log1p(v).rolling(168).mean()) / np.log1p(v).rolling(168).std()
    q(vz, "volz")
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    pb = (c - (mid - 2 * sd)) / (4 * sd); C["bb_below"], C["bb_above"] = pb < 0, pb > 1
    eff = (c - c.shift(24)).abs() / lr.abs().rolling(24).sum().pipe(lambda x: x * c)
    eff = (np.log(c / c.shift(24))).abs() / lr.abs().rolling(24).sum()
    q(eff, "trendiness", 1 / 3, 2 / 3)
    if fund is not None:
        q(fund.reindex(d.index, method="ffill"), "funding")
    names = sorted(C)
    M = np.column_stack([C[k].fillna(False).values.astype(bool) for k in names])
    return names, M


def fwd(d, cost):
    o = d.o.shift(-1)                      # enter at the next bar's open
    return {h: (o.shift(-h) / o - 1).values for h in HOLDS}


def score(M, R, di, sel, rules, cost):
    """rules: array (k, 5) = [c1, c2, c3 (-1 none), dir, hold]. Returns entries, mean, day-clustered t on the bars in sel."""
    out = np.zeros((len(rules), 3))
    idx = np.flatnonzero(sel)
    Ms, dis = M[idx], di[idx]
    bounds = np.r_[0, np.flatnonzero(np.diff(dis)) + 1]
    for h in HOLDS:
        g = np.flatnonzero(rules[:, 4] == h)
        r = R[h][idx]; ok = np.isfinite(r); r0 = np.where(ok, r, 0.0)
        for s in range(0, len(g), 2000):
            G = rules[g[s:s + 2000]]
            m = Ms[:, G[:, 0]] & ok[:, None]
            for col in (1, 2):
                has = G[:, col] >= 0
                m[:, has] &= Ms[:, G[has, col]]
            mf = m.astype(np.float32)
            S = np.add.reduceat(mf * (r0[:, None] * G[:, 3][None, :] - cost).astype(np.float32), bounds, axis=0)
            N = np.add.reduceat(mf, bounds, axis=0)
            n = N.sum(0); tot = S.sum(0)
            with np.errstate(invalid="ignore", divide="ignore"):
                dm = np.where(N > 0, S / np.maximum(N, 1), np.nan)
                k = (N > 0).sum(0)
                mu_d = np.nanmean(dm, axis=0); sd_d = np.nanstd(dm, axis=0, ddof=1)
                t = mu_d / (sd_d / np.sqrt(k))
            out[g[s:s + 2000]] = np.c_[n, tot / np.maximum(n, 1), t]
    return out


def nonoverlap(M, Rn, rule, d, a, b, cost):
    c1, c2, c3, dr, h = rule
    m = M[:, c1].copy()
    if c2 >= 0: m &= M[:, c2]
    if c3 >= 0: m &= M[:, c3]
    idx = np.flatnonzero(m & (d.index >= a) & (d.index < b) & np.isfinite(Rn[h]))
    tr, nxt = [], -1
    for i in idx:
        if i >= nxt:
            tr.append((d.index[i], dr * Rn[h][i] - cost)); nxt = i + h + 1
    return pd.DataFrame(tr, columns=["time", "net"])


def search(name, d, cost, fund, rng, null):
    names, M = conditions(d, fund)
    R = fwd(d, cost)
    di = ((d.index - d.index[0]).days).values
    if null:   # flip return signs by random day blocks (keeps volatility, destroys any real link)
        flip = rng.choice([-1.0, 1.0], di.max() + 1)[di]
        R = {h: R[h] * flip for h in HOLDS}
    k = M.shape[1]
    rules = np.empty((N_RULES, 5), int)
    for i in range(N_RULES):
        nc = rng.integers(1, 4); cs = rng.choice(k, nc, replace=False)
        rules[i] = [cs[0], cs[1] if nc > 1 else -1, cs[2] if nc > 2 else -1, rng.choice([-1, 1]), rng.choice(HOLDS)]
    rules = np.unique(np.c_[np.sort(rules[:, :3], axis=1), rules[:, 3:]], axis=0)
    sel = {p: (d.index >= a) & (d.index < b) for p, (a, b) in PER.items()}
    D = score(M, R, di, sel["disc"], rules, cost)
    elig = np.flatnonzero(D[:, 0] >= 150)
    top = elig[np.argsort(-np.nan_to_num(D[elig, 2], nan=-9))[:100]]
    V = score(M, R, di, sel["val"], rules[top], cost)
    vs = top[(V[:, 1] > 0) & (V[:, 2] >= 1.5)]
    fin = []
    for r in vs:
        T = nonoverlap(M, R, rules[r], d, *PER["final"], cost)
        if len(T) < 20:
            continue
        t = bt.tstat_weekly(T); yrs = T.groupby(T.time.dt.year).net.mean()
        fin.append(dict(rule=" & ".join(names[x] for x in rules[r][:3] if x >= 0) + f" | {'LONG' if rules[r][3] > 0 else 'SHORT'} {rules[r][4]}h",
                        disc_t=round(float(D[r, 2]), 2), val_mean_bp=round(float(V[list(top).index(r), 1] * 1e4), 1),
                        final_n=len(T), final_mean_bp=round(float(T.net.mean() * 1e4), 1), final_t=round(float(t), 2),
                        years_pos=int((yrs > 0).sum()), years=int(len(yrs)), trades=T.net.tolist() if t >= 2 else None))
    surv = [f for f in fin if f["final_mean_bp"] > 0 and f["final_t"] >= 2 and f["years_pos"] == f["years"]]
    return dict(rules_tested=int(len(rules)), eligible=int(len(elig)), top_disc_t=[round(float(x), 2) for x in D[top[:5], 2]],
                pass_validation=int(len(vs)), final_checked=len(fin), pass_final=len(surv), survivors=surv,
                best_final=sorted(fin, key=lambda f: -f["final_t"])[:5])


def mc(trades, n=100_000, risk=0.01, rng=None):
    tr = np.array(trades); s = tr / np.abs(tr[tr < 0]).mean()          # in R units
    paths = rng.choice(s, (n, len(s))) * risk
    eq = np.cumprod(1 + paths, axis=1)
    dd = (eq / np.maximum.accumulate(eq, axis=1) - 1).min(1)
    return dict(median_end=round(float(np.median(eq[:, -1])), 3), p5_end=round(float(np.percentile(eq[:, -1], 5)), 3),
                median_maxdd=round(float(np.median(dd)), 3), p_loss=round(float((eq[:, -1] < 1).mean()), 3), p_dd_over_20pct=round(float((dd < -0.2).mean()), 3))


t0 = time.time()
rng = np.random.default_rng(161)
btc = bt.load("BTCUSDT"); fund = bt.funding("BTCUSDT").resample("1h").last()
pax = pd.read_parquet("/home/user/data/metals/PAXG_1h.parquet").astype(float)
res = dict(plan="edges/plans/E161_mass_search.md", md5=PLAN, real={}, null={})
for name, d, cost, f in (("BTC", btc, 0.0014, fund), ("GOLD(PAXG)", pax, 0.0004, None)):
    for kind in ("real", "null"):
        r = search(name, d, cost, f, rng, kind == "null")
        res[kind][name] = r
        bt.log_attempt(PLAN, f"E161 {name} {kind} search", "all", dict(n=N_RULES, mean_bp=None, t_week=r["pass_final"]))
        print(name, kind, {k: v for k, v in r.items() if k not in ("survivors", "best_final")}, f"{time.time() - t0:.0f}s", flush=True)
        for b in r["best_final"]:
            print("   ", {k: v for k, v in b.items() if k != "trades"})
        if kind == "real":
            for s in r["survivors"]:
                s["monte_carlo_100k"] = mc(s.pop("trades"), rng=rng)
        else:
            for s in r["survivors"]:
                s.pop("trades", None)
real_n = sum(res["real"][a]["pass_final"] for a in res["real"]); null_n = sum(res["null"][a]["pass_final"] for a in res["null"])
res["verdict"] = f"real survivors {real_n} vs null survivors {null_n}: " + ("EDGE CANDIDATES (beat the luck baseline)" if real_n > null_n + 1 else "NOTHING beyond luck")
json.dump(res, open("edges/results/E161_result.json", "w"), indent=1, default=str)
print(res["verdict"])
