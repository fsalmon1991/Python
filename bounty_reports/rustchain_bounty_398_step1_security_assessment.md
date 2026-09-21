# RustChain #398 — Step 1 Security Assessment

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested Step 1 reward: **10 RTC**  
Scope: code-reading assessment only; I did not attack or fuzz production.  
AI disclosure: AI-assisted code review/drafting, with claims grounded in the current RustChain repository.

## 1. How `/attest/submit` works

The active Proof-of-Antiquity specification describes a two-sided attestation protocol rather than trusting a miner's self-description. The client gathers applicable physical-hardware measurements and sends the payload to `POST /attest/submit`. The server then re-evaluates the raw fingerprint evidence with `validate_fingerprint_data()` and derives a canonical architecture with `derive_verified_device()`. On success it writes the verified state to `miner_attest_recent`, marks `fingerprint_passed = 1`, and enrolls the miner for the current epoch. The specification currently sets attestation validity to 24 hours. Code/spec reference: `specs/RIP_POA_SPEC_v1.0.md`, section 2.1, especially the seven-step Attestation Flow.

The important trust boundary is that client booleans are not intended to be authoritative. The same spec states that the server does not simply trust each check's reported `passed` field; it validates raw measurements. This matters because otherwise an attacker could submit `{"passed": true}` for every check without proving anything physical.

The current node has also accumulated defensive fixes around this path. `docs/FIX_1147_ATTEST_SUBMIT_CRASH.md` records a prior malformed-payload DoS class and the remediation: the route was wrapped so unexpected exceptions become a controlled error, while fingerprint parsing added defensive type checks for architecture, bridge type, and SIMD feature lists. That is a good example of why parsing and validation are part of the security boundary, not just correctness plumbing.

Current enrollment logic is also explicitly hardened against reward-tier spoofing. In `node/rustchain_v2_integrated_v2.2.1_rip200.py`, `resolve_enroll_weight_device()` prefers `miner_attest_recent.device_family/device_arch`, which were derived from the verified attestation, rather than trusting the unsigned `device` object in the enrollment request. The source comment explains the historical risk directly: an ordinary x86 miner could otherwise claim a higher-weight architecture at enrollment time.

## 2. How hardware fingerprinting resists VM farms

RustChain's 1-CPU-1-vote design only works if “CPU” means a distinct physical machine, not an arbitrary number of VM identities. `specs/RIP_POA_SPEC_v1.0.md` therefore combines several classes of evidence: clock/oscillator behavior, cache hierarchy, SIMD identity, thermal behavior, instruction jitter, provenance/age evidence, anti-emulation, and optional ROM/device fingerprints. The server cross-validates these measurements instead of relying on a CPU-model string.

The current implementation goes beyond a static all-checks-pass model. In `node/rustchain_v2_integrated_v2.2.1_rip200.py`, `get_epoch_fingerprint_rotation()` derives an epoch-specific measurement nonce and active-check set from prior chain state. `evaluate_rotating_fingerprint_checks()` scores only the checks active for that epoch, distinguishes failed from structurally unmeasurable checks, and fails an empty measured denominator closed unless a capability-limited device has already been accepted on native evidence. This is useful against a miner that tries to win by simply omitting inconvenient measurements.

The architecture-specific validation also tries to stop cross-family masquerading. The current source has server-side helpers for PowerPC, ARM, cache profiles, SIMD evidence, and degenerate measurements. The broader principle is sound: a miner should have to make several physical observations agree with each other. A VM can copy a model string cheaply; reproducing consistent timing, cache, SIMD, thermal, and anti-emulation evidence across many fake identities is a materially harder Sybil problem.

## 3. Epoch rewards and distribution

Reward settlement is implemented in `node/rewards_implementation_rip200.py::settle_epoch_rip200()`. The module describes RIP-200 as deterministic round-robin / time-aging with one physical machine intended to receive one reward per epoch. The base epoch budget is `PER_EPOCH_URTC = 1.5 * 1_000_000`, and the code enforces a total-supply ceiling by clamping the epoch budget to remaining supply headroom.

