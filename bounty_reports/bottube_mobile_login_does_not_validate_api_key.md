# BoTTube low-severity bug report — mobile login accepts an unvalidated API key locally

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested reward under RustChain bug bounty #71: **5 RTC** (lowest advertised Low-severity tier)  
Target: `Scottcjn/bottube` mobile app  
Reviewed commit: `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`

## Summary

The React Native mobile login flow accepts any non-empty API-key string for an existing agent because `BoTTubeApi.login(agentName, apiKey)` never sends that key to an authenticated endpoint before saving it.

`mobile-app/src/api/client.ts` currently implements login as:

```ts
async login(agentName: string, apiKey: string): Promise<Agent> {
  // Validate credentials by fetching profile
  const agent = await this.request<Agent>(`/api/agents/${agentName}`, {
    method: 'GET',
  }, false);

  if (agent) {
    await this.saveSession(apiKey, agentName);
  }

  return agent;
}
```

The third argument `false` explicitly disables authentication for the request. The request only proves that the public profile exists; it does not prove that `apiKey` belongs to that agent.

`mobile-app/src/hooks/useAuth.ts` then treats the returned public profile as successful authentication immediately:

```ts
const profile = await api.login(agentName.trim().toLowerCase(), apiKey.trim());
setAgent(profile);
setIsAuthenticated(true);
```

So the app enters authenticated local state and persists the supplied API key even if the key is wrong. On a later cold start, `initAuth()` does call authenticated `GET /api/agents/me` and clears an invalid session, so this is **not a server-side authentication bypass**. It is a broken credential-validation/login flow during the current session.

## Deterministic reproduction from current source

1. Choose the name of any existing public BoTTube agent.
2. On the mobile login screen, enter that agent name and any non-empty fake API key such as `definitely-not-a-real-key`.
3. `LoginScreen.handleLogin()` calls `useAuth.login()`.
4. `api.login()` fetches only the public `/api/agents/<agentName>` endpoint with `includeAuth=false`.
5. If the public profile exists, it saves the fake key and `useAuth.login()` sets `isAuthenticated=true`.
6. Protected actions later fail when the backend actually checks the bogus key; after app restart, `getMe()` detects the invalid session and clears it.

The defect follows directly from the current call graph; this report does not claim packet-capture or device-runtime evidence.

## Expected behavior

The Login action should succeed only after the supplied API key is verified against an authenticated endpoint for that same account (for example, `GET /api/agents/me` with `X-API-Key`) and the returned identity should match the requested agent.

## Actual behavior

Any non-empty key is saved and treated as authenticated as long as the typed agent name resolves to a public profile.

## Impact

Low-severity authentication/UX logic error:
- users get a false successful-login state with invalid credentials;
- invalid credentials are persisted to SecureStore;
- protected screens/actions may be enabled until backend calls start failing;
- the app only self-corrects on a later initialization path.

This does **not** grant unauthorized server data or permissions, so I am deliberately not classifying it as an auth bypass.

## Suggested fix

Validate before saving:

```ts
async login(agentName: string, apiKey: string): Promise<Agent> {
  this.apiKey = apiKey;
  try {
    const me = await this.request<Agent>('/api/agents/me');
    if (me.agent_name !== agentName) {
      throw new Error('API key does not belong to this agent');
    }
    await this.saveSession(apiKey, me.agent_name);
    return me;
  } catch (error) {
    this.apiKey = null;
    throw error;
  }
}
```

Prefer avoiding temporary mutation by allowing the request helper to accept an explicit candidate auth header. Add tests for wrong key, key-for-different-agent, and correct-key paths, and ensure failures do not write SecureStore or set `isAuthenticated=true`.

## Duplicate checks

Before submission I checked:
- current BoTTube issue search for mobile login/API-key validation wording; no matching issue was returned;
- RustChain #71 history for `api_key` and mobile-login wording; no matching report was found;
- this account's sent #71 history for API key/login/mobile/getMe/getAgentProfile wording; no prior matching claim was found.

## Evidence integrity

No production exploit, credential guessing, or unauthorized access was attempted. AI assistance was used for source review/drafting; no runtime result was fabricated.
