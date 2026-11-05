import json, os, copy
HOME = os.environ.get('OMEGA_BRIDGE_HOME') or os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'), 'OMEGA-Bridge')
DEFAULTS = {
  'guard': {'max_order_usd': 10.0, 'max_risk_usd': 1.0, 'max_open_positions': 3, 'daily_loss_limit_usd': 5.0, 'require_stop': True, 'symbols': []},
  'binance': {'enabled': True, 'live': False, 'testnet_url': 'https://testnet.binancefuture.com', 'live_url': 'https://fapi.binance.com', 'leverage': 1, 'margin': 'ISOLATED'},
  'mt5': {'enabled': True, 'live': False, 'path': '', 'login': 0, 'server': '', 'deviation_points': 20, 'magic': 77777},
}
def path(name): os.makedirs(HOME, exist_ok=True); return os.path.join(HOME, name)
def load():
    c = copy.deepcopy(DEFAULTS); p = path('config.json')
    if os.path.exists(p):
        u = json.load(open(p, encoding='utf-8'))
        for k, v in u.items():
            if isinstance(v, dict) and k in c: c[k].update(v)
            else: c[k] = v
    else: json.dump(c, open(p, 'w', encoding='utf-8'), indent=2)
    for k in ('binance', 'mt5'):                                     # refuse a config file that tries to hold secrets
        for bad in ('key', 'secret', 'password', 'api_key', 'api_secret'):
            if bad in c.get(k, {}): raise ValueError(f'config.json must not contain "{bad}": secrets go in the Windows vault (python -m omega_bridge setkey)')
    return c
