"""OMEGA asset bots (BTC, gold, silver): read each market every 15 minutes, call trades only from tested rules.

  python -m edges.assetbots run <home> [--asset BTC|XAU|XAG]   one cycle for each (or one) asset -> <home>/assets/
  python -m edges.assetbots train XAU|XAG|all [--out DIR]       retrain the metal scouts (needs $OMEGA_DATA/metals)
  python -m edges.assetbots show <home> [--asset XAU]           print the desk summary

<home>/assets/<ASSET>.json is the desk the app shows (GET /assets/<ASSET> on the Live API); <home>/assets/<ASSET>/
holds state.json, readings-YYYY-MM.jsonl, calls-YYYY-MM.jsonl, scores-YYYY-MM.jsonl and NOTEBOOK.md.
Information only: no orders, ever.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "train":
        from edges.assetbots.scout import train
        which = sys.argv[2].upper() if len(sys.argv) > 2 else "ALL"
        out = _arg("--out")
        for a in (("XAU", "XAG") if which == "ALL" else (which,)):
            m = train(a, Path(out) / a if out else None)
            print(a, json.dumps(m["validation_scores"]))
        return 0
    home = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else Path.cwd() / "assetbots_state"
    which = (_arg("--asset") or "ALL").upper()
    from edges.assetbots.assets import BOTS
    names = list(BOTS) if which == "ALL" else [which]
    if cmd == "show":
        for a in names:
            f = home / "assets" / f"{a}.json"
            if f.exists():
                d = json.loads(f.read_text())
                print(a, d["asof"], d["read"].get("price"), {k: v["state"] for k, v in d["horizons"].items()})
        return 0
    if cmd != "run":
        print(__doc__)
        return 2
    from edges.assetbots.engine import LiveProvider
    prov = LiveProvider()
    bad = 0
    for a in names:
        try:
            d = BOTS[a](home, provider=prov).run_once()
            print(f"{a}: price {d['read'].get('price')} | " + " ".join(f"{k}={v['state']}" for k, v in d["horizons"].items())
                  + (f" | errors: {d['errors']}" if d["errors"] else ""), flush=True)
        except Exception as e:      # one asset failing must not stop the others
            bad += 1
            print(f"{a}: FAILED {type(e).__name__}: {e}", flush=True)
    _index(home)
    return 1 if bad == len(names) else 0


def _index(home: Path):
    """assets/INDEX.json: one line per asset for quick listing (the Live API's /assets)."""
    out = {}
    for f in sorted((home / "assets").glob("*.json")):
        if f.stem == "INDEX":
            continue
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        out[f.stem] = dict(name=d.get("name"), asof=d.get("asof"), price=(d.get("read") or {}).get("price"),
                           states={k: v.get("state") for k, v in (d.get("horizons") or {}).items()})
    (home / "assets" / "INDEX.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
