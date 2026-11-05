"""OMEGA trading bots.

  python -m edges.bots backtest --strategy panic_h1 [--from 2024-01-01] [--to 2025-01-01] [--coins BTCUSDT,ETHUSDT]
                                [--max-coins 100] [--stop 0.5] [--margin 5] [--max-open 3] [--save]
  python -m edges.bots run --mode paper|testnet|live [--once]
  python -m edges.bots status
  python -m edges.bots kill [off]
  python -m edges.bots setkey testnet|live
  python -m edges.bots list
"""
import argparse
import warnings
warnings.filterwarnings("ignore", message="Converting to PeriodArray")
import json
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m edges.bots", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("backtest")
    b.add_argument("--strategy", required=True)
    b.add_argument("--from", dest="start", default="2020-01-01")
    b.add_argument("--to", dest="end", default=None)
    b.add_argument("--coins", default=None)
    b.add_argument("--max-coins", type=int, default=None)
    b.add_argument("--stop", type=float, default=None, help="stop as a fraction (0.5 = -50%%) for rules without one")
    b.add_argument("--margin", type=float, default=5.0)
    b.add_argument("--max-open", type=int, default=3)
    b.add_argument("--no-funding", action="store_true")
    b.add_argument("--save", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--mode", choices=["paper", "testnet", "live"], default=None)
    r.add_argument("--once", action="store_true", help="one cycle, then exit")
    sub.add_parser("status")
    k = sub.add_parser("kill")
    k.add_argument("off", nargs="?", default=None)
    s = sub.add_parser("setkey")
    s.add_argument("venue", choices=["testnet", "live"])
    sub.add_parser("list")
    a = ap.parse_args(argv)

    if a.cmd == "backtest":
        from edges.bots import backtest as B
        coins = a.coins.split(",") if a.coins else None
        tr, info = B.run(a.strategy, syms=coins, start=a.start, end=a.end, stop_pct=a.stop, funding=not a.no_funding,
                         max_coins=a.max_coins)
        rep = B.report(tr, info, margin_usdt=a.margin, max_open=a.max_open)
        B.print_report(rep)
        if a.save:
            print("saved", B.save(rep, f"{a.strategy}_{a.start}" + (f"_stop{a.stop}" if a.stop else "")))
    elif a.cmd == "run":
        from edges.bots.live import Runner
        rn = Runner(mode=a.mode)
        if a.once:
            print(json.dumps(rn.cycle(full=True), default=str, indent=1))
        else:
            rn.run_forever()
    elif a.cmd == "status":
        from edges.bots import config as C, guard as G
        from edges.bots.state import State
        cfg, st = C.load(), State()
        print(json.dumps(dict(home=C.home(), mode_config=cfg["mode"], live_switch=cfg["live"], kill_switch=G.killed(),
                              guard=cfg["guard"], approved={k: v.get("status") for k, v in C.approved(cfg).items()},
                              last_bar=st.d.get("last_bar"), resting_orders=list(st.orders.values()),
                              open_positions=list(st.positions.values()), closed_trades=len(st.d["closed"]),
                              today_pnl_paper=st.day_pnl(__import__("pandas").Timestamp.now(tz="UTC").strftime("%Y-%m-%d")),
                              recent_log=C.tail(10)), indent=1, default=str))
    elif a.cmd == "kill":
        from edges.bots import guard as G
        if a.off == "off":
            G.set_kill(False)
            print("kill switch OFF: new orders allowed again")
        else:
            from edges.bots.live import standalone_kill
            print(json.dumps(standalone_kill(), indent=1, default=str))
    elif a.cmd == "setkey":
        from edges.bots import keys
        keys.ask_and_store(a.venue)
    elif a.cmd == "list":
        from edges.bots import config as C, strategies as S
        appr = C.approved(C.load())
        for sid, st in S.all_strategies().items():
            ok = not isinstance(st, Exception)
            print(f"{sid:<24} {'ok ' if ok else 'ERR'} approved={appr.get(sid, {}).get('status', '-'):<8} "
                  f"{(st.tf + ' ' + str(st.universe)[:30]) if ok else st}")
    else:
        ap.print_help()


if __name__ == "__main__":
    sys.exit(main())
