#!/usr/bin/env python3
"""Deterministic procedural weapon SFX for the Xonotic RustChain Arena.

All audio is synthesized from mathematical waveforms/noise generated in this
script. No external samples, recordings, speech models, or copyrighted assets
are used.
"""
from __future__ import annotations

import hashlib
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48_000
OUT = Path(__file__).resolve().parent / "audio"
TMP = Path(__file__).resolve().parent / ".wav_tmp"


def env(n: int, attack: float = 0.01, release: float = 0.20) -> np.ndarray:
    t = np.arange(n) / SR
    dur = n / SR
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    r = np.clip((dur - t) / max(release, 1e-6), 0, 1)
    return np.minimum(a, r)


def lp_noise(rng: np.random.Generator, n: int, smooth: int = 9) -> np.ndarray:
    x = rng.standard_normal(n)
    k = np.ones(smooth) / smooth
    return np.convolve(x, k, mode="same")


def chirp(t: np.ndarray, f0: float, f1: float, power: float = 1.0, phase: float = 0.0) -> np.ndarray:
    u = np.clip(t / max(t[-1], 1e-9), 0, 1) ** power
    f = f0 + (f1 - f0) * u
    ph = phase + 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def normalize(x: np.ndarray, peak: float = 0.88) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    p = float(np.max(np.abs(x))) if x.size else 1.0
    if p > 0:
        x = x * (peak / p)
    return np.clip(x, -0.999, 0.999)


def write_wav(path: Path, x: np.ndarray) -> None:
    pcm = (normalize(x) * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def validator_pistol() -> np.ndarray:
    dur = 0.56
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(1101)
    charge = chirp(t, 520, 1680, power=0.65) * np.exp(-5.2 * t)
    snap = np.sin(2*np.pi*2280*t + 1.4*np.sin(2*np.pi*91*t)) * np.exp(-15*t)
    click = lp_noise(rng, n, 3) * np.exp(-38*t)
    tail = chirp(t, 980, 250, power=1.5, phase=1.2) * np.exp(-7.8*t)
    return (0.34*charge + 0.46*snap + 0.14*click + 0.28*tail) * env(n, .002, .12)


def forker_shotgun() -> np.ndarray:
    dur = 0.92
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(2202)
    x = np.zeros(n)
    pump_t = np.clip(t / 0.19, 0, 1)
    x += 0.17 * np.sin(2*np.pi*(180 + 560*pump_t)*t) * np.exp(-16*np.maximum(t-0.02,0))
    for at, amp, f in [(0.22, 1.0, 92), (0.305, 0.78, 118)]:
        tau = np.maximum(t-at, 0)
        gate = (t >= at).astype(float)
        boom = (np.sin(2*np.pi*f*tau) + 0.36*np.sin(2*np.pi*(f*2.15)*tau)) * np.exp(-7.5*tau)
        burst = lp_noise(rng, n, 5) * np.exp(-13*tau) * gate
        x += gate * amp * (0.49*boom + 0.38*burst)
    return x * env(n, .003, .20)


def hashcannon_railgun() -> np.ndarray:
    dur = 1.10
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3303)
    tick = np.zeros(n)
    for k, at in enumerate(np.linspace(0.03, 0.42, 13)):
        idx = int(at*SR)
        length = min(int(.025*SR), n-idx)
        tt = np.arange(length)/SR
        tick[idx:idx+length] += (0.08 + 0.012*k) * np.sin(2*np.pi*(650+55*k)*tt) * np.exp(-80*tt)
    beam_gate = (t >= .43).astype(float)
    tau = np.maximum(t-.43, 0)
    beam = chirp(tau + 1e-7, 2400, 620, power=0.9) * np.exp(-4.3*tau) * beam_gate
    harmonic = np.sin(2*np.pi*1240*tau + 2.0*np.sin(2*np.pi*36*tau)) * np.exp(-5.5*tau) * beam_gate
    noise = lp_noise(rng, n, 17) * np.exp(-8*tau) * beam_gate
    return (tick + .61*beam + .28*harmonic + .10*noise) * env(n, .0015, .25)


def mempool_grenade() -> np.ndarray:
    dur = 1.18
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(4404)
    x = np.zeros(n)
    for k, at in enumerate([.03, .10, .18, .27, .37, .48]):
        tau = np.maximum(t-at, 0)
        gate = (t >= at).astype(float)
        x += gate * .14*np.sin(2*np.pi*(720+110*k)*tau) * np.exp(-28*tau)
    tau = np.maximum(t-.58, 0)
    gate = (t >= .58).astype(float)
    boom = (np.sin(2*np.pi*62*tau) + .44*np.sin(2*np.pi*126*tau)) * np.exp(-4.8*tau)
    debris = lp_noise(rng, n, 7) * np.exp(-7.2*tau)
    x += gate * (.72*boom + .42*debris)
    return x * env(n, .002, .28)


def double_spend_smgs() -> np.ndarray:
    dur = 0.88
    n = int(SR * dur)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5505)
    x = np.zeros(n)
    for k, at in enumerate(np.arange(.03, .74, .072)):
        idx = int(at*SR)
        length = min(int(.075*SR), n-idx)
        if length <= 0:
            continue
        tt = np.arange(length)/SR
        f = 390 if k % 2 == 0 else 470
        click = np.sin(2*np.pi*f*tt) * np.exp(-44*tt)
        crack = rng.standard_normal(length) * np.exp(-58*tt)
        x[idx:idx+length] += .35*click + .18*crack
    tail = np.sin(2*np.pi*155*t) * np.exp(-6*np.maximum(t-.72,0)) * (t >= .72)
    return (x + .12*tail) * env(n, .001, .12)


SOUNDS = {
    "validator_pistol_alt": validator_pistol,
    "forker_shotgun_alt": forker_shotgun,
    "hashcannon_railgun_alt": hashcannon_railgun,
    "mempool_grenade_alt": mempool_grenade,
    "double_spend_smgs_alt": double_spend_smgs,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    for name, fn in SOUNDS.items():
        wav = TMP / f"{name}.wav"
        ogg = OUT / f"{name}.ogg"
        write_wav(wav, fn())
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(wav), "-c:a", "libvorbis", "-q:a", "5", str(ogg)
        ], check=True)
        print(f"{name}.ogg sha256={hashlib.sha256(ogg.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
