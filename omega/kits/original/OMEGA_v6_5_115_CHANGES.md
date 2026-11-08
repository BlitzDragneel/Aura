# OMEGA v6.5.115 — declutter on every other kept page, phone-safe badges, Install OMEGA
- **Declutter**: one closed "About this page" on Risk Guard, Market Read, Market Intelligence, Live Market Data, CREED
  Scanner, Journal, Positioning Desk, Futures, Growth & Routine, Brain, Autopilot and Settings (long intros moved there).
  Folded and closed: Intelligence (moving together, positioning, patterns, activity, markets to watch), Live data (live-data
  test, data sources), Scanner (alerts, learning, what OMEGA is missing, markets to watch), Brain (You × OMEGA, Claude
  council, evidence ledger), Autopilot (what OMEGA was taught, revalidation, log, market regimes), Growth (daily routine),
  Settings (signal webhooks and alerts, moved below the preferences). Primary content stays open (Risk Guard and Market Read
  cards, market lists, clock, Futures leverage warning, paper accounts, Brain reasoning/dashboard, Autopilot deck).
  Journal/Growth/Settings keep one title; their subtitles moved to About.
- **Phones**: "TD 1/800", clock session chips, pills and grade tags keep one line; long evidence chips are rounded blocks.
- **Install OMEGA** (Settings button and More): the browser's install prompt where offered (beforeinstallprompt), otherwise
  instructions (Android Chrome ⋮ → Install app; iPhone Safari Share → Add to Home Screen; Chrome/Edge address-bar icon).
  On http(s) the real `manifest.json` next to the app is restored as the manifest when it answers (fetch, no-store); the
  icon-less inline blob stays on file:// or when the file is missing. `installInlineManifest()` itself lives in the CREED
  module, which must stay byte-identical, so the fix runs after it instead of editing it. Browser bar colour: #F7F8FC in
  Heaven, light for Light/Paper, dark for dark themes.
- Test `HARNESS=tools node s115_test.js <build>` (22/22). Build `python3 patch115.py <v6.5.114> <out>`.
