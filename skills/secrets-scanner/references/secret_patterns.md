# Secret Patterns Reference

Comprehensive regex patterns for detecting hardcoded secrets in source code, configuration files, and infrastructure definitions. Each pattern includes the secret type, regex, description, redacted example, and severity level.

---

## Cloud Provider Keys

### AWS

#### AWS Access Key ID
- **Regex**: `AKIA[0-9A-Z]{16}`
- **Description**: AWS IAM access key identifier. Always starts with `AKIA` followed by 16 uppercase alphanumeric characters. These keys grant programmatic access to AWS services.
- **Example**: `AKIA****EXAMPLEKEY`
- **Severity**: Critical

#### AWS Secret Access Key
- **Regex**: `(?i)aws_secret_access_key\s*[=:]\s*['"]?([A-Za-z0-9/+=]{40})['"]?`
- **Description**: 40-character base64-encoded string that pairs with the Access Key ID. Often found in AWS config files, environment variables, or source code. Must appear in assignment context to reduce false positives.
- **Example**: `wJal****...****xmpl`
- **Severity**: Critical

#### AWS Session Token
- **Regex**: `(?i)aws_session_token\s*[=:]\s*['"]?(FwoGZX[A-Za-z0-9/+=]{100,})['"]?`
- **Description**: Temporary session token starting with `FwoGZX`. These are long base64 strings used with temporary security credentials from STS.
- **Example**: `FwoG****...****token`
- **Severity**: High

