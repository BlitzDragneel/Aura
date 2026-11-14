# OMEGA v6.5.119 — Desks: Bitcoin, Gold, Silver
- New page **Desks** (menu "Charts & markets", a three-tile strip on Home, the command palette; bottom bar unchanged; Home's
  8 cards unchanged). One desk per asset, read from the asset bots (`edges/assetbots`) through `GET /assets/{BTC|XAU|XAG}`:
  - price: the 24/7 perpetual live in the browser (v6.5.118 chain) and, for metals, the spot quote;
  - "What the bot says now": one plain sentence from its three horizons;
  - Day / Swing / Holding tiles: WAIT · WATCH · SETUP · TRIGGERED · CONFIRMED · INVALIDATED · EXPIRED, since when, the tested
    rules for that horizon, reasons in a "Why" dropdown. A direction appears only on TRIGGERED/CONFIRMED and only from a tested
    rule's call; the call shows rule, grade, entry, stop, target, exit time, size from the rule, evidence, and "paper record"
    or "execution allowed" (testnet/live rules only);
  - dropdowns: the market read (trend per timeframe, volatility regime and percentile, session, 24h/7d/30d ranges, funding,
    scouts as big-move risk with their labels — a scout without validated skill says so), the forward record, the notebook.
- No token: live prices still show, with a button to Settings. Old reading (> 60 min): said plainly. Desk not written yet: said.
- Autopilot job `desks` (2 min while Desks or Home is open, else 15 min); last desks kept for offline reading (`omega_desks_v1`).
- Tests: new s119 (20/20, screenshots with `SHOTS=`); all suites below pass. Build `python3 patch119.py <v6.5.118> <out>`.
