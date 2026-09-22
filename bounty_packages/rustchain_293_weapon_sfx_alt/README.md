# RustChain Arena — Alternate Weapon SFX Set

Original deterministic procedural weapon effects for RustChain bounty #293. This is an **alternate weapon set**, not a reuse of previously submitted audio. Every sample is synthesized by `generate_sfx.py` from mathematical oscillators and fixed-seed noise; there are no external samples, recordings, speech models, or third-party media.

## Cues

| File | Intended weapon | Design |
|---|---|---|
| `validator_pistol_alt.ogg` | Validator pistol | rising energy charge, crisp validation snap, descending plasma tail |
| `forker_shotgun_alt.ogg` | Forker shotgun | mechanical pre-pump followed by two staggered low blasts |
| `hashcannon_railgun_alt.ogg` | HashCannon railgun | accelerating computation ticks into a high-energy beam |
| `mempool_grenade_alt.ogg` | Mempool grenade | packet-like fuse pulses followed by a low cluster detonation |
| `double_spend_smgs_alt.ogg` | Double Spend SMGs | rapid alternating transaction-click bursts with a short mechanical tail |

All packaged assets are mono OGG Vorbis at 48 kHz. The `_alt` suffix deliberately avoids colliding with an already-integrated weapon pack and supports alternate skins/variants.

## Reproduce

```bash
python3 -m pip install numpy
python3 generate_sfx.py
```

Requires FFmpeg with `libvorbis`. Generation is deterministic because each noise source uses a fixed seed.

## Suggested integration

Copy the generated `.ogg` files into a distinct package path such as:

```text
pk3_build/sound/weapons/rustchain_arena_alt/
```

Then map them to the corresponding weapon event hooks. Keeping this path separate avoids overwriting the existing RustChain weapon pack.

## Validation

The GitHub Actions workflow `.github/workflows/rustchain-293-sfx.yml` regenerates the set, checks each file with `ffprobe`, records peak/RMS data with FFmpeg `astats`, writes SHA-256 hashes, and publishes a ZIP artifact. No in-engine Xonotic playtest is claimed.

## License

CC0 1.0 Universal. See `LICENSE`.
