# Secrets Management Review

This reference covers detection of exposed secrets, hardcoded credentials, and best practices for secrets management across application stacks.

---

## Common Secret File Patterns

These files commonly contain secrets and must be reviewed carefully:

| File Pattern | Typical Contents | Risk |
|---|---|---|
| `.env` | Application secrets, database URLs, API keys | Critical — often committed accidentally |
| `.env.local` | Local overrides with real credentials | Critical |
| `.env.production` | Production secrets | Critical |
| `.env.development` | Dev credentials (may match production) | High |
| `application.yml` / `application.properties` | Spring Boot config with DB passwords | Critical |
| `appsettings.json` / `appsettings.*.json` | ASP.NET config with connection strings | Critical |
| `config.py` / `settings.py` | Python app config with SECRET_KEY | Critical |
| `credentials.json` | GCP service account key | Critical |
| `serviceAccount.json` | Firebase/GCP service account | Critical |
| `secrets.yaml` / `secrets.json` | Kubernetes secrets, app secrets | Critical |
| `*.pem` / `*.key` / `*.p12` / `*.pfx` | Private keys and certificates | Critical |
| `wp-config.php` | WordPress DB credentials | Critical |
| `database.yml` | Rails database config | High |
| `docker-compose.yml` | Hardcoded env vars | High |
| `.htpasswd` | HTTP Basic auth hashes | High |
| `id_rsa` / `id_ed25519` | SSH private keys | Critical |
| `known_hosts` | SSH host fingerprints | Low |
| `terraform.tfvars` / `*.auto.tfvars` | Terraform variable values with secrets | Critical |
| `kubeconfig` / `.kube/config` | Kubernetes cluster credentials | Critical |

### Review approach

1. Check if these files exist in the repository
2. Check if they are listed in `.gitignore`
3. If committed, check their contents for actual secrets vs. placeholders
4. Check git history — a file removed now may have been committed before

---

## Hardcoded Secret Indicators

### Variable Name Patterns

Scan for variables, keys, and configuration properties with these name patterns (case-insensitive):

**High-confidence indicators:**
- `SECRET_KEY`, `SECRET`, `APP_SECRET`
- `PASSWORD`, `PASSWD`, `PASS`
- `API_KEY`, `APIKEY`, `API_SECRET`
- `ACCESS_KEY`, `ACCESS_TOKEN`
- `PRIVATE_KEY`, `SIGNING_KEY`
- `AUTH_TOKEN`, `BEARER_TOKEN`
- `CLIENT_SECRET`, `CLIENT_ID` (when paired with a value)
- `DATABASE_URL` (contains password in connection string)
- `ENCRYPTION_KEY`, `MASTER_KEY`
- `AWS_SECRET_ACCESS_KEY`, `AWS_ACCESS_KEY_ID`
- `GITHUB_TOKEN`, `GITLAB_TOKEN`, `NPM_TOKEN`
- `SLACK_TOKEN`, `SLACK_WEBHOOK`
- `SENDGRID_API_KEY`, `TWILIO_AUTH_TOKEN`
- `STRIPE_SECRET_KEY`, `STRIPE_SK`
- `JWT_SECRET`, `JWT_SIGNING_KEY`

**Medium-confidence indicators (context-dependent):**
- `KEY`, `TOKEN`, `CREDENTIAL`, `AUTH`
- `CONNECTION_STRING`, `CONN_STR`
- `DSN` (data source name)
- `SALT`, `PEPPER`, `NONCE`
- `CERTIFICATE`, `CERT`

### Detection approach

For each variable found with a suspicious name:
1. Check if the value is a placeholder (`changeme`, `TODO`, `xxx`, `your-key-here`, `<replace>`)
2. Check if the value references an environment variable (`${VAR}`, `process.env.VAR`, `os.environ`)
3. Check if the value is an actual secret (high entropy, realistic format)

---

## Secret Value Patterns

### High-Entropy Strings

Secrets often appear as high-entropy strings. Look for:

