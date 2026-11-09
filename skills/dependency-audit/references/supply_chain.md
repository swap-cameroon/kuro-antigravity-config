# Supply Chain Security Reference

Comprehensive reference for detecting and mitigating software supply chain risks in dependency management.

---

## Dependency Confusion Attacks

Dependency confusion (also called namespace confusion or substitution attack) exploits the way package managers resolve packages from multiple registries.

### Attack Mechanism
1. Attacker identifies internal/private package names (via leaked `package.json`, error messages, GitHub repos, or job postings).
2. Attacker publishes a public package with the same name but a higher version number.
3. Package manager resolves the public package instead of the private one due to version precedence.

### Affected Ecosystems
- **npm**: Resolves from public registry by default. Scoped packages (`@company/package`) are safer but not immune if the scope is not claimed.
- **pip**: `--extra-index-url` does not take priority over PyPI — both registries are checked and the highest version wins.
- **Maven**: Repository order in `settings.xml` matters, but some configurations check all repositories.
- **NuGet**: Multiple package sources are checked; highest version may win depending on configuration.
- **Composer**: Packagist is checked by default alongside private repos.
- **Go**: Module proxy (`GOPROXY`) settings determine resolution order.
- **RubyGems**: Source order in `Gemfile` affects resolution.

### Mitigation Strategies
- **npm**: Use scoped packages (`@company/package`). Set `.npmrc` with `registry=https://private-registry.company.com/` and use `@company:registry=https://private-registry.company.com/`.
- **pip**: Use `--index-url` (not `--extra-index-url`) to set a single authoritative source. Use a private index proxy that mirrors PyPI.
- **Maven**: Pin repository order in `settings.xml`. Use `<mirrorOf>*</mirrorOf>` with a private proxy.
- **NuGet**: Use `<clear />` in `nuget.config` package sources, then add only trusted sources.
- **General**: Claim your internal package names on public registries as placeholders. Use lock files to pin exact resolved versions and sources.

### Detection
- Check for packages without a scope/namespace that share names with known internal packages.
- Audit lock files for unexpected registry URLs.
- Monitor for new public packages matching internal naming conventions.

---

## Typosquatting

Typosquatting exploits human error in typing package names. Attackers publish malicious packages with names similar to popular legitimate packages.

### Common Patterns
- **Character transposition**: `reqeusts` instead of `requests`
- **Missing characters**: `requsts` instead of `requests`
- **Extra characters**: `requestss` instead of `requests`
- **Character substitution**: `req0ests` (zero for 'u'), `requests-` (trailing hyphen)
- **Wrong separator**: `node_fetch` instead of `node-fetch`
- **Homoglyph**: Using visually similar Unicode characters
- **Plural/singular confusion**: `request` vs `requests`
- **Scope confusion (npm)**: `@types/lodash` (legitimate) vs `@typos/lodash` (malicious)

### Notable Typosquatting Incidents
- **ua-parser-js (npm)**: Legitimate package hijacked; versions 0.7.29, 0.8.0, 1.0.0 contained crypto miners (2021).
- **colors/faker (npm)**: Maintainer sabotaged their own packages; `colors` v1.4.1+ and `faker` v6+ contained infinite loop (2022).
- **event-stream (npm)**: Maintainer transferred ownership; new maintainer added `flatmap-stream` containing Bitcoin-stealing code (2018).
- **ctx (PyPI)**: Typosquatting package harvesting environment variables and AWS credentials (2022).
- **requests (PyPI)**: Multiple typosquats like `request`, `python-requests` targeting the popular `requests` library.

### Detection Techniques
- Compare installed package names against a known-good list.
- Flag packages with names similar to popular packages (Levenshtein distance <= 2).
- Check package download counts — legitimate packages have high download counts; typosquats have low counts.
- Verify package author/maintainer against expected identities.

---

## Malicious Packages

### Common Payload Vectors
- **Install scripts**: `preinstall`, `postinstall` (npm), `setup.py` (pip), `build.rs` (Cargo) — execute arbitrary code during installation.
- **Import-time execution**: Code in `__init__.py` (Python), top-level module code (Node.js) runs on first import.
- **Obfuscated payloads**: Base64-encoded strings, hex-encoded byte arrays, `eval()` calls, dynamically constructed function names.
- **Environment variable exfiltration**: Reading CI/CD tokens, AWS keys, API keys, SSH keys.
- **Reverse shells**: Establishing outbound connections to attacker-controlled servers.
- **Cryptominers**: CPU-intensive background processes.
- **Credential stealers**: Targeting browser credential stores, SSH keys, cloud provider credentials.

