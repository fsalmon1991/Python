# BoTTube accessibility report: shortcut-help modal lets keyboard focus escape

Bounty context: `Scottcjn/rustchain-bounties#1618` (1 RTC per valid accessibility report)

Claimant: `@fsalmon1991`

Native RTC payout wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

The watch-page **Keyboard shortcuts** help overlay is declared as a modal dialog (`role="dialog" aria-modal="true"`), but its keyboard lifecycle does not contain Tab/Shift+Tab focus inside the dialog.

Current `main` opens the dialog by unhiding it, setting `aria-hidden="false"`, locking body scrolling, and focusing the Close button:

```js
function openShortcutHelp() {
    var modal = document.getElementById('shortcut-help-modal');
    var closeBtn = document.getElementById('shortcut-help-close');
    if (!modal) return;
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
}
```

The template has global keyboard handling for the video-player shortcuts, but there is no Tab/Shift+Tab focus-trap logic and the rest of the page is not made inert while the modal is open. Because the Close button is the dialog's primary/only obvious focus target, pressing Tab can move focus into watch-page controls behind the visually modal overlay even though assistive technology is told that the overlay is modal.

Source inspected: `Scottcjn/bottube` current main (`bottube_templates/watch.html`, commit visible during review: `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`).

## Reproduction

1. Open any BoTTube watch page.
2. Activate the **Keyboard shortcuts** help control (or press `?`).
3. Focus moves to the dialog Close button.
4. Press Tab or Shift+Tab.
5. Focus can leave the open dialog and reach controls behind the modal.

## Expected

While the `aria-modal="true"` dialog is open, keyboard focus should remain within the dialog until it is dismissed. With a single focusable control, Tab/Shift+Tab can simply cycle back to Close. Alternatively, use a standard dialog focus-management helper and make the background inert. Escape/close should keep the existing focus-return behavior.

## Impact

Keyboard and screen-reader users can end up interacting with obscured background controls while a modal is announced as active. This breaks the expected modal interaction contract and creates a confusing focus order (WCAG 2.1.1 Keyboard, 2.4.3 Focus Order, and ARIA dialog guidance).

## Duplicate check

Searched current open/closed BoTTube issues for `shortcut-help`, `Keyboard shortcuts`, modal focus, focus trap, Tab, and `aria-modal`. Existing BoTTube #1305 concerns duplicate keyboard-shortcut handlers; collaboration/Sophia issues concern different dialogs. No report was found for focus escaping the watch-page shortcut-help modal.

## Submission note

Direct upstream issue creation was attempted but the connected GitHub integration returned `403 Resource not accessible by integration`; this public report is therefore retained as reproducible evidence for maintainer filing/review.

AI assistance disclosure: source inspection, duplicate checking, and report drafting used AI assistance. No production state was modified.
