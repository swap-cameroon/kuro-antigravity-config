# Docker and Container Security Hardening Checklist

This reference covers security checks for Dockerfiles, docker-compose.yml, and Kubernetes manifests.

---

## Dockerfile Checks

### 1. Running as Root (No USER Directive)

**What to look for:** Dockerfile without a `USER` directive, or `USER root` without switching to a non-root user before the final CMD/ENTRYPOINT.

**Why it matters:** Containers running as root have the same UID as the host root user. If an attacker escapes the container, they have root access to the host. Even within the container, root can modify system files, install packages, and access sensitive data.

**Severity:** High

**Detection pattern:**
- No `USER` directive at all in the Dockerfile
- `USER root` as the last USER directive before CMD/ENTRYPOINT
- `USER 0` (UID 0 = root)

**How to fix:**
```dockerfile
# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Switch to non-root user
USER appuser

CMD ["node", "server.js"]
```

---

### 2. Using `latest` Tag Instead of Pinned Versions

**What to look for:** `FROM image:latest` or `FROM image` (implicit latest).

**Why it matters:** The `latest` tag is mutable. Builds are not reproducible — the base image can change between builds, introducing vulnerabilities or breaking changes. Supply chain attacks can target popular images by pushing a compromised `latest` tag.

**Severity:** Medium

**Detection pattern:**
- `FROM <image>:latest`
- `FROM <image>` (no tag at all)
- Even named tags like `FROM node:18` should ideally use digest pinning for critical production images

**How to fix:**
```dockerfile
# Pin to specific version
FROM node:18.19.0-alpine3.19

# Or pin to digest for maximum reproducibility
FROM node@sha256:abc123...
```

---

### 3. Missing .dockerignore

**What to look for:** No `.dockerignore` file in the build context, or a `.dockerignore` that does not exclude sensitive files.

**Why it matters:** Without `.dockerignore`, the entire build context is sent to the Docker daemon. This can include `.git/` (full repository history with secrets), `.env` files, `node_modules`, private keys, and credentials.

**Severity:** High

**Detection pattern:**
- No `.dockerignore` file exists
- `.dockerignore` exists but does not exclude: `.git`, `.env`, `*.pem`, `*.key`, `node_modules`, `.npm`, `credentials.*`

**How to fix:**
```
# .dockerignore
.git
.gitignore
.env
.env.*
*.pem
*.key
*.p12
node_modules
.npm
npm-debug.log
credentials.*
secrets.*
*.secret
.DS_Store
```

---

### 4. Installing Unnecessary Packages

**What to look for:** `apt-get install` or `apk add` commands installing tools like `curl`, `wget`, `netcat`, `nmap`, `telnet`, `vim`, `ssh`, `sudo`, `gcc`, `make` in the final image.

**Why it matters:** Each unnecessary tool increases the attack surface. An attacker who gains access to the container can use `curl`/`wget` for data exfiltration, `netcat` for reverse shells, `ssh` for lateral movement, and compilers to build exploits.

**Severity:** Medium

**Detection pattern:**
- `RUN apt-get install -y curl wget netcat` (or similar) without a corresponding removal
- Packages installed that are only needed at build time remaining in the final image
- Not using `--no-install-recommends` with apt-get

**How to fix:**
```dockerfile
# Use multi-stage builds to separate build and runtime dependencies
FROM node:18-alpine AS builder
RUN apk add --no-cache python3 make g++
COPY . .
RUN npm ci --only=production

FROM node:18-alpine
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["node", "server.js"]
```

---

### 5. Using ADD Instead of COPY

**What to look for:** `ADD` instruction used for copying local files.

**Why it matters:** `ADD` has implicit behaviors that `COPY` does not: it auto-extracts tar archives and can fetch URLs. This can be exploited to download and execute malicious content. `ADD` makes the build less predictable and harder to audit.

**Severity:** Low

**Detection pattern:**
- `ADD ./src /app/src` (should be COPY)
- `ADD https://example.com/file.tar.gz /tmp/` (downloading URLs in Dockerfile)
- Any `ADD` that is not specifically used for tar extraction

