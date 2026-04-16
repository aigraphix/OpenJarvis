#!/usr/bin/env python3
"""task_voice_command.py

Autonomous Voice Assistant Loop: Listen -> Transcribe -> Execute -> Speak.

Purpose:
- Record a 5-second audio clip from the Mac microphone.
- Transcribe the command using Local Whisper-Free.
- Respond with a neural voice using Edge TTS.
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
WHISPER_BIN = "/opt/homebrew/bin/whisper"

async def _speak(text: str, output_path: Path):
    import edge_tts
    voice = "en-US-AndrewNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--seconds", type=int, default=5)
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Voice Command Loop",
        description=f"Listening for {args.seconds} seconds..."
    )

    if not args.run:
        print("[VoiceAssistant] Prepared mode. Use --run to start listening.")
        return 0

    task.start()

    ts = time.strftime("%Y-%m-%d-%H%M%S")
    work_dir = OUTPUT_DIR / f"voice-cmd-{ts}"
    work_dir.mkdir(parents=True, exist_ok=True)
    
    input_wav = work_dir / "command_input.wav"
    output_mp3 = work_dir / "response.mp3"

    # 1. Record Audio
    def record():
        print(f"\n🎙️  LISTENING NOW ({args.seconds}s)...")
        # Build command
        cmd = [
            "ffmpeg", "-y",
            "-f", "avfoundation",
            "-i", ":2",
            "-t", str(args.seconds + 1), # Add extra second for buffer
            str(input_wav)
        ]
        # Start recording in background for 1 second before signaling user
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1.5) # Wait for hardware to warm up
        print(">>> START SPEAKING NOW <<<")
        proc.wait() # Wait for the full duration
        print(">>> STOP <<<")
        return str(input_wav)

    task.step(f"Record Microphone Input ({args.seconds}s)", record)

    # 2. Transcribe
    def transcribe():
        cmd = [
            WHISPER_BIN,
            str(input_wav),
            "--model", "small",
            "--output_dir", str(work_dir),
            "--output_format", "txt",
            "--fp16", "False"
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        
        txt_file = work_dir / "command_input.txt"
        if txt_file.exists():
            return txt_file.read_text().strip()
        return "No command detected."

    command_text = task.step("Transcribe Command (Whisper-Free)", transcribe)
    print(f"\n👤 You said: \"{command_text}\"")

    # 3. Simple Logic Engine
    def process_logic():
        cmd_lower = command_text.lower()
        if "hello" in cmd_lower or "hi" in cmd_lower:
            response = "Hello Danny! I am operational and ready to assist you. All free tier superpowers are online."
        elif "status" in cmd_lower or "skills" in cmd_lower or "capabilities" in cmd_lower:
            response = "I have several pro-level capabilities: I can transcribe audio using Whisper-Free, generate neural voice feedback with Edge TTS, process data using Excel Mastery, and automatically reflect on system wins. What would you like me to do?"
        elif "audit" in cmd_lower or "excel" in cmd_lower:
            response = "I can generate a professional Excel system audit and read it back locally. You can run it by asking for a system audit."
        elif "viz" in cmd_lower or "chart" in cmd_lower or "icon" in cmd_lower:
            response = "I have advanced visualization powers. I can generate performance charts and custom SVG icons for your projects."
        elif "report" in cmd_lower or "document" in cmd_lower:
            response = "I am capable of high-fidelity document generation. I can render structured reports into both PDF and Word formats."
        elif "reflect" in cmd_lower or "learn" in cmd_lower:
            response = "I can trigger my self-improvement logic to analyze recent missions and update our Shared Brain with new capabilities."
        elif "cleanup" in cmd_lower:
            response = "Understood. I can trigger the desktop cleanup automation to keep your workspace organized."
        elif "thank" in cmd_lower:
            response = "You are very welcome. It is a pleasure to work with you."
        else:
            response = f"I heard you say: {command_text}. I am standing by for your instructions."
        return response

    response_text = task.step("Process Command Logic", process_logic)

    # 4. Speak Back
    def speak_back():
        asyncio.run(_speak(response_text, output_mp3))
        # Play it automatically if possible (macOS 'afplay')
        subprocess.run(["afplay", str(output_mp3)])
        return response_text

    task.step("Generate & Play Voice Feedback (Edge TTS)", speak_back)

    task.finish(success=True, final_result={
        "user_command": command_text,
        "bot_response": response_text,
        "artifacts": str(work_dir)
    })
    
    print(f"\n🤖 Bot: \"{response_text}\"")

if __name__ == "__main__":
    main()
