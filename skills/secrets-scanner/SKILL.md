---
trigger: When user asks to scan for secrets, find hardcoded credentials, detect API keys, check for exposed tokens, or audit for leaked passwords
---

# Secrets Scanner

Detect hardcoded secrets in source code, configuration files, and git history. This skill is language-agnostic and works on any text file regardless of programming language.

## Workflow

### Step 1: File Discovery

Identify files likely to contain secrets across the entire repository.

**Include:**
- Source code files (all languages: `.py`, `.js`, `.ts`, `.go`, `.java`, `.rb`, `.php`, `.rs`, `.cs`, `.c`, `.cpp`, `.swift`, `.kt`, etc.)
- Configuration files (`.yml`, `.yaml`, `.json`, `.toml`, `.ini`, `.cfg`, `.conf`, `.xml`, `.properties`)
- Environment files (`.env`, `.env.*`, `.envrc`)
- CI/CD configs (`.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/*`, `.travis.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`)
- Infrastructure files (`Dockerfile`, `docker-compose*.yml`, `Vagrantfile`, `terraform/*.tf`, `*.tfvars`)
- Shell scripts (`.sh`, `.bash`, `.zsh`, `.fish`, `.bat`, `.ps1`, `.cmd`)
- Build files (`Makefile`, `Rakefile`, `Gruntfile`, `gulpfile`, `webpack.config.*`, `package.json`)

**Exclude:**
- Binary files (images, compiled objects, archives)
- `node_modules/`, `vendor/`, `.venv/`, `venv/`, `__pycache__/`, `.git/`
- Test fixture data that is explicitly marked as fake
- Lock files (`package-lock.json`, `yarn.lock`, `Gemfile.lock`, `poetry.lock`, `Cargo.lock`)
- Minified/bundled files (`*.min.js`, `*.bundle.js`, `dist/`)

### Step 2: Pattern Matching

Use the Grep tool to search identified files for regex patterns. Use the Read tool to load patterns from the `secret_patterns.md` reference file.

1. **Provider-specific patterns** -- Match known secret formats:
   - AWS keys starting with `AKIA`
   - GitHub tokens starting with `ghp_`, `gho_`, `ghu_`, `ghs_`
   - Stripe keys starting with `sk_live_`, `pk_live_`
   - Slack tokens starting with `xoxb-`, `xoxp-`
   - Private key headers (`-----BEGIN RSA PRIVATE KEY-----`)
   - And all other patterns documented in `secret_patterns.md`

2. **Generic high-entropy strings** -- Detect secrets that don't match known provider patterns:
   - Long hex strings (32+ chars) in assignment context
   - Long base64 strings (40+ chars) in assignment context
   - Password and API key variable assignments with literal string values
   - Connection strings with embedded credentials

3. **Context-aware detection** -- Check surrounding code for secret-indicating variable names:
   - `password`, `passwd`, `pwd`, `secret`, `token`, `api_key`, `apikey`, `access_key`, `auth_token`, `credentials`, `private_key`
   - Case-insensitive matching across naming conventions (snake_case, camelCase, UPPER_CASE)

### Step 3: Git History Scanning

Search commit history for secrets that were added and later removed. Use the Read tool to load `git_history_scanning.md` for detailed techniques.

Use the Bash tool to execute these git commands:

1. **Diff search** -- `git log -p --all -S 'PATTERN'` and `git log -p --all -G 'REGEX'` to find secrets that appeared in any commit across all branches.
2. **Deleted file recovery** -- `git log --diff-filter=D --name-only` to find deleted files that may have contained secrets (e.g., `.env` files committed before `.gitignore` was set up).
3. **Sensitive file history** -- `git log -p -- '*.env' '*.pem' '*.key' '*.yml' '*.json'` to search history for changes to files commonly containing secrets.
4. **Reflog inspection** -- `git reflog` to check for force-pushed branches that may have contained secrets in now-orphaned commits.
5. **Scan depth** -- By default scan the last 200 commits. For thorough scans, search the full history.

