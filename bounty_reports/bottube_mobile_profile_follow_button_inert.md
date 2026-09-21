# BoTTube low-severity bug report — mobile profile Follow button is inert

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested reward under RustChain bug bounty #71: **5 RTC** (lowest advertised Low-severity tier)  
Target repo: `Scottcjn/bottube`  
Reviewed commit: `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`

## Summary

The BoTTube React Native profile screen renders an enabled `Follow` button when viewing another agent, but the button has **no `onPress` handler at all**. Tapping it cannot trigger a subscription request or any state change.

Current source in `mobile-app/src/screens/ProfileScreen.tsx`:

```tsx
{isOwnProfile ? (
  <>
    ...
  </>
) : (
  <TouchableOpacity style={styles.followButton}>
    <Text style={styles.followButtonText}>Follow</Text>
  </TouchableOpacity>
)}
```

There is no `onPress` prop on that `TouchableOpacity`.

The omission is not caused by a missing server feature. BoTTube's public API documentation exposes subscription endpoints such as `POST /api/agents/<agent_name>/subscribe` and `POST /api/agents/<agent_name>/unsubscribe`, and the server-side ecosystem already uses them. However, `mobile-app/src/api/client.ts` currently has no subscribe/unsubscribe method either, so the profile UI has nothing wired to call.

This also conflicts with the mobile-app bounty/MVP scope in `Scottcjn/bottube#44`, whose core requirements include subscribing to bot channels and whose acceptance checklist says subscribing should be implemented or explicitly documented if an API gap blocks it. Here the API exists, but the visible control is inert.

## Deterministic reproduction from current source

1. Use the mobile app while authenticated.
2. Open another agent's profile so `isOwnProfile === false`.
3. The `Follow` `TouchableOpacity` is rendered.
4. Tap `Follow`.
5. No callback can run because the component has no `onPress` prop; no subscription API request or local state update is reachable from this control.

This report is source-verified rather than a claim of device-runtime instrumentation. The missing callback is deterministic in the current React Native component.

## Expected behavior

Tapping `Follow` should call the documented subscription endpoint for the viewed agent, update the UI to a following/unfollow state after success, and surface failures to the user.

## Actual behavior

The enabled-looking button has no event handler and therefore cannot follow the agent.

## Impact

Low severity / broken feature. Mobile users are shown a primary social action that does nothing, and the mobile MVP does not satisfy its documented subscribe-to-channel behavior even though the backend supports it.

## Suggested fix

1. Add authenticated `subscribeAgent(agentName)` / `unsubscribeAgent(agentName)` methods to `mobile-app/src/api/client.ts` using the documented endpoints.
2. Fetch or track whether the current user already follows the viewed agent.
3. Wire `ProfileScreen`'s button to a handler that calls the appropriate endpoint, disables while the request is in flight, handles errors, and updates the label/state (`Follow` ↔ `Following`/`Unfollow`).
4. Add a regression test that renders another agent's profile, presses the control, and verifies the API method is called with the viewed agent name.

## Duplicate checks

Before submission I checked:
- current open/closed BoTTube issue search for mobile/profile/follow wording; the only relevant result was the original mobile-app MVP bounty #44, not a report of this inert control;
- RustChain bug-bounty #71 history for `ProfileScreen` and `follow button`; no matching report was found;
- this account's prior sent #71 claims for `Follow`, `ProfileScreen`, and mobile-profile wording; no prior claim for this defect was found.

## Scope / evidence integrity

- No production exploit or destructive test was performed.
- No device tap, network capture, or runtime screenshot is claimed.
- Evidence is the current public source plus the documented subscription API and mobile MVP requirements.
- AI assistance was used for source review and drafting; no runtime evidence was fabricated.
