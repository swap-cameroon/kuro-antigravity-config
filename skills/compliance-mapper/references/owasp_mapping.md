# OWASP Top 10 (2021) Mapping Reference

This reference maps OWASP Top 10 (2021) categories to CWEs, vulnerability patterns, and finding keywords for automated classification of security findings.

---

## A01:2021 -- Broken Access Control

**Description:** Access control enforces policy such that users cannot act outside their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of data, or performing a business function outside the user's limits.

**Associated CWEs:**
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
- CWE-201: Insertion of Sensitive Information Into Sent Data
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)
- CWE-23: Relative Path Traversal
- CWE-35: Path Traversal
- CWE-59: Improper Link Resolution Before File Access
- CWE-276: Incorrect Default Permissions
- CWE-284: Improper Access Control
- CWE-285: Improper Authorization
- CWE-352: Cross-Site Request Forgery (CSRF)
- CWE-359: Exposure of Private Personal Information to an Unauthorized Actor
- CWE-377: Insecure Temporary File
- CWE-402: Transmission of Private Resources into a New Sphere
- CWE-425: Direct Request (Forced Browsing)
- CWE-441: Unintended Proxy or Intermediary
- CWE-497: Exposure of Sensitive System Information to an Unauthorized Actor
- CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory
- CWE-639: Authorization Bypass Through User-Controlled Key (IDOR)
- CWE-651: Exposure of WSDL File Containing Sensitive Information
- CWE-668: Exposure of Resource to Wrong Sphere
- CWE-706: Use of Incorrectly-Resolved Name or Reference
- CWE-862: Missing Authorization
- CWE-863: Incorrect Authorization
- CWE-913: Improper Control of Dynamically-Managed Code Resources
- CWE-922: Insecure Storage of Sensitive Information

**Common Vulnerability Patterns:**
- Insecure Direct Object Reference (IDOR): manipulating IDs to access other users' data
- Privilege escalation: accessing admin functionality as a regular user
- Path traversal: accessing files outside the intended directory using ../ sequences
- CORS misconfiguration: overly permissive cross-origin resource sharing
- Missing function-level access control: no authorization check on sensitive endpoints
- CSRF: performing state-changing actions without verifying request origin
- Directory listing: exposing file system contents via web server
- Forced browsing: accessing pages not linked but directly accessible
- JWT manipulation: modifying token claims to change user identity or role
- Metadata manipulation: tampering with hidden fields, cookies, or tokens

**Finding Keywords:**
access control, authorization, privilege, traversal, IDOR, CORS, CSRF, directory listing, forced browsing, path traversal, permission, role, ACL, JWT, token manipulation, insecure direct object, bypass, escalation, unauthorized

**How to Identify from Findings:**
- SAST findings related to missing authorization checks or role validation
- DAST findings showing accessible endpoints without authentication
- Config review findings about permissive CORS or missing CSRF tokens
- API testing findings showing IDOR or broken object-level authorization

---

## A02:2021 -- Cryptographic Failures

**Description:** Failures related to cryptography (or lack thereof) which often lead to exposure of sensitive data. This was previously known as "Sensitive Data Exposure" which was more of a symptom than a root cause.

**Associated CWEs:**
- CWE-261: Weak Encoding for Password
- CWE-296: Improper Following of a Certificate's Chain of Trust
- CWE-310: Cryptographic Issues
- CWE-319: Cleartext Transmission of Sensitive Information
- CWE-321: Use of Hard-coded Cryptographic Key
- CWE-322: Key Exchange without Entity Authentication
- CWE-323: Reusing a Nonce, Key Pair in Encryption
- CWE-324: Use of a Key Past its Expiration Date
- CWE-325: Missing Cryptographic Step
- CWE-326: Inadequate Encryption Strength
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- CWE-328: Use of Weak Hash
- CWE-329: Generation of Predictable IV with CBC Mode
- CWE-330: Use of Insufficiently Random Values
- CWE-331: Insufficient Entropy
- CWE-335: Incorrect Usage of Seeds in Pseudo-Random Number Generator
- CWE-336: Same Seed in Pseudo-Random Number Generator
- CWE-338: Use of Cryptographically Weak PRNG
- CWE-311: Missing Encryption of Sensitive Data
- CWE-312: Cleartext Storage of Sensitive Information
- CWE-259: Use of Hard-coded Password
- CWE-523: Unprotected Transport of Credentials
- CWE-757: Selection of Less-Secure Algorithm During Negotiation
- CWE-759: Use of a One-Way Hash without a Salt
- CWE-760: Use of a One-Way Hash with a Predictable Salt
- CWE-780: Use of RSA Algorithm without OAEP
- CWE-818: Insufficient Transport Layer Security

