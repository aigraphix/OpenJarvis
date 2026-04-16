#!/usr/bin/env python3
"""task_image_gen_openai.py

Automation Agent task: generate PNG images via the installed `openai-image-gen` skill.

Uses:
- skills/openai-image-gen/scripts/gen.py
- AutomationAgentTask for Brain logging (automation_tasks/automation_steps)

Safe defaults:
- "learning pause" by default (no-op). Use --run to execute.

Example:
  python3 runner.py task_image_gen_openai.py -- --run --prompt "a rocket astronaut" --count 2

Outputs:
- Writes to: reports/artifacts/openai-image-gen-<ts>/
- Logs artifact metadata (paths + sha256 + size) in automation_tasks.result

Requires:
- OPENAI_API_KEY in environment for gen.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from lib import AutomationAgentTask


REPO_ROOT = Path(__file__).resolve().parents[3]
GEN_PY = REPO_ROOT / "skills" / "openai-image-gen" / "scripts" / "gen.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_gen_py(args: List[str], out_dir: Path) -> Dict[str, Any]:
    if not GEN_PY.exists():
        raise FileNotFoundError(f"Missing generator script: {GEN_PY}")

    cmd = ["python3", str(GEN_PY), "--out-dir", str(out_dir)] + args
    p = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"gen.py failed (code={p.returncode})\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    return {"cmd": cmd, "stdout": p.stdout, "stderr": p.stderr, "exit_code": p.returncode}


def collect_artifacts(out_dir: Path) -> Dict[str, Any]:
    files = []
    for p in sorted(out_dir.glob("*")):
        if p.is_file():
            files.append(
                {
                    "name": p.name,
                    "path": str(p),
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )
    return {"out_dir": str(out_dir), "files": files}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="Execute image generation (default: prepared/no-op)")

    # pass-through options for gen.py
    ap.add_argument("--prompt", type=str, default="", help="Prompt to generate (default: gen.py random prompts)")
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--model", type=str, default="gpt-image-1")
    ap.add_argument("--size", type=str, default="")
    ap.add_argument("--quality", type=str, default="")
    ap.add_argument("--background", type=str, default="")
    ap.add_argument("--output-format", type=str, default="")
    ap.add_argument("--style", type=str, default="")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Image Generation (openai-image-gen)",
        description="Generate images via OpenAI Images API using the openai-image-gen skill.",
    )

    if not args.run:
        print("[AutomationAgent] Prepared mode (learning pause). Use --run to execute.")
        return 0

    if not (os.environ.get("OPENAI_API_KEY") or "").strip():
        print("Missing OPENAI_API_KEY; cannot run openai-image-gen.")
        # still journal failure to brain
        task.start()
        task.finish(success=False, final_result={"error": "Missing OPENAI_API_KEY"})
        return 2

    out_dir = REPO_ROOT / "reports" / "artifacts" / f"openai-image-gen-{time.strftime('%Y-%m-%d-%H-%M-%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    passthrough = [
        "--count",
        str(args.count),
        "--model",
        args.model,
    ]
    if args.prompt:
        passthrough += ["--prompt", args.prompt]
    if args.size:
        passthrough += ["--size", args.size]
    if args.quality:
        passthrough += ["--quality", args.quality]
    if args.background:
        passthrough += ["--background", args.background]
    if args.output_format:
        passthrough += ["--output-format", args.output_format]
    if args.style:
        passthrough += ["--style", args.style]

    task.start()
    try:
        run_info = task.step("Generate Images (gen.py)", run_gen_py, passthrough, out_dir)
        artifacts = task.step("Collect Artifacts", collect_artifacts, out_dir)

        final = {
            "status": "COMPLETED",
            "run": run_info,
            "artifacts": artifacts,
        }
        task.finish(success=True, final_result=final)
        print(json.dumps(final, indent=2))
        return 0
    except Exception as e:
        task.finish(success=False, final_result={"error": str(e), "out_dir": str(out_dir)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
