"""E50 time-series momentum (plan edges/plans/E50_tsmom_trend.md, common E50_common_bot2.md)."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, numba
from edges.lib import bt
import lib2

MD5 = hashlib.md5(open(os.path.join(bt.ROOT, "plans/E50_tsmom_trend.md"), "rb").read()).hexdigest()
OUT = f"{lib2.SCR}/e50"
os.makedirs(OUT, exist_ok=True)
SIGS = ["R10", "R20", "R40", "R60", "R120", "COMBO", "EMA10_40", "EMA20_100"]


@numba.njit
def band_path(target, band):
    T, N = target.shape
    w = np.zeros_like(target)
    for j in range(N):
        cur = 0.0
        for i in range(T):
            x = target[i, j]
            if x != x:
                x = 0.0
            if (x == 0.0) or (cur == 0.0) or (np.sign(x) != np.sign(cur)) or abs(x - cur) > band:
                cur = x
            w[i, j] = cur
    return w


def signal(C, name, bpd):
    lc = np.log(C)
    if name.startswith("R"):
        L = int(name[1:]) * bpd
        return np.sign(lc - lc.shift(L))
    if name == "COMBO":
        return sum(np.sign(lc - lc.shift(L * bpd)) for L in (20, 60, 120)) / 3
    f, s = [int(x) for x in name[3:].split("_")]
    return np.sign(C.ewm(span=f * bpd, adjust=False).mean() - C.ewm(span=s * bpd, adjust=False).mean())


def setup(tf):
    P = lib2.trim(lib2.daily() if tf == "1d" else lib2.h4())
    bpd = 1 if tf == "1d" else 6
    D = lib2.trim(lib2.daily())
    ex = lib2.excluded()
    # top-10 membership, re-selected on the 1st of each month (daily data), forward-filled to bars
    months = D["c"].index[D["c"].index.day == 1]
    top = lib2.top_n(D["qv"], D["c"], 10, months, exclude=ex)
    members = sorted(set(sum(top.values(), [])) | {"BTCUSDT", "ETHUSDT"})
    C = P["c"][members].astype(float)
    QV = P["qv"][members].astype(float).rolling(bpd, min_periods=1).sum()   # trailing 24h quote volume
    M = pd.DataFrame(0.0, index=D["c"].index, columns=members)
    for d, l in top.items():
        M.loc[d, l] = 1.0
    M = M.where(np.broadcast_to((M.index.day == 1)[:, None], M.shape)).ffill().fillna(0.0)  # decided at end of the 1st
    if tf == "4h":
        M = M.shift(1)   # day d's selection is known only after day d closes
    M = M.reindex(C.index, method="ffill").fillna(0.0)
    rv = lib2.rv_daily(members).rolling(30, min_periods=20).mean() * 365   # annual variance
    vol = np.sqrt(rv).shift(0)                                             # rv of day d known at end of day d
    vol = vol.reindex(C.index, method="ffill")
    if tf == "4h":   # day d's rv is only complete at day end: use the previous day's for intraday 4h bars
        vol = np.sqrt(rv).shift(1).reindex(C.index, method="ffill")
    rule = "1D" if tf == "1d" else "4h"
    F = lib2.fund_bars(members, rule).reindex(C.index)
    if tf == "4h":   # fill missing funding per settlement (0.01% per 00/08/16 settlement) - fixed 2026-11-07
        settle = np.isin(C.index.hour, (0, 8, 16))
        fill = np.repeat(np.where(settle, 0.0001, 0.0)[:, None], F.shape[1], axis=1)
        F = pd.DataFrame(np.where(F.notna().values, F.values, fill), index=C.index, columns=F.columns)
    return dict(C=C, QV=QV, M=M, vol=vol, F=F, bpd=bpd, members=members)


def fast_prep(S):
    C = S["C"]
    R = (C.shift(-1) / C - 1).fillna(0.0).values
    CR = bt.TAKER + bt.slippage(S["QV"].fillna(0).values)
    F = S["F"].reindex(columns=C.columns).shift(-1)
    FL, FS = F.fillna(0.0003).values, F.fillna(0.0).values
    day = (C.index + (C.index[1] - C.index[0])).floor("1D")
    yrs = day.year.values
    disc = (yrs >= 2020) & (yrs <= 2023)
    cols = {c: i for i, c in enumerate(C.columns)}
    return dict(R=R, CR=CR, FL=FL, FS=FS, day=day, yrs=yrs, disc=disc, cols=cols)


def fast_weakest(FP, W):
    """W: ndarray [T, N] full-column weights. weakest discovery-year mean daily net."""
    dW = np.abs(np.diff(W, axis=0, prepend=0))
    net = (W * FP["R"]).sum(1) - (dW * FP["CR"]).sum(1) - (np.clip(W, 0, None) * FP["FL"] + np.clip(W, None, 0) * FP["FS"]).sum(1)
    d = FP["disc"]
    s = pd.Series(np.log1p(net[d]), index=FP["day"][d]).groupby(level=0).sum()
    s = np.expm1(s)
    return s.groupby(s.index.year).mean().min()


def variant_w(S, asset, sig_df, mode, sizing):
    C = S["C"]
    s = sig_df.values
    if mode == "lf":
        s = np.clip(s, 0, None)
    if sizing == "vt":
        tgt = np.nan_to_num(s * np.clip(0.40 / S["vol"].values, None, 1.0))
        w = band_path(tgt, 0.10)
    else:
        w = np.nan_to_num(s)
    if asset == "BTC":
        m = np.zeros(w.shape[1]); m[S["C"].columns.get_loc("BTCUSDT")] = 1; w = w * m
    elif asset == "ETH":
        m = np.zeros(w.shape[1]); m[S["C"].columns.get_loc("ETHUSDT")] = 1; w = w * m
    else:
        w = w * S["M"].values / 10.0
    return w


def run_book_bars(W, C, QV, F, bar):
    out = lib2.run_book(W, C, QV, F)
    out.index = out.index - pd.Timedelta(days=1) + bar
    return out


def to_daily(o):
    d = o[["gross", "cost", "fund", "net", "n_orders", "turnover"]].copy()
    d["lnet"] = np.log1p(d.net)
    g = d.resample("1D").agg(dict(gross="sum", cost="sum", fund="sum", lnet="sum", n_orders="sum", turnover="sum"))
    g["net"] = np.expm1(g.lnet)
    return g.drop(columns="lnet")


def variant(S, asset, sig_df, mode, sizing):
    C = S["C"]
    s = sig_df.copy()
    if mode == "lf":
        s = s.clip(lower=0)
    if sizing == "vt":
        scale = (0.40 / S["vol"]).clip(upper=1.0)
        tgt = (s * scale).fillna(0.0).values
        w = band_path(tgt, 0.10)
    else:
        w = s.fillna(0.0).values
    W = pd.DataFrame(w, index=C.index, columns=C.columns)
    if asset == "BTC":
        W = W[["BTCUSDT"]]
    elif asset == "ETH":
        W = W[["ETHUSDT"]]
    else:
        W = W * S["M"] / 10.0
    bar = C.index[1] - C.index[0]
    o = run_book_bars(W, C[W.columns], S["QV"][W.columns], S["F"].reindex(columns=W.columns), bar)
    return to_daily(o) if bar < pd.Timedelta(days=1) else o


def bench(S, asset):
    C = S["C"]
    if asset == "BTC":
        W = pd.DataFrame(1.0, index=C.index, columns=["BTCUSDT"])
    elif asset == "ETH":
        W = pd.DataFrame(1.0, index=C.index, columns=["ETHUSDT"])
    else:
        W = S["M"] / 10.0
    W = W.where(C[W.columns].notna(), 0.0)
    bar = C.index[1] - C.index[0]
    o = run_book_bars(W, C[W.columns], S["QV"][W.columns], S["F"].reindex(columns=W.columns), bar)
    return to_daily(o) if bar < pd.Timedelta(days=1) else o


def main():
    res = {"plan": "E50_tsmom_trend", "md5": MD5, "variants": [], "bench": {}}
    rng = np.random.default_rng(50)
    NNULL = int(os.environ.get("NNULL", 200))
    null_best = np.full(NNULL, -np.inf)
    store = {}
    for tf in ("1d", "4h"):
        S = setup(tf)
        C = S["C"]; T = len(C)
        sigs = {n: signal(C, n, S["bpd"]) for n in SIGS}
        FP = fast_prep(S)
        offs = rng.integers(180 * S["bpd"], T - 180 * S["bpd"], size=NNULL)
        for asset in ("BTC", "ETH", "TOP10"):
            b = bench(S, asset)
            for p in ("discovery", "validation", "final"):
                res["bench"][f"{tf}_{asset}_{p}"] = lib2.stats(lib2.period(b, p), f"bh_{tf}_{asset}_{p}")
            for sn in SIGS:
                for mode in ("lf", "ls"):
                    for sizing in ("fx", "vt"):
                        name = f"{tf}_{asset}_{sn}_{mode}_{sizing}"
                        o = variant(S, asset, sigs[sn], mode, sizing)
                        dsc = lib2.period(o, "discovery")
                        st = lib2.stats(dsc, name); w = lib2.weakest_year(dsc)
                        st["weakest_year_bp"] = round(w * 1e4, 2)
                        bt.log_attempt(MD5, name, "discovery", st)
                        res["variants"].append(st)
                        store[name] = o
                        for k in range(NNULL):
                            sh = pd.DataFrame(np.roll(sigs[sn].values, offs[k], axis=0), index=C.index, columns=C.columns)
                            null_best[k] = max(null_best[k], fast_weakest(FP, variant_w(S, asset, sh, mode, sizing)))
                        print(name, st["mean_bp"], st["t_week"], st["weakest_year_bp"], st["cagr"], st["max_dd"],
                              st["orders_per_day"], flush=True)
        pd.to_pickle({k: v for k, v in store.items() if k.startswith(tf)}, f"{OUT}/store_{tf}.pkl")
        store = {}
    res["null_best_weakest_bp"] = [round(x * 1e4, 3) for x in null_best]
    json.dump(res, open(f"{OUT}/disc.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
