"""API keys: from the OS vault (Windows Credential Manager via keyring) or environment variables. Never files, never logs.

Names: binance_testnet_key / binance_testnet_secret, binance_live_key / binance_live_secret.
Env:   OMEGA_BINANCE_TESTNET_KEY / OMEGA_BINANCE_TESTNET_SECRET, OMEGA_BINANCE_LIVE_KEY / OMEGA_BINANCE_LIVE_SECRET.
A live Binance key must have Futures trading only: the runner refuses a key that can withdraw."""
import getpass, os

SERVICE = "omega-bots"


def _keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def get(name):
    v = os.environ.get("OMEGA_" + name.upper())
    if v:
        return v
    kr = _keyring()
    if kr is None:
        return None
    try:
        return kr.get_password(SERVICE, name)
    except Exception:
        return None


def binance(venue):
    """(key, secret) for venue 'testnet' or 'live', or (None, None)."""
    return get(f"binance_{venue}_key"), get(f"binance_{venue}_secret")


def ask_and_store(venue):
    kr = _keyring()
    if kr is None:
        raise SystemExit("pip install keyring  (or set the OMEGA_BINANCE_* environment variables instead)")
    for part, label in (("key", "API key"), ("secret", "API secret")):
        v = getpass.getpass(f"Binance {venue} {label}{' (Futures trading only, NO withdrawals)' if part == 'key' else ''}: ").strip()
        if not v:
            raise SystemExit("nothing entered")
        kr.set_password(SERVICE, f"binance_{venue}_{part}", v)
    print(f"saved to the OS vault (service {SERVICE}): binance_{venue}_key / _secret")
