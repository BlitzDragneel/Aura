"""v6.5.108: "Neon Glow" theme (the owner asked for glowing neon on the main app). Look only: CSS plus a theme option and a
one-time switch. No rule, engine, data or research text changed; CREED's engine is byte-identical.
 1. New theme `neonglow`: deep night background, cyan / magenta / lime neon accents, glowing headings, cards, buttons,
    active tabs and the brand mark; a slow pulse on the brand only (switched off by Settings > Animations off).
 2. It becomes the default: listed first and selected in Settings > Display > Theme.
    (The accent colour setting does not apply in this theme: its cyan is fixed.)
 3. One-time switch: a browser still on the old default ("dark") moves to Neon Glow once (flag omega_neon108). Any other
    theme she chose is kept, and she can pick "Dark" again at any time.
usage: python3 patch108.py <v6.5.107 build> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)


CSS = """
/* ═══ v6.5.108 — NEON GLOW theme (look only) ═══ */
html[data-theme="neonglow"]{ --bg:#05060D; --panel:#0B0E1C; --panel2:#111633; --border:#262C5A;
  --text:#ECF0FF; --text-dim:#97A0C8; --bull:#3DFFB0; --bear:#FF4D7A; --gold:#22F3FF !important; --amber:#FF2BD6; --violet:#B98CFF;
  --neon1:#22F3FF; --neon2:#FF2BD6; --neon3:#9DFF3A; }
html[data-theme="neonglow"] body{ background:
  radial-gradient(1100px 520px at 0% -8%, rgba(120,40,255,.20), transparent 60%),
  radial-gradient(900px 480px at 105% 0%, rgba(0,200,255,.14), transparent 55%), var(--bg) fixed; }
html[data-theme="neonglow"] h1, html[data-theme="neonglow"] h2, html[data-theme="neonglow"] .mh-brand{
  text-shadow:0 0 6px rgba(34,243,255,.55), 0 0 18px rgba(34,243,255,.30); }
html[data-theme="neonglow"] h3{ text-shadow:0 0 8px rgba(255,43,214,.35); }
html[data-theme="neonglow"] .mh-glyph{ color:var(--neon1); text-shadow:0 0 8px var(--neon1),0 0 22px var(--neon1),0 0 40px #0af;
  animation:omegaNeonPulse 3.2s ease-in-out infinite; }
@keyframes omegaNeonPulse{ 0%,100%{ text-shadow:0 0 6px var(--neon1),0 0 16px var(--neon1); } 50%{ text-shadow:0 0 10px var(--neon1),0 0 28px var(--neon1),0 0 48px #0af; } }
html[data-theme="neonglow"] .card{ border-color:rgba(34,243,255,.28);
  box-shadow:0 0 0 1px rgba(34,243,255,.10), 0 0 16px rgba(34,243,255,.10), inset 0 0 22px rgba(120,60,255,.06); }
html[data-theme="neonglow"] .card:hover{ box-shadow:0 0 0 1px rgba(34,243,255,.30), 0 0 22px rgba(34,243,255,.22); }
html[data-theme="neonglow"] .btn-primary{ background:linear-gradient(90deg,#16C8FF,#B44CFF); color:#05060D; border-color:transparent;
  box-shadow:0 0 12px rgba(34,243,255,.55), 0 0 26px rgba(180,76,255,.35); }
html[data-theme="neonglow"] .btn-outline{ border-color:var(--neon1); color:var(--neon1); box-shadow:0 0 8px rgba(34,243,255,.30); }
html[data-theme="neonglow"] .btn-outline:hover, html[data-theme="neonglow"] .btn-ghost:hover{ box-shadow:0 0 14px rgba(34,243,255,.55); }
html[data-theme="neonglow"] .btn-ghost{ color:var(--neon2); }
html[data-theme="neonglow"] .active, html[data-theme="neonglow"] [aria-current="page"]{ text-shadow:0 0 8px rgba(34,243,255,.7); }
html[data-theme="neonglow"] input:focus, html[data-theme="neonglow"] select:focus, html[data-theme="neonglow"] textarea:focus{
  outline:none; border-color:var(--neon1); box-shadow:0 0 0 2px rgba(34,243,255,.25), 0 0 14px rgba(34,243,255,.35); }
html[data-theme="neonglow"] .bull, html[data-theme="neonglow"] .up{ text-shadow:0 0 8px rgba(61,255,176,.45); }
html[data-theme="neonglow"] .bear, html[data-theme="neonglow"] .down{ text-shadow:0 0 8px rgba(255,77,122,.45); }
@media (prefers-reduced-motion: reduce){ html[data-theme="neonglow"] .mh-glyph{ animation:none; } }
"""

# 1. theme CSS, right after the v4.3 theme pack's neon line (inside the same first <style>)
m = re.search(r'html\[data-theme="neon"\]\{[^\n]*\n', s)
assert m and s.count(m.group(0)) == 1
rep(m.group(0), m.group(0) + CSS)

# 2. the option, first and selected
rep('            <option value="dark" selected>Dark (default)</option>\n',
    '            <option value="neonglow" selected>Neon Glow (default)</option>\n            <option value="dark">Dark (classic)</option>\n')

# 3. one-time switch from the old default, applied right after settings load
rep('    loadSettings();\n',
    "    loadSettings();\n"
    "    try{ if(!localStorage.getItem('omega_neon108')){ var th=document.getElementById('setTheme');   // v6.5.108: one-time move to Neon Glow\n"
    "      if(th && th.value==='dark'){ th.value='neonglow'; saveSettings(); }\n"
    "      localStorage.setItem('omega_neon108','1'); applyTheme(); } }catch(e){}\n")

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.107 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.107 ' + sep + ' build ' + o + ' UTC', 'v6.5.108 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.108 · build' in s and 'v6.5.107 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
