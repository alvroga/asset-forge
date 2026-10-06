# Log — one line per friction or win (date, what, why it matters)

- 2026-10-05: project scaffolded from the tennis-spike session; nothing installed or downloaded yet.
- 2026-10-05: tools/setup.sh ran clean first try (lab + both Hunyuan MLX envs); weights download started with user approval.
- 2026-10-05: Qwen weights land in ~/.cache/huggingface/hub, not vendor/sdcpp; overnight.py now searches the HF cache too.
- 2026-10-05: smoke test (barrel) passed end-to-end in 14.9 min: qwen 420s, matte 53s, hunyuan shape+paint 404s, blender finish 17s. raw 300k faces -> final 20k. Added tools/status.sh. report.py needed the lab venv for trimesh (face counts were blank).
- 2026-10-05: Blender 5.2 headless works; tools/render_views.py renders 4 views of a GLB (lab's turntable needs a live Blender socket). Barrel final.glb: clean silhouette, hoops/rivets/planks intact, back side consistent; top-cap texture slightly stretched, colour warmer/brighter than the 2D source.
- 2026-10-05: overnight batch 8/8 OK in 117.7 min; FINDINGS.md written (conditional go). Potion glass failed (opaque); racket strings noisy; rest good.
- 2026-10-05: Rigify addon fails to register in headless Blender 5.2.2 (KeyError 'rigify' / load-order mismatch) -> writing own deform-skeleton rigger (tools/rig_humanoid.py) instead.
- 2026-10-05: postman 3D in 6.3 min (hunyuan 350 s). Rigging gotchas: Hunyuan/retopo GLB is triangle soup (57k verts for 20k faces) -> Blender bone-heat auto-weights silently fail (all verts unweighted) until `remove_doubles`; after welding (10k verts) auto-weights succeed. tools/rig_humanoid.py = own 21-bone deform skeleton from silhouette-detected joints + auto weights + Idle/Walk + GLB export. Postman walk pose looks clean.
