"""Shared backtest toolkit for edge research. Every research bot uses this so results are comparable.

Rules baked in (see edges/PROTOCOL.md):
  * costs on every fill: taker 0.05% + liquidity-scaled slippage (0.02%..0.40% per side), maker 0.02% + 0 slippage
  * periods: DISCOVERY 2020-01..2023-12, VALIDATION 2024-01..2024-12, FINAL 2025-01..latest
  * t-stats are clustered by ISO week (trades in the same week are not independent)
  * leverage is simulated with intrabar adverse excursion -> liquidation, never by multiplying returns
"""
import glob, hashlib, json, os, time
import numpy as np
import pandas as pd

DATA = os.environ.get("OMEGA_DATA", "/home/user/data")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERIODS = {"discovery": ("2020-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
           "final": ("2025-01-01", "2100-01-01")}
TAKER, MAKER = 0.0005, 0.0002


# ---------------------------------------------------------------- data
def load(sym, tf="1h"):
    df = pd.read_parquet(f"{DATA}/{tf}/{sym}.parquet")
    df["t"] = pd.to_datetime(df.ts, unit="ms", utc=True)
    df = df.set_index("t")
    df.loc[df.v <= 0, ["o", "h", "l", "c"]] = np.nan  # volume-0 candles are missing data
    return df


def universe(tf="1h", min_rows=24 * 60):
    out = []
    for f in sorted(glob.glob(f"{DATA}/{tf}/*.parquet")):
        s = os.path.basename(f)[:-8]
        out.append(s)
    return out


def panel(syms, tf="1h", fields=("o", "h", "l", "c", "qv")):
    """Wide frames {field: DataFrame[time x sym]} on a common UTC grid."""
    cols = {f: {} for f in fields}
    for s in syms:
        try:
            d = load(s, tf)
        except FileNotFoundError:
            continue
        for f in fields:
            cols[f][s] = d[f]
    return {f: pd.DataFrame(v).sort_index() for f, v in cols.items()}


def funding(sym):
    f = pd.read_parquet(f"{DATA}/funding/{sym}.parquet")
    f["t"] = pd.to_datetime(f.ts, unit="ms", utc=True)
    return f.set_index("t").rate


# ---------------------------------------------------------------- costs
def slippage(quote_vol_24h):
    """Per-side slippage from 24h quote volume (USDT). Deep books ~2 bp, thin ~40 bp."""
    qv = np.asarray(quote_vol_24h, dtype=float)
    s = np.where(qv >= 1e9, 0.0002, np.where(qv >= 2e8, 0.0004, np.where(qv >= 5e7, 0.0008,
                 np.where(qv >= 1e7, 0.0015, np.where(qv >= 2e6, 0.0025, 0.0040)))))
    return s


def round_trip_cost(qv24, entry="taker", exit="taker"):
    sl = slippage(qv24)
    e = TAKER + sl if entry == "taker" else MAKER
    x = TAKER + sl if exit == "taker" else MAKER
    return e + x


# ---------------------------------------------------------------- evaluation
def tstat_weekly(trades):
    """trades: DataFrame with 'time' (entry, tz-aware) and 'net' (fractional return). Week-clustered t of the mean."""
    if len(trades) < 3:
        return np.nan
    wk = trades.groupby(trades.time.dt.to_period("W"))["net"].agg(["sum", "count"])
    mu = trades.net.mean()
    resid = trades.net - mu
    g = resid.groupby(trades.time.dt.to_period("W")).sum()
    var = (g ** 2).sum() / (len(trades) ** 2)
    return float(mu / np.sqrt(var)) if var > 0 else np.nan


def summarize(trades, label=""):
    """Standard report for a trade list (columns: time, sym, net, [mae], [gross])."""
    if len(trades) == 0:
        return dict(label=label, n=0)
    t = trades.sort_values("time")
    net = t.net
    k = max(1, int(len(t) * 0.05))
    yearly = t.groupby(t.time.dt.year).net.agg(["mean", "count"])
    out = dict(label=label, n=int(len(t)), mean_bp=round(net.mean() * 1e4, 2), median_bp=round(net.median() * 1e4, 2),
               win=round(float((net > 0).mean()), 3), t_week=round(tstat_weekly(t), 2),
               worst=round(float(net.min()), 4), best=round(float(net.max()), 4),
               ex_top5pct_bp=round(float(net.sort_values().iloc[:-k].mean() * 1e4), 2),
               years={int(y): [round(r["mean"] * 1e4, 1), int(r["count"])] for y, r in yearly.iterrows()},
               years_pos=int((yearly["mean"] > 0).sum()), years_total=int(len(yearly)),
               per_day=round(len(t) / max(1, (t.time.max() - t.time.min()).days), 3))
    if "mae" in t:
        out["mae_p99"] = round(float(t.mae.quantile(0.01)), 4)
        out["mae_worst"] = round(float(t.mae.min()), 4)
    return out


def split(trades):
    return {p: trades[(trades.time >= a) & (trades.time < b)] for p, (a, b) in PERIODS.items()}


def random_entry_benchmark(trades, ret_fn, n=200, seed=0):
    """Luck check: same number of trades, same symbols, random times. ret_fn(sym, time) -> net return or nan.
    Returns distribution of mean returns; compare the real mean to its 95th/99th percentile."""
    rng = np.random.default_rng(seed)
    times = trades.time.values
    lo, hi = times.min(), times.max()
    means = []
    for _ in range(n):
        rs = []
        for s in trades.sym.values:
            tt = pd.Timestamp(rng.integers(lo.astype("int64"), hi.astype("int64"))).tz_localize("UTC").floor("h")
            r = ret_fn(s, tt)
            if r == r:
                rs.append(r)
        means.append(np.mean(rs) if rs else np.nan)
    return np.array(means)


# ---------------------------------------------------------------- leverage / account
def account(trades, leverage=1.0, margin_frac=0.05, mm=0.005, start=100.0, max_open=5):
    """Simulate an account. Each trade puts margin_frac of current equity as margin at `leverage`.
    trades need: time, exit_time, net (unlevered, after costs), mae (worst adverse unlevered move, <= 0).
    Liquidation when mae <= -(1/leverage - mm): the margin is lost (plus fees already in net).
    Returns dict with final equity, max drawdown, liquidations, and the equity curve."""
    t = trades.sort_values("time").reset_index(drop=True)
    eq, peak, mdd, liq = start, start, 0.0, 0
    open_pos = []  # (exit_time, margin, pnl)
    curve = []
    liq_line = -(1.0 / leverage - mm)
    for _, r in t.iterrows():
        # close anything finished
        still = []
        for (xt, m, p) in open_pos:
            if xt <= r.time:
                eq += m + p
            else:
                still.append((xt, m, p))
        open_pos = still
        if len(open_pos) >= max_open or eq <= 1:
            continue
        m = eq * margin_frac
        mae = r.get("mae", np.nan)
        if mae == mae and mae <= liq_line:
            pnl = -m
            liq += 1
        else:
            pnl = m * leverage * r.net
            pnl = max(pnl, -m)
        eq -= m
        open_pos.append((r.exit_time, m, pnl))
        tot = eq + sum(mm_ for _, mm_, _ in open_pos)
        peak = max(peak, tot)
        mdd = min(mdd, tot / peak - 1)
        curve.append((r.time, tot))
    for (_, m, p) in open_pos:
        eq += m + p
    return dict(leverage=leverage, margin_frac=margin_frac, final=round(eq, 2), max_dd=round(mdd, 3),
                liquidations=liq, trades=len(curve), curve=curve)


def leverage_table(trades, levs=(1, 2, 3, 5, 10, 20, 40), margin_frac=0.05):
    rows = []
    for L in levs:
        a = account(trades, leverage=L, margin_frac=margin_frac)
        a.pop("curve")
        rows.append(a)
    return rows


# ---------------------------------------------------------------- plan discipline
def register_plan(plan_path):
    """Fingerprint a plan before touching its test data. Appends to edges/registry.jsonl and returns md5."""
    md5 = hashlib.md5(open(plan_path, "rb").read()).hexdigest()
    with open(os.path.join(ROOT, "registry.jsonl"), "a") as f:
        f.write(json.dumps(dict(plan=os.path.relpath(plan_path, ROOT), md5=md5, at=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                                                time.gmtime()))) + "\n")
    return md5


def log_attempt(plan_md5, name, period, stats):
    """Every variant ever evaluated is counted (multiple-testing record)."""
    with open(os.path.join(ROOT, "attempts.jsonl"), "a") as f:
        f.write(json.dumps(dict(plan=plan_md5, name=name, period=period, **{k: v for k, v in stats.items()
                                                                            if k != "years"}), default=str) + "\n")
