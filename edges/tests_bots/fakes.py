"""Test doubles: a simulated Binance USDT-M futures REST API (httpx.MockTransport), a market-data feed from a frame,
and a one-signal strategy."""
import hashlib, hmac, json, urllib.parse
import httpx
import numpy as np
import pandas as pd
from edges.bots.core import Signal, Strategy

SECRET = "test-secret-never-logged"
KEY = "test-key"


class FakeBinance:
    def __init__(self, price=100.0, withdrawals=False, dual=False, algo=True):
        self.price, self.withdrawals, self.dual, self.algo = price, withdrawals, dual, algo
        self.calls, self.orders, self.algos, self.pos = [], {}, {}, {}
        self.next_id = 1000
        self.bad_sig = 0

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handle))

    def _check_sig(self, req, q):
        if "signature" not in q:
            return
        sig = q.pop("signature")
        raw = urllib.parse.urlencode(list(q.items()))
        if hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest() != sig or req.headers.get("X-MBX-APIKEY") != KEY:
            self.bad_sig += 1

    def handle(self, req):
        q = dict(urllib.parse.parse_qsl(req.url.query.decode()))
        self._check_sig(req, dict(q))
        self.calls.append((req.method, req.url.path, q))
        p, m = req.url.path, req.method
        J = lambda x, s=200: httpx.Response(s, json=x)
        if p == "/fapi/v1/exchangeInfo":
            return J(dict(symbols=[dict(symbol="ETHUSDT", status="TRADING", quoteAsset="USDT", contractType="PERPETUAL",
                                        filters=[dict(filterType="LOT_SIZE", stepSize="0.001", minQty="0.001"),
                                                 dict(filterType="MARKET_LOT_SIZE", stepSize="0.001", minQty="0.001"),
                                                 dict(filterType="PRICE_FILTER", tickSize="0.01"),
                                                 dict(filterType="MIN_NOTIONAL", notional="5")])]))
        if p == "/fapi/v1/ticker/price":
            return J(dict(symbol=q["symbol"], price=str(self.price)))
        if p in ("/fapi/v1/marginType", "/fapi/v1/leverage"):
            return J(dict(code=200, msg="success", **q))
        if p == "/fapi/v1/positionSide/dual":
            return J(dict(dualSidePosition=self.dual))
        if p == "/sapi/v1/account/apiRestrictions":
            return J(dict(enableWithdrawals=self.withdrawals, enableFutures=True, enableInternalTransfer=False))
        if p == "/fapi/v1/order" and m == "POST":
            if q["type"] in ("STOP_MARKET", "TAKE_PROFIT_MARKET"):
                return J(dict(code=-4120, msg="Order type not supported for this endpoint. Please use the Algo Order API."), 400)
            oid = self.next_id = self.next_id + 1
            o = dict(orderId=oid, symbol=q["symbol"], side=q["side"], type=q["type"], origQty=q["quantity"],
                     price=q.get("price"), status="NEW", executedQty="0", avgPrice="0", updateTime=0,
                     timeInForce=q.get("timeInForce"), goodTillDate=q.get("goodTillDate"), reduceOnly=q.get("reduceOnly"))
            if q["type"] == "MARKET":
                o.update(status="FILLED", executedQty=q["quantity"], avgPrice=str(self.price))
                sgn = 1 if q["side"] == "BUY" else -1
                cur = self.pos.get(q["symbol"], 0.0)
                new = cur + sgn * float(q["quantity"])
                if q.get("reduceOnly") == "true" and abs(new) > abs(cur):
                    return J(dict(code=-2022, msg="ReduceOnly Order is rejected."), 400)
                self.pos[q["symbol"]] = round(new, 8)
            self.orders[oid] = o
            return J(o)
        if p == "/fapi/v1/algoOrder" and m == "POST":
            if not self.algo:
                return J(dict(code=-5000, msg="Path not found"), 404)
            if getattr(self, "algo_fail", False):
                return J(dict(code=-2021, msg="Order would immediately trigger."), 400)
            aid = self.next_id = self.next_id + 1
            self.algos[aid] = dict(algoId=aid, **q, algoStatus="NEW")
            return J(self.algos[aid])
        if p == "/fapi/v1/order" and m == "GET":
            return J(self.orders[int(q["orderId"])])
        if p == "/fapi/v1/order" and m == "DELETE":
            o = self.orders.get(int(q["orderId"]))
            if not o or o["status"] != "NEW":
                return J(dict(code=-2011, msg="Unknown order sent."), 400)
            o["status"] = "CANCELED"
            return J(o)
        if p == "/fapi/v1/allOpenOrders":
            for o in self.orders.values():
                if o["symbol"] == q["symbol"] and o["status"] == "NEW":
                    o["status"] = "CANCELED"
            return J(dict(code=200, msg="done"))
        if p == "/fapi/v1/algoOpenOrders":
            for a in self.algos.values():
                if a["symbol"] == q["symbol"]:
                    a["algoStatus"] = "CANCELED"
            return J(dict(code=200, msg="done"))
        if p in ("/fapi/v3/positionRisk", "/fapi/v2/positionRisk"):
            return J([dict(symbol=s, positionAmt=str(v), entryPrice=str(self.price), unRealizedProfit="0") for s, v in self.pos.items() if v])
        if p == "/fapi/v1/income":
            return J([])
        if p == "/fapi/v1/userTrades":
            return J([dict(price=str(self.price))])
        if p == "/fapi/v2/balance":
            return J([dict(asset="USDT", balance="100")])
        return J(dict(code=-1, msg=f"unknown path {p}"), 404)

    # test helpers
    def fill(self, oid, t_ms):
        o = self.orders[oid]
        o.update(status="FILLED", executedQty=o["origQty"], avgPrice=o["price"], updateTime=t_ms)
        sgn = 1 if o["side"] == "BUY" else -1
        self.pos[o["symbol"]] = self.pos.get(o["symbol"], 0.0) + sgn * float(o["origQty"])

    def sent(self, path, method="POST"):
        return [q for (m, p, q) in self.calls if p == path and m == method]


