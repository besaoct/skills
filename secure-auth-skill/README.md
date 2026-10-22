# Secure Auth Codex Skill

## Install in a repository

Copy the `secure-auth` skill directory into your repository at:

```text
.agents/skills/secure-auth/
```

The installed directory should contain `SKILL.md` and the `references/` directory.

## Use

Ask Codex to use the `secure-auth` skill to plan, implement, review, or harden authentication in the current project. The skill first inspects the project, asks about desired features, presents recommended presets and custom options, confirms architecture decisions where needed, and tracks requirements through implementation and tests.

## Important

The skill is an instruction package, not a runtime authentication library. It does not itself implement or certify authentication. Codex must adapt the plan to the repository, run available tests, and report unverified requirements and residual risks honestly.
