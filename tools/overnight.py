#!/usr/bin/env python3
"""Overnight batch: prompt -> Qwen-Image -> matte -> Hunyuan3D (shape+paint) -> Blender finish.

    python3 tools/overnight.py                  # all props in prompts/props.json
    python3 tools/overnight.py --only barrel,chest --faces 20000 --seed 7

Resumable: a stage whose output file exists is skipped. One prop failing never stops the
batch. Every stage is timed into runs/<date>/<prop>/result.json; then tools/report.py is run.
Run only after tools/setup.sh and tools/fetch-weights.sh --yes.
"""
import argparse, datetime, json, subprocess, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "vendor" / "image-to-3dlab"
LABPY = LAB / ".venv" / "bin" / "python"
HYPY = LAB / "hunyuan_mlx" / "shape" / ".venv" / "bin" / "python"
SD = LAB / "vendor" / "sdcpp"
HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"  # lab's bootstrap stores Qwen weights here
STAGE_TIMEOUT =60 * 45


def sh(cmd, log, cwd=None):
    with open(log, "a") as f:
        f.write(f"\n$ {' '.join(map(str, cmd))}\n"); f.flush()
        subprocess.run(list(map(str, cmd)), cwd=cwd, stdout=f, stderr=subprocess.STDOUT,
                       check=True, timeout=STAGE_TIMEOUT)


def qwen_weights():
    def pick(pattern):
        hits = sorted(SD.rglob(pattern)) or sorted(HF_CACHE.rglob(pattern))
        if not hits:
            raise FileNotFoundError(f"missing Qwen weight {pattern} under {SD}; run fetch-weights.sh")
        return hits[0]
    return pick("qwen_image_2.1-Q8_0.gguf"), pick("qwen_image_2.1_vae_bf16.safetensors"), pick("Qwen3VL-8B-Instruct-Q4_K_M.gguf")


def stage(res, name, out, fn):
    if out.exists():
        res["stages"][name] = {"skipped": True}; return
    t = time.time(); fn()
    res["stages"][name] = {"seconds": round(time.time() - t, 1)}
    if not out.exists():
        raise RuntimeError(f"stage {name} produced no {out.name}")


def run_prop(prop, style, outdir, args):
    outdir.mkdir(parents=True, exist_ok=True)
    log = outdir / "run.log"
    res = {"id": prop["id"], "subject": prop["subject"], "ok": False, "stages": {}}
    png, matted, raw, final = outdir / "source.png", outdir / "matted.png", outdir / "raw.glb", outdir / "final.glb"
    try:
        diff, vae, llm = qwen_weights()
        prompt = f"{prop['subject']}, {style}"
        stage(res, "qwen_image", png, lambda: sh([
            SD / "sd-cli", "--diffusion-model", diff, "--vae", vae, "--llm", llm, "-p", prompt,
            "--cfg-scale", 2.5, "--sampling-method", "euler", "--steps", 20, "-W", 1024, "-H", 1024,
            "--seed", args.seed, "--diffusion-fa", "-o", png], log))
        stage(res, "matte", matted, lambda: sh([LABPY, ROOT / "tools" / "matte.py", png, matted], log))
        stage(res, "hunyuan_shape_paint", raw, lambda: sh([
            HYPY, "scripts/hunyuan_mlx_xiong_generate.py", matted, raw, "--model", "2.0"], log, cwd=LAB))
        try:  # finish is best-effort: the raw GLB is still a result
            stage(res, "finish_blender", final, lambda: sh([
                LABPY, "scripts/retopo_repaint.py", raw, matted, final,
                "--faces", args.faces, "--skip-paint"], log, cwd=LAB))
        except Exception as e:
            res["stages"]["finish_blender"] = {"failed": str(e)[:300]}
        res["ok"] = raw.exists()
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
        with open(log, "a") as f: f.write(traceback.format_exc())
    (outdir / "result.json").write_text(json.dumps(res, indent=2))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--faces", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    args = ap.parse_args()
    cfg = json.loads((ROOT / "prompts" / "props.json").read_text())
    want = set(filter(None, args.only.split(",")))
    base = ROOT / "runs" / args.date
    t0 = time.time()
    results = [run_prop(p, cfg["style"], base / p["id"], args)
               for p in cfg["props"] if not want or p["id"] in want]
    print(f"{sum(r['ok'] for r in results)}/{len(results)} ok in {(time.time()-t0)/60:.1f} min")
    subprocess.run([sys.executable, str(ROOT / "tools" / "report.py"), args.date])


if __name__ == "__main__":
    main()
