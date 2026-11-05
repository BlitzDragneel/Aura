# PLAN E13 — three questions for the first full Market Watch recording
Written 2026-10-21, before any usable recording exists (the first export held 47 minutes and was not used).
Data: an omega-watch export (decoded by edge/mwload.py). Minimum to run at all: at least 5 days in which BTC has live minute
data in ≥ 80% of minutes; otherwise nothing is run and the file is noted as too short. Run ONCE on the first file that
qualifies (its sha256 recorded first); each question judged on its own; reported whatever happens.
Costs for any trade: 0.10% round trip (Binance USD-M taker 0.05% a side); returns from futures closes (pC), minute bars.
Q1 — does a liquidation flush end when open interest falls?  (cause: forced sellers run out once positions are gone)
  Event (per coin): a minute whose long liquidations (liqL, USDT) are at least 10× that coin's median non-zero minute of
  long liquidations in the file, while pC fell ≥ 1% over the previous 15 minutes. Events closer than 60 minutes on one
  coin count once. Group F: open interest (pos.oi, 5-minute) fell ≥ 0.5% over the 15 minutes up to the event; group N: the rest.
  Outcome: pC return from the next minute's close to 60 minutes later, minus costs.
  Pass: group F has ≥ 30 events, its average outcome is positive with t ≥ 1.65 (events clustered by hour), and it beats
  group N. Mirror for short liquidations reported, not tested.
Q2 — absorption on the real tape.  (cause: aggressive orders met by passive ones that do not give way)
  Minute signal (per coin): futures taker imbalance (pBuy − pSell)/(pBuy + pSell) in the top 5% of that coin's minutes in
  the file AND pC did not rise that minute → short; bottom 5% AND pC did not fall → long. Hold 15 minutes from the next
  minute's close; no overlap within a coin. Pass: average net of costs positive, t ≥ 1.65 (clustered by hour).
  The gross (before-cost) average is reported too.
Q3 — does Coinbase lead Binance?  (cause: US spot demand arrives on Coinbase first)
  Minute log returns of Coinbase BTC (cbBTC) and Binance BTC (bnBTC); lead = correlation of Coinbase's minute with
  Binance's next minute; lag = the reverse. Coinbase leads if lead − lag ≥ 0.05 and lead's t ≥ 3 (n = minutes). Also
  reported: Coinbase premium (cbBTC / (bnBTC × cbUSDT) − 1) vs the next 60 minutes of BTC (correlation, quintile averages).
  Descriptive: even a real lead needs speed and accounts on both exchanges to trade, so no profit is claimed.
