# E145 "OI-confirmed move" on markets it has never been run on (independent replication)
Rule exactly as E143 P4 / E144 (z of 4h OI change >= 2 over 7 days, 4h price move >= 2 ATR14 on 15m bars, follow the
move; entry next 15m open on 1m path; 4h hold with stop 1.5 ATR / target 3 ATR, and 24h hold with stop 3 ATR).
Markets (Binance USDT-M perps with metrics files), all history from 2025-06-01 or listing to 2026-11-13:
 group COMMODITY: XPTUSDT, XPDUSDT, COPPERUSDT, NATGASUSDT, CLUSDT  (the group the hypothesis is about: real-asset
                  perps where a jump in open interest means new outside money)
 group INDEX: QQQUSDT, SPYUSDT
 group CRYPTO: ETHUSDT, SOLUSDT (expected NOT to work, as BTC did not: a contrast)
Cost 0.04% per side everywhere (0.07% crypto). No tuning, so the whole history of each market is test data; results also
shown by halves. Random-entry control (5x entries, seed 145).
Pass for the hypothesis "works on real-asset perps": pooled COMMODITY mean > 0 after costs with week-clustered t >= 2
for a hold, positive in at least 4 of 5 markets, and above the control. If it passes for 24h or 4h, that hold (pooled
with gold and silver) becomes a grade B paper rule on the desks. If pooled COMMODITY <= 0: the gold/silver lead is
treated as a period effect and stays grade C until its forward log decides.
