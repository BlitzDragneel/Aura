"""MetaTrader 5 (Exness or any MT5 broker) through the official MetaTrader5 package. Windows, with the MT5 terminal installed.
Sizes by lots or by money at risk (MT5's own profit calculator), stop and target attached to the order."""
import math, datetime as dt
from . import secrets
class MT5Error(Exception): pass
def _mod():
    try:
        import MetaTrader5 as m; return m
    except ImportError: raise MT5Error('the MetaTrader5 package is not installed (Windows only): pip install MetaTrader5')
class MT5:
    def __init__(self, cfg, mod=None):
        self.cfg = cfg; self.m = mod or _mod(); self.ok = False
    def connect(self):
        if self.ok: return
        m, c = self.m, self.cfg; kw = {}
        if c.get('path'): kw['path'] = c['path']
        if c.get('login'): kw.update(login=int(c['login']), server=c.get('server', ''), password=secrets.get('mt5_password') or '')
        if not m.initialize(**kw): raise MT5Error(f'MT5 did not start or log in: {m.last_error()}  (is the terminal installed and logged in?)')
        self.ok = True
    def account(self):
        self.connect(); a = self.m.account_info()
        if a is None: raise MT5Error(f'no account: {self.m.last_error()}')
        return dict(login=a.login, server=a.server, currency=a.currency, balance=a.balance, equity=a.equity, demo=a.trade_mode == self.m.ACCOUNT_TRADE_MODE_DEMO)
    def resolve(self, symbol):
        """Exness names symbols with suffixes on some accounts (XAUUSDm, EURUSDc): find the tradable one."""
        self.connect(); s = self.m.symbol_info(symbol)
        if s is None:
            cands = [x.name for x in (self.m.symbols_get(group='*' + symbol + '*') or []) if x.name.upper().startswith(symbol.upper())]
            if not cands: raise MT5Error(f'{symbol} is not available on this MT5 account')
            symbol = sorted(cands, key=len)[0]; s = self.m.symbol_info(symbol)
        if not s.visible: self.m.symbol_select(symbol, True)
        return symbol, s
    def price(self, symbol):
        sym, _ = self.resolve(symbol); t = self.m.symbol_info_tick(sym); return dict(symbol=sym, bid=t.bid, ask=t.ask)
    def positions(self):
        self.connect(); return [dict(ticket=p.ticket, symbol=p.symbol, side='BUY' if p.type == 0 else 'SELL', volume=p.volume, entry=p.price_open, sl=p.sl, tp=p.tp, pnl=p.profit) for p in (self.m.positions_get() or [])]
    def day_pnl(self):
        self.connect(); t0 = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        deals = self.m.history_deals_get(t0, dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)) or []
        return sum(d.profit + d.commission + d.swap + getattr(d, 'fee', 0.0) for d in deals) + sum(p['pnl'] for p in self.positions())
    def prepare(self, symbol, side, volume=None, risk_usd=None, type_='MARKET', price=None, stop=None, target=None):
        m = self.m; sym, s = self.resolve(symbol); t = m.symbol_info_tick(sym)
        px = float(price) if (type_ == 'LIMIT' and price) else (t.ask if side == 'BUY' else t.bid)
        ot = m.ORDER_TYPE_BUY if side == 'BUY' else m.ORDER_TYPE_SELL
        if stop is not None and ((side == 'BUY' and stop >= px) or (side == 'SELL' and stop <= px)): raise MT5Error('the stop is on the wrong side of the price')
        loss1 = abs(m.order_calc_profit(ot, sym, 1.0, px, float(stop))) if stop is not None else None    # loss for 1 lot if the stop is hit
        if volume is None:
            if risk_usd is None or not loss1: raise MT5Error('give a volume in lots, or a risk in USD together with a stop')
            volume = risk_usd/loss1
        v = math.floor(volume/s.volume_step + 1e-9)*s.volume_step; v = round(v, 8)
        if v < s.volume_min: raise MT5Error(f'{sym}: {volume:.4f} lots is below the minimum {s.volume_min} (a {s.volume_min}-lot stop here would risk {loss1*s.volume_min:.2f} {self.account()["currency"]})' if loss1 else f'{sym}: below the minimum volume {s.volume_min}')
        r = lambda x: None if x is None else round(float(x), s.digits)
        o = dict(symbol=sym, side=side, type=type_, volume=v, price=r(px), stop=r(stop), target=r(target), contract=s.trade_contract_size)
        o['risk_usd'] = loss1*v if loss1 else None; o['notional_usd'] = v*s.trade_contract_size*px; o['has_stop'] = stop is not None
        return o
    def send(self, o):
        m = self.m; s = m.symbol_info(o['symbol']); fm = s.filling_mode
        fill = m.ORDER_FILLING_FOK if fm & 1 else (m.ORDER_FILLING_IOC if fm & 2 else m.ORDER_FILLING_RETURN)
        req = dict(action=m.TRADE_ACTION_DEAL if o['type'] == 'MARKET' else m.TRADE_ACTION_PENDING, symbol=o['symbol'], volume=o['volume'],
                   type=(m.ORDER_TYPE_BUY if o['side'] == 'BUY' else m.ORDER_TYPE_SELL) if o['type'] == 'MARKET' else (m.ORDER_TYPE_BUY_LIMIT if o['side'] == 'BUY' else m.ORDER_TYPE_SELL_LIMIT),
                   price=o['price'], deviation=int(self.cfg.get('deviation_points', 20)), magic=int(self.cfg.get('magic', 77777)), comment='OMEGA Bridge', type_time=m.ORDER_TIME_GTC, type_filling=fill)
        if o['stop'] is not None: req['sl'] = o['stop']
        if o['target'] is not None: req['tp'] = o['target']
        res = m.order_send(req)
        if res is None or res.retcode != m.TRADE_RETCODE_DONE: raise MT5Error(f"MT5 refused the order: {getattr(res, 'retcode', None)} {getattr(res, 'comment', m.last_error())}")
        return dict(order=res.order, deal=getattr(res, 'deal', None), price=getattr(res, 'price', None), volume=o['volume'])
    def close(self, symbol):
        sym, _ = self.resolve(symbol); out = []
        for p in [x for x in (self.m.positions_get(symbol=sym) or [])]:
            t = self.m.symbol_info_tick(sym); side = 'SELL' if p.type == 0 else 'BUY'
            req = dict(action=self.m.TRADE_ACTION_DEAL, symbol=sym, volume=p.volume, type=self.m.ORDER_TYPE_SELL if side == 'SELL' else self.m.ORDER_TYPE_BUY, position=p.ticket,
                       price=t.bid if side == 'SELL' else t.ask, deviation=int(self.cfg.get('deviation_points', 20)), magic=int(self.cfg.get('magic', 77777)), comment='OMEGA Bridge close')
            r = self.m.order_send(req); out.append(dict(ticket=p.ticket, retcode=getattr(r, 'retcode', None)))
        return dict(closed=bool(out), results=out)
    def cancel(self, order_id):
        r = self.m.order_send(dict(action=self.m.TRADE_ACTION_REMOVE, order=int(order_id))); return dict(retcode=getattr(r, 'retcode', None))
