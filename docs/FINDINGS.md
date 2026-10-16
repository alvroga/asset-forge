# Findings — Qwen-Image -> Hunyuan3D 2.0 -> Hunyuan Paint (Image to 3D Lab), M1 Ultra 128 GB

Run: `runs/2026-10-05/` (8 props, seed 42, `--faces 20000`). Visual review via `tools/render_views.py`
(Blender 5.2.2 headless, 4 views) and `runs/2026-10-05/contact{1,2}.png`. Judged by one reviewer (Claude), by eye, once.

## Verdict: CONDITIONAL GO as an optional, non-commercial prototyping module
Works end-to-end unattended: 8/8 props OK, 0 retries, ~15 min per prop. Output is usable as placeholder/prototype art.
Not shippable as-is: licence chain (below) and some fidelity failures (glass, fine strings).

## Numbers
| | |
|---|---|
| Batch | 117.7 min for 8 props (mean 14.7, range 11.3-20.4 min) |
| Qwen-Image (1024², 20 steps) | 390-443 s per image, ~45% of total time |
| Matte (BiRefNet-lite) | ~7 s (53 s on first cold run) |
| Hunyuan shape+paint | mean 464 s, range 272 s (sword) - 814 s (lantern) |
| Blender finish (retopo+bake+compress) | 6-13 s |
| Raw mesh | 300k faces (decimated cap), 16-32 MB; sword 119k |
| Final mesh | 20k faces, 2.9-5.4 MB GLB, 2048 atlas, one mesh, textured PBR |
| Failures | none (per-prop isolation never needed) |
Peak memory not measured (qwen process alone showed ~13.7 GB RSS).

## Per prop (final.glb, 20k faces)
- **chest** — best result. Clean silhouette, brass corners/lock, side and back plausible. Stylised look differs slightly from the 2D source.
- **barrel** — good. Hoops, rivets, planks intact; back invented plausibly. Top cap texture slightly stretched.
- **crate** — good. Both crates and rope handles preserved; back side generic but consistent.
- **lantern** — good. Glass panes read as faint glazing and the candle survives inside. Slowest prop (814 s Hunyuan).
- **tree** — acceptable. Layered boughs OK; tips washed pale, trunk tiny.
- **sword** — geometry correct (guard, wrapped grip, pommel); blade very thin, so edge-on views nearly vanish. Fine as a prop, check collision/thickness.
- **racket** — frame and grip good; the white strings became a noisy grey speckle texture, not fine strings. Thin-structure weakness.
- **potion** — **fail on transparency**: the glass bottle became an opaque pale-green sphere with a white neck. Glowing liquid colour lost. Glass is not workable with this recipe.

## Cross-cutting
- Hunyuan **invents the unseen back** from one view; it was consistent in every prop here (no holes, no obvious seams).
- **Colour fidelity drifts**: finals are warmer/paler than the 2D source (barrel orange vs dark brown, tree/potion desaturated). Part of this may be my quick preview lighting (flat grey world, sun 3); not yet isolated. Check by viewing the GLB in the real engine before blaming the pipeline.
- Texture bake at 2048 held up at preview res; not inspected at close range.
- 20k faces is the top of the plan's prop budget (2-20k); simple props (crate, barrel) could go lower. Try `--faces 5000`.
- Seed was fixed at 42 for every prop; no variance measured.

## Not tested
- Prop-sheet mode (one image -> nine props); Pixal3D / TRELLIS.2 comparison; Unity import (not installed, glTFast plan only);
  rigging/animation; creatures (dragon-like creatures were tried later, see Characters below).

## Licence caveats (see LICENCES.md)
Qwen weights are non-commercial; Hunyuan is not licensed in EU/UK/South Korea. Every asset here is a **test output, not shippable**.
A cleaner chain would need your own source image (skip Qwen) plus a more permissive 3D model.

## Recommended default recipe (if pursued)
Qwen-Image 1024² seed-fixed -> BiRefNet matte -> Hunyuan 2.0 shape+paint -> `retopo_repaint.py --faces 20000 --skip-paint`.
Pick props that are solid, opaque, compact; avoid glass, fine mesh/strings, very thin parts. Budget ~15 min/prop on this machine;
Qwen is half of it, so reusing hand-drawn or pre-made source images roughly halves the time and removes the Qwen licence problem.

## What a studio-kit "AI 3D assets" page would need
Setup/weights steps (~15 GB in vendor + ~16 GB HF cache; weights live in `~/.cache/huggingface` and `~/.u2net`), the licence
table with a per-asset provenance row, the prop-suitability list above, a Blender preview script (`tools/render_views.py`),
and an engine-import check (Unity/glTFast, not done).

## Characters (runs/characters/, added later the same day)
- **postman** (stylised, flat colours): 3D 6.3 min; kept cap, face, bag, shoes. Rigged with `tools/rig_humanoid.py` (21 bones, auto weights, Idle+Walk) — walk pose looks clean in stills. Rig gotcha: GLB is triangle soup, must weld vertices before Blender auto-weights or they silently fail.
- **barbarian** (painterly realistic, fur/braids/straps): 3D 8.7 min (Hunyuan 502 s). Recognisable, but proportions got squatter (short legs, heavy torso), face and hair detail soft, hair colour shifted redder, and the **back is the weak side**: orange/rust blotches on the upper back and the rear. Fine detail (braids, straps, fur trim) mostly became texture, not geometry. Not rigged (by decision).
- Conclusion so far: the stylised character translates far better than the painterly-realistic one; characters are only a base mesh for hand polish (tri topology, no edge loops for deformation), while props are the realistic use case.
- **dragon** (made-up creature; the source image is not included in this public repo): 3D 15.4 min (Hunyuan 866 s, slowest of all). Kept S body, both wings, skin-toned arm, spikes, scales, and the **thin stick legs with bird feet** (better than the racket strings). Failures: Hunyuan **invented a second arm** on the unseen side (symmetry assumption), body is ribbon-flat from the side, head/face soft. For printing: legs and wing membranes too thin, extra arm needs removing.
