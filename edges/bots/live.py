"""The runner: paper | testnet | live. At every bar close it fetches the closed candles, settles resting orders and
open positions, runs every approved rule's signals() (the exact code the backtest runs), and places what the guard allows.

  paper    (default) no exchange orders; fills judged on the candles exactly like the backtest (limit only when a later
           candle trades through it; stops on intrabar lows; exits at the exit bar's close).
  testnet  orders on Binance's futures testnet (needs testnet keys; rule status testnet|live).
  live     real money: rule status "live" AND config live:true AND OMEGA_LIVE=I_UNDERSTAND_REAL_MONEY AND a key that
           cannot withdraw. Nothing else turns it on.
State: <home>/state.json (atomic). Log: <home>/bots_log.jsonl (every signal, refusal, order, fill, exit).
Kill switch: a file named KILL in <home> (or `python -m edges.bots kill`): cancels every order, closes every position,
blocks new orders until `kill off`.
"""
from __future__ import annotations

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from edges.bots import config as C
from edges.bots import guard as G
from edges.bots import keys, sizing
from edges.bots import strategies as S
from edges.bots.core import Order, Position, bar_time, dense, resample, tf_delta
from edges.bots.exchange_binance import BinanceError, BinanceFutures, MarketData, TransportError, round_for

FEES = {"limit": 0.0002, "market": 0.0005}     # paper fee per side (maker for a filled limit), exits are taker
DEFAULT_INFO = dict(step=1e-6, mstep=1e-6, minQty=0.0, minNotional=5.0, tick=1e-8, status="TRADING")


def iso(t):
    return pd.Timestamp(t).isoformat()


def ts(s):
    return pd.Timestamp(s)


