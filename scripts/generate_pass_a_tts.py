#!/usr/bin/env python3
"""Generate 16 kHz mono English TTS WAVs for Pass A (macOS `say`)."""

import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = "Samantha"
RATE = "165"


def main():
    phrases = json.loads((ROOT / "eval-set.json").read_text())["phrases"]
    out_dir = ROOT / "pass-a-audio"
    out_dir.mkdir(exist_ok=True)
    clips = []

    for phrase in phrases:
        aiff = out_dir / f"{phrase['phrase_key']}.aiff"
        wav = out_dir / f"{phrase['phrase_key']}.wav"
        if wav.exists() and wav.stat().st_size > 4096:
            with wave.open(str(wav), "rb") as handle:
                duration = handle.getnframes() / handle.getframerate()
            clips.append({
                "phrase_key": phrase["phrase_key"],
                "file": wav.name,
                "duration_sec": round(duration, 2),
            })
            print(f"{phrase['phrase_key']:24} {duration:.2f}s (existing)")
            continue
        subprocess.run(
            ["say", "-v", VOICE, "-r", RATE, "-o", str(aiff), phrase["en_gold"]],
            check=True,
        )
        subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16@16000", str(aiff), str(wav)],
            check=True,
        )
        aiff.unlink(missing_ok=True)
        with wave.open(str(wav), "rb") as handle:
            duration = handle.getnframes() / handle.getframerate()
        clips.append({
            "phrase_key": phrase["phrase_key"],
            "file": wav.name,
            "duration_sec": round(duration, 2),
        })
        print(f"{phrase['phrase_key']:24} {duration:.2f}s")

    manifest = {
        "eval_set_id": "aco_mission_eval_v1",
        "recording_pass": "A",
        "spoken_language": "en",
        "contributor_id": "tts_en_v1",
        "tts_engine": "macos_say",
        "tts_voice": VOICE,
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "pcm_s16le",
        "clips": clips,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
