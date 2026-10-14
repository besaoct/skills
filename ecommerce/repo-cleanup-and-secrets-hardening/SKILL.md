---
name: repo-cleanup-and-secrets-hardening
description: Final-pass cleanup and security hardening for vibe-coded or AI-generated projects before they are committed, shared, deployed, or open-sourced. Removes noise (redundant comments, commented-out code, scratch and duplicate files, stale docs, README badge walls, fake UI pills and placeholder text), finds and removes hardcoded secrets, moves them to proper env files with .env.example and startup validation, scans git history for leaked credentials, guides rotation and a clean repo recreation if secrets were ever committed, and sets up a separate private secrets repo. Use whenever the user says clean up, tidy, polish, finalize, prepare for production, ship, publish, make public, "remove AI traces", "remove unnecessary comments or files", "check for secrets", "I pushed my .env", or asks whether a repo is safe to push, even if they never mention secrets.
---

# Repo Cleanup and Secrets Hardening

The goal is a repository that contains the product and nothing else: no leftover scaffolding, no narration from the tools that wrote it, no claims the product cannot back up, and no credential that could hurt the owner if the repo became public tomorrow. The user should be able to ship it and stop thinking about it.

Two kinds of work are involved and they carry different risk. Cleanup is behavior-preserving and reversible, so it can be done confidently in small, reviewable steps. Secret handling is not reversible once a secret has been pushed, so it gets more care, more questions, and no shortcuts.

## Ground rules

1. **Never print a secret value.** Not in chat, logs, reports, commit messages, or summaries. Refer to a secret by type, file, line, and a masked preview (first four characters at most). The bundled scanner already masks values; keep it that way in everything you write.
2. **Never ask the user to paste secrets into the chat.** If values are needed, they come from the user's own local files, and the final step that touches them (encrypting, pushing to the secrets repo) is best run by the user on their own machine. See `references/secrets-repo-setup.md`.
3. **Confirm before anything destructive or hard to undo**: deleting files that are not obviously junk, deleting or force-pushing a remote repository, rewriting history, creating remote repositories, changing visibility. Explain the effect in one or two sentences, then wait for a yes. Prefer giving the user the exact command to run for remote deletions rather than running them yourself.
4. **Preserve behavior.** Cleanup must not change what the product does. Establish a baseline first (build, tests, lint) and re-run it after.
5. **Do not leave debris of your own.** The cleanup report goes in the chat, not into the repo. Do not add notes files, TODO files, or "cleaned by" markers.
6. **Say what you did not verify.** A pattern scan is evidence, not proof. Report limits plainly.

## Workflow

Run the phases in order. Secrets come first because what you find decides whether the repository needs to be recreated, and any cleanup you do afterwards should land in the fresh history, not the compromised one.

### Phase 0: Orient

