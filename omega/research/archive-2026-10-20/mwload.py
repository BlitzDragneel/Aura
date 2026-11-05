import gzip, json, base64, numpy as np, pandas as pd
def load_watch(path):
    d = json.loads(gzip.open(path).read()); F, MF = d['fields'], d['mfields']; out = {'meta':d, 'coins':{}, 'market':None}
    def unpack(rows, nf):
        frames = []
        for r in rows:
            h, b = r[0], r[1]; a = np.frombuffer(base64.b64decode(b), dtype='<f4').reshape(60, nf)
            idx = pd.to_datetime(np.arange(60)*60 + h*3600, unit='s'); frames.append(pd.DataFrame(a, index=idx))
        return pd.concat(frames).sort_index() if frames else None
    for s, rows in d['coins'].items():
        df = unpack(rows, len(F))
        if df is None: continue                     # a coin with no minute rows (e.g. live streams never delivered)
        df.columns = F; out['coins'][s] = df
    m = unpack(d['market'], len(MF))
    if m is not None: m.columns = MF
    out['market'] = m; out['diag'] = d.get('diag')
    return out
