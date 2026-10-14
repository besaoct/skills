# Secret detection: patterns, tools, and false positives

## Contents
1. What counts as a secret
2. What the bundled scanner covers
3. Better tools to add
4. Manual checks the scanners miss
5. Public by design (not secrets)
6. Handling false positives
7. Where secrets hide

## 1. What counts as a secret

A value is a secret if holding it lets someone do something the owner would not want them to do: read or write data, spend money, impersonate a user or service, sign tokens, decrypt data, or deploy code. Common categories:

- Database connection strings with passwords, database admin passwords.
- Cloud provider keys (AWS, GCP service account JSON, Azure client secrets).
- Payment provider secret keys and webhook signing secrets.
- Auth secrets: JWT signing keys, session secrets, OAuth client secrets, SAML or OIDC private keys.
- API keys for email, SMS, AI, maps (server-side), analytics with write access.
- Private keys and certificates (`.pem`, `.key`, `.p12`, SSH keys).
- Personal access tokens, CI tokens, registry tokens (`.npmrc`, `.pypirc`, `.netrc`).
- Infrastructure state and variables (`terraform.tfstate`, `*.tfvars`) which often embed credentials.
- Internal URLs with embedded basic-auth credentials.

## 2. What the bundled scanner covers

`scripts/scan_secrets.py` uses format-specific patterns for AWS access key IDs and secret keys, GitHub tokens, Stripe live keys, Slack tokens, Anthropic and OpenAI keys, SendGrid, Twilio, npm tokens, private key blocks, database URLs with passwords, Google API keys, and JWTs. It also flags generic assignments where a variable name contains words like `secret`, `password`, `token`, `api_key`, or `credential` and the value looks real (not a placeholder, not an env read). It flags tracked sensitive file names (`.env`, `*.pem`, `credentials.json`, `.npmrc`, `*.tfvars`, and similar).

Limits to state honestly in reports:

- Pattern based, so it cannot catch every format, especially custom or short secrets with no distinguishing prefix.
- Skips binaries, files over 1.5 MB, lockfiles, and common build directories.
- History scan covers commits reachable from refs in this clone. It does not see other clones, deleted branches already garbage collected, pull request refs on the host, or stashes.

## 3. Better tools to add

Use these when available, and recommend one for the pre-commit hook and CI.

| Tool | Strength | Typical commands |
|---|---|---|
| gitleaks | Fast, easy pre-commit and CI use, good history scan | `gitleaks detect --source . --redact` (history) and `gitleaks protect --staged --redact` (pre-commit) |
| trufflehog | Verifies whether many detected credentials are still live | `trufflehog git file://. --only-verified` and `trufflehog filesystem .` |
| detect-secrets | Baseline workflow for existing noisy repos | `detect-secrets scan > .secrets.baseline` |
| GitHub secret scanning and push protection | Blocks pushes containing known token formats | Enable under repository security settings where the plan supports it |

Always use `--redact` or equivalent so output does not echo values. If a tool cannot be installed in the current environment (network allowlists often block binary downloads), run the bundled scanner and give the user the commands to run the stronger tool locally.

## 4. Manual checks the scanners miss

- `git log --all --diff-filter=A --name-only --format= | sort -u | grep -Ei '\.env|\.pem|\.key|credentials|secret|\.tfvars|\.npmrc'` lists sensitive-looking file names ever added.
- Search for high-entropy strings near words like `key`, `token`, `auth`, `bearer`, `authorization`.
- Check config and fixtures: `docker-compose*.yml`, `*.yaml` Kubernetes manifests (`kind: Secret` with base64 data is not encrypted), CI files (`.github/workflows`, `.gitlab-ci.yml`), `application.properties`, `appsettings*.json`, `settings.py`, Postman collections, Jupyter notebooks, HAR files, SQL dumps, test fixtures, and seed scripts.
- Check frontend bundles and source maps in committed `dist` or `build` folders.
- Check README and docs for pasted credentials, curl examples with real tokens, and screenshots showing keys.
- Check Docker images and build logs if the project is containerized: `ENV` and `ARG` lines in a Dockerfile bake values into image layers.
- Check issue templates, scripts in `scripts/` and `tools/`, and shell history files accidentally committed.
- Base64-looking blobs: decode a sample to see whether it hides a credential or JSON key file.

## 5. Public by design (not secrets, but check restrictions)

These are meant to be embedded in client code. They are not secret, though some should be restricted in the provider console:

- Stripe publishable keys (`pk_live_...`, `pk_test_...`).
- Firebase web app config (`apiKey`, `authDomain`, `projectId`). Protect with security rules and App Check; the API key itself is an identifier.
- Supabase `anon` key (safe only when row level security is correctly configured). The `service_role` key is a secret.
- Google Maps or other browser keys, safe only when restricted by HTTP referrer or app to the intended use. Unrestricted ones can be abused for billing.
- Analytics measurement IDs, Sentry public DSNs, reCAPTCHA site keys, public OAuth client IDs.

When you classify something as public by design, say why in one line and, where relevant, remind the user to check that the key is restricted.

## 6. Handling false positives

- Placeholders (`your_api_key_here`, `changeme`, `xxxxxxxx`), example values in documentation, and test fixtures with obviously fake data are not findings. Confirm by reading the context.
- Hashes and checksums (lockfile integrity, commit SHAs, content hashes) resemble tokens but are not secrets.
- If a tool keeps flagging a safe value, add a narrowly scoped allowlist entry (for example a gitleaks `.gitleaksignore` fingerprint) with a comment explaining why. Do not disable rules wholesale.
- When uncertain whether a value is live, treat it as live and rotate. Rotation is cheap compared with a breach.

## 7. Where secrets hide

A short checklist for the final sweep:

1. Source code constants and default fallbacks (`process.env.X || "real-value"`).
2. Env files committed, copied (`.env.bak`, `.env.local.old`), or renamed (`env.txt`).
3. Config files for each environment.
4. Infra and CI definitions.
5. Test fixtures, seed data, and sample requests.
6. Documentation and screenshots.
7. Build outputs and source maps.
8. Git history, other branches, tags, and stashes.
9. Container image layers and CI logs.
10. Published packages (an npm or PyPI release can include an `.env` if `files` or `.npmignore` is wrong). Check `npm pack --dry-run` output.
