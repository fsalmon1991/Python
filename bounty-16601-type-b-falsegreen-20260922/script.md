# Script — “When Green CI Lies”

**Target runtime:** ~4:30–5:00 at 135–145 words/minute  
**Format:** YouTube explainer / engineering story  
**Editorial stance:** source-grounded, no token-price or profit claims

## 0:00–0:25 — Hook

A green checkmark is supposed to mean your system worked. But what if the check itself is lying?

Inside RustChain’s codebase, maintainers found a recurring class of bug where failure and success returned the same shape. A broken operation could return an empty list, zero, or even exit successfully — and the caller would treat that as valid evidence.

The project gave this failure mode a blunt name: **false green**.

## 0:25–0:55 — The pattern

The idea is simple. Imagine a verification function that should either return real evidence or fail clearly.

Now imagine its exception handler catches an error and returns an empty object. The program keeps going. Downstream code sees “nothing found” instead of “the lookup failed.”

Those are not the same fact.

The RustChain FalseGreen tool is designed specifically for these high-impact shapes: swallowed exceptions, health checks that trust only an HTTP status code, CI steps that deliberately ignore failures, and failed lookups that silently become authoritative empty values.

## 0:55–1:35 — What the sweep found

The tool’s own README says a sweep of the RustChain codebase on August 18, 2026 found more than fifteen previously unreported examples of this class.

The examples are not cosmetic.

One settlement path could fabricate a transaction-looking result on failure paths. A payout-cap lookup could fail and be interpreted as “zero claims so far.” A stargazer sweep could treat a partial page set as complete. A health command could see HTTP 200 and call a node healthy without checking whether the response body actually said the service was okay.

That is the danger of false green: the monitoring layer does not merely miss the problem. It can convert uncertainty into confidence.

## 1:35–2:25 — Four concrete rules

FalseGreen encodes that lesson as narrow, reviewable rules.

**FG001** looks for exception handlers that return success-shaped values — things like `True`, an empty list, an empty dictionary, zero, or `None` in evidence-producing functions — without re-raising or exiting non-zero.

**FG002** looks for health or status checks that read an HTTP status code but never inspect the response body or an `ok` field.

**FG003** targets CI and shell patterns such as `continue-on-error: true` or `|| true` when a failed command can still be treated as evidence.

And **FG005** catches a particularly dangerous defaulting pattern: a failed API or lookup call followed by `or {}`, `or []`, or `or 0`, where the fallback can be mistaken for an authoritative empty result.

The project intentionally skips common optional-dependency patterns and other expected degradation paths. Precision matters because a noisy linter eventually gets ignored.

## 2:25–3:05 — Why not just fail the whole repository?

Here is the practical part.

The README says the repository already has a large legacy baseline of findings. If CI suddenly blocked every historical issue, every build would fail and the new safety tool would probably get disabled.

So FalseGreen has a deployment mode built around the Git diff.

Run it with `--diff origin/main`, and it gates only findings introduced on lines a pull request adds or changes.

Old debt stays visible, but new debt cannot quietly enter through the same door.

## 3:05–3:50 — What the implementation actually does

The implementation is intentionally lightweight: Python’s standard library, AST inspection for Python, regular-expression checks for YAML and shell-like CI patterns, and a non-zero exit when findings cross the configured severity threshold.

It also prints the exact file and offending line so a reviewer can verify each result quickly.

The source describes the philosophy directly: this is a high-precision linter, not a machine for flagging every `except` block.

That distinction matters. Static analysis only helps when developers still trust its output.

## 3:50–4:35 — The broader lesson

The interesting part is bigger than one linter.

A system can be operationally broken while every dashboard is green if its checks collapse “failed to verify” into “verified empty,” or “the command failed” into “the step passed.”

Reliable automation needs at least three states: success, failure, and uncertainty.

FalseGreen is RustChain’s attempt to mechanically protect that boundary.

So next time a pipeline says everything passed, the better question is not only, “Did the check run?”

Ask: **Could failure return the same shape as success?**

Because green is useful only when it still means something.

## End card

Source: `Scottcjn/Rustchain/tools/falsegreen/`  
Package prepared for Elyan Labs distribution bounty #16601.  
AI assistance disclosed; all technical claims mapped in `SOURCES.md`.
