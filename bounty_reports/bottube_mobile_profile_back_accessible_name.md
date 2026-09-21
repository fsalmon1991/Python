# BoTTube bounty #1618 — mobile profile back control has no functional accessible name

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested reward: **1 RTC**  
Target: `Scottcjn/bottube` mobile app, `mobile-app/src/screens/ProfileScreen.tsx`

## Finding

The native mobile profile screen renders its compact back control as a `TouchableOpacity` whose only child is the glyph `←`:

```tsx
{onBack && (
  <TouchableOpacity style={styles.backButtonContainer} onPress={onBack}>
    <Text style={styles.backButtonText}>←</Text>
  </TouchableOpacity>
)}
```

The control does **not** provide an `accessibilityLabel`, `accessibilityHint`, or an explicit accessible role. Its visual purpose is clear from the arrow icon, but the source does not expose the functional name **“Back”** / **“Go back”** to assistive technology. Depending on platform/screen-reader treatment of the Unicode glyph, the element can be announced as a symbol/left arrow rather than by its navigation purpose.

This is especially inconsistent with the error-state version of the same screen, which renders a text button labelled `Go Back`.

## Impact

A VoiceOver/TalkBack user navigating another agent's profile may encounter a control whose announced name is only the arrow glyph instead of its action. Icon meaning alone should not be required to understand an interactive control.

## Accessibility relevance

- WCAG 2.2 SC 2.4.6 — Headings and Labels
- WCAG 2.2 SC 4.1.2 — Name, Role, Value
- React Native provides `accessibilityLabel` specifically so touch targets can expose a meaningful spoken name.

## Suggested fix

Give the touchable a semantic name and role, for example:

```tsx
<TouchableOpacity
  style={styles.backButtonContainer}
  onPress={onBack}
  accessibilityRole="button"
  accessibilityLabel="Go back"
>
  <Text style={styles.backButtonText} accessible={false}>←</Text>
</TouchableOpacity>
```

An optional `accessibilityHint` such as `Returns to the previous screen` can add context if needed.

## Verification / duplicate check

- Verified against the current public `main` source of `mobile-app/src/screens/ProfileScreen.tsx`.
- Reviewed the current #1618 comment history for `ProfileScreen`, `back button`, and related mobile-profile wording; no matching report was found.
- Searched this account's prior #1618 submission history; no prior mobile-profile back-control report was found.
- This is distinct from earlier reports about web modal focus, generator tabs, live regions, Beacon Atlas controls, and mobile-navigation/menu controls.

## Test-scope disclosure

This is a **source-code accessibility audit**. I did not claim to have run VoiceOver or TalkBack on a built BoTTube mobile binary in this report. The defect is the absence of a functional accessible name in the current React Native source.

AI assistance was used for source review and drafting; no runtime result or screen-reader output was fabricated.
