#!/usr/bin/env python3
"""task_nexus_pro_icon.py

Automation Agent task: create/collect a high-fidelity "Nexus Pro" PNG app icon.

Reality constraint:
- Image generation happens in Antigravity via its `generate_image` tool.
- This task provides an evidence-first wrapper: it records the prompt, then
  ingests the resulting PNG and logs artifact hashes/size into the Brain.

Modes:
- Default (no flags): Prepared/no-op (learning pause)
- --run: start the task and print the canonical prompt (logs to brain)
- --ingest --png-path <file>: ingest an existing PNG (logs sha256, size, path)

Recommended usage (2-phase):
1) Start task + record prompt:
   python3 runner.py task_nexus_pro_icon.py --run
2) After Antigravity generates PNG, ingest:
   python3 runner.py task_nexus_pro_icon.py --ingest --png-path /path/to/icon.png

Output location:
- Copies ingested PNG to: projects/nexus-icons/nexus-pro-<ts>.png

"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict

from lib import AutomationAgentTask


REPO_ROOT = Path(__file__).resolve().parents[3]
# Per team request: store icon artifacts in projects/nexus-icons/
ARTIFACTS_DIR = REPO_ROOT / "projects" / "nexus-icons"

DEFAULT_PROMPT = (
    "High-fidelity iOS app icon for \"Nexus Pro\". Sleek modern glassmorphism style. "
    "Centered stylized orbital node forming an abstract \"N\" monogram (clean geometry, symmetrical, premium). "
    "Translucent frosted glass layers with subtle refraction, glossy highlights, soft neon gradient rim light (cyan → indigo), "
    "minimal dark backdrop (or fully transparent), strong silhouette readability at small sizes, "
    "no text, no watermark, no seafood, no busy background. Ultra crisp edges, premium product design aesthetic."
)

DEFAULT_NEGATIVE = "text, letters, watermark, photo realism, messy details, noisy background, cartoon, clipart, legacy mascot, crab, seafood"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _ensure_png(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PNG path not found: {path}")
    if path.suffix.lower() != ".png":
        raise ValueError(f"Expected a .png file, got: {path.name}")


def _ingest_png(src: Path) -> Dict[str, Any]:
    _ensure_png(src)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d-%H-%M-%S")
    dst = ARTIFACTS_DIR / f"nexus-pro-{ts}.png"
    shutil.copy2(src, dst)
    return {
        "source_path": str(src),
        "artifact_path": str(dst),
        "bytes": dst.stat().st_size,
        "sha256": sha256_file(dst),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-name", type=str, default="Icon Generation Proof", help="Name recorded in automation_tasks")
    ap.add_argument("--prompt", type=str, default="", help="Prompt to record (defaults to a Nexus Pro glassmorphism prompt)")
    ap.add_argument("--negative", type=str, default="", help="Negative prompt (if supported)")
    ap.add_argument("--size", type=str, default="1024x1024")
    ap.add_argument("--background", type=str, default="transparent")
    ap.add_argument("--run", action="store_true", help="Start task + record prompt (default: prepared/no-op)")
    ap.add_argument("--ingest", action="store_true", help="Ingest an existing PNG output from Antigravity")
    ap.add_argument("--png-path", type=str, default="", help="Path to the generated PNG to ingest")
    args = ap.parse_args()

    task_name = getattr(args, "task_name", None) or "Icon Generation Proof"

    task = AutomationAgentTask(
        name=task_name,
        description="Evidence-first wrapper for generating a Nexus Pro PNG icon via Antigravity generate_image, then ingesting the artifact.",
    )

    if not args.run and not args.ingest:
        print("[AutomationAgent] Prepared mode. Use --run to record prompt, then --ingest --png-path <file> to ingest PNG.")
        return 0

    task.start()

    try:
        prompt_payload = {
            "prompt": (args.prompt or DEFAULT_PROMPT),
            "negative": (args.negative or DEFAULT_NEGATIVE),
            "size": args.size,
            "background": args.background,
            "tool": "Antigravity generate_image",
        }
        task.step("Record Prompt", lambda: prompt_payload)
        print("\n=== Nexus Pro Icon Prompt ===\n")
        print(prompt_payload["prompt"])
        print("\nNegative (if supported):\n" + prompt_payload["negative"] + "\n")

        artifact = None
        if args.ingest:
            if not args.png_path:
                raise ValueError("--ingest requires --png-path")
            src = Path(args.png_path).expanduser().resolve()
            artifact = task.step("Ingest PNG Artifact", _ingest_png, src)

        final = {
            "status": "COMPLETED" if artifact else "PROMPT_RECORDED",
            "prompt": prompt_payload,
            "artifact": artifact,
        }
        task.finish(success=True, final_result=final)
        print(json.dumps(final, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
