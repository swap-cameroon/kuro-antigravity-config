# NIST SP 800-53 Rev 5 and PCI DSS v4.0 Mapping Reference

This reference maps NIST and PCI DSS controls to common vulnerability types for compliance classification of security findings.

---

## NIST SP 800-53 Rev 5 Controls

### AC -- Access Control

**AC-2: Account Management**
- Vulnerability types: orphaned accounts, shared accounts, excessive privileges
- Finding patterns: default accounts not disabled, no account review process
- Related CWEs: CWE-284, CWE-269, CWE-276

**AC-3: Access Enforcement**
- Vulnerability types: IDOR, missing authorization, broken access control
- Finding patterns: endpoints accessible without proper authorization checks, horizontal/vertical privilege escalation
- Related CWEs: CWE-284, CWE-285, CWE-639, CWE-862, CWE-863
- OWASP: A01:2021

**AC-4: Information Flow Enforcement**
- Vulnerability types: data leakage between security domains, improper CORS
- Finding patterns: cross-origin data access, information disclosure across trust boundaries
- Related CWEs: CWE-200, CWE-497

**AC-6: Least Privilege**
- Vulnerability types: excessive permissions, privilege escalation
- Finding patterns: application running as root, overly permissive file permissions, unnecessary admin access
- Related CWEs: CWE-250, CWE-269, CWE-276
- OWASP: A01:2021

**AC-7: Unsuccessful Logon Attempts**
- Vulnerability types: brute force, credential stuffing
- Finding patterns: no account lockout, no rate limiting on login, no progressive delays
- Related CWEs: CWE-307
- OWASP: A07:2021

**AC-12: Session Termination**
- Vulnerability types: insufficient session expiration, no idle timeout
- Finding patterns: sessions that never expire, no logout functionality, tokens without expiration
- Related CWEs: CWE-613
- OWASP: A07:2021

**AC-17: Remote Access**
- Vulnerability types: insecure remote access, missing encryption
- Finding patterns: unencrypted remote management, SSH with password auth, exposed management interfaces
- Related CWEs: CWE-319, CWE-306

### AU -- Audit and Accountability

**AU-2: Event Logging**
- Vulnerability types: missing security event logging
- Finding patterns: no logging for authentication failures, no audit trail for sensitive operations
- Related CWEs: CWE-778
- OWASP: A09:2021

**AU-3: Content of Audit Records**
- Vulnerability types: insufficient log detail, sensitive data in logs
- Finding patterns: logs missing timestamp/source/outcome, passwords or tokens in logs
- Related CWEs: CWE-223, CWE-532
- OWASP: A09:2021

**AU-6: Audit Record Review, Analysis, and Reporting**
- Vulnerability types: no log review process, missing alerting
- Finding patterns: logs exist but are never reviewed, no automated alerting on suspicious patterns
- Related CWEs: CWE-778
- OWASP: A09:2021

**AU-9: Protection of Audit Information**
- Vulnerability types: log tampering, unauthorized log access
- Finding patterns: log files with open permissions, no log integrity verification
- Related CWEs: CWE-117

**AU-12: Audit Record Generation**
- Vulnerability types: logging disabled, incomplete audit coverage
- Finding patterns: security-relevant events not generating audit records
- Related CWEs: CWE-778
- OWASP: A09:2021

### CA -- Assessment, Authorization, and Monitoring

**CA-8: Penetration Testing**
- Vulnerability types: insufficient security testing
- Finding patterns: no regular penetration testing, untested attack surfaces
- Related controls: This control validates the testing itself, not specific vulnerabilities

### CM -- Configuration Management

**CM-2: Baseline Configuration**
- Vulnerability types: configuration drift, undocumented changes
- Finding patterns: no documented secure baseline, configuration differs from standard
- Related CWEs: CWE-16
- OWASP: A05:2021

**CM-6: Configuration Settings**
- Vulnerability types: insecure default settings, security misconfiguration
- Finding patterns: debug mode in production, verbose errors, insecure defaults
- Related CWEs: CWE-16, CWE-489, CWE-497, CWE-756
- OWASP: A05:2021

**CM-7: Least Functionality**
- Vulnerability types: unnecessary services, excessive features
- Finding patterns: unused ports open, unnecessary HTTP methods, development tools in production
- Related CWEs: CWE-489
- OWASP: A05:2021

**CM-8: System Component Inventory**
- Vulnerability types: unknown components, shadow IT, missing SBOM
- Finding patterns: no software bill of materials, undocumented dependencies
- Related CWEs: CWE-937, CWE-1035, CWE-1104
- OWASP: A06:2021

