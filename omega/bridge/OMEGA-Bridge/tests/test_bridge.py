import json, hmac, hashlib, urllib.parse, types, asyncio, httpx, respx, pytest
from conftest import FakeMT5
from omega_bridge.config import load
from omega_bridge.binance import Binance, BinanceError
from omega_bridge.mt5 import MT5, MT5Error
from omega_bridge.core import Bridge
from omega_bridge import guard, log
KEY, SECRET = 'test-key-123', 'test-secret-abc'
BASE = 'https://testnet.binancefuture.com'
def mock_binance(positions=(), income=(), orders=None, open_orders=()):
    respx.get(f'{BASE}/fapi/v1/exchangeInfo').mock(return_value=httpx.Response(200, json={'symbols': [{'symbol': 'BTCUSDT', 'status': 'TRADING', 'filters': [
        {'filterType': 'PRICE_FILTER', 'tickSize': '0.10'}, {'filterType': 'LOT_SIZE', 'stepSize': '0.001', 'minQty': '0.001'}, {'filterType': 'MARKET_LOT_SIZE', 'stepSize': '0.001', 'minQty': '0.001'}, {'filterType': 'MIN_NOTIONAL', 'notional': '5'}]}]}))
    respx.get(f'{BASE}/fapi/v1/ticker/price').mock(return_value=httpx.Response(200, json={'symbol': 'BTCUSDT', 'price': '100.00'}))
    respx.get(f'{BASE}/fapi/v2/balance').mock(return_value=httpx.Response(200, json=[{'asset': 'USDT', 'balance': '100'}]))
    respx.get(f'{BASE}/fapi/v2/positionRisk').mock(return_value=httpx.Response(200, json=list(positions)))
    respx.get(f'{BASE}/fapi/v1/income').mock(return_value=httpx.Response(200, json=list(income)))
    respx.post(f'{BASE}/fapi/v1/marginType').mock(return_value=httpx.Response(400, json={'code': -4046, 'msg': 'No need to change margin type.'}))
    respx.post(f'{BASE}/fapi/v1/leverage').mock(return_value=httpx.Response(200, json={'leverage': 1}))
    respx.get(f'{BASE}/fapi/v1/openOrders').mock(return_value=httpx.Response(200, json=list(open_orders)))
    sent = orders if orders is not None else []
    def order(req): sent.append(req); return httpx.Response(200, json={'orderId': len(sent), 'status': 'NEW'})
    respx.post(f'{BASE}/fapi/v1/order').mock(side_effect=order); respx.delete(f'{BASE}/fapi/v1/allOpenOrders').mock(return_value=httpx.Response(200, json={}))
    return sent
def go(B, venue, sym, side, **kw):
    p = B.preview(venue, sym, side, **kw); assert p['allowed'], p['blocked_because']
    return B.place(venue, sym, side, confirm=True, preview_id=p['preview_id'], **kw)
def bridge(mt5=None, **guard_over):
    cfg = load(); cfg['guard'].update(guard_over); return Bridge(cfg, binance=Binance(cfg['binance'], key=KEY, secret=SECRET), mt5=MT5(cfg['mt5'], mod=mt5 or FakeMT5()))
@respx.mock
def test_binance_requests_are_signed_and_the_secret_never_travels():
    sent = mock_binance(); B = bridge()
    r = go(B, 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95, target=110)
    assert r['sent'] and len(sent) == 3                                       # entry, stop, target
    for req in sent:
        q = req.url.query.decode(); params = dict(urllib.parse.parse_qsl(q)); sig = params.pop('signature')
        unsigned = q.split('&signature=')[0]
        assert sig == hmac.new(SECRET.encode(), unsigned.encode(), hashlib.sha256).hexdigest()
        assert req.headers['X-MBX-APIKEY'] == KEY and SECRET not in q
    e, s, t = [dict(urllib.parse.parse_qsl(x.url.query.decode())) for x in sent]
    assert e['type'] == 'MARKET' and e['quantity'] == '0.1' and e['side'] == 'BUY'
    assert s['type'] == 'STOP_MARKET' and s['stopPrice'] == '95.0' and s['closePosition'] == 'true' and s['side'] == 'SELL'
    assert t['type'] == 'TAKE_PROFIT_MARKET' and t['stopPrice'] == '110.0'
    assert SECRET not in open(__import__('omega_bridge.config', fromlist=['path']).path('orders.jsonl')).read()
@respx.mock
def test_preview_never_sends_and_place_needs_confirm():
    sent = mock_binance(); B = bridge()
    assert B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)['allowed'] and sent == []
    r = B.place('binance', 'BTCUSDT', 'BUY', confirm=False, size_usd=10, stop=95); assert not r['sent'] and sent == []
@respx.mock
def test_guard_refuses_and_logs_every_reason():
    mock_binance(positions=[{'symbol': s, 'positionAmt': '1', 'entryPrice': '1', 'unRealizedProfit': '-2'} for s in ('A', 'B', 'C')], income=[{'incomeType': 'REALIZED_PNL', 'income': '-1'}])
    B = bridge()
    r = B.place('binance', 'BTCUSDT', 'BUY', confirm=True, size_usd=20, stop=None)
    why = ' | '.join(r['blocked_because'])
    assert not r['sent'] and 'needs a stop' in why and 'above max_order_usd' in why and 'positions already open' in why and 'daily loss limit' in why
    assert log.tail(1)[0]['event'] == 'refused'
    guard.set_kill(True); r2 = B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95); assert 'kill switch' in ' '.join(r2['blocked_because']); guard.set_kill(False)
