"""Bot-2 shared helpers: crypto-only universe, daily/4h panels from 1h, daily funding, portfolio engine, stats."""
import sys, os, json, glob
sys.path.insert(0, "/home/user/Aura")
import numpy as np, pandas as pd
from edges.lib import bt

SCR = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/research2"
HERE = os.path.dirname(os.path.abspath(__file__))
MANUAL = set("""USDCUSDT USDEXUSDT FDUSDUSDT TUSDUSDT BUSDUSDT USDPUSDT USDBRLUSDT BTCDOMUSDT DEFIUSDT FOOTBALLUSDT BLUEBIRDUSDT
XAUUSDT XAUTUSDT PAXGUSDT XAGUSDT XPTUSDT XPDUSDT COPPERUSDT NATGASUSDT AAPLUSDT TSLAUSDT NVDAUSDT MSFTUSDT AMZNUSDT GOOGLUSDT
METAUSDT COINUSDT MSTRUSDT HOODUSDT SPYUSDT QQQUSDT IWMUSDT TQQQUSDT SQQQUSDT SOXLUSDT SOXSUSDT UVXYUSDT TSLLUSDT NVDLUSDT
STABLEUSDT""".split())


def excluded(write=True):
    fn = os.path.join(HERE, "excluded.json")
    if os.path.exists(fn):
        return set(json.load(open(fn))["excluded"])
    ex = set(MANUAL)
    for f in sorted(glob.glob(f"{bt.DATA}/1h/*.parquet")):
        s = os.path.basename(f)[:-8]
        try:
            d = bt.load(s)
        except Exception:
            continue
        if len(d) < 24 * 20:
            continue
        rng = (d.h - d.l) / d.c
        wk = d.index.dayofweek >= 5
        a, b = rng[wk].median(), rng[~wk].median()
        if b > 0 and a / b < 0.35:
            ex.add(s)
    if write:
        json.dump(dict(rule="manual list + weekend/weekday median hourly range < 0.35", excluded=sorted(ex)),
                  open(fn, "w"), indent=0)
    return ex


def build_panels():
    """daily (00 UTC) and 4h panels for all crypto perps; cached in SCR."""
    fd = f"{SCR}/daily.pkl"
    if os.path.exists(fd):
        return
    ex = excluded()
    D = {k: {} for k in ("o", "h", "l", "c", "qv")}
    H4 = {k: {} for k in ("o", "h", "l", "c", "qv")}
    FUN = {}
    for f in sorted(glob.glob(f"{bt.DATA}/1h/*.parquet")):
        s = os.path.basename(f)[:-8]
        if s in ex:
            continue
        try:
            d = bt.load(s)
        except Exception:
            continue
        if len(d) < 24 * 30:
            continue
        for tgt, rule in ((D, "1D"), (H4, "4h")):
            g = d.resample(rule)
            tgt["o"][s] = g.o.first(); tgt["h"][s] = g.h.max(); tgt["l"][s] = g.l.min(); tgt["c"][s] = g.c.last()
            tgt["qv"][s] = g.qv.sum(min_count=1)
        try:
            fr = bt.funding(s)
            FUN[s] = fr.resample("1D").sum(min_count=1)   # funding settled during day d (00,08,16 of day d)
        except Exception:
            pass
    pd.to_pickle({k: pd.DataFrame(v).sort_index().astype("float32") for k, v in D.items()}, fd)
    pd.to_pickle({k: pd.DataFrame(v).sort_index().astype("float32") for k, v in H4.items()}, f"{SCR}/h4.pkl")
    pd.to_pickle(pd.DataFrame(FUN).sort_index(), f"{SCR}/fund_daily.pkl")


def daily():
    return pd.read_pickle(f"{SCR}/daily.pkl")


def h4():
    return pd.read_pickle(f"{SCR}/h4.pkl")


def fund_daily():
    return pd.read_pickle(f"{SCR}/fund_daily.pkl")


