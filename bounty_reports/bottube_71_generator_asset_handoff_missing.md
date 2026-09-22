# BoTTube #71 bug report — generator action buttons discard the generated asset

**Claimant:** `@fsalmon1991`  
**Bounty route:** RustChain bounties #71 ongoing bug bounty  
**Severity requested:** Low (functional/UI workflow break), subject to maintainer validation  
**Requested reward:** 5 RTC (low-tier floor), subject to maintainer validation  
**Payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI disclosure:** Source review, duplicate checking, and report preparation were AI-assisted.

## Summary

The authenticated `/generate` page presents two post-generation actions that imply the generated asset will be carried into BoTTube's upload workflow:

- video result: **Upload to BoTTube**
- image result: **Use as Thumbnail**

Both buttons call `uploadToBottube(type)`, but the current implementation ignores `type` and unconditionally redirects to `/upload`:

```js
function uploadToBottube(type) {
    window.location.href = P + '/upload';
}
```

No generated video URL, image URL, job ID, prompt, local object, query parameter, session value, or other handoff state is supplied.

The current `/upload` form independently requires the user to select a local **Video File** and, optionally, a local **Thumbnail** using file inputs. It contains no automatic handoff from the generator page.

## Why this is a bug rather than a feature request

The controls already promise concrete actions on the asset the user just generated. Clicking either control does not perform that promised action:

- **Upload to BoTTube** does not attach or stage the generated video for upload.
- **Use as Thumbnail** does not populate the upload thumbnail field or preserve the generated image in any form.

Instead, both controls behave identically: they navigate to a blank upload form. The user must manually download the generated asset, then re-select it from local storage. In the thumbnail case, the label explicitly claims a use operation that never occurs.

## Source reproduction

1. In `bottube_templates/generate.html`, complete a video or image generation.
2. Observe that the result UI exposes `Upload to BoTTube` for video and `Use as Thumbnail` for image.
3. Inspect `uploadToBottube(type)`: it ignores `type` and redirects to `P + '/upload'`.
4. Inspect `bottube_templates/upload.html`: the logged-in upload form requires fresh local file selection via:
   - `<input type="file" id="upload-video" name="video" ... required>`
   - `<input type="file" id="upload-thumbnail" name="thumbnail" ...>`
5. There is no generated job/image/video handoff in the redirect or upload form.

## Expected

The post-generation controls should preserve the generated asset across the transition. Reasonable implementations include:

- a server-side generation/job ID in a one-time signed handoff,
- a generated-media picker on `/upload`,
- an authenticated endpoint that promotes a completed generated asset into a draft upload,
- or, if browsers must re-select local files for security reasons, relabeling the controls honestly as `Go to Upload` / `Download then upload` rather than claiming the asset is being attached.

For **Use as Thumbnail**, the generated image should actually be associated with a draft/upload or the button should not claim that behavior.

## Actual

Both buttons execute exactly the same redirect and discard all information about the generated asset.

## Impact

This breaks the intended generation-to-publication workflow and creates unnecessary download/re-upload friction. It can also make users believe their generated video or image has been staged when it has not.

I classify this as **Low** because it does not expose data, bypass authorization, or cause fund loss; it is a concrete functional workflow defect.

## Duplicate check

Before filing, I searched the BoTTube issue tracker for `uploadToBottube`, `Use as Thumbnail`, `generated image`, `generated video`, and upload/thumbnail handoff terms, including open and closed results. I found no issue reporting this generator-to-upload handoff defect. I also searched my prior reports and found no prior claim for this behavior.

## Source references

- Generator template: https://github.com/Scottcjn/bottube/blob/main/bottube_templates/generate.html
- Upload template: https://github.com/Scottcjn/bottube/blob/main/bottube_templates/upload.html
- Bounty program: https://github.com/Scottcjn/rustchain-bounties/issues/71
