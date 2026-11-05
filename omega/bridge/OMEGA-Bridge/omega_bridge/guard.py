"""One guard for both venues. An order goes out only if every check passes; every refusal is logged with its reasons."""
import math, os
from .config import path
def killed(): return os.path.exists(path('KILL'))
def set_kill(on):
    p = path('KILL')
    if on:
        with open(p, 'w') as f: f.write('kill switch on: no new orders\n')
    elif os.path.exists(p): os.remove(p)
def _bad_number(x): return x is None or isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0
def check(cfg, venue, order, state):
    """order: dict(symbol, side, type, notional_usd, risk_usd or None, has_stop, stop, ...);
    state: dict(live, live_allowed, open_positions, open_symbols, day_pnl_usd, key_restrictions for Binance live)."""
    g = cfg['guard']; why = []
    if killed(): why.append('the kill switch is on')
    if state.get('live') and not state.get('live_allowed'): why.append(f'{venue} is a LIVE account but live trading is not switched on in config.json')
    if order.get('side') not in ('BUY', 'SELL'): why.append(f"side must be BUY or SELL, not {order.get('side')!r}")
    if order.get('type') not in ('MARKET', 'LIMIT'): why.append(f"order type must be MARKET or LIMIT, not {order.get('type')!r}")
    size = order.get('quantity') if venue == 'binance' else order.get('volume')
    if _bad_number(size) or _bad_number(order.get('notional_usd')): why.append('the size is not a positive finite number')
    for k in ('stop', 'target', 'price'):
        if order.get(k) is not None and _bad_number(order[k]): why.append(f'{k} is not a positive finite number')
    if order.get('risk_usd') is not None and (not isinstance(order['risk_usd'], (int, float)) or not math.isfinite(order['risk_usd'])): why.append('the risk could not be computed')
    if g['symbols'] and order['symbol'] not in g['symbols']: why.append(f"{order['symbol']} is not in the allowed symbols")
    if g['require_stop'] and not order.get('has_stop'): why.append('every order needs a stop (guard.require_stop)')
    if g['require_stop'] and order.get('has_stop') and order.get('risk_usd') is None: why.append('the risk to the stop could not be computed')
    if venue == 'binance' and isinstance(order.get('notional_usd'), (int, float)) and order['notional_usd'] > g['max_order_usd'] + 1e-9: why.append(f"size {order['notional_usd']:.2f} USD is above max_order_usd {g['max_order_usd']}")
    if venue == 'mt5' and g.get('max_mt5_lots') and isinstance(size, (int, float)) and size > g['max_mt5_lots'] + 1e-9: why.append(f"{size} lots is above max_mt5_lots {g['max_mt5_lots']} (a tight stop does not cap a gap or slippage)")
    if order.get('risk_usd') is not None and order['risk_usd'] > g['max_risk_usd'] + 1e-9: why.append(f"risk if the stop is hit {order['risk_usd']:.2f} USD is above max_risk_usd {g['max_risk_usd']}")
    if not order.get('reduce_only') and state['open_positions'] >= g['max_open_positions']: why.append(f"{state['open_positions']} positions already open (max {g['max_open_positions']}; resting entry orders count)")
    if not order.get('reduce_only') and not g.get('allow_add_to_position') and order['symbol'] in state.get('open_symbols', ()): why.append(f"{order['symbol']} already has a position or a resting entry order (adding to it would pass the size cap order by order)")
    if state['day_pnl_usd'] <= -g['daily_loss_limit_usd']: why.append(f"today's result {state['day_pnl_usd']:.2f} USD has reached the daily loss limit {g['daily_loss_limit_usd']}")
    if venue == 'binance' and state.get('live'):
        kr = state.get('key_restrictions')
        if not isinstance(kr, dict): why.append(f'the live API key\'s permissions could not be checked ({kr}): live orders are refused until they can')
        elif kr.get('enableWithdrawals'): why.append('the live API key can WITHDRAW funds: make a key with withdrawals disabled')
        elif g.get('require_ip_restriction', True) and not kr.get('ipRestrict'): why.append('the live API key is not restricted to your IP address (Binance API management): restrict it, or set guard.require_ip_restriction false')
    return why
