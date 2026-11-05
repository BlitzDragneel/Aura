# OMEGA v6.5.91 — Daily Plan, Market now, and the Autopilot runs Market Watch again (light) (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.91 · build 2026-10-22 02:10 UTC. Made with `python3 patch91.py <v6.5.90 build> <new build>` (uses `dplan.js`, `autocov91.js`).

## New: Market now and Today's plan (module `OMEGA_DPLAN`)
Shown at the top of **Market Read** and of the **Analysis** page.

**Market now:**
- **State**, using plan E8's definitions on BTC, ETH, SOL, BNB and XRP's own daily index: Booming, Depressed, Correcting, Consolidating or Normal.
- **Trend:** uptrend or downtrend, against the 200-day average.
- **Falling this week:** 7-day return ≤ −5%.
- **The top-5 index's** 7- and 30-day returns.
- **The session now,** in UTC and Tobago time (US hours flagged as the busiest).
- **BTC today:** change and range against a typical day, and positioning.

**Which side, per coin:**

| Market state | Side |
|---|---|
| Booming | Longs (coin above its 200-hour average) |
| Depressed | Shorts (coin below it) |
| Correcting | Longs at the liquidity below |
| Normal or consolidating | Follow the trend where the coin agrees; otherwise stand aside |

**Today's plan:**
- **Entry** at the nearest liquidity pool on the with-trend side (Market Read's levels, within 3 hourly ranges).
- **Stop** half a range beyond it; **target** the nearest pool on the other side.
- **Shown only at 1.5:1 or better,** with the reason in words.
- **Grade C · unproven · paper first:** the trend and sweep rules it resembles failed fair tests. Grade A signals come only from the climax watch.

**Forward record (plan E16, md5 `884bd4e2…`):**
- A plan becomes a paper trade when an hourly bar touches its entry, and closes at the stop, the target or after 48 hours, with 0.12% costs, in R.
- A notification is sent when a plan triggers.
- Judged once after 50 trades or 26 weeks.

**Autopilot job `dplan`** runs hourly.

## Changed
- **The Autopilot runs Market Watch again, in light mode:** one-minute bars instead of every trade, so far lighter for a phone. Its job can be switched off on the Autopilot page, and full mode can still be chosen in Market Watch.
- **Market Read banner:** "what is going on now, which side to trade, today's plan, and where liquidity lies".
- **Brain:** `KN.earlier` gains E16. Research record round 30; the heading now reads rounds 1–30.

## Verification
- **s91 (6 checks):**
  - market state: a built boom reads Booming/uptrend, a built slide reads Depressed/downtrend and falling;
  - booming gives a long at the liquidity below with the exact entry, stop, target and 9:1;
  - depressed gives a short at the liquidity above;
  - it stands aside when the coin disagrees or reward-to-risk is under 1.5:1;
  - the forward record scores a target hit and a stop after costs;
  - a browser run: Market now with a real state and Today's plan for the five coins on Market Read and Analysis, graded C, the forward record and the Autopilot job; no NaN, no overflow, no page errors.
- **Debug finding:** the first browser run showed "Unknown". My fake daily candles had zero highs and lows, and the app's data guard correctly rejected them. The app was right; the test now uses valid candles and requires a real state.
- **All 25 suites pass** (s49…s91). Record-heading checks were widened for round 30; s90 accepts both Market Watch behaviours.
- **Other checks:** 111 script blocks pass the syntax check; no duplicate ids; phone guard clean; 27-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