**How to fix:**
```dockerfile
# Use COPY for local files
COPY ./src /app/src

# If you need to download files, use RUN with curl and verify checksums
RUN curl -fsSL https://example.com/file.tar.gz -o /tmp/file.tar.gz \
    && echo "expected_sha256  /tmp/file.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/file.tar.gz -C /app \
    && rm /tmp/file.tar.gz
```

---

### 6. Not Using Multi-Stage Builds

**What to look for:** Single-stage Dockerfile that installs build tools (compilers, build-essential, dev dependencies) that end up in the final image.

**Why it matters:** Build tools, source code, and development dependencies in the final image increase attack surface, image size, and expose implementation details. Compilers allow an attacker to build exploits inside the container.

**Severity:** Medium

**Detection pattern:**
- Single `FROM` instruction with build tools installed
- `npm install` (not `npm ci --only=production`)
- `pip install` with dev dependencies remaining
- `go build` without a separate runtime stage
- Presence of `.go`, `.ts`, `.java` source files in final image

**How to fix:**
```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server

# Runtime stage
FROM alpine:3.19
RUN adduser -D appuser
COPY --from=builder /app/server /app/server
USER appuser
CMD ["/app/server"]
```

---

### 7. Exposing Unnecessary Ports

**What to look for:** `EXPOSE` directives for ports that are not needed, or exposing debug/management ports.

**Why it matters:** Each exposed port is a potential entry point. Debug ports (9229 for Node.js, 5005 for Java), database ports (3306, 5432), and management ports (8080 for actuators) should not be exposed in production images.

**Severity:** Medium

**Detection pattern:**
- `EXPOSE 22` (SSH — containers should not run SSH)
- `EXPOSE 9229` (Node.js debugger)
- `EXPOSE 5005` (Java debug)
- `EXPOSE 3306` / `EXPOSE 5432` / `EXPOSE 27017` (databases in app containers)
- Multiple `EXPOSE` directives without clear justification

**How to fix:**
```dockerfile
# Only expose the port your application listens on
EXPOSE 8080
```

---

### 8. Missing or Improper HEALTHCHECK

**What to look for:** No `HEALTHCHECK` directive, or a `HEALTHCHECK` that reveals sensitive information.

**Why it matters:** Without HEALTHCHECK, Docker and orchestrators cannot determine if the application is actually healthy. A container may be running but the application crashed. However, health check endpoints should not expose internal state or sensitive data.

**Severity:** Low

**Detection pattern:**
- No `HEALTHCHECK` instruction
- `HEALTHCHECK NONE` (explicitly disabled)
- Health check hitting a verbose debug endpoint
- Health check with very long intervals or excessive retries

**How to fix:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
```

---

### 9. Inefficient Layer Ordering (COPY Before Dependency Install)

**What to look for:** Copying all source files before running dependency installation.

**Why it matters:** Docker caches layers. If source code is copied before `npm install` / `pip install`, every code change invalidates the dependency cache, causing slow builds. While primarily a performance issue, slow builds discourage frequent rebuilds with security patches.

**Severity:** Low

**Detection pattern:**
- `COPY . .` followed by `RUN npm install`
- `COPY . .` followed by `RUN pip install -r requirements.txt`

**How to fix:**
```dockerfile
# Copy dependency files first
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Then copy source code
COPY . .
```

---

### 10. Storing Secrets in ENV or ARG

**What to look for:** `ENV` or `ARG` instructions containing secrets, passwords, API keys, or tokens.

**Why it matters:** `ENV` values persist in the image layers and are visible via `docker inspect`. `ARG` values are recorded in the build history. Anyone with access to the image can extract these secrets. Even if overridden at runtime, the default values remain in the image.

**Severity:** Critical

**Detection pattern:**
- `ENV DATABASE_PASSWORD=...`
- `ENV API_KEY=...`
- `ENV SECRET_KEY=...`
- `ARG DB_PASSWORD`
- Any ENV/ARG with variable names containing: SECRET, PASSWORD, KEY, TOKEN, CREDENTIAL, AUTH, PRIVATE

**How to fix:**
```dockerfile
# Do NOT put secrets in Dockerfile
# Instead, pass at runtime:
# docker run -e DATABASE_PASSWORD="$(vault read -field=password secret/db)" myapp