### IA -- Identification and Authentication

**IA-2: Identification and Authentication (Organizational Users)**
- Vulnerability types: weak authentication, missing MFA
- Finding patterns: no multi-factor authentication, weak password requirements
- Related CWEs: CWE-287, CWE-306, CWE-521
- OWASP: A07:2021

**IA-5: Authenticator Management**
- Vulnerability types: weak credentials, credential exposure
- Finding patterns: hardcoded passwords, weak password policies, credentials in source code
- Related CWEs: CWE-259, CWE-521, CWE-522, CWE-798
- OWASP: A07:2021

**IA-6: Authentication Feedback**
- Vulnerability types: username enumeration
- Finding patterns: different error messages for valid vs invalid usernames
- Related CWEs: CWE-204, CWE-209

**IA-8: Identification and Authentication (Non-Organizational Users)**
- Vulnerability types: missing authentication for external users, weak API auth
- Finding patterns: public endpoints without authentication, API keys in URLs
- Related CWEs: CWE-287, CWE-306
- OWASP: A07:2021

### IR -- Incident Response

**IR-4: Incident Handling**
- Vulnerability types: no incident response capability
- Finding patterns: no incident response plan, no escalation procedures
- Related to: A09:2021 (detection capability)

**IR-5: Incident Monitoring**
- Vulnerability types: no incident tracking
- Finding patterns: security incidents not tracked or documented

**IR-6: Incident Reporting**
- Vulnerability types: no reporting mechanism
- Finding patterns: no process for reporting security events

### MP -- Media Protection

**MP-4: Media Storage**
- Vulnerability types: unencrypted storage media
- Finding patterns: sensitive data on unencrypted volumes
- Related CWEs: CWE-311, CWE-312

### RA -- Risk Assessment

**RA-5: Vulnerability Monitoring and Scanning**
- Vulnerability types: no vulnerability scanning, unpatched systems
- Finding patterns: no regular vulnerability scans, outdated components
- Related CWEs: CWE-937, CWE-1035
- OWASP: A06:2021

### SC -- System and Communications Protection

**SC-7: Boundary Protection**
- Vulnerability types: SSRF, insufficient network segmentation
- Finding patterns: server-side requests to internal networks, missing network controls
- Related CWEs: CWE-918
- OWASP: A10:2021

**SC-8: Transmission Confidentiality and Integrity**
- Vulnerability types: cleartext transmission, weak TLS
- Finding patterns: HTTP instead of HTTPS, weak cipher suites, missing HSTS
- Related CWEs: CWE-319, CWE-523
- OWASP: A02:2021

**SC-12: Cryptographic Key Establishment and Management**
- Vulnerability types: hardcoded keys, weak key management
- Finding patterns: keys in source code, no key rotation, insufficient key length
- Related CWEs: CWE-321, CWE-798
- OWASP: A02:2021

**SC-13: Cryptographic Protection**
- Vulnerability types: weak cryptography, broken algorithms
- Finding patterns: MD5/SHA1 for hashing, DES/RC4 for encryption, insufficient key sizes
- Related CWEs: CWE-327, CWE-328, CWE-330
- OWASP: A02:2021

**SC-23: Session Authenticity**
- Vulnerability types: session hijacking, session fixation, CSRF
- Finding patterns: missing session integrity, no CSRF protection, predictable session IDs
- Related CWEs: CWE-352, CWE-384
- OWASP: A01:2021, A07:2021

**SC-28: Protection of Information at Rest**
- Vulnerability types: unencrypted sensitive data at rest
- Finding patterns: plaintext passwords in database, unencrypted PII storage
- Related CWEs: CWE-311, CWE-312
- OWASP: A02:2021

### SI -- System and Information Integrity

**SI-2: Flaw Remediation**
- Vulnerability types: unpatched vulnerabilities, known CVEs
- Finding patterns: outdated components with published patches, no patch management
- Related CWEs: CWE-937, CWE-1035
- OWASP: A06:2021

**SI-3: Malicious Code Protection**
- Vulnerability types: code injection, malware, supply chain attacks
- Finding patterns: no input validation, command injection, unrestricted file upload
- Related CWEs: CWE-77, CWE-78, CWE-94, CWE-434

**SI-10: Information Input Validation**
- Vulnerability types: injection flaws, all input validation failures
- Finding patterns: SQL injection, XSS, command injection, LDAP injection, XXE, SSTI
- Related CWEs: CWE-20, CWE-79, CWE-89, CWE-77, CWE-78, CWE-611, CWE-917
- OWASP: A03:2021

