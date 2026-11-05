import os, sys, tempfile, types, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv('OMEGA_BRIDGE_HOME', str(tmp_path)); import importlib, omega_bridge.config as c; monkeypatch.setattr(c, 'HOME', str(tmp_path)); return tmp_path
class FakeMT5(types.SimpleNamespace):
    """The MetaTrader5 package's functions and constants, enough to drive the adapter (an Exness-style account)."""
    ORDER_TYPE_BUY, ORDER_TYPE_SELL, ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT = 0, 1, 2, 3
    TRADE_ACTION_DEAL, TRADE_ACTION_PENDING, TRADE_ACTION_REMOVE = 1, 5, 8
    ORDER_TIME_GTC, ORDER_FILLING_FOK, ORDER_FILLING_IOC, ORDER_FILLING_RETURN = 0, 0, 1, 2
    TRADE_RETCODE_DONE, ACCOUNT_TRADE_MODE_DEMO = 10009, 0
    def __init__(self, trade_mode=0):
        super().__init__(); self.mode = trade_mode; self.sent = []; self.pos = []; self.deals = []; self.pending = []
        self.syms = {'XAUUSDm': types.SimpleNamespace(name='XAUUSDm', visible=False, volume_min=0.01, volume_step=0.01, volume_max=200, trade_contract_size=100, digits=3, point=0.001, filling_mode=1)}
    def initialize(self, **kw): self.init_kw = kw; return True
    def last_error(self): return (0, 'ok')
    def account_info(self): return types.SimpleNamespace(login=123, server='Exness-MT5Trial', currency='USD', balance=100.0, equity=100.0, trade_mode=self.mode)
    def symbol_info(self, s): return self.syms.get(s)
    def symbols_get(self, group=''): return [v for k, v in self.syms.items() if group.strip('*').upper() in k.upper()]
    def symbol_select(self, s, on): self.syms[s].visible = True; return True
    def symbol_info_tick(self, s): return types.SimpleNamespace(bid=2000.0, ask=2000.3)
    def order_calc_profit(self, t, s, v, o, c): return (c - o)*v*self.syms[s].trade_contract_size*(1 if t == 0 else -1)
    def order_send(self, req): self.sent.append(req); return types.SimpleNamespace(retcode=10009, order=555, deal=777, price=req.get('price'), comment='done')
    def positions_get(self, symbol=None): return [p for p in self.pos if symbol is None or p.symbol == symbol]
    def history_deals_get(self, a, b): return self.deals
    def orders_get(self, symbol=None): return [o for o in self.pending if symbol is None or o.symbol == symbol]
