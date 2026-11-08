import json, re, glob, importlib.util, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/user/Aura/omega/academy/course.json"
DISCLAIMER = ("OMEGA Academy is education, not financial advice. Trading spot crypto, perpetual futures and CFDs "
 "(forex, gold) carries a high risk of losing money, and leveraged products can lose your whole deposit quickly. "
 "Nothing in this course is a recommendation to buy or sell anything, and nothing promises a profit. Past and "
 "backtested results do not guarantee future results; the research quoted here shows most trading rules fail "
 "fair tests, and the few that passed are fading. Only trade money you can afford to lose, practise on paper or "
 "a demo first, check that your broker or exchange is allowed to serve you where you live, and get independent "
 "advice if you are unsure. The author and OMEGA are not licensed investment advisers.")
def words(s): return len(re.findall(r"[A-Za-z0-9%$.+−\-]+", s))
mods = []
for f in sorted(glob.glob(os.path.join(HERE, "m[0-9][0-9].py"))):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    mods.append(m.MODULE)
total_min = 0; nl = 0; errs = []
for mi, M in enumerate(mods, 1):
    assert M["id"] == "m%02d" % mi, M["id"]
    for li, L in enumerate(M["lessons"], 1):
        assert L["id"] == "%s-l%02d" % (M["id"], li), L["id"]
        w = words(L["body_md"])
        L["minutes"] = max(6, min(15, round(w / 140) + 2))
        if "free" not in L: L["free"] = bool(M["free"] or li == 1)
        assert 3 <= len(L["quiz"]) <= 5, L["id"]
        for qi, q in enumerate(L["quiz"]):
            import hashlib, random
            rnd = random.Random(hashlib.md5((L["id"] + str(qi)).encode()).hexdigest())
            correct = q["options"][q["answer"]]
            opts = q["options"][:]; rnd.shuffle(opts)
            q["options"] = opts; q["answer"] = opts.index(correct)
            assert len(q["options"]) == 4 and 0 <= q["answer"] < 4 and q["why"], (L["id"], q["q"])
        assert len(L["key_points"]) >= 3, L["id"]
        if w < 650: errs.append("%s short: %d words" % (L["id"], w))
        total_min += L["minutes"]; nl += 1
        L["_words"] = w
course = {"title": "OMEGA Academy — Trade with evidence", "version": "1.0", "updated": "2026-11-08",
          "disclaimer": DISCLAIMER, "modules": []}
report = []
for M in mods:
    mm = {k: M[k] for k in ("id", "title", "summary", "free")}
    mm["lessons"] = []
    for L in M["lessons"]:
        report.append((L["id"], L["minutes"], L["_words"], L["free"], L["title"]))
        mm["lessons"].append({k: L[k] for k in ("id", "title", "minutes", "free", "body_md", "key_points", "quiz")})
    course["modules"].append(mm)
json.dump(course, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.load(open(OUT))
for r in report: print(*r, sep=" | ")
print("modules", len(mods), "lessons", nl, "minutes", total_min, "words", sum(r[2] for r in report))
for e in errs: print("WARN", e)

# ---- OUTLINE.md ----
OUTLINE = os.path.join(os.path.dirname(OUT), "OUTLINE.md")
L_all = [l for m in course["modules"] for l in m["lessons"]]
tot = sum(l["minutes"] for l in L_all); free = [l for l in L_all if l["free"]]; fm = sum(l["minutes"] for l in free)
o = [f"# {course['title']} — course outline", "",
     f"Version {course['version']}, updated {course['updated']}. {len(course['modules'])} modules, {len(L_all)} lessons, about {tot} minutes of reading "
     f"(≈{tot/60:.1f} hours) plus exercises in the OMEGA app. Every lesson has key points and a 4-question quiz with explanations.", "",
     f"**Free:** Modules 1–2 in full, plus the first lesson of every other module ({len(free)} lessons, about {fm} minutes). "
     f"**Premium:** the other {len(L_all)-len(free)} lessons (about {tot-fm} minutes).", "",
     "Minutes are estimated from lesson length (about 140 words a minute, plus time for the worked examples). "
     "Research results quoted in the course are listed, test by test, on the progress board: https://omega-board.onrender.com", ""]
for m in course["modules"]:
    mt = sum(l["minutes"] for l in m["lessons"])
    o += [f"## Module {int(m['id'][1:])}. {m['title']} — {mt} min, {'FREE' if m['free'] else 'premium (first lesson free)'}", "", m["summary"], "",
          "| # | Lesson | Minutes | Access |", "|---|---|---|---|"]
    o += [f"| {l['id']} | {l['title']} | {l['minutes']} | {'Free' if l['free'] else 'Premium'} |" for l in m["lessons"]]
    o.append("")
open(OUTLINE, "w", encoding="utf-8").write("\n".join(o))
print("wrote", OUT, "and", OUTLINE)
