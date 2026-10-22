# Implementation Workflow and Completion Gate

## Suggested implementation sequence

1. **Repository reconnaissance:** map entry points, routes, middleware/guards, identity model, persistence, email delivery, configuration, tests, deployment topology.
2. **Scope matrix:** record user choices, recommendations accepted/rejected, non-goals, dependencies, and unresolved decisions.
3. **Threat model:** identify assets, trust boundaries, attacker capabilities, account takeover paths, replay/race risks, and operational failure modes.
4. **Architecture and data model:** define entities, indexes, constraints, state transitions, transactions, token lifetimes, revocation model, and adapter boundaries.
5. **Configuration and primitives:** validated config, secure random generation, token handling using maintained libraries, safe errors, logger redaction.
6. **Identity and OTP:** challenge creation, email delivery integration, atomic verification, provisioning, throttling.
7. **Tokens and sessions:** access validation, refresh rotation, session persistence, revocation, logout.
8. **Device management:** metadata, registration, listing, limits, blocking, atomic enforcement, session-specific controls.
9. **Passkeys and MFA:** only if selected; include enrollment, disablement, recovery, step-up policy, and tests.
10. **Framework integration:** middleware/guards/handlers, cookie or bearer transport, CSRF/Origin rules, server/client boundaries.
11. **Events and operations:** audit logs, revocation propagation, cleanup, metrics, notifications, deployment configuration.
12. **Adversarial testing:** use the security test matrix; test concurrent and alternate paths.
13. **Final audit:** scan for bypass routes, unsafe defaults, secret leakage, missing validation, untested migrations, and undocumented assumptions.

## Requirements matrix template

| Requirement | Status | Implementation location | Security invariant | Verification evidence | Notes |
|---|---|---|---|---|---|
| Example: refresh rotation | Required | service/repository | Old refresh token cannot mint a new session | test command + result | Atomic transaction required |

Statuses: Required, Recommended, Optional, Excluded, Not applicable, Blocked, Implemented/test incomplete, Implemented/tested.

## Completion gate

Do not declare completion until:
- Every in-scope requirement has a status and implementation/test mapping.
- All authentication entry points and refresh routes have been checked for policy bypass.
- Device/session limits and revocation have concurrency coverage when included.
- Passkey/MFA recovery and disablement paths have been tested when included.
- Runtime config and migrations are validated.
- Tests actually run are reported accurately.
- Missing infrastructure, skipped tests, unresolved decisions, and residual risks are explicit.
- No claim of “zero loopholes” or “perfect security” is made.
