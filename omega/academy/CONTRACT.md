# OMEGA Academy — shared contract (app ⇄ course ⇄ server)

## Product
- **Name:** OMEGA Academy — *Trade with evidence* (working title; the owner can rename).
- **Free tier:** Module 1 and Module 2 complete, plus the first lesson of every other module (a preview).
- **Full course:** one-time purchase, lifetime access + updates. **Launch price US$49, regular price US$97**
  (set in `omega/academy/pricing.json`; the real price is whatever the owner sets on the checkout product).
- **Checkout:** Gumroad product with license keys enabled (the owner creates it; its permalink and product id go into
  pricing.json and the server's env `ACADEMY_GUMROAD_PRODUCT_ID`). Gumroad sends the buyer a license key by email.

## Course file — `omega/academy/course.json`
```json
{"title": "...", "version": "1.0", "updated": "2026-11-08",
 "disclaimer": "plain-language risk/education disclaimer shown before any lesson",
 "modules": [
   {"id": "m01", "title": "...", "summary": "...", "free": true,
    "lessons": [
      {"id": "m01-l01", "title": "...", "minutes": 8, "free": true,
       "body_md": "Markdown. Headings, lists, tables, worked examples with numbers. No images required;
                   ASCII/markdown diagrams allowed. Exercises reference OMEGA pages (e.g. 'open Analysis…').",
       "key_points": ["...", "..."],
       "quiz": [{"q": "...", "options": ["a", "b", "c", "d"], "answer": 1, "why": "..."}]}
    ]}
 ]}
```
`free` on a lesson overrides the module (preview lessons). Lesson ids are stable (progress is stored by id).

## Server (OMEGA Live API, Render) — written by the lead
- `GET /academy/catalog` (public): course title, disclaimer, modules and lesson titles/minutes/free flags, and the
  full body of every FREE lesson; premium lessons have no body.
- `POST /academy/unlock` body `{"license_key": "..."}` → verifies with Gumroad (or the server's own key list
  `ACADEMY_KEYS`), returns `{"ok": true, "token": "<signed, 1 year>"}`.
- `GET /academy/lesson/{id}` with header `X-Academy-Token: <token>` → the full lesson (premium needs a valid token).
Premium text never ships inside the HTML app.

## App (original OMEGA) — Academy page
Reads `/academy/catalog` (server URL from Settings, default `https://omega-live-api.onrender.com`), shows modules,
progress (localStorage `omega_academy_v1`: completed lesson ids, quiz scores, token), renders markdown safely
(escape first; no raw HTML), quizzes, "Unlock the full course" → checkout URL from the catalog's pricing block,
"I have a license key" → /academy/unlock. Offline: shows a bundled copy of the free lessons.

## Honesty rules for the course (binding)
No profit promises, no "guaranteed", no income claims, no leverage hype. Teach what the evidence in this repository
shows (edges/RESULTS.md, omega/OMEGA_HANDOVER_2026-11-02.md §3): most rules fail fair tests; CREED measured at about
a coin flip after costs; the panic bounce and climax passed but are fading; 20×/40× liquidates. The course's selling
point is that it teaches how to trade *and how to test before trusting*, with risk management first.