#### AWS MWS Auth Token
- **Regex**: `amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
- **Description**: Amazon Marketplace Web Service authentication token in UUID format prefixed with `amzn.mws.`.
- **Example**: `amzn.mws.1234****...****cdef`
- **Severity**: High

### Google Cloud Platform (GCP)

#### GCP Service Account Key
- **Regex**: `"type"\s*:\s*"service_account"`
- **Description**: JSON key file for GCP service accounts. Look for JSON files containing this field along with `project_id`, `private_key_id`, `private_key`, and `client_email`. The entire JSON file is the secret.
- **Example**: `{"type": "service_account", "project_id": "my-project", ...}`
- **Severity**: Critical

#### GCP API Key
- **Regex**: `AIza[0-9A-Za-z\-_]{35}`
- **Description**: Google Cloud API key. Starts with `AIza` followed by 35 characters. Used for accessing Google APIs including Maps, YouTube, and other services.
- **Example**: `AIza****...****xmpl`
- **Severity**: High

#### GCP OAuth Client Secret
- **Regex**: `(?i)client_secret.*GOCSPX-[A-Za-z0-9\-_]{28}`
- **Description**: Google OAuth 2.0 client secret starting with `GOCSPX-`.
- **Example**: `GOCSPX-****...****xmpl`
- **Severity**: High

### Microsoft Azure

#### Azure Storage Account Key
- **Regex**: `(?i)(AccountKey|azure_storage_key|AZURE_STORAGE_KEY)\s*[=:]\s*['"]?([A-Za-z0-9/+=]{86,90}==)['"]?`
- **Description**: Base64-encoded storage account access key, approximately 88 characters ending in `==`. Grants full access to Azure Storage resources.
- **Example**: `sv3k****...****Q===`
- **Severity**: Critical

#### Azure AD Client Secret
- **Regex**: `(?i)(client_secret|AZURE_CLIENT_SECRET)\s*[=:]\s*['"]?(~[A-Za-z0-9_\-\.]{34})['"]?`
- **Description**: Azure Active Directory application client secret, typically starting with `~` followed by 34 characters.
- **Example**: `~7Q8****...****xmpl`
- **Severity**: High

#### Azure Connection String
- **Regex**: `(?i)(DefaultEndpointsProtocol=https?;AccountName=[^;]+;AccountKey=[A-Za-z0-9/+=]{86,90}==)`
- **Description**: Full Azure Storage connection string containing the account name and access key.
- **Example**: `DefaultEndpointsProtocol=https;AccountName=myacct;AccountKey=****`
- **Severity**: Critical

#### Azure SAS Token
- **Regex**: `(?i)[?&]sig=[A-Za-z0-9%/+=]{43,}%3D`
- **Description**: Shared Access Signature token used in Azure Storage URLs.
- **Example**: `?sv=2020-08-04&sig=****`
- **Severity**: High

### DigitalOcean

#### DigitalOcean Personal Access Token
- **Regex**: `dop_v1_[a-f0-9]{64}`
- **Description**: DigitalOcean personal access token, version 1. Starts with `dop_v1_` followed by 64 hex characters.
- **Example**: `dop_v1_abcd****...****ef01`
- **Severity**: Critical

#### DigitalOcean OAuth Token
- **Regex**: `doo_v1_[a-f0-9]{64}`
- **Description**: DigitalOcean OAuth application token.
- **Example**: `doo_v1_abcd****...****ef01`
- **Severity**: High

#### DigitalOcean Refresh Token
- **Regex**: `dor_v1_[a-f0-9]{64}`
- **Description**: DigitalOcean OAuth refresh token.
- **Example**: `dor_v1_abcd****...****ef01`
- **Severity**: High

### Heroku

#### Heroku API Key
- **Regex**: `(?i)heroku.*[=:]\s*['"]?([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})['"]?`
- **Description**: Heroku API key in UUID format. Must appear in context with "heroku" keyword to avoid false positives with generic UUIDs.
- **Example**: `a1b2c3d4-****-****-****-ef0123456789`
- **Severity**: High

### Alibaba Cloud

#### Alibaba Cloud Access Key ID
- **Regex**: `LTAI[A-Za-z0-9]{20}`
- **Description**: Alibaba Cloud access key identifier starting with `LTAI`.
- **Example**: `LTAI****...****xmpl`
- **Severity**: Critical

### IBM Cloud

#### IBM Cloud IAM API Key
- **Regex**: `(?i)ibm.*api_key\s*[=:]\s*['"]?([A-Za-z0-9\-_]{44})['"]?`
- **Description**: IBM Cloud IAM API key, 44 characters in length.
- **Example**: `abcd****...****xmpl`
- **Severity**: High

---

## Source Code Hosting

### GitHub

#### GitHub Personal Access Token
- **Regex**: `ghp_[A-Za-z0-9_]{36}`
- **Description**: GitHub personal access token (classic). Starts with `ghp_` followed by 36 alphanumeric characters. Grants access to GitHub API based on scopes.
- **Example**: `ghp_****...****ab3f`
- **Severity**: Critical

#### GitHub OAuth Access Token
- **Regex**: `gho_[A-Za-z0-9_]{36}`
- **Description**: GitHub OAuth access token. Generated through OAuth app authorization flow.
- **Example**: `gho_****...****cd5e`
- **Severity**: High

#### GitHub User-to-Server Token
- **Regex**: `ghu_[A-Za-z0-9_]{36}`
- **Description**: GitHub App user-to-server token for acting on behalf of a user.
- **Example**: `ghu_****...****fg7h`
- **Severity**: High

#### GitHub Server-to-Server Token
- **Regex**: `ghs_[A-Za-z0-9_]{36}`
- **Description**: GitHub App server-to-server (installation) token. Shorter-lived but still sensitive.
- **Example**: `ghs_****...****ij9k`
- **Severity**: High

#### GitHub Fine-Grained Personal Access Token
- **Regex**: `github_pat_[A-Za-z0-9_]{82}`
- **Description**: GitHub fine-grained personal access token with repository-scoped permissions.
- **Example**: `github_pat_****...****xmpl`
- **Severity**: Critical

#### GitHub App Refresh Token
- **Regex**: `ghr_[A-Za-z0-9_]{36}`
- **Description**: GitHub App refresh token for renewing user-to-server tokens.
- **Example**: `ghr_****...****lm2n`
- **Severity**: High

### GitLab

#### GitLab Personal Access Token
- **Regex**: `glpat-[A-Za-z0-9\-_]{20}`
- **Description**: GitLab personal access token. Starts with `glpat-` followed by 20 characters.
- **Example**: `glpat-****...****xmpl`
- **Severity**: Critical

#### GitLab Pipeline Trigger Token
- **Regex**: `glptt-[A-Za-z0-9\-_]{40}`
- **Description**: GitLab pipeline trigger token for CI/CD pipeline triggering.
- **Example**: `glptt-****...****xmpl`
- **Severity**: High

#### GitLab Runner Registration Token
- **Regex**: `GR1348941[A-Za-z0-9\-_]{20}`
- **Description**: GitLab Runner registration token starting with `GR1348941`.
- **Example**: `GR1348941****...****xmpl`
- **Severity**: High

### Bitbucket

#### Bitbucket App Password
- **Regex**: `(?i)bitbucket.*[=:]\s*['"]?([A-Za-z0-9]{20,})['"]?`
- **Description**: Bitbucket app password. Requires context keyword "bitbucket" to distinguish from other random strings.
- **Example**: `ATBB****...****xmpl`
- **Severity**: High

---

## Payment Providers

### Stripe

#### Stripe Secret Key (Live)
- **Regex**: `sk_live_[A-Za-z0-9]{24,}`
- **Description**: Stripe live secret API key. Grants full access to the Stripe account in production. This is a critical finding.
- **Example**: `sk_live_****...****xmpl`
- **Severity**: Critical

#### Stripe Publishable Key (Live)
- **Regex**: `pk_live_[A-Za-z0-9]{24,}`
- **Description**: Stripe live publishable key. Designed to be public-facing but its presence in backend code may indicate architecture issues.
- **Example**: `pk_live_****...****xmpl`
- **Severity**: Low

#### Stripe Secret Key (Test)
- **Regex**: `sk_test_[A-Za-z0-9]{24,}`
- **Description**: Stripe test mode secret key. Lower risk but should still not be hardcoded.
- **Example**: `sk_test_****...****xmpl`
- **Severity**: Low

#### Stripe Restricted Key
- **Regex**: `rk_live_[A-Za-z0-9]{24,}`
- **Description**: Stripe restricted API key with limited permissions.
- **Example**: `rk_live_****...****xmpl`
- **Severity**: High

### PayPal

#### PayPal Client Secret
- **Regex**: `(?i)(paypal.*client_secret|PAYPAL_SECRET)\s*[=:]\s*['"]?([A-Za-z0-9\-_]{32,})['"]?`
- **Description**: PayPal REST API client secret. Requires PayPal context keyword.
- **Example**: `EBWKj****...****xmpl`
- **Severity**: Critical

#### PayPal Braintree Access Token
- **Regex**: `access_token\$production\$[a-z0-9]{16}\$[a-f0-9]{32}`
- **Description**: PayPal Braintree production access token.
- **Example**: `access_token$production$****$****`
- **Severity**: Critical

### Square

#### Square Access Token
- **Regex**: `sq0atp-[A-Za-z0-9\-_]{22}`
- **Description**: Square OAuth access token for production API access.
- **Example**: `sq0atp-****...****xmpl`
- **Severity**: Critical

#### Square Application Secret
- **Regex**: `sq0csp-[A-Za-z0-9\-_]{43}`
- **Description**: Square application-level secret.
- **Example**: `sq0csp-****...****xmpl`
- **Severity**: Critical

---

## Communication Services

### Slack

#### Slack Bot Token
- **Regex**: `xoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{24}`
- **Description**: Slack bot user OAuth token. Grants bot-level access to Slack workspaces and channels.
- **Example**: `xoxb-1234****-5678****-AbCd****EfGh`
- **Severity**: High

#### Slack User Token
- **Regex**: `xoxp-[0-9]{10,}-[0-9]{10,}-[0-9]{10,}-[a-f0-9]{32}`
- **Description**: Slack user OAuth token. Grants user-level access to Slack workspaces.
- **Example**: `xoxp-1234****-5678****-9012****-abcd****`
- **Severity**: Critical

#### Slack Webhook URL
- **Regex**: `https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}`
- **Description**: Slack incoming webhook URL. Allows posting messages to a specific channel.
- **Example**: `https://hooks.slack.com/services/T0000****/B0000****/xxxx****xxxx`
- **Severity**: Medium

#### Slack App-Level Token
- **Regex**: `xapp-[0-9]+-[A-Z0-9]+-[0-9]+-[a-z0-9]+`
- **Description**: Slack app-level token for Socket Mode and other app configurations.
- **Example**: `xapp-1-A0****-1234****-abcd****`
- **Severity**: High

### Twilio

#### Twilio Account SID
- **Regex**: `AC[a-f0-9]{32}`
- **Description**: Twilio account identifier. 34 characters starting with `AC`. Not a secret on its own but combined with auth token grants full account access.
- **Example**: `ACabcd****...****ef01`
- **Severity**: Medium

#### Twilio Auth Token
- **Regex**: `(?i)(twilio.*auth_token|TWILIO_AUTH_TOKEN)\s*[=:]\s*['"]?([a-f0-9]{32})['"]?`
- **Description**: Twilio authentication token. 32 hex characters. Must appear in Twilio context to reduce false positives.
- **Example**: `abcd****...****ef01`
- **Severity**: Critical

#### Twilio API Key
- **Regex**: `SK[a-f0-9]{32}`
- **Description**: Twilio API key starting with `SK` followed by 32 hex characters.
- **Example**: `SKab****...****cd01`
- **Severity**: High

### SendGrid

#### SendGrid API Key
- **Regex**: `SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}`
- **Description**: SendGrid API key. Two dot-separated base64url segments.
- **Example**: `SG.xxxx****xxxx.yyyy****...****yyyy`
- **Severity**: High

### Mailgun

#### Mailgun API Key
- **Regex**: `key-[a-z0-9]{32}`
- **Description**: Mailgun API key. Starts with `key-` followed by 32 lowercase hex characters.
- **Example**: `key-abcd****...****ef01`
- **Severity**: High

#### Mailgun Domain Sending Key
- **Regex**: `(?i)mailgun.*[=:]\s*['"]?(key-[a-z0-9]{32})['"]?`
- **Description**: Mailgun domain-specific sending key in assignment context.
- **Example**: `key-abcd****...****ef01`
- **Severity**: High

### Telegram

#### Telegram Bot Token
- **Regex**: `[0-9]{8,10}:[A-Za-z0-9_-]{35}`
- **Description**: Telegram Bot API token. Numeric bot ID followed by colon and 35-character alphanumeric string.
- **Example**: `12345****:ABCd****...****xmpl`
- **Severity**: High

### Discord

#### Discord Bot Token
- **Regex**: `(?i)(discord.*token|DISCORD_TOKEN)\s*[=:]\s*['"]?([A-Za-z0-9\.\-_]{59,68})['"]?`
- **Description**: Discord bot authentication token. Long base64-like string requiring Discord context.
- **Example**: `MTIz****...****xmpl`
- **Severity**: High

#### Discord Webhook URL
- **Regex**: `https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9\-_]+`
- **Description**: Discord webhook URL for posting messages to channels.
- **Example**: `https://discord.com/api/webhooks/1234****/xxxx****`
- **Severity**: Medium

---

## Database Credentials

### MongoDB

#### MongoDB Connection String
- **Regex**: `mongodb(\+srv)?://[^:]+:[^@]+@[^\s'"]+`
- **Description**: MongoDB connection URI with embedded username and password. The credentials between `://` and `@` are the secret.
- **Example**: `mongodb+srv://user:****@cluster0.example.net/db`
- **Severity**: Critical

### PostgreSQL

#### PostgreSQL Connection String
- **Regex**: `postgres(ql)?://[^:]+:[^@]+@[^\s'"]+`
- **Description**: PostgreSQL connection URI with embedded credentials.
- **Example**: `postgresql://admin:****@db.example.com:5432/mydb`
- **Severity**: Critical

### MySQL

#### MySQL Connection String
- **Regex**: `mysql://[^:]+:[^@]+@[^\s'"]+`
- **Description**: MySQL connection URI with embedded credentials.
- **Example**: `mysql://root:****@localhost:3306/mydb`
- **Severity**: Critical

### Redis

#### Redis URL with Password
- **Regex**: `redis://[^:]*:[^@]+@[^\s'"]+`
- **Description**: Redis connection URL with authentication password.
- **Example**: `redis://:****@redis.example.com:6379/0`
- **Severity**: High

### Generic JDBC

#### JDBC Connection String with Password
- **Regex**: `jdbc:[a-z]+://[^\s'"]*password=[^\s&'"]+`
- **Description**: JDBC connection string containing an inline password parameter.
- **Example**: `jdbc:mysql://host:3306/db?password=****`
- **Severity**: Critical

---

## Authentication Tokens and Keys

### Private Keys

#### RSA/EC/OpenSSH Private Key
- **Regex**: `-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY( BLOCK)?-----`
- **Description**: PEM-encoded private key header. The entire key block from BEGIN to END is the secret. Grants authentication capabilities.
- **Example**: `-----BEGIN RSA PRIVATE KEY-----\nMIIEow...`
- **Severity**: Critical

#### PuTTY Private Key
- **Regex**: `PuTTY-User-Key-File-[0-9]+:`
- **Description**: PuTTY private key file header.
- **Example**: `PuTTY-User-Key-File-2: ssh-rsa`
- **Severity**: Critical

### JWT

#### JWT Secret (Variable Assignment)
- **Regex**: `(?i)(jwt_secret|JWT_SECRET|jwtSecret|jwt_signing_key)\s*[=:]\s*['"]([^'"]{8,})['"]`
- **Description**: JWT signing secret assigned to a variable. The secret value is used to sign and verify JSON Web Tokens.
- **Example**: `JWT_SECRET = "mysu****...****cret"`
- **Severity**: Critical

#### Hardcoded JWT Token
- **Regex**: `eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+`
- **Description**: Encoded JWT token (header.payload.signature). Three dot-separated base64url segments.
- **Example**: `eyJh****...****xmpl`
- **Severity**: Medium

### OAuth

#### OAuth Client Secret (Variable Assignment)
- **Regex**: `(?i)(client_secret|CLIENT_SECRET|clientSecret|app_secret|APP_SECRET)\s*[=:]\s*['"]([^'"]{8,})['"]`
- **Description**: OAuth client secret assigned to a variable. Used in OAuth 2.0 confidential client flows.
- **Example**: `CLIENT_SECRET = "aBcD****...****xYz0"`
- **Severity**: High

### Basic Auth

#### Basic Auth in URL
- **Regex**: `https?://[^:]+:[^@]+@[^/\s'"]+`
- **Description**: HTTP(S) URL with embedded basic authentication credentials (username:password@host).
- **Example**: `https://admin:****@api.example.com/v1`
- **Severity**: High

#### Authorization Header with Basic Auth
- **Regex**: `(?i)(Authorization|auth_header)\s*[=:]\s*['"]Basic\s+[A-Za-z0-9+/=]{10,}['"]`
- **Description**: Hardcoded HTTP Basic Authentication header with base64-encoded credentials.
- **Example**: `Authorization: Basic YWRt****...****==`
- **Severity**: High

#### Bearer Token (Hardcoded)
- **Regex**: `(?i)(Authorization|auth_header|token)\s*[=:]\s*['"]Bearer\s+[A-Za-z0-9\-_.]{20,}['"]`
- **Description**: Hardcoded Bearer token in an authorization header or variable assignment.
- **Example**: `Authorization: Bearer eyJh****...****xmpl`
- **Severity**: High

---

## Generic High-Entropy Patterns

### Hex Strings in Assignment Context

#### Long Hex String Assignment
- **Regex**: `(?i)(secret|token|key|password|credential|auth)\s*[=:]\s*['"]?([a-f0-9]{32,})['"]?`
- **Description**: Hex-encoded string of 32 or more characters assigned to a secret-related variable name.
- **Example**: `SECRET_KEY = "a3f8****...****b2c1"`
- **Severity**: High

### Base64 Strings in Assignment Context

#### Long Base64 String Assignment
- **Regex**: `(?i)(secret|token|key|password|credential|auth)\s*[=:]\s*['"]?([A-Za-z0-9+/]{40,}={0,2})['"]?`
- **Description**: Base64-encoded string of 40+ characters assigned to a secret-related variable name.
- **Example**: `AUTH_TOKEN = "dGhpc****...****dG9r"`
- **Severity**: High

### Password Assignments

#### Password Variable Assignment
- **Regex**: `(?i)(password|passwd|pwd|pass)\s*[=:]\s*['"]([^'"]{8,})['"]`
- **Description**: Password value assigned to a password-named variable. Minimum 8 characters to avoid trivial matches.
- **Example**: `password = "Sup3r****...****d!"`
- **Severity**: High

### API Key Assignments

#### API Key Variable Assignment
- **Regex**: `(?i)(api_key|apikey|api_token|access_token|auth_key)\s*[=:]\s*['"]([^'"]{16,})['"]`
- **Description**: API key or token assigned to an API-key-named variable. Minimum 16 characters.
- **Example**: `API_KEY = "sk-pr****...****xmpl"`
- **Severity**: High

### Encryption Keys

#### Encryption Key Assignment
- **Regex**: `(?i)(encryption_key|encrypt_key|aes_key|ENCRYPTION_KEY)\s*[=:]\s*['"]([^'"]{16,})['"]`
- **Description**: Encryption key value hardcoded in source code.
- **Example**: `ENCRYPTION_KEY = "0x4a****...****ff"`
- **Severity**: Critical

---

## CI/CD Specific Patterns

### GitHub Actions

#### Secrets Leaked in Echo/Run
- **Regex**: `echo.*\$\{\{\s*secrets\.[A-Z_]+\s*\}\}`
- **Description**: GitHub Actions workflow echoing a secret value, which would expose it in logs.
- **Example**: `echo "Key is ${{ secrets.API_KEY }}"`
- **Severity**: Critical

#### Hardcoded Secrets in Workflow
- **Regex**: `(?i)(env|with):\s*\n\s+[A-Z_]+:\s*['"]?[A-Za-z0-9\-_./+=]{20,}['"]?`
- **Description**: Hardcoded secret values in GitHub Actions workflow environment variables or input parameters instead of using `${{ secrets.NAME }}`.
- **Example**: `env:\n  API_KEY: "hardcoded****value"`
- **Severity**: High

### Docker

#### Docker Build Arg with Secret
- **Regex**: `(?i)ARG\s+(password|secret|token|key|api_key|credentials)[=\s]`
- **Description**: Dockerfile ARG instruction defining a secret-named build argument. Build args are visible in image history.
- **Example**: `ARG SECRET_KEY=myse****cret`
- **Severity**: High

#### Docker Env with Secret
- **Regex**: `(?i)ENV\s+(password|secret|token|key|api_key|credentials)\s+\S+`
- **Description**: Dockerfile ENV instruction embedding a secret value in the image layer.
- **Example**: `ENV DB_PASSWORD super****cret`
- **Severity**: High

### Terraform

#### Terraform Variable Default with Secret
- **Regex**: `(?i)variable\s+"(password|secret|token|key)"\s*\{[^}]*default\s*=\s*"[^"]+"`
- **Description**: Terraform variable with a hardcoded default value for a secret-named variable.
- **Example**: `variable "db_password" { default = "****" }`
- **Severity**: High

#### Terraform State File Credentials
- **Regex**: `(?i)"(password|secret_key|access_key|token)"\s*:\s*"[^"]+"`
- **Description**: Credentials found in Terraform state files (`.tfstate`). State files should never be committed.
- **Example**: `"password": "****"`
- **Severity**: Critical

### Kubernetes

#### Kubernetes Secret Data (Non-Opaque)
- **Regex**: `(?i)data:\s*\n(\s+[A-Za-z_\-]+:\s*[A-Za-z0-9+/=]{10,}\n)+`
- **Description**: Base64-encoded secret data in Kubernetes Secret manifests. While technically "encoded," base64 is not encryption.
- **Example**: `data:\n  password: c3Vw****ZXI=`
- **Severity**: High

---

## Third-Party Service Keys

### OpenAI

#### OpenAI API Key
- **Regex**: `sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}`
- **Description**: OpenAI API key format containing the `T3BlbkFJ` marker.
- **Example**: `sk-xxxx****T3BlbkFJ****xxxx`
- **Severity**: High

#### OpenAI Project Key
- **Regex**: `sk-proj-[A-Za-z0-9\-_]{80,}`
- **Description**: OpenAI project-scoped API key starting with `sk-proj-`.
- **Example**: `sk-proj-****...****xmpl`
- **Severity**: High

### Anthropic

#### Anthropic API Key
- **Regex**: `sk-ant-[A-Za-z0-9\-_]{80,}`
- **Description**: Anthropic API key starting with `sk-ant-`.
- **Example**: `sk-ant-****...****xmpl`
- **Severity**: High

### Firebase

#### Firebase Server Key
- **Regex**: `AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}`
- **Description**: Firebase Cloud Messaging server key.
- **Example**: `AAAA****:xxxx****...****xxxx`
- **Severity**: High

### Shopify

#### Shopify Access Token
- **Regex**: `shpat_[a-f0-9]{32}`
- **Description**: Shopify admin API access token.
- **Example**: `shpat_abcd****...****ef01`
- **Severity**: High

#### Shopify Shared Secret
- **Regex**: `shpss_[a-f0-9]{32}`
- **Description**: Shopify app shared secret.
- **Example**: `shpss_abcd****...****ef01`
- **Severity**: High

### Datadog

#### Datadog API Key
- **Regex**: `(?i)(datadog|dd).*api_key\s*[=:]\s*['"]?([a-f0-9]{32})['"]?`
- **Description**: Datadog API key, 32 hex characters in Datadog context.
- **Example**: `DD_API_KEY=abcd****...****ef01`
- **Severity**: High

### NPM

#### NPM Access Token
- **Regex**: `npm_[A-Za-z0-9]{36}`
- **Description**: NPM registry access token for publishing packages.
- **Example**: `npm_xxxx****...****xxxx`
- **Severity**: High

### PyPI

#### PyPI API Token
- **Regex**: `pypi-[A-Za-z0-9\-_]{100,}`
- **Description**: PyPI upload token for publishing Python packages.
- **Example**: `pypi-AgEI****...****xmpl`
- **Severity**: High

### NuGet

#### NuGet API Key
- **Regex**: `oy2[a-z0-9]{43}`
- **Description**: NuGet.org API key for publishing .NET packages.
- **Example**: `oy2a****...****xmpl`
- **Severity**: High

---

## Pattern Usage Notes

### Reducing False Positives

1. **Context matters**: Many patterns require surrounding context (variable names, file types) to avoid false positives. A 32-character hex string alone is not a finding; a 32-character hex string assigned to `API_KEY` is.

2. **File type considerations**: Secrets in `.env` files are higher confidence than secrets in test files. Adjust severity based on file path.

3. **Placeholder detection**: Before reporting a match, check if the value matches common placeholders: `changeme`, `CHANGEME`, `xxx`, `TODO`, `REPLACE_ME`, `your-*-here`, `example`, `sample`, `test`, `dummy`, `fake`, `mock`, `placeholder`.

4. **Entropy validation**: For generic patterns (hex strings, base64 strings), calculate Shannon entropy. Real secrets typically have entropy above 3.5 bits per character. Values below 3.0 are likely constants or code.

5. **Assignment operators**: Patterns using `[=:]` cover both `=` (code) and `:` (YAML/JSON) assignment contexts. Some patterns also match environment variable export syntax (`export VAR=value`).
