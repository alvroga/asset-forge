#!/usr/bin/env python3
"""Write runs/<date>/report.md from each prop's result.json (sizes, timings, face counts)."""
import json, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
date = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
base = ROOT / "runs" / date


def faces(p):
    try:
        import trimesh
        s = trimesh.load(p, force="scene")
        return sum(len(g.faces) for g in s.geometry.values())
    except Exception:
        return None


rows = []
for rj in sorted(base.glob("*/result.json")):
    r = json.loads(rj.read_text()); d = rj.parent
    st = r["stages"]
    secs = sum(v.get("seconds", 0) for v in st.values() if isinstance(v, dict))
    def sz(n):
        f = d / n
        return f"{f.stat().st_size/1e6:.1f} MB" if f.exists() else "-"
    def fc(n):
        f = d / n
        v = faces(f) if f.exists() else None
        return f"{v:,}" if v else "-"
    rows.append(f"| {r['id']} | {'OK' if r['ok'] else 'FAIL'} | {secs/60:.1f} | {sz('raw.glb')} / {fc('raw.glb')} | {sz('final.glb')} / {fc('final.glb')} | {r.get('error','')[:60]} |")
out = [f"# Run report {date}", "",
       "| prop | status | minutes | raw GLB (size / faces) | final GLB (size / faces) | error |",
       "|---|---|---|---|---|---|", *rows, "",
       "Judge quality by eye: open `runs/<date>/<prop>/final.glb` (and `source.png` beside it).",
       "Licences: see docs/LICENCES.md. This run used Qwen (non-commercial) and Hunyuan (territory-restricted)."]
(base / "report.md").write_text("\n".join(out) + "\n")
print(f"wrote {base/'report.md'}")
