# BoTTube #1618 accessibility report — “Show Seed” state is not exposed to assistive technology

## Bounty

- RustChain bounty: `Scottcjn/rustchain-bounties#1618`
- Advertised reward: **1 RTC per valid accessibility report**
- Claimant: `@fsalmon1991`
- RTC payout wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

On BoTTube’s **Wallet Settings** page, activating **Show Seed** reveals the wallet seed visually inside `#local-wallet-box`, but that newly disclosed content has no focus or announcement contract. The `<pre id="local-wallet-box">` is neither a live region nor a labelled/focusable disclosure target, and `showSeed()` leaves keyboard focus on the triggering button.

As a result, a screen-reader user can activate **Show Seed** and receive no programmatic indication that the sensitive seed has appeared or where the disclosed value is located. The only live status updated by the shared refresh path says that the local wallet is loaded; it does not state that the seed was revealed.

This is distinct from the already-fixed wallet-operation status issue (#2069): the three ordinary status/result containers now have `role="status"` / `aria-live`, while the seed disclosure itself remains a separate generic `<pre>`.

## Current source evidence

`bottube_templates/settings_wallet.html` renders the disclosure target as:

```html
<pre id="local-wallet-box" style="display:none; ..."></pre>
```

The button is:

```html
<button onclick="showSeed()" aria-label="Show wallet seed phrase">Show Seed</button>
```

The reveal path is:

```js
async function showSeed() {
  refreshLocalWalletUI(true);
}
```

and `refreshLocalWalletUI(true)` performs:

```js
box.style.display = "block";
box.textContent = "address: " + w.address +
  "\\npublic_key: " + w.publicKeyHex +
  "\\nseed_hex: " + w.seedHex;
```

No focus is moved to `#local-wallet-box`, the box has no accessible label/region role, and no status message tells assistive technology that the seed is now displayed.

## Reproduction

1. Open `/settings/wallet` with a local wallet loaded.
2. Navigate to **Show Seed** using a screen reader / keyboard.
3. Activate the button.
4. The seed appears visually inside `#local-wallet-box`.
5. Keyboard focus remains on **Show Seed** and there is no dedicated announcement or programmatic disclosure relationship identifying the newly revealed seed content.

## Expected behavior

Do **not** automatically read the secret seed aloud. Instead, expose the disclosure state without leaking the secret. For example:

- give the trigger `aria-expanded` and `aria-controls="local-wallet-box"`;
- expose the revealed box as a labelled region/group, with a safe accessible label such as “Wallet seed details”; and
- update a polite status with a non-secret message such as “Seed phrase displayed below. Navigate to Wallet seed details to review it.”

This makes the state change perceivable while avoiding involuntary speech of sensitive credentials.

## Accessibility impact

A screen-reader user can intentionally request the seed but is not told that the disclosure succeeded or where the newly visible sensitive content lives. Sighted users receive an immediate visual state change that assistive-technology users do not.

Relevant WCAG considerations: **4.1.2 Name, Role, Value** and **4.1.3 Status Messages**.

## Duplicate check

Searched the current BoTTube issue tracker for `Show Seed`, `local-wallet-box`, `seed phrase`, wallet screen-reader reports, and wallet live-region reports. No issue covering this seed-disclosure state was found. Existing #2069 covered ordinary wallet operation result/status containers and is already reflected in current source; this report concerns the separate seed disclosure target.

## AI assistance disclosure

Source review, duplicate checking, and report drafting were AI-assisted. No production state-changing action or wallet secret was accessed.
