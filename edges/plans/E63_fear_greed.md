# E63 — Fear & Greed index extremes as a contrarian daily signal (BTC, ETH)
Conventions: `E63_common_bot3.md`. Written before the data was compared with prices.
Source: alternative.me Fear & Greed (daily, 2018-02 →), keyless. Not tested before in OMEGA (E28 used candles only).
## Hypothesis: extreme fear marks capitulation (buy), extreme greed marks crowded tops (short), multi-day horizon.
## Trades: BTCUSDT and ETHUSDT perps pooled into one rule (both coins trade the same index value). Entry D 02:00 UTC after
the value stamped D; time exit after H days; one position per coin.
## Grid (27 variants)
- L: long when FNG ≤ X, X ∈ {10, 15, 20, 25}; H ∈ {3, 7, 14} d → 12
- S: short when FNG ≥ Y, Y ∈ {75, 80, 85, 90}; H ∈ {3, 7, 14} d → 12
- D: long when FNG fell ≥ 20 points over the last 3 days; H ∈ {3, 7, 14} d → 3
## Luck check: FNG series circularly shifted vs prices (200 shifts), whole grid re-run, best discovery t.
## Promotion/FINAL per common conventions. Note: trades are few (daily, 2 coins); the ≥100 FINAL-trade or ≥50 with t≥3
requirement is likely binding — stated in advance.