# Or use Docker secrets (Swarm) / Kubernetes secrets
# Or use build-time secrets with BuildKit:
RUN --mount=type=secret,id=db_password cat /run/secrets/db_password
```

---

### 11. Not Setting WORKDIR

**What to look for:** No `WORKDIR` directive, operating in the root filesystem `/`.

**Why it matters:** Without WORKDIR, files are copied to and executed from the root directory. This clutters the filesystem, can overwrite system files, and makes the container harder to debug and secure.

**Severity:** Low

**Detection pattern:**
- No `WORKDIR` instruction
- `COPY . /` (copying to root)
- Relative paths used without a preceding WORKDIR

**How to fix:**
```dockerfile
WORKDIR /app
COPY . .
```

---

### 12. Shell Form vs Exec Form for CMD/ENTRYPOINT

**What to look for:** `CMD command arg1 arg2` (shell form) instead of `CMD ["command", "arg1", "arg2"]` (exec form).

**Why it matters:** Shell form wraps the command in `/bin/sh -c`, which means the process does not receive signals properly (SIGTERM for graceful shutdown). It also introduces a shell injection vector if arguments are interpolated. The application runs as a child of the shell process rather than PID 1.

**Severity:** Low

**Detection pattern:**
- `CMD node server.js` (shell form)
- `ENTRYPOINT /start.sh` (shell form)
- `CMD npm start` (shell form, also problematic because npm does not forward signals)

**How to fix:**
```dockerfile
# Use exec form
CMD ["node", "server.js"]
ENTRYPOINT ["/start.sh"]

# Avoid npm start — run node directly
CMD ["node", "server.js"]
```

---

## docker-compose.yml Checks

### 13. Privileged Mode Enabled

**What to look for:** `privileged: true` on any service.

**Why it matters:** Privileged mode gives the container almost all capabilities of the host. The container can access all host devices, load kernel modules, modify kernel parameters, and trivially escape to the host. This effectively removes all container isolation.

**Severity:** Critical

**Detection pattern:**
```yaml
services:
  app:
    privileged: true
```

**How to fix:**
```yaml
services:
  app:
    # Remove privileged: true entirely
    # If specific capabilities are needed, use cap_add with only what's required:
    cap_add:
      - NET_BIND_SERVICE
    cap_drop:
      - ALL
```

---

### 14. Host Network Mode

**What to look for:** `network_mode: "host"` on any service.

**Why it matters:** Host network mode removes network isolation. The container shares the host's network namespace, can access all host network interfaces, and can bind to any port. This bypasses network-based security controls and firewall rules.

**Severity:** High

**Detection pattern:**
```yaml
services:
  app:
    network_mode: "host"
```

**How to fix:**
```yaml
services:
  app:
    # Use bridge network (default) or custom networks
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

---

### 15. Excessive Volume Mounts

**What to look for:** Mounting the host root filesystem, Docker socket, or sensitive host directories.

**Why it matters:** Mounting `/` gives the container full host filesystem access. Mounting `/var/run/docker.sock` allows the container to control Docker — creating privileged containers, accessing other containers, and escaping to the host. Mounting `/etc`, `/proc`, or `/sys` exposes host configuration and kernel parameters.

**Severity:** Critical

**Detection pattern:**
```yaml
volumes:
  - /:/host                        # Host root — critical
  - /var/run/docker.sock:/var/run/docker.sock  # Docker socket — critical
  - /etc:/etc                      # Host config — high
  - /proc:/host/proc               # Kernel info — high
  - ~/.ssh:/root/.ssh              # SSH keys — critical
```

**How to fix:**
```yaml
volumes:
  # Mount only specific directories that are needed
  - ./data:/app/data
  # Use named volumes for data persistence
  - db-data:/var/lib/postgresql/data
```

---

### 16. Missing Resource Limits

**What to look for:** Services without `deploy.resources.limits` or `mem_limit`/`cpus` settings.

**Why it matters:** Without resource limits, a single container can consume all host memory and CPU. This enables denial-of-service attacks and resource exhaustion. A memory leak or fork bomb in one container can crash the entire host.

**Severity:** Medium

**Detection pattern:**
```yaml
services:
  app:
    image: myapp
    # No deploy.resources section
```

