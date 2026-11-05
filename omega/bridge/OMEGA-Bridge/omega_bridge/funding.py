"""Funding monitor (E34): shows what a delta-neutral harvest would collect now and the warning signs. PLACES NOTHING.
E34 (Nov 2026) failed as a strategy: steady +1–3% a month when funding was high, then one coin's funding flipped (DEXE, June
2026: −20.8% in a day, −64.6% in a month) and erased years of gains. So this is information, not a bot."""
import httpx
def snapshot(top=10, client=None, url='https://fapi.binance.com'):
    c = client or httpx.Client(timeout=15)
    p = c.get(url.rstrip('/') + '/fapi/v1/premiumIndex').json()
    rows = []
    for x in p:
        if not x['symbol'].endswith('USDT'): continue
        r = float(x.get('lastFundingRate') or 0); rows.append(dict(symbol=x['symbol'], rate_8h_pct=round(r*100, 4), per_year_pct=round(r*3*365*100, 1), mark=float(x['markPrice'])))
    rows.sort(key=lambda z: -z['per_year_pct']); hi = rows[:top]; lo = sorted(rows, key=lambda z: z['per_year_pct'])[:5]
    warn = []
    for z in hi:
        if z['per_year_pct'] > 200: warn.append(f"{z['symbol']}: funding {z['per_year_pct']}%/yr is extreme — that is a crowded squeeze, the kind that flips")
    for z in lo:
        if z['per_year_pct'] < -100: warn.append(f"{z['symbol']}: funding {z['per_year_pct']}%/yr — shorts are paying heavily right now (what sank E34)")
    return dict(top_positive=hi, most_negative=lo, warnings=warn,
                note='A harvest = spot long + perp short of equal size, collecting positive funding. E34 FAILED as a strategy (2025–26: −17%/yr, one flip cost −64.6% in a month). Shown for information; nothing is placed.')
