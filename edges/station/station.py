"""OMEGA Station — runs every OMEGA bot on one laptop, on time, 24/7.

Jobs (UTC clock):
  paper/testnet bot   minutes 07, 22, 37, 52   python -m edges.bots run --mode <mode> --once
  fast scouts         minutes 02, 17, 32, 47   python -m edges.scouts.live <home>/fast_scouts --fast
  hourly scouts       minute 17                python -m edges.scouts.live <home>/scouts
  live data API       always on                http://127.0.0.1:8787  (omega/live_api)
  update              daily 06:41              git pull (only in paper/testnet mode; never while live)
Records: <home>/  (STATION.md = latest summary; bots/ = paper bot state & log; scouts/, fast_scouts/ = scoreboards)
Keeps the computer awake while running (Windows: SetThreadExecutionState; macOS: caffeinate).
Stop: close the window or Ctrl+C. Kill switch for orders: edges\\bots\\KILL_all.bat (or python -m edges.bots kill).
Config: <home>/station.json  {"mode": "paper"|"testnet", "auto_update": true, "api": true}
        Live trading is NOT started by the Station: it needs the bot's own live checklist (edges/bots/README.md).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOME = Path(os.environ.get("OMEGA_STATION_HOME") or (Path(os.environ.get("APPDATA") or Path.home()) / "OMEGA-Station"))
PY = sys.executable
DEFAULT = {"mode": "paper", "auto_update": True, "api": True}


def log(msg):
    line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC  {msg}"
    print(line, flush=True)
    with open(HOME / "station.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def config():
    f = HOME / "station.json"
    if not f.exists():
        f.write_text(json.dumps(DEFAULT, indent=1))
    c = {**DEFAULT, **json.loads(f.read_text())}
    if c["mode"] not in ("paper", "testnet"):
        log(f"mode {c['mode']!r} is not allowed in the Station; using paper (live needs the bot's own checklist)")
        c["mode"] = "paper"
    return c


def keep_awake():
    if platform.system() == "Windows":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        return None
    if platform.system() == "Darwin":
        return subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
    return None


def run(name, args, env=None, timeout=900):
    t0 = time.time()
    e = {**os.environ, "PYTHONWARNINGS": "ignore", **(env or {})}
    try:
        p = subprocess.run([PY, *args], cwd=REPO, env=e, capture_output=True, text=True, timeout=timeout)
        ok = p.returncode == 0
        tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
        log(f"{name}: {'ok' if ok else 'FAILED (' + str(p.returncode) + ')'} in {time.time() - t0:.0f}s"
            + ("" if ok else " | " + " | ".join(tail)))
        (HOME / f"last_{name}.txt").write_text(p.stdout[-20000:] + "\n" + p.stderr[-5000:], encoding="utf-8")
        return ok
    except subprocess.TimeoutExpired:
        log(f"{name}: timed out after {timeout}s")
        return False


def start_api():
    e = {**os.environ, "OMEGA_API_HOST": "127.0.0.1", "OMEGA_API_PORT": "8787", "OMEGA_REPO": str(REPO)}
    out = open(HOME / "api.log", "a", encoding="utf-8")
    p = subprocess.Popen([PY, "-m", "omega_live"], cwd=REPO / "omega" / "live_api", env=e, stdout=out, stderr=out)
    log(f"live data API started on http://127.0.0.1:8787 (pid {p.pid})")
    return p


def summary(c):
    parts = [f"# OMEGA Station — {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC", "",
             f"Mode: **{c['mode']}** · computer: {platform.node()} · code: {git_rev()}", ""]
    for title, path in (("Paper bot (positions, orders, recent actions)", HOME / "last_status.txt"), ("Hourly scouts", HOME / "scouts" / "SCOUTS.md"),
                        ("Fast scouts", HOME / "fast_scouts" / "SCOUTS.md")):
        if path.exists():
            txt = path.read_text(encoding="utf-8", errors="ignore")
            parts += [f"## {title}", "", txt[:3000], ""]
    (HOME / "STATION.md").write_text("\n".join(parts), encoding="utf-8")


def git_rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip() or "?"
    except OSError:
        return "?"


def update(c):
    if not c.get("auto_update") or c["mode"] not in ("paper", "testnet"):
        return
    try:
        p = subprocess.run(["git", "pull", "--ff-only"], cwd=REPO, capture_output=True, text=True, timeout=120)
        log("update: " + (p.stdout.strip().splitlines() or ["(no output)"])[-1])
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"update skipped: {e}")


def main():
    HOME.mkdir(parents=True, exist_ok=True)
    (HOME / "bots").mkdir(exist_ok=True)
    c = config()
    log(f"OMEGA Station starting — mode {c['mode']}, records in {HOME}")
    awake = keep_awake()
    api = start_api() if c.get("api") else None
    bot_env = {"OMEGA_BOTS_HOME": str(HOME / "bots")}
    done = set()
    try:
        while True:
            now = dt.datetime.now(dt.timezone.utc)
            m, key = now.minute, now.strftime("%Y%m%d%H%M")
            c = config()
            jobs = []
            if m in (7, 22, 37, 52):
                jobs.append(("bot", ["-m", "edges.bots", "run", "--mode", c["mode"], "--once"], bot_env))
            if m in (2, 17, 32, 47):
                jobs.append(("fast_scouts", ["-m", "edges.scouts.live", str(HOME / "fast_scouts"), "--fast"], None))
            if m == 17:
                jobs.append(("scouts", ["-m", "edges.scouts.live", str(HOME / "scouts")], None))
            if now.hour == 6 and m == 41:
                jobs.append(("update", None, None))
            for name, args, env in jobs:
                if (name, key) in done:
                    continue
                done.add((name, key))
                if name == "update":
                    update(c)
                else:
                    run(name, args, env)
                    if name == "bot":
                        run("status", ["-m", "edges.bots", "status"], bot_env, timeout=120)
                summary(c)
            if api is not None and api.poll() is not None and c.get("api"):
                log("live data API stopped; restarting")
                api = start_api()
            if len(done) > 500:
                done = {d for d in done if d[1] >= key[:10]}
            time.sleep(20)
    except KeyboardInterrupt:
        log("OMEGA Station stopped by the user")
    finally:
        if api is not None:
            api.terminate()
        if awake is not None:
            awake.terminate()


if __name__ == "__main__":
    main()
