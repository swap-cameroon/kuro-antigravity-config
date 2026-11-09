---
name: dependency-audit
description: Scan dependency manifests for known CVEs across multiple programming ecosystems
trigger:
  - audit dependencies
  - check for vulnerable packages
  - scan for CVEs
  - review supply chain security
  - dependency security check
  - find vulnerable dependencies
  - package vulnerability scan
---

# Dependency Audit Skill

Scan project dependency manifests for known CVEs and supply chain risks across all major programming ecosystems. This skill is language-agnostic and supports npm, pip, maven, bundler, go, composer, cargo, dotnet, and more.

## Workflow

### Step 1: Ecosystem Detection

Scan the project root and subdirectories for dependency manifest files to auto-detect the language and ecosystem in use. A project may use multiple ecosystems simultaneously.

**Detection matrix:**

| Ecosystem | Manifest Files |
|-----------|---------------|
| Node.js (npm/yarn/pnpm) | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python (pip/pipenv/poetry) | `requirements.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `poetry.lock`, `setup.py`, `setup.cfg` |
| Java (Maven/Gradle) | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| Ruby (Bundler) | `Gemfile`, `Gemfile.lock` |
| Go (modules) | `go.mod`, `go.sum` |
| PHP (Composer) | `composer.json`, `composer.lock` |
| Rust (Cargo) | `Cargo.toml`, `Cargo.lock` |
| .NET (NuGet) | `*.csproj`, `*.fsproj`, `packages.config`, `Directory.Build.props`, `Directory.Packages.props` |

Use glob patterns to find these files. Report which ecosystems were detected before proceeding.

### Step 2: Dependency Enumeration

Parse each detected manifest file to extract all direct and transitive dependencies with their version numbers.

**For lock files** (`package-lock.json`, `yarn.lock`, `Pipfile.lock`, `poetry.lock`, `Gemfile.lock`, `composer.lock`, `Cargo.lock`, `go.sum`):
- Extract exact resolved versions, not ranges.
- These represent the actual installed versions and are the ground truth for auditing.

**For manifest files without lock files** (`package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, etc.):
- Extract declared version ranges.
- Note that actual installed versions may differ; flag this as reduced audit confidence.

**For each dependency, record:**
- Package name (including scope/namespace if applicable)
- Declared version or version range
- Resolved version (from lock file if available)
- Whether it is a direct or transitive dependency
- Whether it is a production or development dependency

### Step 3: Vulnerability Lookup

Use the Bash tool to run the appropriate ecosystem-specific audit tool. Try tools in order of preference:

**Node.js:**
1. `npm audit --json` (preferred)
2. `yarn audit --json`
3. `pnpm audit --json`
4. Manual: cross-reference versions against `references/known_cves.md`

**Python:**
1. `pip-audit --format=json` (preferred)
2. `safety check --json`
3. `pip install pipdeptree && pipdeptree --warn fail`
4. Manual: cross-reference versions against `references/known_cves.md`

**Java:**
1. `mvn org.owasp:dependency-check-maven:check` (Maven)
2. `gradle dependencyCheckAnalyze` (Gradle with OWASP plugin)
3. Manual: cross-reference versions against `references/known_cves.md`

**Ruby:**
1. `bundle-audit check --update` (preferred)
2. `bundler-audit`
3. Manual: cross-reference versions against `references/known_cves.md`

**Go:**
1. `govulncheck ./...` (preferred)
2. `go list -m -json all` then cross-reference
3. Manual: cross-reference versions against `references/known_cves.md`

**PHP:**
1. `composer audit --format=json` (preferred, Composer 2.4+)
2. Manual: cross-reference versions against `references/known_cves.md`

**Rust:**
1. `cargo audit --json` (preferred)
2. Manual: cross-reference versions against `references/known_cves.md`

**.NET:**
1. `dotnet list package --vulnerable --format json` (preferred)
2. Manual: cross-reference versions against `references/known_cves.md`

**Fallback strategy:** If no audit tool is available or the Bash tool cannot execute the command, perform manual version analysis:
- Use the Read tool to read the dependency list from Step 2.
- Use the Read tool to load `references/known_cves.md` and cross-reference each package name and version.
- Use the Read tool to load `references/supply_chain.md` and check for supply chain risks.

### Step 4: Impact Assessment

For each vulnerability finding, assess the following dimensions:

1. **Severity (CVSS):** Report the CVSS v3.1 score and severity rating (Critical >= 9.0, High >= 7.0, Medium >= 4.0, Low < 4.0).

2. **Exploitability in project context:**
   - Is the vulnerable function/module actually imported and used in the project code?
   - Search the codebase for imports and usages of the affected package.
   - Determine if the vulnerable code path is reachable from user-controlled input.
   - Flag as "Reachable", "Potentially Reachable", or "Not Reachable" based on analysis.

3. **Patch availability:**
   - Is there a fixed version available?
   - What is the minimum version that resolves the vulnerability?
   - Are there multiple fix versions across major version lines?

4. **Breaking change risk:**
   - Is the fix a patch version bump (low risk)?
   - Is the fix a minor version bump (moderate risk)?
   - Is the fix a major version bump (high risk, likely breaking changes)?
   - Are there known breaking changes documented in the changelog?

5. **Transitive vs Direct:**
   - Is this a direct dependency (easier to fix) or transitive (may require upstream fix)?
   - If transitive, identify the dependency chain leading to the vulnerable package.

### Step 5: Report

Generate a structured report with the following sections:

**Summary:**
- Total dependencies scanned
- Number of vulnerabilities found by severity
- Ecosystems analyzed
- Audit confidence level (high if lock files present, medium otherwise)

**Findings table (sorted by severity, highest first):**

For each finding, include:
- CVE ID (or advisory ID)
- Affected package name and installed version
- Severity (Critical/High/Medium/Low) with CVSS score
- Brief description of the vulnerability
- Fixed version (minimum version that resolves the issue)
- Upgrade path (exact command or change needed)
- Reachability assessment (whether the vulnerable code path is actually used)

**Recommended actions:**
- Prioritized list of upgrades to perform
- Group by risk level (breaking vs non-breaking changes)
- Provide exact commands for each ecosystem (`npm install package@version`, `pip install package>=version`, etc.)

**Supply chain observations:**
- Any dependency confusion risks detected
- Suspicious package names (potential typosquatting)
- Packages with install scripts that should be reviewed
- Lock file integrity observations
