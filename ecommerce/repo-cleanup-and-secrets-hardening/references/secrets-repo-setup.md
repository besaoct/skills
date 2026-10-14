# Private secrets repository

## Contents
1. Purpose and the one rule that matters
2. Prerequisites and where to run the commands
3. Repository layout
4. Encrypting with SOPS and age
5. Creating the repository safely
6. The secrets index
7. Daily use: pulling and adding secrets
8. Access and hygiene
9. Plaintext fallback
10. If the session cannot do this directly

## 1. Purpose and the one rule that matters

A separate private repository holds the application's environment values and related secrets, so the owner has one reliable place to recover them from and the application repository never contains them.

The one rule: this repository must never become public and its plaintext must never leak. A private repository is protected only by an access setting that one click can change. So the default design encrypts the files inside it, which means a mistake in visibility, a shared collaborator account, or a stolen token does not by itself expose the values. The decryption key lives outside any repository, in the owner's password manager.

## 2. Prerequisites and where to run the commands

Needed tools: `git`, GitHub CLI `gh` (authenticated), `sops`, and `age`.

Preferred: the user runs the encrypt and push steps on their own machine, so secret values never pass through this session. In that case, prepare the repository skeleton and give the user the exact commands. If the values already exist in the user's local `.env` files and this session runs on that same machine (for example, a local Claude Code session), working directly is fine, but still never display the values.

Ask before creating any remote repository and confirm the owner (personal account or organization) and the repository name.

## 3. Repository layout

Name: `<app>-secrets` (for example `shopfront-secrets`). Keep one secrets repository per application, or one per organization with a folder per application if the team prefers.

```text
<app>-secrets/
  README.md              what this is, how to decrypt, who has access (no values)
  SECRETS_INDEX.md       inventory of every secret: name, purpose, provider, env, owner, last rotated
  .sops.yaml             encryption rules and recipient public keys
  .gitignore             ignores decrypted output files
  env/
    development.env      dotenv format, encrypted values
    staging.env
    production.env
  files/                 encrypted binary or JSON files (service account keys, certificates)
    gcp-service-account.json
    signing-key.pem
  services/              optional: per-service env files for monorepos
    api/production.env
    web/production.env
```

With SOPS, the files keep readable key names (`DATABASE_URL=ENC[AES256_GCM,data:...]`), so diffs show which variables changed without exposing values.

## 4. Encrypting with SOPS and age

One-time setup on the owner's machine:

```bash
# install: macOS `brew install sops age`; Linux via your package manager or the project release pages
age-keygen -o ~/.config/sops/age/keys.txt
# the output shows a public key beginning with "age1..."; the private key stays in that file
```

Store the contents of `keys.txt` in a password manager and keep a second offline backup. Losing it means losing access to the encrypted secrets. It never goes into any repository.

Rules file `.sops.yaml` in the secrets repo (replace the public key):

```yaml
creation_rules:
  - path_regex: env/.*\.env$
    age: age1REPLACE_WITH_PUBLIC_KEY
  - path_regex: files/.*
    age: age1REPLACE_WITH_PUBLIC_KEY
```

Add more `age` recipients (comma separated) for teammates who need access, and use separate recipients per environment if production access must be narrower.

Encrypt a local env file into the repo:

```bash
sops --encrypt --input-type dotenv --output-type dotenv /path/to/app/.env > env/development.env
sops --encrypt /path/to/service-account.json > files/gcp-service-account.json
```

Decrypt when needed:

```bash
sops --decrypt --input-type dotenv --output-type dotenv env/production.env > /path/to/app/.env
sops --decrypt files/gcp-service-account.json > /path/to/service-account.json
```

Edit in place (decrypts to your editor, re-encrypts on save): `sops env/production.env`.

Make sure decrypted outputs are never created inside the secrets repository folder, or that `.gitignore` there covers them (`*.dec`, `*.decrypted`, `.env`).

Verify the encryption worked before committing: open the file and confirm every value shows `ENC[...]` and a `sops:` metadata block exists.

## 5. Creating the repository safely

After the user confirms:

```bash
gh repo create <owner>/<app>-secrets --private \
  --description "Encrypted secrets for <app>. Private. Never make public."

# verify immediately; stop if this does not say private
gh repo view <owner>/<app>-secrets --json visibility,isPrivate
```

If the result is not private, stop, fix it, and do not push anything.

Then:

