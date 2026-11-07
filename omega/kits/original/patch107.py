"""v6.5.107: security hardening from audits/security/APP_FINDINGS.md (A1-A4). No rule, engine or research text changed;
CREED's engine is byte-identical.
 1. Backups (A1): the alert webhook (omega_alert_url; a Discord webhook URL carries its secret) and the WhatsApp number inside
    creed_alert_v1 are left out of every backup file; any Discord/Slack webhook URL found inside another store is cut out too.
    The quick fallback backup on the storage card skips the same stores.
 2. Restore (A2): a backup file can no longer set API keys or the alert webhook (a crafted "backup" could otherwise send every
    alert to a stranger), and it keeps this browser's WhatsApp number. If the file changes the custom news feeds, the status
    line says so and asks to check them in Settings.
 3. Subresource Integrity (A3) on the chart library from unpkg (sha384 checked on 5 and 7 Nov 2026 from unpkg and jsDelivr:
    identical), with crossorigin="anonymous" (unpkg sends Access-Control-Allow-Origin: *).
 4. Content-Security-Policy (A4), the part that cannot break a data feed: scripts only from the page itself, unpkg and
    TradingView (no eval), frames only from TradingView, no plugins (object-src 'none'), no <base>, no form posts.
    connect-src is deliberately NOT restricted: alerts, the recorder, the Live API and custom feeds go to addresses she types,
    and an allowlist would silently cut them on her phone. default-src is not set (the in-page manifest is a blob: URL).
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)

# 3. SRI
rep('<script src="https://unpkg.com/lightweight-charts@5.0.2/dist/lightweight-charts.standalone.production.js"></script>',
    '<script src="https://unpkg.com/lightweight-charts@5.0.2/dist/lightweight-charts.standalone.production.js" integrity="sha384-NWTHVp/2n1SsvFhrMDcsRGYu71Cla1UgKADA6+ErV2oklVI3DLjsnXK92nl4Cm+J" crossorigin="anonymous"></script>')

# 4. CSP (first thing after the charset)
rep('<meta charset="UTF-8" />\n',
    '<meta charset="UTF-8" />\n<meta http-equiv="Content-Security-Policy" content="script-src \'self\' \'unsafe-inline\' https://unpkg.com https://s3.tradingview.com; frame-src https://*.tradingview.com https://*.tradingview-widget.com; object-src \'none\'; base-uri \'none\'; form-action \'none\'">\n')

# 1. backups
rep("  function isSecretKey(k){ return !!SECRET_KEYS[k] || /(^|_)(key|token|secret|apikey|password|pass)$/i.test(k); }",
    "  function isSecretKey(k){ return !!SECRET_KEYS[k] || /(^|_)(key|token|secret|apikey|password|pass)$/i.test(k); }\n"
    "  // v6.5.107: personal stores that never go into a backup file and are never taken from one\n"
    "  var PERSONAL_KEYS = { omega_alert_url:1 }, HOOK_RE = /https?:\\/\\/(?:[a-z0-9-]+\\.)?(?:discord(?:app)?\\.com\\/api\\/webhooks|hooks\\.slack\\.com\\/services)\\/[^\\s\"'\\\\<>]+/gi;\n"
    "  function noNumber(v){ try{ var o = JSON.parse(v); if(o && typeof o === 'object' && o.number){ delete o.number; return JSON.stringify(o); } }catch(e){} return v; }")
rep("    Object.keys(keys).forEach(function(k){ var v=localStorage.getItem(k); if(v==null) return; if(isSecretKey(k)){ bundle.excluded.push(k); return; }\n"
    "      secrets.forEach(function(x){ if(v.indexOf(x) > -1) v = v.split(x).join(''); }); bundle.data[k]=v; });",
    "    Object.keys(keys).forEach(function(k){ var v=localStorage.getItem(k); if(v==null) return; if(isSecretKey(k) || PERSONAL_KEYS[k]){ bundle.excluded.push(k); return; }\n"
    "      if(k === 'creed_alert_v1'){ var v2 = noNumber(v); if(v2 !== v){ v = v2; bundle.excluded.push('creed_alert_v1 (WhatsApp number)'); } }\n"
    "      v = v.replace(HOOK_RE, '');\n"
    "      secrets.forEach(function(x){ if(v.indexOf(x) > -1) v = v.split(x).join(''); }); bundle.data[k]=v; });")
rep("(bundle.excluded.length ? 'API keys were NOT included ('+bundle.excluded.join(', ')+') — re-enter them after restoring on another device. ' : '')",
    "(bundle.excluded.length ? 'Keys, the alert webhook and your WhatsApp number were NOT included ('+bundle.excluded.join(', ')+') — re-enter them after restoring on another device. ' : '')")
rep("      for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(/(^|_)(key|token|secret|apikey|password|pass)$/i.test(k)) continue; dump[k]=localStorage.getItem(k); }",
    "      for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(/(^|_)(key|token|secret|apikey|password|pass)$/i.test(k) || k === 'omega_alert_url' || k === 'creed_alert_v1') continue; dump[k]=localStorage.getItem(k); }")

# 2. restore
rep("    var J = window.OMEGA_JOURNAL, data = {}, keys = Object.keys(bundle.data).filter(function(k){ return !NO_RESTORE[k]; });",
    "    var J = window.OMEGA_JOURNAL, data = {}, skipped = Object.keys(bundle.data).filter(function(k){ return isSecretKey(k) || PERSONAL_KEYS[k]; }),\n"
    "        keys = Object.keys(bundle.data).filter(function(k){ return !NO_RESTORE[k] && !isSecretKey(k) && !PERSONAL_KEYS[k]; });   // v6.5.107: never take keys or a webhook from a file")
rep("    var cold = (bundle.archive || []).slice();",
    "    if(data.creed_alert_v1 != null){ try{ var ia = JSON.parse(data.creed_alert_v1), ca = JSON.parse(localStorage.getItem('creed_alert_v1') || '{}'); if(ia && typeof ia === 'object'){ delete ia.number; if(ca && ca.number) ia.number = ca.number; data.creed_alert_v1 = JSON.stringify(ia); } }catch(e){} }\n"
    "    var feedsChanged = data.omega_custom_feeds != null && data.omega_custom_feeds !== localStorage.getItem('omega_custom_feeds');\n"
    "    var cold = (bundle.archive || []).slice();")
rep("          (bundle.excluded && bundle.excluded.length ? ' API keys are not in backups — re-enter them in Settings.' : '')+(opts.noReload ? '' : ' Reloading…'));",
    "          (bundle.excluded && bundle.excluded.length ? ' API keys are not in backups — re-enter them in Settings.' : '')+(skipped.length ? ' Not taken from the file: '+skipped.join(', ')+'.' : '')+(feedsChanged ? ' ⚠ The custom news feeds came from the file — check them in Settings.' : '')+(opts.noReload ? '' : ' Reloading…'));")
rep("      return { ok:true, stores:keys.length, archived:archived };",
    "      return { ok:true, stores:keys.length, archived:archived, skipped:skipped, feedsChanged:feedsChanged };")

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.106 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.106 ' + sep + ' build ' + o + ' UTC', 'v6.5.107 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.107 · build' in s and 'v6.5.106 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
