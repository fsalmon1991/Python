# BoTTube accessibility report: Collaboration invite modal does not contain keyboard focus

**Bounty:** Scottcjn/rustchain-bounties#1618  
**Target:** BoTTube collaboration page (`bottube_templates/collaboration.html`)  
**Finding type:** Keyboard / modal-dialog focus management  
**Method:** Static review of the current public source. I did not claim a screen-reader or browser test that I did not perform.

## Summary

The **Invite to Collaboration** overlay is marked up as a modal dialog (`role="dialog"`, `aria-modal="true"`) and correctly moves focus into the Agent Name field when opened. It also restores focus to the trigger when closed. However, while the modal is open, the implementation does **not trap/contain Tab focus inside the dialog** and does not make the underlying page inert.

As a result, keyboard users can tab past the dialog's final control and reach focusable content behind the modal overlay. That conflicts with the expected keyboard behavior of a modal dialog: while the dialog is active, focus should remain within it until it is closed.

## Source evidence

Current template:

- The modal is explicitly declared modal:

```html
<div class="invite-modal" id="inviteModal" role="dialog" aria-modal="true" aria-labelledby="inviteModalTitle">
```

- Opening the dialog moves focus to the first field:

```js
function openInviteModal(trigger) {
    inviteModalTrigger = trigger || document.activeElement;
    document.getElementById('inviteModal').classList.add('active');
    document.getElementById('agentName').focus();
}
```

- Closing it restores focus to the trigger:

```js
function closeInviteModal() {
    document.getElementById('inviteModal').classList.remove('active');
    document.getElementById('inviteForm').reset();
    if (inviteModalTrigger) {
        inviteModalTrigger.focus();
        inviteModalTrigger = null;
    }
}
```

- The only document-level keyboard handler checks `Escape`; there is no `Tab`/`Shift+Tab` containment logic, and the background content is never given `inert` or otherwise removed from the tab order:

```js
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeInviteModal();
    }
});
```

## Reproduction expectation from the DOM/source

1. Sign in as a collaboration owner or participant with invite permission.
2. Open a collaboration and activate **Invite Collaborator**.
3. Focus starts in **Agent Name**.
4. Press `Tab` through Agent Name, Message, Cancel, and Send Invite.
5. Press `Tab` again.
6. Because there is no focus trap and the page behind the overlay remains focusable, focus can leave the modal and cycle to underlying page/navigation controls even though the overlay still claims `aria-modal="true"`.
7. `Shift+Tab` from the first dialog field has the corresponding escape path in the reverse direction.

## Impact

A sighted keyboard user can lose track of focus because the visually blocking overlay remains open while focus moves behind it. Screen-reader users can also encounter controls that are supposed to be unavailable while a modal dialog is active. This makes the modal's actual keyboard behavior inconsistent with its ARIA modal semantics.

## Accessibility mapping

- **WCAG 2.1.1 — Keyboard:** the dialog workflow must be operable predictably from the keyboard.
- **WCAG 2.4.3 — Focus Order:** focus should follow an order that preserves meaning and operability.
- **ARIA Authoring Practices — Modal Dialog Pattern:** `Tab` and `Shift+Tab` should cycle among focusable elements contained in the dialog while it is open.

## Suggested fix

When opening the modal, make the rest of the page inert (preferred where supported) or implement a focus trap that:

1. collects the currently focusable controls inside `#inviteModal`;
2. intercepts `Tab` on the last control and moves to the first;
3. intercepts `Shift+Tab` on the first control and moves to the last;
4. removes the inert/trap state on close;
5. preserves the existing initial-focus and focus-return behavior.

Example shape:

```js
function trapInviteModalFocus(e) {
    if (e.key !== 'Tab' || !document.getElementById('inviteModal').classList.contains('active')) return;
    const modal = document.getElementById('inviteModal');
    const focusable = [...modal.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
    )];
    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
    }
}
```

Also consider applying `inert` to the non-dialog page container while the modal is active so pointer/accessibility-tree behavior matches the modal semantics, then removing it on close.

## Duplicate check

Before submitting, I searched the current #1618 claim thread for `modal`, `focus trap`, `focus containment`, and `Invite to Collaboration` and found no matching report. I also searched the BoTTube issue tracker for a collaboration-modal focus accessibility report and found no matching issue. This is distinct from existing collaboration accessibility work on form labels and collaboration-type radio/keyboard semantics.

## Disclosure

This report was prepared with AI assistance, then checked against the current public BoTTube source and the existing bounty claim history. No runtime test result, screenshot, or assistive-technology result is fabricated.