@respx.mock
def test_binance_rounding_minimums_and_wrong_side_stops():
    mock_binance(); B = bridge()
    with pytest.raises(BinanceError, match='minimum'): B.preview('binance', 'BTCUSDT', 'BUY', size_usd=3, stop=95)
    with pytest.raises(BinanceError, match='wrong side'): B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=105)
    o = B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, type_='LIMIT', price=98.37, stop=93.33)['order']
    assert o['quantity'] == 0.101 and o['price'] == 98.3 and o['stop'] == 93.3 and abs(o['risk_usd'] - 0.101*(98.37 - 93.3)) < 1e-9
def test_mt5_finds_exness_suffix_sizes_by_risk_and_attaches_stop_and_target():
    f = FakeMT5(); B = bridge(mt5=f, max_risk_usd=3)
    p = B.preview('mt5', 'XAUUSD', 'BUY', risk_usd=3, stop=1998.3, target=2010)
    o = p['order']; assert o['symbol'] == 'XAUUSDm' and o['volume'] == 0.01 and abs(o['risk_usd'] - 2.0) < 1e-6 and p['allowed']
    r = go(B, 'mt5', 'XAUUSD', 'BUY', risk_usd=3, stop=1998.3, target=2010)
    q = f.sent[-1]; assert r['sent'] and q['sl'] == 1998.3 and q['tp'] == 2010.0 and q['type'] == f.ORDER_TYPE_BUY and q['type_filling'] == f.ORDER_FILLING_FOK and q['magic'] == 77777
def test_mt5_refuses_below_minimum_lot_and_explains_the_real_risk():
    B = bridge()
    with pytest.raises(MT5Error, match='below the minimum 0.01'): B.preview('mt5', 'XAUUSD', 'BUY', risk_usd=1, stop=1998.3)
    p = B.preview('mt5', 'XAUUSD', 'BUY', volume=0.01, stop=1998.3); assert not p['allowed'] and 'above max_risk_usd' in ' '.join(p['blocked_because'])
def test_real_mt5_account_is_refused_unless_live_is_switched_on():
    B = bridge(mt5=FakeMT5(trade_mode=2), max_risk_usd=3)
    p = B.preview('mt5', 'XAUUSD', 'BUY', volume=0.01, stop=1998.3); assert 'LIVE account' in ' '.join(p['blocked_because'])
    B.cfg['mt5']['live'] = True; assert B.preview('mt5', 'XAUUSD', 'BUY', volume=0.01, stop=1998.3)['allowed']
def test_config_refuses_secrets(home):
    json.dump({'binance': {'api_secret': 'x'}}, open(home/'config.json', 'w'))
    with pytest.raises(ValueError, match='Windows vault'): load()
@respx.mock
def test_kill_switch_with_flatten_closes_both_venues():
    sent = mock_binance(positions=[{'symbol': 'BTCUSDT', 'positionAmt': '0.1', 'entryPrice': '100', 'unRealizedProfit': '0'}])
    f = FakeMT5(); f.pos = [types.SimpleNamespace(ticket=9, symbol='XAUUSDm', type=0, volume=0.01, price_open=2000, sl=1990, tp=0, profit=-1)]
    B = bridge(mt5=f); out = B.kill(True, flatten=True)
    assert guard.killed() and any(x['venue'] == 'binance' for x in out['flattened']) and any(x['venue'] == 'mt5' for x in out['flattened'])
    close = dict(urllib.parse.parse_qsl(sent[-1].url.query.decode())); assert close['reduceOnly'] == 'true' and close['side'] == 'SELL' and close['quantity'] == '0.1'
    assert f.sent[-1]['position'] == 9 and f.sent[-1]['type'] == f.ORDER_TYPE_SELL
    guard.set_kill(False)
def test_connector_exposes_the_tools():
    from omega_bridge import mcp_server
    names = {t.name for t in asyncio.run(mcp_server.app.list_tools())}
    assert {'status', 'price', 'positions', 'preview_order', 'place_order', 'close_position', 'kill_switch', 'order_log'} <= names
@respx.mock
def test_funding_monitor_ranks_annualizes_warns_and_places_nothing():
    from omega_bridge.funding import snapshot
    respx.get('https://fapi.binance.com/fapi/v1/premiumIndex').mock(return_value=httpx.Response(200, json=[
        {'symbol': 'AAAUSDT', 'lastFundingRate': '0.0003', 'markPrice': '1'}, {'symbol': 'BBBUSDT', 'lastFundingRate': '0.003', 'markPrice': '2'},
        {'symbol': 'CCCUSDT', 'lastFundingRate': '-0.002', 'markPrice': '3'}, {'symbol': 'BTCUSD_PERP', 'lastFundingRate': '0.01', 'markPrice': '9'}]))
    order = respx.post(url__regex=r'.*/order').mock(return_value=httpx.Response(200, json={}))
    s = snapshot(3)
    assert [x['symbol'] for x in s['top_positive']] == ['BBBUSDT', 'AAAUSDT', 'CCCUSDT'] and s['top_positive'][1]['per_year_pct'] == 32.9
    assert any('BBBUSDT' in w and 'extreme' in w for w in s['warnings']) and any('CCCUSDT' in w and 'shorts are paying' in w for w in s['warnings'])
    assert order.call_count == 0 and 'FAILED' in s['note']
def test_connector_has_the_funding_monitor():
    from omega_bridge import mcp_server
    assert 'funding_monitor' in {t.name for t in asyncio.run(mcp_server.app.list_tools())}
