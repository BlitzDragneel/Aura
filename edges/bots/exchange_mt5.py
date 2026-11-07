"""Exness / any MT5 broker, routed THROUGH OMEGA Bridge's guard (omega/bridge/OMEGA-Bridge/omega_bridge/core.py).

STUB-LEVEL ADAPTER. None of the rules that passed trades on MT5 (they are Binance perpetual rules), so the runner does
not use it yet (a rule with "venue": "mt5" is skipped and logged) and config mt5.enabled is false by default.
Every order goes Bridge.preview -> Bridge.place(confirm=True, preview_id=...), so the Bridge's own guard applies on top
of this bot's: its kill switch, stop required, risk cap, daily loss limit, max positions, demo unless MT5 live is on,
and its on-screen confirmation dialog for LIVE orders. The MetaTrader5 package exists only on Windows with the MT5
terminal installed; it is imported lazily and MT5Unavailable is raised everywhere else. Never run against a real
terminal from Claude's sandbox."""
import sys

from edges.bots import guard as G


class MT5Unavailable(Exception):
    pass


def _bridge(bridge_path, bridge=None):
    if bridge is not None:
        return bridge
    if bridge_path and bridge_path not in sys.path:
        sys.path.insert(0, bridge_path)
    try:
        from omega_bridge.core import Bridge  # noqa
    except ImportError as e:
        raise MT5Unavailable(f"OMEGA Bridge not found at {bridge_path}: {e}")
    return Bridge()


class MT5Broker:
    def __init__(self, cfg, bridge=None):
        if not cfg.get("enabled") and bridge is None:
            raise MT5Unavailable("mt5.enabled is false in config.json")
        self.cfg = cfg
        self.b = _bridge(cfg.get("bridge_path"), bridge)

    def entry(self, sym, side, risk_usd, stop_price, kind="MARKET", price=None):
        """Preview through the Bridge (its guard decides), then place with the preview id. Returns the Bridge result."""
        if G.killed():
            return dict(sent=False, blocked_because=["the kill switch is on"])
        kw = dict(risk_usd=risk_usd, type_=kind, price=price, stop=stop_price)
        p = self.b.preview("mt5", sym, "BUY" if side == "long" else "SELL", **kw)
        if not p.get("allowed"):
            return dict(sent=False, **p)
        return self.b.place("mt5", sym, "BUY" if side == "long" else "SELL", confirm=True, preview_id=p.get("preview_id"), **kw)

    def positions(self):
        return self.b.positions("mt5")

    def close(self, sym):
        return self.b.close("mt5", sym)
