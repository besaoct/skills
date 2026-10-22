# Project Discovery and Feature Selection

## Interview behavior

Be concise, adaptive, and conversational. Ask about the project and desired feature scope before committing to an architecture. If the repository is accessible, inspect it first and do not ask questions that repository evidence already answers. Ask questions in small groups; accept partial answers. Avoid presenting a giant form or requiring the user to know security jargon.

## Initial questions

Establish:
1. **What are we securing?** Existing app, API, monorepo, new backend, or reusable package? What does the app do?
2. **What stack is it using?** Infer from the repository when possible; otherwise ask runtime/framework, language, database/ORM, and package manager.
3. **What is already in place?** Existing auth, users table, email provider, database, Redis/pub-sub, and deployment model.
4. **What does the user want?** Ask them to choose a preset or select features, and invite custom requirements.

Do not ask all follow-up questions at once. Ask only questions that affect the proposed design.

## Feature presets

### A — Essential passwordless auth
Recommended for a straightforward app that needs a secure baseline.
- Email OTP login and email verification
- Optional username, first-login provisioning if requested
- Short-lived access token
- Rotating opaque refresh token
- Session storage and logout
- OTP expiry, one-time use, attempt limits, resend throttles
- Input validation, enumeration resistance, rate limiting
- Safe errors, audit hooks, baseline tests

### B — Production auth with device controls
Recommended for apps where users manage active logins or need account-level control.
- Everything in A
- Device/session registry and active-session listing
- Per-session logout, logout everywhere, logout other sessions
- Configurable active session/device limits
- Device block/unblock with server-side enforcement
- Refresh-token reuse detection and token-family revocation
- Revocation-aware protected routes and distributed invalidation when multi-instance
- Concurrency tests, security events, operational guidance

### C — High-assurance authentication
Recommended for sensitive data, privileged users, or higher account-takeover risk.
- Everything in B
- Passkey/WebAuthn enrollment and login
- TOTP MFA and hashed single-use recovery codes
- Step-up authentication and recent-authentication checks
- MFA/passkey security-change protections
- Expanded threat model, abuse detection hooks, adversarial tests

### D — Custom scope
The user may select any combination. Explicitly identify dependencies and incompatibilities instead of forcing a preset.

## Feature decision groups

Offer these only when relevant, with choices such as **Required / Recommended / Optional / Not needed / Unsure**:

1. Authentication methods: email OTP, passkeys, TOTP, recovery codes, OAuth/SSO, future extension points.
2. Tokens and transport: JWT access token, opaque refresh token, cookie-based, bearer header, hybrid by client type.
3. Sessions: list sessions, individual logout, logout others, logout all, idle/absolute timeout, max concurrent sessions.
4. Devices: device metadata, device list, maximum registered devices, maximum active devices/sessions, block/unblock, trust/new-device verification, cross-device notifications.
5. Revocation timing: immediate server-side rejection required; best-effort client notification; multi-instance propagation requirements.
6. Storage/infrastructure: existing SQL/NoSQL database, ORM, Redis, queue/pub-sub, email provider, WebSocket/SSE infrastructure.
7. Deployment: single process, multiple instances, serverless, multi-region, unknown.
8. Security posture: standard production, sensitive/high assurance, regulated/compliance requirements if any.
9. Constraints: minimal dependencies, existing schema compatibility, no breaking changes, test scope, data retention.

## Recommendation rules

- Recommend the simplest architecture that meets the user's security requirements.
- Do not recommend Redis solely for fashion; explain when distributed throttling or revocation propagation needs shared infrastructure.
- If immediate access-token revocation is mandatory, do not propose purely stateless JWT verification as sufficient.
- If hard device limits are mandatory, explain that enforcement needs atomic server-side state and consistent handling across OTP, passkey, MFA, and refresh flows.
- If the app runs in multiple instances, identify how revocation, rate limits, and device limits remain consistent across instances.
- If browser device identification is requested, explain that browser fingerprints are not unique or trustworthy; propose a server-issued device registration ID and stronger cryptographic binding where justified.
- If passkeys or TOTP are requested, include secure enrollment, removal, recovery, and account-recovery policy—not just the happy-path verification.
- Reuse existing project infrastructure when appropriate, but do not retain unsafe legacy behavior just to avoid changes.
- Separate required security guarantees from optional UX features.
- State trade-offs plainly and let the user decide where a policy choice is genuinely theirs.

## Before implementation: confirm scope

Summarize:
- Project facts discovered
- Recommended preset and why
- Selected and excluded features
- Important defaults (token lifetimes, session/device limits, OTP policy) that still need values
- Required infrastructure and dependencies
- Security guarantees and limitations

Ask for approval if major architectural choices remain unresolved. If the user has already authorized autonomous implementation, proceed while documenting assumptions and avoid unsafe guesses.