### Detection Techniques
- **Static analysis of install scripts**: Review `preinstall`/`postinstall` in `package.json`. Check `setup.py` for suspicious imports (`os`, `subprocess`, `socket`, `urllib`).
- **Network activity monitoring**: Flag packages making outbound HTTP requests during installation.
- **Code obfuscation detection**: Flag `eval()`, `exec()`, base64 decoding, `Buffer.from()` with encoding in install scripts.
- **File system access patterns**: Flag packages reading `/etc/passwd`, `~/.ssh/`, `~/.aws/`, browser credential stores.
- **Behavioral analysis**: Run installation in a sandbox and monitor syscalls.

### npm-Specific Checks
```
npm ls --all                    # List all installed packages with versions
npm explain <package>           # Show why a package is installed (dependency chain)
npm audit signatures            # Verify registry signatures (npm 8.13+)
npm pack --dry-run <package>    # Preview package contents before install
```

### pip-Specific Checks
```
pip show <package>              # Show package metadata
pip download --no-binary :all:  # Download source to inspect before install
pip install --require-hashes    # Enforce hash checking from requirements file
```

---

## SBOM (Software Bill of Materials)

An SBOM is a formal record of all components, libraries, and dependencies in a software application. Required by Executive Order 14028 for US government software suppliers.

### Formats
- **CycloneDX**: OWASP standard, supports JSON and XML. Focus on security use cases. Supports vulnerability references, license information, and component relationships.
- **SPDX**: Linux Foundation standard, ISO/IEC 5962:2021. Broader scope including license compliance. Supports RDF, JSON, YAML, tag-value formats.

### Generation Tools
- **Syft** (Anchore): Multi-ecosystem SBOM generator. `syft . -o cyclonedx-json`
- **cdxgen** (CycloneDX): `cdxgen -o bom.json`
- **trivy** (Aqua Security): `trivy fs --format cyclonedx .`
- **npm**: `npm sbom --sbom-format cyclonedx` (npm 10+)
- **pip**: `cyclonedx-py` or `pip-audit --format cyclonedx`
- **Maven**: `mvn org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom`
- **Gradle**: CycloneDX Gradle plugin
- **Go**: `cyclonedx-gomod`
- **Cargo**: `cargo-cyclonedx`

### SBOM Best Practices
- Generate SBOMs at build time, not from source manifests alone.
- Include transitive dependencies with exact versions.
- Store SBOMs as build artifacts alongside release binaries.
- Regularly scan SBOMs against vulnerability databases (OSV, NVD).

---

## Lock File Integrity

Lock files pin exact dependency versions and integrity hashes, preventing silent upgrades to compromised versions.

### What Lock Files Protect Against
- Unexpected version bumps (range resolution changing).
- Registry-side package replacement (if hashes are verified).
- Build reproducibility — everyone installs the same versions.

### Integrity Verification

| Ecosystem | Lock File | Hash Algorithm | Verification Command |
|-----------|-----------|---------------|---------------------|
| npm | `package-lock.json` | SHA-512 (integrity field) | `npm ci` (strict install from lock file) |
| Yarn | `yarn.lock` | SHA-512 | `yarn install --frozen-lockfile` |
| pnpm | `pnpm-lock.yaml` | SHA-512 | `pnpm install --frozen-lockfile` |
| pip | `requirements.txt` | SHA-256 (optional) | `pip install --require-hashes -r requirements.txt` |
| Poetry | `poetry.lock` | SHA-256 | `poetry install --no-update` |
| Bundler | `Gemfile.lock` | N/A (version pin only) | `bundle install --frozen` |
| Cargo | `Cargo.lock` | SHA-256 (checksum field) | `cargo install --locked` |
| Go | `go.sum` | SHA-256 (h1: hash) | `go mod verify` |
| Composer | `composer.lock` | SHA-256 | `composer install --no-update` |

### Lock File Audit Checks
1. **Lock file exists**: Warn if a manifest file exists without a corresponding lock file.
2. **Lock file committed**: Lock files should be in version control (except for libraries — npm recommends not committing `package-lock.json` for libraries).
3. **No unauthorized changes**: Diff lock files in PRs to detect unexpected dependency changes.
4. **Hash integrity**: Verify that hashes in lock files match the actual downloaded packages.
5. **Source consistency**: Ensure all packages resolve from expected registries.

---

## Pinning Strategies

