# Sources / Claim Map

Reviewed upstream snapshot: `Scottcjn/Rustchain` commit `217ba85ef9cab3daac0da7b822c79437693444df`.

## Claim 1 — RIP-200 is deterministic round-robin, “1 CPU = 1 Vote”

Source:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/rip_200_round_robin_1cpu1vote.py

Relevant source text in the module header:
- `RIP-200: Round-Robin Consensus (1 CPU = 1 Vote)`
- `Block production: Deterministic rotation (no lottery)`
- `Rewards: Weighted by time-decaying antiquity multiplier`
- `Anti-pool: Each CPU gets equal block production turns`

Use in script: supports the distinction between block-production turns and reward weighting.

## Claim 2 — the current node reward table assigns `vax` a 3.5x base antiquity multiplier

Source:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/rip_200_round_robin_1cpu1vote.py

Relevant entry:
- `"vax": 3.5` — comment identifies DEC VAX (1977).

Independent public-repo cross-checks at the same reviewed commit:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/CPU_ANTIQUITY_SYSTEM.md — lists `vax` / DEC VAX at 3.5.
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/README.md — lists DEC VAX-11/780 (1977) at 3.5x.

Use in script: supports only the wording **3.5x base antiquity multiplier / base weight**. It does not support a guarantee of 3.5x realized earnings.

## Claim 3 — reward allocation uses time-aged antiquity weights rather than treating 3.5x as a fixed guaranteed payout

Sources:
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/rip_200_round_robin_1cpu1vote.py — module header states rewards are weighted by a time-decaying antiquity multiplier; the file defines `get_time_aged_multiplier()` and `calculate_epoch_rewards_time_aged()`.
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/specs/RIP_POA_SPEC_v1.0.md — reward path describes calculating chain age, evaluating miners, applying the time-aged multiplier, and crediting epoch rewards.
- https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/BOUNTY_2275_FORMAL_VERIFICATION.md — documents reward-weight verification cases, including multiplier proportionality and zero reward for failed fingerprint eligibility.

Use in script: supports the caveat that base multiplier is only one input to final reward allocation.

## Editorial guardrails

- Do **not** say “a VAX earns 3.5x more RTC” without qualification.
- Do **not** imply current market value or guaranteed profitability.
- Do **not** conflate block-producer rotation with reward-weight allocation.
- Pin captures to the reviewed commit above so future source changes do not silently change the package’s factual basis.