# BoTTube #1102 — Pi payment status is routed into the developer-only setup panel

**Target:** `Scottcjn/bottube`  
**Source revision reviewed:** `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`  
**Classification:** UI / functional feedback bug (3 RTC tier)  
**Reporter:** `@fsalmon1991`  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes — source review and report drafting were AI-assisted; the finding and cited code paths were verified against the current repository revision.

## Summary

The normal Pi purchase flow and the developer checklist test-payment flow share a single status sink: `#pi-setup-status`. That element lives inside the developer-only `#pi-setup` panel, even though ordinary tier buttons also call `piBuy(...)`.

As a result, status/error text for a normal customer purchase is written into the developer setup area instead of the normal purchase UI. The current template also has a separate known bug where `#pi-setup` starts visible despite the comment saying it should only appear with `?setup=1`; once that visibility bug is fixed as intended, ordinary payment progress and errors written to `#pi-setup-status` will become hidden entirely.

## Source evidence

### 1. Normal product buttons call `piBuy(...)`

`bottube_templates/pi_home.html` renders each public tier with:

```html
<button class="buy" data-product="{{ t.key }}"
    onclick="piBuy && piBuy(this.getAttribute('data-product'))">
    Generate · pay {{ t.pi }} Pi
</button>
```

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_templates/pi_home.html

### 2. `#pi-setup-status` belongs to the developer setup panel

The same template places the only payment status element inside `#pi-setup`, whose own comment says it is developer setup intended to be visible only with `?setup=1`:

```html
<div id="pi-setup" ...>
    ...
    <span class="pi-status" id="pi-setup-status" ...></span>
</div>
```

### 3. Every `piBuy()` status update targets that developer-only element

`bottube_static/pi_pay.js` defines:

```js
function _payStatus(msg) {
  const el = document.getElementById("pi-setup-status");
  if (el) el.textContent = msg;
  console.log("[pi-pay]", msg);
}
```

The ordinary `piBuy(product)` path then calls `_payStatus(...)` for all user-facing states, including SDK-not-loaded, unknown product, authorization, payment opening, approval, completion, cancellation, and errors.

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_static/pi_pay.js

## Reproduction

1. Open the normal BoTTube Pi purchase page without `?setup=1`.
2. Select any public generation tier and activate its `Generate · pay ... Pi` button.
3. Follow the code path: the button calls `piBuy(product)`.
4. Observe that every progress/error message from `piBuy()` is routed by `_payStatus()` to `#pi-setup-status`, which is inside the developer checklist panel rather than the public purchase section.
5. If the developer panel is hidden as its template comment intends, the normal user receives no visible payment progress/error feedback at all. In the current broken-visible state, the feedback appears in the wrong developer-only area.

No payment or production state needs to be modified to reproduce the DOM/status-routing defect; it is deterministic from the current template and JavaScript.

## Expected

- Normal customer payment progress and errors should render in a status region associated with the public purchase UI.
- The developer checklist test-payment status should remain isolated inside the `?setup=1` developer panel.

## Actual

- Both flows use `#pi-setup-status`.
- Normal purchase feedback is therefore coupled to the developer-only panel.

## Impact

This is primarily a UI/functional feedback defect, not a payment-integrity flaw. A normal user can receive payment states in an unrelated developer panel; after the intended `#pi-setup` visibility behavior is restored, those messages can become invisible. That is especially confusing for SDK-not-loaded, authorization, cancellation, and server error paths where the status text is the main user feedback.

## Suggested fix

Create a dedicated public status region near the tier purchase controls, e.g.:

```html
<div id="pi-payment-status" role="status" aria-live="polite" aria-atomic="true"></div>
```

Then route ordinary `piBuy(product)` messages there and use `#pi-setup-status` only for `test_payment`, for example by passing a target element/id into the status helper or into `piBuy()`.

Separately, initialize `#pi-setup` hidden and only reveal it when `?setup=1`; that is the previously reported visibility defect and is not being double-claimed here.

## Duplicate check

Before filing, the current comment history of RustChain bounty #1102 was checked for `pi-setup-status`, `_payStatus`, and `test payment`; no matching report was found. The broader ongoing bug-bounty thread was also checked for `pi-setup-status`; no matching report was found. This report is intentionally distinct from the previously submitted bug that the developer setup panel itself is visible without `?setup=1`.