**SI-11: Error Handling**
- Vulnerability types: information leakage through errors
- Finding patterns: stack traces in responses, verbose error messages, debug information
- Related CWEs: CWE-209, CWE-497
- OWASP: A05:2021

**SI-16: Memory Protection**
- Vulnerability types: buffer overflow, memory corruption
- Finding patterns: out-of-bounds access, use-after-free (primarily for native code)
- Related CWEs: CWE-119, CWE-120, CWE-125, CWE-787

---

## PCI DSS v4.0 Requirements

### Requirement 1: Install and Maintain Network Security Controls

**1.2: Network security controls are configured and maintained**
- Vulnerability types: missing firewall rules, permissive network access
- Finding patterns: unnecessary ports open, no network segmentation between CDE and other networks
- NIST controls: SC-7

**1.3: Network access to and from the cardholder data environment is restricted**
- Vulnerability types: SSRF, unrestricted network access
- Finding patterns: direct internet access to CDE, missing DMZ, SSRF to internal services
- NIST controls: SC-7, AC-4
- Related CWEs: CWE-918

**1.4: Network connections between trusted and untrusted networks are controlled**
- Vulnerability types: missing network controls at trust boundaries
- Finding patterns: no WAF, no reverse proxy, direct database access from internet

### Requirement 2: Apply Secure Configurations to All System Components

**2.2.2: Vendor default accounts are managed**
- Vulnerability types: default credentials, unchanged defaults
- Finding patterns: admin/admin, default API keys, sample accounts
- NIST controls: CM-6, IA-5
- Related CWEs: CWE-259, CWE-798

**2.2.5: Secure configuration for services, protocols, and daemons**
- Vulnerability types: insecure service configuration
- Finding patterns: unnecessary services running, insecure protocol versions
- NIST controls: CM-6, CM-7

**2.2.7: Non-console administrative access is encrypted**
- Vulnerability types: unencrypted admin access
- Finding patterns: admin panels over HTTP, unencrypted management protocols
- NIST controls: SC-8, AC-17

### Requirement 3: Protect Stored Account Data

**3.4: Access to displays of PAN is restricted**
- Vulnerability types: PAN displayed without masking
- Finding patterns: full card numbers visible in UI, logs, or API responses
- Related CWEs: CWE-200, CWE-312

**3.5: Primary Account Number (PAN) is secured wherever it is stored**
- Vulnerability types: unencrypted PAN storage
- Finding patterns: plaintext card numbers in database, files, or backups
- NIST controls: SC-28
- Related CWEs: CWE-311, CWE-312

**3.6: Cryptographic keys used to protect stored account data are secured**
- Vulnerability types: weak key management
- Finding patterns: hardcoded encryption keys, no key rotation, keys stored alongside data
- NIST controls: SC-12
- Related CWEs: CWE-321, CWE-798

### Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission

**4.2.1: Strong cryptography is used for data transmission**
- Vulnerability types: cleartext transmission, weak TLS
- Finding patterns: HTTP endpoints handling sensitive data, TLS 1.0/1.1, weak cipher suites
- NIST controls: SC-8, SC-13
- Related CWEs: CWE-319, CWE-327

**4.2.2: PAN is secured with strong cryptography whenever sent via end-user messaging**
- Vulnerability types: PAN in email, SMS, or chat
- Finding patterns: card numbers sent via unencrypted channels

### Requirement 5: Protect All Systems and Networks from Malicious Software

**5.2: Malicious software is prevented or detected**
- Vulnerability types: malware, malicious uploads
- Finding patterns: no file scanning on uploads, missing malware protection
- NIST controls: SI-3
- Related CWEs: CWE-434

**5.3: Anti-malware mechanisms are active and maintained**
- Vulnerability types: disabled security controls
- Finding patterns: antivirus disabled, no runtime protection

### Requirement 6: Develop and Maintain Secure Systems and Software

**6.2.1: Custom software is developed securely**
- Vulnerability types: all software vulnerabilities
- Finding patterns: absence of secure coding practices, no security training evidence
- NIST controls: SI-10, SA-15

**6.2.4: Software engineering techniques prevent common attacks**
- Vulnerability types: injection, XSS, CSRF, buffer overflow, insecure cryptography
- Finding patterns: SQL injection, XSS, command injection, path traversal, all OWASP Top 10
- NIST controls: SI-10, SI-3
- Related CWEs: CWE-79, CWE-89, CWE-77, CWE-78, CWE-352, CWE-22

