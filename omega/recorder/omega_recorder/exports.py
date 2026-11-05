"""Exports in the format OMEGA's research loader already reads (load.py dec_market): {tf, markets:[{sym, dp, t, o, h, l, c, v}]}.
t = delta-coded candle numbers (tf-minute units since 1970), c = delta-coded integer closes at 10^-dp, o/h/l = integer offsets."""
import gzip, json, math

def choose_dp(closes):
    p = min((x for x in closes if x > 0), default=1.0)
    return max(0, min(10, 6 - int(math.floor(math.log10(p)))))   # ≥ 6 significant digits on the cheapest close

def encode_market(sym, rows, tf=60, src="recorder"):
    """rows: dicts with t (ms), o, h, l, c, v; sorted by t."""
    dp = choose_dp([r["c"] for r in rows]); S = 10 ** dp
    T, C, O, H, L, V = [], [], [], [], [], []
    pt = pc = 0
    for r in rows:
        tn = r["t"] // (tf * 60_000); ci = round(r["c"] * S); oi = round(r["o"] * S)
        hi = round(r["h"] * S); li = round(r["l"] * S)
        T.append(tn - pt); C.append(ci - pc); pt, pc = tn, ci
        O.append(oi - ci); H.append(max(0, hi - max(oi, ci))); L.append(max(0, min(oi, ci) - li)); V.append(r["v"])
    return dict(sym=sym, src=src, dp=dp, t=T, c=C, o=O, h=H, l=L, v=V)

def history_gz(markets, tf=60, meta=None):
    doc = dict(tf=tf, kind="omega_history", made_by="omega-recorder", **(meta or {}), markets=markets)
    return gzip.compress(json.dumps(doc, separators=(",", ":")).encode())
