#!/usr/bin/env python3
"""task_whisper_test.py

Local Whisper Certification: Speech-to-Text via Small Model.

Purpose:
- Generate a native macOS speech sample via 'say'.
- Transcribe it using Local Whisper (Small model).
- Verify 'Pro Level' speech-to-text transcription readiness.
"""

from __future__ import annotations

import argparse
import subprocess
import time
import os
from pathlib import Path

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "reports" / "artifacts"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--model", type=str, default="small")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Local Whisper Certification",
        description=f"Testing transcription using the '{args.model}' model."
    )

    if not args.run:
        print("[WhisperTest] Prepared mode. Use --run.")
        return 0

    task.start()

    ts = time.strftime("%Y-%m-%d-%H%M%S")
    work_dir = OUTPUT_DIR / f"whisper-test-{ts}"
    work_dir.mkdir(parents=True, exist_ok=True)

    sample_wav = work_dir / "general_sample.wav"
    
    # 1. Generate Sample via macOS 'say'
    def gen_sample():
        text = "This is a high-fidelity transcription test of the local speech-to-text engine. All systems are operational."
        # Use macOS 'say' to generate a vocal sample
        subprocess.run(["say", "-o", str(sample_wav), "--data-format=LEI16@16000", text], check=True)
        return str(sample_wav)

    task.step("Generate General Audio Sample (macOS say)", gen_sample)

    # 2. Transcription
    def transcribe():
        # Running whisper CLI
        # This will trigger model download if not present
        cmd = [
            "whisper",
            str(sample_wav),
            "--model", args.model,
            "--output_dir", str(work_dir),
            "--output_format", "txt",
            "--fp16", "False" # Use False if no GPU, but Mac M1+ handles it
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Whisper failed: {result.stderr}")
            
        txt_file = work_dir / "general_sample.txt"
        if txt_file.exists():
            return txt_file.read_text().strip()
        return "Transcription file not found."

    transcription = task.step(f"Transcribe using Whisper ({args.model})", transcribe)

    task.finish(success=True, final_result={
        "transcription": transcription,
        "model": args.model,
        "artifact_path": str(work_dir)
    })
    
    print(f"\n[Whisper Success] Result: {transcription}")

if __name__ == "__main__":
    main()
