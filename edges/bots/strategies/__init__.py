"""Strategy registry: every module here (not starting with "_") that defines STRATEGY is a rule."""
import importlib, os, pkgutil

_HERE = os.path.dirname(os.path.abspath(__file__))


def ids():
    return sorted(m.name for m in pkgutil.iter_modules([_HERE]) if not m.name.startswith("_"))


def load(sid):
    mod = importlib.import_module(f"edges.bots.strategies.{sid}")
    st = getattr(mod, "STRATEGY", None)
    if st is None:
        raise ValueError(f"strategy module {sid} defines no STRATEGY")
    if getattr(st, "id", None) != sid:
        raise ValueError(f"strategy module {sid}: STRATEGY.id is {getattr(st, 'id', None)!r}, must equal the file name")
    return st


def all_strategies():
    out = {}
    for s in ids():
        try:
            out[s] = load(s)
        except Exception as e:  # a broken research file must not stop the others
            out[s] = e
    return out
