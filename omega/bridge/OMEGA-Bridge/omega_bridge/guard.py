"""One guard for both venues. An order goes out only if every check passes; every refusal is logged with its reasons."""
import os
from .config import path
def killed(): return os.path.exists(path('KILL'))
def set_kill(on):
    p = path('KILL')
    if on: open(p, 'w').write('kill switch on: no new orders\n')
    elif os.path.exists(p): os.remove(p)
def check(cfg, venue, order, state):
    """order: dict(symbol, side, notional_usd, risk_usd or None, has_stop); state: dict(live, live_allowed, open_positions, day_pnl_usd)."""
    g = cfg['guard']; why = []
    if killed(): why.append('the kill switch is on')
    if state.get('live') and not state.get('live_allowed'): why.append(f'{venue} is a LIVE account but live trading is not switched on in config.json')
    if g['symbols'] and order['symbol'] not in g['symbols']: why.append(f"{order['symbol']} is not in the allowed symbols")
    if g['require_stop'] and not order.get('has_stop'): why.append('every order needs a stop (guard.require_stop)')
    if venue == 'binance' and order['notional_usd'] > g['max_order_usd'] + 1e-9: why.append(f"size {order['notional_usd']:.2f} USD is above max_order_usd {g['max_order_usd']}")
    if order.get('risk_usd') is not None and order['risk_usd'] > g['max_risk_usd'] + 1e-9: why.append(f"risk if the stop is hit {order['risk_usd']:.2f} USD is above max_risk_usd {g['max_risk_usd']}")
    if not order.get('reduce_only') and state['open_positions'] >= g['max_open_positions']: why.append(f"{state['open_positions']} positions already open (max {g['max_open_positions']})")
    if state['day_pnl_usd'] <= -g['daily_loss_limit_usd']: why.append(f"today's result {state['day_pnl_usd']:.2f} USD has reached the daily loss limit {g['daily_loss_limit_usd']}")
    return why
