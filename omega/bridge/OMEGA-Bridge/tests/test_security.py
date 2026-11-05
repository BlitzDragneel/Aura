"""Security review (Nov 2026): every path to an order must pass preview -> confirm -> guard (-> a person's Yes when LIVE),
a stop that fails must never leave a naked position, and the kill switch must survive one venue failing."""
import json, math, time, types, urllib.parse, asyncio, httpx, respx, pytest
from conftest import FakeMT5
from test_bridge import mock_binance, bridge, go, BASE, KEY, SECRET
from omega_bridge.config import load
from omega_bridge.binance import Binance, BinanceError
from omega_bridge.mt5 import MT5
from omega_bridge.core import Bridge
from omega_bridge import guard, log, core, human
LIVE = 'https://fapi.binance.com'; SPOT = 'https://api.binance.com'
def filled_after_entry(sent):
    """positionRisk is empty until the entry order has gone out, then shows the filled position."""
    pos = [{'symbol': 'BTCUSDT', 'positionAmt': '0.1', 'entryPrice': '100', 'unRealizedProfit': '0'}]
    respx.get(f'{BASE}/fapi/v2/positionRisk').mock(side_effect=lambda req: httpx.Response(200, json=pos if sent else []))
def q(req): return dict(urllib.parse.parse_qsl(req.url.query.decode()))
@respx.mock
def test_place_without_a_matching_preview_is_refused():
    sent = mock_binance(); B = bridge()
    r = B.place('binance', 'BTCUSDT', 'BUY', confirm=True, size_usd=10, stop=95)            # straight to place, no preview
    assert not r['sent'] and sent == [] and 'no matching preview' in r['blocked_because'][0]
    p = B.preview('binance', 'BTCUSDT', 'BUY', size_usd=6, stop=95)                           # preview a small order ...
    r = B.place('binance', 'BTCUSDT', 'BUY', confirm=True, preview_id=p['preview_id'], size_usd=10, stop=95)   # ... place a bigger one
    assert not r['sent'] and sent == []
    p = B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert B.place('binance', 'BTCUSDT', 'BUY', confirm=True, preview_id=p['preview_id'], size_usd=10, stop=95)['sent']
    n = len(sent); r = B.place('binance', 'BTCUSDT', 'BUY', confirm=True, preview_id=p['preview_id'], size_usd=10, stop=95)
    assert not r['sent'] and len(sent) == n                                                   # single use
    assert log.tail(1)[0]['event'] == 'refused'
@respx.mock
def test_preview_expires(monkeypatch):
    sent = mock_binance(); B = bridge(); p = B.preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    t = time.time(); monkeypatch.setattr(core.time, 'time', lambda: t + core.PREVIEW_TTL_S + 1)
    assert not B.place('binance', 'BTCUSDT', 'BUY', confirm=True, preview_id=p['preview_id'], size_usd=10, stop=95)['sent'] and sent == []
@respx.mock
@pytest.mark.parametrize('kw', [dict(size_usd=float('nan'), stop=95), dict(size_usd=float('inf'), stop=95), dict(size_usd=-10, stop=95),
                                dict(size_usd=10, stop=float('nan')), dict(size_usd=10, stop=-5), dict(size_usd=10, stop=95, side='LONG'),
                                dict(size_usd=10, stop=95, type_='STOP'), dict(size_usd=10, stop=95, type_='LIMIT'), dict(size_usd='10', stop=95)])
def test_bad_numbers_sides_and_types_are_refused(kw):
    sent = mock_binance(); B = bridge(); side = kw.pop('side', 'BUY')
    with pytest.raises((ValueError, BinanceError)): B.preview('binance', 'BTCUSDT', side, **kw)
    assert sent == []
@respx.mock
def test_adding_to_an_open_symbol_and_resting_entries_count():
    mock_binance(positions=[{'symbol': 'BTCUSDT', 'positionAmt': '0.05', 'entryPrice': '100', 'unRealizedProfit': '0'}])
    p = bridge().preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not p['allowed'] and 'already has a position' in ' '.join(p['blocked_because'])
    respx.reset(); mock_binance(open_orders=[{'symbol': s, 'orderId': i, 'reduceOnly': False, 'closePosition': False} for i, s in enumerate(('A', 'B', 'C'))])
    p = bridge().preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not p['allowed'] and 'positions already open' in ' '.join(p['blocked_because'])
