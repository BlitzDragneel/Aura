"""E68 — new-data regime filters on panic bounce H1 and climax reversal (plan edges/plans/E68_regime_filters.md)."""
import os, pickle, warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA, bt, MD5, write_result, period, tstat

warnings.filterwarnings("ignore")
SCR = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/research3"
EXCL = ("USDC", "FDUSD", "TUSD", "BUSD", "USDP", "USDE", "BTCDOM", "DEFI", "XAU", "XAG", "PAXG")


def day_thresholds(x, lookback=720, step=24, q=10):
    n = len(x); lo = np.full(n, np.nan)
    for s in range(lookback, n, step):
        w = x[s - lookback:s]; w = w[np.isfinite(w)]
        if len(w) >= lookback // 2:
            lo[s:s + step] = np.percentile(w, q)
    return lo


def base_trades(sym):
    df = perp(sym)
    o, h, l, c, v = df.o.values, df.h.values, df.l.values, df.c.values, df.v.values
    F, Fm, qv24, idx = df.fund.values, df.fund_missing.values, df.qv24.fillna(0).values, df.index
    n = len(c)
    lr = np.log(df.c / df.c.shift(1))
    sig = lr.rolling(168, min_periods=120).std().shift(1).values
    r24 = np.log(df.c / df.c.shift(24)).values
    th = day_thresholds(r24)
    out = []
    # ---- H1
    mask = np.nan_to_num(r24 <= th, nan=0).astype(bool) & np.isfinite(th)
    nxt = -1
    for t in np.flatnonzero(mask):
        if t < nxt or not (sig[t] > 0 and c[t] > 0):
            continue
        lim = c[t] * np.exp(-2 * sig[t]); f = None
        for j in range(t + 1, min(n, t + 4)):
            if l[j] < lim:
                f = j; break
        if f is None:
            nxt = t + 3; continue
        if f + 24 >= n or not (c[f + 24] > 0):
            nxt = t + 3; continue
        gross = c[f + 24] / lim - 1
        cost = bt.MAKER + bt.TAKER + float(bt.slippage(qv24[t]))
        fund = F[f + 1:f + 25].sum() + bt_def(Fm[f + 1:f + 25])
        mae = np.nanmin(l[f:f + 25]) / lim - 1
        out.append(("H1", idx[t], idx[f], idx[f + 24] + pd.Timedelta(hours=1), sym, gross - cost - fund, mae))
        nxt = f + 24
    # ---- climax
    vs = pd.Series(v).rolling(168, min_periods=168).median().shift(1).values
    rng = h - l
    cl = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.5)
    z = lr.values / sig
    m2 = np.nan_to_num((z <= -3) & (v >= 3 * vs) & (cl >= 0.6), nan=0).astype(bool)
    m2[:24 * 30] = False
    nxt = -1
    for i in np.flatnonzero(m2):
        if i < nxt or i + 13 >= n:
            continue
        e, x = o[i + 1], o[i + 13]
        if not (e > 0 and x > 0):
            continue
        cost = float(bt.round_trip_cost(qv24[i + 1]))
        fund = F[i + 1:i + 13].sum() + bt_def(Fm[i + 1:i + 13])
        mae = np.nanmin(l[i + 1:i + 13]) / e - 1
        out.append(("CLX", idx[i], idx[i + 1], idx[i + 13], sym, x / e - 1 - cost - fund, mae))
        nxt = i + 12
    return out


def bt_def(fm):
    return 0.0001 * fm.sum()


def all_base():
    p = f"{SCR}/e68_base.pkl"
    if os.path.exists(p):
        return pd.read_pickle(p)
    rows = []
    for k, s in enumerate(bt.universe("1h")):
        if any(x in s for x in EXCL):
            continue
        try:
            rows += base_trades(s)
        except Exception as ex:
            print("skip", s, ex)
        if k % 100 == 0:
            print(k, len(rows), flush=True)
    T = pd.DataFrame(rows, columns=["rule", "sig_time", "time", "exit_time", "sym", "net", "mae"])
    T.to_pickle(p)
    return T


