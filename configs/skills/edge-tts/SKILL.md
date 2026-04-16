---
name: edge-tts
description: FREE/Local-ish text-to-speech using Microsoft Edge's engine.
homepage: https://github.com/rany2/edge-tts
metadata: {
    "nexus": { "emoji": "🔊", "requires": { "libs": ["edge-tts"] } },
}
---

# Edge TTS (Free)

This skill provides natural-sounding voice feedback using Microsoft Edge's free
TTS engine. While it requires a network connection to fetch the audio, it does
not require an API key or a paid subscription.

## Capabilities

- **High-Quality Voices**: Access to numerous neural voices (e.g.,
  `en-US-AndrewNeural`, `en-US-EmmaNeural`).
- **Customization**: Support for rate, volume, and pitch adjustments.
- **Offline Playback**: Generates MP3 files that can be played back at any time.

## Usage

Run the voice feedback task: `python3 runner.py task_voice_feedback.py --run`

## Governance

- **Zero-Cost**: Leverage public endpoints without billing.
- **Privacy**: Text is sent to Microsoft for synthesis, but no account or
  persistent ID is required.
