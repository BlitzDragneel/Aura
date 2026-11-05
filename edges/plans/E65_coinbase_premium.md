# E65 — Coinbase premium (US spot demand vs Binance spot) as a lead signal, 1h (BTC, ETH)
Conventions: `E63_common_bot3.md`. Sources: Coinbase Exchange public candles BTC-USD/ETH-USD 1h (2020 →), Binance spot
BTCUSDT/ETHUSDT 1h (data.binance.vision, 2020 →).
## Signal: p_t = ln(Coinbase close / Binance spot close) at hour t. USD/USDT drift is removed by a z-score:
z = (p_t − mean_W) / sd_W over the trailing W hours (excluding t).
## Hypothesis: a large US-spot premium (US buyers lifting offers) leads price up over the next hours; a discount leads down.
The fade (opposite) is tested too because premium spikes can be stale prints.
## Grid (24 variants): W ∈ {168, 720} × k ∈ {2, 3} × H ∈ {4, 12, 24} h × mode {follow (z≥k long, z≤−k short), fade
(z≥k short, z≤−k long)}. BTC and ETH pooled, each on its own premium. Perp is the traded instrument.
## Luck check: premium series circularly shifted (200 shifts).
