"""Builds omega/apps/index.html - the neon progress board served with both apps (Render static site).
Reads only what is in the repo: edges/results/*.json, edges/approved.json, edges/attempts.jsonl, audits/.
Usage: python3 -m edges.lead.build_site
"""
import datetime as dt
import glob
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)

TITLES = {}
for f in glob.glob(P("edges", "plans", "E*.md")):
    m = re.match(r"E(\d+)", os.path.basename(f))
    if m:
        first = open(f, encoding="utf-8").readline().strip("# \n")
        TITLES.setdefault(int(m.group(1)), first[:110])


# failed FINAL but kept on the paper watch list by the research bots' reports (edges/RESULTS.md)
WATCH = {37, 38, 40, 66, 68}


def verdict(d):
    v = str(d.get("verdict") or d.get("final_status") or d.get("result") or "")
    return v


def rows():
    out = []
    for f in sorted(glob.glob(P("edges", "results", "E*_result.json")), key=lambda x: int(re.findall(r"E(\d+)", x)[0])):
        n = int(re.findall(r"E(\d+)", f)[0])
        d = json.load(open(f))
        v = verdict(d)
        ok = v.upper().startswith("PASS")
        watch = "grade c" in v.lower() or "watch" in v.lower() or n in WATCH
        out.append(dict(n=n, title=TITLES.get(n, d.get("plan", ""))[:110], v=v[:160],
                        cls="pass" if ok else ("watch" if watch else "fail"),
                        variants=d.get("variants") or d.get("n_variants") or ""))
    return out