# ---------------------------------------------------------------- market-wide filter series (hourly, as known)
def daily(path, col, lag_h):
    d = pd.read_parquet(path)
    s = pd.Series(d[col].values.astype(float), index=pd.to_datetime(d.ts, unit="ms", utc=True)).sort_index()
    s = s[~s.index.duplicated()].asfreq("D")
    return s, lag_h


def filters_raw():
    st, _ = daily(f"{DATA}/stablecoins/total.parquet", "usd", 26)
    cm = pd.read_parquet(f"{DATA}/coinmetrics/btc.parquet")
    cm.index = pd.to_datetime(cm.ts, unit="ms", utc=True)
    cm = cm.sort_index().asfreq("D")
    fng, _ = daily(f"{DATA}/fear_greed/fng.parquet", "value", 2)
    dv = pd.read_parquet(f"{DATA}/deribit_dvol/BTC.parquet")
    dv = pd.Series(dv.c.values, index=pd.to_datetime(dv.ts, unit="ms", utc=True)).sort_index()
    dv = dv[~dv.index.duplicated()].asfreq("h").ffill()
    return dict(st=st, nf=(cm.FlowInExNtv - cm.FlowOutExNtv), fng=fng, dv=dv)


def build_filters(raw, shift_days=0):
    """Return {name: hourly bool Series (as known at that hour)}."""
    def sh(s, per_day):
        if not shift_days:
            return s
        return pd.Series(np.roll(s.values, shift_days * per_day), index=s.index)
    st, nf, fng, dv = sh(raw["st"], 1), sh(raw["nf"], 1), sh(raw["fng"], 1), sh(raw["dv"], 24)
    g30 = st / st.shift(30) - 1
    out = {}
    def lagd(x, h):
        x = x.copy(); x.index = x.index + pd.Timedelta(hours=h); return x
    out["F1 stable30>0"] = lagd(g30 > 0, 26)
    out["F2 stable30>med365"] = lagd(g30 > g30.rolling(365, min_periods=180).median().shift(1), 26)
    out["F3 btc netflow7<0"] = lagd(nf.rolling(7).sum() < 0, 28)
    out["F4 fng<=25"] = lagd(fng <= 25, 2)
    out["F5 fng<=40"] = lagd(fng <= 40, 2)
    out["F6 dvol>=p70"] = lagd(dv >= dv.rolling(24 * 365, min_periods=24 * 180).quantile(0.7).shift(1), 1)
    out["F7 dvol24h>=+10%"] = lagd(np.log(dv / dv.shift(24)) >= np.log(1.10), 1)
    out["F8 fng>=50"] = lagd(fng >= 50, 2)
    return out


def apply(T, fser):
    """bool per trade: filter value as known at the trade's signal hour (ffill)."""
    s = fser.astype(float)
    v = s.reindex(s.index.union(pd.DatetimeIndex(T.sig_time.unique()))).sort_index().ffill()
    return v.reindex(T.sig_time).values > 0.5


DV_START = "2021-03-24"

