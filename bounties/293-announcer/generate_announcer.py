#!/usr/bin/env python3
"""Generate an original Xonotic RustChain Arena announcer voice-line set.

Speech is synthesized locally with eSpeak and post-processed with ffmpeg.
No samples, recordings, or network services are used.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "audio"
OUT.mkdir(exist_ok=True)

LINES = [
    ("double_spend", "Double spend!", 158, 56),
    ("triple_fork", "Triple fork!", 155, 54),
    ("consensus_reached", "Consensus reached!", 143, 50),
    ("calculating", "Calculating...", 135, 42),
    ("building_momentum", "Building momentum!", 150, 52),
    ("singularity", "Singularity!", 138, 48),
    ("block_confirmed", "Block confirmed!", 148, 50),
    ("chain_reorganization", "Chain reorganization!", 145, 46),
    ("attack_51_detected", "Fifty one percent attack detected!", 150, 44),
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    espeak = shutil.which("espeak")
    ffmpeg = shutil.which("ffmpeg")
    if not espeak or not ffmpeg:
        raise SystemExit("Requires espeak and ffmpeg in PATH")

    generated = []
    with tempfile.TemporaryDirectory(prefix="rustchain-announcer-") as tmp:
        tmp = Path(tmp)
        for stem, text, speed, pitch in LINES:
            raw = tmp / f"{stem}.wav"
            out = OUT / f"{stem}.ogg"
            run([
                espeak,
                "-v", "en-us",
                "-s", str(speed),
                "-p", str(pitch),
                "-a", "175",
                "-w", str(raw),
                text,
            ])
            af = (
                "highpass=f=90,"
                "lowpass=f=9000,"
                "equalizer=f=1800:t=q:w=1.1:g=3.0,"
                "acompressor=threshold=0.12:ratio=3:attack=5:release=90:makeup=1.6,"
                "aecho=0.75:0.50:55:0.18,"
                "alimiter=limit=0.88"
            )
            run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(raw),
                "-af", af,
                "-ac", "1", "-ar", "48000",
                "-c:a", "libvorbis", "-q:a", "5",
                str(out),
            ])
            generated.append({"file": out.name, "line": text, "sha256": sha256(out)})

    manifest = {
        "set": "RustChain Arena announcer voice lines",
        "generator": "eSpeak + ffmpeg, local/offline",
        "sample_rate_hz": 48000,
        "channels": 1,
        "codec": "Ogg Vorbis",
        "license": "GPL-3.0-or-later",
        "files": generated,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