### Step 4: False Positive Filtering

Reduce noise by excluding findings that are clearly not real secrets.

**Exclude:**
- Placeholder values: `xxx`, `TODO`, `CHANGEME`, `changeme`, `REPLACE_ME`, `your-key-here`, `INSERT_HERE`, `<your_token>`, `example`, `sample`
- Obviously fake values: `test123`, `password123`, `abc123`, `foobar`, `dummy`, `fake`, `mock`
- Documentation domains: `example.com`, `example.org`, `test.com`, `localhost`, `127.0.0.1`
- Template variables: `${VAR}`, `{{ var }}`, `%{var}`, `<%= var %>`, `ENV['...']`, `os.environ[...]`, `process.env.`
- Example/documentation files when values are clearly illustrative
- `.env.example`, `.env.sample`, `.env.template` files with placeholder values
- Test files where secrets are explicitly marked as test fixtures
- Empty string assignments (`password = ""`, `secret = ''`)
- Comment-only references explaining what a variable should contain

**Entropy check:**
- Calculate Shannon entropy of candidate strings
- Real secrets typically have entropy > 3.5 bits per character
- Constants, code identifiers, and English words typically have entropy < 3.0
- Use entropy as a secondary signal, not a sole determinant

### Step 5: Report

Generate a structured report of all findings.

**For each finding, include:**
- **Location**: `file:line` for current files, or `commit_hash (file:line)` for git history findings
- **Secret type**: The category of secret detected (e.g., "AWS Access Key", "GitHub PAT", "Database Connection String")
- **Provider**: The service provider if identifiable (e.g., AWS, GitHub, Stripe, Slack)
- **Masked value**: Show only first 4 and last 4 characters with masking (e.g., `AKIA****WXYZ`, `ghp_****ab3f`)
- **Risk level**:
  - **Critical**: Production keys with broad access (AWS root keys, admin tokens, private keys, database credentials for production)
  - **High**: Keys with scoped access (scoped API tokens, service-specific keys, OAuth secrets)
  - **Medium**: Internal tokens (internal service tokens, webhook URLs, CI/CD variables)
  - **Low**: Test/dev keys (test API keys, development-only credentials, sandbox tokens)
- **Remediation**:
  - Rotate the credential immediately with the provider
  - Store in a secrets vault (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
  - Add the file pattern to `.gitignore` if applicable
  - Use environment variables or secrets management instead of hardcoding
  - For git history: rewrite history with `git filter-repo` or BFG Repo-Cleaner, then force push
  - Set up pre-commit hooks to prevent future secret commits

**Report structure:**

1. **Executive summary**: Total findings count by risk level, most critical findings highlighted
2. **Current file findings**: Grouped by risk level (Critical first), then by file
3. **Git history findings**: Grouped by risk level, including commit hash and date
4. **Recommendations**: Prioritized list of remediation actions
5. **Prevention**: Suggestions for preventing future secret leaks (pre-commit hooks, CI scanning, `.gitignore` improvements)

## Key Principles

- **Never echo actual secret values** -- Always mask secrets in the report. Show only the first 4 and last 4 characters with asterisks in between (e.g., `AKIA****WXYZ`). For short secrets (fewer than 12 characters), show only the first 2 and last 2 characters.
- **Prioritize by impact**: committed secrets in current files > secrets visible in git history > secrets in example/template files
- **Context-aware analysis**: A `SECRET_KEY` in `.env.example` with value `changeme` is not a finding. A `SECRET_KEY` in `.env` with a 64-character hex string is a critical finding.
- **No false sense of security**: Clearly state that automated scanning cannot catch all secrets. Recommend manual review for custom secret formats.
- **Actionable output**: Every finding must include a specific remediation step. Generic advice is not sufficient.
- **Language-agnostic**: This skill works on any text file. Do not assume any specific programming language or framework.
