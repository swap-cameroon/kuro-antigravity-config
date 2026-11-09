# Project Detection Reference

Comprehensive detection patterns for identifying a project's technology stack, framework,
running services, and configuration. Used by the security-audit orchestrator in Step 1.

---

## 1. Language and Runtime Detection

### Node.js / TypeScript

**Manifest files:**
- `package.json` — primary manifest (check `dependencies` and `devDependencies` keys)
- `package-lock.json` — npm lock file
- `yarn.lock` — Yarn lock file
- `pnpm-lock.yaml` — pnpm lock file
- `bun.lockb` — Bun lock file

**Configuration files:**
- `tsconfig.json` — TypeScript configuration (confirms TypeScript usage)
- `.nvmrc` / `.node-version` — Node version pinning
- `.npmrc` — npm configuration (may contain registry tokens)
- `.yarnrc.yml` — Yarn configuration

**Typical entry points:**
- `index.js`, `index.ts`, `app.js`, `app.ts`, `server.js`, `server.ts`
- `src/index.js`, `src/main.ts`, `src/app.ts`
- Check `package.json` → `"main"` and `"scripts.start"` fields

**Framework detection (check `dependencies` in package.json):**
- `express` → Express.js
- `koa` → Koa
- `fastify` → Fastify
- `@nestjs/core` → NestJS
- `@hapi/hapi` → Hapi
- `restify` → Restify
- `next` → Next.js (SSR/SSG framework)
- `nuxt` → Nuxt.js (Vue SSR framework)
- `@angular/core` → Angular (frontend)
- `react` → React (frontend)
- `vue` → Vue.js (frontend)
- `socket.io` → WebSocket support

**Security-relevant packages to note:**
- `helmet` — HTTP security headers
- `cors` → CORS configuration
- `express-rate-limit` — Rate limiting
- `jsonwebtoken` / `jose` — JWT handling
- `bcrypt` / `argon2` — Password hashing
- `express-validator` / `joi` / `zod` — Input validation
- `csurf` / `csrf` — CSRF protection
- `passport` — Authentication middleware

---

### Python

**Manifest files:**
- `requirements.txt` — pip dependencies (one per line, may include version constraints)
- `pyproject.toml` — modern Python project config (PEP 621)
- `Pipfile` — Pipenv manifest
- `Pipfile.lock` — Pipenv lock file
- `setup.py` — legacy setuptools manifest
- `setup.cfg` — declarative setuptools config
- `poetry.lock` — Poetry lock file
- `conda-environment.yml` / `environment.yml` — Conda environment

**Configuration files:**
- `pyproject.toml` — may contain tool configs (black, ruff, mypy, pytest)
- `tox.ini` — test automation
- `.python-version` — pyenv version pinning
- `mypy.ini` / `.mypy.ini` — type checking config

**Typical entry points:**
- `app.py`, `main.py`, `run.py`, `wsgi.py`, `asgi.py`
- `manage.py` (Django)
- `src/main.py`, `src/app.py`

**Framework detection (check imports or dependency lists):**
- `flask` → Flask
- `django` → Django
- `fastapi` → FastAPI
- `tornado` → Tornado
- `sanic` → Sanic
- `starlette` → Starlette
- `aiohttp` → aiohttp
- `bottle` → Bottle
- `pyramid` → Pyramid
- `falcon` → Falcon

**Security-relevant packages:**
- `python-jose` / `pyjwt` — JWT handling
- `bcrypt` / `passlib` — Password hashing
- `cryptography` — Crypto operations
- `django-cors-headers` — CORS for Django
- `flask-cors` — CORS for Flask
- `flask-wtf` — CSRF protection for Flask
- `django-csp` — CSP headers for Django
- `bandit` — Python security linter (if in dev dependencies, security is being considered)
- `safety` — Dependency vulnerability checker

---

### Java / Kotlin

**Manifest files:**
- `pom.xml` — Maven project object model
- `build.gradle` — Gradle build script (Groovy DSL)
- `build.gradle.kts` — Gradle build script (Kotlin DSL)
- `settings.gradle` / `settings.gradle.kts` — multi-project settings
- `mvnw` / `gradlew` — wrapper scripts (confirm build tool)

