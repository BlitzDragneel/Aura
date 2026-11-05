# OMEGA v6.5.66 — one futures file on its own

Built from v6.5.65 by patch66.py. Delivered as omega-v6_5-47.html (same file name, so stored data carries over).

## Why
A phone can quietly drop a download that the app hands it (for example, at a "this site wants to download several
files" prompt). The app can't see this. In v6.5.65, once all 6 futures files were marked saved, the only option was the
big button, and it silently started the whole 75-minute download over.

## What changed
- **Strategy page → futures download:** a new row, "One file on its own", with six buttons: Fresh coins 1, Fresh coins 2,
  New coins 1, New coins 2, New coins 3, BTC/ETH positioning.
  - Each button downloads only that file and never resets the others.
  - ✓ means the app handed that file to the phone before.
  - The big button works as Stop while a single file is downloading.
- **Save again:** every file made during this visit stays behind a link ("Not in your Downloads? Tap a name to save it
  again"). A tap always saves, because the phone treats it as your own action. The links last until the page is closed.
- **The big button says what it does:** once all 6 are marked saved, it reads "Download all 6 futures files again"
  (it used to read "Download the rest…").
- **Self-check:** the accessibility check now runs the accessibility pass itself if page setup hasn't reached it yet. That
  case is a busy phone during a long download, which caused the yellow "a11y pass has not run yet" warning. The pass
  also now runs even if an earlier setup step fails.

## Not changed
Strategies, CREED, the Brain, the Autopilot, the harvest and the desk are untouched. No research results are in this
build; they come in the next update.

## Checks
- **Browser test** (mocked Binance, all six marked saved):
  - one file on its own downloads only that file;
  - the save-again link saves the same bytes;
  - Stop during a single file saves nothing and changes nothing;
  - the metrics file works on its own;
  - the ticks persist after reload;
  - the accessibility self-check passes;
  - no page errors.
- **Regression tests:** s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11.
- **Phone-number guard:** clean.
- **Layout:** no sideways scroll at phone width.