**Common Vulnerability Patterns:**
- Weak hash algorithms: MD5, SHA1 used for passwords or integrity
- Weak cipher algorithms: DES, 3DES, RC4, Blowfish with small keys
- Hardcoded cryptographic keys or passwords in source code
- Plaintext storage of sensitive data (passwords, PII, financial data)
- Missing TLS/HTTPS: sensitive data transmitted in cleartext
- Predictable tokens or session IDs generated with weak randomness
- Self-signed or expired certificates in production
- Missing certificate validation
- ECB mode usage for block ciphers
- Insufficient key length (RSA < 2048, AES < 128)

**Finding Keywords:**
crypto, hash, cipher, encryption, plaintext, certificate, TLS, SSL, key, token, MD5, SHA1, DES, RC4, random, entropy, salt, HTTPS, cleartext, password storage, PRNG, IV, nonce, key management

**How to Identify from Findings:**
- SAST findings about weak hash or cipher usage
- Secrets scanner findings about hardcoded keys
- Config review findings about missing TLS or weak cipher suites
- DAST findings about cleartext transmission or weak certificates

---

## A03:2021 -- Injection

**Description:** An application is vulnerable to injection when user-supplied data is not validated, filtered, or sanitized, and is sent to an interpreter as part of a command or query.

**Associated CWEs:**
- CWE-20: Improper Input Validation
- CWE-73: External Control of File Name or Path
- CWE-74: Improper Neutralization of Special Elements in Output Used by a Downstream Component
- CWE-75: Failure to Sanitize Special Elements into a Different Plane
- CWE-77: Improper Neutralization of Special Elements Used in a Command (Command Injection)
- CWE-78: Improper Neutralization of Special Elements Used in an OS Command (OS Command Injection)
- CWE-79: Improper Neutralization of Input During Web Page Generation (XSS)
- CWE-80: Improper Neutralization of Script-Related HTML Tags
- CWE-83: Improper Neutralization of Script in Attributes
- CWE-87: Improper Neutralization of Alternate XSS Syntax
- CWE-88: Improper Neutralization of Argument Delimiters in a Command
- CWE-89: Improper Neutralization of Special Elements Used in an SQL Command (SQL Injection)
- CWE-90: Improper Neutralization of Special Elements Used in an LDAP Query (LDAP Injection)
- CWE-91: XML Injection
- CWE-93: Improper Neutralization of CRLF Sequences (CRLF Injection)
- CWE-94: Improper Control of Generation of Code (Code Injection)
- CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code (Eval Injection)
- CWE-96: Improper Neutralization of Directives in Statically Saved Code
- CWE-97: Improper Neutralization of Server-Side Includes (SSI)
- CWE-98: Improper Control of Filename for Include/Require Statement
- CWE-99: Improper Control of Resource Identifiers
- CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers (HTTP Response Splitting)
- CWE-116: Improper Encoding or Escaping of Output
- CWE-138: Improper Neutralization of Special Elements
- CWE-564: SQL Injection: Hibernate
- CWE-611: Improper Restriction of XML External Entity Reference (XXE)
- CWE-917: Improper Neutralization of Special Elements Used in an Expression Language Statement (Expression Language Injection)
- CWE-1236: Improper Neutralization of Formula Elements in a CSV File

**Common Vulnerability Patterns:**
- SQL injection: user input concatenated into SQL queries
- Cross-Site Scripting (XSS): reflected, stored, or DOM-based
- Command injection: user input passed to system shell commands
- LDAP injection: user input in LDAP queries
- XXE: XML parser processes external entity references
- Server-Side Template Injection (SSTI): user input in template engines
- Code injection: user input evaluated as code (eval, exec)
- NoSQL injection: user input in NoSQL query operators
- Header injection / CRLF injection: user input in HTTP headers
- Expression Language injection: user input in EL expressions

