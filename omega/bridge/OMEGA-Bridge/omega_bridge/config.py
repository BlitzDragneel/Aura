import json, os, copy
HOME = os.environ.get('OMEGA_BRIDGE_HOME') or os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'), 'OMEGA-Bridge')
DEFAULTS = {
  'guard': {'max_order_usd': 10.0, 'max_risk_usd': 1.0, 'max_open_positions': 3, 'daily_loss_limit_usd': 5.0, 'require_stop': True, 'symbols': [],
            'max_mt5_lots': 0.1, 'allow_add_to_position': False, 'require_ip_restriction': True, 'live_confirm_dialog': True},
  'binance': {'enabled': True, 'live': False, 'testnet_url': 'https://testnet.binancefuture.com', 'live_url': 'https://fapi.binance.com', 'leverage': 1, 'margin': 'ISOLATED',
              'spot_url': 'https://api.binance.com', 'recv_window': 5000},
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
    bad = _secretish(c)                                               # refuse a config file that tries to hold secrets, at any depth
    if bad: raise ValueError(f'config.json must not contain "{bad}": secrets go in the Windows vault (python -m omega_bridge setkey)')
    return c
SECRET_NAMES = ('key', 'secret', 'password', 'passwd', 'api_key', 'api_secret', 'apikey', 'token')
def _secretish(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if str(k).lower() in SECRET_NAMES: return k
            b = _secretish(v)
            if b: return b
    elif isinstance(x, list):
        for v in x:
            b = _secretish(v)
            if b: return b
    return None
