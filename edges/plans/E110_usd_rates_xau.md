# E110 — Gold vs the US dollar and rates (honest data: Yahoo DX-Y.NYB, ^TNX daily), swing
Common rules E100. GC_1d closes; DXY/TNX at their close on day t (17:00 NY, after the 13:30 gold settle) → position from
gold settle t+1 to t+2 (one extra day lag, no look-ahead). Rules:
  D_MA{50,100,200} long/flat: long gold when DXY < its N-day mean; D_MA{...} long/short: short gold when above. (6)
  R_CHG{20,60}: long gold when TNX's N-day change < 0 (yields falling), else flat (LF) or short (LS). (4)
10 variants. Costs as E108 (0.05% turnover + CFD financing). Luck/control: circular shift of the DXY/TNX signal
(500 replicates), as E108. Also compared with buy-and-hold on Sharpe.