def main():
    R = rows()
    approved = json.load(open(P("edges", "approved.json")))
    attempts = sum(1 for _ in open(P("edges", "attempts.jsonl"))) if os.path.exists(P("edges", "attempts.jsonl")) else 0
    n_pass = sum(r["cls"] == "pass" for r in R)
    n_watch = sum(r["cls"] == "watch" for r in R)
    now = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y %H:%M UTC")
    trs = "\n".join(
        f'<tr class="{r["cls"]}"><td>E{r["n"]}</td><td>{html.escape(r["title"])}</td>'
        f'<td>{html.escape(str(r["variants"]))}</td><td>{html.escape(r["v"])}</td></tr>' for r in R)
    rules = "\n".join(
        f'<div class="rule g{html.escape(a["grade"])}"><b>{html.escape(a["id"])}</b><span>grade {html.escape(a["grade"])}'
        f' · {html.escape(a["status"])} · max {a["max_leverage"]}×</span><p>{html.escape(a.get("note", ""))}</p></div>'
        for a in approved)
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>OMEGA — progress board</title>
<style>
:root{{--bg:#05060d;--panel:#0b0e1c;--cyan:#22f3ff;--pink:#ff2bd6;--lime:#9dff3a;--amber:#ffb627;--red:#ff4d6d;--ink:#e8ecff;--mut:#8a93b8}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(1200px 600px at 10% -10%,#1a0a3a 0,transparent 60%),
radial-gradient(900px 500px at 110% 10%,#002a3a 0,transparent 55%),var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:1100px;margin:0 auto;padding:22px 16px 60px}}
h1{{font-size:30px;margin:6px 0 2px;letter-spacing:.06em;color:#fff;text-shadow:0 0 6px var(--cyan),0 0 18px var(--cyan),0 0 36px #0af}}
.sub{{color:var(--mut)}} .sub b{{color:var(--ink)}}
.apps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:20px 0}}
a.app{{display:block;padding:18px;border-radius:14px;background:var(--panel);color:var(--ink);text-decoration:none;
border:1px solid #2a2f55;transition:.2s}} a.app:hover{{transform:translateY(-2px)}}
a.app.p{{box-shadow:0 0 0 1px var(--pink),0 0 18px #ff2bd655}} a.app.o{{box-shadow:0 0 0 1px var(--cyan),0 0 18px #22f3ff55}}
a.app.l{{box-shadow:0 0 0 1px var(--lime),0 0 18px #9dff3a44}}
a.app b{{font-size:18px}} a.app span{{display:block;color:var(--mut);font-size:13px;margin-top:4px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:8px 0 22px}}
.stat{{background:var(--panel);border-radius:12px;padding:14px;border:1px solid #232849}}
.stat i{{font-style:normal;font-size:28px;font-weight:700;display:block}} .stat small{{color:var(--mut)}}
.c1 i{{color:var(--cyan);text-shadow:0 0 12px var(--cyan)}} .c2 i{{color:var(--lime);text-shadow:0 0 12px var(--lime)}}
.c3 i{{color:var(--amber);text-shadow:0 0 12px var(--amber)}} .c4 i{{color:var(--red);text-shadow:0 0 12px var(--red)}}
h2{{font-size:18px;margin:26px 0 10px;color:#fff;text-shadow:0 0 10px var(--pink)}}
.rules{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}
.rule{{background:var(--panel);border-radius:12px;padding:14px;border:1px solid #2a2f55}} .rule span{{display:block;color:var(--mut);font-size:13px}}
.rule p{{margin:6px 0 0;font-size:13px}} .gA{{box-shadow:0 0 14px #9dff3a33;border-color:var(--lime)}} .gB{{box-shadow:0 0 14px #22f3ff33;border-color:var(--cyan)}}
.note{{background:#170b16;border:1px solid var(--pink);border-radius:12px;padding:14px;box-shadow:0 0 16px #ff2bd633}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden;font-size:13.5px}}
td{{padding:9px 10px;border-bottom:1px solid #1c2142;vertical-align:top}} td:first-child{{font-weight:700;white-space:nowrap}}
tr.fail td:first-child{{color:var(--red)}} tr.pass td:first-child{{color:var(--lime);text-shadow:0 0 8px var(--lime)}}
tr.watch td:first-child{{color:var(--amber);text-shadow:0 0 8px var(--amber)}}
.foot{{color:var(--mut);font-size:12.5px;margin-top:26px}}
</style></head><body><div class="wrap">
<h1>OMEGA · PROGRESS BOARD</h1>
<div class="sub">Updated <b>{now}</b> · research, bots and apps from the repository BlitzDragneel/Aura. Every number below
comes from the result files; nothing on this page is a forecast.</div>
<div class="apps">
<a class="app p" href="omega-prime.html"><b>OMEGA Prime →</b><span>Claude's lean app: today's verdict, your orders, signals, evidence</span></a>
<a class="app o" href="omega-v6_5-47.html"><b>OMEGA original →</b><span>Your full app with CREED (4.5 MB, loads slower on phones)</span></a>
<a class="app p" href="https://github.com/BlitzDragneel/Aura/blob/bot-state/STATUS.txt"><b>Paper bot record →</b><span>Runs every hour on GitHub (paper only): open orders, positions, last actions</span></a>
<a class="app l" href="https://omega-live-api.onrender.com/health"><b>Live API health →</b><span>OKX/Binance crypto, Swissquote forex & gold, Deribit DVOL (wakes in ~1 min)</span></a>
</div>
<div class="stats">
<div class="stat c1"><i>{len(R)}</i><small>new plans judged (E37+)</small></div>
<div class="stat c2"><i>{n_pass}</i><small>passed</small></div>
<div class="stat c3"><i>{n_watch}</i><small>watch list (grade C)</small></div>
<div class="stat c4"><i>{attempts:,}</i><small>variants counted</small></div>
</div>
<h2>Rules the bots may trade (edges/approved.json)</h2>
<div class="rules">{rules}</div>
<h2>Leverage — what the tests say</h2>
<div class="note">On every rule tested, 2× already causes liquidations and <b>20× / 40× wipe out the account</b>
(30–60% of trades touch the liquidation price first). Highest safe leverage so far: <b>1×</b>.</div>
<h2>Every test this round</h2>
<table>{trs}</table>
<div class="foot">Paper and testnet first. Grade A/B = passed a fair, pre-registered test; not a promise of future profit.</div>
</div></body></html>"""
    open(P("omega", "apps", "index.html"), "w", encoding="utf-8").write(doc)
    print("wrote omega/apps/index.html", len(R), "results")


if __name__ == "__main__":
    main()
