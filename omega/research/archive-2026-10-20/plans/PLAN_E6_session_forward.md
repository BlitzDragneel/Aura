# PLAN E6 — forward record of the session split, six markets (no trading)
Written 2026-10-20, before any of the days it uses. Found (descriptive, plans E3 and E5, data already used): in gold and in
DOGE, LINK, LTC, ADA, AVAX, returns built up outside US hours and drifted down during them (bars opening 13:00–20:00 UTC).
Forward record, kept by OMEGA v6.5.85 from 2026-10-21 00:00 UTC: Binance USD-M perpetual hourly closes for XAUUSDT,
DOGEUSDT, LINKUSDT, LTCUSDT, ADAUSDT, AVAXUSDT. Each UTC day: OUT = sum of hourly log returns of bars opening 21:00–12:00,
US = sum for bars opening 13:00–20:00 (gold days without bars are skipped).
Judged once, after 26 full weeks (on or after 2027-04-21): weekly (OUT − US) per market, t = mean/(sd/√weeks).
Confirmed for a market if t ≥ 1.65; confirmed overall if the six markets' weekly differences pooled (equal weight) give
t ≥ 2.0. A confirmed split is a timing fact (when to buy, when to wait), not a trading rule, and claims no profit.