**Lock files:**
- `gradle.lockfile` — Gradle dependency lock
- Maven does not have a standard lock file

**Typical entry points:**
- `src/main/java/**/Application.java`
- `src/main/java/**/Main.java`
- `src/main/kotlin/**/Application.kt`

**Framework detection (check dependencies in pom.xml or build.gradle):**
- `spring-boot-starter-web` → Spring Boot
- `spring-boot-starter-security` → Spring Security
- `io.micronaut` → Micronaut
- `io.quarkus` → Quarkus
- `jakarta.` / `javax.` → Jakarta EE
- `io.dropwizard` → Dropwizard
- `io.vertx` → Vert.x
- `play` → Play Framework

**Configuration files:**
- `application.properties` / `application.yml` — Spring Boot config
- `application-{profile}.properties` — Spring profiles
- `persistence.xml` — JPA configuration
- `web.xml` — Servlet configuration (legacy)
- `logback.xml` / `log4j2.xml` — Logging configuration

---

### Ruby

**Manifest files:**
- `Gemfile` — Bundler dependency manifest
- `Gemfile.lock` — Bundler lock file
- `*.gemspec` — Gem specification

**Typical entry points:**
- `config.ru` — Rack configuration (Rails, Sinatra)
- `app.rb` — Sinatra application
- `bin/rails` — Rails binary

**Framework detection (check Gemfile):**
- `rails` → Ruby on Rails
- `sinatra` → Sinatra
- `hanami` → Hanami
- `grape` → Grape (API framework)
- `roda` → Roda

**Configuration files:**
- `config/database.yml` — Database configuration (Rails)
- `config/routes.rb` — Route definitions (Rails)
- `config/environments/*.rb` — Environment configs (Rails)
- `config/initializers/` — Initialization scripts (Rails)
- `config/secrets.yml` — Secrets (Rails, deprecated but may still exist)
- `config/credentials.yml.enc` — Encrypted credentials (Rails 5.2+)

---

### Go

**Manifest files:**
- `go.mod` — Go module definition
- `go.sum` — Go dependency checksums

**Typical entry points:**
- `main.go` — standard entry point
- `cmd/*/main.go` — multi-binary projects
- `internal/` — private packages

**Framework detection (check go.mod or imports):**
- `github.com/gin-gonic/gin` → Gin
- `github.com/labstack/echo` → Echo
- `github.com/gofiber/fiber` → Fiber
- `github.com/go-chi/chi` → Chi
- `net/http` → Standard library HTTP
- `github.com/gorilla/mux` → Gorilla Mux
- `google.golang.org/grpc` → gRPC

**Security-relevant packages:**
- `golang.org/x/crypto` — Crypto utilities
- `github.com/golang-jwt/jwt` — JWT handling
- `github.com/rs/cors` — CORS middleware

---

### PHP

**Manifest files:**
- `composer.json` — Composer dependency manifest
- `composer.lock` — Composer lock file

**Typical entry points:**
- `index.php` — traditional entry point
- `public/index.php` — modern framework entry point
- `artisan` — Laravel CLI

**Framework detection (check composer.json `require`):**
- `laravel/framework` → Laravel
- `symfony/symfony` or `symfony/framework-bundle` → Symfony
- `slim/slim` → Slim
- `cakephp/cakephp` → CakePHP
- `codeigniter4/framework` → CodeIgniter
- `yiisoft/yii2` → Yii

**Configuration files:**
- `.env` — Environment configuration (Laravel, Symfony)
- `config/app.php` — Application config (Laravel)
- `config/database.php` — Database config (Laravel)
- `config/packages/security.yaml` — Security config (Symfony)
- `php.ini` / `.user.ini` — PHP runtime settings

---

### Rust

**Manifest files:**
- `Cargo.toml` — Cargo manifest
- `Cargo.lock` — Cargo lock file

**Typical entry points:**
- `src/main.rs` — binary entry point
- `src/lib.rs` — library entry point

**Framework detection (check Cargo.toml `[dependencies]`):**
- `actix-web` → Actix-web
- `axum` → Axum
- `rocket` → Rocket
- `warp` → Warp
- `tide` → Tide
- `hyper` → Hyper (low-level HTTP)
- `tonic` → gRPC

---

### .NET (C# / F#)

