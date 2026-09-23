# SOURCES — claim-by-claim map

**Upstream snapshot reviewed:** `Scottcjn/Rustchain` commit `217ba85ef9cab3daac0da7b822c79437693444df`.

## S1 — Definition of the false-green class
**Claim:** FalseGreen targets cases where failure and success return the same shape, so a caller cannot distinguish them.

Source:
- `tools/falsegreen/README.md`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/README.md

## S2 — Historical sweep and documented examples
**Claim:** The README says a 2026-08-18 sweep found 15+ unreported instances and names examples involving a settlement path, payout cap, stargazer pagination, and a health CLI.

Source:
- `tools/falsegreen/README.md`, “The class”
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/README.md

**Editorial limitation:** This package reports the README’s historical statement. It does not claim those exact findings remain unfixed on current main.

## S3 — FG001
**Claim:** FG001 flags exception handlers that return success-shaped values such as `True`, `[]`, `{}`, `0`, or certain `None` returns without surfacing the failure.

Sources:
- README rule table
- `falsegreen.py` module documentation and `visit_ExceptHandler`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S4 — FG002
**Claim:** FG002 targets health/status checks that trust HTTP status without checking the response body or `ok` state.

Sources:
- README rule table
- `falsegreen.py`, `check_py`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S5 — FG003
**Claim:** FG003 targets CI/shell patterns including `continue-on-error: true` and `|| true` when failure can still be consumed as evidence.

Sources:
- README rule table
- `falsegreen.py`, `check_yaml`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S6 — FG005
**Claim:** FG005 flags failed evidence lookups defaulting to empty/zero via patterns such as `api(...) or {}` / `[]` / `0`.

Sources:
- README rule table
- `falsegreen.py`, `visit_Assign`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S7 — Precision-over-recall policy
**Claim:** The tool deliberately excludes expected optional-dependency degradation and favors precision because noisy linting gets ignored.

Sources:
- README paragraph after the rule table
- `falsegreen.py` module documentation and exception-type exclusions
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S8 — Diff-only deployment mode
**Claim:** `--diff origin/main` reports only findings on lines added/changed by a PR, allowing the tool to block new false-green regressions without first clearing the legacy baseline.

Sources:
- README, “Why `--diff` is the point”
- `falsegreen.py`, `added_lines`
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S9 — Implementation / exit contract
**Claim:** The implementation is Python stdlib-based, parses Python AST plus YAML/shell-like patterns, and exits non-zero when qualifying findings are present.

Sources:
- README usage/tests
- `falsegreen.py` module documentation and implementation
  https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen/falsegreen.py

## S10 — Bounty requirements
**Claim:** Bounty #16601 currently lists Type B as a 15 RTC YouTube script + storyboard kit, with first-five acceptance cap, and permits generated assets.

Source:
- https://github.com/Scottcjn/rustchain-bounties/issues/16601

## Disclosure
This package was produced with AI assistance and manually source-checked against the pinned public commit above. Any terminal visual must use real output or be labeled as an illustration. No fabricated production evidence is included.
