# BoTTube #1618 accessibility report — collaboration participant add/remove changes are not announced

**Bounty:** Scottcjn/rustchain-bounties#1618 — 1 RTC per valid accessibility report  
**Claimant:** @fsalmon1991  
**Canonical native RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Target:** `Scottcjn/bottube` → `bottube_templates/collaboration_new.html`

## Summary

The **Create Collaboration** form lets a user add and remove invited creators dynamically, but those changes are communicated only by visually mutating `#participantsList`.

`addParticipant()` appends a name to `selectedParticipants`, calls `updateParticipantsList()`, clears the input, and returns focus to the participant input. `removeParticipant()` similarly updates the array and rerenders the list. The persistent `#participantsList` container has no `role="status"`, `aria-live`, or equivalent announcement mechanism, and the add/remove handlers do not send a concise confirmation to any existing live region.

A screen-reader user can therefore activate **Add** and remain focused in the input without receiving programmatic confirmation that `@name` was added. The same problem occurs after activating a generated **Remove participant @name** button: the visual chip disappears, but there is no announced confirmation that the requested removal succeeded.

This is distinct from the older participant-input-label issue (#1315) and the collaboration-type keyboard issue (#1321): current `main` now has a proper label for the participant input and radio-group keyboard behavior. This report concerns **dynamic feedback after the add/remove action**.

## Source evidence

Current `main` renders:

```html
<div class="participants-list" id="participantsList"></div>
<input type="hidden" name="participants" id="participantsInput" value="">
```

and updates it with:

```js
function addParticipant() {
    const input = document.getElementById('participantInput');
    const name = input.value.trim().replace('@', '');
    if (!name) return;
    if (selectedParticipants.includes(name)) {
        alert('This creator is already invited');
        return;
    }
    selectedParticipants.push(name);
    updateParticipantsList();
    input.value = '';
    input.focus();
}

function removeParticipant(name) {
    selectedParticipants = selectedParticipants.filter(p => p !== name);
    updateParticipantsList();
}

function updateParticipantsList() {
    const list = document.getElementById('participantsList');
    const input = document.getElementById('participantsInput');
    list.innerHTML = selectedParticipants.map(name => `
        <span class="participant-tag">
            @${name}
            <button type="button" onclick="removeParticipant('${name}')"
                    aria-label="Remove participant ${name}" title="Remove participant">&times;</button>
        </span>
    `).join('');
    input.value = JSON.stringify(selectedParticipants.map(name => ({ agent_name: name })));
}
```

The controls themselves have names, but the state change they cause is not exposed as an announcement.

## Reproduction

1. Open `/collaboration/new` while signed in and use a screen reader.
2. Focus **Invite Creators (optional)**, enter an agent name, and activate **Add**.
3. The participant chip appears visually and focus returns to the text input.
4. Observe that there is no live-region/status announcement confirming the participant was added.
5. Navigate to the generated **Remove participant <name>** button and activate it.
6. The chip disappears visually, but there is no programmatic confirmation of the removal.

## Expected behavior

Adding and removing a participant should produce a concise status announcement without moving focus unnecessarily, for example:

- `@alice added to collaboration.`
- `@alice removed from collaboration.`

A robust fix is to add a dedicated visually-hidden `role="status" aria-live="polite" aria-atomic="true"` container and update only that status text from `addParticipant()` / `removeParticipant()`. Making the entire chip list a live region is less desirable because rerendering the complete list can create noisy repeated announcements.

## Impact

The visible interface gives immediate confirmation, but screen-reader users who remain on the input or removal control are not told whether their action changed the collaboration roster. This is an accessibility feedback/state-change defect in a form where invited participants affect the submitted collaboration.

Relevant WCAG intent: 4.1.3 Status Messages and 4.1.2 Name, Role, Value.

## Duplicate check

Before filing, I searched current BoTTube issues for `participantsList`, `selectedParticipants`, `participant added`, `participant removed`, `Add participant`, `Remove participant`, collaboration participant accessibility, and live-region reports. I found no issue matching this add/remove-feedback defect. Existing related reports cover the participant input label (#1315), collaboration type keyboard/role behavior (#1321), and invite modal focus/dialog behavior (#2018), all different failure modes.

I also searched the claimant's prior #1618 fallback submissions and found no prior participant add/remove announcement claim.

## AI assistance disclosure

AI assistance was used for source inspection, duplicate checking, and report drafting. No production state was modified and no evidence was fabricated.
