# OMEGA v6.5.68: untouched-coins download and the week's order list

Built from v6.5.67 by patch68.py. Delivered as omega-v6_5-47.html.

- **Strategy page, new button: "Download the untouched coins for the final test".**
  - Downloads every Binance spot coin against USDT that is trading now and that no research round has used (not among
    the 166).
  - Leaves out stablecoins, fiat, wrapped coins, gold tokens and leveraged tokens, and coins listed after
    31 Mar 2025.
  - Daily bars from Jan 2020, plus funding where the coin has a perpetual.
  - The rule that picks the list is fixed in PLAN12 and written into the file.
  - One file, omega-history-final3-….json.gz, with a save-again link if your phone drops it.
- **Harvest card, new: "Orders at this close".** For the 5-coin and 10-coin versions it shows:
  - which pairs to open (buy the coin and short its perpetual, with the USDT amount for your account size);
  - which to close (both legs at once);
  - which to keep.

  You place the orders; OMEGA places none. If you're starting fresh, open every pair it holds.
- **Checks:**
  - browser test of the download against a fake Binance: the rule's exclusions, a coin listed too late, a coin that
    stopped trading, a coin with no perpetual, and a file the research code reads;
  - order list rendering;
  - s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11;
  - phone-number guard clean.
