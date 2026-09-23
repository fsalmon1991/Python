# Metadata

## Primary title

**One CPU, Five Miner IDs? RustChain’s Anti-Double-Mining Check**

## Alternate titles

1. **Why Changing Your Miner ID Shouldn’t Multiply Your RustChain Reward**
2. **RustChain Groups Miner IDs by Hardware Identity**

## Hook

**1 CPU + 5 MINER IDs ≠ 5 REWARDS**

## Description

RustChain’s public anti-double-mining path is designed to stop one physical machine from multiplying its epoch reward simply by running several miner IDs. The implementation computes a machine identity from architecture plus stable fingerprint data, detects miner IDs that map to the same identity, and selects a representative for reward treatment.

The repo also documents limits: this is same-node epoch enforcement, not a claim that all Sybil or cross-node replay strategies are impossible.

Author: @fsalmon1991  
Built for RustChain bounty #16601.

## Tags

`RustChain` `RIP-200` `anti double mining` `hardware fingerprint` `blockchain` `consensus` `vintage computing` `Sybil resistance`

## Suggested caption

A miner ID is just an identifier. RustChain’s anti-double-mining code tries to count the underlying machine instead — while its own security docs are explicit about the limits.

## Publication guardrails

- Do not claim the mechanism prevents every Sybil or replay attack.
- Do not demonstrate bypasses against production.
- Keep “same-node / same-epoch” in the description or on-screen caveat.
- Credit @fsalmon1991 if published under #16601.