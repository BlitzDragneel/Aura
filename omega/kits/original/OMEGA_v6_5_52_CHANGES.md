# OMEGA v6.5.52 — the outside research, recorded in the app

Builds on v6.5.51 (= v6.5.50's history export plus a plain message when a copy has no history). Delivered under the
file name `omega-v6_5-47.html` on purpose: the browser keeps each copy's data by file name, and her data lives with
that name. Keep this name for every future build.

## New
- **Outside research record** (OMEGA Strategy page, the research report's `outsideResearch`, one Brain note): the
  18 Oct study of her exported history: 25 crypto markets, hourly, Oct 2023 to 17 Oct 2026; 87 variants in 8
  families; plan written before the data was seen (`PLAN.md`); 6 candidates chosen on design data, all failed on
  Apr–Dec 2025; the 2 that stayed positive lost in 2026. No edge survived, so nothing was added as a strategy.

## Checked
s48 (6), s49 (11), s50 (4) checks pass on this build; 21 pages crawled in Chromium, no errors, no overflow.

## Research files (`omega-research-2026-10-18.tar.gz`)
`PLAN.md` (with the addendum written before the holdout), `engine.py`, `families.py`, `design.py`, `validate.py`,
`holdout.py`, outputs `design_out.txt`, `validation.json`, `holdout.json`, `research_record.json`, and
`omega_history.py` (decoder). The price file itself is not included.
