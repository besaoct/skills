# Monorepo scaffold

## Contents
1. Tooling choices
2. Standard layout
3. Shared packages
4. Boundary enforcement
5. Standard scripts and local development
6. Configuration and secrets
7. CI/CD for a monorepo
8. Versioning and releases

## 1. Tooling choices

A monorepo means one repository with many independently buildable projects and shared tooling. It does not mean one deployable. Pick tooling that matches the existing stack; do not migrate a working setup without a reason.

| Concern | Default choice | Notes |
|---|---|---|
| JS/TS package manager | pnpm workspaces | Fast, strict, disk efficient |
| Task orchestration and caching | Turborepo, or Nx for larger repos needing generators and strict boundary rules | Both give affected builds and remote cache |
| Go services | `go.work` workspace | One module per service |
| Python services | uv or Poetry workspaces | Only when there is a real reason for Python |
| Mobile (Flutter) | Melos for multi-package Dart | Only when mobile is in scope |
| Containers | Docker with multi-stage builds, one Dockerfile per deployable | Non-root, minimal base image |
| Local infra | Docker Compose | Database, cache, queue, search |
| Infra as code | Terraform | Separate `infra/` folder |

## 2. Standard layout

```text
repo/
  apps/                 # deployable user-facing and edge apps
    web/                # customer web (for example Next.js)
    admin/              # internal tool
    mobile/             # optional
    api/                # modular monolith backend (omit for pure microservices)
    gateway/            # optional BFF or API gateway
  services/             # independently deployable backend services (microservices or extracted parts)
  packages/             # shared libraries, no deployables
    contracts/          # OpenAPI, event schemas, generated types and clients
    ui/                 # design system components (see the UI skill)
    config/             # shared tsconfig, eslint, prettier, env schema
    observability/      # logger, tracing, metrics helpers
    auth/               # token verification, permission helpers
    testing/            # fixtures, factories, test containers helpers
  infra/                # terraform, helm or manifests, compose files
  tools/                # scripts, generators, codegen
  docs/                 # architecture.md, adr/, runbooks/
  .github/workflows/    # or the CI system in use
  package.json  pnpm-workspace.yaml  turbo.json  (or nx.json)
```

Rules:

- `apps/` and `services/` are leaves. Nothing imports from them.
- `packages/` never import from `apps/` or `services/`.
- Services never import each other. They share only `packages/contracts` and small utility packages.
- Keep each package small and single-purpose with an explicit public entry point.

## 3. Shared packages

**contracts** is the most important package. It holds:

- OpenAPI specs (or Protobuf) per service, plus event schemas (JSON Schema, Avro, or Protobuf).
- Generated TypeScript types, runtime validators (for example Zod generated from the schema), and typed API clients.
- A compatibility check script that fails CI on breaking changes (see `frontend-backend-contract.md`).

**config** holds shared compiler and lint settings and the environment schema helper so every app validates config the same way.

**observability** exposes one logger (structured JSON, correlation ID aware), one tracing setup (OpenTelemetry), and standard metrics (request duration histogram, error count, cache hit ratio, queue lag).

**ui** is the design system. Follow `production-ui-ux-and-centralized-styling` for tokens and components.

Avoid a giant `utils` or `common` package. If something is shared by two consumers and truly generic, create a named package for it.

## 4. Boundary enforcement

Boundaries that are not enforced erode within weeks. Add checks to CI:

- TypeScript: ESLint `no-restricted-imports` or `eslint-plugin-boundaries`, or `dependency-cruiser`, or Nx `enforce-module-boundaries` with tags (`type:app`, `type:service`, `type:package`, `scope:orders`).
- Go: `internal/` directories and a depguard rule.
- Database: separate credentials per service or module so a cross-boundary query fails at the database.
- Contracts: no import of another service's generated server code, only its client.

Fail the build on violations. Allow exceptions only through a recorded ADR.

## 5. Standard scripts and local development

Every project exposes the same script names, and the root runs them across the workspace with caching:

```text
install   dev   lint   typecheck   test   test:integration   build   start
db:migrate   db:seed   codegen   check:contracts
```

Local development requirements:

- `docker compose up` starts Postgres, Redis, and any queue or search dependency with health checks and named volumes.
- One command (for example `pnpm dev`) runs the needed apps and services with hot reload and prints the URLs.
- Seed data is deterministic and safe (no production data, no real personal data).
- Environment files: `.env.example` committed with every key and a comment; real `.env` ignored.
- A `doctor` script checks tool versions, ports, and dependencies and prints actionable fixes.

## 6. Configuration and secrets

- Parse and validate all environment variables at startup with a schema; exit non-zero with a clear message if invalid.
- Separate config by environment through variables, never by code branches on environment names where avoidable.
- Secrets come from a secret manager in deployed environments, never from the repo, images, or client bundles.
- Public (client-exposed) variables use an explicit prefix and contain nothing sensitive.
- Feature flags are config with ownership and an expiry date; they never replace authorization.

## 7. CI/CD for a monorepo

Pipeline stages, each cached and run only for affected projects:

1. Install with a frozen lockfile.
2. Lint, typecheck, unit tests (parallel by project).
3. Contract checks: OpenAPI lint, breaking-change diff against the main branch, event schema compatibility.
4. Integration tests with real Postgres and Redis (containers), including migration up and a rollback or forward-fix test.
5. Build images; scan dependencies, images, and secrets; generate an SBOM where required.
6. End-to-end smoke test against a composed environment.
7. Deploy per service on merge with progressive rollout (canary or blue-green), health-gated, with automatic rollback.

Practices:

- Affected-only execution (`turbo run --filter=...[origin/main]` or `nx affected`) plus remote caching keeps CI fast as the repo grows.
- Database migrations are backward compatible (expand, migrate, contract) so old and new code can run together during a rollout.
- Pin tool and runtime versions (`.nvmrc`, `packageManager` field, Go toolchain version).
- Branch protection: required checks, review, and no direct pushes to main.

## 8. Versioning and releases

- Applications are deployed from commit SHAs; tag releases.
- Published packages (if any) use Changesets or an equivalent for versioning and changelogs.
- Public APIs are versioned (`/v1`) with a documented deprecation policy; events carry a schema version.
- Keep a `CODEOWNERS` file so each folder has a named owner.
