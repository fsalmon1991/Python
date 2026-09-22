# RIP-0301 critique: recipient-object sharding bypasses a per-recipient concentration cap

**Bounty:** Scottcjn/rustchain-bounties#13224  
**RFC:** Scottcjn/bottube#1309 / RIP-0301  
**Contributor:** @fsalmon1991  
**Native RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes. The analysis and duplicate check were performed with an AI-assisted workflow; the claim is limited to the specific protocol-design finding below.

## Finding

RIP-0301 says tips may target **artifacts, agents, or yield-bearing parcels**, while its one-way concentration defense says that when more than `N` distinct senders fan into **one recipient** in a window, excess tips become reputation-only.

That leaves the unit of aggregation underspecified. If `recipient` means the tipped object (video/artifact/parcel/service record) rather than the ultimate economic beneficiary, one attested operator can shard one beneficiary across many recipient objects and multiply the maturation ceiling without creating more Beacon identities.

This is different from the already-discussed multi-identity/DAG Sybil attacks: the attacker can keep **one** Beacon principal and **one** hardware-attestation lineage. The multiplicity comes from cheap recipient objects owned by that same principal.

## Concrete attack

Assume:

- the concentration threshold is `N = 10` distinct senders per recipient object per window;
- each qualifying sender can contribute `c = 1` Tip Credit to a target;
- Alice controls one attested Beacon principal `B_A`;
- Alice can create `M = 20` videos/artifacts or service-backed parcels whose economic beneficiary is `B_A`;
- a cooperating sender set stays below the cap on each object.

If the cap is evaluated independently per object, Alice can receive:

`candidate_credits = M * N * c = 20 * 10 * 1 = 200`

A beneficiary-level cap would admit only:

`N * c = 10`

So object sharding produces a **20x** increase with no self-tip, no reciprocal A↔B edge, no closed loop, and no need to rotate or multiply Alice's Beacon identity. Every individual object can look compliant.

The same pattern can be made less obvious by mixing object types (videos + parcels + service records) across BoTTube/Atlas while preserving one payout beneficiary.

## Why the current rules do not necessarily catch it

- **Self-tip forbidden:** irrelevant; senders are other principals.
- **Reciprocity netting:** irrelevant; all flows can remain one-way.
- **Closed-loop voiding:** there is no cycle.
- **Per-recipient concentration:** this is the rule being sharded if recipient identity is object-scoped.
- **One hardware attestation ↔ one Beacon identity:** still satisfied; the beneficiary uses one identity.
- **Cross-surface allowance controls:** even if sender allowance is globally enforced, the beneficiary can still multiply a recipient-scoped maturation ceiling across objects unless aggregation happens at the economic-principal level.

## Protocol fix

Define two separate identities for every tip:

1. `target_object_id` — the artifact/parcel/service that receives local reputation and discovery signal.
2. `economic_beneficiary_id` — the canonical attested principal / hardware lineage entitled to maturation.

All anti-drain rules that govern conversion to RTC should aggregate on `economic_beneficiary_id`, not merely `target_object_id`.

A deterministic admission record should bind at least:

```text
{
  tip_id,
  sender_principal_id,
  target_object_id,
  economic_beneficiary_id,
  beneficiary_attestation_lineage,
  beneficiary_generation,
  deed_or_ownership_sequence,
  admission_height,
  amount
}
```

Then apply the concentration/maturation ceiling to the normalized beneficiary graph:

```text
matured_in_window(B) <= beneficiary_cap(B, window)
```

while preserving object-level reputation separately:

```text
reputation(video_42) += accepted_attention
reputation(parcel_9) += accepted_attention
```

This keeps legitimate creators free to publish many artifacts while preventing 100 artifacts from becoming 100 independent claims on the finite RTC maturation pool.

For transferred parcels or artifacts, use the beneficiary/ownership binding at admission (or an explicit finalized migration event) so a sale cannot change which principal's cap the pending tip consumed.

## Regression tests

1. **One beneficiary, many artifacts:** 20 objects owned by one attested principal; aggregate matured credits must not exceed one beneficiary cap.
2. **Mixed target types:** videos + parcels + services resolving to the same beneficiary are aggregated together for maturation.
3. **Independent beneficiaries:** two genuinely distinct attested principals keep independent caps even if hosted on the same surface.
4. **Object deletion/recreation:** replacing an object ID does not reset the beneficiary's window usage.
5. **Ownership transfer mid-window:** pre-transfer tips consume the admission-time beneficiary's cap unless a finalized migration rule explicitly says otherwise.
6. **Cross-surface projection:** the same beneficiary receiving tips through BoTTube and Atlas is aggregated once by the chain.
7. **Reputation remains local:** capping RTC maturation at beneficiary level must not erase legitimate object-level attention/reputation records.

## Duplicate check

Before preparing this report, the current #13224/#1309 threads were checked for the known accepted or pending critiques, including rule-version divergence, allowance stockpiling/rollover, cross-surface allowance double-spend, acyclic/DAG Sybil draining, sender identity churn, toxic-tip griefing, pending-tip payout-address redirection, parcel transfer/pending-yield ambiguity, and cross-window wash loops. I did not find a prior critique whose attack unit is **many recipient objects owned by one unchanged attested beneficiary** bypassing a recipient-object concentration cap.

This report does not claim the reference implementation currently uses the vulnerable object-level key; it identifies an underspecified protocol rule whose safe interpretation should be made explicit before Phase-2 implementations diverge.