- Strings longer than 20 characters with mixed case, digits, and special characters
- Hex strings: `[0-9a-f]{32,}` (MD5, SHA hashes, or keys)
- Base64 blocks: `[A-Za-z0-9+/]{40,}={0,2}`
- UUID-like: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`

### Known Secret Formats

| Provider | Pattern | Example |
|---|---|---|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIA_EXAMPLE_KEY` |
| AWS Secret Key | 40-char base64 | `AWS_SECRET_EXAMPLE_KEY` |
| GitHub Token | `ghp_[A-Za-z0-9]{36}` | `ghp_EXAMPLE_TOKEN` |
| GitHub OAuth | `gho_[A-Za-z0-9]{36}` | `gho_EXAMPLE_TOKEN` |
| GitLab Token | `glpat-[A-Za-z0-9\-]{20}` | `glpat_EXAMPLE_TOKEN` |
| Slack Token | `xox[baprs]-[0-9a-zA-Z-]+` | `xoxb_EXAMPLE_TOKEN` |
| Stripe Secret | `sk_live_[0-9a-zA-Z]{24,}` | `sk_live_EXAMPLE_SECRET` |
| Stripe Publishable | `pk_live_[0-9a-zA-Z]{24,}` | (lower risk but still flag) |
| SendGrid | `SG\.[0-9a-zA-Z\-_]{22}\.[0-9a-zA-Z\-_]{43}` | `SG.EXAMPLE_KEY` |
| Twilio | `SK[0-9a-fA-F]{32}` | `SK_EXAMPLE_TOKEN` |
| Google API Key | `AIza[0-9A-Za-z\-_]{35}` | `AIza_EXAMPLE_KEY` |
| npm Token | `npm_[A-Za-z0-9]{36}` | `npm_EXAMPLE_TOKEN` |
| PyPI Token | `pypi-[A-Za-z0-9]{50,}` | `pypi-xxxxxxxxxx...` |
| JWT | `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` | `eyJhbG...` |
| RSA Private Key | `-----BEGIN RSA PRIVATE KEY-----` | PEM block |
| Generic Private Key | `-----BEGIN PRIVATE KEY-----` | PEM block |
| Connection String | `(postgres\|mysql\|mongodb)://[^:]+:[^@]+@` | `postgres://user:pass@host/db` |

---

## Environment Variable Best Practices vs Hardcoding

### What NOT to do

```python
# Hardcoded in source code
DATABASE_URL = "postgres://admin:p@ssw0rd@db.example.com/myapp"
API_KEY = "sk-abc123def456"
SECRET_KEY = "my-secret-key-do-not-share"
```

```yaml
# Hardcoded in config file committed to VCS
spring:
  datasource:
    password: production_password_123
```

### Acceptable patterns

```python
# Environment variable reference
DATABASE_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ["SECRET_KEY"]
```

```yaml
# Spring Boot with env var reference
spring:
  datasource:
    password: ${DB_PASSWORD}
```

```typescript
// Node.js with environment variable
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error("API_KEY is required");
```

### Important caveats about environment variables

Environment variables are better than hardcoding but are not perfectly secure:
- They appear in `docker inspect` output
- They are visible in `/proc/<pid>/environ` on Linux
- They may be logged by process managers
- They are captured in core dumps
- Child processes inherit parent environment

For high-security applications, prefer secret management services (see below).

---

## Secrets in Git History

### .gitignore Patterns That Should Be Present

```gitignore
# Environment files
.env
.env.*
!.env.example

# Private keys
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519

# Credential files
credentials.json
serviceAccount.json
*-credentials.json
*.secret

# Terraform
*.tfvars
*.auto.tfvars
.terraform/

# Kubernetes
kubeconfig
*-kubeconfig.yaml

# IDE and local config
.idea/
.vscode/settings.json
```

### Checking for secrets committed in the past

Even if a file is now in `.gitignore`, it may have been committed previously. Secrets in git history remain accessible to anyone who clones the repository.

**Detection approach:**
1. Check `git log --all --diff-filter=D -- .env credentials.json` for deleted secret files
2. Check `git log --all -p -- .env` to see contents of previously committed env files
3. Recommend tools like `truffleHog` or `gitleaks` for comprehensive history scanning

### git-secrets Hooks

