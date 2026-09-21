# BoTTube `/embed-guide`: copy-success feedback is not announced to assistive technology

## Summary

On BoTTube's `/embed-guide`, the Copy buttons provide a transient **visual** success state (`Copied!`) after `navigator.clipboard.writeText(...)` resolves, but the success message is not exposed as a status message for assistive technology.

Current source reviewed: `Scottcjn/bottube`, `bottube_templates/embed_guide.html`.

Each Copy control has a persistent accessible name such as `aria-label="Copy basic embed HTML code"`. After a successful copy, JavaScript changes only `btn.textContent` to `Copied!` for 1.5 seconds and then resets it to `Copy`. Because the explicit `aria-label` remains unchanged and there is no `role="status"`, `aria-live`, or other live-region update in this flow, a screen-reader user may receive no programmatic confirmation that the clipboard action succeeded.

## Source evidence

The template gives the buttons static accessible names, for example:

```html
<button class="copy-btn" onclick="copyCode(this)" aria-label="Copy basic embed HTML code">Copy</button>
```

The success path changes only visible text:

```javascript
navigator.clipboard.writeText(text).then(function() {
    btn.textContent = "Copied!";
    btn._copyResetTimer = setTimeout(function() {
        btn.textContent = "Copy";
        btn._copyResetTimer = undefined;
    }, 1500);
});
```

No status live region is updated in this flow.

## Reproduction from current source/DOM semantics

1. Open `https://bottube.ai/embed-guide`.
2. Navigate to any Copy button.
3. Activate it.
4. When the clipboard promise resolves, the visible label changes to `Copied!` for 1.5 seconds.
5. Inspect the accessibility semantics: the static `aria-label` remains the original Copy action, and no live region receives the success result.

## Expected

Successful copy should be exposed as a programmatic status message without moving focus, for example `Copied to clipboard` through a `role="status"` / `aria-live="polite"` region or equivalent accessible state update.

## Actual

Only the visible button text changes temporarily. The explicit accessible name remains the original Copy action and there is no live-region feedback.

## Accessibility impact

A user relying on a screen reader can activate the copy control but may not know whether the clipboard action succeeded. This is a status-message feedback issue consistent with WCAG 2.1/2.2 **4.1.3 Status Messages**.

## Suggested fix

Add a visually hidden shared status element, for example:

```html
<div id="copy-status" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></div>
```

Then update that element on success and failure, e.g. `Copied to clipboard` / `Copy failed`. Temporarily updating the button's `aria-label` could also expose state, but a status live region is more robust because focus does not need to move.

## Duplicate check

Before preparing this report, I checked the current `rustchain-bounties#1618` thread for `Copied!`, `embed-guide`, `copy confirmation`, and related Copy reports, and searched current `Scottcjn/bottube` issues for clipboard/copy/live-region reports. Existing reports cover other Copy-control naming/keyboard issues and a repeated-copy clipboard corruption bug, not this distinct missing success announcement on `/embed-guide`.

## Verification boundary

This report is based on current source and DOM/accessibility semantics. I am **not** claiming a physical screen-reader test or a successful production clipboard write that I did not perform.

Related bounty: `Scottcjn/rustchain-bounties#1618` (1 RTC per valid accessibility report).

AI assistance disclosed. Claimant: `@fsalmon1991`.

RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`
