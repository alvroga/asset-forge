# Test plan (for the orchestrating Claude)

## Question
Can we get **usable game props** offline on this Mac with Qwen-Image -> Hunyuan3D -> Hunyuan Paint, at acceptable
speed, quality, poly count and licence risk — and would it be a worthwhile *optional* module for studio-kit videogame projects?

## Phases
1. **Setup** (`tools/setup.sh`) then confirm weights with the user -> `tools/fetch-weights.sh --yes`.
   Check free disk first (`df -h`), Xcode present (`xcode-select -p`), `uv` present.
2. **Smoke test**: one prop (`--only barrel --date smoke`). Check each stage's log. Fix script paths if the lab layout differs
   (the overnight script was written from reading the lab's README/source, never executed — expect small fixes, e.g. sd-cli
   weight locations under `vendor/image-to-3dlab/vendor/sdcpp`, the `retopo_repaint.py` args, Hunyuan `--model` names).
3. **Overnight batch** (8 props). Then read `runs/<date>/report.md`.
4. **Evaluate** (record in `docs/FINDINGS.md`):
   - time per stage and per prop; peak memory if observable
   - raw vs finished face counts and file size (game budget: props ~2-20k faces)
   - visual quality: silhouette, texture legibility, seams, holes, consistency with the 2D source
   - single-object prompts vs the lab's *prop sheet* mode (one image -> nine props)
   - which prompts fail and why (e.g. thin parts, transparency like glass)
5. **Optional comparison** if time: same matted image through Pixal3D (needs DINOv3 HF access) and TRELLIS.2 (gated, ~1h setup). Ask the user first.
6. **Engine check**: Unity is not installed. Import path would be GLB via the glTFast package. Do NOT install Unity without the user.
   Godot is available (`/Applications/Godot.app`) but the user asked for no Godot windows on this Mac — do not open it.
   A Blender turntable render (`scripts/blender_turntable.py` in the lab) is the headless way to eyeball results.

## Deliverable
`docs/FINDINGS.md`: verdict (go / no-go / conditional) for a studio-kit "AI 3D assets" optional module, with numbers, a
recommended default recipe, licence caveats, and a list of what the kit page would need. Then tell the user; they decide what
goes into studio-kit (do not edit it).
