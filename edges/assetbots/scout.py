"""Scouts for the asset bots: the chance of a BIG move (either way) over the next 4 h (day) and 24 h (swing).

BTC uses the existing OMEGA scouts (edges/scouts/models15 = 15m bars, 4 h; edges/scouts/models = 1h bars, 24 h),
trained on 30 coins and tested in E81/E82: they rank big moves better than chance (AUC ~0.57-0.61) but trading their
flags lost money after costs. Information only.

Gold and silver have their own scouts, trained here with the SAME features and labels (edges/scouts/model.py) on hourly
bars: gold on PAXG/USDT (a 24/7 gold-backed token, a proxy for XAUUSDT), silver on SI=F hourly futures (CME hours, a
different clock from the 24/7 perpetual). They are fitted on DISCOVERY and checked on VALIDATION only (ASSETS_BRIEF.md
periods; the FINAL period is left untouched for the research bots), then refitted on discovery+validation for live use.
They are UNTESTED as trading signals: shown as "big-move risk" only, never as a direction.

  python -m edges.assetbots train XAU|XAG|all [--out DIR]    (monthly; needs $OMEGA_DATA/metals, see fetch_metals.py)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
METAL_DATA = {"XAU": ("PAXG_1h", "PAXG/USDT spot hourly (24/7 gold-backed token, a proxy)",
                      ("2020-01-01", "2024-01-01", "2025-01-01")),
              "XAG": ("SI_1h", "SI=F silver futures hourly (CME hours)",
                      ("2024-06-01", "2025-07-01", "2026-01-01"))}
HORIZONS = {"day": 4, "swing": 24}           # hours, on 1h bars
TARGETS = ("up_move", "down_move")


def model_dir(asset: str, home: Path | None = None) -> Path:
    """Retrained models in the bot's home win over the ones shipped in the repo."""
    if home is not None and (Path(home) / "models" / asset / "meta.json").exists():
        return Path(home) / "models" / asset
    return HERE / "models" / asset


def _load_metal(asset: str) -> pd.DataFrame:
    name = METAL_DATA[asset][0]
    d = pd.read_parquet(Path(os.environ.get("OMEGA_DATA", "/home/user/data")) / "metals" / f"{name}.parquet")
    if "ts" in d.columns:
        d.index = pd.to_datetime(d.pop("ts"), unit="ms", utc=True)
    d = d.rename(columns=str.lower)
    for k in ("o", "h", "l", "c", "v"):
        if k not in d.columns:
            raise ValueError(f"{name}: missing column {k}")
    if "qv" not in d.columns:
        d["qv"] = d.v * d.c
    d = d[~d.index.duplicated(keep="last")].sort_index()
    d = d[d.c > 0]
    return d[["o", "h", "l", "c", "v", "qv"]].astype(float)


def train(asset: str, out: Path | None = None) -> dict:
    """Fit on discovery, score on validation (AUC, Brier skill), refit on discovery+validation, save. CPU: 1 thread."""
    from sklearn.metrics import roc_auc_score
    from edges.scouts.model import features, labels, fit
    d = _load_metal(asset)
    a, b, c = (pd.Timestamp(x, tz="UTC") for x in METAL_DATA[asset][2])
    X = features(d, None)
    fcols = list(X.columns)
    out = Path(out or HERE / "models" / asset)
    out.mkdir(parents=True, exist_ok=True)
    meta = dict(asset=asset, data=METAL_DATA[asset][1], features=fcols, tf="1h", horizons=HORIZONS,
                discovery=[str(a.date()), str(b.date())], validation=[str(b.date()), str(c.date())],
                final_untouched_from=str(c.date()), thresholds={}, validation_scores={}, base_rates={},
                status="UNTESTED as a trading signal: big-move risk only, never a direction")
    for hz, hb in HORIZONS.items():
        D = X.join(labels(d, hb))
        for t in TARGETS:
            key = f"{hz}_{t}"
            tr = D[(D.index >= a) & (D.index < b - pd.Timedelta(hours=hb))].dropna(subset=[t])
            va = D[(D.index >= b) & (D.index < c - pd.Timedelta(hours=hb))].dropna(subset=[t])
            m = _fit1(fit, tr[fcols], tr[t])
            p = m.predict_proba(va[fcols])[:, 1]
            y, base = va[t].values, tr[t].mean()
            auc = float(roc_auc_score(y, p)) if len(set(y)) > 1 else float("nan")
            bss = float(1 - np.mean((p - y) ** 2) / np.mean((base - y) ** 2))
            meta["validation_scores"][key] = dict(n_train=int(len(tr)), n_val=int(len(va)), auc=round(auc, 4),
                                                  brier_skill=round(bss, 4))
            full = D[(D.index >= a) & (D.index < c - pd.Timedelta(hours=hb))].dropna(subset=[t])
            m = _fit1(fit, full[fcols], full[t])
            m.booster_.save_model(str(out / f"{key}.txt"))
            meta["thresholds"][key] = float(np.quantile(m.predict_proba(full[fcols])[:, 1], 0.95))
            meta["base_rates"][key] = float(full[t].mean())
    meta["trained_to"] = str((c - pd.Timedelta(hours=1)).date())
    meta["trained_at"] = pd.Timestamp.now(tz="UTC").isoformat()[:19]
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def _fit1(fit, X, y):
    """edges.scouts.model.fit's settings, on one CPU thread (the research bots share this machine)."""
    import lightgbm as lgb
    m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=31, min_child_samples=400,
                           subsample=0.7, subsample_freq=1, colsample_bytree=0.7, reg_lambda=5.0,
                           random_state=0, verbose=-1, n_jobs=1)
    m.fit(X, y)
    return m