- Identify the stack, package manager, framework, test and build commands, and where the repo is hosted (GitHub, GitLab, other).
- Check `git status`. If there are uncommitted changes, ask the user to commit or stash them so your changes are isolated. Work on a new branch (for example `cleanup/final-pass`) unless the repo has no commits yet.
- Run the baseline: install, build, lint, tests. Record what passes and fails now so you can tell your effect from pre-existing problems.
- Look for existing guardrails (pre-commit hooks, secret scanning in CI, `.gitignore`, `.env.example`) so you extend rather than duplicate them.
- Note tooling files that look like clutter but may be load-bearing: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/`, `.husky/`, `.editorconfig`. Do not remove these without asking.

### Phase 1: Secret audit (read-only)

Run the bundled scanner from this skill's directory against the project root:

```bash
python3 <skill-path>/scripts/scan_secrets.py <project-root>
```

It scans the working tree and every commit on every branch and tag, reports tracked sensitive files (`.env`, keys, service account files), and distinguishes secrets still present in current files from ones that exist only in history. Exit code 1 means findings.

Then supplement it, because regex scanning misses things. Read `references/secret-detection-patterns.md` for the tool options (gitleaks, trufflehog), the false-positive guide, and what is public by design (publishable keys, Firebase web config, anon keys). Use judgment: a finding is a secret if possession of the value grants access to something the owner would not want strangers to use.

Classify each finding:

- **A. In current files only**: fix in Phase 2. Not yet in history if never committed.
- **B. In history** (committed at any point, on any branch, even if later deleted): needs rotation and a clean history. Go to Phase 4 after cleanup.
- **C. Public by design or false positive**: note and leave, with a one-line reason.

Tell the user the headline result before continuing: how many secrets, which types, whether any are in history. Keep it short and calm; the point is to give them a plan, not alarm.

### Phase 2: Fix secrets in the code, and clean the noise

**Secrets**: replace each hardcoded value with a read from the environment, create or update `.env.example` (names and safe placeholders only), make sure `.gitignore` excludes every real env file, add startup validation so a missing variable fails loudly, and make sure no secret reaches client-side bundles. Details and per-framework rules are in `references/env-and-config.md`.

**Noise**: apply the catalog in `references/cleanup-catalog.md`, in three tiers:

- Tier A, apply directly: comments that restate the code, narration comments, commented-out code, banner comments, stray debug output, emoji decoration in code and logs.
- Tier B, list first, apply after a quick confirmation (or immediately when plainly generated junk): scratch and duplicate files, stale or invented docs, README badge walls, unused dependencies and dead modules, UI pills and marketing claims the product cannot support, placeholder and lorem ipsum text.
- Tier C, leave unless asked: license headers, comments explaining why, public API docs, ticket-linked TODOs, tooling and CI configuration, lockfiles, migrations.

Make small commits grouped by purpose (secrets to env; comment cleanup; file removal; docs) with plain messages. Reviewers can then revert one category without losing the rest.

### Phase 3: Verify

- Re-run the baseline commands. Results must match or improve on Phase 0.
- Re-run the scanner. Working-tree findings should be zero apart from classified false positives. History findings will remain until Phase 4.
- Skim `git diff --stat` for surprises, such as large deletions you did not intend.
- If the app can boot locally, boot it with only `.env.example` copied to a real env file and filled with dummy values, to confirm validation messages are clear and nothing depends on a hardcoded fallback.

### Phase 4: If secrets were ever committed

This phase applies only to class B findings. Read `references/history-remediation.md` and follow it. In brief:

1. **Rotate first.** A secret that reached a commit is compromised no matter what happens to the repository afterwards. Give the user a per-secret rotation checklist, ordered by blast radius (database, cloud keys, payment keys, signing secrets, then the rest).
2. **Then recreate the repository clean.** Ask the user to delete the remote repository and create a new one, and prepare the clean local copy with a fresh history that includes your cleanup. Rewriting history in place is the fallback, with caveats the reference explains (pull request refs, forks, and caches survive on hosting platforms).
3. Do not delete the remote repo or force-push yourself. Show the steps, confirm the user has rotated, and let them perform the deletion. Offer to run the push to the new empty repo once they confirm it exists.

If no secrets were ever committed, say so and skip this phase.

### Phase 5: Private secrets repository

The user wants one place to keep the application's environment values and other secrets for future reference, separate from the application repo and never public. Set this up following `references/secrets-repo-setup.md`:

- A new private repository named like `<app>-secrets`, verified private after creation.
- Encrypted by default (SOPS with age) so that a mistake in visibility or access does not expose plaintext. Plaintext only if the user explicitly insists, with one clear warning about the risk.
- An index file listing every secret by name, purpose, provider, environment, owner, and last rotation date, without values.
- Instructions for pulling values into a local `.env`, and for adding new ones later.

Ask before creating the remote repository. If the session cannot reach the user's GitHub account or the secret values live only on the user's machine, give them the exact commands to run locally instead of moving values through this session.

### Phase 6: Guardrails and report

Add protections so the problem does not return, with the user's agreement: a pre-commit secret scan (gitleaks or the bundled script), the same scan in CI, and GitHub push protection or secret scanning where the plan supports it. Keep them light so developers do not bypass them.

Finish with a short report in chat:

- Secrets: what was found (masked), what was fixed in code, what needs rotation, current status of history.
- Cleanup: counts and categories of what was removed, and what was deliberately kept and why.
- Verification: which commands were run and their results, and what could not be verified.
- Decisions waiting on the user: Tier B items they deferred, rotations outstanding, the repo deletion and recreation, the secrets repo.

## Judgment calls that come up often

- **A secret that is "only a test key" or "only in a private repo".** Still treat as exposed if it was committed: private repos get shared, forked, and made public later. Test-mode keys are lower risk, and the user can decide to accept that, but say so explicitly.
- **A secret that was committed and removed within minutes.** History keeps it. Same handling.
- **A tool config file that looks like AI residue** (`CLAUDE.md`, `.cursorrules`): ask. Some people maintain these on purpose, and removing them changes how their tools behave. Offer to remove if the user wants a "no AI traces" repository.
- **Comments in generated code that do carry useful reasoning.** Keep the why, drop the narration. When unsure whether a comment adds information, keep it and move on; a few extra comments cost less than lost context.
- **Docs that are accurate but verbose.** Tighten rather than delete. The README should let a newcomer run the project, list required environment variable names, and explain what the product is, all verified against the code.
- **No git repository yet.** Run the file-level scan and cleanup, add `.gitignore` and `.env.example` before the first commit, and the history question disappears.

## Reference index

- `references/secret-detection-patterns.md`: patterns, tools (gitleaks, trufflehog), false positives, public-by-design values.
- `references/env-and-config.md`: env file layout, `.gitignore`, `.env.example`, validation snippets, public vs server variables per framework, Docker and CI.
- `references/cleanup-catalog.md`: what counts as noise, what to keep, detection commands, tiering, and how to verify removals.
- `references/history-remediation.md`: rotation checklist, delete-and-recreate procedure, in-place rewrite fallback, what survives on hosting platforms.
- `references/secrets-repo-setup.md`: private secrets repo layout, SOPS and age setup, index template, access rules, plaintext fallback.
- `scripts/scan_secrets.py`: dependency-free scanner for the working tree and full git history with masked output.