if __name__ == "__main__":
    md5 = MD5["E68_regime_filters"]
    T = all_base()
    T["time"] = pd.to_datetime(T.time, utc=True); T["sig_time"] = pd.to_datetime(T.sig_time, utc=True)
    T["exit_time"] = pd.to_datetime(T.exit_time, utc=True)
    print(T.groupby("rule").size())
    raw = filters_raw()
    FL = build_filters(raw)
    res = dict(plan="E68", md5=md5, base={}, discovery=[], promoted=[], validation={}, final=None)
    for rule in ("H1", "CLX"):
        B = T[T.rule == rule]
        for p in ("discovery", "validation", "final"):
            s = bt.summarize(period(B, p), f"{rule} base {p}")
            s["t"] = tstat(period(B, p))
            res["base"][f"{rule} {p}"] = s
            bt.log_attempt(md5, f"E68:{rule} base", p, s)
    rng = np.random.default_rng(0)
    nulls = [build_filters(raw, int(rng.integers(60, 2000))) for _ in range(200)]
    rows = []
    for rule in ("H1", "CLX"):
        B = T[T.rule == rule].reset_index(drop=True)
        for name, fs in FL.items():
            start = DV_START if "dvol" in name else None
            D = period(B, "discovery", start)
            base_mean = D.net.mean()
            keep = apply(D, fs)
            Dk = D[keep]
            s = bt.summarize(Dk, f"{rule} {name}") if len(Dk) else dict(label=f"{rule} {name}", n=0)
            s["t"] = tstat(Dk); s["base_mean_bp"] = round(base_mean * 1e4, 2)
            s["improve_bp"] = round((Dk.net.mean() - base_mean) * 1e4, 2) if len(Dk) else np.nan
            nm = []
            for NF in nulls:
                kk = apply(D, NF[name])
                if kk.sum() >= 10:
                    nm.append(D.net[kk].mean() - base_mean)
            s["null_p95_improve_bp"] = round(float(np.nanpercentile(nm, 95)) * 1e4, 2)
            s["luck_pct"] = float((np.array(nm) < (Dk.net.mean() - base_mean)).mean()) if len(Dk) else 0
            bt.log_attempt(md5, f"E68:{s['label']}", "discovery", s)
            rows.append(s)
            print(s["label"], s["n"], s.get("mean_bp"), s["base_mean_bp"], s["improve_bp"], s["null_p95_improve_bp"],
                  round(s["t"], 2) if s["t"] == s["t"] else None, flush=True)
    res["discovery"] = rows
    cand = sorted([r for r in rows if r["n"] >= 30 and r["luck_pct"] >= 0.95 and r["improve_bp"] > 0
                   and r["years_pos"] >= 0.6 * r["years_total"]], key=lambda r: -r["t"])[:3]
    res["promoted"] = [r["label"] for r in cand]
    best = None
    for r in cand:
        rule, name = r["label"].split(" ", 1)
        B = T[T.rule == rule]
        V = period(B, "validation"); Vk = V[apply(V, FL[name])]
        s = bt.summarize(Vk, r["label"]) if len(Vk) else dict(label=r["label"], n=0)
        s["t"] = tstat(Vk); s["base_mean_bp"] = round(V.net.mean() * 1e4, 2)
        bt.log_attempt(md5, f"E68:{r['label']}", "validation", s)
        res["validation"][r["label"]] = s
        if s.get("n", 0) and s["mean_bp"] > 0 and s["t"] >= 1.5 and s["mean_bp"] > s["base_mean_bp"] and \
                (best is None or s["t"] > best[1]):
            best = (r["label"], s["t"])
    if best is None:
        res["verdict"] = "FAIL: no filter " + ("beat the luck check" if not cand else "improved the base in VALIDATION")
    else:
        rule, name = best[0].split(" ", 1)
        B = T[T.rule == rule]
        Fn = period(B, "final"); Fk = Fn[apply(Fn, FL[name])]
        s = bt.summarize(Fk, best[0]); s["t"] = tstat(Fk); s["base_mean_bp"] = round(Fn.net.mean() * 1e4, 2)
        bt.log_attempt(md5, f"E68:{best[0]}", "final", s)
        res["final"] = s; res["final_variant"] = best[0]
        Ak = B[apply(B, FL[name])]
        ay = Ak.groupby(Ak.time.dt.year).net.mean()
        ok = (s["mean_bp"] > 0 and s["t"] >= 2 and (ay > 0).mean() >= 0.6 and s["mean_bp"] > s["base_mean_bp"]
              and (s["n"] >= 100 or (s["n"] >= 50 and s["t"] >= 3)) and s["ex_top5pct_bp"] > 0)
        res["all_years_pos"] = [int((ay > 0).sum()), int(len(ay))]
        res["verdict"] = "PASS" if ok else "FAIL at FINAL"
        if ok:
            res["leverage"] = bt.leverage_table(Ak[Ak.time >= pd.Timestamp("2024-01-01", tz="UTC")])
            res["leverage_all"] = bt.leverage_table(Ak)
    write_result("E68", res)
    print(res["promoted"], res["validation"], res["final"], res["verdict"])
