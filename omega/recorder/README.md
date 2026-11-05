# OMEGA Recorder 1.0.1

A small FastAPI service that keeps a record of the Binance USDT-M perpetual market for OMEGA's research and forward paper
records. **Paper only:** it uses public endpoints, holds no API keys and places no orders.

## What it records
| Data | How often | Why record it |
|---|---|---|
| Symbols and their status, with every listing and delisting | 6 h | Survivorship: delisted coins are kept, with the date they went |
| Hourly candles, every perpetual | hourly | H1/H3 and all hourly research |
| 1-minute candles, the 40 most-traded | 5 min | CPI and other event studies |
| Mark price, index price, current funding, every perpetual | 5 min | Funding and basis |
| Funding history | 8 h | Funding harvest, trade costs |
| Open interest, long/short ratios (accounts, top traders, taker buy/sell), top 40 | hourly (5-min points) | Binance keeps only ~30 days of these |
| Liquidations (live stream) | continuous | Binance sends at most one per coin per second: a sample, not every one |
| Order-book summary, top 10 (spread, depth within 0.5% and 2%) | 1 min | Not kept anywhere by Binance |
| Archive backfill from data.binance.vision: hourly candles and funding since 2020, **delisted coins included** | on request | PLAN E25 |

## What it serves
- `/health`: every job's last success and last error, row counts, coins whose hourly candles are behind. Check this first.
- `/symbols`, `/listings`, `/candles`, `/funding`, `/premium`, `/oi`, `/ratios`, `/depth`, `/liquidations`.
- `/panic`: H3's breadth, the share of coins in their own bottom-10% 24-hour fall, hour by hour.
- `/signals`: the H1/H3 forward **paper** record since `OMEGA_FORWARD_START`, recomputed from the stored candles every
  time (so a restart cannot corrupt it). Grade B: passed a fair test, unconfirmed.
- `/events` (GET; POST/DELETE need the token): CPI, FOMC and other dates, entered from official sources only.
- `/export/history`: hourly candles as `omega_history_recorder_YYYY_MM_DD_json.gz`, in the format the research loader
  already reads, with each coin's status. `/export/table/<name>`: any other table as gzipped JSON lines.
- `/docs`: the interactive API page.

## Setup (recommended: a small always-on server, ~4–6 USD a month, region in Europe or Asia; Binance blocks US addresses)
1. Ubuntu server: `sudo apt install python3-venv caddy`, copy this folder to `/opt/omega-recorder`, then
   `python3 -m venv venv && venv/bin/pip install -r requirements.txt`.
2. `venv/bin/python -m omega_recorder selfcheck`: every line should say `ok`. If not, stop there and send the output.
3. Make a long random token: `python3 -c "import secrets;print(secrets.token_urlsafe(32))"`. Put `OMEGA_TOKEN=<it>` in
   `/etc/omega-recorder.env` (chmod 600). Never put it in a file you share or a backup.
4. Install `omega-recorder.service`, then `sudo systemctl enable --now omega-recorder`.
5. HTTPS: point a free DuckDNS name at the server and use the `Caddyfile` (Caddy fetches the certificate itself).
6. Backfill (hours; resumable, already-fetched files are skipped):
   `curl -X POST -H "X-Token: <token>" https://<name>/admin/backfill`
7. Restrict who may call it from a browser: `OMEGA_CORS=https://<where the app is served from>`.

Windows instead: double-click `run_windows.bat`. It records only while the window is open and the PC is awake; candles and
funding can be backfilled later, but open interest, ratios, liquidations and order books missed are lost.

## Settings (environment variables)
`OMEGA_DB`, `OMEGA_HOST` (127.0.0.1), `OMEGA_PORT` (8000), `OMEGA_TOKEN`, `OMEGA_CORS` (*), `OMEGA_WATCH_N` (40),
`OMEGA_DEPTH_N` (10), `OMEGA_BACKFILL_FROM` (2020-01), `OMEGA_FORWARD_START` (2026-11-01), `OMEGA_JOBS` (1).

## Tests: `python -m pytest -q tests` (14 tests)
- H1 and H3 give **exactly** the research engine's trades (107 and 84 on synthetic data with gaps), against verbatim copies
  of `e22_lib.py`/`e21_lib.py` (`tests/REFERENCE_MD5`); breadth identical; no look-ahead when replayed hour by hour; live mode
  reports pending and open trades without changing closed ones.
- Exports read back through the research decoder (`load.py dec_market`) to 6 significant digits, with exact times.
- Archive: listing pages, CSV with and without header, microsecond timestamps, delisted symbols kept, re-runs fetch nothing.
- Jobs against a mocked Binance: delistings (status change and disappearance) recorded with time; the forming candle is not
  stored; rate limit 429 backs off without calling Binance again.
- API: every endpoint, the token on writes, the delisted coin in the export.

## Delisted coins in the archive
After a perpetual stops trading, Binance's archive keeps publishing flat, zero-volume candles at its last price (WAVES: last
trade June 2024, flat candles to October 2026). The recorder stores them as they are, but treats every volume-0 candle as
missing in `/panic`, `/signals` and `/export/history`, and the export lists each coin's last traded hour.

## Not verified
**Never run against the real Binance:** the build sandbox cannot reach it. The endpoint shapes come from Binance's public
documentation as I know it. Run `selfcheck` first; the archive listing address (`OMEGA_ARCHIVE_LIST`) is the one most likely to
need a change. Not run on a real server or phone.
