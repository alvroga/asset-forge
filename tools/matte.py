#!/usr/bin/env python3
"""Cut the background out of an image using the lab's BiRefNet-lite remover.

Run with the lab's venv:  vendor/image-to-3dlab/.venv/bin/python tools/matte.py in.png out.png
Qwen-Image writes RGBA with noise alpha, so every image MUST pass through here before 3D.
"""
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "vendor" / "image-to-3dlab"
sys.path.insert(0, str(LAB))
from PIL import Image  # noqa: E402
from image_to_3dlab import matte  # noqa: E402

src, dst = sys.argv[1], sys.argv[2]
rgba, model = matte.cut_out(Image.open(src).convert("RGB"))
rgba.save(dst)
print(f"matted with {model}: {dst}")
