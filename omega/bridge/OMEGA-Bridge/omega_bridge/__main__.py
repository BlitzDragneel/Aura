"""python -m omega_bridge  setkey binance | setkey mt5 | status | funding | mcp | kill on|off"""
import sys, json
def main():
    a = sys.argv[1:] or ['status']
    if a[0] == 'setkey':
        from .secrets import ask_and_store
        if a[1:] == ['binance']: ask_and_store('binance_key'); ask_and_store('binance_secret')
        elif a[1:] == ['mt5']: ask_and_store('mt5_password')
        else: print('setkey binance | setkey mt5')
    elif a[0] == 'status':
        from .core import Bridge; print(json.dumps(Bridge().status(), indent=1, default=str))
    elif a[0] == 'mcp':
        from .mcp_server import run; run()
    elif a[0] == 'funding':
        from .funding import snapshot; print(json.dumps(snapshot(), indent=1))
    elif a[0] == 'kill':
        from .core import Bridge; print(Bridge().kill(on=(a[1:] != ['off'])))
    else: print(__doc__)
if __name__ == '__main__': main()
