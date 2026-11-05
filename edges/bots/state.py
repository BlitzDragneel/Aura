"""Bot state on disk (JSON, written atomically): resting orders, open positions, closed trades, last bar processed."""
import json, os
from edges.bots.config import path


class State:
    def __init__(self, name="state.json"):
        self.file = path(name)
        self.d = dict(orders={}, positions={}, closed=[], last_bar=None, seen=[], mode=None)
        if os.path.exists(self.file):
            self.d.update(json.load(open(self.file, encoding="utf-8")))

    def save(self):
        tmp = self.file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.d, f, indent=1, default=str)
        os.replace(tmp, self.file)

    # helpers
    @property
    def orders(self):
        return self.d["orders"]

    @property
    def positions(self):
        return self.d["positions"]

    def busy(self, strategy, sym):
        return any(o["strategy"] == strategy and o["sym"] == sym for o in self.orders.values()) or \
            any(p["strategy"] == strategy and p["sym"] == sym for p in self.positions.values())

    def open_symbols(self):
        return {o["sym"] for o in self.orders.values()} | {p["sym"] for p in self.positions.values()}

    def open_count(self):
        return len(self.orders) + len(self.positions)

    def seen(self, key):
        return key in self.d["seen"]

    def mark_seen(self, key):
        self.d["seen"].append(key)
        self.d["seen"] = self.d["seen"][-5000:]

    def day_pnl(self, day):
        return sum(c.get("pnl_usdt") or 0.0 for c in self.d["closed"] if str(c.get("exit_time", ""))[:10] == day)
