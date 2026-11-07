# OMEGA v6.5.106 — corrections from the bugs / misinformation audit (5 Nov 2026)
Build: `python3 patch106.py <v6.5.105>.html <new>.html`; delivered as `apps/omega-v6_5-47.html`. Test: `s106_test.js` (14 checks;
`PREV=<v6.5.105>` adds the CREED byte-identity check). Full audit: `audits/bugs/BUG_REPORT.md`.

Text and one Brain note only. **CREED's engine is byte-identical** (s102 and s106 with `PREV`); no rule's logic, sizing or
storage key changed.

1. **Funding harvest vs E34.** The app still called the harvest "the rule that passed its untouched test" (Autopilot job label),
   showed a green "passed its untouched test" chip and taught "being paid for supplying leverage is [a law]". E34 (Nov 2026)
   ran the delta-neutral harvest on 2025–26: −17% a year, worst 30 days −33%, one funding flip −64.6% in a month. Now shown on
   the harvest card (red "Read this first" line, heading, chip), the Round 12 winners card (half of each winner is the
   harvest), the Round 12 summary, the research-record heading, the lesson in the round list and both Autopilot labels.
   The historical round results (7, 8, 10, 12) are kept as they were measured.
2. **Futures page: "Leverage — what the tests say".** No word on the page said that no tested rule has an edge worth levering.
   New red card: CREED −0.10R to −0.12R a trade, 76% of simulated accounts lose half in a year at 1% risk; E26 (H1 as a
   100 USDT account, no leverage) fell 56–59%; the 5% × 10× default puts half the account into each position and a ~9% move
   liquidates it; Prime uses 1× isolated and the Bridge caps a Binance order at 10 USDT.
3. **"Why signals are rare" footer** listed two ideas as "not yet run" that had been run (BTC/ETH timing, E28 round 5; H1/H3 on
   every perpetual, E25/E26). Now lists the untested ones from the handover (on-chain flows, options data).
4. **"Risk-free" after a breakeven stop** (signal plan, Simulation plan) → the stop limits the loss, but gaps, slippage, fees
   and funding still apply (the app's own stop note already says a stop is not a guaranteed exit).
5. **Brain:** one pinned correction note about E34, written once (flag `omega_e34_note_v1`).
6. **Bug: two cards shared one `<style id="pbCss">`.** The research card and the panic card each create it only if it is
   missing, so whichever 1-second timer ran first won and the panic gauge could lose its `.pgauge` rules. The research card's
   style is now `id="rareCss"` (s106 checks both exist and the gauge rules are present).