### Exact Pinning (`==`, `=`)
- **Pros**: Maximum reproducibility. Exact version installed every time.
- **Cons**: No automatic security patches. Requires manual updates. Can cause conflicts with other packages requiring different versions.
- **Best for**: Production deployments, applications, Docker images.

### Range Pinning (`^`, `~`, `>=`)
- **Pros**: Automatic patch/minor updates. Reduced maintenance burden.
- **Cons**: New versions may introduce bugs or vulnerabilities. Less reproducible without lock files.
- **Best for**: Libraries (to avoid dependency conflicts for consumers).

### Recommendations by Ecosystem
- **npm/yarn/pnpm**: Use `^` (caret) ranges in `package.json` with committed `package-lock.json`. Run `npm audit` in CI.
- **pip**: Use exact versions in `requirements.txt` with hashes. Use `pip-compile` (pip-tools) to generate pinned files from `requirements.in`.
- **Bundler**: Use `~>` (pessimistic operator) in `Gemfile`. Commit `Gemfile.lock`.
- **Go**: `go.mod` pins minimum versions. `go.sum` provides integrity verification. Both should be committed.
- **Cargo**: Use exact versions for applications, semver ranges for libraries. Commit `Cargo.lock` for applications.
- **Composer**: Use `^` in `composer.json`. Commit `composer.lock`.

---

## Registry Security

### npm
- **2FA**: Enable for publishing (`npm profile enable-2fa auth-and-writes`).
- **Audit signatures**: `npm audit signatures` verifies that packages were published through the registry and not modified.
- **Provenance**: npm provenance links packages to their source repo and build process (SLSA).
- **Token scoping**: Use granular tokens with minimal permissions. Set IP allowlists.
- **Automation tokens**: Use automation tokens in CI/CD (no 2FA prompt).

### PyPI
- **Trusted Publishers**: OIDC-based publishing from GitHub Actions, GitLab CI — no long-lived API tokens needed.
- **2FA**: Required for all new projects since 2024. Mandatory for critical projects.
- **API tokens**: Scoped to individual projects (preferred over account-wide passwords).

### Maven Central
- **GPG signing**: All artifacts must be GPG-signed.
- **Namespace verification**: Group IDs must be verified (domain ownership or GitHub org).
- **Immutability**: Published artifacts cannot be modified or deleted.

### RubyGems
- **MFA**: Required for gem owners with high-profile gems.
- **Yanking**: Gems can be yanked but the version number cannot be reused.
- **Trusted publishing**: Available via OIDC with GitHub Actions.

### Crates.io (Rust)
- **API tokens**: Scoped tokens for publishing.
- **Yanking**: Crates can be yanked; version number cannot be reused.

---

## Detection and Monitoring Tools

### Vulnerability Scanning
- **Snyk**: Commercial. Supports all major ecosystems. Provides fix PRs. CLI: `snyk test`.
- **Dependabot** (GitHub): Free for GitHub repos. Auto-creates PRs for vulnerable dependencies.
- **Renovate** (Mend): Free. Auto-creates PRs for dependency updates. Highly configurable update policies.
- **Socket.dev**: Focuses on supply chain attacks (malicious packages, typosquatting). Analyzes package behavior.
- **Trivy** (Aqua Security): Free. Scans filesystems, containers, IaC. `trivy fs .`
- **Grype** (Anchore): Free. SBOM-based vulnerability scanner. `grype sbom:bom.json`
- **OSV-Scanner** (Google): Free. Uses OSV database. `osv-scanner -r .`

### Ecosystem-Specific Tools
- **npm**: `npm audit`, `npm audit signatures`, `npm outdated`
- **pip**: `pip-audit`, `safety`, `pip-compile` (pip-tools)
- **Maven**: OWASP Dependency-Check plugin, `mvn versions:display-dependency-updates`
- **Bundler**: `bundle-audit`, `bundle outdated`
- **Go**: `govulncheck`, `go list -m -u all`
- **Cargo**: `cargo audit`, `cargo outdated`
- **Composer**: `composer audit`, `composer outdated`
- **NuGet**: `dotnet list package --vulnerable`, `dotnet list package --outdated`

### CI/CD Integration
- Run audit tools in CI pipelines and fail builds on critical/high vulnerabilities.
- Use lock files with `--frozen-lockfile` or `--ci` flags for reproducible installs.
- Generate and archive SBOMs as build artifacts.
- Set up automated alerts via Dependabot, Renovate, or Snyk for new vulnerabilities.
- Periodically audit lock file diffs in pull requests for unexpected changes.
