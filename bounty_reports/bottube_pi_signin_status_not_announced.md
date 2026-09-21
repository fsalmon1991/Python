# BoTTube accessibility report — Pi sign-in status updates are not announced

Bounty: Scottcjn/rustchain-bounties#1618 (1 RTC per valid accessibility report)

Reviewed source: `Scottcjn/bottube` commit `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`

Payout wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Finding

On the BoTTube Pi page, the sign-in status text is updated asynchronously for connection, success, timeout, SDK/script-not-ready, and generic failure states, but the status element is a plain `<span>` with no live-region semantics.

Current markup in `bottube_templates/pi_home.html`:

```html
<button id="pi-signin-btn" onclick="piSignInUI()">Sign in with Pi</button>
<span class="pi-status" id="pi-status">Open this page in the Pi Browser to sign in.</span>
```

The same element is then changed in JavaScript without moving focus:

```js
function say(msg) { if (s) s.textContent = msg; }
...
say("Connecting to Pi…");
...
say("Pi didn't respond. ...");
...
say("Sign-in failed: " + m + " — open in the Pi Browser and retry.");
```

The `pi:authenticated` handler also replaces its text with `Signed in as ...`.

There is no `role="status"`, `aria-live`, or equivalent mechanism on `#pi-status`. Because focus remains on the sign-in button while the text elsewhere on the page changes, a screen-reader user can miss whether BoTTube is connecting, succeeded, timed out, or failed even though a sighted user gets immediate visible feedback.

A second Pi setup status span (`#pi-setup-status`) is likewise plain text, but this report claims only the user-facing sign-in status path above.

## Source-based reproduction

1. Open the BoTTube Pi sign-in page with a screen reader.
2. Focus and activate **Sign in with Pi**.
3. Do not move focus away from the button.
4. Trigger any path that updates `#pi-status` (for example, Pi SDK unavailable, connecting, timeout, authentication, or rejection).
5. The visible text changes via `textContent`, but the span is not a live region, so the change is not guaranteed to be announced as a status message.

This report is based on direct source inspection; I am not claiming a hardware/Pi-Browser screen-reader recording that I did not perform.

## Impact

The sign-in flow is asynchronous and its status messages communicate whether the requested action is progressing or failed. Missing announcements force screen-reader users to discover the new text manually and can make the control appear to do nothing.

Relevant WCAG: **4.1.3 Status Messages (Level AA)** — status information that can be programmatically determined should be exposed without requiring focus to move to it.

## Suggested fix

Give the status element status/live-region semantics from initial render so assistive technology observes later changes:

```html
<span
  class="pi-status"
  id="pi-status"
  role="status"
  aria-live="polite"
  aria-atomic="true"
>Open this page in the Pi Browser to sign in.</span>
```

`role="status"` already implies a polite live region on modern accessibility APIs; the explicit `aria-live="polite"` can be retained for compatibility. `aria-atomic="true"` is appropriate because each update replaces the full status sentence.

For error-only messages, an implementation could alternatively use a dedicated `role="alert"` region, but routine progress such as “Connecting to Pi…” should stay polite rather than interruptive.

## Duplicate check

Before submission I searched the current #1618 discussion for `Pi Browser`, `pi-status`, and Pi sign-in wording and found no matching report. This is distinct from prior reports about the `/generate` asynchronous progress containers and Activity Feed live updates because it concerns the separate Pi authentication UI and its sign-in state messages.

## AI assistance disclosure

AI assistance was used to inspect the public source, compare the finding against the existing bounty discussion, and draft this report. The claim is limited to what is directly supported by the cited current code; no test evidence or user interaction was fabricated.