# ---------------------------------------------------------------- brokers
class PaperBroker:
    venue = "paper"

    def __init__(self, info_fn=None):
        self.bars = {}                 # {tf: {sym: dense frame}} (the runner's frames)
        self._info_fn = info_fn

    def frame(self, sym, tf="1h"):
        return (self.bars.get(tf) or {}).get(sym)

    def info(self, sym):
        if self._info_fn:
            try:
                return self._info_fn(sym)
            except Exception:
                pass
        return dict(DEFAULT_INFO)

    def price(self, sym, tf=None):
        for t in ([tf] if tf else []) + ["5m", "15m", "1h"]:
            d = self.frame(sym, t)
            if d is not None and len(d.c.dropna()):
                return float(d.c.dropna().iloc[-1])
        return None

    def entry(self, o):
        if o["kind"] == "market":
            return dict(filled=True, price=o["ref_price"], qty=o["qty"], fill_bar=o["signal_bar"], ids={"paper": True})
        return dict(filled=False, ids={"paper": True})

    def entry_status(self, o, now):
        step = tf_delta(o.get("tf", "1h"))
        d = self.frame(o["sym"], o.get("tf", "1h"))
        sb = ts(o["signal_bar"])
        if d is not None:
            seg = d[(d.index > sb) & (d.index <= sb + o["valid_for_bars"] * step) & (d.index + step <= now)]
            hit = seg[seg.l < o["price"]] if o["side"] == "long" else seg[seg.h > o["price"]]
            if len(hit):
                return dict(state="filled", price=o["price"], qty=o["qty"], fill_bar=iso(hit.index[0]))
        return dict(state="expired" if now >= ts(o["expires_at"]) else "open")

    def cancel_entry(self, o):
        return {"paper": "cancelled"}

    def check_position(self, p, now):
        """(alive, exit_price, reason) — the stop judged on intrabar extremes, as in the backtest."""
        step = tf_delta(p.get("tf", "1h"))
        d = self.frame(p["sym"], p.get("tf", "1h"))
        if d is None or p.get("stop_price") is None:
            return True, None, ""
        first = ts(p["entry_bar"]) if p["entry_kind"] == "limit" else ts(p["entry_bar"]) + step
        seg = d[(d.index >= first) & (d.index + step <= now)]
        sp = p["stop_price"]
        for t, r in seg.iterrows():
            if (p["side"] == "long" and r.l <= sp) or (p["side"] == "short" and r.h >= sp):
                gap = t > first and ((p["side"] == "long" and r.o < sp) or (p["side"] == "short" and r.o > sp))
                return False, float(r.o if gap else sp), "stop"
        return True, None, ""

    def exit(self, p, now):
        tf = p.get("tf", "1h")
        d = self.frame(p["sym"], tf)
        xb = ts(p["exit_due"]) - tf_delta(tf)
        if d is not None:
            c = d.c[(d.index <= xb)].dropna()
            if len(c):
                return float(c.iloc[-1])
        return self.price(p["sym"], tf)

    def kill_all(self, state):
        return [dict(sym=s, ok=True) for s in state.open_symbols()]

    def exposure(self):
        return 0, set()

    def day_pnl(self, state):
        return state.day_pnl(pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d"))


class ExchangeBroker:
    """Binance testnet/live through BinanceFutures."""

    def __init__(self, api: BinanceFutures, venue="testnet"):
        self.api, self.venue = api, venue
        self.bars = {}

    def info(self, sym):
        return self.api.info(sym)

    def price(self, sym):
        return self.api.price(sym)

    def _send_entry(self, o, cid):
        """Place the entry. On a network error, ask the exchange whether it arrived (by client order id)."""
        a = self.api
        try:
            if o["kind"] == "limit":
                return a.place_limit(o["sym"], o["side"], o["qty"], o["price"], client_id=cid,
                                     expires_ms=int(ts(o["expires_at"]).timestamp() * 1000),
                                     now_ms=int(ts(o["placed_at"]).timestamp() * 1000))
            return a.place_market(o["sym"], o["side"], o["qty"], client_id=cid)
        except TransportError:
            found = a.find_order(o["sym"], cid)
            if not found:
                raise
            return found

    def entry(self, o):
        """Entry + protective stop. A failed stop undoes the entry; if the undo fails too, the kill switch goes on and
        the result says `unprotected` so the runner keeps the position in state (marked UNPROTECTED) and retries."""
        a = self.api
        a.prepare(o["sym"], o["leverage"])
        cid = "omg-" + o["id"][:20]
        r = self._send_entry(o, cid)
        ids = dict(entry=r.get("orderId"), client=cid)
        filled = o["kind"] == "market" or r.get("status") == "FILLED"
        px = float(r.get("avgPrice") or 0) or (o.get("price") if o["kind"] == "limit" else None) or a.price(o["sym"])
        qty = float(r.get("executedQty") or 0) or o["qty"]
        if o.get("stop_price"):
            try:
                st = a.place_stop(o["sym"], o["side"], o["stop_price"], client_id=cid + "-s")
                ids.update(stop=st.get("algoId") or st.get("orderId"), stop_algo=st.get("algo"))
            except Exception as e:
                undo = {}
                try:
                    if o["kind"] == "limit":
                        undo["cancel"] = a.cancel(o["sym"], ids["entry"])
                    q, _ = a.close(o["sym"])        # anything that filled meanwhile is closed
                    undo["closed_qty"] = q
                    if a.positions().get(o["sym"]):
                        raise BinanceError("position still open after the undo")
                except Exception as e2:
                    G.set_kill(True, f"UNPROTECTED {o['sym']}: stop failed ({e}) and the undo failed ({e2})")
                    return dict(filled=filled, unprotected=True, price=px, qty=qty, fill_bar=o["signal_bar"], ids=ids,
                                error=f"stop failed: {e}; undo failed: {e2}")
                return dict(filled=False, rolled_back=True, ids=ids, error=f"stop failed, entry undone: {e}", undo=undo)
        if filled:
            return dict(filled=True, price=px, qty=qty, fill_bar=o["signal_bar"], ids=ids)
        return dict(filled=False, ids=ids)

    def exposure(self):
        """Exchange truth for the limits: open positions and resting entry orders on the whole account."""
        pos = set(self.api.positions())
        pend = set(self.api.pending_entries())
        return len(pos | pend), pos | pend

    def entry_status(self, o, now):
        r = self.api.order(o["sym"], o["exchange_ids"]["entry"])
        st, q = r.get("status"), float(r.get("executedQty") or 0)
        fill_bar = iso(pd.Timestamp(int(r.get("updateTime") or time.time() * 1000), unit="ms", tz="UTC").floor(tf_delta(o.get("tf", "1h"))))
        if st == "FILLED":
            return dict(state="filled", price=float(r.get("avgPrice") or o["price"]), qty=q, fill_bar=fill_bar)
        expired = now >= ts(o["expires_at"])
        if st in ("CANCELED", "EXPIRED", "REJECTED") or (expired and st in ("NEW", "PARTIALLY_FILLED")):
            if st in ("NEW", "PARTIALLY_FILLED"):
                self.api.cancel(o["sym"], o["exchange_ids"]["entry"])
            if q > 0:                                     # part-filled: keep what filled, with its stop
                return dict(state="filled", price=float(r.get("avgPrice") or o["price"]), qty=q, fill_bar=fill_bar)
            return dict(state="expired")
        return dict(state="open")

    def cancel_entry(self, o):
        out = self.api.cancel(o["sym"], o["exchange_ids"].get("entry"))
        self.api.cancel_all(o["sym"])                     # its resting stop too
        return out

    def check_position(self, p, now):
        pos = self.api.positions().get(p["sym"])
        if pos and abs(pos["qty"]) > 0:
            return True, None, ""
        self.api.cancel_all(p["sym"])
        return False, self.api.last_fill_price(p["sym"]), "stop_or_external"

    def exit(self, p, now):
        q, px = self.api.close(p["sym"])
        return px or self.api.last_fill_price(p["sym"])

    def kill_all(self, state):
        """Close every position and cancel every order on the account (all symbols). Per-symbol errors never stop the
        loop. Returns [{sym, ok, ...}]; `ok` only when the exchange shows no position left."""
        out, syms = [], set(state.open_symbols())
        for fetch in (lambda: set(self.api.positions()), lambda: {x["symbol"] for x in self.api.open_orders()},
                      lambda: {x.get("symbol") for x in self.api.open_algo_orders() if x.get("symbol")}):
            try:
                syms |= fetch()
            except Exception as e:
                out.append(dict(error=f"listing failed: {type(e).__name__}: {e}"))
        for s in sorted(syms):
            try:
                q, px = self.api.close(s)
                left = self.api.positions().get(s)
                out.append(dict(sym=s, ok=not left, closed_qty=q, price=px))
            except Exception as e:
                out.append(dict(sym=s, ok=False, error=f"{type(e).__name__}: {e}"))
        return out

    def day_pnl(self, state):
        return self.api.day_pnl()


# ---------------------------------------------------------------- runner
class Runner:
    def __init__(self, cfg=None, mode=None, broker=None, market=None, state=None, now_fn=None):
        self.cfg = cfg or C.load()
        self.mode = mode or self.cfg.get("mode", "paper")
        self.market = market or MarketData(self.cfg["binance"]["data_url"], spacing=self.cfg["binance"]["request_spacing_s"],
                                           alt_gap_s=self.cfg["binance"].get("fallback_gap_s"))
        self.now_fn = now_fn or (lambda: pd.Timestamp.now(tz="UTC"))
        from edges.bots.state import State
        self.state = state or State()
        self.cache = {}                # {fetch tf: {sym: dense frame}}
        self.frames = {}               # cache + derived tfs (15m from 5m)
        self.meta = {}
        self._uni, self._uni_t, self._global = None, 0.0, set()
        self._short = {}
        self.broker = broker or self._make_broker()
        self.rules, self.strats = self._rules()

    # -- setup
    def _make_broker(self):
        if self.mode == "paper":
            return PaperBroker(info_fn=self._public_info)
        k, s = keys.binance(self.mode)
        # first every check that needs no network (the withdrawal check comes after, with the key itself)
        why = G.mode_refusals(self.cfg, self.mode, have_keys=bool(k and s), withdrawals_enabled=False)
        if why:
            raise SystemExit(f"refused to start {self.mode}: " + "; ".join(why))
        url = self.cfg["binance"]["live_url"] if self.mode == "live" else self.cfg["binance"]["testnet_url"]
        api = BinanceFutures(url, k, s, cfg=self.cfg["binance"])
        if self.mode == "live":
            rs = api.key_restrictions(self.cfg["binance"]["spot_url"])
            wd = None if rs is None else bool(rs.get("enableWithdrawals")) or bool(rs.get("enableInternalTransfer"))
            why = G.mode_refusals(self.cfg, "live", have_keys=True, withdrawals_enabled=wd,
                                  ip_restricted=bool(rs and rs.get("ipRestrict")))
            if keys.from_env("live"):
                C.log("warning", note="the live key comes from environment variables; the OS vault is safer (setkey live)")
            if why:
                raise SystemExit("refused to start LIVE: " + "; ".join(why))
        if api.dual_side():
            raise SystemExit("refused to start: the account is in Hedge Mode; switch Binance futures to One-way Mode")
        return ExchangeBroker(api, self.mode)

    _pinfo = None

    def _public_info(self, sym):
        if self._pinfo is None:
            info = self.market.exchange_info()
            self._pinfo = {}
            for s in info["symbols"]:
                f = {x["filterType"]: x for x in s["filters"]}
                self._pinfo[s["symbol"]] = dict(step=float(f["LOT_SIZE"]["stepSize"]), minQty=float(f["LOT_SIZE"]["minQty"]),
                                                tick=float(f["PRICE_FILTER"]["tickSize"]),
                                                minNotional=float(f.get("MIN_NOTIONAL", {}).get("notional", 5)))
        return self._pinfo[sym]

    def _rules(self):
        appr = C.approved(self.cfg)
        want = self.cfg.get("strategies") or list(appr)
        rules, strats = {}, {}
        for rid in want:
            r = appr.get(rid)
            why = G.rule_refusals(self.cfg, self.mode, r)
            if r is not None and r.get("venue", "binance") != "binance":
                why.append(f"venue {r.get('venue')} is handled by exchange_mt5 (not by this runner yet)")
            if why:
                C.log("rule_skipped", rule=rid, mode=self.mode, reasons=why)
                continue
            try:
                strats[rid] = S.load(rid)
                rules[rid] = r
            except Exception as e:
                C.log("rule_error", rule=rid, error=f"{type(e).__name__}: {e}")
        return rules, strats

    # -- data
    def _fetch_tf(self, st):
        return getattr(st, "source_tf", None) or st.tf

    def universe(self):
        """The global universe ("all" / "top:N" / a list in config), cached for `universe_refresh_h` hours."""
        u = self.cfg.get("universe", "all")
        if isinstance(u, list):
            return {s: {} for s in u}
        t = time.time()
        if self._uni is None or t - self._uni_t > float(self.cfg.get("universe_refresh_h", 6)) * 3600:
            top = int(u.split(":")[1]) if isinstance(u, str) and u.startswith("top:") else None
            self._uni, self._uni_t = self.market.universe(top=top), t
        return self._uni

    def needs(self, now):
        """{fetch_tf: {sym: bars}}: every coin each rule needs at the candle size its data comes from, plus the coins of
        resting orders / open positions (at their rule's candles, so paper fills are judged on the right bars)."""
        need, uni = {}, None
        hist = int(self.cfg.get("history_bars", 1000))

        def add(tf, syms, n):
            d = need.setdefault(tf, {})
            for s in syms:
                d[s] = max(d.get(s, 0), int(n))

        for rid, st in self.strats.items():
            src = self._fetch_tf(st)
            k = max(1, int(tf_delta(st.tf) / tf_delta(src)))
            n = (int(st.lookback) + 2) * k + k + 10
            if src == "1h":
                n = max(n, hist)
            if isinstance(st.universe, list):
                add(src, st.universe, n)
            else:
                if uni is None:
                    uni = self.universe()
                    for s, m in uni.items():
                        if m.get("onboard"):
                            self.meta[s] = dict(first_ts=pd.Timestamp(int(m["onboard"]), unit="ms", tz="UTC").floor("h"))
                add(src, uni, n)
        self._global = set(uni) if uni is not None else set()
        for rec in list(self.state.orders.values()) + list(self.state.positions.values()):
            tf = rec.get("tf", "1h")
            src = rec.get("src_tf") or tf
            add(src, [rec["sym"]], max(need.get(src, {}).get(rec["sym"], 0), 300))
        return need

    def _disk(self, tf, sym):
        return os.path.join(C.home(), "bars", tf, f"{sym}.parquet")

    def _load_disk(self, tf, sym):
        if not self.cfg.get("bar_cache", True):
            return None
        f = self._disk(tf, sym)
        try:
            return pd.read_parquet(f) if os.path.exists(f) else None
        except Exception:
            return None

    def _save_disk(self, tf, sym, d):
        if not self.cfg.get("bar_cache", True):
            return
        f = self._disk(tf, sym)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        try:
            d.to_parquet(f + ".tmp")
            os.replace(f + ".tmp", f)
        except Exception as e:
            C.log("cache_error", sym=sym, tf=tf, error=f"{type(e).__name__}: {e}")

    def _fetch(self, sym, tf, n):
        hist = getattr(self.market, "history", None)
        return hist(sym, tf, n) if hist is not None else self.market.klines(sym, tf, n)

    def _refresh_one(self, tf, s, n, bar):
        """Bring one frame up to `bar` (the last closed bar at tf). Incremental when the cache (memory or disk) reaches
        back far enough; a full history fetch otherwise. Returns (frame, changed) or raises."""
        step = tf_delta(tf)
        d = self.cache.setdefault(tf, {}).get(s)
        if d is None:
            d = self._load_disk(tf, s)
        if d is not None and len(d) and d.index[-1] >= bar:
            return d, False
        span_ok = d is not None and len(d) and (d.index[0] <= bar - (n - 1) * step or self._short.get((tf, s)) == d.index[0])
        if span_ok and d.index[-1] >= bar - step * 900:
            k = int((bar - d.index[-1]) / step) + 3
            new = self._fetch(s, tf, k)
            d = pd.concat([d, new]).sort_index()
            d = d[~d.index.duplicated(keep="last")]
        else:
            d = self._fetch(s, tf, n)
            if 0 < len(d) < n:                                  # a young coin: its whole history is this
                self._short[(tf, s)] = d.index[0]
        d = d[d.index <= bar]
        if not len(d):
            return None, False
        return dense(d, tf).iloc[-(n + 50):], True

    def refresh(self, need, now):
        """Fetch what `need` asks for, only where a new bar has closed since the last fetch; in parallel threads
        (the providers pace their own requests). Then rebuild derived frames (15m from 5m) and hand them to the broker."""
        jobs = []
        for tf, syms in need.items():
            bar = bar_time(now, tf)
            for s, n in syms.items():
                jobs.append((tf, s, n, bar))

        def work(j):
            tf, s, n, bar = j
            try:
                return j, self._refresh_one(tf, s, n, bar), None
            except Exception as e:
                return j, (None, False), e

        workers = max(1, int(self.cfg.get("fetch_workers", 6)))
        if workers > 1 and len(jobs) > 1:
            with ThreadPoolExecutor(workers) as ex:
                res = list(ex.map(work, jobs))
        else:
            res = [work(j) for j in jobs]
        fetched = 0
        for (tf, s, n, bar), (d, changed), err in res:
            if err is not None:
                C.log("data_error", sym=s, tf=tf, error=f"{type(err).__name__}: {err}")
                continue
            if d is None:
                continue
            self.cache.setdefault(tf, {})[s] = d
            if changed:
                fetched += 1
                self._save_disk(tf, s, d)
        self._derive(now)
        self.broker.bars = self.frames
        return fetched

    def _derive(self, now):
        """frames = fetched frames + rules' bars built from finer candles (core.resample), dropping a bin whose
        sub-bars have not all closed yet."""
        fr = {tf: dict(d) for tf, d in self.cache.items()}
        want = {}
        for st in self.strats.values():
            src = self._fetch_tf(st)
            if src != st.tf:
                want.setdefault((st.tf, src), set()).update(st.universe if isinstance(st.universe, list) else self.cache.get(src, {}))
        for rec in list(self.state.orders.values()) + list(self.state.positions.values()):
            if rec.get("src_tf") and rec.get("src_tf") != rec.get("tf"):
                want.setdefault((rec["tf"], rec["src_tf"]), set()).add(rec["sym"])
        for (tf, src), syms in want.items():
            last = bar_time(now, tf)
            out = fr.setdefault(tf, {})
            for s in syms:
                d = self.cache.get(src, {}).get(s)
                if d is None or not len(d):
                    continue
                r = resample(d, tf, src)
                out[s] = r[r.index <= last]
        self.frames = fr

    # -- one cycle
    def _due(self, now):
        """{rule: [bar open times to evaluate]}. Paper mode catches up every bar closed since the rule's last
        evaluation (up to `catchup_hours`), so a 5m rule run every 15 minutes (GitHub Actions) still sees every bar;
        testnet/live evaluate only the bar that just closed (an old signal is not traded)."""
        last_all = self.state.d.setdefault("last_bars", {})
        out = {}
        for rid, st in self.strats.items():
            step = tf_delta(st.tf)
            b = bar_time(now, st.tf)
            last = last_all.get(rid)
            if last is None and st.tf == "1h":
                last = self.state.d.get("last_bar")          # state files written before per-rule bookkeeping
            last = ts(last) if last else None
            if last is not None and last >= b:
                continue
            if self.mode == "paper" and last is not None:
                lim = b - pd.Timedelta(hours=float(self.cfg.get("catchup_hours", 24)))
                first = max(last + step, lim)
                out[rid] = list(pd.date_range(first.ceil(step), b, freq=step))
            else:
                out[rid] = [b]
        return out

    def cycle(self, full=True):
        now = self.now_fn()
        if G.killed():
            if self.state.orders or self.state.positions:
                self.kill(reason="KILL file present")
            return dict(killed=True)
        placed = []
        due = self._due(now) if full else {}
        if full and (due or self.state.orders or self.state.positions):
            self.refresh(self.needs(now), now)
        events = sorted((t + tf_delta(self.strats[rid].tf), t, rid) for rid, lst in due.items() for t in lst)
        for close, t, rid in events:
            if self.mode == "paper":
                self.settle(min(close, now))
            placed += self.evaluate_rule(rid, t, min(close, now) if self.mode == "paper" else now)
            self.state.d["last_bars"][rid] = iso(t)
        self.settle(now)
        if full:
            self.state.d["last_bar"] = iso(bar_time(now, "1h"))
        self.state.d["mode"] = self.mode
        self.state.save()
        return dict(bar=iso(bar_time(now, "1h")), evaluated={r: len(v) for r, v in due.items()}, placed=placed,
                    open=len(self.state.positions), resting=len(self.state.orders))

    def settle(self, now):
        st = self.state
        for oid, o in list(st.orders.items()):
            try:
                r = self.broker.entry_status(o, now)
            except Exception as e:
                C.log("sync_error", order=oid, error=str(e))
                continue
            if r["state"] == "filled":
                self._open_position(o, r, now)
                del st.orders[oid]
            elif r["state"] == "expired":
                try:
                    self.broker.cancel_entry(o)
                except Exception as e:
                    C.log("cancel_error", order=oid, error=str(e))
                C.log("expired", order=oid, sym=o["sym"], strategy=o["strategy"], price=o["price"])
                del st.orders[oid]
        for pid, p in list(st.positions.items()):
            try:
                alive, px, why = self.broker.check_position(p, now)
                if not alive:
                    self._close(pid, px, why, now)
                    continue
                if now >= ts(p["exit_due"]):
                    px = self.broker.exit(p, now)
                    self._close(pid, px, "time", now)
            except Exception as e:
                C.log("exit_error", position=pid, sym=p["sym"], error=f"{type(e).__name__}: {e}")

    def _open_position(self, o, r, now=None):
        step = tf_delta(o.get("tf", "1h"))
        fill_bar = ts(r["fill_bar"])
        due = fill_bar + (o["hold_bars"] + 1) * step if o["kind"] == "limit" else ts(o["signal_bar"]) + (o["hold_bars"] + 1) * step
        p = Position(id=o["id"], strategy=o["strategy"], sym=o["sym"], side=o["side"], qty=r["qty"], entry=r["price"],
                     entry_time=iso(now if now is not None else self.now_fn()), exit_due=iso(due), stop_price=o.get("stop_price"),
                     leverage=o["leverage"], margin_usdt=o["margin_usdt"], entry_kind=o["kind"],
                     exchange_ids=o.get("exchange_ids", {}), note=o.get("note", ""))
        d = p.__dict__.copy()
        d["entry_bar"] = iso(fill_bar)
        d["tf"], d["src_tf"] = o.get("tf", "1h"), o.get("src_tf") or o.get("tf", "1h")
        self.state.positions[p.id] = d
        C.log("filled", mode=self.mode, strategy=p.strategy, sym=p.sym, qty=p.qty, price=p.entry, exit_due=p.exit_due,
              stop=p.stop_price)

    def _close(self, pid, px, reason, now):
        p = self.state.positions.pop(pid)
        sgn = 1 if p["side"] == "long" else -1
        pnl = None
        if px:
            fee = (FEES["limit"] if p["entry_kind"] == "limit" else FEES["market"]) + FEES["market"]
            pnl = round(sgn * (px / p["entry"] - 1) * p["qty"] * p["entry"] - fee * p["qty"] * p["entry"], 6)
        p.update(status="closed", exit=px, exit_time=iso(now), exit_reason=reason, pnl_usdt=pnl)
        self.state.d["closed"].append(p)
        C.log("closed", mode=self.mode, strategy=p["strategy"], sym=p["sym"], price=px, reason=reason, pnl_usdt=pnl)

    def evaluate_rule(self, rid, bar, now):
        """Run one rule at bar `bar` (open time of a closed bar at the rule's tf) and place what it signals."""
        st = self.strats[rid]
        st.meta = self.meta
        fr = self.frames.get(st.tf, {})
        if isinstance(st.universe, list):
            syms = [s for s in st.universe if s in fr]
        else:
            syms = [s for s in fr if s in self._global] if self._global else list(fr)
        bars = {}
        for s in syms:
            d = fr[s]
            if not len(d):
                continue
            if d.index[-1] != bar:
                d = d.loc[:bar]
                if not len(d) or d.index[-1] != bar:
                    continue
            bars[s] = d
        try:
            sigs = st.signals(bars, bar) or []
        except Exception as e:
            C.log("strategy_error", rule=rid, error=f"{type(e).__name__}: {e}")
            return []
        placed = []
        for sg in sigs:
            sg.strategy = sg.strategy or rid
            r = self.place(self.rules[rid], sg, bar, now, tf=st.tf, src_tf=self._fetch_tf(st))
            if r:
                placed.append(r)
        return placed

    def evaluate(self, bar, now):
        """Every rule at `bar` (kept for callers of the hourly-only runner)."""
        out = []
        for rid in self.strats:
            out += self.evaluate_rule(rid, bar, now)
        return out

    def _book(self, rule):
        """(open_count, open_symbols, day_pnl) the guard sees for this rule. A paper rule with "book": "own" in
        approved.json (the watch list) keeps its own book: it neither blocks nor is blocked by other rules, and account
        limits (max open, daily loss) do not cut its record short; nothing it does reaches an exchange."""
        st = self.state
        own = {r for r, x in self.rules.items() if self.mode == "paper" and x.get("book") == "own"}
        if rule["id"] in own:
            recs = [x for x in list(st.orders.values()) + list(st.positions.values()) if x["strategy"] == rule["id"]]
            return 0, {x["sym"] for x in recs}, 0.0, True
        recs = [x for x in list(st.orders.values()) + list(st.positions.values()) if x["strategy"] not in own]
        day = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")
        pnl = sum(c.get("pnl_usdt") or 0.0 for c in st.d["closed"]
                  if str(c.get("exit_time", ""))[:10] == day and c.get("strategy") not in own)
        return len(recs), {x["sym"] for x in recs}, pnl, False

    def place(self, rule, sg, bar, now, tf="1h", src_tf=None):
        """Size, guard and send one signal. Returns the order record or None (the refusal is logged)."""
        st, cfg = self.state, self.cfg
        key = f"{rule['id']}|{sg.sym}|{iso(bar)}"
        if st.seen(key):
            return None
        st.mark_seen(key)
        if st.busy(rule["id"], sg.sym):
            C.log("ignored_busy", rule=rule["id"], sym=sg.sym, note="the rule already holds this coin (as in the research)")
            return None
        L = int(min(rule.get("max_leverage", 1), cfg["guard"]["hard_max_leverage"]))
        margin = float(rule.get("margin_usdt", 5))
        stop_pct = G.protective_stop(cfg, sg.stop_pct, L, self.mode)
        try:
            info = self.broker.info(sg.sym)
            ref = sg.ref_close or self.broker.price(sg.sym)
            px = sg.price if sg.entry == "limit" else ref
            if self.mode == "testnet" and cfg["binance"].get("rebase_testnet_prices") and ref:
                vp = self.broker.price(sg.sym)
                ratio = vp / ref
                px = px * ratio
                ref = vp
            px_r, _ = round_for(info, sg.side, entry=px) if sg.entry == "limit" else (px, None)
            stop_px = None
            if stop_pct is not None:
                _, stop_px = round_for(info, sg.side, stop=(px_r or ref) * (1 - stop_pct if sg.side == "long" else 1 + stop_pct))
                stop_pct = abs(1 - stop_px / (px_r or ref))
            qty = sizing.quantity(margin, L, px_r or ref, info)
        except (sizing.SizingError, BinanceError, KeyError, TypeError) as e:
            C.log("refused", mode=self.mode, rule=rule["id"], sym=sg.sym, reasons=[f"sizing: {e}"])
            return None
        b_n, b_syms, b_pnl, own = self._book(rule)
        if own:
            day, ex_n, ex_syms = b_pnl, 0, set()
        else:
            try:
                day = self.broker.day_pnl(st) if self.mode != "paper" else b_pnl
            except Exception as e:
                C.log("refused", mode=self.mode, rule=rule["id"], sym=sg.sym, reasons=[f"cannot read today's P&L: {e}"])
                return None
            try:
                ex_n, ex_syms = self.broker.exposure()
            except Exception as e:
                C.log("refused", mode=self.mode, rule=rule["id"], sym=sg.sym, reasons=[f"cannot read exchange positions/orders: {e}"])
                return None
        syms = b_syms | set(ex_syms)
        why = G.order_refusals(cfg, self.mode, rule,
                               dict(sym=sg.sym, leverage=L, margin_usdt=margin, notional=qty * (px_r or ref), stop_pct=stop_pct),
                               dict(open_count=0 if own else max(b_n, ex_n, len(syms)), open_symbols=syms, day_pnl_usdt=day))
        if why:
            C.log("refused", mode=self.mode, rule=rule["id"], sym=sg.sym, reasons=why)
            return None
        step = tf_delta(tf)
        o = Order(id=uuid.uuid4().hex[:16], strategy=rule["id"], sym=sg.sym, side=sg.side, kind=sg.entry, qty=qty,
                  price=px_r if sg.entry == "limit" else None, placed_at=iso(now),
                  expires_at=iso(bar + (sg.valid_for_bars + 1) * step), hold_bars=sg.hold_bars, stop_price=stop_px,
                  leverage=L, margin_usdt=margin, signal_bar=iso(bar), note=sg.note)
        rec = o.__dict__.copy()
        rec.update(valid_for_bars=sg.valid_for_bars, ref_price=ref, tf=tf, src_tf=src_tf or tf)
        try:
            r = self.broker.entry(rec)
        except Exception as e:
            C.log("order_error", mode=self.mode, rule=rule["id"], sym=sg.sym, error=f"{type(e).__name__}: {e}")
            return None
        rec["exchange_ids"] = r.get("ids", {})
        if r.get("rolled_back"):
            C.log("order_error", mode=self.mode, rule=rule["id"], sym=sg.sym, error=r.get("error"), undo=r.get("undo"))
            return None
        if r.get("unprotected"):
            C.log("UNPROTECTED", mode=self.mode, rule=rule["id"], sym=sg.sym, error=r.get("error"),
                  note="kill switch set; the position is kept in state and closed by the kill cycle")
            self._open_position(rec, dict(r, state="filled"))
            self.state.positions[rec["id"]]["status"] = "UNPROTECTED"
            self.state.save()
            return rec
        C.log("order", mode=self.mode, rule=rule["id"], sym=sg.sym, kind=sg.entry, qty=qty, price=rec["price"], ref=ref,
              stop=stop_px, leverage=L, margin_usdt=margin, expires=rec["expires_at"], why=sg.note)
        if r.get("filled"):
            self._open_position(rec, r, now)
        else:
            st.orders[rec["id"]] = rec
        return rec

    # -- kill switch
    def kill(self, reason="kill command"):
        """Cancel and close everything. On the exchange first; state drops only what the exchange confirmed closed
        (the rest stays, marked, and the next cycle tries again while the KILL file is there)."""
        G.set_kill(True)
        now = self.now_fn()
        out = dict(reason=reason, cancelled=[], closed=[], still_open=[])
        for oid, o in list(self.state.orders.items()):
            try:
                self.broker.cancel_entry(o)
                out["cancelled"].append(o["sym"])
                del self.state.orders[oid]
            except Exception as e:
                C.log("cancel_error", order=oid, error=str(e))
        res = self.broker.kill_all(self.state)
        out["exchange"] = res
        done = {r["sym"]: r for r in res if r.get("sym")}
        for pid, p in list(self.state.positions.items()):
            r = done.get(p["sym"])
            if self.mode == "paper" or (r and r.get("ok")):
                try:
                    px = self.broker.exit(p, now) if self.mode == "paper" else r.get("price")
                except Exception:
                    px = None
                self._close(pid, px, "kill", now)
                out["closed"].append(p["sym"])
            else:
                p["status"] = "KILL_PENDING"
                out["still_open"].append(p["sym"])
        self.state.save()
        C.log("kill", **out)
        return out

    def status(self):
        return dict(mode=self.mode, kill_switch=G.killed(), rules=list(self.rules), guard=self.cfg["guard"],
                    resting=list(self.state.orders.values()), open=list(self.state.positions.values()),
                    closed=len(self.state.d["closed"]), last_bar=self.state.d.get("last_bar"))

    def run_forever(self):
        C.log("start", mode=self.mode, rules=list(self.rules), home=C.home())
        while True:
            try:
                self.cycle(full=True)
            except Exception as e:
                C.log("cycle_error", error=f"{type(e).__name__}: {e}")
            step = min([tf_delta(st.tf) for st in self.strats.values()] or [pd.Timedelta(hours=1)])   # the shortest rule bar
            nxt = (self.now_fn().floor(step) + step + pd.Timedelta(seconds=self.cfg["poll_delay_s"]))
            while self.now_fn() < nxt:
                time.sleep(max(1.0, min(self.cfg["check_every_s"], (nxt - self.now_fn()).total_seconds())))
                if self.now_fn() < nxt:
                    try:
                        self.cycle(full=False)
                    except Exception as e:
                        C.log("cycle_error", error=f"{type(e).__name__}: {e}")


def standalone_kill(cfg=None, mode=None):
    """Kill without building strategies (works even if a rule file is broken)."""
    cfg = cfg or C.load()
    G.set_kill(True)
    from edges.bots.state import State
    st = State()
    mode = mode or st.d.get("mode") or cfg.get("mode", "paper")
    r = Runner.__new__(Runner)
    r.cfg, r.mode, r.state, r.now_fn, r.cache = cfg, mode, st, (lambda: pd.Timestamp.now(tz="UTC")), {}
    r.market = None
    if mode == "paper":
        r.broker = PaperBroker()
    else:
        k, s = keys.binance(mode)
        url = cfg["binance"]["live_url"] if mode == "live" else cfg["binance"]["testnet_url"]
        r.broker = ExchangeBroker(BinanceFutures(url, k, s, cfg=cfg["binance"]), mode)
    return r.kill()
