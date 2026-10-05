# Log — one line per friction or win (date, what, why it matters)

- 2026-10-05: project scaffolded from the tennis-spike session; nothing installed or downloaded yet.
- 2026-10-05: tools/setup.sh ran clean first try (lab + both Hunyuan MLX envs); weights download started with user approval.
- 2026-10-05: Qwen weights land in ~/.cache/huggingface/hub, not vendor/sdcpp; overnight.py now searches the HF cache too.
- 2026-10-05: smoke test (barrel) passed end-to-end in 14.9 min: qwen 420s, matte 53s, hunyuan shape+paint 404s, blender finish 17s. raw 300k faces -> final 20k. Added tools/status.sh. report.py needed the lab venv for trimesh (face counts were blank).
