# OMEGA v6.5.110 — Academy page and first-run tutorial (contract: omega/academy/CONTRACT.md)
- **Academy** (phone bar and menu "Learn"): course title, overall and per-module progress, "Continue", lesson list with free /
  preview / 🔒 marks; the reader shows the disclaimer, the lesson (safe markdown), key points, a quiz with explanations, "Mark
  lesson complete" and previous/next. Progress: localStorage `omega_academy_v1` = { done, quiz, last, token }.
- **Safe markdown:** every character is HTML-escaped first, then only headings, bold/italic, inline code, code blocks, lists,
  tables, quotes, rules and https links become tags. No raw HTML from content; `javascript:` links stay text.
- **Server** (`{server}` = Settings > Data & Keys > Academy server, default https://omega-live-api.onrender.com; https only, or
  http://localhost): catalog from `GET /academy/catalog`; premium lessons from `GET /academy/lesson/{id}` with header
  `X-Academy-Token`; "I have a license key" → `POST /academy/unlock {license_key}` → token kept. Errors show the server's reason.
  Offline or before the server answers, the FREE lessons built into the app are shown. Premium text is never embedded
  (patch110 asserts it).
- **Unlock button:** opens `pricing.json` checkout_url (https only); while empty: "Coming soon — launch price $49, regular $97".
- **Tutorial:** 6 steps (Home verdict, a chart, mark-up, CREED and OMEGA signals read honestly, Risk Guard and bots, the
  Academy). A card at the top of the page, not a blocking overlay; shown once on first run (`omega_tutorial_v1`), skippable,
  "Show me" opens the step's page; reopen from Settings > Data & Keys or the Academy page.
- **Refresh the embedded free lessons** after course.json or pricing.json changes (re-runnable; only the data block and the
  build time change):
  `cd omega/kits/original && python3 patch110.py ../../apps/omega-v6_5-47.html ../../apps/omega-v6_5-47.html`
  (optional 3rd/4th arguments: another course.json / pricing.json).
- CREED's engine byte-identical (s102/s109 with PREV = v6.5.108). Build: `python3 patch110.py <v6.5.109> <out>`. Test: s110 (25/25,
  server mocked with route() in the contract's shapes). Built with 19 free lessons from course.json as it stood at 11:28 UTC
  (the course is still being written: refresh with the command above). Size 2,621,277 bytes. Phone shots: audits/ux/shots/v110/.
