#!/usr/bin/env bash
# Install Image to 3D Lab (code + Python packages only, NO model weights) into vendor/.
# Safe to re-run. Weights are fetched separately by tools/fetch-weights.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
LAB=vendor/image-to-3dlab
mkdir -p vendor
if [ ! -d "$LAB/.git" ]; then
  curl -fsSL https://raw.githubusercontent.com/Bingeljell/image-to-3dlab/main/install.sh \
    | bash -s -- --yes --no-start --dir "$PWD/$LAB"
else
  bash "$LAB/install.sh" --yes --no-start --dir "$PWD/$LAB"
fi
# Hunyuan3D-MLX environments (Python 3.12 pinned by the lab, uv builds them)
uv sync --project "$LAB/hunyuan_mlx/shape"
uv sync --project "$LAB/hunyuan_mlx/paint"
echo "setup done. Next: tools/fetch-weights.sh --yes"