# ------------------------------------------------------------- portfolio engine (daily)
def run_book(W, C, QV, FUND=None, delist_pen=0.05, cost_mult=1.0):
    """W: target weights decided at close of day t (index = day t label, meaning bar of day t closed at t+1 00:00).
    Convention: daily bars are labelled by their open (00:00 UTC). Weight W.loc[d] is set at the CLOSE of bar d
    (i.e. at 00:00 of d+1, trading at close price c[d]) and earns return of bar d+1 (c[d+1]/c[d]-1).
    Costs: |dW| * (taker + slippage(qv24 of bar d)). Funding: weight held during bar d+1 pays FUND[d+1] * w (long pays).
    Delisting: if c[d+1] is NaN while held and the coin never trades again -> exit at c[d], -5% against the holder.
    Returns DataFrame indexed by day d+1 with gross, cost, fund, net, turnover, n_orders."""
    W = W.reindex(columns=C.columns).fillna(0.0)
    C = C.reindex(W.index)
    ret = (C.shift(-1) / C - 1)                     # return of next bar, aligned with decision day
    alive_later = C[::-1].notna().cummax()[::-1].shift(-1).fillna(False).astype(bool)  # trades again after d
    dead = ret.isna() & (W != 0) & ~alive_later & C.notna()
    ret = ret.where(~dead, -0.05 * np.sign(W))      # holder loses 5% whatever side (sign multiplied below)
    ret = ret.fillna(0.0)
    Wprev = W.shift(1).fillna(0.0)
    # drift: weights are reset to target each day decision (rebalance-to-target only on rebalance days is done by caller)
    dW = (W - Wprev).abs()
    sl = pd.DataFrame(bt.slippage(QV.reindex(W.index).reindex(columns=W.columns).fillna(0).values),
                      index=W.index, columns=W.columns)
    cost = (dW * (bt.TAKER + sl) * cost_mult).sum(1)
    gross = (W * ret).where(~dead, -0.05 * W.abs()).sum(1)
    fund = pd.Series(0.0, index=W.index)
    if FUND is not None:
        F = FUND.reindex(index=W.index, columns=W.columns).shift(-1)
        Fl = F.fillna(0.0003)   # missing: 0.01%/8h charged to longs
        Fs = F.fillna(0.0)
        fund = -(W.clip(lower=0) * Fl + W.clip(upper=0) * Fs).sum(1)
    out = pd.DataFrame(dict(gross=gross, cost=-cost, fund=fund))
    out["net"] = out.gross + out.cost + out.fund
    out["n_orders"] = ((W - Wprev).abs() > 1e-9).sum(1)
    out["turnover"] = dW.sum(1)
    out.index = out.index + pd.Timedelta(days=1)
    return out


def hold_between(Wreb, index, C, mode="drift"):
    """Expand rebalance-day targets to daily weights. 'hold': keep target weights constant between rebalances
    (equivalent to tiny daily rebalancing, cost of it ignored -> we use drift instead). 'drift': weights drift with
    prices between rebalances (no trading), which is what a real book does."""
    Wd = Wreb.reindex(index).ffill().fillna(0.0)
    if mode == "hold":
        return Wd
    # drift: w_t = w_reb * P_t/P_reb normalised by the book value growth
    R = (C.reindex(index) / C.reindex(index).shift(1)).fillna(1.0)
    W = Wd.copy()
    vals = W.values; Rv = R.values; reb = set(np.where(Wreb.reindex(index).notna().any(1).values)[0])
    for i in range(1, len(index)):
        if i in reb:
            continue
        w = vals[i - 1] * Rv[i]
        tot = 1 + (vals[i - 1] * (Rv[i] - 1)).sum()
        vals[i] = w / tot if tot > 0 else 0
    return pd.DataFrame(vals, index=index, columns=W.columns)


def stats(daily_df, label=""):
    """daily_df: output of run_book (index = day). Returns protocol stats."""
    d = daily_df.dropna(subset=["net"])
    if len(d) < 5:
        return dict(label=label, n=0)
    tr = pd.DataFrame(dict(time=d.index, net=d.net.values))
    s = bt.summarize(tr, label)
    eq = (1 + d.net).cumprod()
    yrs = (d.index[-1] - d.index[0]).days / 365.25
    s["cagr"] = round(float(eq.iloc[-1] ** (1 / max(yrs, 1e-9)) - 1), 4)
    s["max_dd"] = round(float((eq / eq.cummax() - 1).min()), 4)
    s["total"] = round(float(eq.iloc[-1] - 1), 4)
    s["sharpe"] = round(float(d.net.mean() / d.net.std() * np.sqrt(365)), 2) if d.net.std() > 0 else None
    s["orders"] = int(d.n_orders.sum()); s["orders_per_day"] = round(float(d.n_orders.mean()), 3)
    s["gross_bp"] = round(d.gross.mean() * 1e4, 2); s["cost_bp"] = round(d.cost.mean() * 1e4, 2)
    s["fund_bp"] = round(d.fund.mean() * 1e4, 2)
    s["exposure"] = None
    return s


def weakest_year(daily_df, years=(2020, 2021, 2022, 2023)):
    d = daily_df.net
    m = [d[d.index.year == y].mean() for y in years]
    m = [x for x in m if x == x]
    return min(m) if m else -np.inf


