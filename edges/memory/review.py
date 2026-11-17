"""Candle memory self-review (daily, first run after 00:30 UTC). For each market it looks at the model's scored
predictions - its own live record plus an out-of-sample replay - and:
- measures how often it is right in each kind of situation (the 'why it was wrong' table);
- re-chooses the call threshold for the mistake model on the older half of the window and KEEPS the change only if it
  also beats the current setting on the newer half (no fitting to noise);
- blocks calls in situations where it is reliably wrong (150+ cases, accuracy clearly under 52%), unblocks them when
  they recover;
- writes config.json (read by live.py) and appends what changed and why to UPGRADES.md.
Usage: python -m edges.memory.review <state_dir> [--force]"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from edges.memory.features import RICH
from edges.memory.live import DEFAULT, OKX, SEED, YF
from edges.memory.model import META, mistake_model, p_right

CONDS = ["close vote", "unfamiliar", "against 24h move", "high volatility", "session Asia", "session London",
         "session New York", "session late", "weekend"]
THRESH = [0.50, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.60]


def flags(S, dist_p80):
    h = S.index.hour
    return pd.DataFrame({"close vote": S.margin < 0.05, "unfamiliar": S.dist >= dist_p80,
                         "against 24h move": np.sign(S.r96) != np.sign(S.p_up1h - 0.5), "high volatility": S.volp >= 2 / 3,
                         "session Asia": h < 7, "session London": (h >= 7) & (h < 13), "session New York": (h >= 13) & (h < 20),
                         "session late": h >= 20, "weekend": S.wkend > 0}, index=S.index)


def score(S, thr):
    c = S[S.p_right >= thr]
    if len(c) < 100:
        return -9, len(c), None
    acc = c.right.mean()
    return (acc - 0.5) * np.sqrt(len(c)), len(c), acc


def window(sym, root):
    """Scored predictions with an out-of-sample p_right: live ones as they were, plus a replay whose mistake model is
    trained only on what came before the last 60 days."""
    parts = []
    cf = root / f"{sym}_calls.csv"
    if cf.exists():
        C = pd.read_csv(cf, index_col=0, parse_dates=True)
        if C.index.tz is None:
            C.index = C.index.tz_localize("UTC")
        C = C.dropna(subset=["right", "p_right"])
        if len(C):
            parts.append(C.assign(src="live"))
    own = SEED / f"{sym}_history.parquet"
    if own.exists():
        H = pd.read_parquet(own).astype(float)
        cut = H.index.max() - pd.Timedelta(days=60)
        mm = mistake_model(H[H.index < cut - pd.Timedelta("5h")])
        R = H[H.index >= cut].copy()
        if mm is not None and len(R):
            R["p_right"] = p_right(mm, R)
            parts.append(R.assign(src="replay"))
    if not parts:
        return None
    W = pd.concat(parts).sort_index()
    W = W[~W.index.duplicated(keep="last")]
    return W[W.index >= W.index.max() - pd.Timedelta(days=90)]


def main(state_dir, force=False):
    root = Path(state_dir) / "memory"; root.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    cfg_f = root / "config.json"
    CFG = json.loads(cfg_f.read_text()) if cfg_f.exists() else {}
    if not force and (CFG.get("_reviewed") == str(now.date()) or now.hour == 0 and now.minute < 30):
        return print("review: not due")
    log = [f"\n## Self-review {now:%Y-%m-%d %H:%M} UTC\n"]
    why = {}
    for sym in list(OKX) + list(YF):
        cur = {**DEFAULT, **CFG.get(sym, {})}
        W = window(sym, root)
        if W is None or len(W) < 400:
            log.append(f"- {sym}: not enough scored predictions yet ({0 if W is None else len(W)}); settings unchanged ({cur['threshold']}, blocked {cur['blocked']})")
            continue
        p80 = float(W.dist.quantile(0.8))
        F = flags(W, p80)
        tab = {c: (round(float(W.right[F[c]].mean()), 3), int(F[c].sum())) for c in CONDS if F[c].sum()}
        why[sym] = dict(all=(round(float(W.right.mean()), 3), len(W)), by_situation=tab)
        # threshold: choose on the older half, keep only if it also wins on the newer half
        mid = W.index[len(W) // 2]
        old, new = W[W.index < mid], W[W.index >= mid]
        best = max(THRESH, key=lambda t: score(old, t)[0])
        s_new_best, s_new_cur = score(new, best), score(new, cur["threshold"])
        thr, note = cur["threshold"], "kept"
        if best != cur["threshold"] and s_new_best[0] > s_new_cur[0] and s_new_best[0] > max(s_new_cur[0], 1.0):     # clearly better than chance on fresh data
            thr, note = best, f"changed {cur['threshold']} -> {best} (newer half: {s_new_best[2]:.1%} right on {s_new_best[1]} calls vs {s_new_cur[2] or 0:.1%} on {s_new_cur[1]})"
        # blocks: situations where its CALLS are reliably wrong
        calls = W[W.p_right >= thr]; Fc = F.loc[calls.index]
        blocked = []
        for cnd in CONDS:
            x = calls.right[Fc[cnd]]
            if len(x) >= 150 and x.mean() + 1.64 * np.sqrt(0.25 / len(x)) < 0.52:
                blocked.append(cnd)
            elif cnd in cur["blocked"]:
                y = W.right[F[cnd]]                      # previously blocked: unblock if it recovered on all scored
                if not (len(y) >= 150 and y.mean() >= 0.52):
                    blocked.append(cnd)
        ch = []
        if note != "kept":
            ch.append("threshold " + note)
        if set(blocked) != set(cur["blocked"]):
            ch.append(f"blocked situations {cur['blocked']} -> {blocked}")
        CFG[sym] = dict(threshold=thr, blocked=blocked, dist_p80=round(p80, 4))
        c_acc = calls.right.mean() if len(calls) else float("nan")
        log.append(f"- {sym}: {len(W)} scored (last 90 days, {int((W.src == 'live').sum())} live); right {W.right.mean():.1%} overall, "
                   f"{c_acc:.1%} on {len(calls)} calls at threshold {thr}. " + ("; ".join(ch) if ch else "No change (nothing beat the current settings on fresh data)."))
        worst = sorted(tab.items(), key=lambda kv: kv[1][0])[:3]
        log.append("  worst situations: " + ", ".join(f"{k} {v[0]:.1%} (n {v[1]})" for k, v in worst))
    CFG["_reviewed"] = str(now.date())
    cfg_f.write_text(json.dumps(CFG, indent=1))
    mf = root / "mistakes.csv"
    if mf.exists():
        M = pd.read_csv(mf); M["bar"] = pd.to_datetime(M.bar, utc=True)
        M = M[M.bar >= pd.Timestamp(now) - pd.Timedelta(days=7)]
        if len(M):
            reasons = M.why.str.split("; ").explode().str.replace(r"news: .*", "news", regex=True).str.replace(r"shock move .*", "shock move", regex=True)
            log.append(f"- wrong calls in the last 7 days: {len(M)}; reasons: " + ", ".join(f"{k} {v}" for k, v in reasons.value_counts().items()))
    (root / "UPGRADES.md").open("a").write("\n".join(log) + "\n")
    (root / "WHY.json").write_text(json.dumps(why, indent=1))
    print("\n".join(log))


if __name__ == "__main__":
    main(sys.argv[1], "--force" in sys.argv)
