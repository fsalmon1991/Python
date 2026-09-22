# BoTTube `/pi` exposes the developer setup payment control without `?setup=1`

**Target:** `Scottcjn/bottube` current `bottube_templates/pi_home.html`  
**Bounty:** `Scottcjn/rustchain-bounties#71`  
**Requested tier:** Low (5 RTC), subject to maintainer validation  
**Claimant:** `@fsalmon1991`  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

The Pi page says its developer checklist payment control is **"Visible only with `?setup=1` so it isn't shown to normal visitors"**, but the element is rendered with inline `display:block`. The following script only sets the element to `display:block` again when `setup=1`; it never hides it when the query flag is absent.

As a result, the developer-only `Make test payment (0.1 Pi)` control is visible in the normal page render instead of being gated behind the documented query flag.

This is a low-severity UI/logic issue. The same template explicitly configures Pi sandbox/testnet mode, so this report does **not** claim mainnet fund loss.

## Source evidence

Current template:

```html
<!-- Developer setup: complete the Pi Developer Portal checklist's "process a
     user-to-app payment" step. Visible only with ?setup=1 so it isn't shown to
     normal visitors. Pushes a small test payment through /pi/approve + /pi/complete. -->
<div id="pi-setup" style="display:block; text-align:center; ...">
    ...
    <button onclick="piBuy && piBuy('test_payment')">
        Make test payment (0.1 Pi)
    </button>
</div>
<script>
  if (/[?&]setup=1/.test(location.search)) {
    var el = document.getElementById("pi-setup"); if (el) el.style.display = "block";
  }
</script>
```

The initial inline declaration already makes the block visible. The conditional script has no `else` branch and therefore cannot make a no-query render hidden.

## Reproduction

1. Render/open the Pi home page **without** the `setup=1` query parameter.
2. Inspect `#pi-setup`.
3. Its inline style is `display:block`.
4. The script does nothing when `location.search` does not contain `setup=1`.
5. The developer setup text and `Make test payment (0.1 Pi)` button therefore remain visible to a normal visitor.

Expected: `#pi-setup` is hidden by default and is shown only when the explicit developer query flag is present.

Actual: it is visible by default and `?setup=1` changes nothing about its visibility.

## Suggested fix

Hide the developer block by default:

```html
<div id="pi-setup" style="display:none; ...">
```

and keep the existing conditional script that changes it to `display:block` only for `?setup=1`.

Preferably also add a focused template/DOM regression test with two cases:

- no query flag => `#pi-setup` hidden
- `?setup=1` => `#pi-setup` visible

## Scope / safety

This report is based on current source inspection and does not attempt a payment or interact with production payment state. It does not claim that sandbox Pi can be converted into real funds.