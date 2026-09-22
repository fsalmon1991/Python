# BoTTube #1102 — Real Pi Browser is forced into SDK sandbox mode

**Target:** `Scottcjn/bottube`  
**Source revision reviewed:** `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`  
**Classification:** Functional bug (5 RTC tier)  
**Reporter:** `@fsalmon1991`  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes — source review and report drafting were AI-assisted; the finding and cited code paths were verified against the current repository revision.

## Summary

BoTTube's own Pi authentication code says the Pi SDK must use `sandbox:false` inside the real mobile Pi Browser because `sandbox:true` is only for the desktop Pi Sandbox and prevents the native auth bridge from being reached. However, the shared `base.html` template unconditionally sets `window.PI_SANDBOX = true`, and the Pi storefront template sets it to `true` again.

That value is consumed by both `pi_auth.js` and `pi_pay.js`, forcing `_SANDBOX` / `_PAY_SANDBOX` to `true` even when the page is running in the real Pi Browser. Based on the repository's own comments, this breaks real Pi Browser authentication/payment initialization.

## Source evidence

### 1. `pi_auth.js` explicitly documents the required behavior

`bottube_static/pi_auth.js` states:

```js
// NOTE on sandbox: `sandbox: true` is ONLY for the desktop Pi Sandbox
// (sandbox.minepi.com). Inside the real Pi Browser app it MUST be false, or the
// native auth bridge is never reached and authenticate() silently fails.
```

It then computes:

```js
var _SANDBOX = /[?&]pi_sandbox=1/.test(location.search) || window.PI_SANDBOX === true;
function piInit() {
  if (!_init) {
    _init = Promise.resolve(Pi.init({ version: "2.0", sandbox: _SANDBOX }));
  }
  return _init;
}
```

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_static/pi_auth.js

### 2. The shared template does the exact opposite

`bottube_templates/base.html` contains a comment that says the same thing — and even records that `sandbox:true` broke payment auth — but immediately sets the global to `true`:

```html
<!-- Pi.init sandbox=false in the REAL mobile Pi Browser. sandbox:true is ONLY for the
     desktop sandbox (sandbox.minepi.com); testnet vs mainnet is the app's network +
     wallet, not this flag. sandbox:true here broke payments auth ("open in sandbox"). -->
<script>window.PI_SANDBOX = true;</script>
```

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_templates/base.html

### 3. The Pi storefront reinforces the bad value

`bottube_templates/pi_home.html` also contains:

```html
<script>window.PI_SANDBOX = true;</script>
```

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_templates/pi_home.html

### 4. The payment code consumes the same global

`bottube_static/pi_pay.js` documents that real Pi Browser must use `sandbox:false`, then computes:

```js
const _PAY_SANDBOX = /[?&]pi_sandbox=1/.test(location.search) || window.PI_SANDBOX === true;
```

and later initializes:

```js
Pi.init({ version: "2.0", sandbox: _PAY_SANDBOX });
```

Source: https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/bottube_static/pi_pay.js

## Deterministic reproduction from current source

1. Load a BoTTube page using `base.html` inside the real Pi Browser, without `?pi_sandbox=1`.
2. `base.html` executes `window.PI_SANDBOX = true` before the deferred Pi auth script runs.
3. `pi_auth.js` evaluates `_SANDBOX` as:
   - query flag: `false`
   - `window.PI_SANDBOX === true`: `true`
   - result: `true`
4. `piInit()` therefore calls `Pi.init({ version: "2.0", sandbox: true })` in the real Pi Browser.
5. The repository's own `pi_auth.js` comment says this prevents the native auth bridge from being reached and causes authentication to fail.
6. On `/pi`, `pi_home.html` sets the same global to `true` again, and `pi_pay.js` likewise resolves `_PAY_SANDBOX` to `true`.

No production transaction or invasive test is needed to establish the configuration defect; the boolean flow is deterministic from the current source.

## Expected

- Real Pi Browser: `sandbox:false` unless the explicit desktop-sandbox opt-in `?pi_sandbox=1` is present.
- Desktop Pi Sandbox: `sandbox:true` when explicitly requested.
- Testnet vs mainnet should be controlled by the Pi app/network configuration and server `PI_SANDBOX`, not by forcing the client SDK sandbox flag globally.

## Actual

The shared template globally forces `window.PI_SANDBOX = true`, so both authentication and payment initialization choose SDK sandbox mode everywhere.

## Impact

This is a functional onboarding/payment bug for real Pi Browser users. The repository itself states that the wrong SDK sandbox mode prevents the native bridge from being reached. Affected users can fail authentication or payment initialization even though they are using the intended Pi Browser environment.

## Suggested fix

Remove the unconditional global assignment from `base.html` and `pi_home.html`, or default it to `false`:

```html
<script>window.PI_SANDBOX = false;</script>
```

Prefer letting the existing explicit opt-in in the JavaScript decide desktop sandbox mode:

```js
var _SANDBOX = /[?&]pi_sandbox=1/.test(location.search);
```

If a server-rendered flag is needed, pass a distinct configuration value that reflects the actual client SDK environment rather than server testnet/mainnet mode.

Add a regression test/assertion for both contexts:
- real Pi Browser, no query flag -> `sandbox:false`
- desktop sandbox with `?pi_sandbox=1` -> `sandbox:true`

## Duplicate check

Before filing, the current #1102 history was checked for `PI_SANDBOX`; no matching report was found. The broader #71 bug-bounty history was also checked for `PI_SANDBOX`; no matching report was found. A repository-wide issue search for `PI_SANDBOX`, `sandbox:true`, `open in sandbox`, and `Pi Browser` found no existing issue in `Scottcjn/bottube`.

This is distinct from the previously reported developer-panel visibility bug and from the separate payment-status-target bug: this finding concerns the Pi SDK environment flag used by authentication and payments in the real Pi Browser.