**Manifest files:**
- `*.csproj` — C# project file
- `*.fsproj` — F# project file
- `*.sln` — Solution file
- `global.json` — SDK version pinning
- `Directory.Build.props` — Shared build properties
- `NuGet.config` — NuGet package source configuration

**Lock files:**
- `packages.lock.json` — NuGet lock file

**Typical entry points:**
- `Program.cs` — application entry point
- `Startup.cs` — ASP.NET Core startup (pre-.NET 6)

**Framework detection (check `<PackageReference>` in .csproj):**
- `Microsoft.AspNetCore.*` → ASP.NET Core
- `Microsoft.AspNetCore.Blazor` → Blazor
- `Swashbuckle.AspNetCore` → Swagger/OpenAPI support
- `Microsoft.EntityFrameworkCore` → Entity Framework ORM

**Configuration files:**
- `appsettings.json` — Application settings
- `appsettings.{Environment}.json` — Environment-specific settings
- `web.config` — IIS configuration (legacy)
- `launchSettings.json` — Development launch profiles

---

## 2. Framework-Specific Entry Point Patterns

Use these code patterns to confirm framework detection when manifest files are ambiguous.

### Express.js
```
app.listen(          # Server startup
express()            # App initialization
router.get(          # Route definition
router.post(         # Route definition
app.use(             # Middleware registration
```

### Flask
```
Flask(__name__)      # App initialization
@app.route(          # Route decorator
app.run(             # Server startup
Blueprint(           # Blueprint registration
```

### Django
```
INSTALLED_APPS       # settings.py
urlpatterns          # urls.py
manage.py            # Management script
from django.        # Django imports
```

### Spring Boot
```
@SpringBootApplication    # Main class annotation
@RestController           # Controller annotation
@RequestMapping           # Route mapping
application.properties    # Config file
application.yml           # Config file
```

### Laravel
```
Route::get(          # Route definition
Route::post(         # Route definition
php artisan          # CLI tool
Illuminate\\        # Laravel namespace
```

### Rails
```
Rails.application    # Application reference
config.ru            # Rack config
resources :          # Route resources (routes.rb)
class.*Controller    # Controller classes
```

### ASP.NET Core
```
WebApplication.CreateBuilder    # .NET 6+ minimal API
builder.Services.               # Service registration
app.MapGet(                     # Minimal API route
[ApiController]                 # Controller attribute
[HttpGet]                       # HTTP method attribute
```

### Gin (Go)
```
gin.Default()        # Router initialization
gin.New()            # Router initialization
r.GET(               # Route definition
r.POST(              # Route definition
```

### FastAPI
```
FastAPI()            # App initialization
@app.get(            # Route decorator
@app.post(           # Route decorator
Depends(             # Dependency injection
```

### Actix-web (Rust)
```
HttpServer::new      # Server initialization
App::new()           # App builder
web::get()           # Route handler
web::post()          # Route handler
#[actix_web::main]   # Main macro
```

---

## 3. Port Probing Strategy

### Common Development Ports

| Port | Common Usage |
|------|-------------|
| 3000 | Node.js (Express, Next.js, React dev server) |
| 3001 | Secondary Node.js service |
| 4000 | Phoenix (Elixir), GraphQL dev servers |
| 4200 | Angular dev server |
| 5000 | Flask, ASP.NET Core |
| 5173 | Vite dev server |
| 5432 | PostgreSQL (do not probe — database, not HTTP) |
| 8000 | Django, FastAPI, PHP built-in server |
| 8080 | Java (Spring Boot, Tomcat), Go, general HTTP |
| 8443 | HTTPS variant of 8080 |
| 9000 | PHP-FPM, SonarQube |

