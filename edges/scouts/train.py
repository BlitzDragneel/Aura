"""Train the live scouts on all available history (default: the 30 TOP coins, hourly) and save them.
Writes edges/scouts/models/{up_move,down_move,turn_up,turn_down}.txt + meta.json (feature list, top-2% thresholds).
Usage: python -m edges.scouts.train [data_dir]
"""
import json, os, sys
import numpy as np, pandas as pd
from edges.lib import bt
from edges.data.fetch import TOP
from edges.scouts.model import features, labels, fit, H

HERE = os.environ.get("SCOUT_MODELS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def main():
    os.makedirs(HERE, exist_ok=True)
    btc = bt.load("BTCUSDT")
    rows = []
    for s in TOP:
        try:
            d = bt.load(s)
        except FileNotFoundError:
            continue
        X = features(d, btc).join(labels(d))
        rows.append(X.iloc[::3])
    D = pd.concat(rows)
    lab = ("fwd", "sig24", "up_move", "down_move", "turn_up", "turn_down")
    fcols = [c for c in D.columns if c not in lab]
    meta = dict(features=fcols, horizon_h=H, trained_to=str(D.index.max()), coins=TOP, thresholds={}, base_rates={})
    for t in ("up_move", "down_move", "turn_up", "turn_down"):
        tr = D.dropna(subset=[t])
        m = fit(tr[fcols], tr[t])
        m.booster_.save_model(os.path.join(HERE, f"{t}.txt"))
        p = m.predict_proba(tr[fcols])[:, 1]
        meta["thresholds"][t] = float(np.quantile(p, 0.98))
        meta["base_rates"][t] = float(tr[t].mean())
        print(t, len(tr), meta["thresholds"][t], flush=True)
    json.dump(meta, open(os.path.join(HERE, "meta.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
