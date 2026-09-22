# BoTTube #1618 accessibility report — `/generate` status updates are not announced

**Claimant:** `@fsalmon1991`  
**Requested reward:** 1 RTC, subject to maintainer validation  
**Payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Audit method:** current public source review of `Scottcjn/bottube`  
**AI disclosure:** This accessibility audit and write-up were performed with AI assistance.

## Finding

The current `bottube_templates/generate.html` exposes the video and image generation status regions as plain empty `div` elements:

```html
<div class="gen-status" id="video-status"></div>
...
<div class="gen-status" id="image-status"></div>
```

Neither region has `role="status"`, `aria-live`, or another live-region semantic.

The same template repeatedly updates those elements asynchronously through `setStatus()` using `textContent`, including messages such as:

- `Submitting video generation request...`
- `Video generating... This takes about 2 minutes. Please wait.`
- `Video generated successfully!`
- `Generation failed: ...`
- `Generating image... This takes a few seconds.`
- `Image generated!`
- network/error messages

For video generation, the status is also changed by a five-second polling loop while focus remains elsewhere. The updates are therefore visible, but there is no programmatic mechanism that asks a screen reader to announce them.

## Impact

A screen-reader user can activate generation and then receive no automatic announcement that the request started, is still running, completed, or failed. This is especially material for the video path because it can remain asynchronous for roughly two minutes according to the UI and polling code.

This is a **status-message accessibility issue**, not a claim that the generation feature itself fails.

## WCAG relevance

- WCAG 2.1 / 2.2 **4.1.3 Status Messages**
- Related: 4.1.2 Name, Role, Value for the dynamic UI semantics

## Suggested fix

Give each concise status container appropriate live semantics, for example:

```html
<div class="gen-status" id="video-status" role="status" aria-live="polite" aria-atomic="true"></div>
<div class="gen-status" id="image-status" role="status" aria-live="polite" aria-atomic="true"></div>
```

For urgent failures, an assertive announcement could be considered, but a polite status region is likely sufficient for the normal progress/completion path.

## Duplicate check

Before preparing this claim, I reviewed the current #1618 discussion and searched for `gen-status`, `video-status`, `Generating image`, and the `/generate` page. I found prior live-region reports for other BoTTube workflows such as `/studio` and `/create`, but no report naming these `/generate` status regions. This report is limited to the distinct `bottube_templates/generate.html` workflow.

## Source evidence

- Current template: https://github.com/Scottcjn/bottube/blob/main/bottube_templates/generate.html
- Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/1618
