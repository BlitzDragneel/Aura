import httpx, json, os, re, sys, time, concurrent.futures as cf
import xml.etree.ElementTree as ET
L = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; A = "https://data.binance.vision/"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
U = json.load(open('symbols.json'))['universe']
c = httpx.Client(timeout=60, limits=httpx.Limits(max_connections=32))
def get(url, **p):
    for a in range(4):
        try:
            r = c.get(url, params=p or None)
            if r.status_code in (200, 404): return r
        except httpx.HTTPError: pass
        time.sleep(1 + 2 * a)
    return None
def keys(prefix):
    out, marker = [], None
    while True:
        p = dict(prefix=prefix); 
        if marker: p['marker'] = marker
        r = get(L, **p); root = ET.fromstring(r.text)
        ks = [e.findtext(f"{NS}Key") for e in root.findall(f"{NS}Contents")]; out += ks
        if (root.findtext(f"{NS}IsTruncated") or 'false') == 'true' and ks: marker = ks[-1]
        else: return out
MONTHS = [f"{y}-{m:02d}" for y in (2023, 2024, 2025, 2026) for m in range(1, 13) if "2023-10" <= f"{y}-{m:02d}" <= "2026-09"]
DAYS = [f"2026-10-{d:02d}" for d in range(1, 19)]
def one(sym):
    d = f"zips/{sym}"; os.makedirs(d, exist_ok=True); log = []
    if os.path.exists(f"{d}/.done"): return sym, 'skip'
    ks = [k for k in keys(f"data/futures/um/monthly/klines/{sym}/1h/") if k.endswith('.zip')]
    have = {re.search(r'(\d{4}-\d{2})\.zip$', k).group(1): k for k in ks}
    want = [have[m] for m in MONTHS if m in have]
    last_m = max(have) if have else None
    if last_m is None or last_m >= "2026-08":
        want += [f"data/futures/um/daily/klines/{sym}/1h/{sym}-1h-{day}.zip" for day in DAYS]
        if last_m is None or last_m < "2026-09":   # new coin: its September is only in daily files
            want += [f"data/futures/um/daily/klines/{sym}/1h/{sym}-1h-2026-09-{x:02d}.zip" for x in range(1, 31)]
            want += [f"data/futures/um/daily/klines/{sym}/1h/{sym}-1h-2026-08-{x:02d}.zip" for x in range(1, 32)] if last_m is None else []
    n = 0; miss = []
    for k in want:
        fn = f"{d}/{k.split('/')[-1]}"
        if os.path.exists(fn): n += 1; continue
        r = get(A + k)
        if r is None: miss.append(k); continue
        if r.status_code == 200: open(fn, 'wb').write(r.content); n += 1
        elif '/monthly/' in k: miss.append(k)          # listed but 404: logged (addendum A, 6)
    json.dump(dict(months_listed=sorted(have), got=n, missing=miss), open(f"{d}/.done", 'w'))
    return sym, n
if __name__ == '__main__':
    syms = U
    with cf.ThreadPoolExecutor(24) as ex:
        for i, (s, n) in enumerate(ex.map(one, syms)):
            if i % 50 == 0: print(time.strftime('%H:%M:%S'), i, s, n, flush=True)
    print('ALL DONE', flush=True)