The settlement path takes `BEGIN IMMEDIATE` before checking whether the epoch is already settled. That ordering is security-relevant: the settled check happens under the SQLite write lock, preventing two concurrent settlement workers from both seeing “unsettled” and crediting the same epoch. In production the anti-double-mining path is also configured fail-closed by default: if anti-double-mining is required but unavailable, settlement returns an error instead of silently falling back to the non-grouping path. The anti-double-mining implementation groups reward eligibility around hardware identity rather than wallet count.

Once rewards are calculated, the design writes epoch reward records and balance/ledger state. The current code also includes explicit ledger reconciliation work and optional UTXO dual-write support, which is important because account balance, audit ledger, and UTXO representations must not diverge into multiple spendable versions of the same reward.

## 4. Potential attack vector / architectural risk: fail-open producer enrollment

The highest-value risk I would keep on the security roadmap is the **producer-enrollment fail-open boundary already documented in draft RIP-202**. `rips/docs/RIP-0202-fail-closed-producer-enrollment.md` states that the current producer-selection gate treats a missing `epoch_enroll` row differently from an explicit zero/negative weight: an absent miner can fall back to a heuristic weight. In that model, a VM/Sybil that is rejected by enrollment has an incentive to avoid enrollment entirely rather than submit a row that excludes it.

This is not a claim that I discovered a new exploitable vulnerability, and I would not represent it as such. The repository itself documents the condition and, importantly, explains why the fix cannot be a one-line “missing means zero” change: producer selection is deterministic consensus, while `miner_attest_recent` / `epoch_enroll` are presently node-local rather than fully chain-replicated state. A naïve fail-closed change on partially synchronized nodes could make honest nodes choose different producers and fork.

The correct mitigation is therefore the staged plan in RIP-202: make the relevant enrollment snapshot deterministic and chain-derived, seal it before producer selection, enforce non-empty finalized snapshots, activate the rule fleet-wide from deterministic on-chain state, then treat absence from a finalized snapshot as exclusion. Until those prerequisites are complete, I would treat the gap as a **known defense-in-depth weakness** and monitor it rather than pretending the enrollment gate is a hard anti-Sybil boundary.

## Assessment

The strongest part of RustChain's security model is that reward identity is pushed toward server-verified physical evidence and not left as an arbitrary wallet/account count. The codebase also shows a useful pattern of turning past findings into regression checks: malformed attestation inputs, architecture-reward spoofing, replay resistance, settlement races, and double-mining have dedicated hardening paths. The largest architectural caution is consistency between node-local attestation/enrollment data and consensus decisions. Physical-fingerprint quality can be excellent and still fail to secure producer selection if different nodes do not derive the same eligible set from the same finalized chain state.

### Sources / code references reviewed

- `specs/RIP_POA_SPEC_v1.0.md` — active PoA protocol, §2.1 attestation flow and fingerprint checks
- `node/rustchain_v2_integrated_v2.2.1_rip200.py` — `get_epoch_fingerprint_rotation`, `evaluate_rotating_fingerprint_checks`, `resolve_enroll_fingerprint`, `resolve_enroll_weight_device`, architecture-evidence helpers
- `node/rewards_implementation_rip200.py` — `settle_epoch_rip200`, `BEGIN IMMEDIATE`, supply clamp, anti-double-mining fail-closed path, UTXO dual-write
- `docs/FIX_1147_ATTEST_SUBMIT_CRASH.md` — malformed-attestation crash root cause and validation hardening
- `rips/docs/RIP-0202-fail-closed-producer-enrollment.md` — current producer-enrollment gap, consensus constraints, and staged remediation

No production exploit was attempted, no security evidence was fabricated, and the potential vector above is explicitly characterized as an already-documented architectural risk rather than a novel bounty finding.
