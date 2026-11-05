"""Binance USDT-M futures over its REST API: signed requests (HMAC-SHA256), exchange rounding, bracket orders. Testnet by default."""
import hmac, hashlib, time, math, uuid, datetime as dt, urllib.parse
import httpx
from . import secrets
class BinanceError(Exception): pass
class BinanceTransportError(BinanceError): pass                            # network failure: the request's outcome is unknown
class BinanceProtectError(BinanceError):
    """The entry went out but its stop could not be placed. The Bridge has tried to undo the entry; detail says what happened."""
    def __init__(self, msg, detail): super().__init__(msg); self.detail = detail
def _dec(step):
    s = ('%.12f' % float(step)).rstrip('0'); return len(s.split('.')[1]) if '.' in s else 0
def _floor(x, step): return math.floor(x/step + 1e-9)*step
class Binance:
    def __init__(self, cfg, client=None, key=None, secret=None):
        self.cfg = cfg; self.live = bool(cfg.get('live')); self.base = (cfg['live_url'] if self.live else cfg['testnet_url']).rstrip('/')
        self.c = client or httpx.Client(timeout=15); self._key, self._secret = key, secret; self._info = None; self._offset = 0; self._restrictions = None
    def _creds(self):
        k = self._key or secrets.get('binance_key'); s = self._secret or secrets.get('binance_secret')
        if not (k and s): raise BinanceError('no Binance key in the Windows vault: run  python -m omega_bridge setkey binance')
        return k, s
    def _req(self, method, path, params=None, signed=False, _retry=True, base=None):
        p = dict(params or {}); headers = {}
        if signed:
            k, s = self._creds(); p['timestamp'] = int(time.time()*1000) + self._offset; p['recvWindow'] = int(self.cfg.get('recv_window', 5000))
            q = urllib.parse.urlencode(p); p['signature'] = hmac.new(s.encode(), q.encode(), hashlib.sha256).hexdigest(); headers['X-MBX-APIKEY'] = k
        try: r = self.c.request(method, (base or self.base) + path, params=p, headers=headers)
        except httpx.HTTPError as e:                                           # never let the URL (signed query) reach a message or log
            raise BinanceTransportError(f'Binance unreachable on {path}: {type(e).__name__}') from None
        if r.status_code >= 400:
            try: j = r.json(); code, msg = j.get('code'), j.get('msg')
            except Exception: code, msg = None, r.text[:200]
            if signed and _retry and code == -1021:                            # clock drift: resync with the server once and retry (the request was rejected, so a retry cannot double it)
                self.sync_time(); return self._req(method, path, params, signed, _retry=False, base=base)
            raise BinanceError(f'Binance {r.status_code} on {path}: {code}: {msg}')
        return r.json()
    def sync_time(self):
        t = self._req('GET', '/fapi/v1/time')['serverTime']; self._offset = int(t) - int(time.time()*1000); return self._offset
    # ── public ──
    def info(self, symbol):
        if self._info is None: self._info = {s['symbol']: s for s in self._req('GET', '/fapi/v1/exchangeInfo')['symbols']}
        s = self._info.get(symbol)
        if not s: raise BinanceError(f'{symbol} is not a Binance USDT-M futures symbol')
        f = {x['filterType']: x for x in s['filters']}
        return dict(step=float(f['LOT_SIZE']['stepSize']), minQty=float(f['LOT_SIZE']['minQty']), mstep=float(f.get('MARKET_LOT_SIZE', f['LOT_SIZE'])['stepSize']),
                    tick=float(f['PRICE_FILTER']['tickSize']), minNotional=float(f.get('MIN_NOTIONAL', {}).get('notional', 5)), status=s.get('status'))
    def price(self, symbol): return float(self._req('GET', '/fapi/v1/ticker/price', {'symbol': symbol})['price'])
    # ── account ──
    def balance(self):
        b = [x for x in self._req('GET', '/fapi/v2/balance', signed=True) if x['asset'] == 'USDT']
        return float(b[0]['balance']) if b else 0.0
    def positions(self):
        return [dict(symbol=p['symbol'], qty=float(p['positionAmt']), entry=float(p['entryPrice']), pnl=float(p['unRealizedProfit'])) for p in self._req('GET', '/fapi/v2/positionRisk', signed=True) if float(p['positionAmt']) != 0]
    def open_orders(self, symbol=None): return self._req('GET', '/fapi/v1/openOrders', {'symbol': symbol} if symbol else {}, signed=True)
    def day_pnl(self):
        t0 = int(dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()*1000)
        inc = self._req('GET', '/fapi/v1/income', {'startTime': t0, 'limit': 1000}, signed=True)
        realized = sum(float(x['income']) for x in inc if x['incomeType'] in ('REALIZED_PNL', 'COMMISSION', 'FUNDING_FEE'))
        return realized + sum(p['pnl'] for p in self.positions())
    # ── orders ──
    def prepare(self, symbol, side, size_usd=None, qty=None, type_='MARKET', price=None, stop=None, target=None):
        i = self.info(symbol); px = float(price) if price else self.price(symbol); step = i['mstep'] if type_ == 'MARKET' else i['step']
        q = _floor(qty if qty else (size_usd or 0)/px, step)
        if q < i['minQty'] or q*px < i['minNotional'] - 1e-9: raise BinanceError(f'{symbol}: {q} is below Binance’s minimum (qty {i["minQty"]}, {i["minNotional"]} USDT)')
        rnd = lambda v: None if v is None else round(_floor(float(v), i['tick']) if side == 'BUY' else math.ceil(float(v)/i['tick'] - 1e-9)*i['tick'], _dec(i['tick']))
        o = dict(symbol=symbol, side=side, type=type_, quantity=round(q, _dec(step)), price=rnd(price) if type_ == 'LIMIT' else None, stop=None if stop is None else round(round(float(stop)/i['tick'])*i['tick'], _dec(i['tick'])),
                 target=None if target is None else round(round(float(target)/i['tick'])*i['tick'], _dec(i['tick'])), ref=px)
        o['notional_usd'] = o['quantity']*px; o['risk_usd'] = abs(px - o['stop'])*o['quantity'] if o['stop'] else None; o['has_stop'] = o['stop'] is not None
        if o['stop'] and ((side == 'BUY' and o['stop'] >= px) or (side == 'SELL' and o['stop'] <= px)): raise BinanceError('the stop is on the wrong side of the price')
        return o
    def pending_entries(self):
        """Symbols with an open entry order (not a stop/target): a resting LIMIT can fill later, so it counts like a position."""
        return sorted({x['symbol'] for x in self.open_orders() if str(x.get('reduceOnly')).lower() != 'true' and str(x.get('closePosition')).lower() != 'true'})
    def key_restrictions(self):
        """The API key's own permissions (Binance spot API). Live trading is refused when withdrawals are enabled or this cannot be read."""
        if self._restrictions is None:
            self._restrictions = self._req('GET', '/sapi/v1/account/apiRestrictions', signed=True, base=self.cfg.get('spot_url', 'https://api.binance.com').rstrip('/'))
        return self._restrictions
    def _conditional(self, symbol, side, type_, trigger):
        p = dict(symbol=symbol, side=side, type=type_, stopPrice=trigger, closePosition='true', workingType='MARK_PRICE')
        try: return self._req('POST', '/fapi/v1/order', p, signed=True)
        except BinanceError as e:
            if '-4120' not in str(e): raise                                    # -4120: conditional orders moved to the Algo Order API (Binance, Dec 2025)
            a = dict(algoType='CONDITIONAL', symbol=symbol, side=side, type=type_, triggerPrice=trigger, closePosition='true', workingType='MARK_PRICE')
            return dict(self._req('POST', '/fapi/v1/algoOrder', a, signed=True), via='algoOrder')
    def _find(self, symbol, cid):
        try: return self._req('GET', '/fapi/v1/order', {'symbol': symbol, 'origClientOrderId': cid}, signed=True)
        except BinanceTransportError: raise
        except BinanceError: return None                                       # -2013: no such order, so it was never placed
    def _unwind(self, symbol, cid):
        out = {}
        try: out['cancel_entry'] = self._req('DELETE', '/fapi/v1/order', {'symbol': symbol, 'origClientOrderId': cid}, signed=True)
        except BinanceError as e: out['cancel_entry'] = f'not cancelled: {e}'        # filled already (or gone): close below
        try: out['close'] = self.close(symbol)
        except BinanceError as e: out['close'] = f'FAILED: {e}'
        out['unprotected'] = isinstance(out['close'], str); return out
    def send(self, o):
        try: self._req('POST', '/fapi/v1/marginType', {'symbol': o['symbol'], 'marginType': self.cfg.get('margin', 'ISOLATED')}, signed=True)
        except BinanceError as e:
            if '-4046' not in str(e): raise                                     # -4046: already isolated
        self._req('POST', '/fapi/v1/leverage', {'symbol': o['symbol'], 'leverage': int(self.cfg.get('leverage', 1))}, signed=True)
        cid = 'omega-' + uuid.uuid4().hex[:24]                                  # lets a timed-out entry be looked up instead of re-sent
        p = dict(symbol=o['symbol'], side=o['side'], type=o['type'], quantity=o['quantity'], newOrderRespType='RESULT', newClientOrderId=cid)
        if o['type'] == 'LIMIT': p.update(price=o['price'], timeInForce='GTC')
        try: main = self._req('POST', '/fapi/v1/order', p, signed=True)
        except BinanceTransportError:
            try: main = self._find(o['symbol'], cid)
            except BinanceTransportError: raise BinanceError(f'network failure while sending {o["symbol"]}: the entry may or may not exist (client id {cid}). Check positions in the Binance app now.')
            if main is None: raise BinanceError('network failure: the entry was not placed (checked)')
        out = dict(entry=main, client_order_id=cid)
        exit_side = 'SELL' if o['side'] == 'BUY' else 'BUY'
        if o['stop']:
            try: out['stop'] = self._conditional(o['symbol'], exit_side, 'STOP_MARKET', o['stop'])
            except BinanceError as e:                                           # never leave an entry without its stop
                out['stop_error'] = str(e); out['unwind'] = self._unwind(o['symbol'], cid)
                msg = 'the stop could not be placed, so the entry was undone' if not out['unwind']['unprotected'] else 'THE STOP COULD NOT BE PLACED AND THE POSITION COULD NOT BE CLOSED: close it in the Binance app now'
                raise BinanceProtectError(f'{o["symbol"]}: {msg} ({e})', out)
        if o['target']:
            try: out['target'] = self._conditional(o['symbol'], exit_side, 'TAKE_PROFIT_MARKET', o['target'])
            except BinanceError as e: out['target_error'] = str(e)              # the stop protects the position; the target is optional
        return out
    def close(self, symbol):
        pos = [p for p in self.positions() if p['symbol'] == symbol]
        if not pos: return dict(closed=False, note='no position')
        q = abs(pos[0]['qty']); side = 'SELL' if pos[0]['qty'] > 0 else 'BUY'
        r = self._req('POST', '/fapi/v1/order', dict(symbol=symbol, side=side, type='MARKET', quantity=q, reduceOnly='true'), signed=True)
        self._req('DELETE', '/fapi/v1/allOpenOrders', {'symbol': symbol}, signed=True); return dict(closed=True, order=r)
    def cancel(self, symbol, order_id): return self._req('DELETE', '/fapi/v1/order', {'symbol': symbol, 'orderId': order_id}, signed=True)
