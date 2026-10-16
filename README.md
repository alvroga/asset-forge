# asset-forge

A research test bench for **local, offline AI game-asset generation** on an Apple Silicon Mac (developed on an
M1 Ultra, 128 GB). It was built and run largely by an AI coding agent (Claude Code) working from a written plan,
as an experiment in orchestrating AI on a small R&D question:

> Can a fully local pipeline produce usable game props, and is it worth adopting for real projects?

## What is in here

| Path | What |
|---|---|
| `tools/` | Orchestration for the 3D recipe: Qwen-Image -> Hunyuan3D 2.0 shape + paint -> Blender cleanup (batch runner, matting, view renderer, humanoid auto-rigger, status/report scripts). Built on [Image to 3D Lab](https://github.com/Bingeljell/image-to-3dlab). |
| `prompts/` | The prop prompts used. |
| `docs/` | `PLAN.md` (what to test), `FINDINGS.md` (results and verdict), `LOG.md` (lab notes), `LICENCES.md` (licence audit of the models). |
| `runs/` | Run reports and contact sheets from the first batch. Raw outputs are not committed. |
| `CLAUDE.md` | The standing instructions given to the agent (boundaries, workflow). |

Start with `docs/FINDINGS.md` for the conclusions.

## What is **not** here

- Model weights and the `vendor/` toolchain (tens of GB; fetched by `tools/fetch-weights.sh`, which requires an
  explicit `--yes`).
- Most generated images and 3D models.
- Project-specific work built on top of this bench.

## Licences and caveats

- The code in this repo is MIT-licensed (see `LICENSE`).
- **Generated assets are test outputs, not shippable.** Some of the models used are non-commercial (Qwen-Image
  Research License) or not licensed in the EU/UK/South Korea (Hunyuan3D). See `docs/LICENCES.md`; re-verify at the
  source before relying on any of it.
- Scripts assume macOS, Blender, and local paths set up by `tools/setup.sh`. This is a lab notebook, not a polished
  tool: expect rough edges.
