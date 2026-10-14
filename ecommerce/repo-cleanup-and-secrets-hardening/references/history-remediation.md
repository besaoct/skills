# When a secret was committed: rotate, then recreate the repository

## Contents
1. The core fact
2. Step 1: Inventory what was exposed
3. Step 2: Rotate
4. Step 3: Check for misuse
5. Step 4: Recreate the repository clean (preferred)
6. Step 5: In-place history rewrite (fallback)
7. What survives on hosting platforms
8. Other places the secret may live
9. What to tell the user

## 1. The core fact

Once a secret reaches a commit that has left the machine, assume someone has copied it. Bots scan public repositories within minutes, and private repositories are shared, forked, cloned, and made public later. Removing the secret from the repository does not un-leak it. Only rotation does. Cleaning the history matters too, because it stops the old value from being found later, but it is the second line of defense, not the first.

So the order is always: rotate, then clean.

## 2. Step 1: Inventory what was exposed

From the scanner output, build a table for the user (masked, no values):

| Secret type | Where (file, commit) | Still in current files? | Provider | Blast radius |
|---|---|---|---|---|

Order by blast radius: production database credentials, cloud provider keys, payment secret keys, signing keys (JWT, session, webhook), admin tokens, third-party API keys, then low-risk items. Include secrets that were committed and then deleted; history still has them.

## 3. Step 2: Rotate

Give the user a checklist tailored to the secrets found. General guidance by type:

| Secret | Rotation steps |
|---|---|
| Database password or connection string | Create a new user or password, update the application's secret store, restart services, drop the old credential. Check that no other service used the old one. |
| JWT or session signing secret | Generate a new random value (32+ bytes), deploy. This invalidates existing sessions and tokens; plan for users to sign in again. If supporting overlap, accept both keys briefly. |
| AWS access keys | Create a new key, deploy it, deactivate then delete the old key. Review CloudTrail for unfamiliar activity. Prefer IAM roles or OIDC instead of long-lived keys. |
| GCP service account key | Create a new key, switch workloads, delete the old key. Check audit logs. |
| Stripe and other payment keys | Roll the secret key in the dashboard (set an expiry on the old one if offered), roll webhook signing secrets, check recent events for anomalies. |
| GitHub, GitLab, npm, registry tokens | Revoke in account settings, create a new token with minimal scopes. |
| OAuth client secrets | Regenerate in the provider console, update the app, revoke old refresh tokens if the provider supports it. |
| Email, SMS, AI, analytics API keys | Regenerate in the provider console, check usage for spikes, set spend limits. |
| Private keys and certificates | Generate a new key pair, replace the public key or certificate where it is installed, revoke the old certificate. |
| SSH keys | Remove the old public key from every server and service, add the new one. |
| Webhook secrets | Regenerate on both sides at the same time. |
| Internal shared passwords | Change, and tell the people who use them. |

Principles:

- New values must never be committed. They go into the platform secret store, the local `.env`, and the private secrets repo (see `secrets-repo-setup.md`).
- Rotate in an order that avoids downtime: create new, deploy, verify, revoke old.
- If a secret cannot be rotated quickly (a third-party system with manual steps), tell the user plainly that the exposure window stays open until it is, and suggest interim limits (IP allowlists, spend caps).
- Do not rotate on the user's behalf unless they ask and the tools are available. Provide the exact steps.

## 4. Step 3: Check for misuse

Suggest the user look at provider audit and usage logs for the exposure window: unfamiliar logins, new users or keys, unexpected spend, data exports, new webhooks, changes to permissions, and requests from unfamiliar IP ranges. If there is evidence of misuse, treat it as an incident and follow the organization's response process, including notifying affected parties where required.

## 5. Step 4: Recreate the repository clean (preferred)

Why this is the preferred route: deleting the remote repository removes all refs, pull request refs, and cached views the platform holds for that repository, and a fresh single history guarantees the old objects are not reachable from it. Rewriting history in place leaves loose ends (section 7).

Prerequisites, to confirm with the user before proceeding:

- Secrets have been rotated (or the user accepts the open exposure window knowingly).
- All work is saved: nothing important exists only on the remote (unpushed branches elsewhere, issues, pull requests, wiki, releases, discussions, project boards). If they want to keep issues or releases, export them first (for GitHub: `gh issue list --json ...`, the repository export tools, or the API). Stars, watchers, and forks do not carry over.
- Team members know to discard their old clones and re-clone, so they do not push the old history to the new repository.

Procedure:

