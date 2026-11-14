"""The shared engine of the three asset bots (BTC, XAU, XAG). One run = one 15-minute cycle on CLOSED bars:

 1. read the market (perp candles 15m/1h/4h/1d, spot quote for metals, funding) -> market.read()
 2. read the scouts (big-move risk, no direction)                               -> scout.ScoutReader
 3. update open calls bar by bar (fill, stop-first, target, time exit)          -> calls book
 4. run the approved rules for this asset (one horizon each)                    -> new calls (TRIGGERED)
 5. step the state machine per horizon (day / swing / hold)                     -> machine.step()
 6. log the reading and any call BEFORE outcomes; score older readings/calls     -> forward record
 7. write <home>/assets/<ASSET>.json (the desk the app shows), history files and NOTEBOOK.md

States: WAIT -> WATCH -> SETUP -> TRIGGERED -> CONFIRMED -> INVALIDATED / EXPIRED.
WATCH = big-move risk without a direction. SETUP/TRIGGERED/CONFIRMED only from rules in edges/approved.json for this
asset and horizon with status paper/testnet/live. The bot never invents a direction and never places an order.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from edges.assetbots import machine, market, notebook, rules
from edges.assetbots.scout import ScoutReader

TFS = {"15m": 500, "1h": 500, "4h": 300, "1d": 400}
TF_DELTA = {"5m": pd.Timedelta(minutes=5), "15m": pd.Timedelta(minutes=15), "1h": pd.Timedelta(hours=1),
            "4h": pd.Timedelta(hours=4), "1d": pd.Timedelta(days=1)}
# how a WATCH reading is scored later: horizon in hours on 1h bars, big move = |log return| > max(floor, k x ATR1h%)
SCORE = {"day": (4, 0.004, 2.0), "swing": (24, 0.01, 4.0), "hold": (168, 0.03, 10.0)}
HISTORY_KEEP = 30           # closed calls kept in the desk JSON


class LiveProvider:
    """Closed candles, spot quote and funding from the Live API providers (Binance -> OKX -> Gate; Swissquote)."""

    def __init__(self):
        import sys
        root = Path(__file__).resolve().parents[2] / "omega" / "live_api"
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from omega_live.providers import FX, Crypto, Http
        h = Http()
        self.cx, self.fx = Crypto(h), FX(h)

    def klines(self, sym, tf, limit):
        k = self.cx.klines(sym, tf, limit)
        rows = [c for c in k["candles"] if c["closed"]]
        df = pd.DataFrame(rows)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
        df.attrs["source"] = k.get("source")
        return df[["o", "h", "l", "c", "v", "qv"]].astype(float)

    def quote(self, sym):
        return self.fx.quote(sym)

    def funding(self, sym):
        return self.cx.funding(sym)


def _iso(t) -> str:
    return pd.Timestamp(t).isoformat()


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    return o


class AssetBot:
    spec = None                       # set by the asset classes in assets.py

    def __init__(self, home, provider=None, approved: list | None = None, scouts: ScoutReader | None = None):
        self.root = Path(home) / "assets"
        self.dir = self.root / self.spec.code
        self.dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider
        self.approved = approved
        self.scouts = scouts or ScoutReader(self.spec.code, self.root)

    # ---------------------------------------------------------------- state files
    def _state(self) -> dict:
        f = self.dir / "state.json"
        if f.exists():
            try:
                return json.loads(f.read_text())
            except json.JSONDecodeError:
                pass
        return dict(horizons={}, open_calls=[], closed_calls=[], pending=[], forward={}, calls_record={},
                    runs=0, created=dt.datetime.now(dt.timezone.utc).isoformat()[:19])

    def _append(self, name: str, row: dict, month: str):
        with open(self.dir / f"{name}-{month}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(_jsonable(row), separators=(",", ":")) + "\n")

    # ---------------------------------------------------------------- data
    def fetch(self) -> tuple[dict, dict | None, dict | None, list]:
        p = self.provider or LiveProvider()
        bars, errors = {}, []
        for tf, n in TFS.items():
            try:
                bars[tf] = p.klines(self.spec.perp, tf, n)
            except Exception as e:
                errors.append(f"{tf} candles: {type(e).__name__}")
        quote = funding = None
        if self.spec.spot:
            try:
                quote = p.quote(self.spec.spot)
            except Exception as e:
                errors.append(f"spot quote: {type(e).__name__}")
        try:
            funding = p.funding(self.spec.perp)
        except Exception as e:
            errors.append(f"funding: {type(e).__name__}")
        return bars, quote, funding, errors

    def _rule_bars(self, strat, bars):
        tf = getattr(strat, "tf", "1h")
        df = bars.get(tf)
        if df is None and self.provider is not None:
            try:
                df = self.provider.klines(self.spec.perp, tf, max(TFS.get(tf, 500), getattr(strat, "lookback", 0) + 5))
                bars[tf] = df
            except Exception:
                df = None
        if df is None:
            return None, tf
        uni = getattr(strat, "universe", "all")
        syms = [self.spec.perp] if uni == "all" else list(uni)
        return {s: df for s in syms}, tf

    # ---------------------------------------------------------------- calls book
    def _new_call(self, rule, sig, bar_time, tf, horizon) -> dict:
        ref = float(sig.ref_close) if sig.ref_close else None
        entry = float(sig.price) if sig.entry == "limit" and sig.price else ref
        side = 1 if sig.side == "long" else -1
        stop = entry * (1 - side * sig.stop_pct) if entry and sig.stop_pct else None
        target = entry * (1 + side * sig.target_pct) if entry and sig.target_pct else None
        exit_time = pd.Timestamp(bar_time) + TF_DELTA[tf] * (int(sig.hold_bars) + (1 if sig.entry == "market" else 0))
        margin, lev = float(rule.get("margin_usdt") or 0), float(rule.get("max_leverage") or 1)
        return dict(id=f"{rule['id']}-{pd.Timestamp(bar_time):%Y%m%d%H%M}", rule=rule["id"], horizon=horizon,
                    asset=self.spec.code, symbol=self.spec.perp, side=sig.side, entry_type=sig.entry, entry=entry,
                    stop=stop, target=target, valid_for_bars=int(sig.valid_for_bars), hold_bars=int(sig.hold_bars),
                    tf=tf, signal_bar=_iso(bar_time), exit_by=_iso(exit_time),
                    size=dict(margin_usdt=margin, leverage=lev, notional_usdt=margin * lev),
                    grade=rule.get("grade"), status_rule=rule.get("status"), evidence=rule.get("evidence"),
                    findings=f"edges/assets/{self.spec.code}/FINDINGS.md", note=sig.note,
                    research_only=rule["research_only"], execution_allowed=rule["execution_allowed"],
                    state="TRIGGERED", fill_time=None, fill_price=None, logged_at=_iso(pd.Timestamp.now(tz="UTC")))

    def update_call(self, c: dict, df: pd.DataFrame) -> dict:
        """Walk closed bars after the signal bar: fill, then stop-first, target, time exit. Same rules as edges/bots."""
        if df is None or c["state"] not in ("TRIGGERED", "CONFIRMED"):
            return c
        side = 1 if c["side"] == "long" else -1
        sig_t, step = pd.Timestamp(c["signal_bar"]), TF_DELTA[c["tf"]]
        after = df[df.index > sig_t]
        if c["state"] == "TRIGGERED":
            for i, (t, b) in enumerate(after.iterrows()):
                if c["entry_type"] == "market":
                    fill = float(b.o)
                elif (side == 1 and b.l < c["entry"]) or (side == -1 and b.h > c["entry"]):
                    fill = float(c["entry"])
                elif i + 1 >= c["valid_for_bars"]:
                    c.update(state="EXPIRED", outcome="not filled in time", closed_at=_iso(t + step))
                    return c
                else:
                    continue
                c.update(state="CONFIRMED", fill_time=_iso(t), fill_price=fill)
                if c["entry_type"] == "market" and c.get("entry"):
                    # re-base stop/target on the actual fill, as the trading bot does
                    for k in ("stop", "target"):
                        if c[k]:
                            c[k] = fill * c[k] / c["entry"]
                    c["entry"] = fill
                break
            else:
                return c
        fill_t = pd.Timestamp(c["fill_time"])
        start_t = fill_t if c["entry_type"] == "limit" else sig_t
        last_t = start_t + step * c["hold_bars"]
        for t, b in df[df.index >= fill_t].iterrows():
            px = None
            if c["stop"] and ((side == 1 and b.l <= c["stop"]) or (side == -1 and b.h >= c["stop"])):
                px, why, st = c["stop"], "stop hit", "INVALIDATED"
            elif c["target"] and ((side == 1 and b.h >= c["target"]) or (side == -1 and b.l <= c["target"])):
                px, why, st = c["target"], "target hit", "EXPIRED"
            elif t >= last_t:
                px, why, st = float(b.c), "time exit", "EXPIRED"
            if px is not None:
                net = side * (px / c["fill_price"] - 1) - 2 * self.spec.cost_side
                c.update(state=st, outcome=why, exit_price=float(px), closed_at=_iso(t + step),
                         net_pct=round(net * 100, 3))
                return c
        return c

    # ---------------------------------------------------------------- forward record
    def _score_pending(self, st: dict, h1: pd.DataFrame | None):
        if h1 is None or not len(h1):
            return
        keep = []
        for p in st["pending"]:
            hrs = SCORE[p["horizon"]][0]
            t0 = pd.Timestamp(p["t"])
            t1 = t0 + pd.Timedelta(hours=hrs)
            if t1 not in h1.index:
                if t1 > h1.index[-1]:
                    keep.append(p)
                continue             # the bar is missing: drop rather than guess
            ret = float(np.log(h1.c.loc[t1] / p["price"]))
            big = abs(ret) > p["thr"]
            f = st["forward"].setdefault(p["horizon"], dict(n=0, big=0, watch_n=0, watch_big=0, brier=0.0,
                                                            brier_base=0.0, scout_n=0))
            f["n"] += 1
            f["big"] += int(big)
            if p["watch"]:
                f["watch_n"] += 1
                f["watch_big"] += int(big)
            if p.get("p") is not None:
                f["scout_n"] += 1
                f["brier"] += (p["p"] - big) ** 2
            self._append("scores", dict(t=p["t"], horizon=p["horizon"], watch=p["watch"], p=p.get("p"), ret=ret,
                                        thr=p["thr"], big=big), p["t"][:7])
        st["pending"] = keep

    def forward_summary(self, st: dict) -> dict:
        out = {}
        for hz in rules.HORIZONS:
            f = st["forward"].get(hz)
            if not f or not f["n"]:
                out[hz] = dict(scored=0, text="no readings scored yet (each is scored once its horizon has passed)")
                continue
            base = f["big"] / f["n"]
            wr = f["watch_big"] / f["watch_n"] if f["watch_n"] else None
            nw = f["n"] - f["watch_n"]
            nwr = (f["big"] - f["watch_big"]) / nw if nw else None
            out[hz] = dict(scored=f["n"], big_move_rate=round(base, 3), watch_readings=f["watch_n"],
                           big_move_rate_when_watch=round(wr, 3) if wr is not None else None,
                           big_move_rate_otherwise=round(nwr, 3) if nwr is not None else None,
                           scout_brier=round(f["brier"] / f["scout_n"], 4) if f["scout_n"] else None,
                           enough=f["n"] >= 200 and f["watch_n"] >= 30)
            msg = f"{f['n']} readings scored; big moves followed {base:.0%} of them"
            if wr is not None:
                msg += f", {wr:.0%} after a WATCH ({f['watch_n']} WATCH readings)"
            if not out[hz]["enough"]:
                msg += " - too few to judge yet"
            out[hz]["text"] = msg
        rec = st["calls_record"]
        out["calls"] = dict(rec) if rec else dict(closed=0, text="no calls yet: no tested rule for this asset has fired")
        return out

    def _record_call(self, st, c):
        r = st["calls_record"]
        r["closed"] = r.get("closed", 0) + 1
        if c.get("net_pct") is not None:
            r["filled"] = r.get("filled", 0) + 1
            r["wins"] = r.get("wins", 0) + int(c["net_pct"] > 0)
            r["sum_net_pct"] = round(r.get("sum_net_pct", 0.0) + c["net_pct"], 3)
            r["mean_net_pct"] = round(r["sum_net_pct"] / r["filled"], 3)
        r["text"] = (f"{r.get('filled', 0)} calls filled and closed, {r.get('wins', 0)} won, "
                     f"average {r.get('mean_net_pct', 0):+.2f}% after costs")

    # ---------------------------------------------------------------- watch
    def watch_reasons(self, horizon: str, read: dict) -> list[str]:
        v, rs = read.get("volatility", {}), []
        sc = (read.get("scouts") or {}).get(horizon if horizon != "hold" else "swing") or {}
        if horizon in ("day", "swing") and sc.get("flag"):
            rs.append(f"scout: {sc['p_big_move']:.0%} chance of a big move in {sc['horizon']} (top of its range; "
                      "direction unknown)")
        if horizon == "day":
            p = v.get("atr1h_pctile")
            if p is not None and p >= 90:
                rs.append(f"hourly volatility is high ({p:.0f}th percentile of the last 3 weeks)")
            if p is not None and p <= 5:
                rs.append(f"hourly volatility is unusually compressed ({p:.0f}th percentile): squeezes often end in a "
                          "burst (untested here)")
        if horizon == "swing":
            p = v.get("rv20d_pctile")
            if p is not None and p >= 85:
                rs.append(f"daily volatility is high ({p:.0f}th percentile)")
            r30 = (read.get("ranges") or {}).get("30d") or {}
            for side, k in (("high", "to_high_atr"), ("low", "to_low_atr")):
                if r30.get(k) is not None and r30[k] <= 1.0:
                    rs.append(f"price is within 1 hourly ATR of its 30-day {side}: a break or a rejection is near")
        if horizon == "hold":
            p = v.get("rv20d_pctile")
            if p is not None and p >= 90:
                rs.append(f"daily volatility is in its top 10% ({p:.0f}th percentile): holding risk is elevated")
        return rs

    # ---------------------------------------------------------------- one cycle
    def run_once(self, bars=None, quote=None, funding=None, now=None) -> dict:
        errors = []
        if bars is None:
            bars, quote, funding, errors = self.fetch()
        bars = {k: v for k, v in bars.items() if v is not None and len(v)}
        now = pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz="UTC")
        st = self._state()
        scouts = self.scouts.read(bars, self.spec)
        read = market.read(bars, now, self.spec, quote, funding, scouts)
        approved = rules.load_approved() if self.approved is None else self.approved

        # 3. open calls
        closed_now = []
        still = []
        for c in st["open_calls"]:
            c = self.update_call(c, bars.get(c["tf"]))
            if c["state"] in ("TRIGGERED", "CONFIRMED"):
                still.append(c)
            else:
                closed_now.append(c)
                self._record_call(st, c)
                self._append("calls", dict(event="closed", **c), now.strftime("%Y-%m"))
        st["open_calls"] = still
        st["closed_calls"] = (closed_now + st["closed_calls"])[:HISTORY_KEEP]

        # 4 + 5. rules and states per horizon
        horizons_out = {}
        for hz in rules.HORIZONS:
            rl = rules.rules_for(self.spec.code, hz, approved)
            new_calls, setups, notes = [], [], []
            for r in rl:
                strat = rules.load_strategy(r["id"])
                if strat is None:
                    notes.append(f"{r['id']}: strategy file missing or broken - cannot give a direction")
                    continue
                data, tf = self._rule_bars(strat, bars)
                if data is None:
                    notes.append(f"{r['id']}: no {tf} candles this cycle")
                    continue
                last_t = next(iter(data.values())).index[-1]
                try:
                    sigs = strat.signals({s: d.iloc[-(getattr(strat, 'lookback', 500) + 1):] for s, d in data.items()},
                                         last_t)
                    if hasattr(strat, "setup"):
                        s_up = strat.setup(data, last_t)
                        if s_up:
                            setups.append(dict(rule=r["id"], grade=r.get("grade"), detail=s_up))
                except Exception as e:
                    notes.append(f"{r['id']}: rule error {type(e).__name__}")
                    continue
                for sg in sigs or []:
                    if sg.sym not in data:
                        continue
                    if sg.ref_close is None:
                        sg.ref_close = float(data[sg.sym].c.iloc[-1])
                    c = self._new_call(r, sg, last_t, tf, hz)
                    if any(o["id"] == c["id"] for o in st["open_calls"] + st["closed_calls"]):
                        continue
                    new_calls.append(c)
            for c in new_calls:
                self._append("calls", dict(event="called", **c), now.strftime("%Y-%m"))   # logged before outcome
                st["open_calls"].append(c)
            ctx = dict(now=_iso(now), watch=self.watch_reasons(hz, read), setups=setups,
                       open_calls=[c for c in st["open_calls"] if c["horizon"] == hz],
                       closed_now=[c for c in closed_now if c["horizon"] == hz], n_rules=len(rl), notes=notes)
            prev = st["horizons"].get(hz)
            h = machine.step(prev, ctx)
            st["horizons"][hz] = h
            horizons_out[hz] = dict(h, rules=[dict(id=r["id"], grade=r.get("grade"), status=r.get("status"),
                                                   execution_allowed=r["execution_allowed"],
                                                   research_only=r["research_only"], evidence=r.get("evidence"))
                                              for r in rl])

        # 6. forward record: score old readings, log this one before its outcome
        h1 = bars.get("1h")
        self._score_pending(st, h1)
        bar = read.get("bar")
        if h1 is not None and len(h1) > 20 and bar:
            a = float((market.atr(h1) / h1.c).iloc[-1])
            for hz, (hrs, floor, k) in SCORE.items():
                if hz in ("day", "swing") or now.minute < 15:     # hold: once an hour is plenty
                    sc = (read.get("scouts") or {}).get(hz) or {}
                    st["pending"].append(dict(t=_iso(h1.index[-1]), price=float(h1.c.iloc[-1]), horizon=hz,
                                              thr=max(floor, k * a), watch=horizons_out[hz]["state"] != "WAIT",
                                              p=sc.get("p_big_move")))
            # keep one pending row per (time, horizon)
            seen, uniq = set(), []
            for p in st["pending"]:
                key = (p["t"], p["horizon"])
                if key not in seen:
                    seen.add(key)
                    uniq.append(p)
            st["pending"] = uniq
        row = dict(t=_iso(now), bar=bar, price=read.get("price"),
                   atr1h_pct=read.get("volatility", {}).get("atr1h_pct"),
                   regime=read.get("volatility", {}).get("regime"),
                   trend={k: (v or {}).get("state") for k, v in read["trend"].items()},
                   states={k: v["state"] for k, v in horizons_out.items()},
                   scouts={k: v.get("p_big_move") for k, v in (read.get("scouts") or {}).items() if isinstance(v, dict)})
        self._append("readings", row, now.strftime("%Y-%m"))
        st["runs"] = st.get("runs", 0) + 1
        st["last_run"] = _iso(now)

        # 7. outputs
        fwd = self.forward_summary(st)
        nb = notebook.build(self.spec, read, fwd, bars, approved)
        (self.dir / "NOTEBOOK.md").write_text(nb["markdown"], encoding="utf-8")
        desk = dict(asset=self.spec.code, name=self.spec.name, perp=self.spec.perp, spot_symbol=self.spec.spot,
                    asof=_iso(now), data_source=(bars.get("15m").attrs.get("source") if bars.get("15m") is not None
                                                 else None),
                    errors=errors, read=read, horizons=horizons_out,
                    open_calls=st["open_calls"], recent_calls=st["closed_calls"][:10], forward=fwd,
                    notebook=nb["sections"], runs=st["runs"],
                    honesty=("Calls come only from rules that passed a pre-registered test (edges/approved.json, "
                             "status paper or higher). With no such rule the bot only WAITs or WATCHes. "
                             "Paper records, never an order; execution_allowed is true only for testnet/live rules."))
        (self.dir / "state.json").write_text(json.dumps(_jsonable(st), indent=0), encoding="utf-8")
        (self.root / f"{self.spec.code}.json").write_text(json.dumps(_jsonable(desk), indent=1), encoding="utf-8")
        return desk
