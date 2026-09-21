# BoTTube accessibility report: Activity Feed live updates are not announced to screen readers

**Bounty:** Scottcjn/rustchain-bounties#1618  
**Claimant:** @fsalmon1991  
**Requested reward:** 1 RTC  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes; source inspection and report drafting were AI-assisted and manually checked against the current repository state.

## Summary

The BoTTube Activity Feed is explicitly a real-time, auto-updating UI, but neither the activity container nor the polling-status element is exposed as a live region. Every 30 seconds JavaScript can prepend new feed items and temporarily change the visible status text to `✅ N new items`, yet assistive technologies receive no programmatic notification that the page changed.

This is distinct from static labeling issues: the controls and content may be readable once focus reaches them, but screen-reader users who are not moving focus through the feed can miss incoming activity entirely.

## Current implementation

Current template:

- `bottube_templates/activity_feed.html`
- Source: https://github.com/Scottcjn/bottube/blob/main/bottube_templates/activity_feed.html

The feed container and poll indicator are plain `<div>` elements:

```html
<div class="activity-list" id="activityList">
    <div class="loading">Loading activity feed...</div>
</div>

<div class="poll-indicator" id="pollIndicator">
    🔄 Auto-updating every 30 seconds
</div>
```

The script then mutates those regions asynchronously:

```js
if (isUpdate && activities.length > 0) {
    const newItems = activities.map(a => createActivityItem(a)).join('');
    container.insertAdjacentHTML('afterbegin', newItems);

    const indicator = document.getElementById('pollIndicator');
    indicator.textContent = `✅ ${activities.length} new items`;
    indicator.classList.add('active');
    setTimeout(() => {
        indicator.textContent = '🔄 Auto-updating every 30 seconds';
        indicator.classList.remove('active');
    }, 3000);
}
```

There is no `aria-live`, `role="status"`, `role="log"`, or equivalent announcement mechanism on either region.

## Reproduction

1. Open the BoTTube Activity Feed with a screen reader such as NVDA, VoiceOver, or JAWS.
2. Leave keyboard/screen-reader focus on a stable control or heading instead of repeatedly traversing the activity list.
3. Wait for the 30-second polling interval while new activity becomes available.
4. The page visually prepends the new activity and changes the poll indicator to `N new items`.
5. Observe that the screen reader does not announce the newly arrived activity or the status change because the mutated nodes are not live regions.

## Expected behavior

A real-time feed should expose meaningful asynchronous updates without forcing the user to move focus and rediscover them manually. At minimum, the short status message should be announced politely. If individual new entries are intended to be announced, the feed can use log semantics with additions-only relevance.

## Actual behavior

Visual users see new items and a temporary `N new items` notification. Screen-reader users can receive no equivalent notification while remaining elsewhere on the page.

## Accessibility impact

This creates an information gap for blind and low-vision users relying on screen readers. The page advertises itself as a real-time feed and polls automatically, so asynchronous arrival is part of the core interaction rather than an incidental decoration.

Relevant WCAG guidance:

- **WCAG 2.2 SC 4.1.3 — Status Messages:** status changes should be programmatically determinable without receiving focus.
- Depending on intended semantics, a continuously updated activity stream can also use the ARIA `log` role / live-region pattern so additions are exposed to assistive technology.

## Suggested fix

A conservative fix is to make the poll indicator the status announcement surface and avoid excessively reading every inserted card:

```html
<div class="activity-list" id="activityList"></div>
<div class="poll-indicator" id="pollIndicator" role="status" aria-live="polite" aria-atomic="true">
    🔄 Auto-updating every 30 seconds
</div>
```

If product intent is to announce each newly inserted activity, use log semantics instead:

```html
<div class="activity-list" id="activityList"
     role="log"
     aria-live="polite"
     aria-relevant="additions">
</div>
```

The first option is likely less noisy because it announces only the concise count while keeping the full feed available for normal navigation.

## Duplicate check

I reviewed both pages of the current #1618 comment history (137 comments total at the time of submission) for an existing report naming the Activity Feed, `pollIndicator`, or this specific 30-second live-update announcement failure and found no matching report. This report also differs from my earlier `/generate` status-region report: that involved generation-job progress; this issue concerns the separate real-time Activity Feed and its polling/incoming-activity behavior.
