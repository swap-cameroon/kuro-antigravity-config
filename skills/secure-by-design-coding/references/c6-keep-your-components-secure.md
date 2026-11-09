### C6 — Keep Your Components Secure

*Your application is only as secure as its weakest dependency.*

**Dependency management rules:**
- Pin exact versions or use narrow ranges in production (`1.2.3` or `~1.2.3`, not `^1.2.3`)
- Maintain lockfiles (`package-lock.json`, `yarn.lock`, `Pipfile.lock`) — commit them
- Run `npm audit` / `pip-audit` in CI — fail on Critical/High
- Review new dependencies before adding: maintenance activity, download count, known CVEs
- Remove unused dependencies regularly
- Use Dependabot, Renovate, or similar for automated updates

**Supply chain protection:**
- Verify package integrity (checksums, signatures)
- Use `npm install --ignore-scripts` in CI, then run scripts explicitly
- Prefer packages from verified publishers
- Flag packages with no releases in >2 years
- Generate SBOM (Software Bill of Materials) for production

**Container security:**
- Use minimal base images (Alpine, distroless)
- Pin image digests, not just tags
- Scan images for CVEs (Trivy, Snyk)
- Never run as root in containers
- Don't store secrets in image layers (ENV, COPY .env)