**Finding Keywords:**
injection, SQLi, XSS, command, template, XML, eval, exec, LDAP, NoSQL, CRLF, header injection, script, sanitize, escape, parameterized, prepared statement, input validation, XXE, SSTI, expression language

**How to Identify from Findings:**
- SAST findings about string concatenation in queries or commands
- DAST findings about reflected/stored XSS or SQL injection
- API testing findings about injection in API parameters
- Any finding mentioning unsanitized user input reaching an interpreter

---

## A04:2021 -- Insecure Design

**Description:** Insecure design is a broad category representing different weaknesses expressed as missing or ineffective control design. It focuses on risks related to design and architectural flaws, calling for more use of threat modeling, secure design patterns, and reference architectures.

**Associated CWEs:**
- CWE-73: External Control of File Name or Path
- CWE-183: Permissive List of Allowed Inputs
- CWE-209: Generation of Error Message Containing Sensitive Information
- CWE-213: Exposure of Sensitive Information Due to Incompatible Policies
- CWE-235: Improper Handling of Extra Parameters
- CWE-256: Plaintext Storage of a Password
- CWE-266: Incorrect Privilege Assignment
- CWE-269: Improper Privilege Management
- CWE-280: Improper Handling of Insufficient Permissions
- CWE-311: Missing Encryption of Sensitive Data
- CWE-312: Cleartext Storage of Sensitive Information
- CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition
- CWE-434: Unrestricted Upload of File with Dangerous Type
- CWE-444: Inconsistent Interpretation of HTTP Requests
- CWE-501: Trust Boundary Violation
- CWE-522: Insufficiently Protected Credentials
- CWE-602: Client-Side Enforcement of Server-Side Security
- CWE-640: Weak Password Recovery Mechanism for Forgotten Password
- CWE-656: Reliance on Security Through Obscurity
- CWE-799: Improper Control of Interaction Frequency
- CWE-840: Business Logic Errors

**Common Vulnerability Patterns:**
- Missing rate limiting on sensitive operations
- No brute-force protection on authentication
- Predictable or guessable OTP / reset tokens
- Race conditions (TOCTOU)
- Missing business logic validation
- No CAPTCHA on forms susceptible to automation
- Client-side-only security controls
- Missing input length limits
- Unrestricted file upload without type validation
- Lack of separation of duties

**Finding Keywords:**
design, rate limit, brute force, OTP, race condition, TOCTOU, business logic, upload, file type, client-side, trust boundary, password recovery, frequency, automation, CAPTCHA, threat model

**How to Identify from Findings:**
- Config review findings about missing rate limiting
- DAST findings about unrestricted operations
- API testing findings about missing business logic validation
- Any architectural or design-level weakness

---

## A05:2021 -- Security Misconfiguration

**Description:** The application might be vulnerable if it is missing appropriate security hardening, has unnecessary features enabled, has default accounts and passwords, or uses overly verbose error handling.

**Associated CWEs:**
- CWE-2: Environment
- CWE-11: ASP.NET Misconfiguration
- CWE-13: ASP.NET Misconfiguration: Password in Configuration File
- CWE-15: External Control of System or Configuration Setting
- CWE-16: Configuration
- CWE-260: Password in Configuration File
- CWE-315: Cleartext Storage of Sensitive Information in a Cookie
- CWE-520: .NET Misconfiguration: Use of Impersonation
- CWE-526: Exposure of Sensitive Information Through Environmental Variables
- CWE-537: Java Runtime Error Message Containing Sensitive Information
- CWE-541: Inclusion of Sensitive Information in an Include File
- CWE-547: Use of Hard-coded, Security-relevant Constants
- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute
- CWE-756: Missing Custom Error Page
- CWE-776: Improper Restriction of Recursive Entity References in DTDs
- CWE-942: Permissive Cross-domain Policy with Untrusted Domains
- CWE-1004: Sensitive Cookie Without 'HttpOnly' Flag
- CWE-1032: OWASP Top Ten 2017 Category A6 - Security Misconfiguration
- CWE-388: Error Handling
- CWE-489: Active Debug Code
- CWE-497: Exposure of Sensitive System Information to an Unauthorized Actor

