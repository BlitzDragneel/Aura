# OMEGA apps: security findings (for the app owners; not edited by the security bot)

Scope: `omega/apps/omega-v6_5-47.html` (v6.5.105, 34,920 lines, 4.5 MB) and `omega/apps/omega-prime.html`.
Method: targeted review, not a line-by-line audit of all 376 `innerHTML` sinks. I traced each external input (fetches,
proxies, backup and CSV import, AI replies) to where it is rendered, and grepped for eval, `new Function`, postMessage,
service worker, CSP, SRI and outbound hosts. Line numbers are for the current repo copy.

**Overall:** the original app is already defensive in most places. It escapes fetched text (`esc`/`escapeHtml`),
allowlists links (`safeUrl`, line 6131), never sends a keyed URL through the CORS proxy (line 14332), strips keys from
backups (lines 9706–9725), and has no eval, `new Function` or cross-window postMessage. Prime only talks to
`fapi.binance.com` and escapes everything it renders. The issues below are mostly hardening.

## Medium

### A1. Backups carry the WhatsApp number and the alert webhook URL (standing rule 4)
- `creed_alert_v1` (line 16184) holds `alertCfg.number`, the WhatsApp number (line 16221). Backups include every
  `creed_*` key (line 9718). **A phone number ends up in every backup file.**
- `omega_alert_url` (line 12770) holds the alert webhook. A Discord webhook URL contains its secret token. It is not
  caught by `isSecretKey` (line 9711) because the name ends in `_url`.

Fix (in `buildBackup`, after the `secrets` list is built, around line 9716):
```js
// v6.5.106: never put the WhatsApp number or a webhook URL in a backup
var PERSONAL = { omega_alert_url:1 };
// in the Object.keys(keys).forEach(...) loop, before bundle.data[k]=v:
if(PERSONAL[k]){ bundle.excluded.push(k); return; }
if(k === 'creed_alert_v1'){ try{ var ac = JSON.parse(v); if(ac && ac.number){ delete ac.number; v = JSON.stringify(ac); } }catch(e){} }
```
Also extend `isSecretKey` to `/(^|_)(key|token|secret|apikey|password|pass|webhook|url)$/i`, or list the keys by name.
Add a test in the kit: back up with a number and a webhook set, then assert that `hasPhone(file)` (nophone.js) is false
and that the file does not contain `discord.com/api/webhooks`.

### A2. A crafted backup can change the alert webhook or the RSS proxy (data goes to a stranger)
`restoreAllData` (line 9771) writes every `omega*`/`creed_*` key from the file. That includes `omega_alert_url`, secret
keys (`omega_claude_key` and the rest, if present in the file), `omega_custom_feeds`, and settings that hold the RSS
proxy. If Maro is sent a "backup" and imports it, every later alert (signals and trades) goes to the sender's webhook.
Fix, in `restoreAllData` after `keys` is computed:
```js
keys = keys.filter(function(k){ return !isSecretKey(k) && k !== 'omega_alert_url'; });   // never take keys or a webhook from a file
```
After the restore, show any URL-valued settings that changed (webhook, RSS proxy, custom feeds) and ask her to confirm them.

### A3. The chart library loads from a CDN without Subresource Integrity
Line 14: `<script src="https://unpkg.com/lightweight-charts@5.0.2/dist/lightweight-charts.standalone.production.js">`.
If unpkg (or the npm package) is compromised, that script runs with full access to localStorage, where the Claude,
Twelve Data and CryptoPanic keys are kept. I fetched the file on 5 Nov 2026 from unpkg and from jsDelivr and got the same
hash from both:
```html
<script src="https://unpkg.com/lightweight-charts@5.0.2/dist/lightweight-charts.standalone.production.js"
        integrity="sha384-NWTHVp/2n1SsvFhrMDcsRGYu71Cla1UgKADA6+ErV2oklVI3DLjsnXK92nl4Cm+J"
        crossorigin="anonymous"></script>
```
Better still, inline the file (176 KB) so the charts also work offline. The app already notes that they do not.
TradingView's `tv.js` (lines 9633, 17329) is injected at runtime and versionless, so SRI cannot pin it. Load it only after
a user action (it may already work this way) and treat it as fully trusted code.

