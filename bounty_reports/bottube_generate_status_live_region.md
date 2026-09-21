# BoTTube `/generate` async status updates are not exposed as live status messages

**Bounty:** Scottcjn/rustchain-bounties#1618  
**Requested payout:** 1 RTC  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Source reviewed:** `Scottcjn/bottube` main, `bottube_templates/generate.html` (GitHub search/fetch snapshot `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`)

## Finding

The AI generation page has asynchronous status containers for video and image generation:

```html
<div class="gen-status" id="video-status"></div>
...
<div class="gen-status" id="image-status"></div>
```

Neither container has `role="status"`, `aria-live`, or another live-region mechanism.

The page updates those containers after user actions and while polling background generation jobs:

```js
function setStatus(id, msg, type) {
    const el = document.getElementById(id);
    el.className = 'gen-status ' + type;
    el.textContent = msg;
}
```

For example, video generation changes the text to messages such as:

- `Submitting video generation request...`
- `Video generating... This takes about 2 minutes. Please wait.`
- `Video generated successfully!`
- network/server error messages

These changes occur without moving focus. A sighted user sees the state change, but a screen-reader user can remain unaware that the job started, failed, or completed.

## Reproduction

1. Open `/generate` with a screen reader.
2. Enter a prompt and activate **Generate Video** or **Generate Image**.
3. Keep focus on the activated control / continue normal navigation.
4. Observe that `#video-status` / `#image-status` changes visually as the request progresses, but the status container has no live/status semantics that would request an automatic announcement.

The defect is verifiable directly from the current template: both containers are plain `<div>` elements and all state transitions are written through `setStatus()`.

## Accessibility impact

This is a status-message problem under WCAG 2.1/2.2 **4.1.3 Status Messages**: important progress, completion, and error state is presented visually without programmatically exposing the change in a way assistive technology can announce without receiving focus.

## Suggested fix

Give each concise status container status/live semantics, for example:

```html
<div class="gen-status" id="video-status" role="status" aria-live="polite" aria-atomic="true"></div>
<div class="gen-status" id="image-status" role="status" aria-live="polite" aria-atomic="true"></div>
```

If errors need stronger interruption than progress updates, use a dedicated `role="alert"` path for error messages rather than making all polling updates assertive.

## Duplicate check

Before submitting, I checked both pages of the full current `#1618` comment history and searched the BoTTube issue tracker for combinations including `generate`, `video-status`, `generation status`, `aria-live`, and accessibility. Existing reports cover other pages/regions (including Studio/Create status regions), but I found no prior report naming the `/generate` page's `#video-status` / `#image-status` containers or this specific generation workflow.

## AI-assistance disclosure

This report was produced with AI-assisted source review and duplicate checking, consistent with the automation-friendly bounty workflow. No production exploitation or state-changing testing was performed.
