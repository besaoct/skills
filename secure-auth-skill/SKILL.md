---
name: secure-auth
description: Plan, implement, integrate, and security-test project-specific authentication systems. Interview the user about their project and desired features, recommend options, then build only the agreed scope while tracking every security requirement to tests.
---

# Secure Auth Engineering Skill

Use this skill whenever the user asks to design, add, review, harden, or replace authentication, sessions, device management, passkeys, or MFA in a software project.

## Mission

Build a secure, project-appropriate authentication system without skipping requirements, blindly adding features, or imposing unnecessary dependencies. The solution is UI-independent unless the user explicitly requests UI. Treat security as a set of verifiable invariants, not as a claim that the system has “no loopholes.” Never claim perfect security.

## Mandatory workflow

### Phase 1 — Discover the project

1. Inspect the repository before proposing implementation details when project files are available. Identify runtime, language, framework, package manager, entry points, existing auth, data store/ORM, email delivery, deployment model, tests, and conventions.
2. Do not overwrite or replace existing authentication until its behavior and migration risks are understood.
3. Ask the user for any material facts that cannot be inferred from the repository. If no repository is available, ask what project they are building and which stack they use.
4. Ask the user what features they want. Do not assume every optional feature is wanted.
5. Present a compact set of selectable options, with recommended defaults and short trade-offs. Let the user choose a preset, customize individual features, or request the full recommended scope. Accept partial answers and do not repeat questions already answered.

### Phase 2 — Interview and recommend

Use `references/feature-catalog.md` as the full feature inventory and `references/project-discovery.md` for the interview. Ask conversationally; avoid dumping the entire catalog at once.

Collect these decisions before implementation:
- Project purpose, stack, current auth state, and whether this is a new implementation or migration.
- Authentication methods wanted: email OTP, passkeys, TOTP/MFA, other methods.
- Session/token requirements: JWT access token, refresh rotation, cookies or bearer tokens, logout/revocation expectations.
- Device requirements: device/session listing, maximum devices/sessions, block/unblock, per-device logout, logout everywhere, cross-device updates.
- Storage and infrastructure already available: database, ORM, Redis/pub-sub, email provider, event transport.
- Deployment model: one instance, multi-instance, serverless, multi-region, or not yet known.
- Constraints: compatibility, dependency policy, data retention/privacy, timeline, and test expectations.

Offer options in clear groups, for example:
- **Preset A — Essential:** email OTP, short-lived access token, rotating refresh token, sessions, logout, rate limits, input validation, audit hooks, and tests.
- **Preset B — Recommended production:** Essential plus device/session management, configurable device limits, server-side revocation, concurrency protections, security events, and deployment guidance.
- **Preset C — High assurance:** Recommended production plus passkeys, TOTP MFA, recovery codes, step-up authentication, stronger risk controls, and expanded adversarial testing.
- **Custom:** let the user select individual features and exclusions.

These are starting points, not automatic authorization to implement every feature. Recommend a preset based on the actual project and explain important trade-offs briefly. Always allow the user to choose less, more, or custom scope. If a choice materially affects security or architecture, ask before proceeding.

### Phase 3 — Produce a scope and architecture plan

Before coding, create or present a requirements matrix with columns:
- Requirement / feature
- Status: required, recommended, optional, excluded, not applicable, or blocked
- Project-specific implementation
- Data/storage implications
- Security invariant
- Verification test
- Decision or rationale

Then document:
- Threat model and trust boundaries
- Authentication flows and state transitions
- Data model and indexes/migrations
- Token and session lifecycle
- Device identity and enforcement model
- Revocation and cross-instance propagation strategy
- Rate-limiting and abuse strategy
- Framework integration boundaries
- Dependencies and why each is needed
- Test plan and rollback/migration plan if applicable

Do not code a major auth redesign before the user has had a chance to approve the material architecture and scope, unless they explicitly asked you to proceed autonomously.

### Phase 4 — Implement safely

1. Follow existing project conventions unless unsafe or unsuitable.
2. Keep core authentication logic separate from UI and framework adapters where practical.
3. Prefer existing maintained dependencies or runtime primitives over introducing redundant packages. Do not hand-roll cryptography or standards protocols.
4. Use atomic database operations/transactions for OTP consumption, refresh rotation, device limits, and revocation-sensitive state changes.
5. Enforce every security-critical policy server-side on every applicable route and authentication method.
6. Add migrations, indexes, configuration validation, safe errors, audit events, and tests alongside implementation.
7. Never log OTPs, access tokens, refresh tokens, recovery codes, private keys, or other secrets.
8. Never treat user-agent strings, IP addresses, browser fingerprints, or client-provided device labels as proof of identity.
9. If required infrastructure is absent, present practical alternatives and their trade-offs. Do not silently weaken a required guarantee.
10. Do not invent environment variables, providers, endpoints, schema fields, or successful test results. Verify them in the repository or clearly label assumptions.

### Phase 5 — Verify and report

Use `references/security-test-matrix.md`. Run relevant formatters, type checks, unit/integration tests, migrations checks, and security tests available in the project. Test alternate auth paths and concurrent requests, not just happy paths.

Update the requirements matrix with evidence and one of:
- Implemented and tested
- Implemented, test incomplete
- Not implemented
- Blocked by missing infrastructure or decision
- Not applicable, with reason

Finish with a concise report of changed files, chosen design, tests actually run and results, migration/configuration steps, unresolved risks, and remaining items. Never claim all requirements are met unless the matrix supports that claim. Never claim zero vulnerabilities.

## Non-negotiable security principles

- Authentication and authorization are separate concerns.
- Validate inputs at runtime; TypeScript types alone are not validation.
- Enforce unique identity constraints in persistent storage, not only in application code.
- OTPs and one-time challenges must expire, be single-use, be rate-limited, and be consumed atomically.
- Access tokens should be short-lived. Refresh tokens should be high entropy, stored hashed when persisted, rotated atomically, and checked for reuse.
- JWT verification must pin allowed algorithms and validate relevant claims, issuer, audience, expiry, and token type.
- Immediate revocation cannot be guaranteed by purely stateless JWT validation. Choose and document a server-side revocation strategy consistent with the user's requirement.
- Global logout must revoke server-side sessions/token families, not merely clear browser storage.
- Device limits and device blocks must be enforced atomically on the server across all authentication and refresh routes.
- Real-time events improve client synchronization but do not replace server-side revocation checks.
- Browser fingerprints are unstable and spoofable. Device metadata is descriptive, not an authentication factor.
- Passkeys require standards-compliant WebAuthn validation, including challenge, origin, RP ID, credential, and signature checks.
- MFA enrollment, disablement, recovery, and authenticator removal require explicit security policies and appropriate reauthentication.
- Cookies require deliberate Secure, HttpOnly, SameSite, domain/path, CSRF, and origin policies.
- Trust forwarded IP headers only behind explicitly configured trusted proxies.
- Do not promise “no loopholes”; identify residual risks and verify the security properties that can be tested.

## References

Read the relevant reference files as needed:
- `references/project-discovery.md` — user interview and decision options.
- `references/feature-catalog.md` — comprehensive feature inventory.
- `references/security-test-matrix.md` — mandatory verification scenarios.
- `references/implementation-workflow.md` — implementation sequence and completion gate.
