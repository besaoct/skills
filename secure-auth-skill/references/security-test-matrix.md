# Security Test Matrix

Tailor this matrix to the chosen features and runtime. A feature excluded from scope may be marked not applicable with a reason. Do not mark a test passed unless it was actually run and passed.

## OTP and identity
- Expired, malformed, wrong, already-used, and superseded OTPs are rejected.
- OTP cannot be verified twice under concurrent requests.
- Guessing and resend limits hold across the actual deployment topology.
- Responses do not disclose whether an email account exists.
- Email/username normalization and database uniqueness hold under concurrent creation.
- Delivery failures do not accidentally authenticate users or leak OTPs.

## JWT and refresh tokens
- Wrong signature, disallowed algorithm, wrong issuer/audience/type, expired and not-yet-valid tokens are rejected.
- Missing or malformed claims fail safely.
- Refresh tokens are rotated atomically and stored hashed if persisted.
- Reuse of a rotated refresh token triggers the documented response.
- Parallel refresh requests cannot create multiple valid token branches beyond the documented policy.
- Revoked sessions/token families cannot refresh.
- Access token revocation behavior matches the stated guarantee.

## Sessions and devices
- A user can list only their own sessions/devices.
- Individual logout revokes the selected session, not unrelated sessions.
- Logout everywhere revokes all applicable server-side sessions/token families.
- Device blocks survive browser storage clearing, new session attempts, token refresh, and alternate auth methods.
- Device/session caps hold under concurrent logins and across application instances.
- Expired or revoked device registration does not grant trust.
- Client-supplied device labels, user agents, and fingerprints cannot bypass controls.
- Missed real-time events do not permit a revoked session to access protected routes.
- Cross-tab/client state updates work where included, while server enforcement remains authoritative.

## Passkeys/WebAuthn (if selected)
- Invalid, expired, reused, or wrong-purpose challenges are rejected.
- Wrong origin, RP ID, credential, signature, and user handle are rejected.
- Credential removal/enrollment follows the required reauthentication policy.
- Credentials cannot be attached to another user's account.
- Recovery/replacement does not silently bypass the account security policy.

## MFA (if selected)
- Invalid/expired TOTP and repeated accepted time-step codes follow policy.
- Recovery codes are single-use and stored safely.
- MFA enrollment is not active before confirmation.
- Disabling/resetting MFA requires the configured reauthentication/recovery checks.
- Alternative login methods cannot bypass an enforced MFA policy.
- Step-up authorization expires and cannot be reused for unrelated actions.

## HTTP, authorization, and operations
- Cookie-authenticated state changes enforce CSRF/Origin policy.
- CORS and trusted proxy behavior match configuration.
- Authentication does not imply authorization; tenant/resource boundaries are tested.
- Errors and logs contain no OTPs, tokens, recovery codes, private keys, or secrets.
- Rate limits are enforced on every relevant endpoint and across instances when required.
- Account suspension and security changes invalidate the intended sessions.
- Cleanup, migrations, indexes, and rollback behavior are tested where applicable.

## Required evidence in final report
For every in-scope row, record test name/command, result, and any limitation. Distinguish tests not run from tests that failed. List residual risks and infrastructure-dependent guarantees explicitly.
