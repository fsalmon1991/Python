# Sources / Claim Map

Reviewed upstream snapshot: `Scottcjn/Rustchain` commit `217ba85ef9cab3daac0da7b822c79437693444df`.

## Claim 1 — one physical machine running multiple miner IDs can otherwise multiply rewards

Source:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/docs/ISSUE_1449_ANTI_DOUBLE_MINING.md

Relevant public documentation states that without anti-double-mining enforcement a single machine could run multiple miner instances with different `miner_id` values and receive separate rewards for the same epoch, violating the RIP-200 “one CPU = one vote” principle.

## Claim 2 — implementation derives a machine identity from architecture and fingerprint information

Sources:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/anti_double_mining.py
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/docs/ISSUE_1449_ANTI_DOUBLE_MINING.md

Relevant functions documented/implemented:
- `normalize_fingerprint()` — extracts stable hardware characteristics.
- `compute_machine_identity_hash()` — generates a machine identity from `device_arch` plus normalized fingerprint information.
- `detect_duplicate_identities()` — finds machine identities associated with multiple miner IDs.

## Claim 3 — duplicate miner IDs sharing one machine identity are reduced to a representative for reward treatment

Sources:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/anti_double_mining.py
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/docs/ISSUE_1449_ANTI_DOUBLE_MINING.md

The implementation/documentation exposes `select_representative_miner()` and the full anti-double-mining reward/settlement path. The package deliberately says “selects one representative for reward treatment” rather than claiming miner IDs are deleted or globally banned.

## Claim 4 — this supports RIP-200’s “one CPU = one vote” principle

Source:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/rip_200_round_robin_1cpu1vote.py

The module header names `RIP-200: Round-Robin Consensus (1 CPU = 1 Vote)` and describes equal block-production turns per CPU.

## Claim 5 — documented limits exist; the mechanism is not universal Sybil-proofing

Sources:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/security/attestation-replay-attack/README.md — documents that machine-identity deduplication at epoch settlement is local to a node and discusses cross-node replay limitations.
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/submissions/self-audits/bosschaos-anti_double_mining-7458.md — documents identity-rotation limitations across epochs.

## Editorial guardrails

- Do not say “double mining is impossible.”
- Do not imply global cross-node deduplication when describing the reviewed implementation.
- Do not publish attack instructions or production exploitation steps.
- Keep the short focused on the defensive design goal and its documented scope.