# Git History Scanning Reference

Techniques for detecting secrets that were committed to git history, including secrets that have been removed from the current working tree but remain accessible in the repository's commit history.

---

## Core Scanning Techniques

### Full Diff Search with String Matching

Search all branches for commits that added or removed a specific string:

```bash
git log -p --all -S 'AKIA' --source --format='%H %ai %an %s'
```

- `-p` shows the patch (diff) for each commit
- `--all` searches across all branches, including remote-tracking branches
- `-S 'PATTERN'` finds commits where the number of occurrences of the pattern changed (added or removed)
- `--source` shows which ref led to each commit being found
- Useful for provider-specific prefixes like `AKIA`, `ghp_`, `sk_live_`, `xoxb-`

### Regex Search in History

Search all branches using regex patterns in diffs:

```bash
git log -p --all -G 'AKIA[0-9A-Z]{16}' --source --format='%H %ai %an %s'
```

- `-G 'REGEX'` finds commits where the diff matches the regex (even if count didn't change)
- More flexible than `-S` for complex patterns
- Can be combined with `--diff-filter` to target only additions (`A`) or modifications (`M`)

### Searching Specific File Types

Limit history search to files commonly containing secrets:

```bash
git log -p --all -- '*.env' '*.env.*' '*.pem' '*.key' '*.yml' '*.yaml' '*.json' '*.toml' '*.ini' '*.cfg' '*.conf' '*.properties' '*.xml' '*.tfvars' '*.auto.tfvars'
```

- The `--` separator tells git the remaining arguments are file paths/globs
- Reduces scan time and noise by focusing on high-value targets
- Combine with `-S` or `-G` for targeted searches

### Deleted File Recovery

Find files that were deleted from the repository:

```bash
# List all deleted files across history
git log --diff-filter=D --name-only --format='%H %ai' -- '*.env' '*.pem' '*.key' '*.json'

# Recover a specific deleted file from the commit before deletion
git show COMMIT_HASH^:path/to/deleted/file

# Find the commit that deleted a specific file
git log --diff-filter=D --summary -- path/to/file
```

- `--diff-filter=D` shows only commits that deleted files
- `COMMIT_HASH^` references the parent of the deletion commit (where the file still existed)
- Common targets: `.env` files, key files, credential configs committed before `.gitignore`

### Force-Push Detection via Reflog

Check for orphaned commits from force pushes:

```bash
# View reflog for recent force pushes (local repo only)
git reflog show --all --format='%H %gd %gs %ai'

# Find unreachable commits that might contain secrets
git fsck --unreachable --no-reflogs | grep commit

# Show content of an unreachable commit
git show UNREACHABLE_COMMIT_HASH
```

- Reflog is only available on the local machine where the push originated
- Unreachable commits are eventually garbage collected (default: 90 days)
- Force pushes to shared branches are a common source of leaked secrets

### Branch Scanning

Iterate over all branches to ensure full coverage:

```bash
# List all local and remote branches
git branch -a --format='%(refname:short)'

# Search a specific branch for secrets
git log -p BRANCH_NAME -S 'secret_pattern'

# Compare branches to find secrets unique to a branch
git log -p main..feature-branch -G 'AKIA[0-9A-Z]{16}'
```

- Remote branches (`remotes/origin/*`) may contain secrets not in local branches
- Feature branches that were merged and deleted may still have history accessible via merge commits
- Stale branches are a common source of forgotten credentials

---

## Common Patterns Where Secrets Appear in History

### Initial Commits

The first few commits of a repository often contain secrets because `.gitignore` was not yet configured:

```bash
# Check the first N commits
git log --reverse --format='%H %s' | head -20

# Inspect early commits for sensitive files
git show FIRST_COMMIT_HASH --stat
git show FIRST_COMMIT_HASH -- .env database.yml config/secrets.yml
```

### Debug Commits

Developers sometimes commit real credentials during debugging:

```bash
# Search for common debug commit messages
git log --all --grep='debug' --grep='test.*cred' --grep='temp.*key' --grep='quick fix' -i --format='%H %ai %s'
```

- Look for messages containing: "debug", "testing", "temp", "quick fix", "WIP", "hack"
- These commits may contain hardcoded credentials used for local testing

### Configuration Migration Commits

When teams move from hardcoded secrets to environment variables, the migration commit contains the old values in the diff:

```bash
# Find commits that modified configuration files
git log -p -- 'config/*' 'settings/*' '*.env*' '*.yml' --format='%H %ai %s'

# Look for patterns where hardcoded values were replaced with env var references
git log -p --all -G '(process\.env|os\.environ|ENV\[|getenv)' -- '*.py' '*.js' '*.rb'
```

### .env Files Before .gitignore

A very common scenario: `.env` was committed, then added to `.gitignore`:

```bash
# Check if .env was ever tracked
git log --all --follow -- '.env'
git log --all --follow -- '.env.local'
git log --all --follow -- '.env.production'

# Check when .gitignore was modified to include .env
git log -p -- '.gitignore' | grep -A2 -B2 '\.env'
```

### Merge Commits

Merge commits can introduce secrets from feature branches:

```bash
# List merge commits
git log --merges --format='%H %ai %s' --all

# Inspect the diff introduced by a merge
git diff MERGE_COMMIT^1...MERGE_COMMIT
```

### Reverted Commits

Secrets added and then reverted still exist in history:

```bash
# Find revert commits
git log --all --grep='revert' -i --format='%H %ai %s'

# Check what was reverted
git show REVERT_COMMIT_HASH
```

---

## Remediation for Historical Secrets

### Mandatory: Credential Rotation

**Removing a secret from git history does NOT make it safe.** Anyone who cloned or forked the repository before cleanup has a copy. The secret MUST be rotated with the provider.

Rotation checklist:
1. Generate a new credential with the provider (AWS, GitHub, Stripe, etc.)
2. Update all systems using the old credential
3. Revoke/delete the old credential
4. Verify services still function with the new credential
5. Monitor for unauthorized usage of the old credential

### History Rewriting with git filter-repo

The recommended tool for rewriting git history (replaces `git filter-branch`):

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove a specific file from all history
git filter-repo --path .env --invert-paths

# Replace specific strings across all history
git filter-repo --replace-text expressions.txt
# expressions.txt format: literal:OLD_SECRET==>REDACTED
# or regex: regex:AKIA[0-9A-Z]{16}==>REDACTED_AWS_KEY

# Remove specific blobs by content
git filter-repo --strip-blobs-with-ids blob-ids.txt
```

### BFG Repo-Cleaner

Faster alternative for large repositories:

```bash
# Remove a file from history
java -jar bfg.jar --delete-files .env

# Replace text in all files across history
java -jar bfg.jar --replace-text passwords.txt
# passwords.txt format: one secret per line, optionally with ==>replacement

# Remove large files (often binary secrets like keystores)
java -jar bfg.jar --strip-blobs-bigger-than 1M
```

### Post-Cleanup Steps

After rewriting history:

```bash
# Force push all branches
git push --force --all origin
git push --force --tags origin

# Expire reflog and garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

Team coordination:
1. Notify all contributors before force push
2. All team members must re-clone or `git fetch --all && git reset --hard origin/BRANCH`
3. Forks must also be updated or recreated
4. GitHub/GitLab caches may retain old data temporarily -- contact support if needed

### Platform-Specific Secret Scanning

#### GitHub
- Secret scanning alerts: automatic detection and alerts for known secret formats
- Push protection: blocks pushes containing detected secrets
- Enable in repository Settings > Code security and analysis

#### GitLab
- Secret detection CI/CD component: add to `.gitlab-ci.yml` pipeline
- Pre-receive secret detection (Ultimate tier)
- Enable in Settings > Security & Compliance

---

## Prevention: Pre-Commit Hooks and CI Integration

### git-secrets (AWS-focused)

```bash
# Install
brew install git-secrets  # macOS
git secrets --install      # per-repo setup
git secrets --register-aws # register AWS patterns

# Add custom patterns
git secrets --add 'PRIVATE_KEY'
git secrets --add --allowed 'PRIVATE_KEY_EXAMPLE'
```

### detect-secrets (Yelp)

```bash
# Install
pip install detect-secrets

# Generate baseline (existing secrets to ignore)
detect-secrets scan --all-files > .secrets.baseline

# Pre-commit hook integration
# .pre-commit-config.yaml:
# - repo: https://github.com/Yelp/detect-secrets
#   rev: v1.4.0
#   hooks:
#     - id: detect-secrets
#       args: ['--baseline', '.secrets.baseline']
```

### gitleaks

```bash
# Install
brew install gitleaks  # macOS

# Scan current state
gitleaks detect --source . --verbose

# Scan git history
gitleaks detect --source . --verbose --log-opts="--all"

# CI integration (GitHub Actions)
# - uses: gitleaks/gitleaks-action@v2
#   env:
#     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### truffleHog

```bash
# Install
pip install trufflehog

# Scan local repo history
trufflehog git file://. --since-commit HEAD~100

# Scan with entropy analysis
trufflehog git file://. --entropy

# Scan specific branch
trufflehog git file://. --branch feature-branch
```

### husky + lint-staged (Node.js projects)

```bash
# Install
npm install -D husky lint-staged

# Setup husky
npx husky install

# Add pre-commit hook
npx husky add .husky/pre-commit "npx lint-staged"

# package.json lint-staged config:
# "lint-staged": {
#   "*": "detect-secrets-hook --baseline .secrets.baseline"
# }
```
