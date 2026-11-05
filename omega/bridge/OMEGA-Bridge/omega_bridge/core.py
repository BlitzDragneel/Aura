"""One entry point for both venues: preview (exact order + every guard check) and place (only if every check passes).
Sending needs three things: a preview of exactly that order made in the last PREVIEW_TTL_S seconds (its preview_id),
confirm=true, and on a LIVE account a Yes clicked by a person in a dialog on this PC (human.confirm)."""
import json, math, secrets as _rnd, time
from . import guard, log, human
from .config import load
from .binance import Binance, BinanceError, BinanceProtectError
from .mt5 import MT5, MT5Error
PREVIEW_TTL_S = 120
def _num(name, v):
    if v is None: return None
    if isinstance(v, bool) or not isinstance(v, (int, float)): raise ValueError(f'{name} must be a number')
    v = float(v)
    if not math.isfinite(v) or v <= 0: raise ValueError(f'{name} must be a positive finite number')
    return v
class Bridge:
    def __init__(self, cfg=None, binance=None, mt5=None, confirm_dialog=None):
        self.cfg = cfg or load(); self._b, self._m = binance, mt5; self._previews = {}; self._dialog = confirm_dialog
    def b(self):
        if self._b is None: self._b = Binance(self.cfg['binance'])
        return self._b
    def m(self):
        if self._m is None: self._m = MT5(self.cfg['mt5'])
        return self._m
    def _state(self, venue):
        if venue == 'binance':
            b = self.b(); syms = sorted({p['symbol'] for p in b.positions()} | set(b.pending_entries()))
            st = dict(live=b.live, live_allowed=bool(self.cfg['binance'].get('live')), open_positions=len(syms), open_symbols=syms, day_pnl_usd=b.day_pnl())
            if b.live:
                try: st['key_restrictions'] = b.key_restrictions()
                except BinanceError as e: st['key_restrictions'] = str(e)
            return st
        m = self.m(); a = m.account(); syms = sorted({p['symbol'] for p in m.positions()} | {o['symbol'] for o in m.pending()})
        return dict(live=not a['demo'], live_allowed=bool(self.cfg['mt5'].get('live')), open_positions=len(syms), open_symbols=syms, day_pnl_usd=m.day_pnl())
    def status(self):
        out = dict(kill_switch=guard.killed(), guard=self.cfg['guard'])
        for v in ('binance', 'mt5'):
            if not self.cfg[v].get('enabled'): out[v] = 'disabled in config.json'; continue
            try:
                st = self._state(v); out[v] = dict(mode='LIVE' if st['live'] else ('demo' if v == 'mt5' else 'testnet'), **st)
                out[v]['balance'] = self.b().balance() if v == 'binance' else self.m().account()['balance']
            except (BinanceError, MT5Error) as e: out[v] = f'not connected: {e}'
        return out
    @staticmethod
    def _fingerprint(venue, symbol, side, kw):
        return json.dumps([venue, symbol.upper(), side.upper(), {k: kw.get(k) for k in sorted(kw)}], sort_keys=True, default=str)
    def preview(self, venue, symbol, side, size_usd=None, volume=None, risk_usd=None, type_='MARKET', price=None, stop=None, target=None):
        if venue not in ('binance', 'mt5'): raise ValueError('venue must be binance or mt5')
        if not self.cfg[venue].get('enabled'): raise ValueError(f'{venue} is disabled in config.json')
        side = str(side).upper(); type_ = str(type_).upper()
        if side not in ('BUY', 'SELL'): raise ValueError('side must be BUY or SELL')
        if type_ not in ('MARKET', 'LIMIT'): raise ValueError('order type must be MARKET or LIMIT')
        size_usd, volume, risk_usd, price, stop, target = (_num(n, v) for n, v in (('size_usd', size_usd), ('volume', volume), ('risk_usd', risk_usd), ('price', price), ('stop', stop), ('target', target)))
        if type_ == 'LIMIT' and price is None: raise ValueError('a LIMIT order needs a price')
        if venue == 'binance': o = self.b().prepare(symbol.upper(), side, size_usd=size_usd, qty=volume, type_=type_, price=price, stop=stop, target=target)
        else: o = self.m().prepare(symbol.upper(), side, volume=volume, risk_usd=risk_usd, type_=type_, price=price, stop=stop, target=target)
        st = self._state(venue); blocks = guard.check(self.cfg, venue, o, st)
        out = dict(venue=venue, mode='LIVE' if st['live'] else 'demo/testnet', order=o, allowed=not blocks, blocked_because=blocks)
        if not blocks:
            now = time.time(); self._previews = {k: v for k, v in self._previews.items() if now - v[0] < PREVIEW_TTL_S}
            pid = _rnd.token_hex(8); self._previews[pid] = (now, self._fingerprint(venue, symbol, side, dict(size_usd=size_usd, volume=volume, risk_usd=risk_usd, type_=type_, price=price, stop=stop, target=target)))
            out['preview_id'] = pid; out['preview_expires_s'] = PREVIEW_TTL_S
        return out
    def place(self, venue, symbol, side, confirm=False, preview_id=None, **kw):
        p = self.preview(venue, symbol, side, **kw); p.pop('preview_id', None); p.pop('preview_expires_s', None)
        if not p['allowed']: log.write('refused', venue=venue, order=p['order'], reasons=p['blocked_because']); return dict(sent=False, **p)
        if not confirm: return dict(sent=False, note='preview only: call again with confirm=true and the preview_id to send', **p)
        rec = self._previews.get(preview_id or '')
        norm = {k: _num(k, kw.get(k)) if k != 'type_' else str(kw.get(k, 'MARKET')).upper() for k in ('size_usd', 'volume', 'risk_usd', 'type_', 'price', 'stop', 'target')}
        if norm['type_'] is None: norm['type_'] = 'MARKET'
        if not rec or time.time() - rec[0] >= PREVIEW_TTL_S or rec[1] != self._fingerprint(venue, symbol, side, norm):
            why = 'no matching preview: call preview_order for exactly this order, show it to the user, then place_order with its preview_id (valid %d s, once)' % PREVIEW_TTL_S
            log.write('refused', venue=venue, order=p['order'], reasons=[why]); return dict(sent=False, blocked_because=[why], **{k: v for k, v in p.items() if k != 'blocked_because'})
        del self._previews[preview_id]                                          # single use
        if p['mode'] == 'LIVE' and self.cfg['guard'].get('live_confirm_dialog', True):
            o = p['order']; txt = (f"OMEGA Bridge wants to send a LIVE order on {venue.upper()}:\n\n{o['side']} {o.get('quantity', o.get('volume'))} {o['symbol']} {o['type']}"
                                   f"\nsize ≈ {o['notional_usd']:.2f}   stop {o['stop']}   target {o.get('target')}\nrisk if the stop is hit ≈ {o.get('risk_usd') or 0:.2f}\n\nSend it? (No = nothing is sent)")
            if not human.confirm('OMEGA Bridge: LIVE order', txt, dialog=self._dialog):
                why = 'the person at the PC did not confirm this LIVE order in the on-screen dialog (or answered after %d s)' % human.MAX_WAIT_S
                log.write('refused', venue=venue, order=o, reasons=[why]); return dict(sent=False, blocked_because=[why], **{k: v for k, v in p.items() if k != 'blocked_because'})
        try: res = (self.b() if venue == 'binance' else self.m()).send(p['order'])
        except BinanceProtectError as e:
            log.write('error', venue=venue, order=p['order'], error=str(e), detail=e.detail)
            if e.detail.get('unwind', {}).get('unprotected'): guard.set_kill(True)   # a position may be open without a stop: stop everything new
            return dict(sent=False, error=str(e), detail=e.detail, **p)
        except (BinanceError, MT5Error) as e: log.write('error', venue=venue, order=p['order'], error=str(e)); return dict(sent=False, error=str(e), **p)
        log.write('sent', venue=venue, order=p['order'], result=res); return dict(sent=True, result=res, **p)
    def positions(self, venue): return self.b().positions() if venue == 'binance' else self.m().positions()
    def close(self, venue, symbol):
        r = self.b().close(symbol.upper()) if venue == 'binance' else self.m().close(symbol.upper()); log.write('close', venue=venue, symbol=symbol, result=r); return r
    def _cancel_pending(self, venue):
        if venue == 'binance':
            b = self.b(); out = []
            for o in b.open_orders():
                if str(o.get('reduceOnly')).lower() == 'true' or str(o.get('closePosition')).lower() == 'true': continue   # stops stay until the position is closed
                try: out.append(dict(symbol=o['symbol'], cancelled=b.cancel(o['symbol'], o['orderId'])))
                except BinanceError as e: out.append(dict(symbol=o.get('symbol'), error=str(e)))
            return out
        return self.m().cancel_all_pending()
    def kill(self, on=True, flatten=False):
        guard.set_kill(on); out = dict(kill_switch=on, flattened=[], cancelled=[])
        if on and flatten:
            for v in ('binance', 'mt5'):                                        # one venue failing never stops the other
                try: out['cancelled'].append(dict(venue=v, orders=self._cancel_pending(v)))
                except Exception as e: out['cancelled'].append(dict(venue=v, error=f'{type(e).__name__}: {e}'))
                try: ps = self.positions(v)
                except Exception as e: out['flattened'].append(dict(venue=v, error=f'{type(e).__name__}: {e}')); continue
                for p in ps:
                    try: out['flattened'].append(dict(venue=v, symbol=p['symbol'], result=self.close(v, p['symbol'])))
                    except Exception as e: out['flattened'].append(dict(venue=v, symbol=p['symbol'], error=f'{type(e).__name__}: {e}'))
        log.write('kill', **out); return out
