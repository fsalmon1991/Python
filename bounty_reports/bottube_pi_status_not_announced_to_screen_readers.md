# BoTTube accessibility report: Pi sign-in/payment status changes are not announced to screen readers

**Target:** `Scottcjn/bottube`  
**Bounty:** `Scottcjn/rustchain-bounties#1618`  
**Severity:** Accessibility / UI  
**Source reviewed:** `bottube_templates/pi_home.html` at current `main`

## Summary

The Pi landing page updates sign-in and payment status text dynamically, but the status elements are plain `<span>` elements without `role="status"`, `aria-live`, or another live-region mechanism. A sighted user sees messages such as “Connecting to Pi…”, “Signed in as …”, timeout text, and other sign-in failures. A screen-reader user who activates the sign-in control can remain unaware that these messages changed because focus stays on the button while the off-focus text is silently replaced.

Two affected elements are:

```html
<span class="pi-status" id="pi-status">Open this page in the Pi Browser to sign in.</span>
```

and

```html
<span class="pi-status" id="pi-setup-status" ...></span>
```

The page's JavaScript repeatedly changes `#pi-status` with `textContent` during authentication:

```js
function say(msg) { if (s) s.textContent = msg; }
...
say("Connecting to Pi…");
...
say("Pi didn't respond. ...");
...
say("Sign-in failed: " + m + " ...");
```

The `pi:authenticated` handler also changes it to `Signed in as ...` and then hides the sign-in button.

The payment frontend uses the separate `#pi-setup-status` element for user-visible payment feedback, so the same live-region problem applies to payment progress/errors on that surface.

## Expected

Authentication and payment progress/errors should be announced to assistive technology without moving focus.

A minimal semantic fix is:

```html
<span class="pi-status" id="pi-status"
      role="status" aria-live="polite" aria-atomic="true">
  Open this page in the Pi Browser to sign in.
</span>

<span class="pi-status" id="pi-setup-status"
      role="status" aria-live="polite" aria-atomic="true"></span>
```

For a terminal payment/sign-in failure, `role="alert"` / `aria-live="assertive"` can be considered if the project wants failures announced immediately, while routine progress should remain `polite`.

## Reproduction reasoning

1. Open `/pi` with a screen reader.
2. Move focus to **Sign in with Pi** and activate it.
3. `piSignInUI()` changes `#pi-status` to progress, timeout, or failure text using `textContent`.
4. Focus remains on the button and the status span has no live-region semantics.
5. The changed message is visible but is not guaranteed to be announced to the screen reader.

The same issue exists for payment feedback written into `#pi-setup-status`.

## Standards impact

This is consistent with a WCAG 2.2 **4.1.3 Status Messages** failure pattern: a status message is programmatically updated but is not exposed through a role/property that allows assistive technology to announce it without focus.

## Duplicate check

Before filing, GitHub issue search was checked for `pi-status`, `Pi screen reader status`, and related accessibility phrasing in `Scottcjn/bottube`; no matching report was found.

## Scope / limitations

This report is source-grounded. I did not claim a live Pi Browser run or fabricate a screen-reader recording. The defect follows directly from the rendered semantics and the documented JavaScript update path.

## Suggested regression check

A lightweight DOM test can assert that both dynamic status containers have either `role="status"` or an `aria-live` attribute. A browser accessibility test can then trigger `piSignInUI()` with a rejected mocked promise and verify that the failure message appears in a live region.

**AI assistance disclosed.**
