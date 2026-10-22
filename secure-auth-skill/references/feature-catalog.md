# Authentication Feature Catalog

Use this as an inventory, not as a mandate to implement every feature. Mark each item required, recommended, optional, excluded, blocked, or not applicable in the project requirements matrix.

## Identity and core flows
- Email OTP/passwordless login
- Email verification and challenge lifecycle
- Existing-user lookup and first-login provisioning
- Optional unique username with normalization and database uniqueness
- Configurable identity fields and user schema
- Account active/suspended/disabled states
- Login, logout, current user, session state
- Authentication lifecycle hooks
- Step-up authentication
- No registration UI, password login, forgot-password, or reset-password flows unless requested

## OTP and abuse controls
- Cryptographically secure OTP generation
- Expiration, single use, atomic consumption, invalidation on resend
- Hashed OTP/challenge storage where appropriate
- Attempt limits, resend cooldown, email/account/IP/device throttling
- Distributed rate limiting where deployment requires it
- Replay and brute-force protection
- Email enumeration resistance and generic responses
- Email provider adapter and delivery failure handling
- Idempotency and concurrency protection

## JWT/access tokens
- Short lifetime and explicit token type
- Algorithm allowlist; no algorithm confusion
- Validate issuer, audience, subject, expiry, issued-at, not-before, and relevant claims
- Key separation, rotation, `kid`, key-strength checks
- Minimal claims and no secrets/PII in payload
- Revocation strategy and token-version strategy where suitable
- Safe header/cookie extraction and consistent auth context

## Refresh tokens
- High-entropy opaque tokens
- Hash at rest
- Rotation and reuse detection
- Token families and family invalidation
- Atomic rotation and concurrent request handling
- Idle and absolute expiration
- Session binding and revocation
- Cleanup and audit events

## Sessions and devices
- Session/device registry and current-session identification
- List active sessions/devices with metadata and timestamps
- Browser/OS/device category metadata, user agent, IP history subject to policy
- Server-issued random device registration identifier
- Optional cryptographic device-bound credential
- Per-session logout, logout others, logout everywhere
- Session revocation and session invalidation on account changes
- Maximum active sessions and/or registered devices
- Device allowlist/blocklist, temporary/permanent blocks, unblock policy
- Device trust status and new-device verification
- Atomic limit enforcement across concurrent logins and all auth methods
- Session idle timeout and absolute lifetime
- Cross-tab, cross-device, and mobile synchronization events
- Revocation-aware request validation; event transport is not the enforcement mechanism
- Privacy-aware collection and metadata retention

## Passkeys / WebAuthn
- Enrollment, authentication, multiple credentials, naming/listing/removal
- Challenge generation, expiration, single use, and intent binding
- Validate origin, RP ID, client data, authenticator data, credential ownership, and signature
- User presence/verification policy
- Discoverable credentials and authenticator preferences where supported
- Credential counter handling where applicable
- Enrollment/removal reauthentication
- Recovery and replacement policies
- Browser client/server separation and conformance tests
- Use a maintained standards-compliant implementation; do not hand-roll WebAuthn

## 2FA/MFA
- TOTP enrollment and verification
- Provisioning URI/QR data (UI rendering remains application-owned)
- TOTP time window and replay controls
- Hashed single-use recovery codes and regeneration
- Enable/disable/recovery security policies
- MFA challenges, expiry, attempt limits
- Passkeys as passwordless credentials or MFA according to policy
- Step-up auth and recent-auth requirements
- Per-user/role/tenant enforcement
- MFA requirements for new device, passkey removal, recovery, or security changes
- Optional push/hardware-key integrations via adapters

## HTTP and browser security
- Secure HttpOnly cookies and explicit Secure/SameSite/domain/path policies
- CSRF and Origin validation for cookie-authenticated state changes
- CORS guidance, TLS assumptions, cache-control
- Trusted proxy configuration for forwarded headers
- No secrets in URLs or logs
- Safe redirects and request-size limits
- SSR-safe imports and strict server/client separation
- Browser storage policy; avoid implying localStorage is safe for secrets

## Validation and data integrity
- Runtime schemas and normalization
- Unknown-field rejection where appropriate
- Input size and length limits
- Prototype pollution and mass-assignment protection
- Injection-safe data access patterns
- Unique database constraints and indexes
- Atomic transactions and compare-and-set operations
- Idempotency where relevant
- Race-condition and replay prevention

## Authorization and tenancy
- Keep authentication distinct from authorization
- Hooks for roles, permissions, resource ownership, and tenant isolation
- Account status checks
- Default-deny integration patterns
- Reauthentication for sensitive changes

## Storage and integration
- User, identity, challenge, session, device, refresh token, passkey, MFA, recovery-code, rate-limit, and audit repositories as needed
- Database transaction and atomic operation interfaces
- Existing DB/ORM integration; optional adapters only where useful
- Email, logger, event, cache, and pub/sub adapters
- Express, Node.js, NestJS, Next.js, Fastify, Hono or other project-specific integration
- Framework-independent core where practical
- No UI components unless explicitly requested

## Events, logging, operations
- Structured security events and audit hooks
- Redaction of OTPs, tokens, recovery codes, keys, and sensitive personal data
- Correlation/request IDs
- New device, MFA/passkey change, refresh reuse, block/revoke events
- Event deduplication, reconnection, missed-event recovery
- Metrics and observability hooks
- Cleanup, retention, key rotation, backups, incident response

## Testing and supply chain
- Unit, integration, end-to-end, concurrency, fuzz/property tests where appropriate
- OTP expiry/replay/guessing and enumeration tests
- JWT claim/algorithm validation tests
- Refresh rotation/reuse/concurrency tests
- Device limit/block bypass and race tests
- Individual/global logout and stale-token tests
- Cross-instance revocation tests
- WebAuthn conformance and MFA replay/recovery tests
- CSRF, Origin, proxy, rate-limit, and authorization boundary tests
- Dependency and secret scanning, static analysis, reproducible release practices
- Document runtime support, limitations, threat model, configuration, migrations, and residual risks