def hourly(n=60, start="2026-11-01 00:00", price=100.0):
    idx = pd.date_range(start, periods=n, freq="h", tz="UTC")
    c = np.full(n, price)
    return pd.DataFrame(dict(o=c, h=c * 1.01, l=c * 0.99, c=c, v=1000.0, qv=1e5), index=idx)


class FrameMarket:
    """Market data from a fixed frame: klines() returns only bars closed by `clock()`."""
    def __init__(self, frames, clock):
        self.frames, self.clock = frames, clock

    def exchange_info(self):
        return dict(symbols=[dict(symbol=s, filters=[dict(filterType="LOT_SIZE", stepSize="0.001", minQty="0.001"),
                                                     dict(filterType="PRICE_FILTER", tickSize="0.01"),
                                                     dict(filterType="MIN_NOTIONAL", notional="5")]) for s in self.frames])

    def universe(self, info=None, top=None):
        return {s: {} for s in self.frames}

    def klines(self, sym, tf="1h", limit=1000):
        d = self.frames[sym]
        return d[d.index + pd.Timedelta(hours=1) <= self.clock()].iloc[-limit:]


class OneShot(Strategy):
    """Emits one signal at a chosen bar."""
    id = "fake_rule"
    tf = "1h"
    lookback = 10

    def __init__(self, at, sig):
        super().__init__()
        self.at, self.sig = pd.Timestamp(at), sig
        self.calls = 0

    def signals(self, bars, now):
        self.calls += 1
        if pd.Timestamp(now) == self.at and self.sig.sym in bars:
            return [Signal(**self.sig.to_dict())]
        return []


def approve(home, rules):
    import os
    p = os.path.join(home, "approved.json")
    json.dump(rules, open(p, "w"))
    json.dump({"approved_file": p, "universe": ["ETHUSDT"]}, open(os.path.join(home, "config.json"), "w"))
    return p
