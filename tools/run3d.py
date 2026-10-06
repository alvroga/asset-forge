#!/usr/bin/env python3
"""Run matte -> Hunyuan3D -> Blender finish on existing source images (Qwen step is skipped).

    python3 tools/run3d.py runs/characters/postman runs/characters/barbarian runs/characters/dragon

Each directory must already hold source.png. Reuses overnight.run_prop, so stages are timed, resumable and
failure-isolated per directory. Writes result.json beside each source.png.
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import overnight

ap = argparse.ArgumentParser()
ap.add_argument("dirs", nargs="+"); ap.add_argument("--faces", type=int, default=20000); ap.add_argument("--seed", type=int, default=42)
args = ap.parse_args()
for d in args.dirs:
    d = Path(d).resolve()
    r = overnight.run_prop({"id": d.name, "subject": d.name}, "", d, args)
    print(d.name, "OK" if r["ok"] else f"FAILED {r.get('error')}", {k: v.get("seconds") for k, v in r["stages"].items()}, flush=True)
