"""Backtester for any strategy in edges/bots/strategies — the same signals the live runner trades.

Pipeline
  1. data: parquet files in $OMEGA_DATA/<tf>/ via edges/lib/bt.py `load` (volume-0 bars are missing), on a dense grid.
  2. signals: `strategy.scan()` (vectorised; proven equal to calling `signals()` bar by bar) or engine="bar", which calls
     `signals()` at every bar exactly as the live runner does (slow; for checks).
  3. execution, bar by bar per (strategy, coin): one order or position per coin at a time (a signal while busy is ignored,
     as in the research); a limit fills only if a later bar trades THROUGH it (low < limit for a long) within
     valid_for_bars; a market order fills at the next bar's open; exits at the close of the exit bar (next valid close
     after a gap); optional stop from intrabar extremes (gap-through fills at the open); worst adverse excursion (mae)
     from intrabar lows for the liquidation check; costs from bt.round_trip_cost (maker for filled limits, taker +
     liquidity slippage otherwise); funding charged on positions held across a funding time when a funding file exists.
  4. report: bt.summarize per period, bt.leverage_table (5% of equity margin, PROTOCOL.md), and a fixed-seat account
     (100 USDT, `margin_usdt` per trade, max open positions, liquidation when mae passes 1/L - 0.5%).
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

from edges.lib import bt
from edges.bots.core import Signal, dense, tf_delta
from edges.bots import strategies as S

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 0.005


# ---------------------------------------------------------------- data
def available(tf="1h"):
    return sorted(os.path.basename(f)[:-8] for f in glob.glob(f"{bt.DATA}/{tf}/*.parquet"))


def load_coin(sym, tf="1h", start=None, end=None, pad_bars=0):
    """Dense frame (o h l c v qv) and meta {first_ts, first_valid_ts, last_valid_ts}."""
    d = bt.load(sym, tf)
    d = d[~d.index.duplicated(keep="last")].sort_index()
    meta = dict(first_ts=d.index[0])
    ok = np.isfinite(d.c.values)
    if not ok.any():
        return None, meta
    meta["first_valid_ts"] = d.index[int(np.argmax(ok))]
    meta["last_valid_ts"] = d.index[len(ok) - 1 - int(np.argmax(ok[::-1]))]
    d = dense(d[["o", "h", "l", "c", "v", "qv"]].astype(float), tf)
    if start is not None:
        d = d[d.index >= pd.Timestamp(start, tz="UTC") - pad_bars * tf_delta(tf)]
    if end is not None:
        d = d[d.index < pd.Timestamp(end, tz="UTC")]
    return d, meta


_FUND = {}


def funding_series(sym):
    if sym not in _FUND:
        try:
            _FUND[sym] = bt.funding(sym).sort_index()
        except (FileNotFoundError, OSError, ValueError):
            _FUND[sym] = None
    return _FUND[sym]


# ---------------------------------------------------------------- execution (one coin, one strategy)
def simulate(sym, df, sigs, tf="1h", stop_pct=None, gap_policy="next", funding=True, data_end=None, last_valid=None,
             strategy=""):
    """sigs: [(bar_time, Signal)] for this coin, time-sorted. Returns trade records (filled and missed limits)."""
    if not sigs:
        return []
    idx = df.index
    o, h, l, c = (df[k].values for k in ("o", "h", "l", "c"))
    qv24 = df.qv.rolling(24, min_periods=1).sum().values
    n = len(c)
    pos_of = {t: i for i, t in enumerate(idx)}
    step = tf_delta(tf)
    fund = funding_series(sym) if funding else None
    delisted = (last_valid is not None and data_end is not None and last_valid < data_end - pd.Timedelta(hours=48))
    lv_i = pos_of.get(last_valid, n - 1) if last_valid is not None else n - 1
    busy, out = -1, []
    for t, sg in sigs:
        i = pos_of.get(t)
        if i is None or i < busy:
            continue
        sgn = 1.0 if sg.side == "long" else -1.0
        rec = dict(strategy=strategy or sg.strategy, sym=sym, signal_time=t, side=sg.side, kind=sg.entry,
                   qv24=float(qv24[i]), valid_until=idx[min(n - 1, i + sg.valid_for_bars)] + step)
        if sg.entry == "limit":
            f = None
            for j in range(i + 1, min(n, i + 1 + sg.valid_for_bars)):
                if (sgn > 0 and l[j] < sg.price) or (sgn < 0 and h[j] > sg.price):
                    f = j
                    break
            if f is None:
                busy = i + sg.valid_for_bars
                if i + sg.valid_for_bars < n:
                    out.append(dict(rec, status="missed", time=t, exit_time=rec["valid_until"]))
                continue
            ei, entry, xi = f, float(sg.price), f + sg.hold_bars
        else:
            ei = i + 1
            if ei >= n or not (o[ei] > 0):
                continue
            entry, xi = float(o[ei]), i + sg.hold_bars
        # exit bar and price
        reason, xpx, xk = "time", None, None
        sp = sg.stop_pct if sg.stop_pct is not None else stop_pct
        stop_px = entry * (1 - sgn * sp) if sp else None
        last = min(xi, n - 1)
        if delisted:
            last = min(last, lv_i)
        if stop_px is not None:
            for k in range(ei, last + 1):
                if not np.isfinite(l[k]):
                    continue
                hit = (l[k] <= stop_px) if sgn > 0 else (h[k] >= stop_px)
                if hit:
                    gap = (k > ei or sg.entry != "limit") and ((sgn > 0 and o[k] < stop_px) or (sgn < 0 and o[k] > stop_px))
                    xpx, xk, reason = (float(o[k]) if gap else stop_px), k, "stop"
                    break
        if xpx is None:
            if xi < n and not (delisted and xi > lv_i):
                if c[xi] > 0:
                    xpx, xk = float(c[xi]), xi
                elif gap_policy == "skip":
                    if sg.entry == "limit":
                        busy = i + sg.valid_for_bars
                    continue
                else:
                    for k in range(xi + 1, n):
                        if c[k] > 0:
                            xpx, xk, reason = float(c[k]), k, "after_gap"
                            break
            elif delisted and xi > lv_i:
                xpx, xk, reason = float(c[lv_i]) * 0.95, lv_i, "delisted"   # as E25: last close minus 5%
            if xpx is None:                                                  # data ends before the exit: still open
                if gap_policy == "skip" and sg.entry == "limit":
                    busy = i + sg.valid_for_bars
                else:
                    busy = n
                continue
        seg = l[ei:xk + 1] if sgn > 0 else h[ei:xk + 1]
        worst = np.nanmin(seg) if sgn > 0 else np.nanmax(seg)
        mae = min(0.0, sgn * (worst / entry - 1)) if np.isfinite(worst) else 0.0
        gross = sgn * (xpx / entry - 1)
        cost = float(bt.round_trip_cost(rec["qv24"], entry="maker" if sg.entry == "limit" else "taker", exit="taker"))
        fnd = 0.0
        t_out = idx[xk] + step
        if fund is not None and len(fund):
            fnd = float(sgn * fund[(fund.index > idx[ei]) & (fund.index <= t_out)].sum())
        out.append(dict(rec, status="filled", time=idx[ei], entry_time=idx[ei], entry=entry, exit_time=t_out,
                        exit=xpx, reason=reason, gross=gross, cost=cost, funding=fnd, net=gross - cost - fnd, mae=mae,
                        exit_bar=idx[xk]))
        busy = xk
    return out


# ---------------------------------------------------------------- account with fixed seats
def seat_account(trades, leverage=1, margin_usdt=5.0, start=100.0, max_open=3, mm=MM):
    """Fixed margin per trade (the live bot's sizing). Pending limits hold a seat until they fill or expire.
    Liquidation when the trade's mae passes the liquidation line: the margin is lost."""
    ev = trades.sort_values("signal_time")
    eq, peak, mdd, liq, taken, skipped = start, start, 0.0, 0, 0, 0
    book = []          # (release_time, margin, pnl)
    line = -(1.0 / leverage - mm)
    for _, r in ev.iterrows():
        now = r.signal_time
        keep = []
        for (xt, m, p) in book:
            if xt <= now:
                eq += m + p
            else:
                keep.append((xt, m, p))
        book = keep
        if len(book) >= max_open or eq < margin_usdt:
            skipped += 1
            continue
        if r.status == "missed":
            book.append((r.exit_time, 0.0, 0.0))
            continue
        if r.mae == r.mae and r.mae <= line:
            pnl, liq = -margin_usdt, liq + 1
        else:
            pnl = max(-margin_usdt, margin_usdt * leverage * r.net)
        eq -= margin_usdt
        book.append((r.exit_time, margin_usdt, pnl))
        taken += 1
        tot = eq + sum(m for _, m, _ in book)
        peak = max(peak, tot)
        mdd = min(mdd, tot / peak - 1)
    for (_, m, p) in book:
        eq += m + p
    peak = max(peak, eq)
    mdd = min(mdd, eq / peak - 1)
    return dict(leverage=leverage, margin_usdt=margin_usdt, final=round(eq, 2), max_dd=round(mdd, 3),
                liquidations=liq, trades=taken, skipped=skipped)


def max_safe_leverage(table, dd_limit=-0.35):
    ok = [r["leverage"] for r in table if r["liquidations"] == 0 and r["max_dd"] > dd_limit]
    best = 0
    for r in sorted(table, key=lambda r: r["leverage"]):            # the highest L with every lower L also safe
        if r["leverage"] in ok:
            best = r["leverage"]
        else:
            break
    return best


# ---------------------------------------------------------------- run
def run(strategy_id, syms=None, start="2020-01-01", end=None, tf=None, stop_pct=None, engine="scan",
        gap_policy="next", funding=True, max_coins=None, verbose=True):
    st = S.load(strategy_id)
    tf = tf or st.tf
    syms = syms or (st.universe if isinstance(st.universe, list) else available(tf))
    if max_coins:
        syms = syms[:max_coins]
    pad = st.lookback + 24 * 31
    data, meta = {}, {}
    t0 = time.time()
    for s in syms:
        try:
            d, m = load_coin(s, tf, start, end, pad_bars=pad)
        except (FileNotFoundError, OSError, ValueError):
            continue
        if d is None or len(d) < 50:
            continue
        data[s], meta[s] = d, m
    st.meta = meta
    data_end = max((m["last_valid_ts"] for m in meta.values()), default=None)
    t_start = pd.Timestamp(start, tz="UTC") if start else None
    t_end = pd.Timestamp(end, tz="UTC") if end else None
    if engine == "bar":
        sigs = bar_by_bar(st, data, t_start, t_end)
    else:
        sigs = st.scan(data, t_start, t_end)
    by = {}
    for t, sg in sigs:
        by.setdefault(sg.sym, []).append((t, sg))
    recs = []
    for s, lst in by.items():
        recs += simulate(s, data[s], lst, tf, stop_pct=stop_pct, gap_policy=gap_policy, funding=funding,
                         data_end=data_end, last_valid=meta[s]["last_valid_ts"], strategy=st.id)
    if verbose:
        print(f"{st.id}: {len(data)} coins, {len(sigs)} signals, {sum(r['status'] == 'filled' for r in recs)} trades "
              f"({time.time() - t0:.0f}s)", file=sys.stderr)
    return pd.DataFrame(recs), dict(coins=len(data), signals=len(sigs), data_end=str(data_end))


def bar_by_bar(st, data, start=None, end=None):
    """Call strategy.signals() at every bar with the trailing window, exactly as the live runner does."""
    times = sorted(set().union(*[d.index for d in data.values()]))
    out = []
    for t in times:
        if (start is not None and t < start) or (end is not None and t >= end):
            continue
        win = {}
        for s, d in data.items():
            if d.index[0] <= t <= d.index[-1]:
                j = d.index.get_loc(t)
                win[s] = d.iloc[max(0, j - st.lookback): j + 1]
        for sg in st.signals(win, t):
            out.append((t, sg))
    return out


def report(trades, info=None, margin_usdt=5.0, max_open=3, levs=(1, 2, 3, 5, 10, 20, 40)):
    f = trades[trades.status == "filled"].copy() if len(trades) else trades
    out = dict(info=info or {})
    if len(f) == 0:
        out["all"] = dict(n=0)
        return out
    f["time"] = pd.to_datetime(f.time, utc=True)
    f["exit_time"] = pd.to_datetime(f.exit_time, utc=True)
    out["all"] = bt.summarize(f, "all")
    out["periods"] = {p: bt.summarize(x, p) for p, x in bt.split(f).items()}
    out["exit_reasons"] = f.reason.value_counts().to_dict()
    out["gross_mean_bp"] = round(float(f.gross.mean() * 1e4), 2)
    out["cost_mean_bp"] = round(float(f.cost.mean() * 1e4), 2)
    out["funding_mean_bp"] = round(float(f.funding.mean() * 1e4), 2)
    out["leverage_table_5pct_equity"] = bt.leverage_table(f, levs=levs, margin_frac=0.05)
    out["max_leverage_protocol"] = max_safe_leverage(out["leverage_table_5pct_equity"])
    out["seat_account_100usdt"] = [seat_account(trades, L, margin_usdt, max_open=max_open) for L in levs]
    out["liquidation_mae_needed"] = {L: round(-(1 / L - MM), 4) for L in levs}
    out["share_trades_liquidated"] = {L: round(float((f.mae <= -(1 / L - MM)).mean()), 4) for L in levs}
    return out


def save(rep, name):
    os.makedirs(os.path.join(HERE, "reports"), exist_ok=True)
    p = os.path.join(HERE, "reports", f"{name}.json")
    json.dump(rep, open(p, "w"), indent=1, default=str)
    return p


def print_report(rep):
    a = rep["all"]
    if not a.get("n"):
        print("no trades")
        return
    print(f"trades {a['n']}  mean {a['mean_bp']} bp  median {a['median_bp']} bp  win {a['win']}  t(week) {a['t_week']}  "
          f"worst {a['worst']}  without best 5% {a['ex_top5pct_bp']} bp  years+ {a['years_pos']}/{a['years_total']}")
    for p, s in rep["periods"].items():
        if s.get("n"):
            print(f"  {p:<10} n {s['n']:>5}  mean {s['mean_bp']:>7} bp  t {s['t_week']}")
    print(f"  gross {rep['gross_mean_bp']} bp, costs {rep['cost_mean_bp']} bp, funding {rep['funding_mean_bp']} bp; "
          f"exits {rep['exit_reasons']}")
    print("  leverage (5% of equity margin, bt.leverage_table):")
    for r in rep["leverage_table_5pct_equity"]:
        print(f"    {r['leverage']:>3}x  final {r['final']:>10}  maxDD {r['max_dd']:>7}  liquidations {r['liquidations']}")
    print(f"  highest leverage with 0 liquidations and maxDD < 35%: {rep['max_leverage_protocol']}x")
    print("  100 USDT account, fixed seats:")
    for r in rep["seat_account_100usdt"]:
        print(f"    {r['leverage']:>3}x  {r['margin_usdt']} USDT seat  final {r['final']:>10}  maxDD {r['max_dd']:>7}  "
              f"liquidations {r['liquidations']}  trades {r['trades']}")