**Common Vulnerability Patterns:**
- Debug mode enabled in production
- Default credentials left unchanged
- Unnecessary features, services, or ports enabled
- Missing security headers (CSP, X-Frame-Options, HSTS, etc.)
- Verbose error messages exposing stack traces or internal details
- Exposed admin panels or management interfaces
- Directory listing enabled on web server
- Unpatched or misconfigured cloud storage (S3 buckets, etc.)
- XML parser not configured to prevent XXE
- Missing cookie security flags (Secure, HttpOnly, SameSite)
- CORS wildcard or overly permissive configuration
- Unnecessary HTTP methods enabled (TRACE, PUT, DELETE)

**Finding Keywords:**
config, misconfiguration, debug, default, header, stack trace, verbose, error, exposed, admin panel, directory listing, cookie, HSTS, CSP, X-Frame-Options, security header, production, environment, XML parser, cloud, S3, permissions

**How to Identify from Findings:**
- Config review findings about missing headers or insecure settings
- DAST findings about information leakage or debug pages
- Secrets scanner findings about credentials in config files
- Any finding about default or insecure configuration

---

## A06:2021 -- Vulnerable and Outdated Components

**Description:** Components such as libraries, frameworks, and software modules run with the same privileges as the application. If a vulnerable component is exploited, it can cause serious data loss or server takeover.

**Associated CWEs:**
- CWE-937: Using Components with Known Vulnerabilities (OWASP)
- CWE-1035: Using Vulnerable Third-Party Software (OWASP)
- CWE-1104: Use of Unmaintained Third-Party Components

**Common Vulnerability Patterns:**
- Known CVEs in direct or transitive dependencies
- Outdated framework versions with known security patches available
- End-of-life components no longer receiving security updates
- Unpatched libraries with published exploits
- Components with known malware or supply chain compromises
- Using alpha/beta versions in production

**Finding Keywords:**
CVE, dependency, outdated, component, version, vulnerability, library, package, framework, end-of-life, EOL, deprecated, upgrade, patch, supply chain, npm, pip, maven, nuget, gem, cargo

**How to Identify from Findings:**
- Dependency audit findings about vulnerable packages
- Any finding referencing a specific CVE number
- Findings about outdated or unmaintained dependencies

---

## A07:2021 -- Identification and Authentication Failures

**Description:** Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks.

**Associated CWEs:**
- CWE-255: Credentials Management Errors
- CWE-259: Use of Hard-coded Password
- CWE-287: Improper Authentication
- CWE-288: Authentication Bypass Using an Alternate Path or Channel
- CWE-290: Authentication Bypass by Spoofing
- CWE-294: Authentication Bypass by Capture-replay
- CWE-295: Improper Certificate Validation
- CWE-297: Improper Validation of Certificate with Host Mismatch
- CWE-300: Channel Accessible by Non-Endpoint
- CWE-302: Authentication Bypass by Assumed-Immutable Data
- CWE-304: Missing Critical Step in Authentication
- CWE-306: Missing Authentication for Critical Function
- CWE-307: Improper Restriction of Excessive Authentication Attempts
- CWE-346: Origin Validation Error
- CWE-384: Session Fixation
- CWE-521: Weak Password Requirements
- CWE-613: Insufficient Session Expiration
- CWE-620: Unverified Password Change
- CWE-640: Weak Password Recovery Mechanism for Forgotten Password
- CWE-798: Use of Hard-coded Credentials

**Common Vulnerability Patterns:**
- Weak passwords allowed (no complexity requirements)
- No rate limiting on login attempts
- Session fixation (session ID not rotated after login)
- Long-lived tokens or sessions that never expire
- Credential stuffing possible (no detection or prevention)
- Predictable session IDs
- Missing multi-factor authentication on sensitive operations
- No account lockout after failed attempts
- Password recovery via security questions only
- Credentials transmitted in URL parameters

**Finding Keywords:**
authentication, login, password, session, token, JWT, credential, brute force, lockout, MFA, two-factor, 2FA, session fixation, session expiration, password policy, password recovery, remember me, cookie, OAuth

**How to Identify from Findings:**
- Config review findings about authentication settings
- DAST findings about login page weaknesses
- SAST findings about hardcoded credentials
- Secrets scanner findings about exposed credentials
- API testing findings about missing authentication

---

## A08:2021 -- Software and Data Integrity Failures

**Description:** Software and data integrity failures relate to code and infrastructure that does not protect against integrity violations. This includes insecure deserialization, use of software from untrusted sources, and CI/CD pipelines without integrity verification.

