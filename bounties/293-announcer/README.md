# RustChain Arena announcer voice-line set

Original announcer lines for **Xonotic RustChain Arena**, prepared for bounty `Scottcjn/rustchain-bounties#293`.

## Contents

Nine short arena callouts matching the bounty's requested announcer phrases:

- `double_spend.ogg` — “Double spend!”
- `triple_fork.ogg` — “Triple fork!”
- `consensus_reached.ogg` — “Consensus reached!”
- `calculating.ogg` — “Calculating...”
- `building_momentum.ogg` — “Building momentum!”
- `singularity.ogg` — “Singularity!”
- `block_confirmed.ogg` — “Block confirmed!”
- `chain_reorganization.ogg` — “Chain reorganization!”
- `attack_51_detected.ogg` — “Fifty one percent attack detected!”

All files are **mono 48 kHz OGG Vorbis**. They use only locally synthesized speech (eSpeak) plus deterministic ffmpeg post-processing; there are no external recordings, samples, API calls, or copied sound assets.

Suggested package location:

```text
pk3_build/sound/announcer/rustchain/
```

Example QuakeC path:

```c
precache_sound("announcer/rustchain/consensus_reached.ogg");
sound(self, CHAN_VOICE, "announcer/rustchain/consensus_reached.ogg", VOL_BASE, ATTEN_NONE);
```

## Regenerate

Requires `espeak` and `ffmpeg`:

```bash
python3 generate_announcer.py
python3 verify_announcer.py
```

`manifest.json` records a SHA-256 for every packaged file. `verification.json` is the captured verifier output from this submitted package.

## Design notes

The source voice is intentionally synthetic: the game vocabulary is machine/consensus themed, so a robotic public-address voice fits better than pretending to be a human announcer. Processing is restrained to preserve intelligibility: rumble removal, presence boost, compression, short slapback echo, and limiting.

## License

This package's scripts, arrangement, post-processing choices, documentation, and generated assets are offered under **GPL-3.0-or-later**, a license compatible with the GPL-licensed DarkPlaces/Xonotic codebase. The package contains no third-party recordings.

AI assistance was used to design and validate the procedural package. The actual audio assets were generated and tested locally from the included script.
