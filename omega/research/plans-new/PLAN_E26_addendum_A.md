# PLAN E26 — addendum A (written 2026-10-26 before the 2020–2023 archive was assembled and before any E26 signal, trade or
# account was computed). Settles what PLAN E26 left open, and one thing it needs that is not available.
1. MINIMUM ORDER: exchangeInfo (the plan's source) is not reachable from the sandbox and has not been uploaded, and delisted coins
   are not in it anyway. Every coin is given Binance's usual USDT-M minimum of 5 USDT. Also reported (not pass/fail): the result
   without BTCUSDT and ETHUSDT, whose minimums may be higher. If exchangeInfo arrives later, the share of trades on coins whose
   real minimum is above the seat is reported; if it exceeds 5% of trades, E26 is marked provisional.
2. SEATS: arm A: seat = max(5 USDT, equity at Monday 00:00 UTC / 20); arm B: seat = max(10 USDT, equity at Monday / 10).
   Seat size is fixed for the week. 1× (notional = margin): open plus reserved seats may not exceed equity, so after losses fewer
   seats can be open; never more than 20 (A) or 10 (B). A seat is RESERVED when the limit order is placed (the signal hour) and
   freed if the order is unfilled after 3 hours; a filled seat is held until its exit. A coin already holding a seat or an order
   is not taken again.
3. SAME-HOUR SIGNALS: deepest 24-hour return first (as the plan).
4. TRADE RESULT: H1 exactly as E25 (fill below the limit within 3 hours, exit at the close 24 hours after the fill hour);
   0.12% + 0.03% funding; the −10% disaster stop from the fill price, checked on the candles AFTER the fill hour (as E24's code):
   if a low reaches it, exit at the stop or at that candle's open if it opened below, with 0.10% extra slippage; delisting and gaps
   as E25 (addenda A and B: volume-0 candles missing; past the last traded hour, last close − 5%).
5. RANDOM ACCOUNTS (500 per arm, seed 26): each copies the real account's trade timeline exactly (same entry hours, exit hours
   and seat sizes) but every trade's coin is drawn at random from the coins with a real candle at that hour, listed 30+ days, not
   already held; entry at that hour's close, exit 24 hours later, same costs (0.15%), stop and delisting rules. So it holds the
   same exposure at the same times in random coins: the test is whether H1's choice of coin and price beats that.
6. EQUITY, DRAWDOWN AND YEARS: equity is booked at exits (as E23/E24); max drawdown on that curve (this understates intratrade
   swings, stated in the report). Calendar years 2021–2026 (2026 to 18 Oct).
7. DATA: monthly 1h archive files 2020-11 → 2023-09 joined to E25's 2023-10 → 2026-10-18; same symbol rule and addendum B rules.
   Signals from 2021-01-01; coins listed 30+ days.
Pass per arm (unchanged): above ≥ 97.5% of random accounts, above 100, max drawdown < 35%, gains in ≥ 5 of the 6 years.