```bash
mkdir <app>-secrets && cd <app>-secrets
git init -b main
# add README.md, SECRETS_INDEX.md, .sops.yaml, .gitignore, then encrypted files
git add .
git status                         # confirm only encrypted files and docs are staged
git commit -m "Add encrypted secrets and index"
git remote add origin git@github.com:<owner>/<app>-secrets.git
git push -u origin main
```

Repository settings to apply (via the web UI or `gh api`):

- Disable forking (organization setting) and disable issues, wiki, and projects (nothing there should hold secrets).
- Add collaborators sparingly, with the lowest permission that works, and turn on two-factor authentication for every account with access.
- Protect `main` (require pull request review where the team is more than one person).
- Enable secret scanning and push protection if the plan supports it. Note that scanning cannot recognize encrypted values, which is the point.

Never add the application repository as a remote of the secrets repository, never add the secrets repository as a submodule of the application, and never reference its URL in public documentation.

## 6. The secrets index

`SECRETS_INDEX.md` records metadata about each secret, never a value. It is what makes rotation and onboarding manageable.

```markdown
# Secrets index for <app>

| Name | Purpose | Provider | Environments | Owner | Last rotated | How to rotate |
|---|---|---|---|---|---|---|
| DATABASE_URL | Primary PostgreSQL connection | Managed Postgres | dev, prod | Backend lead | 2026-10-12 | Create new DB user, update env, restart |
| JWT_SECRET | Signs access tokens | Self-generated | dev, prod | Backend lead | 2026-10-12 | `openssl rand -base64 32`; forces re-login |
| STRIPE_SECRET_KEY | Server-side payments | Stripe | prod | Finance/Eng | 2026-10-12 | Roll key in dashboard |
| STRIPE_WEBHOOK_SECRET | Verifies webhooks | Stripe | prod | Eng | 2026-10-12 | Regenerate endpoint secret |

## Files
| Path | Purpose | Used by |
|---|---|---|
| files/gcp-service-account.json | Storage access | api service |

## Not secrets (public by design)
NEXT_PUBLIC_API_URL, STRIPE_PUBLISHABLE_KEY
```

Keep it in step with `.env.example` in the application repository: every variable in the example appears in the index, and every secret in the index is either in the example or documented as a file.

## 7. Daily use: pulling and adding secrets

New developer or new machine:

1. Get access to the secrets repository and the age private key (shared securely by the owner, never through chat or email in plaintext).
2. Clone the secrets repository next to the app.
3. `sops --decrypt --input-type dotenv --output-type dotenv env/development.env > ../app/.env`.

Adding or rotating a secret:

1. Update the value in the platform's secret store and wherever it is consumed.
2. `sops env/production.env` (edit), save, commit with a message that names the variable but not the value.
3. Update `SECRETS_INDEX.md` (last rotated date, any change in owner or purpose).
4. If the variable is new, add it with a placeholder to `.env.example` and to the config validation in the application repository.

## 8. Access and hygiene

- Least privilege: only people who deploy or operate the system need production secrets.
- Separate environments: development secrets are usable by the whole team, production by few.
- Rotate on schedule and after any staff departure or suspected exposure; record it in the index.
- Audit access periodically (collaborator list, deploy keys, tokens with repository scope).
- Do not paste values into tickets, chat, or documents; reference the variable name and the index.
- Back up the age private key and test recovery once.

## 9. Plaintext fallback

If the user explicitly wants plain `.env` files in the private repository instead of encrypted ones, honor it after stating the risk once, briefly: plaintext secrets are exposed to anyone who gains read access to the repository, including through a visibility change, a compromised account or token, or a forked or cloned copy. Then proceed with the same layout minus the `sops` steps, and add:

- Verification that the repository is private immediately after creation and again after any settings change.
- A strict collaborator list with two-factor authentication.
- A README line at the top: "Private. Contains plaintext secrets. Never make public."
- A reminder that the secret scanner will (rightly) flag this repository; do not scan it into other tools or share its contents.

## 10. If the session cannot do this directly

The environment may not allow it: no `gh` authentication, no `sops` or `age` installed and no network route to install them, or the secret values exist only on the user's machine while this session runs elsewhere. In that case:

1. Create the skeleton files (README, `SECRETS_INDEX.md` with names taken from `.env.example`, `.sops.yaml` with a placeholder for the public key, `.gitignore`) and send them to the user.
2. Give the user a short, ordered command list to run locally: install tools, generate the age key, encrypt, create the private repo, verify privacy, push.
3. Tell them what to check afterward: that the values show as `ENC[...]`, that the repository is private, and that the age key is saved outside any repository.
4. Do not ask them to paste values into the chat to make it easier.
