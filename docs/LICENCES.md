# Licences of the pipeline (verify before any commercial use)

Sourced from the lab's README/provenance notes on 2026-10-05; **re-verify at the source** before relying on them.

| Component | Licence | Consequence |
|---|---|---|
| Image to 3D Lab code | Apache-2.0 | free to use |
| Qwen-Image 2.1 (weights) | Qwen Research License (non-commercial); Qwen *says* generated images are the user's, but licence text still says non-commercial | Treat as **non-commercial** unless a licence is obtained. Source images from here taint the chain. |
| Hunyuan3D 2.0 (weights, MLX port code/weights) | Tencent Community License | **Not licensed in the EU, UK or South Korea**; other limits (large-user threshold, no improving other models). |
| BiRefNet-lite | MIT | fine |
| TRELLIS.2 / Pixal3D (not in this recipe) | MIT + DINOv3 License (gated) | "commercial-conditional" |

The lab writes a `.provenance.json` sidecar per run; keep it next to any asset.
Any asset that ever enters a game needs a row in that game's asset-licence table (no unclear-licence assets).
Comparison option with a cleaner chain: bring your own source image (skips Qwen) + Pixal3D/TRELLIS.2.
