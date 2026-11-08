# Keep the bots on time — free pinger (cron-job.org), about 10 minutes, once

GitHub's own scheduler skips most runs. cron-job.org (free) will start each bot exactly on time by calling GitHub.
GitHub's own schedule stays on as a backup; a double run does no harm (the bots skip candles they've already handled).

## Step 1 — a GitHub key that can only start these bots
1. github.com → your picture → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
   → **Generate new token**.
2. Name: `omega-pinger` · Expiration: 1 year · **Repository access: Only select repositories → Aura**.
3. **Permissions → Repository permissions → Actions: Read and write.** Leave everything else at "No access".
4. Generate and copy the token (starts with `github_pat_`). Keep it only in cron-job.org, never in chat or files.
   It can start and stop the Aura workflows and nothing else: no code, no money, no other repos.

## Step 2 — three jobs on cron-job.org
Sign up at cron-job.org (free). For each job: **Create cronjob**, then:
- **URL:** see the table · **Execution schedule:** custom, as in the table, **time zone UTC**
- **Advanced → Request method: POST**
- **Advanced → Headers** (add all three):
  - `Authorization` = `Bearer github_pat_…` (your token)
  - `Accept` = `application/vnd.github+json`
  - `X-GitHub-Api-Version` = `2022-11-28`
- **Advanced → Request body:** `{"ref":"main"}`
- Save. "Test run" should return **204** (= started).

| Job | URL | Schedule (UTC) |
|---|---|---|
| Fast scouts | `https://api.github.com/repos/BlitzDragneel/Aura/actions/workflows/omega-fast-scouts.yml/dispatches` | minutes 2, 17, 32, 47 of every hour |
| Hourly scouts | `https://api.github.com/repos/BlitzDragneel/Aura/actions/workflows/omega-scouts.yml/dispatches` | minute 17 of every hour |
| Paper bot | `https://api.github.com/repos/BlitzDragneel/Aura/actions/workflows/omega-paper-bot.yml/dispatches` | minute 7 of every hour |

(Optional, keeps the Live API awake for your phone: a 4th job, method GET, URL
`https://omega-live-api.onrender.com/health`, every 10 minutes, no headers. On Render's free plan this uses most of
the 750 free hours a month on one service, which is fine for this single service.)

## Step 3 — check
GitHub → Aura → **Actions**: runs appear every 15 minutes, marked "workflow_dispatch". Within an hour,
`STATUS.txt`, `scouts/SCOUTS.md` and `fast_scouts/SCOUTS.md` on the **bot-state** branch show fresh times.
If runs stop: cron-job.org → the job's history shows the reason (a 401 means the token expired; make a new one).