1. **Finish the cleanup on a branch** (Phases 2 and 3) so the new history starts clean.
2. **Prepare a clean copy of the working tree without `.git`:**
   ```bash
   mkdir ../<project>-clean
   rsync -a --include '.env.example' --exclude '.git' --exclude 'node_modules' \
         --exclude '.env' --exclude '.env.*' ./ ../<project>-clean/
   ```
   Make sure `.env.example` is included and real env files are not. Check that no ignored local files with secrets (keys, service account files) were copied.
3. **Scan the copy**: `python3 <skill-path>/scripts/scan_secrets.py ../<project>-clean --no-history` must report nothing (aside from classified false positives).
4. **Ask the user to delete the old remote repository** themselves. On GitHub: repository, Settings, scroll to Danger Zone, Delete this repository. Do not run the deletion yourself; it is irreversible and they should be the one to decide.
5. **Create the new empty repository** (same name is fine after deletion), private unless the user intends it to be public. Do not initialize it with a README, so the first push is the clean history.
6. **Initialize and push:**
   ```bash
   cd ../<project>-clean
   git init -b main
   git add .
   git status            # review the file list one more time
   git commit -m "Initial commit"
   git remote add origin <new-repo-url>
   git push -u origin main
   ```
   If the user wants to preserve meaningful history, a squash is the safe middle path: one commit per milestone made by hand, never a replay of old commits (which would reintroduce the secrets).
7. **Run the scanner on the new clone** (with history) to confirm a clean result, and enable push protection and secret scanning on the new repository.
8. **Reconnect integrations**: CI secrets, deploy hooks, webhooks, branch protection, and collaborators. Re-add secrets from the secrets repo or the platform store using the rotated values.
9. **Retire old clones**: ask everyone to delete their local copies of the old repository.

If the repository has forks, the forks keep the old history. Ask the user to have fork owners delete them (or, for GitHub, contact support to request removal of cached sensitive data and to address the fork network). Rotation already makes the leaked values useless.

## 6. Step 5: In-place history rewrite (fallback)

Use when the user cannot delete the repository (a large project with stars and forks, an organization policy, or links that must stay valid). Be upfront that it is weaker than recreation on hosted platforms.

Tool: `git filter-repo` (preferred over `filter-branch` and BFG for current Git versions).

```bash
# work on a fresh mirror clone, never on the only copy
git clone --mirror <repo-url> repo-mirror.git
cd repo-mirror.git

# remove files that should never have been committed
git filter-repo --invert-paths --path .env --path config/secrets.json

# replace secret strings across all history (file lists literal==>REMOVED lines; keep this file out of the repo)
git filter-repo --replace-text ../replacements.txt

# verify, then force-push all refs
git push --force --mirror origin
```

Caveats to explain:

- Every collaborator must re-clone or hard reset; old clones can re-introduce the secrets.
- Hosting platforms keep pull request refs (`refs/pull/*`) and cached commits reachable by their SHA after a force push. Open pull requests, forks, and cached views may still serve the old content until the platform's cleanup runs or support purges it.
- Tags and releases containing the secret must be rewritten or deleted too.
- Protected branches need protection temporarily lifted, which is another reason to involve the user.
- The `replacements.txt` file itself contains the secrets, so keep it outside the repo and delete it afterwards.

After the rewrite, run the scanner against a fresh clone, rotate anyway (already done), and ask the platform to garbage collect or remove cached views if needed.

## 7. What survives on hosting platforms

Even after history is rewritten, these may still hold the old data:

- Forks and their clones.
- Pull request and merge request refs and diffs.
- Cached commit pages reachable by SHA until garbage collection.
- Clones on teammates' laptops and CI runners, and CI caches and logs.
- Third-party mirrors, code search indexes, archive services, and scraping bots.
- Release assets, packages, and container images built from the contaminated state.

This is why rotation is the real fix and why recreation is preferred.

## 8. Other places the secret may live

Check and clean, or rotate away from:

- Build logs and deployment logs on hosting platforms (Vercel, Netlify, Render, GitHub Actions).
- Container images in registries built with `ENV`, `ARG`, or copied `.env` files. Delete those images and rebuild.
- Published packages (npm, PyPI, crates). Deprecate or unpublish the version and publish a clean one after rotating.
- Error trackers and analytics that captured request bodies or environment dumps.
- Chat messages, tickets, and documentation where the value was pasted.
- Local shell history and editor backups on shared machines.

## 9. What to tell the user

Keep the message plain and actionable:

1. What was found, in masked form, and why it matters (a short sentence, no drama).
2. The order: rotate first, then recreate the repository.
3. A checklist they can follow, with provider-specific steps for the secrets found.
4. That you will prepare the clean copy and cleanup, and that the deletion of the old remote is theirs to do, with the exact path in the platform's settings.
5. What happens to issues, pull requests, stars, and forks.
6. Offer to continue with the secrets repository and guardrails once the new repository exists.
