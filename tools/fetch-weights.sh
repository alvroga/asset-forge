#!/usr/bin/env bash
# Download the model weights for the Qwen -> Hunyuan3D -> Hunyuan Paint recipe.
# ~27 GB total. Refuses to run without --yes (see docs/LICENCES.md first).
set -euo pipefail
cd "$(dirname "$0")/.."
[ "${1:-}" = "--yes" ] || { cat <<'MSG'
This will download (approx):
  Qwen-Image 2.1 GGUF + text encoder + VAE   ~13.4 GB  (Qwen Research License: non-commercial)
  Hunyuan3D 2.0 shape + paint (MLX)          ~13   GB  (Tencent Community License: not for EU/UK/South Korea)
  BiRefNet-lite background remover           ~0.2  GB  (MIT)
Read docs/LICENCES.md, then re-run with --yes.
MSG
exit 1; }
LAB=vendor/image-to-3dlab
cd "$LAB"
.venv/bin/python scripts/bootstrap_matte.py --yes
.venv/bin/python scripts/bootstrap_qwen_image.py --yes
hunyuan_mlx/shape/.venv/bin/python hunyuan_mlx/download_weights.py --model 2.0
