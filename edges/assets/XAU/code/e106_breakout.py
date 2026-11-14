"""E106 session range breakouts + vol gate + maker-only fade (plan edges/plans/E106_session_breakout_xau.md)."""
import numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X
P = "E106"

def day_frames(px):
    lt = px.index.tz_convert(X.NY)
    return px, lt

def simulate(px, per, rng_name, mode, exit_, gate, maker=False, mult=1.0, levels=None):
    o, h, l, c = (px[k].values for k in "ohlc"); idx = px.index
    dates = pd.date_range(per[0], per[1], freq="D")[:-1]
    daily = px.c.resample("1D").last(); tr = (px.h.resample("1D").max() - px.l.resample("1D").min())
    atr = tr.rolling(14).mean(); gate_ok = (atr > atr.rolling(60).median()).shift(1)
    rows = []
    for d in dates:
        if d.weekday() > 4: continue
        if rng_name == "R1":
            ra = pd.Timestamp(f"{d.date()} 00:00", tz="UTC"); rb = pd.Timestamp(f"{d.date()} 08:00", tz=X.LDN).tz_convert("UTC")
            te = pd.Timestamp(f"{d.date()} 12:00", tz=X.LDN).tz_convert("UTC")
        else:
            ra = pd.Timestamp(f"{d.date()} 08:00", tz=X.NY).tz_convert("UTC"); rb = ra + pd.Timedelta("1h")
            te = pd.Timestamp(f"{d.date()} 12:00", tz=X.NY).tz_convert("UTC")
        if exit_ == "EXIT2": te = pd.Timestamp(f"{d.date()} 17:00", tz=X.NY).tz_convert("UTC")
        tw = pd.Timestamp(f"{d.date()} 12:00", tz=X.LDN if rng_name == "R1" else X.NY).tz_convert("UTC")   # signal window end
        i0, i1, i2, i3 = idx.searchsorted([ra, rb, tw, te])
        if i1 - i0 < 3 or i3 - i1 < 4: continue
        if gate and not bool(gate_ok.get(d.tz_localize("UTC") if gate_ok.index.tz else d, False) or False): continue
        hi, lo = h[i0:i1].max(), l[i0:i1].min()
        if levels is not None:
            fr = levels.get(d)
            if fr is None: continue
            hi, lo = c[i1 - 1] * fr[0], c[i1 - 1] * fr[1]
        R = hi - lo
        if R <= 0: continue
        ent = None
        if maker:
            for j in range(i1, i2):
                if h[j] > hi + 0.1 * R: ent, side, px_e = j, -1, hi + 0.1 * R; break
                if l[j] < lo - 0.1 * R: ent, side, px_e = j, 1, lo - 0.1 * R; break
            if ent is None: continue
            k0 = ent  # the fill bar itself counts for the stop afterwards (conservative: from next bar)
            k0 = ent + 1
        else:
            for j in range(i1, i2 - 1):
                if c[j] > hi or c[j] < lo:
                    up = c[j] > hi; side = (1 if up else -1) * (1 if mode == "FOLLOW" else -1); ent = j + 1; break
            if ent is None: continue
            px_e = o[ent]; k0 = ent
        if mode == "FOLLOW": stop = lo if side > 0 else hi
        else: stop = (lo - R) if side > 0 else (hi + R)
        xp, mae = None, 0.0
        for k in range(k0, i3):
            if side > 0:
                mae = min(mae, l[k] / px_e - 1)
                if l[k] <= stop: xp = min(o[k], stop); break
            else:
                mae = min(mae, px_e / h[k] - 1)
                if h[k] >= stop: xp = max(o[k], stop); break
        if xp is None: xp = c[i3 - 1]
        gross = xp / px_e - 1 if side > 0 else px_e / xp - 1
        rows.append((idx[ent], gross, mae, idx[i3 - 1]))
    t = pd.DataFrame(rows, columns=["time", "gross", "mae", "exit_time"])
    t["net"] = X.net_of(t.gross, 0, mult); t["sym"] = "XAU"
    t["net_perp_maker"] = t.gross - (0.0002 + 0.0007) if maker else t.gross - 0.0014
    return t

def specs():
    out = {}
    for r in ("R1", "R2"):
        for m in ("FOLLOW", "FADE"):
            for e in ("EXIT1", "EXIT2"):
                for g in (0, 1):
                    out[f"{r}_{m}_{e}_G{g}"] = dict(rng_name=r, mode=m, exit_=e, gate=g)
        for e in ("EXIT1", "EXIT2"):
            out[f"{r}_MAKERFADE_{e}"] = dict(rng_name=r, mode="FADE", exit_=e, gate=0, maker=True)
    return out

def main():
    px = X.bars("PAXG_15m"); S = specs()
    out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    for k, sp in S.items():
        t = simulate(px, X.PER_PAXG["discovery"], **sp); s = X.summ(t, k); s["perp_cost_mean_bp"] = round(t.net_perp_maker.mean() * 1e4, 2)
        s["gross_bp"] = round(t.gross.mean() * 1e4, 2); out["discovery"][k] = s; X.log(P, k, "discovery", s)
        print(k, s["n"], s["gross_bp"], s["mean_bp"], s["t_week"], s["years"], flush=True)
    elig = sorted([k for k, s in out["discovery"].items() if X.eligible(s)], key=lambda k: -out["discovery"][k]["t_week"])[:2]
    out["eligible_promoted"] = elig
    if not elig:
        out["luck"] = "not run: nothing eligible (cannot change a FAIL)"; out["verdict"] = "FAIL (nothing eligible)"
    else:
        raise NotImplementedError("luck null (range levels from a random other day) to be run before validation")
        out["luck"] = "see code"; out["verdict"] = "eligible found: luck/validation needed"
    X.dump(P, out); print(out["verdict"], elig)

if __name__ == "__main__":
    main()
