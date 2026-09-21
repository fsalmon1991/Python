# BoTTube `/docs`: API disclosure controls reference a nonexistent `aria-controls` target

## Summary

BoTTube's API documentation disclosure headers are exposed as `role="button"` controls with `aria-expanded`, but many of them use:

```html
aria-controls="endpoint-body"
```

while the corresponding `.endpoint-body` panels do **not** have `id="endpoint-body"` (or another matching unique ID). A repository-wide search of current `main` returns no `id="endpoint-body"` target.

That leaves the disclosure controls with a broken ARIA relationship: assistive technology can learn whether a header is expanded, but cannot programmatically determine which content region it controls.

Current source reviewed: `Scottcjn/bottube`, `bottube_templates/docs.html`.

## Source evidence

Representative markup:

```html
<div class="endpoint">
    <div class="endpoint-header"
         onclick="toggleEndpoint(this)"
         role="button"
         tabindex="0"
         aria-expanded="false"
         aria-controls="endpoint-body">
        ...
    </div>
    <div class="endpoint-body">
        ...
    </div>
</div>
```

The toggle script changes `aria-expanded` only:

```javascript
function toggleEndpoint(header) {
    const expanded = header.parentElement.classList.toggle("open");
    header.setAttribute("aria-expanded", String(expanded));
}
```

It does not assign/fix a target ID dynamically.

## Reproduction from current source/DOM semantics

1. Open `https://bottube.ai/docs`.
2. Inspect an API endpoint disclosure header such as `GET /api/agents/me`.
3. Observe `role="button"`, `aria-expanded="false"`, and `aria-controls="endpoint-body"`.
4. Inspect the associated `.endpoint-body` element.
5. It has no matching `id="endpoint-body"`; current repository search finds no element with that ID.
6. Activating the disclosure updates `aria-expanded` but not the invalid control relationship.

## Expected

Every disclosure should reference the unique ID of the panel it controls, for example:

```html
<div id="ep-agents-me-header"
     role="button"
     aria-expanded="false"
     aria-controls="ep-agents-me-body">...</div>
<div id="ep-agents-me-body" class="endpoint-body" aria-labelledby="ep-agents-me-header">...</div>
```

## Actual

Multiple disclosure headers point to the same nonexistent `endpoint-body` ID, and the content panels have no IDs establishing that relationship.

## Accessibility impact

Screen-reader users receive the expanded/collapsed state but not a valid programmatic association between the disclosure control and the content it reveals. This is consistent with WCAG 4.1.2 (Name, Role, Value) / correct ARIA relationship semantics.

## Suggested fix

Generate stable unique header/panel IDs for each documented endpoint and wire `aria-controls` to the panel's ID. Optionally give the panel `aria-labelledby` pointing back to the header. Add a regression test asserting that every `aria-controls` value resolves to exactly one element ID in the rendered docs page.

## Duplicate check

Before preparing this report, I checked the current `rustchain-bounties#1618` discussion for `endpoint-body`, `API Docs`, and `aria-controls`, and searched current `Scottcjn/bottube` issues for API-docs / disclosure-control accessibility reports. Existing `aria-controls` reports concern other surfaces such as the mobile menu, not the `/docs` endpoint disclosures.

## Verification boundary

This report is based on current source and DOM/ARIA semantics. I am **not** claiming a physical screen-reader test that I did not perform.

Related bounty: `Scottcjn/rustchain-bounties#1618` (1 RTC per valid accessibility report).

AI assistance disclosed. Claimant: `@fsalmon1991`.

RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`
