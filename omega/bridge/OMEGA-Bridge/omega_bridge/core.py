"""One entry point for both venues: preview (exact order + every guard check) and place (only if every check passes)."""
from . import guard, log
from .config import load
from .binance import Binance, BinanceError
from .mt5 import MT5, MT5Error
class Bridge:
    def __init__(self, cfg=None, binance=None, mt5=None):
        self.cfg = cfg or load(); self._b, self._m = binance, mt5
    def b(self):
        if self._b is None: self._b = Binance(self.cfg['binance'])
        return self._b
    def m(self):
        if self._m is None: self._m = MT5(self.cfg['mt5'])
        return self._m
    def _state(self, venue):
        if venue == 'binance':
            b = self.b(); return dict(live=b.live, live_allowed=bool(self.cfg['binance'].get('live')), open_positions=len(b.positions()), day_pnl_usd=b.day_pnl())
        m = self.m(); a = m.account(); return dict(live=not a['demo'], live_allowed=bool(self.cfg['mt5'].get('live')), open_positions=len(m.positions()), day_pnl_usd=m.day_pnl())
    def status(self):
        out = dict(kill_switch=guard.killed(), guard=self.cfg['guard'])
        for v in ('binance', 'mt5'):
            if not self.cfg[v].get('enabled'): out[v] = 'disabled in config.json'; continue
            try:
                st = self._state(v); out[v] = dict(mode='LIVE' if st['live'] else ('demo' if v == 'mt5' else 'testnet'), **st)
                out[v]['balance'] = self.b().balance() if v == 'binance' else self.m().account()['balance']
            except (BinanceError, MT5Error) as e: out[v] = f'not connected: {e}'
        return out
    def preview(self, venue, symbol, side, size_usd=None, volume=None, risk_usd=None, type_='MARKET', price=None, stop=None, target=None):
        side = side.upper(); type_ = type_.upper()
        if venue == 'binance': o = self.b().prepare(symbol.upper(), side, size_usd=size_usd, qty=volume, type_=type_, price=price, stop=stop, target=target)
        elif venue == 'mt5': o = self.m().prepare(symbol.upper(), side, volume=volume, risk_usd=risk_usd, type_=type_, price=price, stop=stop, target=target)
        else: raise ValueError('venue must be binance or mt5')
        blocks = guard.check(self.cfg, venue, o, self._state(venue))
        return dict(venue=venue, order=o, allowed=not blocks, blocked_because=blocks)
    def place(self, venue, symbol, side, confirm=False, **kw):
        p = self.preview(venue, symbol, side, **kw)
        if not p['allowed']: log.write('refused', venue=venue, order=p['order'], reasons=p['blocked_because']); return dict(sent=False, **p)
        if not confirm: return dict(sent=False, note='preview only: call again with confirm=true to send', **p)
        try: res = (self.b() if venue == 'binance' else self.m()).send(p['order'])
        except (BinanceError, MT5Error) as e: log.write('error', venue=venue, order=p['order'], error=str(e)); return dict(sent=False, error=str(e), **p)
        log.write('sent', venue=venue, order=p['order'], result=res); return dict(sent=True, result=res, **p)
    def positions(self, venue): return self.b().positions() if venue == 'binance' else self.m().positions()
    def close(self, venue, symbol):
        r = self.b().close(symbol.upper()) if venue == 'binance' else self.m().close(symbol.upper()); log.write('close', venue=venue, symbol=symbol, result=r); return r
    def kill(self, on=True, flatten=False):
        guard.set_kill(on); out = dict(kill_switch=on, flattened=[])
        if on and flatten:
            for v in ('binance', 'mt5'):
                try:
                    for p in self.positions(v): out['flattened'].append(dict(venue=v, symbol=p['symbol'], result=self.close(v, p['symbol'])))
                except (BinanceError, MT5Error) as e: out['flattened'].append(dict(venue=v, error=str(e)))
        log.write('kill', **out); return out