**How to fix:**
```yaml
services:
  app:
    image: myapp
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.50'
        reservations:
          memory: 256M
          cpus: '0.25'
```

---

### 17. Missing Restart Policies

**What to look for:** No `restart` policy defined for services.

**Why it matters:** Without a restart policy, if the application crashes it stays down. While not directly a security issue, availability is part of the security triad (CIA). Crashed services may leave data in an inconsistent state. However, `restart: always` can mask crash loops that indicate an attack.

**Severity:** Low

**Detection pattern:**
```yaml
services:
  app:
    image: myapp
    # No restart policy
```

**How to fix:**
```yaml
services:
  app:
    restart: unless-stopped
    # Or for production: restart: on-failure:5
```

---

### 18. Hardcoded Secrets in Environment Section

**What to look for:** Passwords, API keys, tokens, and secrets defined directly in the environment section of docker-compose.yml.

**Why it matters:** docker-compose.yml is typically committed to version control. Secrets in this file are visible to anyone with repository access. They persist in git history even if removed later.

**Severity:** Critical

**Detection pattern:**
```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD: mysecretpassword  # Hardcoded secret
      API_KEY: sk-abc123                   # Hardcoded secret
```

**How to fix:**
```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Reference env var
    env_file:
      - .env  # Use env file (must be in .gitignore)
    secrets:
      - db_password  # Or use Docker secrets

secrets:
  db_password:
    external: true
```

---

### 19. Exposed Ports on 0.0.0.0 vs 127.0.0.1

**What to look for:** Ports published without binding to localhost, making them accessible on all network interfaces.

**Why it matters:** By default, `ports: "3306:3306"` binds to `0.0.0.0`, exposing the port to the entire network. Internal services like databases, caches, and admin panels should only be accessible from localhost or within the Docker network.

**Severity:** High

**Detection pattern:**
```yaml
ports:
  - "3306:3306"     # Exposed on all interfaces
  - "6379:6379"     # Redis exposed to network
  - "9200:9200"     # Elasticsearch exposed
  - "8080:8080"     # Unless this is the public-facing port
```

**How to fix:**
```yaml
ports:
  # Bind to localhost only for internal services
  - "127.0.0.1:3306:3306"
  - "127.0.0.1:6379:6379"
  # Only the public-facing service should be on 0.0.0.0
  - "80:8080"
```

---

### 20. Missing Read-Only Filesystem

**What to look for:** No `read_only: true` on services that do not need to write to the filesystem.

**Why it matters:** A read-only filesystem prevents an attacker from writing malicious scripts, web shells, or modified binaries inside the container. It limits post-exploitation capabilities significantly.

**Severity:** Medium

**Detection pattern:**
```yaml
services:
  app:
    image: myapp
    # No read_only setting
```

**How to fix:**
```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    volumes:
      - app-data:/app/data  # Only writable where needed
```

---

### 21. Missing security_opt (no-new-privileges)

**What to look for:** No `security_opt` setting to prevent privilege escalation.

**Why it matters:** The `no-new-privileges` flag prevents processes inside the container from gaining additional privileges via setuid binaries, setgid, or other mechanisms. Without it, an attacker could escalate from a low-privilege user to root within the container.

**Severity:** Medium

**Detection pattern:**
```yaml
services:
  app:
    image: myapp
    # No security_opt section
```

**How to fix:**
```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

---

## Kubernetes Manifest Checks

### 22. Pod Running as Root / Privileged

**What to look for:** Pods or containers without `securityContext` restricting root, or with `privileged: true`.

**Why it matters:** Same as Docker privileged mode — a privileged pod can access host devices, escape the container, and compromise the node. Running as root (UID 0) gives unnecessary capabilities even without privileged mode.

**Severity:** Critical (privileged), High (running as root)

**Detection pattern:**
```yaml
spec:
  containers:
    - name: app
      securityContext:
        privileged: true           # Critical
        runAsUser: 0               # High
      # Or no securityContext at all (defaults to root)
```

**How to fix:**
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
    - name: app
      securityContext:
        privileged: false
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

---

### 23. Missing securityContext

**What to look for:** Pods or containers with no `securityContext` at pod or container level.

**Why it matters:** Without securityContext, Kubernetes uses defaults which are permissive: runs as root, allows privilege escalation, has a writable filesystem, and retains all Linux capabilities. Every production workload should have an explicit securityContext.

**Severity:** High

**Detection pattern:**
- No `securityContext` field in pod spec
- No `securityContext` field in container spec
- Missing key fields: `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation`, `capabilities.drop`

**How to fix:**
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
```

