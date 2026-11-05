import asyncio, httpx, re, json, sys, hashlib
sys.path.insert(0, '/home/claude/omega/recorder')
from omega_recorder.archive import list_all
L = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; root = "data/futures/um/monthly/klines/"
async def go():
    async with httpx.AsyncClient(timeout=60) as c:
        pref, _ = await list_all(c, L, root)
        allf = sorted(p[len(root):].strip('/') for p in pref)
        syms = [s for s in allf if re.fullmatch(r'[A-Z0-9]+USDT', s)]
        # daily folder list too: coins that started trading after the last monthly file exist only there
        dpref, _ = await list_all(c, L, "data/futures/um/daily/klines/")
        dsyms = sorted(p[len("data/futures/um/daily/klines/"):].strip('/') for p in dpref)
        dsyms = [s for s in dsyms if re.fullmatch(r'[A-Z0-9]+USDT', s)]
        u = sorted(set(syms) | set(dsyms))
        json.dump(dict(monthly_folders=len(allf), monthly_usdt=syms, daily_usdt=dsyms, universe=u), open('symbols.json', 'w'))
        print(len(allf), 'monthly folders;', len(syms), 'USDT perps monthly;', len(dsyms), 'daily;', len(u), 'union')
        print('md5 of sorted universe:', hashlib.md5('\n'.join(u).encode()).hexdigest())
asyncio.run(go())
