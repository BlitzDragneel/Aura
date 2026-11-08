"""The guard: every order passes every check or it is refused (with the reasons logged). Extends OMEGA Bridge's guard.

Mode ladder: paper (default, no exchange orders) -> testnet (needs testnet keys; rule status testnet|live) -> live
(rule status "live" in approved.json AND config live:true AND env OMEGA_LIVE=I_UNDERSTAND_REAL_MONEY AND a key that
cannot withdraw)."""
import os
from edges.bots.config import path
from edges.bots.core import liquidation_distance, stop_inside_liquidation

LIVE_PHRASE = "I_UNDERSTAND_REAL_MONEY"
MODES = ("paper", "testnet", "live")
ALLOWED_STATUS = {"paper": {"paper", "testnet", "live"}, "testnet": {"testnet", "live"}, "live": {"live"}}


def bridge_kill_path():
    """OMEGA Bridge's kill file: one kill switch for both, since they trade the same Binance account."""
    home = os.environ.get("OMEGA_BRIDGE_HOME") or os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "OMEGA-Bridge")
    return os.path.join(home, "KILL")


def killed():
    return os.path.exists(path("KILL")) or os.path.exists(bridge_kill_path())


def set_kill(on, why="kill switch on: no new orders; everything was cancelled and closed"):
    """On: writes the bots' KILL file AND the Bridge's. Off: removes both (one switch)."""
    for p in (path("KILL"), bridge_kill_path()):
        if on:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w") as f:
                    f.write(why + "\n")
            except OSError:
                pass
        elif os.path.exists(p):
            os.remove(p)


def mode_refusals(cfg, mode, have_keys=None, withdrawals_enabled=None, ip_restricted=True):
    """Reasons the RUNNER may not start in this mode (empty list = ok)."""
    why = []
    if mode not in MODES:
        return [f"unknown mode {mode!r} (paper | testnet | live)"]
    if mode in ("testnet", "live") and not have_keys:
        why.append(f"no Binance {mode} API key: run  python -m edges.bots setkey {mode}  (or set OMEGA_BINANCE_{mode.upper()}_KEY/_SECRET)")
    if mode == "live":
        if not cfg.get("live"):
            why.append('live trading is not switched on in config.json ("live": true)')
        if os.environ.get("OMEGA_LIVE") != LIVE_PHRASE:
            why.append(f"environment variable OMEGA_LIVE is not {LIVE_PHRASE}")
        if withdrawals_enabled is None:
            why.append("could not confirm the live API key has withdrawals disabled")
        elif withdrawals_enabled:
            why.append("the live API key can WITHDRAW (or transfer): create a key with Futures trading only")
        if cfg["guard"].get("require_ip_restriction", True) and not ip_restricted:
            why.append("the live API key is not restricted to your IP address (Binance API management: restrict access to trusted IPs)")
    return why


def rule_refusals(cfg, mode, rule):
    """Reasons a rule may not trade in this mode."""
    if rule is None:
        return ["the rule is not in edges/approved.json"]
    st = rule.get("status", "paper")
    if st not in ALLOWED_STATUS.get(mode, set()):
        return [f"rule {rule['id']} has status {st!r}: {mode} mode needs one of {sorted(ALLOWED_STATUS[mode])}"]
    if mode != "paper" and (rule.get("grade") == "C" or rule.get("book") == "own"):
        return [f"rule {rule['id']} is on the watch list (grade C / own paper book): paper only"]
    if mode == "live" and not (cfg.get("live") and os.environ.get("OMEGA_LIVE") == LIVE_PHRASE):
        return ["live needs config live:true and OMEGA_LIVE=" + LIVE_PHRASE]
    return []


def liq_buffer(cfg, mode=None):
    g = cfg["guard"]
    return max(g["liq_buffer"], g.get("live_liq_buffer", 0.02)) if mode == "live" else g["liq_buffer"]


def protective_stop(cfg, rule_stop, leverage, mode=None):
    """The stop the bot places: the rule's own, else the configured protective one, never outside liquidation."""
    g = cfg["guard"]
    cap = 1.0 / leverage - liq_buffer(cfg, mode) - 0.005
    s = rule_stop if rule_stop is not None else g["protective_stop_pct"]
    return None if s is None else min(float(s), cap)


def order_refusals(cfg, mode, rule, order, book):
    """order: dict(sym, leverage, margin_usdt, notional, stop_pct, reduce_only)
    book:  dict(open_count, open_symbols, day_pnl_usdt)"""
    g = cfg["guard"]
    why = []
    if killed():
        why.append("the kill switch is on")
    why += rule_refusals(cfg, mode, rule)
    if order.get("reduce_only"):
        return []                       # closing a position is always allowed (even with the kill switch on)
    L = order["leverage"]
    lmax = min(int(g["hard_max_leverage"]), int((rule or {}).get("max_leverage", 1)))
    if L < 1 or L > lmax:
        why.append(f"leverage {L}x is above the allowed {lmax}x (rule max_leverage and guard.hard_max_leverage)")
    if order["margin_usdt"] > g["max_margin_usdt"] + 1e-9:
        why.append(f"margin {order['margin_usdt']:.2f} USDT is above max_margin_usdt {g['max_margin_usdt']}")
    sp = order.get("stop_pct")
    if g["require_stop"] and sp is None:
        why.append("every position needs a stop (guard.require_stop)")
    buf = liq_buffer(cfg, mode)
    if sp is not None and not stop_inside_liquidation(sp, L, buf):
        why.append(f"stop {sp*100:.1f}% is not inside the liquidation distance at {L}x "
                   f"({liquidation_distance(L)*100:.1f}%; must be < {(1/L - buf)*100:.1f}%)")
    if sp is not None and order.get("notional") is not None and g.get("max_risk_usdt") is not None:
        risk = order["notional"] * sp
        if risk > g["max_risk_usdt"] + 1e-9:
            why.append(f"risk if the stop is hit {risk:.2f} USDT (size {order['notional']:.2f} x stop {sp*100:.1f}%) "
                       f"is above max_risk_usdt {g['max_risk_usdt']}")
    if book["open_count"] >= g["max_open_positions"]:
        why.append(f"{book['open_count']} positions/orders already open (max {g['max_open_positions']})")
    if g.get("one_position_per_symbol", True) and order["sym"] in book.get("open_symbols", set()):
        why.append(f"{order['sym']} already has an open position or order (one per coin: Binance nets positions)")
    if book["day_pnl_usdt"] <= -g["daily_loss_limit_usdt"]:
        why.append(f"today's result {book['day_pnl_usdt']:.2f} USDT reached the daily loss limit {g['daily_loss_limit_usdt']}")
    return why
