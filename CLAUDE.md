# CLAUDE.md — asset-forge

## What this is
A **test bench** for local, offline AI game-asset generation on an Apple Silicon Mac (M1 Ultra, 128 GB).
Goal: decide whether this pipeline can complement the studio-kit (`~/Projects/studio-kit`) for **videogame**
projects. It is NOT a game and NOT part of tennis-spike (halted) or studio-kit.

Recipe under test (recommended by other users): **Qwen-Image -> Hunyuan3D -> Hunyuan Paint -> Unity**.
Tooling: [Image to 3D Lab](https://github.com/Bingeljell/image-to-3dlab), installed under `vendor/` (gitignored, external,
never vendored into this repo or studio-kit).

## Boundaries — never without explicit approval
- Never **push**, create remotes, upload anything, or sign up for / spend money on services. Local commits only.
- Never download model weights without the user's yes (`tools/fetch-weights.sh` enforces `--yes`; sizes and licences in `docs/LICENCES.md`).
- Never edit studio-kit or tennis-spike from here. Findings go to `docs/FINDINGS.md`; the user decides what moves into studio-kit.
- Generated assets are **test outputs, not shippable**: Qwen is non-commercial/ambiguous, Hunyuan weights are not licensed in the EU/UK/South Korea. Never claim otherwise.
- Do not run installs outside `vendor/` or a venv. No global pip.

## How to run (in order)
1. `tools/setup.sh` — lab code + Python envs, no weights (a few GB with PyTorch).
2. `tools/fetch-weights.sh --yes` — ~27 GB: Qwen-Image 13.4, Hunyuan 2.0 shape+paint ~13, BiRefNet 0.2. Needs user OK.
3. Smoke test one prop: `python3 tools/overnight.py --only barrel --date smoke`
4. Overnight: `python3 tools/overnight.py` (8 props, resumable, per-prop failure isolation) -> `runs/<date>/report.md`.
Prompts: `prompts/props.json`. Everything is timed; logs in `runs/<date>/<prop>/run.log`.

## Orchestrator brief
See `docs/PLAN.md` (what to test, how to judge, what to write down).
Workflow: friction/win -> one line in `docs/LOG.md` immediately. Conclusions -> `docs/FINDINGS.md`.
Run long jobs in the background (`run_in_background`), never block on them.
Blender (`/Applications/Blender.app`) is installed; Unity is NOT installed (see PLAN).
