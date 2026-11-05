"""Secrets live in the operating system's vault (Windows Credential Manager) through keyring. Never in files or logs."""
import getpass
SERVICE = 'omega-bridge'
NAMES = {'binance_key': 'Binance API key (trading only, NO withdrawals)', 'binance_secret': 'Binance API secret', 'mt5_password': 'MT5 account password'}
def get(name):
    import keyring
    return keyring.get_password(SERVICE, name)
def put(name, value):
    import keyring
    keyring.set_password(SERVICE, name, value)
def ask_and_store(name):
    v = getpass.getpass(NAMES[name] + ': ').strip()
    if not v: raise SystemExit('nothing entered')
    put(name, v); print('saved to the Windows vault:', name)
