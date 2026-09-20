#!/usr/bin/env python3
"""Verify codec/container, sample rate, channels, duration, hashes and PCM energy."""
from __future__ import annotations
import hashlib, json, math, struct, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "manifest.json").read_text())
rows = []
for item in manifest["files"]:
    p = ROOT / "audio" / item["file"]
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest == item["sha256"], (p, "sha mismatch")
    probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels:format=duration",
        "-of", "json", str(p)
    ], text=True)
    meta = json.loads(probe)
    s = meta["streams"][0]
    duration = float(meta["format"]["duration"])
    assert s["codec_name"] == "vorbis"
    assert int(s["sample_rate"]) == 48000
    assert int(s["channels"]) == 1
    assert 0.45 <= duration <= 4.5
    pcm = subprocess.check_output([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(p),
        "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "48000", "-"
    ])
    vals = struct.unpack("<" + "h" * (len(pcm)//2), pcm)
    rms = math.sqrt(sum(v*v for v in vals) / len(vals))
    peak = max(abs(v) for v in vals)
    assert rms > 250, (p, "too quiet")
    assert peak < 32767, (p, "clipped")
    rows.append({
        "file": item["file"], "duration_s": round(duration, 3),
        "rms": round(rms, 1), "peak": peak, "sha256": digest,
    })
print(json.dumps(rows, indent=2))