**Associated CWEs:**
- CWE-345: Insufficient Verification of Data Authenticity
- CWE-346: Origin Validation Error
- CWE-353: Missing Support for Integrity Check
- CWE-426: Untrusted Search Path
- CWE-494: Download of Code Without Integrity Check
- CWE-502: Deserialization of Untrusted Data
- CWE-565: Reliance on Cookies without Validation and Integrity Checking
- CWE-784: Reliance on Cookies without Validation and Integrity Checking in a Security Decision
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere
- CWE-830: Inclusion of Web Functionality from an Untrusted Source
- CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes (Mass Assignment)

**Common Vulnerability Patterns:**
- Insecure deserialization of untrusted data
- Missing code signing or integrity verification on updates
- CI/CD pipeline vulnerabilities (poisoned pipelines, missing approvals)
- Prototype pollution in JavaScript
- Mass assignment allowing modification of protected fields
- Unsigned software updates or packages
- Missing subresource integrity (SRI) on CDN resources
- Webhook endpoints without signature verification
- Auto-update mechanisms without integrity checks

**Finding Keywords:**
integrity, deserialization, prototype pollution, mass assignment, CI/CD, pipeline, signature, checksum, webhook, SRI, subresource, code signing, update, package, CDN, pickle, yaml.load, unserialize, ObjectInputStream

**How to Identify from Findings:**
- SAST findings about unsafe deserialization calls
- Config review findings about CI/CD pipeline security
- Dependency audit findings about missing integrity checks
- API testing findings about mass assignment vulnerabilities

---

## A09:2021 -- Security Logging and Monitoring Failures

**Description:** Without logging and monitoring, breaches cannot be detected. Insufficient logging, detection, monitoring, and active response occurs any time security-critical events are not logged or alerts are not triggered.

**Associated CWEs:**
- CWE-117: Improper Output Neutralization for Logs
- CWE-223: Omission of Security-relevant Information
- CWE-532: Insertion of Sensitive Information into Log File
- CWE-778: Insufficient Logging

**Common Vulnerability Patterns:**
- Missing audit logging for authentication failures
- No logging for sensitive operations (data access, admin actions)
- Logs accessible without authentication
- Log injection (unsanitized user input in log entries)
- Sensitive data written to logs (passwords, tokens, PII)
- No alerting on suspicious activity patterns
- Logs not centralized or easily searchable
- Insufficient log retention
- No monitoring for anomalous behavior
- Missing correlation between log sources

**Finding Keywords:**
logging, monitoring, audit, log, alert, detection, SIEM, log injection, log file, sensitive data in logs, audit trail, event logging, security event, incident detection, log rotation, log retention

**How to Identify from Findings:**
- Config review findings about missing logging configuration
- SAST findings about sensitive data in log statements
- Any finding noting absence of security event logging
- Findings about log injection vulnerabilities

---

## A10:2021 -- Server-Side Request Forgery (SSRF)

**Description:** SSRF flaws occur whenever a web application fetches a remote resource without validating the user-supplied URL. It allows an attacker to coerce the application to send a crafted request to an unexpected destination.

**Associated CWEs:**
- CWE-918: Server-Side Request Forgery (SSRF)

**Common Vulnerability Patterns:**
- Unvalidated URL fetch: application fetches user-supplied URLs without allowlist
- Open proxy: application can be used to proxy requests to internal services
- SSRF via file import: importing files from user-controlled URLs
- SSRF via webhook: webhook URLs pointing to internal infrastructure
- DNS rebinding: bypassing SSRF protections via DNS resolution tricks
- Internal network scanning: using SSRF to enumerate internal hosts and ports
- Cloud metadata access: accessing cloud provider metadata endpoints (169.254.169.254)
- PDF/image rendering SSRF: URL inclusion in rendered documents

**Finding Keywords:**
SSRF, fetch, proxy, URL, internal, metadata, request forgery, webhook, redirect, DNS rebinding, cloud metadata, file import, URL validation, allowlist, blocklist, localhost, 127.0.0.1, 169.254

**How to Identify from Findings:**
- SAST findings about unvalidated URL usage in HTTP client calls
- DAST findings about SSRF in URL parameters
- API testing findings about URL-based parameters that fetch resources
- Any finding about fetching resources from user-controlled URLs
