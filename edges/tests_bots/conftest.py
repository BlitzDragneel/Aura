import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pytest


@pytest.fixture(autouse=True)
def bots_home(tmp_path, monkeypatch):
    """Every test gets its own config/state/log folder and no real-money switch."""
    monkeypatch.setenv("OMEGA_BOTS_HOME", str(tmp_path))
    monkeypatch.delenv("OMEGA_LIVE", raising=False)
    for k in list(os.environ):
        if k.startswith("OMEGA_BINANCE_"):
            monkeypatch.delenv(k, raising=False)
    return tmp_path