@respx.mock
def test_a_stop_that_fails_undoes_the_entry():
    sent = []
    mock_binance(orders=sent)
    def order(req):
        sent.append(req); d = q(req)
        if d['type'] == 'STOP_MARKET': return httpx.Response(400, json={'code': -2021, 'msg': 'Order would immediately trigger.'})
        return httpx.Response(200, json={'orderId': len(sent), 'status': 'FILLED'})
    respx.post(f'{BASE}/fapi/v1/order').mock(side_effect=order)
    respx.delete(f'{BASE}/fapi/v1/order').mock(return_value=httpx.Response(400, json={'code': -2011, 'msg': 'Unknown order'}))
    filled_after_entry(sent)
    r = go(bridge(), 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not r['sent'] and 'entry was undone' in r['error']
    close = q(sent[-1]); assert close['reduceOnly'] == 'true' and close['side'] == 'SELL' and close['type'] == 'MARKET'
    assert not guard.killed() and log.tail(1)[0]['event'] == 'error'
@respx.mock
def test_a_stop_that_fails_and_cannot_be_undone_turns_the_kill_switch_on():
    sent = []; mock_binance(orders=sent)
    def order(req):
        sent.append(req); d = q(req)
        if d['type'] == 'STOP_MARKET' or d.get('reduceOnly') == 'true': return httpx.Response(400, json={'code': -1001, 'msg': 'Internal error'})
        return httpx.Response(200, json={'orderId': 1, 'status': 'FILLED'})
    respx.post(f'{BASE}/fapi/v1/order').mock(side_effect=order)
    respx.delete(f'{BASE}/fapi/v1/order').mock(return_value=httpx.Response(400, json={'code': -2011, 'msg': 'Unknown order'}))
    filled_after_entry(sent)
    r = go(bridge(), 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not r['sent'] and 'COULD NOT BE CLOSED' in r['error'] and guard.killed()
    guard.set_kill(False)
@respx.mock
def test_conditional_orders_fall_back_to_the_algo_api():
    sent = []; mock_binance(orders=sent)
    def order(req):
        sent.append(req)
        if q(req)['type'] in ('STOP_MARKET', 'TAKE_PROFIT_MARKET'): return httpx.Response(400, json={'code': -4120, 'msg': 'Order type not supported for this endpoint. Please use the Algo Order API endpoints instead.'})
        return httpx.Response(200, json={'orderId': 1, 'status': 'FILLED'})
    respx.post(f'{BASE}/fapi/v1/order').mock(side_effect=order)
    algo = respx.post(f'{BASE}/fapi/v1/algoOrder').mock(return_value=httpx.Response(200, json={'algoId': 9}))
    r = go(bridge(), 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95, target=110)
    assert r['sent'] and r['result']['stop']['via'] == 'algoOrder' and algo.call_count == 2
    a = q(algo.calls[0].request); assert a['algoType'] == 'CONDITIONAL' and a['triggerPrice'] == '95.0' and a['closePosition'] == 'true'
def live_bridge(dialog, restrictions):
    cfg = load(); cfg['binance']['live'] = True
    return Bridge(cfg, binance=Binance(cfg['binance'], key=KEY, secret=SECRET), mt5=MT5(cfg['mt5'], mod=FakeMT5()), confirm_dialog=dialog)
def mock_live(restrictions):
    respx.get(f'{LIVE}/fapi/v1/exchangeInfo').mock(return_value=httpx.Response(200, json={'symbols': [{'symbol': 'BTCUSDT', 'status': 'TRADING', 'filters': [
        {'filterType': 'PRICE_FILTER', 'tickSize': '0.10'}, {'filterType': 'LOT_SIZE', 'stepSize': '0.001', 'minQty': '0.001'}, {'filterType': 'MIN_NOTIONAL', 'notional': '5'}]}]}))
    respx.get(f'{LIVE}/fapi/v1/ticker/price').mock(return_value=httpx.Response(200, json={'price': '100.00'}))
    for path, j in (('/fapi/v2/positionRisk', []), ('/fapi/v1/income', []), ('/fapi/v1/openOrders', [])): respx.get(LIVE + path).mock(return_value=httpx.Response(200, json=j))
    respx.post(f'{LIVE}/fapi/v1/marginType').mock(return_value=httpx.Response(200, json={})); respx.post(f'{LIVE}/fapi/v1/leverage').mock(return_value=httpx.Response(200, json={}))
    if isinstance(restrictions, dict): respx.get(f'{SPOT}/sapi/v1/account/apiRestrictions').mock(return_value=httpx.Response(200, json=restrictions))
    else: respx.get(f'{SPOT}/sapi/v1/account/apiRestrictions').mock(return_value=httpx.Response(401, json={'code': -2015, 'msg': 'Invalid API-key'}))
    return respx.post(f'{LIVE}/fapi/v1/order').mock(return_value=httpx.Response(200, json={'orderId': 1}))
@respx.mock
@pytest.mark.parametrize('restr,why', [({'enableWithdrawals': True, 'ipRestrict': True}, 'WITHDRAW'), (None, 'could not be checked'), ({'enableWithdrawals': False, 'ipRestrict': False}, 'not restricted to your IP')])
def test_live_binance_key_must_not_withdraw_and_must_be_ip_restricted(restr, why):
    mock_live(restr); p = live_bridge(lambda t, x: True, restr).preview('binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not p['allowed'] and why in ' '.join(p['blocked_because'])
@respx.mock
def test_live_orders_need_a_yes_on_the_pc():
    order = mock_live({'enableWithdrawals': False, 'ipRestrict': True}); asked = []
    B = live_bridge(lambda t, x: asked.append(x) or False, None)
    r = go(B, 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)
    assert not r['sent'] and order.call_count == 0 and 'LIVE' in asked[0] and 'did not confirm' in r['blocked_because'][0]
    B._dialog = lambda t, x: True
    assert go(B, 'binance', 'BTCUSDT', 'BUY', size_usd=10, stop=95)['sent'] and order.call_count == 2
def test_dialog_is_no_off_windows_and_late_answers_are_refused(monkeypatch):
    monkeypatch.setattr(human.sys, 'platform', 'linux'); assert human.confirm('t', 'x') is False
    t = [0.0]; monkeypatch.setattr(human.time, 'monotonic', lambda: t[0])
    def slow(a, b): t[0] += human.MAX_WAIT_S + 5; return True
    assert human.confirm('t', 'x', dialog=slow) is False and human.confirm('t', 'x', dialog=lambda a, b: True) is True
def test_connector_cannot_lift_the_kill_switch():
    from omega_bridge import mcp_server
    guard.set_kill(True)
    out = json.loads(mcp_server.kill_switch(on=False)); assert guard.killed() and 'only be lifted on the PC' in out['refused']
    guard.set_kill(False)
@respx.mock
def test_network_errors_never_leak_the_signed_url_and_kill_survives_them():
    respx.get(url__regex=r'.*').mock(side_effect=httpx.ConnectError('boom https://x/?signature=abc'))
    respx.post(url__regex=r'.*').mock(side_effect=httpx.ConnectError('boom'))
    f = FakeMT5(); f.pos = [types.SimpleNamespace(ticket=9, symbol='XAUUSDm', type=0, volume=0.01, price_open=2000, sl=1990, tp=0, profit=-1)]
    f.pending = [types.SimpleNamespace(ticket=11, symbol='XAUUSDm')]
    out = bridge(mt5=f).kill(True, flatten=True)
    assert guard.killed() and any('error' in x and x['venue'] == 'binance' for x in out['flattened'])
    assert 'signature' not in json.dumps(out) and f.sent[0]['order'] == 11 and f.sent[-1]['position'] == 9   # MT5: pending cancelled, then closed
    guard.set_kill(False)
@respx.mock
def test_clock_drift_resyncs_and_retries_once():
    calls = []
    def bal(req):
        calls.append(int(q(req)['timestamp']))
        return httpx.Response(400, json={'code': -1021, 'msg': 'Timestamp outside recvWindow'}) if len(calls) == 1 else httpx.Response(200, json=[{'asset': 'USDT', 'balance': '7'}])
    respx.get(f'{BASE}/fapi/v2/balance').mock(side_effect=bal)
    respx.get(f'{BASE}/fapi/v1/time').mock(return_value=httpx.Response(200, json={'serverTime': int(time.time() * 1000) + 60_000}))
    b = Binance(load()['binance'], key=KEY, secret=SECRET); assert b.balance() == 7.0 and calls[1] - calls[0] > 50_000
def test_config_refuses_nested_secrets(home):
    json.dump({'guard': {'extra': {'token': 'x'}}}, open(home / 'config.json', 'w'))
    with pytest.raises(ValueError, match='Windows vault'): load()
def test_mt5_lot_cap_and_failed_closes_are_reported():
    f = FakeMT5(); B = bridge(mt5=f, max_risk_usd=1000)
    p = B.preview('mt5', 'XAUUSD', 'BUY', volume=0.5, stop=1990); assert 'max_mt5_lots' in ' '.join(p['blocked_because'])
    f.pos = [types.SimpleNamespace(ticket=9, symbol='XAUUSDm', type=0, volume=0.01, price_open=2000, sl=1990, tp=0, profit=-1)]
    f.order_send = lambda req: types.SimpleNamespace(retcode=10019, comment='No money')
    r = B.close('mt5', 'XAUUSD'); assert r['closed'] is False and r['results'][0]['ok'] is False