### Probe Command

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:PORT/
```

### Response Interpretation

| HTTP Status | Interpretation |
|-------------|---------------|
| 200 | Server running, root endpoint accessible |
| 301, 302 | Server running, redirecting (likely to /login or HTTPS) |
| 400 | Server running, bad request (may need specific headers) |
| 401, 403 | Server running, authentication required |
| 404 | Server running, root not mapped but server responds |
| 405 | Server running, method not allowed on root |
| 500 | Server running but erroring (still scannable) |
| 000 / timeout | Connection refused or timeout — server not running |

### HTTPS Probing

For ports 443 and 8443, use:
```bash
curl -sk -o /dev/null -w "%{http_code}" --max-time 2 https://localhost:PORT/
```

The `-k` flag skips certificate verification (development self-signed certs).

---

## 4. Configuration File Locations

### Container and Orchestration

| File | Purpose | Security Relevance |
|------|---------|-------------------|
| `Dockerfile` | Container image definition | Base image vulnerabilities, running as root, exposed ports, secrets in layers |
| `docker-compose.yml` | Multi-container orchestration | Exposed ports, environment variables with secrets, network configuration |
| `.dockerignore` | Build context exclusions | Missing exclusions may leak .env, .git, node_modules into image |
| `kubernetes/*.yaml` | K8s manifests | RBAC, network policies, secret management, resource limits |
| `helm/` | Helm charts | Template injection, default values with secrets |

### CI/CD Pipelines

| File | Platform | Security Relevance |
|------|----------|-------------------|
| `.github/workflows/*.yml` | GitHub Actions | Secret handling, permissions, third-party action versions |
| `.gitlab-ci.yml` | GitLab CI | Variable exposure, shared runners, artifact security |
| `Jenkinsfile` | Jenkins | Script approval, credential binding, agent security |
| `.circleci/config.yml` | CircleCI | Context/secret management, orb versions |
| `.travis.yml` | Travis CI | Encrypted variables, deployment keys |
| `bitbucket-pipelines.yml` | Bitbucket | Pipeline variables, deployment permissions |
| `azure-pipelines.yml` | Azure DevOps | Service connections, variable groups |

### Secret and Environment Files

| File | Risk Level | Notes |
|------|------------|-------|
| `.env` | HIGH | Often contains database URLs, API keys, JWT secrets |
| `.env.local` | HIGH | Local overrides, frequently has real credentials |
| `.env.production` | CRITICAL | Production secrets — should never be in repo |
| `.env.example` / `.env.sample` | LOW | Template, but may contain default passwords |
| `credentials.json` | CRITICAL | Service account keys (GCP) |
| `service-account*.json` | CRITICAL | Cloud service account keys |
| `*.pem` / `*.key` | CRITICAL | Private keys |
| `.npmrc` / `.pypirc` | HIGH | Package registry tokens |
| `aws-credentials` / `~/.aws/credentials` | CRITICAL | AWS access keys |

### Cloud Infrastructure as Code

| Path | Tool | Security Relevance |
|------|------|-------------------|
| `*.tf` / `terraform/` | Terraform | IAM policies, security groups, encryption settings |
| `cloudformation/*.yaml` | CloudFormation | Resource policies, parameter defaults |
| `pulumi/` / `Pulumi.yaml` | Pulumi | Infrastructure security configuration |
| `cdk.json` / `lib/*.ts` | AWS CDK | Synthesized CloudFormation security |
| `serverless.yml` | Serverless Framework | Function permissions, API Gateway auth |
| `sam-template.yaml` | AWS SAM | Lambda security, API definitions |

### API Specifications

| File | Format | Security Relevance |
|------|--------|-------------------|
| `openapi.yaml` / `openapi.json` | OpenAPI 3.x | Endpoint inventory, auth schemes, input schemas |
| `swagger.yaml` / `swagger.json` | Swagger 2.0 | Legacy API specification |
| `schema.graphql` / `*.graphql` | GraphQL | Schema introspection, query complexity |
| `*.raml` | RAML | API definition |
| `*.proto` | Protocol Buffers | gRPC service definitions |
| `*.postman_collection.json` | Postman | API test collection (may contain auth tokens) |

---

## 5. Multi-Language / Polyglot Projects

Some projects use multiple languages. Detection strategy:

1. Check the repository root for all manifest files listed above
2. Check subdirectories (e.g., `frontend/package.json` + `backend/requirements.txt`)
3. Check for monorepo indicators:
   - `lerna.json` / `nx.json` / `turbo.json` — JavaScript monorepos
   - `packages/` / `apps/` / `services/` directories
   - Multiple manifest files in subdirectories
4. For each detected language, run the appropriate sub-skill scans
5. Note inter-service communication patterns (REST, gRPC, message queues) as additional attack surface
