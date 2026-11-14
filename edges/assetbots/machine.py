"""The per-horizon state machine (day / swing / hold), as in the external handoff:

  WAIT         nothing qualifies (reasons listed)
  WATCH        big-move risk without a direction (scouts with validated skill, volatility, range extremes)
  SETUP        an APPROVED rule for this asset+horizon reports its conditions are forming (optional Strategy.setup())
  TRIGGERED    an approved rule fired on the bar that just closed: a call exists, entry not filled yet
  CONFIRMED    the call's entry filled; the trade is running (paper unless the rule is testnet/live)
  INVALIDATED  the call's stop was hit
  EXPIRED      the call ended otherwise (target, time exit, limit never filled) or a SETUP faded without firing

INVALIDATED / EXPIRED are shown for one cycle, then the horizon falls back to WATCH or WAIT.
A direction (side) can only appear in SETUP/TRIGGERED/CONFIRMED, and only from an approved rule's own output.
"""
from __future__ import annotations

STATES = ("WAIT", "WATCH", "SETUP", "TRIGGERED", "CONFIRMED", "INVALIDATED", "EXPIRED")
PLAIN = {"WAIT": "Nothing to do. No tested rule is calling a trade.",
         "WATCH": "Big-move risk, direction unknown. Watch only: no tested rule is calling a trade.",
         "SETUP": "A tested rule's conditions are forming. No trade yet.",
         "TRIGGERED": "A tested rule fired: a call is out, waiting for its entry.",
         "CONFIRMED": "The call's entry filled: the trade is running (paper record unless the rule is testnet/live).",
         "INVALIDATED": "The call's stop was hit.",
         "EXPIRED": "The call or setup ended (target, time exit, or never filled)."}


def step(prev: dict | None, ctx: dict) -> dict:
    """prev: last cycle's horizon record (or None). ctx: now, watch (reasons), setups, open_calls, closed_now,
    n_rules, notes. Returns the new record {state, since, reasons, call?, setup?, plain}."""
    prev_state = (prev or {}).get("state", "WAIT")
    open_calls, closed = ctx.get("open_calls") or [], ctx.get("closed_now") or []
    reasons, extra = [], {}
    if open_calls:
        c = open_calls[-1]
        state = c["state"]                     # TRIGGERED or CONFIRMED
        extra["call"] = c
        reasons.append(f"rule {c['rule']} (grade {c.get('grade')}) called {c['side']} at {c['signal_bar'][:16]} UTC")
    elif closed:
        c = closed[-1]
        state = c["state"]                     # INVALIDATED or EXPIRED
        extra["call"] = c
        reasons.append(f"call {c['id']} ended: {c.get('outcome')}")
    elif ctx.get("setups"):
        state = "SETUP"
        extra["setup"] = ctx["setups"]
        reasons += [f"rule {s['rule']} (grade {s.get('grade')}) conditions forming" for s in ctx["setups"]]
    elif prev_state == "SETUP":
        state = "EXPIRED"
        reasons.append("the setup faded without the rule firing")
    else:
        w = ctx.get("watch") or []
        state = "WATCH" if w else "WAIT"
        reasons += w
        if not ctx.get("n_rules"):
            reasons.append("no rule for this asset and horizon has passed its test yet, so the bot calls no trades")
        elif state == "WAIT":
            reasons.append("the tested rule(s) for this horizon have not fired")
    reasons += ctx.get("notes") or []
    since = (prev or {}).get("since") if state == prev_state and prev else ctx["now"]
    return dict(state=state, since=since or ctx["now"], previous=prev_state, reasons=reasons, plain=PLAIN[state],
                direction=(extra.get("call") or {}).get("side") if state in ("TRIGGERED", "CONFIRMED") else None,
                **extra)