Recommend installing `git-secrets` or `gitleaks` as a pre-commit hook:
```bash
# git-secrets
git secrets --install
git secrets --register-aws

# gitleaks (via pre-commit)
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

---

## Secret Management Services

### HashiCorp Vault

**Integration patterns to look for:**
```python
# Dynamic secrets — good
client = hvac.Client(url='https://vault.example.com:8200')
secret = client.secrets.kv.v2.read_secret_version(path='myapp/db')
password = secret['data']['data']['password']
```

**Misconfigurations to flag:**
- Vault token hardcoded in source code
- Vault address using HTTP instead of HTTPS
- Root token used in application (should use AppRole or Kubernetes auth)
- No token renewal/rotation configured

### AWS Secrets Manager

**Good pattern:**
```python
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='myapp/production/db')
```

**Misconfigurations:**
- AWS credentials hardcoded alongside Secrets Manager calls
- Not using IAM roles (EC2 instance profile or EKS IRSA)
- Secrets without rotation configured

### Azure Key Vault

**Good pattern:**
```csharp
var client = new SecretClient(new Uri("https://myvault.vault.azure.net/"), new DefaultAzureCredential());
var secret = await client.GetSecretAsync("DatabasePassword");
```

### GCP Secret Manager

**Good pattern:**
```python
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(name="projects/my-project/secrets/db-password/versions/latest")
```

---

## Kubernetes Secrets

### Key points to review

1. **Base64 is NOT encryption**: Kubernetes Secrets are base64-encoded, not encrypted. Anyone with RBAC access to read Secrets can decode them trivially. Flag any documentation or comments suggesting base64 provides security.

2. **Encryption at rest**: Check if the cluster has encryption at rest configured (`EncryptionConfiguration`). Without it, Secrets are stored in plain text in etcd.

3. **Better alternatives:**
   - **Sealed Secrets** (Bitnami): Encrypt secrets client-side, only the controller can decrypt
   - **External Secrets Operator**: Sync secrets from AWS/Azure/GCP/Vault into Kubernetes
   - **SOPS**: Mozilla's Secret Operations tool for encrypting files
   - **CSI Secret Store Driver**: Mount secrets from external stores as volumes

4. **RBAC for Secrets**: Check that Roles/ClusterRoles granting access to Secrets are minimally scoped

---

## CI/CD Secrets

### GitHub Actions Secrets
- **Good**: Using `${{ secrets.MY_SECRET }}` in workflow files
- **Bad**: Printing secrets in logs (`echo ${{ secrets.MY_SECRET }}`)
- **Check**: Are secrets scoped to environments with protection rules?
- **Check**: Are secrets available to pull request workflows from forks?

### GitLab CI Variables
- **Good**: Variables marked as "Protected" and "Masked"
- **Bad**: Variables available to all branches (should be protected branches only)
- **Check**: Are variables scoped to environments?
- **Check**: `CI_JOB_TOKEN` permissions restricted appropriately

### Jenkins Credentials Store
- **Good**: Using `withCredentials()` binding
- **Bad**: Credentials in Jenkinsfile as plain text
- **Check**: Credentials scoped to specific folders/pipelines
- **Check**: Script console access restricted

---

## Secret Rotation

### What to check

1. **Static secrets**: Are long-lived secrets (API keys, database passwords) rotated on a schedule?
2. **Token expiry**: Do JWT tokens and OAuth tokens have reasonable expiry times?
3. **Key rotation**: Are encryption keys versioned and rotatable?
4. **Automated rotation**: Is rotation automated or manual? Manual rotation is error-prone and often skipped.

### Rotation tooling
- AWS Secrets Manager rotation lambdas
- HashiCorp Vault dynamic secrets (auto-rotating)
- Cloud provider managed identity (no secrets to rotate)
- `rotate-secrets` Kubernetes operator

---

## Detection Tools

Recommend these tools for ongoing secret detection:

| Tool | Scope | Integration |
|---|---|---|
| **gitleaks** | Git history + current files | Pre-commit hook, CI/CD |
| **truffleHog** | Git history, S3, filesystem | CI/CD, one-time scan |
| **detect-secrets** | Current files (baseline approach) | Pre-commit hook |
| **git-secrets** | Git hooks (AWS-focused) | Pre-commit hook |
| **GitHub Secret Scanning** | GitHub repos | Automatic (free for public repos) |
| **GitLab Secret Detection** | GitLab repos | CI/CD template |
| **talisman** | Pre-push hook | Git hook |
| **whispers** | Structured config files | CI/CD |

### Recommended baseline

At minimum, a project should have:
1. A pre-commit hook running `gitleaks` or `detect-secrets`
2. A CI/CD job scanning for secrets on every push
3. `.gitignore` rules for all known secret file patterns
4. Documentation of where secrets should be stored (not in code)
