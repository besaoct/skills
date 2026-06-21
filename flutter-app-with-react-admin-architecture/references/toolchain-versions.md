# Toolchain & Dependency Version Reference

These are the version pins from the source codebase this skill is based on. They're a **starting point for new projects**, not a hard requirement — dependency versions age fast, so when scaffolding a genuinely new project, check current published versions (e.g. on pub.dev) rather than blindly applying these if there's reason to think they're stale.

## Build & Gradle

| Component | Version |
|---|---|
| Gradle Wrapper | `9.5.1` (in `gradle-wrapper.properties`) |
| Android Gradle Plugin | `9.2.0` |
| Kotlin Compiler | `2.3.21` (in `settings.gradle.kts` via `org.jetbrains.kotlin.android`) |
| Target Android Java Version | JVM 17 |

## Key Flutter Dependencies

| Package | Version constraint |
|---|---|
| `firebase_core` | `^4.10.0` |
| `firebase_crashlytics` | `^5.2.4` |
| `firebase_auth` | `^6.5.3` |
| `cloud_firestore` | `^6.6.0` |
| `flutter_riverpod` | `^3.3.2` |
| `drift` | `^2.18.0` |
| `go_router` | `^17.3.0` |
| `responsive_framework` | `^1.5.1` |

## When scaffolding a brand-new project

If the user is starting fresh rather than matching an existing codebase, it's worth a quick check (web search or `pub.dev`) on whether these are still the latest stable majors before pinning them — especially `firebase_core`, `go_router`, and `flutter_riverpod`, which release frequently and sometimes carry breaking changes between majors (e.g. Riverpod 2 → 3 changed the codegen API surface).
