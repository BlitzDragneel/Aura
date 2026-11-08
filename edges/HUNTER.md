# Edge Hunter — the daily research routine

A scheduled Claude session runs this once a day. Its single mission: find a real, tradeable edge — or prove an idea
does not work — and keep the owner's apps and boards truthful. Owner: Maro (Tobago, UTC−4), 100 USDT account,
Binance futures + Exness; wants daily edges, asks about high leverage. Standing rules (omega/OMEGA_HANDOVER_2026-11-02.md §4
and edges/PROTOCOL.md) bind every step: never fabricate; plan before data (write + fingerprint with bt.register_plan);
count every variant (bt.log_attempt); luck-check; DISCOVERY 2020–23 / VALIDATION 2024 / FINAL 2025→ judged once;
costs from bt.round_trip_cost; leverage table for anything that passes; paper first.

## Each run (one idea per day; stop early if the usage limit is near and push what exists)
1. `git clone https://github.com/BlitzDragneel/Aura && cd Aura && git checkout claude/trading-edge-research-bots-gpkvi1`
   (if a newer research branch is named at the top of edges/IDEAS.md, use that one).
2. Read edges/PROTOCOL.md, edges/RESULTS.md (what failed and why) and edges/IDEAS.md.
3. Read the live forward records on the bot-state branch: `STATUS.txt` (paper bot) and `scouts/SCOUTS.md` (UpScout/DownScout).
   If 50+ paper tickets have closed, or 500+ scout calls are scored, write the forward verdict first (it outranks new ideas).
4. Take the first unchecked idea in edges/IDEAS.md. Fetch only the data it needs (edges/data/fetch.py has `top1h`, `5m`,
   `funding`; data.binance.vision, OKX, Deribit, Coinbase, DefiLlama, alternative.me are reachable keyless).
   Write edges/plans/E<next>_<name>.md, register it, run discovery → luck → validation → final.
5. Write edges/results/E<n>_result.json, append a section to edges/RESULTS.md, tick the idea in IDEAS.md with its
   verdict, add 1–3 new ideas the work suggested. A PASS also goes to edges/approved.json (status "paper", max_leverage
   from the leverage table) with a strategy file under edges/bots/strategies/ and a parity check.
6. `python3 -m edges.lead.build_site`, commit with a clear message, push to the same branch.
7. Finish with a 5-line summary: idea, verdict, key numbers, what's next.
Never: place orders, touch keys, change CREED's engine, publish anything outside the repo, or delete research history.
