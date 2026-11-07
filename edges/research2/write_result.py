import sys, json, os
sys.path.insert(0, "/home/user/Aura")
S = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/research2/"
plan, fname, reason = sys.argv[1], sys.argv[2], sys.argv[3]
f = json.load(open(S + plan.lower() + "/finish.json"))
d = json.load(open(S + plan.lower() + "/disc.json"))
res = dict(plan=fname, md5=f["md5"], common_md5="bd0672286814170e8fee514bb6d55788", verdict=f["verdict"], reason=reason,
           variants=f["variants"], luck=f["luck"], eligible=f["eligible"], promoted=f["promoted"], validation=f["validation"],
           final=f["final"], info_only_final=f["info_only"], best_discovery=f["best_discovery"],
           bench=d.get("bench"), discovery=d["variants"])
json.dump(res, open(f"/home/user/Aura/edges/results/{plan}_result.json", "w"), indent=1, default=str)
print("written", plan)