---

### 24. Missing NetworkPolicy

**What to look for:** No NetworkPolicy resources in the project, or pods without matching NetworkPolicy.

**Why it matters:** Without NetworkPolicy, all pods can communicate with all other pods in the cluster by default. If one pod is compromised, the attacker has unrestricted lateral movement to databases, internal APIs, and other services.

**Severity:** High

**Detection pattern:**
- No files with `kind: NetworkPolicy`
- Pods in namespaces without any NetworkPolicy
- NetworkPolicy with overly broad selectors (empty podSelector = all pods)

**How to fix:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              role: database
      ports:
        - port: 5432
```

---

### 25. Using Default Namespace

**What to look for:** Resources deployed to the `default` namespace (no `namespace` field or `namespace: default`).

**Why it matters:** The default namespace is shared by all users and has no RBAC restrictions by default. Resources in the default namespace are harder to manage with NetworkPolicies and RBAC. It also makes it easy to accidentally expose or access resources.

**Severity:** Medium

**Detection pattern:**
- No `namespace` field in metadata
- `namespace: default`

**How to fix:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-production
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp-production
```

---

### 26. Missing Resource Requests and Limits

**What to look for:** Containers without `resources.requests` and `resources.limits`.

**Why it matters:** Without resource limits, a pod can consume all node resources, causing other pods to be evicted or the node to become unresponsive. This enables denial-of-service. Without requests, the scheduler cannot make informed placement decisions.

**Severity:** Medium

**Detection pattern:**
```yaml
spec:
  containers:
    - name: app
      # No resources section
```

**How to fix:**
```yaml
spec:
  containers:
    - name: app
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "512Mi"
          cpu: "500m"
```

---

### 27. Service Account with Excessive Permissions

**What to look for:** Pods using the default service account, or service accounts with cluster-admin or wildcard permissions.

**Why it matters:** The default service account in each namespace has a token mounted into every pod. If a pod is compromised, the attacker can use this token to interact with the Kubernetes API. Overly permissive RBAC allows the attacker to read secrets, create pods, or escalate privileges.

**Severity:** High

**Detection pattern:**
- No `serviceAccountName` specified (uses default)
- `automountServiceAccountToken` not set to `false`
- ClusterRoleBinding to `cluster-admin`
- Roles with `verbs: ["*"]` or `resources: ["*"]`

**How to fix:**
```yaml
spec:
  serviceAccountName: myapp-sa
  automountServiceAccountToken: false  # If API access not needed
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: myapp-role
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]  # Only what's needed
```

---

### 28. Missing PodDisruptionBudget

**What to look for:** Deployments without a corresponding PodDisruptionBudget.

**Why it matters:** Without a PDB, all replicas of a deployment can be evicted simultaneously during node maintenance or cluster autoscaling. This causes downtime. While primarily an availability concern, availability is a security property.

**Severity:** Low

**Detection pattern:**
- Deployment exists but no PodDisruptionBudget with matching selector

**How to fix:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: myapp
```

---

### 29. Secrets in Plain ConfigMaps

**What to look for:** ConfigMap resources containing passwords, API keys, tokens, or other secret values.

**Why it matters:** ConfigMaps are not encrypted and are not subject to RBAC restrictions on Secrets. They may be logged, cached, and visible to anyone with read access to the namespace. Secrets should use the Secret resource type (and ideally be encrypted at rest with KMS).

**Severity:** High

**Detection pattern:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_PASSWORD: "mypassword"   # Secret in ConfigMap
  API_KEY: "sk-abc123"              # Secret in ConfigMap
```

**How to fix:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  DATABASE_PASSWORD: bXlwYXNzd29yZA==  # base64 encoded (NOT encryption!)
---
# Better: use external-secrets or sealed-secrets for actual encryption
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: app-secrets
  data:
    - secretKey: DATABASE_PASSWORD
      remoteRef:
        key: secret/data/myapp
        property: db_password
```
