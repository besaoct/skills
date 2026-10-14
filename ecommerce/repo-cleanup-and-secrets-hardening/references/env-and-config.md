# Environment variables and configuration

## Contents
1. Principles
2. File layout and `.gitignore`
3. `.env.example` format
4. Moving a hardcoded secret to env
5. Startup validation
6. Public vs server-only variables
7. Docker and CI
8. Logging and error hygiene
9. Preventing regressions

## 1. Principles

- Code holds names, never values. Values come from the environment at runtime.
- A missing required variable should stop the app at startup with a clear message, not fail later in a confusing way and not fall back to a hardcoded default.
- Defaults are allowed only for non-sensitive settings (port, log level, feature toggles, local development URLs).
- Different environments use different values. A development database must never share credentials with production.
- Anything compiled into a client bundle is public. Do not put secrets behind a "public" prefix.

## 2. File layout and `.gitignore`

Typical layout:

```text
.env.example          committed: every variable name, safe placeholders, short comments
.env                  local values, never committed
.env.local            local overrides, never committed
.env.development      only if it holds non-sensitive defaults and the team agrees; otherwise ignore
.env.production       never committed
```

Add to `.gitignore` (adapt to the project):

```gitignore
# environment and secrets
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
*.keystore
credentials.json
service-account*.json
*.tfvars
terraform.tfstate*
.npmrc.local
```

Verify: `git check-ignore -v .env` should print the matching rule, and `git ls-files | grep -i env` should list only the example file.

If a real env file is already tracked, untrack it without deleting the local copy: `git rm --cached .env`. This does not remove it from history (see `history-remediation.md`).

Monorepos: put an `.env.example` in each app or service that reads variables, plus a root one only if the root tooling uses variables.

## 3. `.env.example` format

Group variables, name each, say whether it is required, and give a safe placeholder. Never copy real values, not even partially.

```dotenv
# --- Server ---
NODE_ENV=development
PORT=3000

# --- Database (required) ---
# Connection string for PostgreSQL. Create a dedicated user per environment.
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DB_NAME

# --- Auth (required) ---
# 32+ random bytes, for example from: openssl rand -base64 32
JWT_SECRET=replace_with_random_value

# --- Third-party services (optional in development) ---
STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_WEBHOOK_SECRET=whsec_replace_me

# --- Client-exposed (public by design) ---
NEXT_PUBLIC_API_URL=http://localhost:3000
```

Keep it in sync: every variable the code reads appears here, and every variable here is read by the code. A quick check is to grep for `process.env.`, `os.environ`, `os.Getenv`, `env::var`, or `import.meta.env.` and compare.

## 4. Moving a hardcoded secret to env

1. Locate every use of the value (grep for the value itself and for the config key), including tests, scripts, and docs.
2. Choose a descriptive variable name (`STRIPE_SECRET_KEY`, not `KEY1`).
3. Replace the literal with a read from validated config (section 5). Do not leave the old literal as a fallback.
4. Add the name to `.env.example` with a placeholder.
5. Put the real value in the local `.env` (and later in the private secrets repo and the hosting platform's secret settings). Do this without printing the value.
6. Remove the value from docs, comments, fixtures, and scripts. Tests should use obvious fake values or generated ones.
7. Re-run the scanner to confirm the literal is gone from the working tree.
8. Mark the secret for rotation if it was ever committed.

## 5. Startup validation

Validate once, in one module, and import config from there. Never read `process.env` ad hoc across the codebase.

TypeScript with Zod:

```ts
import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_SECRET_KEY: z.string().startsWith("sk_"),
});

const parsed = schema.safeParse(process.env);
if (!parsed.success) {
  const missing = parsed.error.issues.map((i) => i.path.join(".")).join(", ");
  console.error(`Invalid environment configuration. Check: ${missing}`);
  process.exit(1);
}
export const config = parsed.data;
```

Note that the error lists variable names only, never values.

Python with pydantic-settings:

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str = Field(min_length=32)
    port: int = 8000

settings = Settings()  # raises a clear error naming missing fields
```

Go: use a small loader such as `envconfig` or `caarlos0/env` with `required` tags, and fail in `main` before serving. Other stacks have equivalents; the rule is the same: one place, fail fast, names not values.

## 6. Public vs server-only variables

Frameworks expose some variables to the browser by prefix. Anything with these prefixes ends up in client JavaScript:

| Framework | Public prefix |
|---|---|
| Next.js | `NEXT_PUBLIC_` |
| Vite (React, Vue, Svelte) | `VITE_` |
| Create React App | `REACT_APP_` |
| Expo / React Native | `EXPO_PUBLIC_` |
| Nuxt | `NUXT_PUBLIC_` (runtime config `public`) |
| SvelteKit | `PUBLIC_` (via `$env/static/public`) |

Rules:

- Secrets never carry a public prefix. If a secret is needed by the client, the architecture is wrong: call a server route that holds the secret.
- Server-only variables are read in server code paths only. In Next.js, that means route handlers, server components, and server actions, not client components.
- Check built output for leaks: grep the build directory for variable names and known secret prefixes. Do not commit `dist`, `.next`, or source maps.

## 7. Docker and CI

Docker:

- Add `.env*`, key files, and `.git` to `.dockerignore`.
- Do not `COPY .env` and do not put secrets in `ENV` or `ARG` lines; both persist in image layers. Pass values at runtime (`docker run --env-file`, orchestrator secrets) or use BuildKit secret mounts (`RUN --mount=type=secret,id=...`) for build-time needs.
- Compose files: reference variables with `${VAR}` and load from a local ignored env file; no literal passwords in committed `docker-compose.yml` except throwaway local-only database passwords that are clearly dev values and documented as such.

CI and hosting:

- Store secrets in the platform's secret store (GitHub Actions secrets, Vercel/Netlify/Render environment settings, cloud secret managers), per environment.
- Do not echo secrets in workflow steps; avoid `set -x` around commands using them. Prefer OIDC federation to cloud providers over long-lived keys.
- Restrict secrets to protected branches and environments where possible.
- Pull request workflows from forks do not receive secrets by default; keep it that way.

## 8. Logging and error hygiene

- Do not log full request headers, bodies containing credentials, connection strings, or tokens. Redact fields named `authorization`, `cookie`, `password`, `token`, `secret`, `apiKey`.
- Error responses to clients never include stack traces, SQL, connection strings, or environment values.
- Remove debug prints that dump `process.env`, config objects, or request objects.

## 9. Preventing regressions

- Pre-commit hook running a secret scan on staged files (gitleaks `protect --staged`, or the bundled scanner with `--no-history`).
- The same scan in CI on every pull request, failing the build on findings.
- Host-level push protection and secret scanning where available.
- A short section in the README: "Configuration" listing required variable names (from `.env.example`) and where the real values are kept (the private secrets repo, by name, without links that expose anything).
- Code review habit: any new variable gets a line in `.env.example` and validation in the config module.
