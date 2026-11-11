---
name: security-config-review
description: "Reviews infrastructure and configuration files for security misconfigurations across Docker, Kubernetes, CI/CD pipelines, web frameworks and secrets management. Use to check or harden deployment config."
trigger: When user asks to review security configuration, check for misconfigurations, harden infrastructure, audit deployment settings, or review config security posture.
---

# Security Configuration Review

Review infrastructure and configuration files for security misconfigurations. This skill is language-agnostic and supports containers, orchestration, CI/CD pipelines, web frameworks, cloud IaC, and secrets management.

## Workflow

### Step 1: Configuration Discovery

Scan the project for all configuration files. Auto-detect file types across these categories:

**Container & Orchestration:**
- `Dockerfile`, `Dockerfile.*`, `*.dockerfile`
- `docker-compose.yml`, `docker-compose.*.yml`, `compose.yml`, `compose.*.yml`
- `.dockerignore`
- Kubernetes manifests: `*.yaml`, `*.yml` in `k8s/`, `kubernetes/`, `manifests/`, `deploy/`, `helm/` directories, or any YAML with `apiVersion`/`kind` fields

**CI/CD Pipelines:**
- `.github/workflows/*.yml`
- `.gitlab-ci.yml`
- `Jenkinsfile`, `Jenkinsfile.*`
- `.circleci/config.yml`
- `azure-pipelines.yml`
- `bitbucket-pipelines.yml`
- `.travis.yml`

**Web Framework Configuration:**
- Express/Node.js: `index.ts`, `index.js`, `app.ts`, `app.js`, `server.ts`, `server.js`, `package.json`
- Flask: `app.py`, `config.py`, `wsgi.py`, `__init__.py`
- Django: `settings.py`, `settings/*.py`, `urls.py`
- Spring Boot: `application.yml`, `application.properties`, `application-*.yml`, `application-*.properties`, `pom.xml`
- Laravel: `.env`, `config/*.php`, `config/app.php`, `config/auth.php`, `config/cors.php`
- ASP.NET: `appsettings.json`, `appsettings.*.json`, `Startup.cs`, `Program.cs`, `web.config`

**Secrets & Credentials:**
- `.env`, `.env.*`, `.env.local`, `.env.production`
- `credentials.json`, `serviceAccount.json`, `secrets.yaml`, `secrets.json`
- Vault config files
- `*.pem`, `*.key` (check if committed)

**Cloud Infrastructure as Code:**
- `terraform/*.tf`, `*.tf`, `terraform.tfvars`, `*.tfvars`
- `cloudformation/*.yaml`, `cloudformation/*.json`, `*.template`
- `pulumi/*`, `Pulumi.yaml`, `Pulumi.*.yaml`
- `ansible/*.yml`, `playbook*.yml`

Use Glob and Grep to discover these files. Do not assume a project uses only one technology — scan for all categories.

### Step 2: Checklist Application

For each discovered configuration file, use the Read tool to load the appropriate hardening checklist from the reference documents:

- Docker/Kubernetes files: Use `references/docker_hardening.md`
- Web framework configs: Use `references/web_framework_hardening.md`
- Secret/credential files: Use `references/secrets_management.md`
- CI/CD pipeline files: Use `references/cicd_hardening.md`

Use the Read tool to read each config file fully. Check every applicable item from the relevant checklist. Do not skip checks — be thorough.

### Step 3: Severity Assessment

Rate each finding using this scale:

| Severity | Criteria | Examples |
|----------|----------|---------|
| **Critical** | Secrets exposed, RCE possible, complete auth bypass | Hardcoded API keys, privileged containers with host mounts, DEBUG=True with exposed management endpoints |
| **High** | Elevated privileges, missing authentication, data exposure risk | Running as root, CORS wildcard with credentials, missing network policies |
| **Medium** | Weak defaults, missing security headers, overly permissive settings | No rate limiting, missing helmet, unpinned image tags |
| **Low** | Best practice deviations, defense-in-depth gaps | Missing HEALTHCHECK, no resource limits in dev, shell form CMD |

### Step 4: Context Evaluation

Consider the project context before finalizing findings:

- **Development vs Production**: A `DEBUG=True` in a clearly-labeled dev config is lower severity than in a production config. Note the distinction but still flag it.
- **Project type**: A public-facing web app has different threat exposure than an internal tool.
- **Existing mitigations**: If a reverse proxy handles TLS and headers, missing framework-level headers may be mitigated. Note this.
- **Intentional choices**: Some configs may be intentionally permissive for valid reasons. Flag but acknowledge.

Do NOT dismiss findings just because it is a development project. Development configs often become production configs.

### Step 5: Report

Present findings in a structured report. For each finding include:

| Field | Description |
|-------|-------------|
| **Finding** | Clear description of the misconfiguration |
| **File:Line** | Exact location (file path and line number) |
| **Severity** | Critical / High / Medium / Low |
| **Current Value** | What the config currently does |
| **Recommended Value** | What it should be changed to |
| **Rationale** | Why this matters — what attack or risk it enables |

Group findings by severity (Critical first, then High, Medium, Low).

End the report with:
- A summary count: X Critical, Y High, Z Medium, W Low
- Top 3 priority actions to take immediately
- Any positive security practices already in place (acknowledge good config)
