#!/usr/bin/env python3
"""Scan a project for hardcoded secrets in the working tree and in git history.

Dependency free (Python 3.8+, git on PATH for history scanning).
Secret values are never printed in full: only a masked preview and the length.

Usage:
    python3 scan_secrets.py [PATH] [--no-history] [--json] [--max-history-findings N]

Exit codes:
    0  nothing found
    1  findings reported
    2  usage or environment error
"""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".nuxt", ".svelte-kit",
    ".venv", "venv", "__pycache__", "vendor", "coverage", ".turbo", ".cache",
    "target", ".gradle", ".idea", ".vscode", "Pods",
}
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Cargo.lock", "composer.lock", "Gemfile.lock", "go.sum", "uv.lock",
}
MAX_FILE_BYTES = 1_500_000
MAX_LINE_CHARS = 5000

# (name, severity, compiled regex). The secret is the last capture group if
# the regex has any group, otherwise the whole match.
PATTERNS = [
    ("aws-access-key-id", "high", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-secret-access-key", "high", re.compile(
        r"(?i)aws.{0,25}?(?:secret|sk).{0,25}?['\"=:\s]+([A-Za-z0-9/+=]{40})\b")),
    ("github-token", "high", re.compile(
        r"\b(?:(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("stripe-live-key", "high", re.compile(r"\b(?:sk|rk)_live_[0-9a-zA-Z]{16,}\b")),
    ("slack-token", "high", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("anthropic-key", "high", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-key", "high", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("sendgrid-key", "high", re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b")),
    ("twilio-api-key", "high", re.compile(r"\bSK[0-9a-fA-F]{32}\b")),
    ("npm-token", "high", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("private-key-block", "high", re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----")),
    ("database-url-with-password", "high", re.compile(
        r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|rediss|amqps?)://"
        r"[^\s:/@'\"]+:([^\s@'\"]{3,})@[^\s'\"]+")),
    ("google-api-key", "medium", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("jwt", "medium", re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]

GENERIC = re.compile(
    r"(?i)\b([A-Za-z0-9_.\-]*(?:secret|passw(?:or)?d|pwd|token|api[_-]?key|apikey|"
    r"private[_-]?key|access[_-]?key|auth[_-]?key|client[_-]?secret|credential)"
    r"[A-Za-z0-9_.\-]*)\s*[:=]\s*[\"']?([A-Za-z0-9_\-+/=.@!#$%^&*~]{8,})[\"']?")

ENV_READ_HINTS = ("process.env", "os.environ", "getenv", "import.meta.env",
                  "env(", "config(", "System.getenv", "ENV[", "os.Getenv")
PLACEHOLDER_HINTS = ("example", "placeholder", "changeme", "change_me", "your_",
                     "your-", "<", ">", "${", "{{", "redacted", "xxxx", "****",
                     "process.env", "dummy", "replace_me", "replace_with",
                     "replace-with", "todo")

SENSITIVE_FILE_GLOBS = [
    "*.pem", "*.key", "*.p12", "*.pfx", "*.keystore", "*.jks", "id_rsa", "id_ed25519",
    "credentials.json", "serviceAccount*.json", "*service-account*.json",
    ".npmrc", ".pypirc", ".netrc", "terraform.tfstate", "terraform.tfstate.backup",
    "*.tfvars", "secrets.yml", "secrets.yaml", "secrets.json",
]
ENV_SAFE_SUFFIXES = (".example", ".sample", ".template", ".dist", ".defaults", ".schema")


def is_env_file(path):
    base = os.path.basename(path)
    if base == ".env" or base.startswith(".env."):
        return not base.endswith(ENV_SAFE_SUFFIXES)
    return base.endswith(".env")


def is_sensitive_file(path):
    base = os.path.basename(path)
    if is_env_file(path):
        return True
    return any(fnmatch.fnmatch(base, g) for g in SENSITIVE_FILE_GLOBS)


def mask(value):
    n = len(value)
    if n >= 12:
        return f"{value[:4]}...{value[-2:]} ({n} chars)"
    if n >= 6:
        return f"{value[:2]}... ({n} chars)"
    return f"*** ({n} chars)"


WEAK_PLACEHOLDER_VALUES = {
    "password", "passwd", "pass", "secret", "changeit", "admin", "root", "postgres",
    "mysql", "user", "username", "test", "testing", "123456", "12345678", "qwerty",
}


def looks_placeholder(value, line):
    low = (value + " " + line).lower()
    if any(h in low for h in PLACEHOLDER_HINTS):
        return True
    if value.lower() in WEAK_PLACEHOLDER_VALUES:
        return True
    return len(set(value)) <= 2


def scan_line(line, path):
    """Return list of (pattern_name, severity, value)."""
    if len(line) > MAX_LINE_CHARS:
        line = line[:MAX_LINE_CHARS]
    found = []
    seen = set()
    for name, sev, rx in PATTERNS:
        for m in rx.finditer(line):
            value = m.group(m.lastindex) if m.lastindex else m.group(0)
            if name != "private-key-block" and looks_placeholder(value, ""):
                continue
            if (name, value) not in seen:
                seen.add((name, value))
                found.append((name, sev, value))
    if not any(h in line for h in ENV_READ_HINTS):
        for m in GENERIC.finditer(line):
            key, value = m.group(1), m.group(2)
            if looks_placeholder(value, line):
                continue
            envlike = is_env_file(path)
            has_complexity = any(c.isdigit() for c in value) or bool(re.search(r"[^A-Za-z]", value))
            if not (envlike or has_complexity):
                continue
            if value.lower() in ("undefined", "null", "string", "required", "optional"):
                continue
            if re.fullmatch(r"[A-Za-z_]+(?:\.[A-Za-z_]+)+", value):
                continue  # dotted identifier such as z.string or config.token: code, not a secret
            if (("generic-secret-assignment"), value) not in seen:
                seen.add(("generic-secret-assignment", value))
                found.append(("generic-secret-assignment", "medium", value))
    return found


def is_binary(path):
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(8192)
    except OSError:
        return True


def run_git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True)


def list_working_files(root):
    if run_git(root, "rev-parse", "--is-inside-work-tree").returncode == 0:
        out = run_git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        files = [f for f in out.stdout.decode("utf-8", "replace").split("\0") if f]
        return files, True
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            files.append(os.path.relpath(os.path.join(dp, fn), root))
    return files, False


def in_skipped_dir(rel):
    return any(part in SKIP_DIRS for part in rel.split(os.sep)[:-1])


def scan_working_tree(root, is_git):
    findings, sensitive_files, ignored_env = [], [], []
    files, _ = list_working_files(root)
    tracked = set()
    if is_git:
        out = run_git(root, "ls-files", "-z")
        tracked = {f for f in out.stdout.decode("utf-8", "replace").split("\0") if f}
    for rel in files:
        if in_skipped_dir(rel) or os.path.basename(rel) in SKIP_FILES:
            continue
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        if is_sensitive_file(rel) and (not is_git or rel in tracked):
            sensitive_files.append(rel)
        try:
            if os.path.getsize(full) > MAX_FILE_BYTES or is_binary(full):
                continue
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    for name, sev, value in scan_line(line.rstrip("\n"), rel):
                        findings.append({"pattern": name, "severity": sev, "file": rel,
                                         "line": lineno, "preview": mask(value),
                                         "fingerprint": hashlib.sha1(value.encode()).hexdigest()[:12]})
        except OSError:
            continue
    if is_git:
        out = run_git(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard")
        for rel in out.stdout.decode("utf-8", "replace").split("\0"):
            if rel and is_env_file(rel) and not in_skipped_dir(rel):
                ignored_env.append(rel)
    return findings, sensitive_files, ignored_env


def scan_history(root, cap):
    """Scan added lines in every commit reachable from any ref."""
    proc = subprocess.Popen(
        ["git", "-C", root, "log", "--all", "--no-color", "-p", "-U0", "--no-ext-diff",
         "--format=@@@COMMIT %H"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    commit, path = None, None
    by_fp = {}
    sensitive = {}
    total = 0
    for raw in proc.stdout:
        line = raw.decode("utf-8", "replace").rstrip("\n")
        if line.startswith("@@@COMMIT "):
            commit = line.split()[1][:10]
            path = None
            continue
        if line.startswith("+++ "):
            p = line[4:]
            path = None if p == "/dev/null" else (p[2:] if p.startswith("b/") else p)
            if path and is_sensitive_file(path):
                sensitive.setdefault(path, commit)
            continue
        if not line.startswith("+") or line.startswith("+++") or path is None:
            continue
        if os.path.basename(path) in SKIP_FILES or in_skipped_dir(path):
            continue
        for name, sev, value in scan_line(line[1:], path):
            fp = hashlib.sha1(value.encode()).hexdigest()[:12]
            key = (name, fp)
            if key not in by_fp:
                if total >= cap:
                    continue
                total += 1
                by_fp[key] = {"pattern": name, "severity": sev, "file": path,
                              "commit": commit, "preview": mask(value), "fingerprint": fp}
            else:
                by_fp[key]["commit"] = commit
                by_fp[key]["file"] = path
    proc.wait()
    return list(by_fp.values()), sensitive


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--no-history", action="store_true", help="skip git history scan")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max-history-findings", type=int, default=200)
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    is_git = run_git(root, "rev-parse", "--is-inside-work-tree").returncode == 0
    wt_findings, tracked_sensitive, ignored_env = scan_working_tree(root, is_git)

    hist_findings, hist_sensitive = [], {}
    if is_git and not args.no_history:
        hist_findings, hist_sensitive = scan_history(root, args.max_history_findings)

    head_fps = {f["fingerprint"] for f in wt_findings}
    for h in hist_findings:
        h["still_in_working_tree"] = h["fingerprint"] in head_fps
    hist_only_sensitive = {p: c for p, c in hist_sensitive.items() if p not in tracked_sensitive}

    result = {
        "path": root, "is_git_repo": is_git,
        "working_tree_findings": wt_findings,
        "tracked_sensitive_files": tracked_sensitive,
        "ignored_env_files_present": ignored_env,
        "history_findings": hist_findings,
        "sensitive_files_in_history": hist_sensitive,
        "history_scanned": bool(is_git and not args.no_history),
    }
    has_findings = bool(wt_findings or tracked_sensitive or hist_findings or hist_sensitive)

    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if has_findings else 0

    print(f"Scanned: {root}")
    if not is_git:
        print("Not a git repository: history scan skipped.")
    print(f"\nWorking tree findings: {len(wt_findings)}")
    for f in sorted(wt_findings, key=lambda x: (x["severity"] != "high", x["file"], x["line"])):
        print(f"  [{f['severity'].upper():6}] {f['pattern']:28} {f['file']}:{f['line']}  {f['preview']}")
    print(f"\nSensitive files tracked by git: {len(tracked_sensitive)}")
    for p in tracked_sensitive:
        print(f"  {p}")
    if ignored_env:
        print(f"\nIgnored env files present locally (expected, not in git): {len(ignored_env)}")
        for p in ignored_env:
            print(f"  {p}")
    if result["history_scanned"]:
        print(f"\nHistory findings: {len(hist_findings)}")
        for h in sorted(hist_findings, key=lambda x: (x["severity"] != "high", x["file"])):
            where = "also in current files" if h["still_in_working_tree"] else "removed from current files, still in history"
            print(f"  [{h['severity'].upper():6}] {h['pattern']:28} {h['file']}  commit {h['commit']}  {h['preview']}  ({where})")
        print(f"\nSensitive file names that were ever committed: {len(hist_sensitive)}")
        for p, c in hist_sensitive.items():
            note = "" if p not in hist_only_sensitive else "  (no longer tracked, still in history)"
            print(f"  {p}  commit {c}{note}")
    print()
    if has_findings:
        print("RESULT: findings present. Treat every listed secret as exposed until proven otherwise.")
        print("Values are masked above. Review each item; false positives are possible.")
        return 1
    print("RESULT: no findings. This is a pattern scan, not a guarantee.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
