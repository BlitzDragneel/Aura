# The Scroll

The whole Bible, offline — an installable web app (PWA) in a single HTML file.

## Files
- `index.html` — the entire app and all its texts
- `sw.js` — service worker (offline)
- `manifest.webmanifest`, `icon-*.png`, `apple-touch-icon.png`, `favicon.svg`, `logo.svg` — install metadata and icons
- `render.yaml` — Render Blueprint (static site + security headers)

## Deploy on Render
1. Push this folder to a GitHub repository.
2. In Render: **New → Blueprint**, pick the repository. Render reads `render.yaml` and publishes the site.

## Install
- **Android / Chrome / Edge (phone or computer):** open the site, then browser menu → **Install app**.
- **iPhone / iPad:** open in Safari → **Share** → **Add to Home Screen**.
- **Mac Safari:** File → **Add to Dock**.

It must be served over https to install; opened as a file it still works fully, just without install.

## Before publishing (optional)
- `HELP_CONTACT` in `index.html`: set an email to add a "Send to the developer" button to Help.
- `SUPPORT` in `index.html`: gift / sponsor links.
