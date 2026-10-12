#!/usr/bin/env python3
"""Fetch LeetCode stats and regenerate assets/leetcode.svg (stdlib only)."""
import json, os, sys, time, urllib.request

USERNAME = os.environ.get("LEETCODE_USERNAME", "Abhivansh_Parashar")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "leetcode.svg")
FONT = "'Fira Code','JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono','Courier New',monospace"
BG, TXT, GRAY, SPRING = "#0b0f14", "#e6edf3", "#8b949e", "#6db33f"
QUERY = """query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum{difficulty count}}}}"""


def fetch(username, tries=3):
    body = json.dumps({"query": QUERY, "variables": {"u": username}}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql", data=body,
        headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/u/{username}/",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
            rows = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
            d = {x["difficulty"]: x["count"] for x in rows}
            return d["Easy"], d["Medium"], d["Hard"]
        except Exception as ex:
            print(f"attempt {i+1} failed: {ex}", file=sys.stderr)
            time.sleep(3 * (i + 1))
    return None


def svg(e, m, h):
    tot = e + m + h; R = 24; C = 2 * 3.14159265 * R; W, H = 900, 84
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{SPRING}" stroke-opacity="0.4"/>',
         f'<circle cx="52" cy="42" r="{R}" fill="none" stroke="#1c2230" stroke-width="6"/>']
    off, bt = 0, 0.2
    for val, col in ((e, "#00b8a3"), (m, "#ffc01e"), (h, "#ef4743")):
        seg = val / tot * C
        o.append(f'<circle cx="52" cy="42" r="{R}" fill="none" stroke="{col}" stroke-width="6" transform="rotate(-90 52 42)" stroke-dasharray="{seg-2:.1f} {C-seg+2:.1f}" stroke-dashoffset="{-off:.1f}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{bt:.2f}s" dur="0.4s" fill="freeze"/></circle>')
        off += seg; bt += 0.25
    o.append(f'<text x="52" y="47" font-size="15" font-weight="bold" fill="{TXT}" text-anchor="middle">{tot}</text>')
    o.append(f'<text x="100" y="32" font-size="11" fill="{GRAY}">$ leetcode --stats</text><text x="100" y="54" font-size="16" font-weight="bold" fill="{TXT}">{USERNAME}</text>')
    o.append(f'<text x="100" y="72" font-size="12" fill="{SPRING}">{tot} problems solved</text>')
    bx = 330
    for label, val, col in (("Easy", e, "#00b8a3"), ("Medium", m, "#ffc01e"), ("Hard", h, "#ef4743")):
        pct = val / tot
        o.append(f'<text x="{bx}" y="32" font-size="13" font-weight="bold" fill="{col}">{label}</text><text x="{bx+160}" y="32" font-size="15" font-weight="bold" fill="{TXT}" text-anchor="end">{val}</text>'
                 f'<rect x="{bx}" y="42" width="160" height="6" rx="3" fill="#1c2230"/><rect x="{bx}" y="42" width="0" height="6" rx="3" fill="{col}"><animate attributeName="width" from="0" to="{160*pct:.1f}" begin="0.4s" dur="1s" fill="freeze"/></rect>'
                 f'<text x="{bx}" y="68" font-size="11" fill="{GRAY}">{round(pct*100)}% of solved</text>')
        bx += 185
    o.append("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    stats = tuple(int(x) for x in sys.argv[2:5]) if len(sys.argv) == 5 and sys.argv[1] == "--mock" else fetch(USERNAME)
    if not stats:
        print("Could not fetch stats; keeping existing SVG.")
        sys.exit(0)  # don't fail the workflow
    open(OUT, "w").write(svg(*stats))
    print("Updated:", stats)