**6.3.1: Security vulnerabilities are identified and managed**
- Vulnerability types: no vulnerability management process
- Finding patterns: no CVE tracking, no vulnerability assessment process

**6.3.2: Software inventory is maintained**
- Vulnerability types: unknown components, missing SBOM
- Finding patterns: no dependency inventory, no tracking of third-party components
- NIST controls: CM-8
- Related CWEs: CWE-937, CWE-1035

**6.4.1: Public-facing web applications are protected**
- Vulnerability types: web application attacks
- Finding patterns: no WAF, no web application security controls
- NIST controls: SI-10

**6.4.2: Public-facing web applications have automated technical solution for detecting attacks**
- Vulnerability types: missing attack detection
- Finding patterns: no WAF, no RASP, no automated detection

### Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know

**7.2: Access to system components and data is appropriately defined and assigned**
- Vulnerability types: excessive access, missing RBAC
- Finding patterns: users with unnecessary privileges, no role-based access, missing authorization
- NIST controls: AC-3, AC-6
- Related CWEs: CWE-284, CWE-862, CWE-863

**7.2.5: Access is assigned based on least privilege**
- Vulnerability types: excessive privileges, missing least privilege
- Finding patterns: application running as admin/root, overly broad database permissions
- NIST controls: AC-6

### Requirement 8: Identify Users and Authenticate Access to System Components

**8.2: User identification is managed**
- Vulnerability types: shared accounts, no unique IDs
- Finding patterns: shared credentials, generic accounts, no individual accountability
- NIST controls: IA-2

**8.3: Strong authentication is established**
- Vulnerability types: weak authentication mechanisms
- Finding patterns: no MFA, weak passwords, plaintext credential storage
- NIST controls: IA-2, IA-5
- Related CWEs: CWE-287, CWE-521

**8.3.4: Account lockout mechanisms**
- Vulnerability types: no lockout, brute force possible
- Finding patterns: unlimited login attempts, no progressive delays
- NIST controls: AC-7
- Related CWEs: CWE-307

**8.3.6: Password complexity requirements**
- Vulnerability types: weak passwords
- Finding patterns: no minimum length, no complexity, passwords under 12 characters
- NIST controls: IA-5
- Related CWEs: CWE-521

### Requirement 9: Restrict Physical Access to Cardholder Data

**Note:** Requirement 9 covers physical security controls and is generally not applicable to code review or application security scanning. Mark as N/A for code-level assessments.

### Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

**10.2: Audit logs are implemented**
- Vulnerability types: missing audit logging
- Finding patterns: no logging for access to sensitive data, no login/logout logging
- NIST controls: AU-2, AU-12
- Related CWEs: CWE-778

**10.3: Audit logs are protected from destruction and tampering**
- Vulnerability types: log tampering, unauthorized log access
- Finding patterns: writable log files, no log integrity monitoring
- NIST controls: AU-9
- Related CWEs: CWE-117

**10.4.1: Audit logs are reviewed for anomalies**
- Vulnerability types: no log review process
- Finding patterns: logs collected but never analyzed, no automated alerting
- NIST controls: AU-6

**10.6: Time-synchronization mechanisms are supported**
- Vulnerability types: clock drift, inconsistent timestamps
- Finding patterns: no NTP configuration, log timestamp inconsistencies

### Requirement 11: Test Security of Systems and Networks Regularly

**11.3: External and internal vulnerabilities are regularly identified and addressed**
- Vulnerability types: unpatched vulnerabilities, untested systems
- Finding patterns: no regular vulnerability scanning, known CVEs in production
- NIST controls: RA-5
- Related CWEs: CWE-937

**11.4: External and internal penetration testing is regularly performed**
- Vulnerability types: insufficient security testing coverage
- Finding patterns: no penetration testing, untested attack vectors
- NIST controls: CA-8

### Requirement 12: Support Information Security with Organizational Policies and Programs

**Note:** Requirement 12 covers organizational policies, risk assessment processes, and security awareness training. These are generally assessed at the organizational level rather than through code-level findings. Mark as N/A for automated scanning or note if findings suggest policy gaps.

**12.6: Security awareness education is provided**
- Vulnerability types: developer security knowledge gaps
- Finding patterns: recurring vulnerability patterns suggesting lack of training

**12.10: Suspected and confirmed security incidents are responded to immediately**
- Vulnerability types: no incident response capability
- Finding patterns: no alerting, no incident response plan evidence
- NIST controls: IR-4, IR-5, IR-6
