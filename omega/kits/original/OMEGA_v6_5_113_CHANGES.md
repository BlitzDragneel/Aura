# OMEGA v6.5.113 — "Heaven" theme (new default) and the About OMEGA page
- **Heaven**: soft white/pearl surfaces over a faint cool-blue/lavender wash, deep slate text #1A2332 (15.8:1 on white),
  secondary #586274 (6.2:1), one accent — deep soft gold #8A6A1E (5.1:1) — calm green #0B7D55 / red #B42F45; rounded cards with
  soft shadows; sentence-case headings in Inter/system UI (no new font or CDN); banner glows, the "flow" pills and neon text
  shadows off; frosted header and bottom bar; light lightweight-charts (createChart wrapped, existing charts repainted on theme
  change); light first-load mark. Applied before first paint by a tiny inline script (no dark flash).
- Theme list: Heaven (default), Neon Glow, Dark (classic), and every other theme. One-time switch `omega_heaven113`: neonglow or
  dark → heaven once; any other chosen theme kept; Neon Glow/Dark can be chosen again and stick.
- **About OMEGA** (`page-about`; menu/More and a button at the top of Settings): 10 dropdowns, closed by default — what OMEGA is,
  every page, signals and grades with the measured evidence (handover §3, edges/RESULTS.md: climax A 324 coins; panic B E22/E25
  t 4.54 and its caveats; C watch list E37/E38/E40/E81 and the Daily Plan; CREED 49% vs 50%, −0.118R/−0.100R/−0.118R), the bots
  (in-app, 24/7 cloud, laptop Station, scouts), data sources, Live API and token, Academy, risk and leverage (2× already
  liquidates; 20× ~1 USDT; 40× ~60% of trades), privacy and backups, the progress board.
- s108 updated for the new default (Neon Glow still offered). Test `s113_test.js` (with v6.5.114 also checks the declutter).
