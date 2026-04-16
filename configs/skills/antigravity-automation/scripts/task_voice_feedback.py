#!/usr/bin/env python3
"""task_voice_feedback.py

Edge TTS Certification: Natural Voice Feedback.

Purpose:
- Install edge-tts library.
- Generate a high-quality MP3 voice sample.
- Demonstrate "Superpower" level voice feedback.
"""

from __future__ import annotations

import argparse
import subprocess
import time
import asyncio
import os
from pathlib import Path

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "reports" / "artifacts"

async def _speak(text: str, output_path: Path):
    import edge_tts
    # Using a professional male voice for the test
    voice = "en-US-AndrewNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Edge TTS: Voice Certification",
        description="Generating high-fidelity voice feedback using Edge's engine."
    )

    if not args.run:
        print("[VoiceFeedback] Prepared mode. Use --run.")
        return 0

    task.start()

    # 1. Install Dependencies
    def install_deps():
        # Using --break-system-packages for this managed environment
        subprocess.run(["python3", "-m", "pip", "install", "--user", "--break-system-packages", "edge-tts"], check=True)
        return "edge-tts library installed."

    task.step("Install edge-tts library", install_deps)

    ts = time.strftime("%Y-%m-%d-%H%M%S")
    work_dir = OUTPUT_DIR / f"voice-test-{ts}"
    work_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = work_dir / "voice_handshake.mp3"

    # 2. Generate Voice
    def gen_voice():
        text = "Hello. This is a demonstration of our new voice feedback system. I am now capable of providing natural sounding verbal updates for all our automation tasks. Mission successful."
        asyncio.run(_speak(text, mp3_path))
        return str(mp3_path)

    task.step("Generate Neural Voice Sample (MP3)", gen_voice)

    # 3. Verify
    def verify():
        if mp3_path.exists() and mp3_path.stat().st_size > 1000:
            return f"MP3 generated successfully: {mp3_path.name} ({mp3_path.stat().st_size} bytes)"
        raise RuntimeError("Voice generation failed or file is too small.")

    verification = task.step("Verify Audio Artifact", verify)

    task.finish(success=True, final_result={
        "verification": verification,
        "artifact_path": str(mp3_path)
    })
    
    print(f"\n[Voice Success] Result: {verification}")

if __name__ == "__main__":
    main()
