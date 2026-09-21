# BoTTube #1618 accessibility report — `/generate` tablist cannot be changed from the keyboard

Claimant: `@fsalmon1991`  
Bounty: `Scottcjn/rustchain-bounties#1618`  
Requested payout: **1 RTC**, subject to maintainer validation  
Native RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
AI assistance: **Yes** — source review and write-up were AI-assisted for the claimant.

## Finding

The `/generate` page exposes its Video / Image / My History mode selector as an ARIA tab set, but the inactive tabs are removed from the normal Tab sequence (`tabindex="-1"`) and there is no keyboard handler implementing the required arrow-key navigation between tabs.

As a result, a keyboard-only user can focus the currently selected tab, but cannot reach the other generation modes. Pressing Tab leaves the tablist and moves into the active panel; Arrow Left/Right/Up/Down do not switch tabs because no `keydown` handler exists.

This is distinct from the previously reported Studio mode-selector issues: this finding is specifically the separate `/generate` template and its `gen-tab` / `switchTab()` implementation.

## Current source evidence

Current `bottube_templates/generate.html` declares the control as a tablist:

```html
<div class="gen-tabs" role="tablist" aria-label="Generation type">
    <button class="gen-tab active"
            onclick="switchTab('video')"
            id="tab-video"
            role="tab"
            aria-controls="panel-video"
            aria-selected="true"
            tabindex="0">...</button>

    <button class="gen-tab"
            onclick="switchTab('image')"
            id="tab-image"
            role="tab"
            aria-controls="panel-image"
            aria-selected="false"
            tabindex="-1">...</button>
```

For signed-in users, `tab-history` is likewise initialized with `tabindex="-1"`.

`switchTab()` correctly updates selection state and roving tabindex *after a tab has been activated*:

```js
function switchTab(tab) {
    document.querySelectorAll('.gen-tab').forEach(t => {
        const selected = t.id === 'tab-' + tab;
        t.classList.toggle('active', selected);
        t.setAttribute('aria-selected', String(selected));
        t.tabIndex = selected ? 0 : -1;
    });
    // ...
}
```

However, the template contains no `keydown` listener or equivalent keyboard navigation routine that can move focus to an inactive `tabindex=-1` tab and activate it.

Source reviewed at repository commit `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`.

## Reproduction

1. Open BoTTube's `/generate` page.
2. Use only the keyboard.
3. Tab until the selected **Video** tab receives focus.
4. Press **Arrow Right** (or Arrow Left/Up/Down).
5. Observe that focus/selection does not move to **Image**.
6. Press **Tab**.
7. Observe that focus leaves the tablist and enters the Video panel rather than making Image reachable.
8. When signed in, the same problem prevents reaching **My History** through the tablist.

## Expected behavior

For a `role="tablist"` using roving tabindex, keyboard interaction should let the user move among tabs with arrow keys (and commonly Home/End), update focus, and activate the selected tab according to the chosen activation model.

## Actual behavior

Only the active tab participates in sequential focus navigation. The other tabs are `tabindex="-1"`, and no arrow-key logic is present to focus or select them. They therefore remain mouse/touch accessible but not keyboard-operable through the declared tab widget.

## Accessibility impact

Keyboard-only users cannot switch the generator between Video, Image, and History using the tab control. The problem is particularly severe because changing tabs changes the primary task and form controls shown on the page.

Relevant guidance:

- WCAG 2.1.1 Keyboard — functionality must be operable through a keyboard interface.
- WAI-ARIA Tabs pattern — a focused tab in a tablist should support arrow-key navigation to its sibling tabs when using roving `tabindex`.

## Suggested fix

Add a keydown handler to `.gen-tab` elements. For example:

```js
const tabs = [...document.querySelectorAll('.gen-tab')];

tabs.forEach((tab, index) => {
    tab.addEventListener('keydown', (event) => {
        let next = null;

        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
            next = (index + 1) % tabs.length;
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
            next = (index - 1 + tabs.length) % tabs.length;
        } else if (event.key === 'Home') {
            next = 0;
        } else if (event.key === 'End') {
            next = tabs.length - 1;
        }

        if (next !== null) {
            event.preventDefault();
            tabs[next].focus();
            switchTab(tabs[next].id.replace('tab-', ''));
        }
    });
});
```

If manual activation is preferred, arrow keys can move focus and Enter/Space can call `switchTab()` instead.

## Duplicate check

Before preparing this claim, the current #1618 comment history was checked for the specific `/generate` tab widget, `gen-tab`, `Generation type`, inactive `tabindex=-1` tabs, and missing arrow-key navigation. No matching report was found. Existing reports covering Studio mode selection/tab behavior concern a different page/control and are not this defect.
