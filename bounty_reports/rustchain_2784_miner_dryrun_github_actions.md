# RustChain bounty #2784 — miner dry-run hardware report

**Run date:** 2026-09-22  
**Tester:** `@fsalmon1991` via an authorized AI agent  
**Bounty:** https://github.com/Scottcjn/rustchain-bounties/issues/2784  
**RustChain source commit tested:** `217ba85ef9cab3daac0da7b822c79437693444df` (current `main` at test time)  
**Evidence workflow run:** https://github.com/fsalmon1991/Python/actions/runs/35735945563  
**Evidence artifact:** https://github.com/fsalmon1991/Python/actions/runs/35735945563/artifacts/10698220650

## Environment

This was a real execution on a GitHub-hosted Ubuntu runner. It is a Microsoft/Azure virtual machine, **not physical hardware**, and I am reporting it that way rather than presenting it as a personal workstation.

- OS: Ubuntu 24.04.5 LTS
- Kernel: `6.17.0-1022-azure`
- Architecture: `x86_64`
- CPU: AMD EPYC 7763 64-Core Processor
- Exposed CPUs: 4
- Memory reported by miner: 15 GB
- Hypervisor vendor: Microsoft
- Virtualization: full / AMD-V
- `systemd-detect-virt`: `microsoft`
- Python: 3.11.16
- Miner version reported by node: `2.2.1-rip200`

## Command

```bash
python rustchain_linux_miner.py --dry-run --show-payload --verbose
```

The workflow checked out `Scottcjn/Rustchain` directly and installed only the miner runtime dependencies (`requests`, `pynacl`).

## Result

The miner completed successfully with process exit success. The fingerprint suite did **not** fully pass, which is expected/useful on this VM:

```text
[FINGERPRINT] Running 6 hardware fingerprint checks...
Running 6 Hardware Fingerprint Checks...
==================================================

[1/6] Clock-Skew & Oscillator Drift...
  Result: PASS

[2/6] Cache Timing Fingerprint...
  Result: FAIL

[3/6] SIMD Unit Identity...
  Result: PASS

[4/6] Thermal Drift Entropy...
  Result: PASS

[5/6] Instruction Path Jitter...
  Result: PASS

[6/6] Anti-Emulation Checks...
  Result: FAIL

==================================================
OVERALL RESULT: FAILED
Failed checks: ['cache_timing', 'anti_emulation']
[FINGERPRINT] FAILED checks: ['cache_timing', 'anti_emulation']
[FINGERPRINT] WARNING: May receive reduced/zero rewards
```

The dry-run preflight then reported:

```text
[DRY-RUN] RustChain Linux Miner preflight
[DRY-RUN] No mining or network state will be modified
[DRY-RUN] Verbose mode: ON
[DRY-RUN] Node URL: https://rustchain.org
[DRY-RUN] API endpoint: https://rustchain.org/health
[DRY-RUN] TLS verify: True
[DRY-RUN] Hostname: runnervmtr4k5
[DRY-RUN] CPU: AMD EPYC 7763 64-Core Processor
[DRY-RUN] Cores: 4
[DRY-RUN] Memory(GB): 15
[DRY-RUN] MAC count: 2
[DRY-RUN] Serial present: yes
[DRY-RUN] Fingerprint checks available: yes
[DRY-RUN] Fingerprint pass status: False
[DRY-RUN] GET https://rustchain.org/health
[DRY-RUN] Health probe: HTTP 200
[DRY-RUN] Node version: 2.2.1-rip200
[DRY-RUN] Next real steps would be: attest -> enroll -> mine loop
```

The read-only health response at test time was:

```json
{
  "backup_age_hours": 10.476262920233939,
  "db_rw": true,
  "ok": true,
  "tip_age_slots": 0,
  "uptime_s": 228299,
  "version": "2.2.1-rip200"
}
```

## Compatibility observations

1. The miner runs to completion on this Ubuntu 24.04 / x86_64 / Microsoft-Azure VM.
2. VM detection worked as intended: `anti_emulation` failed, and the overall fingerprint status was false.
3. `cache_timing` also failed on this VM, while clock drift, SIMD identity, thermal drift, and instruction jitter passed.
4. The bounty text says dry-run is “safe: no network calls, no mining,” but the current miner performs a **read-only `GET https://rustchain.org/health`** during `dry_run()`. It did not attest, enroll, submit state, or mine, but the wording in the bounty is now slightly stale and could confuse testers who interpret “no network calls” literally.
5. Dry-run correctly used an ephemeral signing key and did not save `miner_key.json`.

## Payout

If accepted, please pay the posted **3 RTC** to the canonical native RTC wallet:

`RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

The automatically generated ephemeral dry-run wallet shown in workflow output is test-only and **must not** be used for payout.

## AI disclosure

This test was orchestrated by an AI agent acting through `@fsalmon1991`'s authorized GitHub connection. The hardware/runtime facts and output above come from the actual GitHub Actions execution linked above; they were not simulated or fabricated.