### A4. No Content-Security-Policy
There is no CSP, so any XSS (or a compromised CDN script) can send localStorage anywhere. The app relies on inline
scripts, so `script-src` needs `'unsafe-inline'`. A `connect-src` allowlist still limits where data can be sent.
Proposed `<meta>` (first element in `<head>`):
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://s3.tradingview.com;
 style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com data:; img-src 'self' data: blob: https:;
 frame-src https://*.tradingview.com; object-src 'none'; base-uri 'none'; form-action 'none';
 connect-src 'self' http://127.0.0.1:8787 http://localhost:8787 https://fapi.binance.com https://api.binance.com https://data-api.binance.vision
 https://data.binance.vision https://api.twelvedata.com https://www.okx.com https://api.bybit.com https://api.kraken.com https://api.exchange.coinbase.com
 https://www.deribit.com https://api.hyperliquid.xyz https://nfs.faireconomy.media https://corsproxy.io https://api.rss2json.com https://cryptopanic.com
 https://api.anthropic.com https://news.google.com https://www.coindesk.com https://stats.bis.org https://discord.com https://*.duckdns.org">
```
A user-typed webhook or recorder address outside this list will be blocked. Either add her hosts, or ship it as
`Content-Security-Policy-Report-Only` first. Run the full s49…s105 suites and the 28-page crawl with the CSP in place
before shipping.

### A5. Prices fetched through a third-party CORS proxy can be faked
`fetchJSON` (line 14324) and the economic calendar (line 26591) fall back to `https://corsproxy.io`. Keyed URLs never go
through it, which is good. But the proxy can change any unkeyed response, such as candles or the calendar. In a trading
app, a faked price or a missing high-impact event is an integrity risk, not just a privacy one.
Recommendation: when `lastFetchVia === 'proxy'`, mark the data as unverified in the UI (partly done). Never let proxied
candles feed a trade ticket, the risk stop or the Autopilot. Prefer the local Live API (`omega/live_api`, 127.0.0.1:8787)
as the fallback when it is running.

## Low

- **A6. Unescaped journal fallback renderer.** Line 5272 (`renderJournal` fallback) writes `e.source`, `e.symbol`,
  `e.direction` and `e.result` raw into `innerHTML`. These values come from CSV import (line 5406) and backup restore.
  Today the Journal Pro renderer (line 10563, escaped) replaces it, so the sink is dormant. Wrap the fields in an escape
  function or delete the fallback.
- **A7. Two `esc()` variants do not escape `"`** (lines 10707 and 13356). Inside double-quoted attributes
  (`title="'+esc(psy)+'"` at 13118, `value="'+esc(x)+'"` at 11485) a `"` breaks out of the attribute. The current inputs
  are internal (catalog, generated text). Use the 4-character version from line 9857 everywhere. `'` is not escaped in any
  variant, so never build single-quoted attributes from data.
- **A8. Error text in innerHTML.** Line 5920 joins `r.reason` (an error from the data-source test) into `innerHTML`.
  Use `textContent` or `esc()`.
- **A9. Keys in localStorage.** The Claude key, Twelve Data key and CryptoPanic token live in localStorage (by design:
  this is a single-file PWA with no backend). Any XSS reads them. Mitigations: A3 and A4, and keep backups key-free
  (already done). The Claude key is sent straight from the browser (`anthropic-dangerous-direct-browser-access`,
  line 5183). Use a key with a low monthly spend limit set in the Anthropic console.
- **A10. Service worker.** Line 5944 registers `./service-worker.js`, which is not in the repo. Wherever the app is
  hosted, that file must be served from the same origin over HTTPS, cache only same-origin GETs, and never cache API
  responses or the `?apikey=` URLs. Otherwise, remove the registration.
- **A11. WhatsApp share.** `wa.me` links (lines 16222, 22036) put signal text in a URL that WhatsApp/Meta receives.
  This is the expected behavior, but it is an outbound data path. The number typed there is A1.

## Not found (checked)
- No eval, `new Function`, `setTimeout(string)`, `document.write` or `srcdoc`, and no `message` event listener (the two
  `postMessage` calls are `MessageChannel` yields).
- No hard-coded keys remain. The Twelve Data key that was at about line 29759 has been removed (now a comment). The
  `BROWSERKEY99887766` in `kits/original/s84_test.js` is a test fixture. `nophone.js` found no phone number in any of
  the 621 tracked and untracked files.
- Prime: one outbound host (`fapi.binance.com`), escaped rendering, no imports.
