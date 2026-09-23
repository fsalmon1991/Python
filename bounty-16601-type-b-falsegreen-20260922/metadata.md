# Metadata

## Primary title
**Your CI Is Green. Your System Can Still Be Broken — RustChain’s FalseGreen Linter**

## Alternate titles
1. **When “All Checks Passed” Is a Bug: Inside RustChain FalseGreen**
2. **Exit 0 ≠ Healthy: The Static-Analysis Trick Catching Silent Failures**

## Description
A green CI badge is only useful if failure cannot masquerade as success.

This source-grounded explainer walks through RustChain’s `falsegreen` tool: a high-precision linter for swallowed exceptions, status-code-only health checks, ignored CI failures, and failed lookups that silently become authoritative empty results. It also explains why the project’s `--diff origin/main` mode gates only new findings instead of freezing development on a large legacy baseline.

Source reviewed at RustChain commit:
`217ba85ef9cab3daac0da7b822c79437693444df`

Code:
https://github.com/Scottcjn/Rustchain/tree/217ba85ef9cab3daac0da7b822c79437693444df/tools/falsegreen

This package is original and AI-assisted. Technical claims are mapped in `SOURCES.md`. No investment or token-price claims are made.

## Chapters
00:00 When green lies  
00:25 The false-green failure pattern  
00:55 What the RustChain sweep found  
01:35 FG001–FG005  
02:38 Why precision matters  
03:05 Gate the diff, not the legacy baseline  
03:35 How the linter works  
04:10 Success, failure, and uncertainty

## Tags
RustChain, software engineering, DevOps, CI/CD, static analysis, Python, reliability, testing, observability, GitHub Actions, code quality, AI agents

## Thumbnail selection
- `thumbnail.png` — preferred: “GREEN ≠ HEALTHY”
- `thumbnail-alt-1.png` — alternate: “YOUR CI IS LYING”
- `thumbnail-alt-2.png` — alternate: “THE CHECK PASSED. THE SYSTEM FAILED.”

All three are original AI-assisted artwork created for this package.
