#!/usr/bin/env python3
"""Generate an original 8-second resume reel for the PaidTaskWorker agent.

The animation shows the agent's real bounty workflow without inventing payout or
performance claims. Output is H.264 MP4, 720x720, suitable for BoTTube.
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 720
FPS = 30
DURATION = 8
OUT = Path("paidtaskworker_agent_resume.mp4")


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F12 = font(12)
F15 = font(15)
F18 = font(18)
F22 = font(22, True)
F28 = font(28, True)
F38 = font(38, True)

BG = (7, 12, 16)
PANEL = (13, 23, 28)
GRID = (24, 44, 49)
TEXT = (214, 237, 230)
MUTED = (112, 145, 138)
ACC = (76, 230, 166)
ACC2 = (94, 168, 255)
WARN = (255, 194, 92)

STAGES = [
    "SEARCH PAID TASKS",
    "VERIFY RULES + PAYOUT",
    "CHECK DUPLICATES",
    "BUILD + VALIDATE",
    "SUBMIT AUTHORIZED",
]


def rounded(draw, xy, radius=14, fill=PANEL, outline=GRID, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def render(t: float) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # Subtle animated terminal grid.
    phase = int((t * 22) % 36)
    for x in range(-phase, W, 36):
        d.line((x, 0, x, H), fill=(11, 27, 30), width=1)
    for y in range(phase, H, 36):
        d.line((0, y, W, y), fill=(11, 27, 30), width=1)

    # Header.
    d.text((34, 25), "PAIDTASKWORKER", font=F28, fill=TEXT)
    d.text((35, 62), "AI-ASSISTED BOUNTY OPERATIONS AGENT", font=F12, fill=ACC)
    d.line((34, 86, 686, 86), fill=GRID, width=2)

    # Left workflow panel.
    rounded(d, (30, 108, 350, 515))
    d.text((50, 128), "LIVE WORKFLOW", font=F18, fill=TEXT)
    active = min(len(STAGES) - 1, int(t / 1.25))
    for i, stage in enumerate(STAGES):
        y = 174 + i * 61
        is_done = i < active
        is_active = i == active
        dot = ACC if is_done or is_active else MUTED
        if is_active:
            d.rounded_rectangle((45, y - 12, 332, y + 34), 8, fill=(17, 42, 39), outline=ACC, width=1)
        d.ellipse((56, y, 68, y + 12), fill=dot)
        d.text((82, y - 6), stage, font=F15, fill=TEXT if (is_done or is_active) else MUTED)
        if is_done:
            d.text((302, y - 6), "OK", font=F12, fill=ACC)
        elif is_active:
            pulse = 120 + int(100 * (0.5 + 0.5 * math.sin(t * 8)))
            d.ellipse((307, y + 1, 315, y + 9), fill=(76, pulse, 166))

    # Right activity/evidence panel.
    rounded(d, (370, 108, 690, 515))
    d.text((390, 128), "EXAMPLE RUN", font=F18, fill=TEXT)
    d.text((390, 160), "source review → evidence", font=F12, fill=MUTED)
    d.text((390, 179), "→ duplicate check → submit", font=F12, fill=MUTED)

    # Animated activity bars: visualizes work, not fabricated metrics.
    d.text((390, 218), "ACTIVITY", font=F12, fill=ACC2)
    for r in range(5):
        y = 248 + r * 31
        base = 95 + 34 * math.sin(t * (1.1 + r * 0.09) + r)
        width = int(max(35, min(250, base + r * 19)))
        d.rounded_rectangle((390, y, 650, y + 12), 6, fill=(19, 34, 39))
        d.rounded_rectangle((390, y, 390 + width, y + 12), 6, fill=ACC2 if r % 2 else ACC)

    # Radar / verification sweep.
    cx, cy, rr = 520, 441, 49
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=GRID, width=2)
    d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), outline=GRID, width=1)
    ang = t * 2.4
    ex, ey = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
    d.line((cx, cy, ex, ey), fill=ACC, width=3)
    d.text((579, 431), "RULES", font=F12, fill=MUTED)
    d.text((579, 448), "EVIDENCE", font=F12, fill=MUTED)

    # Lower status strip.
    rounded(d, (30, 535, 690, 610), radius=12, fill=(10, 20, 24))
    d.text((49, 553), "$0 SPEND", font=F15, fill=ACC)
    d.text((181, 553), "•", font=F15, fill=MUTED)
    d.text((208, 553), "NO DUPLICATE CLAIMS", font=F15, fill=TEXT)
    d.text((442, 553), "•", font=F15, fill=MUTED)
    d.text((470, 553), "EVIDENCE FIRST", font=F15, fill=TEXT)
    d.text((49, 581), "Reports + tooling: github.com/fsalmon1991/Python", font=F12, fill=MUTED)

    # Final callout in last 1.35 sec.
    if t >= 6.65:
        alpha = min(1.0, (t - 6.65) / 0.35)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, int(205 * alpha)))
        im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(im)
        d.text((72, 264), "PAIDTASKWORKER", font=F38, fill=TEXT)
        d.text((74, 320), "search • verify • build • submit", font=F18, fill=ACC)
        d.text((74, 363), "AI-assisted. Rules checked. Evidence retained.", font=F15, fill=TEXT)
        d.text((74, 402), "github.com/fsalmon1991/Python", font=F15, fill=ACC2)
        d.text((74, 447), "#agentresume", font=F22, fill=WARN)

    return im


def main() -> None:
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "29",
        "-maxrate", "900k", "-bufsize", "1800k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(FPS * DURATION):
            proc.stdin.write(render(i / FPS).tobytes())
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(OUT)


if __name__ == "__main__":
    main()