class ScoutReader:
    """Reads the scouts for one asset from closed bars. Returns None (with a reason) when models are missing."""

    def __init__(self, asset: str, home: Path | None = None):
        self.asset, self.home = asset, home
        self._m = None

    def _omega(self, d15, d1h):
        import lightgbm as lgb
        from edges.scouts.model import features
        out = {}
        for hz, (env, sub, df) in (("day", ("SCOUT_MODELS15", "models15", d15)), ("swing", ("SCOUT_MODELS", "models", d1h))):
            p = os.environ.get(env)
            d = Path(p) if p and (Path(p) / "meta.json").exists() else REPO / "edges" / "scouts" / sub
            if df is None or len(df) < 400 or not (d / "meta.json").exists():
                continue
            meta = json.loads((d / "meta.json").read_text())
            x = features(df, df).iloc[[-1]][meta["features"]]
            r = {}
            for t in TARGETS:
                r[t] = float(lgb.Booster(model_file=str(d / f"{t}.txt")).predict(x)[0])
                r[f"flag_{t}"] = bool(r[t] >= meta["thresholds"][t])
            out[hz] = self._shape(r, "4 h" if hz == "day" else "24 h", meta.get("trained_to", "")[:10],
                                  "OMEGA scouts (30 coins); tested E81/E82: rank big moves better than chance, "
                                  "trading the flags lost money after costs")
        return out

    def _asset(self, d1h):
        import lightgbm as lgb
        from edges.scouts.model import features
        d = model_dir(self.asset, self.home)
        if d1h is None or len(d1h) < 400 or not (d / "meta.json").exists():
            return {}
        meta = json.loads((d / "meta.json").read_text())
        x = features(d1h, None).iloc[[-1]][meta["features"]]
        out = {}
        for hz in HORIZONS:
            r = {}
            for t in TARGETS:
                key = f"{hz}_{t}"
                r[t] = float(lgb.Booster(model_file=str(d / f"{key}.txt")).predict(x)[0])
                r[f"flag_{t}"] = bool(r[t] >= meta["thresholds"][key])
            vs = meta.get("validation_scores", {})
            aucs = [vs.get(f"{hz}_{t}", {}).get("auc") for t in TARGETS]
            ok = all(isinstance(a, float) and a == a and a >= 0.55 for a in aucs)
            out[hz] = self._shape(r, f"{HORIZONS[hz]} h", meta.get("trained_to", ""),
                                  f"own scout on {meta['data']}; validation AUC "
                                  + "/".join(f"{a:.2f}" if isinstance(a, float) and a == a else "?" for a in aucs)
                                  + " (up/down); UNTESTED as a trading signal"
                                  + ("" if ok else "; NO SKILL on validation (AUC < 0.55): not used for WATCH"),
                                  skill_ok=ok)
        return out

    @staticmethod
    def _shape(r, horizon, trained_to, label, skill_ok=True):
        return dict(horizon=horizon, skill_ok=skill_ok, p_big_move=round(min(1.0, r["up_move"] + r["down_move"]), 3),
                    flag=bool((r["flag_up_move"] or r["flag_down_move"]) and skill_ok),
                    detail=dict(p_up_move=round(r["up_move"], 3), p_down_move=round(r["down_move"], 3)),
                    trained_to=trained_to, label=label, direction="none: big-move risk only")

    def read(self, bars: dict, spec) -> dict:
        try:
            if spec.scout == "omega":
                out = self._omega(bars.get("15m"), bars.get("1h"))
            else:
                out = self._asset(bars.get("1h"))
            return out or dict(missing="no scout models available for this asset yet")
        except Exception as e:     # never let a model problem stop the read
            return dict(missing=f"scouts unavailable: {type(e).__name__}")
