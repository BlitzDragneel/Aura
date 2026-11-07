# OMEGA v6.5.107 — security hardening (7 Nov 2026)
Build: `python3 patch107.py <v6.5.106>.html <new>.html`; delivered as `apps/omega-v6_5-47.html`. Test: `s107_test.js` (7 checks
with `LWC=<lightweight-charts 5.0.2 standalone file>`, 6 without). Source: `audits/security/APP_FINDINGS.md` A1–A4.
No rule, engine or research text changed; **CREED's engine is byte-identical** (s102 with `PREV`).

1. **Backups (A1).** The alert webhook (`omega_alert_url`; a Discord webhook URL contains its secret) and the WhatsApp number
   inside `creed_alert_v1` are no longer written into backup files; any Discord/Slack webhook URL inside another store is cut
   out too. The status line names what was left out. The storage card's fallback backup skips the same stores.
2. **Restore (A2).** A backup file can no longer set API keys or the alert webhook (a crafted "backup" could have sent every
   alert to a stranger), and it keeps this browser's WhatsApp number. If the file changes the custom news feeds, the status
   line says so ("check them in Settings").
3. **Subresource Integrity (A3)** on the chart library (`sha384-NWTHVp…Cm+J`, checked 5 and 7 Nov 2026 from unpkg and jsDelivr,
   identical) with `crossorigin="anonymous"`. If unpkg ever serves a different file, the charts do not load (the app's
   existing "charts library not loaded" notice applies) rather than running unknown code.
4. **Content-Security-Policy (A4), the safe part:** `script-src 'self' 'unsafe-inline' https://unpkg.com
   https://s3.tradingview.com; frame-src https://*.tradingview.com https://*.tradingview-widget.com; object-src 'none';
   base-uri 'none'; form-action 'none'`. Checked: the TradingView widget still loads (tv.js has no eval; it frames
   s.tradingview.com), the 28-page crawl shows no CSP violations. **Not restricted on purpose:** `connect-src` (alerts, the
   recorder, the Live API and custom feeds go to addresses Maro types; an allowlist would silently cut them on the phone) and
   `default-src` (the in-page manifest is a `blob:` URL). So a script that runs can still send data out; the CSP stops
   foreign scripts and plugins from being loaded.

Not done here (see the security report): A5 proxied prices marked unverified, A6–A8 escaping in dormant/internal sinks.