def period(df, p):
    a, b = bt.PERIODS[p]
    return df[(df.index >= a) & (df.index < b)]


def top_n(QV, C, n, asof_index, min_hist=60, exclude=()):
    """For each date in asof_index: list of top-n syms by trailing 30d quote volume (days before and incl. the date)."""
    qv30 = QV.rolling(30, min_periods=20).sum()
    hist = C.notna().cumsum()
    out = {}
    for d in asof_index:
        q = qv30.loc[d]
        ok = (hist.loc[d] >= min_hist) & C.loc[d].notna() & q.notna()
        q = q[ok].drop([x for x in exclude if x in q.index], errors="ignore")
        out[d] = list(q.sort_values(ascending=False).index[:n])
    return out


def trim(P):
    """drop the last (possibly partial) bar."""
    return {k: v.iloc[:-1] for k, v in P.items()}


def rv_daily(syms):
    """daily realised variance from hourly log returns (sum of squares within the UTC day)."""
    out = {}
    for s in syms:
        d = bt.load(s)
        r = np.log(d.c).diff()
        out[s] = (r ** 2).resample("1D").sum(min_count=12)
    return pd.DataFrame(out)


def fund_bars(syms, rule):
    out = {}
    for s in syms:
        try:
            out[s] = bt.funding(s).resample(rule).sum(min_count=1)
        except Exception:
            pass
    return pd.DataFrame(out)


def crypto_ok():
    return lambda s: s not in excluded()


# ------------------------------------------------------------- fast rebalanced book (numba), daily bars
import numba


@numba.njit(cache=True)
def _book(T_, reb, RL, RS, CR, FL, FS):
    T, N = RL.shape
    w = np.zeros(N)
    gross = np.zeros(T); cost = np.zeros(T); fund = np.zeros(T); nord = np.zeros(T)
    for t in range(T):
        if reb[t]:
            for j in range(N):
                x = T_[t, j]
                if x != x:
                    x = 0.0
                d = abs(x - w[j])
                if d > 1e-12:
                    cost[t] += d * CR[t, j]; nord[t] += 1
                w[j] = x
        g = 0.0; f = 0.0
        for j in range(N):
            if w[j] > 0:
                g += w[j] * RL[t, j]; f -= w[j] * FL[t, j]
            elif w[j] < 0:
                g += w[j] * RS[t, j]; f -= w[j] * FS[t, j]
        gross[t] = g; fund[t] = f
        # drift
        for j in range(N):
            if w[j] != 0:
                r = RL[t, j] if w[j] > 0 else RS[t, j]
                if RL[t, j] == -0.05 and RS[t, j] == 0.05:   # dead marker -> closed
                    w[j] = 0.0
                else:
                    w[j] = w[j] * (1 + r) / (1 + g) if (1 + g) > 0 else 0.0
    return gross, cost, fund, nord


class Book:
    """Precomputes arrays for a set of columns on the daily grid. Row t = decision at the end of day t."""

    def __init__(self, C, QV, FUND, cols=None):
        cols = list(C.columns) if cols is None else cols
        C = C[cols].astype(float)
        self.idx, self.cols = C.index, cols
        ret = C.shift(-1) / C - 1
        alive_later = C.notna()[::-1].cummax()[::-1].shift(-1, fill_value=False).astype(bool)
        dead = ret.isna() & C.notna() & ~alive_later
        RL = ret.fillna(0.0).values.copy(); RS = RL.copy()
        RL[dead.values] = -0.05; RS[dead.values] = 0.05
        self.RL, self.RS = RL, RS
        qv24 = QV[cols].reindex(C.index).fillna(0).values
        self.CR = bt.TAKER + bt.slippage(qv24)
        F = FUND.reindex(index=C.index, columns=cols).shift(-1)
        self.FL, self.FS = F.fillna(0.0003).values, F.fillna(0.0).values
        self.ci = {c: i for i, c in enumerate(cols)}

    def run(self, targets, reb_mask):
        """targets: ndarray [T, N] (rows used only where reb_mask). Returns DataFrame indexed by day t+1."""
        g, c, f, n = _book(np.ascontiguousarray(targets, dtype=np.float64), reb_mask.astype(np.bool_), self.RL, self.RS,
                           self.CR, self.FL, self.FS)
        out = pd.DataFrame(dict(gross=g, cost=-c, fund=f, n_orders=n), index=self.idx + pd.Timedelta(days=1))
        out["net"] = out.gross + out.cost + out.fund
        return out
