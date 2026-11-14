# External handoff — reference numbers to compare against (OMEGA-HANDOFF, prepared 14 Nov 2026)
Another assistant's research, reconstructed from memory; its datasets, models and code are lost and nothing below was
re-run by it. Treat every number as a claim to check, not evidence. Its sample: 2026 Binance BTCUSDT and XAUUSDT
perpetuals (5m/15m), train Jan–Jun 2026, select Jul–Aug, evaluate Sep–Oct, check Nov 1–12. Account 10,000, risk 25 per
trade incl. costs, ≤1× notional, 6 bp per side (stress 12), funding charged, adverse gaps at the open, stop-first.

## BTC (Sep–Oct 2026, account returns)
| family | trades | base | 2× cost |
|---|---|---|---|
| learned price-only | 1 | +0.249% | +0.182% |
| learned flow/macro | 33 | −0.497% | −1.802% |
| price breakout | 383 | −29.6% | −42.0% |
| spot-led breakout | 193 | −14.5% | −19.8% |
| compression | 137 | −14.6% | −19.5% |
| compression + confirmation | 16 | −1.61% | −2.19% |
| economic flow/macro/ETF | 23 | +0.012% | −0.868% |
| accepted retest | 96 | −8.14% | −10.5% |
| macro follow + spot confirm | 5 | −0.70% | −0.78% |
Failed auction BTC: unconfirmed 94 trades −4.63%; spot-confirmed 11 −0.85%; OI-contraction 2 −0.26%.
Movement-timing watch (75th pct threshold): large-move rate 32.9% overall vs 56.1% in watch windows (Sep–Oct), 29.4% vs
58.2% (Nov); a vol/clock-only control scored better overall log loss (0.5878 vs 0.5923; Nov 0.5282 vs 0.5394).
Longer history (train 2024, select 2025, eval Jan–Oct 2026): price-only 22 trades −1.51%; spot/macro/ETF 246 −15.3%.

## Gold XAUUSDT (Sep–Oct 2026)
| family | trades | base | 2× cost |
|---|---|---|---|
| learned price-only | 71 | −0.712% | −4.93% |
| learned flow/macro | 133 | −7.57% | −13.7% |
| price breakout | 433 | −36.3% | −56.4% |
| spot-led breakout | 183 | −10.3% | −19.0% |
| compression | 118 | −13.8% | −24.7% |
| accepted retest | 82 | −5.33% | −8.86% |
Gross price PnL of the 71-trade price-only model +484 vs costs 560 at 6 bp: break-even ≈ 5.2 bp per side.
Native XAUUSD bid/ask replay (Dukascopy, 9 trades, NY 08–12): +1.76% at 1 bp commission; constant SHORT on the same
opportunities +2.72% (beat the model); November 2 trades −0.06%. Weekends: gold "flat" 82.8% of the time (much of the
model's score came from recognising quiet weekends).
Failed auction gold: unconfirmed 100 trades −8.23%; spot-confirmed 34 −2.37%.

## Macro events (delayed 4-hour continuation of the initial reaction, gross)
BTC FOMC +0.643% (2024–25) → −0.126% (2026); PPI +0.481% → −0.322%. Gold (PAXG proxy) PPI +0.048% → −0.517% (2026).
Fixed follow/fade transfer 2026: BTC 18 trades −0.95%, gold 31 trades −2.99%.

## Trend/volatility controller (re-run here as E85)
Gold proxy 2022–Jun 2025 +32.5% (dd 8.9%), BTC 2024–Oct 2026 +14.1% (dd 7.8%); gold 2010–2018 −8.45% under stress.
E85 (this repo): FAIL as an edge, drawdowns 3–7× smaller than holding.

## Their conclusions
Movement timing is somewhat predictable; profitable direction was not established; nothing production-qualified.
