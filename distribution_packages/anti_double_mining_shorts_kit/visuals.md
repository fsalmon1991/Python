# 9:16 Visual / Capture Plan

Canvas: **1080×1920 vertical**, 30 fps. Use only public RustChain source screens plus original text/diagram cards.

| Time | Narration beat | Exact visual |
|---|---|---|
| 0:00–0:05 | One machine, five miner IDs | Original card: one CPU icon/box on top, five text labels below (`miner-a`…`miner-e`). Large overlay: `5 IDs = 5 REWARDS?` |
| 0:05–0:15 | Anti-double-mining path | Screen-record `docs/ISSUE_1449_ANTI_DOUBLE_MINING.md`; frame the problem statement that says a single machine could run multiple `miner_id` values and receive separate rewards. |
| 0:15–0:27 | Machine identity hash | Screen-record `node/anti_double_mining.py`; search for `compute_machine_identity_hash`. Crop around the function name and input arguments. Overlay: `architecture + stable fingerprint → machine identity`. |
| 0:27–0:38 | Group duplicates / representative | Show the implementation-documentation list containing `detect_duplicate_identities()` and `select_representative_miner()`. Animate five miner labels collapsing into one machine group, then highlight one representative. |
| 0:38–0:47 | One CPU, one vote | Cut to the RIP-200 module header showing `Round-Robin Consensus (1 CPU = 1 Vote)`. Overlay: `MINER ID IS NOT THE PHYSICAL VOTE`. |
| 0:47–0:55 | Limits / close | Original caution card: `NOT UNIVERSAL SYBIL-PROOFING`. Beneath: `same-node epoch enforcement · documented cross-node limits`. Final line: `Changing the ID should not clone the CPU.` |

## Capture instructions

1. Use the commit-pinned source links in `SOURCES.md`.
2. Browser zoom 175–200% so the relevant code/doc line is readable in a vertical crop.
3. Keep repository + file path visible whenever showing source.
4. Never show API keys, wallet secrets, private tabs, notifications, or production admin interfaces.
5. Do not demonstrate an attack against a live node. The short explains public source behavior only.
6. Keep the final edit under 60 seconds; recommended cut is ~52 seconds.

## Rights

All cards, diagrams, captions, and edit instructions here are original. Source screens are used only to show the cited public code/documentation. No third-party music, stock footage, or unlicensed imagery is required.