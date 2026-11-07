"""Settings, paths and the action log. Config lives in %APPDATA%\\OMEGA-Bots\\config.json (or $OMEGA_BOTS_HOME).
It never holds secrets: a config containing a key, secret or password is refused."""
import copy, json, os, re, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULTS = {
    "mode": "paper",                       # paper | testnet | live  (the CLI --mode overrides)
    "live": False,                         # real money also needs approved.json status "live" and OMEGA_LIVE env
    "approved_file": os.path.join(REPO, "edges", "approved.json"),
    "strategies": [],                      # empty = every rule in approved.json the mode allows
    "universe": "all",                     # "all" USDT-M perpetuals, "top:100" by 24h volume, or a list
    "history_bars": 1000,                  # bars fetched per coin on start (rules need ~820)
    "poll_delay_s": 20,                    # wait after a bar closes so the exchange has the final candle
    "check_every_s": 60,                   # between bar closes: check fills, stops, kill switch
    "binance": {
        "testnet_url": "https://demo-fapi.binance.com",   # Binance's current futures testnet ("demo") REST base
        "live_url": "https://fapi.binance.com",
        "data_url": "https://fapi.binance.com",           # signals always come from the real market's public candles
        "spot_url": "https://api.binance.com",            # only for the live key's no-withdrawal check
        "margin_type": "ISOLATED",
        "recv_window": 5000,
        "use_gtd": True,                   # limit orders expire on the exchange too (goodTillDate), not only in the bot
        "stop_via_algo": True,             # since 2025-12-09 STOP_MARKET goes through POST /fapi/v1/algoOrder
        "rebase_testnet_prices": True,     # testnet prices differ from the real market: scale limits by venue/real price
        "request_spacing_s": 0.12,
    },
    "guard": {
        "hard_max_leverage": 3,            # global cap; each rule's max_leverage in approved.json applies too
        "max_open_positions": 3,           # open positions + resting entry orders
        "max_margin_usdt": 10.0,           # per order
        "daily_loss_limit_usdt": 5.0,      # realized + open, UTC day; then no new orders
        "protective_stop_pct": 0.5,        # rules without a stop get this one (capped inside the liquidation distance)
        "liq_buffer": 0.005,               # stop distance must be < 1/leverage - liq_buffer
        "live_liq_buffer": 0.02,           # wider buffer for real money (mark price can jump past both)
        "max_risk_usdt": 3.0,              # notional x stop distance per trade (5 USDT at 1x with the 50% stop = 2.5)
        "require_ip_restriction": True,    # live key must be bound to your IP
        "require_stop": True,
        "one_position_per_symbol": True,   # Binance one-way mode nets positions: never two rules in one coin
    },
    "mt5": {"enabled": False, "bridge_path": os.path.join(REPO, "omega", "bridge", "OMEGA-Bridge"), "live": False},
}
BAD = re.compile(r"(key|secret|password|token)$", re.I)


def home():
    h = os.environ.get("OMEGA_BOTS_HOME") or os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "OMEGA-Bots")
    os.makedirs(h, exist_ok=True)
    return h


def path(name):
    return os.path.join(home(), name)


def _merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            _merge(a[k], v)
        else:
            a[k] = v
    return a


def _scan_secrets(d, where="config"):
    for k, v in d.items():
        if BAD.search(str(k)):
            raise ValueError(f'{where} must not contain "{k}": keys go in the Windows Credential Manager '
                             f"(python -m edges.bots setkey testnet|live) or in environment variables")
        if isinstance(v, dict):
            _scan_secrets(v, f"{where}.{k}")


def load(overrides=None):
    c = copy.deepcopy(DEFAULTS)
    p = path("config.json")
    if os.path.exists(p):
        _merge(c, json.load(open(p, encoding="utf-8")))
    else:
        json.dump(c, open(p, "w", encoding="utf-8"), indent=2)
    if overrides:
        _merge(c, overrides)
    _scan_secrets(c)
    return c


def approved(cfg):
    try:
        rules = json.load(open(cfg["approved_file"], encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return {r["id"]: r for r in rules if isinstance(r, dict) and "id" in r}


# ---------------------------------------------------------------- action log (JSON lines, secrets redacted)
SECRETISH = re.compile(r"(signature|apikey|api_key|secret|password|X-MBX-APIKEY)", re.I)


def log(event, **kw):
    rec = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), event=event, **kw)
    txt = json.dumps(rec, default=str)
    if SECRETISH.search(txt):
        txt = json.dumps(dict(t=rec["t"], event=event, note="redacted: a secret-like field was present"))
    with open(path("bots_log.jsonl"), "a", encoding="utf-8") as f:
        f.write(txt + "\n")
    if os.environ.get("OMEGA_BOTS_QUIET") != "1":
        print(txt[:400], flush=True)
    return rec


def tail(n=20):
    try:
        return [json.loads(x) for x in open(path("bots_log.jsonl"), encoding="utf-8").read().splitlines()[-n:]]
    except FileNotFoundError:
        return []
