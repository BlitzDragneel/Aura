# Selling the OMEGA Academy — setup (about 20 minutes, once)

Everything technical is already built: the free lessons show in the app, premium lessons live only on your server
(https://omega-live-api.onrender.com) and open only with a license key from a real purchase. What's left is yours to do,
because it involves your money, your name and your tax details.

## 1. Create the product on Gumroad (handles payment, VAT, receipts and license keys)
1. Sign up at gumroad.com and connect a payout method (bank or PayPal; check it works from Trinidad & Tobago).
2. New product → type **Digital product** → name it (e.g. *OMEGA Academy — Trade with evidence*).
3. Price: **$97**, with a launch **discount code** that takes it to **$49** (or set $49 now and raise it later;
   both numbers live in `omega/academy/pricing.json`).
4. Content tab → tick **Generate a unique license key per sale**. Add a short welcome note: "Open OMEGA → Academy →
   'I have a license key' and paste the key from this email."
5. Publish. Copy two things:
   - the product **link** (https://yourname.gumroad.com/l/…)
   - the **product ID** (product edit page → Content → license key section shows it; it looks like `aBcD12…==`).

## 2. Tell OMEGA about it (send me the two values, or do it yourself)
- Render → service **omega-live-api** → Environment → add `ACADEMY_GUMROAD_PRODUCT_ID` = the product ID → Save
  (it redeploys by itself).
- `omega/academy/pricing.json` → put the product link in `checkout_url` (I'll rebuild the app so the "Unlock" button
  goes there).
- Gift or test keys without a sale: add them to `ACADEMY_KEYS` on Render, separated by commas.

## 3. Test it before telling anyone
1. On Gumroad, make a 100%-off discount code and "buy" the course yourself → you get a license key by email.
2. In OMEGA → Academy → "I have a license key" → paste → the premium lessons open.
3. Refund that test sale on Gumroad → the key stops unlocking on new devices.

## 4. Things only you can decide
- **Legal wording:** the course carries an education-only, not-financial-advice disclaimer. Selling trading education in
  Trinidad & Tobago may touch securities rules (TTSEC); a short check with a local adviser is worth it before marketing.
- **Refunds:** a clear policy (e.g. 14 days, no questions) builds trust and reduces chargebacks.
- **Marketing claims:** never promise profits or show income screenshots. The honest selling point is the course
  itself: real trading skills, risk first, and how to test an idea before risking money.
- **Free plan limits:** Render's free plan sleeps when idle (first request after a pause takes ~1 minute). Once sales
  start, the $7/month plan keeps the server awake for buyers.
