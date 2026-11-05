# OMEGA v6.5.82 — audit, fixes and trim (19 Oct 2026)

Built from v6.5.81 by `patch82.py`. Delivered as `omega-v6_5-47.html`. The file is 100 KB smaller.

## Audit
Every one of the 24 pages was opened in Chromium at phone width, twice:
- offline;
- with a simulated Binance feeding data.

Checked on each page:
- page errors and console errors;
- any reading showing NaN, "undefined", Infinity or "[object Object]";
- sideways scrolling;
- syntax of every script block;
- duplicate element ids;
- the phone-number guard.

**Result: no errors, no broken readings, no overflow, before and after the changes.** The text of the research-facing
pages was read against the research files. Outdated statements were found and fixed (below).

## Removed (finished or failed; the code stays in the build kit)
- **Capitulation watch:** failed its final test, and only recorded.
- **Seven research downloads whose data has been collected and used:**
  - the futures data;
  - the round 14 final test;
  - CREED's 15-minute data;
  - Bybit funding;
  - the untouched coins;
  - forex history;
  - (the older-history, fresh-coin and new-coin buttons; their coin lists stay because the data stores read them).
- **The funding carry card and its Autopilot job:** it failed both untouched tests. Its data helpers stay, because the
  harvest uses them.

The two exports still in use stay: the research report and the price history.

## Corrected
- **The research record's heading** now names what passed: the funding harvest (rounds 7, 8 and 10, and with
  dip-buying in round 12) and the climax reversal (round 16).
- **The carry row** no longer calls carry "a frozen paper strategy at the top of this page". It failed rounds 5 and 7.
- **The harvest card title and its Brain note** said "the one idea that passed … three times". They now say rounds 7,
  8 and 10.
- **The Positioning Desk** no longer says the harvest is the only thing that passed.
- **The OMEGA Strategy panel** said "There is no OMEGA strategy yet". It now says the phone's own Research Lab has not
  produced a rule, and points to the two rules that passed.
- **Built-in knowledge:** rounds 2–6 had shifted labels. They now match the research record:
  - sweep fade = round 2;
  - with-the-sweep = round 3;
  - carry = round 4;
  - buy-and-hold comparison = round 6.

## Added
**OMEGA Signals** now shows the climax reversal's signals first, above the Research Lab's own (which has none).

## Checks
- **s82 7/7.**
- **Every suite:**
  - s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21;
  - s71 11/11 (now checks that the round-14 downloads were removed on purpose);
  - s73 7/7, s77 27/27, s78 13/13, s79 9/9, s80 4/4, s81 3/3.
  - s72, which tested the removed capitulation watch, is retired.
- 104 script blocks pass `node --check`. No duplicate ids. Phone guard clean.
- Not run on a real phone.
