import json, time, re
from .config import path
SECRETISH = re.compile(r'(signature|apikey|api_key|secret|password|X-MBX-APIKEY)', re.I)
def write(event, **kw):
    rec = dict(t=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), event=event, **kw)
    txt = json.dumps(rec, default=str)
    if SECRETISH.search(txt): txt = json.dumps(dict(t=rec['t'], event=event, note='redacted: a secret-like field was present'))
    with open(path('orders.jsonl'), 'a', encoding='utf-8') as f: f.write(txt + '\n')
    return rec
def tail(n=20):
    try: return [json.loads(l) for l in open(path('orders.jsonl'), encoding='utf-8').read().splitlines()[-n:]]
    except FileNotFoundError: return []
