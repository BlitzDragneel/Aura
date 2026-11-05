"""Exness / any MT5 broker through OMEGA Bridge's mt5.py (omega/bridge/OMEGA-Bridge/omega_bridge/mt5.py).

STUB-LEVEL ADAPTER. None of the rules that passed trades on MT5 (they are Binance perpetual rules), so the runner only
uses this for a rule whose approved.json entry says "venue": "mt5". The MetaTrader5 package exists only on Windows
with the MT5 terminal installed; this module imports it lazily and raises MT5Unavailable everywhere else.
Never run against a real terminal from Claude's sandbox. The Bridge's own guard (demo unless live, stop required,
risk cap) still applies inside Bridge; this bot's guard applies first."""
import os, sys


class MT5Unavailable(Exception):
    pass


def bridge_mt5(bridge_path, cfg=None, mod=None):
    if bridge_path and bridge_path not in sys.path:
        sys.path.insert(0, bridge_path)
    try:
        from omega_bridge.mt5 import MT5, MT5Error  # noqa
    except ImportError as e:
        raise MT5Unavailable(f"OMEGA Bridge not found at {bridge_path}: {e}")
    try:
        return MT5(cfg or {}, mod=mod)
    except MT5Error as e:
        raise MT5Unavailable(str(e))


class MT5Broker:
    """The subset the runner needs, mapped onto Bridge's MT5 class (sizes by money at risk with MT5's calculator)."""

    def __init__(self, cfg, mod=None):
        self.cfg = cfg
        self.m = bridge_mt5(cfg.get("bridge_path"), cfg, mod=mod)

    def account(self):
        return self.m.account()

    def is_demo(self):
        return bool(self.m.account()["demo"])

    def entry(self, sym, side, risk_usd, stop_price, kind="MARKET", price=None):
        if not self.is_demo() and not self.cfg.get("live"):
            raise MT5Unavailable("this MT5 account is LIVE and mt5.live is false in config.json")
        o = self.m.prepare(sym, "BUY" if side == "long" else "SELL", risk_usd=risk_usd, type_=kind, price=price, stop=stop_price)
        return self.m.send(o)

    def positions(self):
        return self.m.positions()

    def close(self, sym):
        return self.m.close(sym)

    def day_pnl(self):
        return self.m.day_pnl()
