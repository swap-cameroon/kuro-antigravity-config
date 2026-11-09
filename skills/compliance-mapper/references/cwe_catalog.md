# CWE Catalog Reference

This catalog covers the most frequently encountered CWEs mapped to OWASP Top 10, NIST SP 800-53, and PCI DSS frameworks. Each entry provides cross-references for compliance mapping.

---

## CWE-22: Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)

- **Description:** The application uses external input to construct a pathname for accessing files, but does not properly neutralize special elements (e.g., `../`) that can resolve to a location outside the intended directory.
- **Severity:** High
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement), SI-10 (Information Input Validation)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** Yes (#8)
- **Example:** `open("/uploads/" + userInput)` where userInput is `../../etc/passwd`

---

## CWE-77: Improper Neutralization of Special Elements Used in a Command (Command Injection)

- **Description:** The application constructs a command using externally-influenced input but does not neutralize special elements that could modify the intended command.
- **Severity:** Critical
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation), SI-3 (Malicious Code Protection)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#5)
- **Example:** `system("ping " + userHost)` where userHost is `; rm -rf /`

---

## CWE-78: Improper Neutralization of Special Elements Used in an OS Command (OS Command Injection)

- **Description:** The application constructs an OS command using externally-influenced input but does not properly neutralize special elements that could modify the command.
- **Severity:** Critical
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation), SI-3 (Malicious Code Protection)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#5)
- **Example:** `exec("ls " + userDir)` where userDir contains shell metacharacters

---

## CWE-79: Improper Neutralization of Input During Web Page Generation (Cross-Site Scripting / XSS)

- **Description:** The application does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output that is served as a web page to other users.
- **Severity:** Medium to High
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation), SC-18 (Mobile Code)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#2)
- **Example:** `<div>Hello, ${userName}</div>` where userName is `<script>alert(1)</script>`

---

## CWE-89: Improper Neutralization of Special Elements Used in an SQL Command (SQL Injection)

- **Description:** The application constructs SQL statements using string concatenation with externally-influenced input, without proper parameterization or escaping.
- **Severity:** Critical
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#3)
- **Example:** `query("SELECT * FROM users WHERE id=" + userId)` where userId is `1 OR 1=1`

---

## CWE-94: Improper Control of Generation of Code (Code Injection)

- **Description:** The application constructs code segments using externally-influenced input, allowing an attacker to execute arbitrary code.
- **Severity:** Critical
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation), SI-3 (Malicious Code Protection)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** No
- **Example:** `eval(userExpression)` where userExpression is attacker-controlled

---

## CWE-200: Exposure of Sensitive Information to an Unauthorized Actor

- **Description:** The application exposes sensitive information to an actor that is not explicitly authorized to have access to that information.
- **Severity:** Medium
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement), AC-4 (Information Flow Enforcement)
- **PCI DSS:** Req 3.4 (Render PAN unreadable), Req 6.2.4
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** No
- **Example:** API endpoint returning full user records including password hashes

---

## CWE-259: Use of Hard-coded Password

- **Description:** The application contains a hard-coded password used for authentication or as a cryptographic key.
- **Severity:** High
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** IA-5 (Authenticator Management), SC-12 (Cryptographic Key Establishment)
- **PCI DSS:** Req 2.2.2 (Vendor default accounts), Req 8.3.6
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** `if (password == "admin123")` or `SECRET_KEY = "hardcoded-secret"`

---

## CWE-276: Incorrect Default Permissions

- **Description:** During installation or deployment, the application sets incorrect permissions on files, directories, or other resources, allowing unauthorized access.
- **Severity:** Medium
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **PCI DSS:** Req 7.2 (Restrict access to system components)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** No
- **Example:** Configuration files created with 0777 permissions, writable by all users

---

## CWE-284: Improper Access Control

- **Description:** The application does not restrict or incorrectly restricts access to a resource from an unauthorized actor.
- **Severity:** High
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **PCI DSS:** Req 7.2 (Restrict access to system components)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** No
- **Example:** Admin endpoints accessible without role verification

---

## CWE-287: Improper Authentication

- **Description:** The application does not sufficiently verify that the claimed identity of an actor is correct.
- **Severity:** Critical
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** IA-2 (Identification and Authentication), IA-8 (Identification and Authentication for Non-Organizational Users)
- **PCI DSS:** Req 8.2 (User identification), Req 8.3 (Secure authentication)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** Yes (#13)
- **Example:** Authentication bypass via parameter manipulation or alternate channels

---

## CWE-295: Improper Certificate Validation

- **Description:** The application does not validate, or incorrectly validates, a certificate, allowing man-in-the-middle attacks.
- **Severity:** High
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** SC-8 (Transmission Confidentiality and Integrity), SC-23 (Session Authenticity)
- **PCI DSS:** Req 4.2.1 (Strong cryptography for transmission)
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** `verify=False` in HTTP client calls or `NODE_TLS_REJECT_UNAUTHORIZED=0`

---

## CWE-307: Improper Restriction of Excessive Authentication Attempts

- **Description:** The application does not implement sufficient measures to prevent multiple failed authentication attempts, enabling brute-force attacks.
- **Severity:** Medium
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** AC-7 (Unsuccessful Logon Attempts), IA-5 (Authenticator Management)
- **PCI DSS:** Req 8.3.4 (Account lockout)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** Login endpoint with no rate limiting or account lockout mechanism

---

## CWE-311: Missing Encryption of Sensitive Data

- **Description:** The application does not encrypt sensitive information, making it readable by unauthorized parties.
- **Severity:** High
- **OWASP:** A02:2021 Cryptographic Failures
- **NIST:** SC-28 (Protection of Information at Rest), SC-8 (Transmission Confidentiality)
- **PCI DSS:** Req 3.5 (Protect stored account data), Req 4.2.1
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** Database storing credit card numbers in plaintext columns

---

## CWE-312: Cleartext Storage of Sensitive Information

- **Description:** The application stores sensitive information in cleartext within a resource that might be accessible to unauthorized actors.
- **Severity:** High
- **OWASP:** A02:2021 Cryptographic Failures
- **NIST:** SC-28 (Protection of Information at Rest)
- **PCI DSS:** Req 3.5 (Protect stored account data)
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** Passwords stored as plaintext in a database table or config file

---

## CWE-319: Cleartext Transmission of Sensitive Information

- **Description:** The application transmits sensitive information in cleartext over a channel that could be intercepted.
- **Severity:** High
- **OWASP:** A02:2021 Cryptographic Failures
- **NIST:** SC-8 (Transmission Confidentiality and Integrity)
- **PCI DSS:** Req 4.2.1 (Strong cryptography for transmission)
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** Login form submitted over HTTP instead of HTTPS

---

## CWE-327: Use of a Broken or Risky Cryptographic Algorithm

- **Description:** The application uses a broken or risky cryptographic algorithm or protocol (e.g., MD5, SHA1 for password hashing, DES, RC4).
- **Severity:** High
- **OWASP:** A02:2021 Cryptographic Failures
- **NIST:** SC-13 (Cryptographic Protection)
- **PCI DSS:** Req 3.6 (Cryptographic key management), Req 4.2.1
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** `hashlib.md5(password)` for password storage instead of bcrypt/scrypt/argon2

---

## CWE-330: Use of Insufficiently Random Values

- **Description:** The application uses insufficiently random numbers or values in a security context, making them predictable.
- **Severity:** Medium
- **OWASP:** A02:2021 Cryptographic Failures
- **NIST:** SC-13 (Cryptographic Protection)
- **PCI DSS:** Req 3.6 (Cryptographic key management)
- **ISO 27001:** A.8.24 (Use of cryptography)
- **SANS Top 25:** No
- **Example:** Using `Math.random()` or `random.random()` for session tokens or CSRF tokens

---

## CWE-352: Cross-Site Request Forgery (CSRF)

- **Description:** The application does not verify that a state-changing request was intentionally sent by the authenticated user, allowing an attacker to forge requests from the user's browser.
- **Severity:** Medium
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** SC-23 (Session Authenticity)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#9)
- **Example:** Form submission without CSRF token validation on state-changing operations

---

## CWE-384: Session Fixation

- **Description:** The application does not regenerate the session identifier after a successful authentication, allowing an attacker to set a known session ID before the user logs in.
- **Severity:** Medium
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** SC-23 (Session Authenticity), IA-2 (Identification and Authentication)
- **PCI DSS:** Req 8.2 (User identification)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** Session cookie not rotated after login, allowing pre-set session IDs to persist

---

## CWE-434: Unrestricted Upload of File with Dangerous Type

- **Description:** The application allows upload of files without properly validating the file type, enabling upload of executable or malicious content.
- **Severity:** High
- **OWASP:** A04:2021 Insecure Design
- **NIST:** SI-3 (Malicious Code Protection), CM-7 (Least Functionality)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#10)
- **Example:** File upload endpoint accepting .php, .jsp, or .exe files without restriction

---

## CWE-502: Deserialization of Untrusted Data

- **Description:** The application deserializes untrusted data without sufficiently verifying that the resulting data will be valid and safe, enabling remote code execution.
- **Severity:** Critical
- **OWASP:** A08:2021 Software and Data Integrity Failures
- **NIST:** SI-10 (Information Input Validation)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#14)
- **Example:** `pickle.loads(user_data)` or `ObjectInputStream.readObject()` on untrusted input

---

## CWE-521: Weak Password Requirements

- **Description:** The application does not require strong passwords, allowing users to create accounts with easily guessable credentials.
- **Severity:** Medium
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** IA-5 (Authenticator Management)
- **PCI DSS:** Req 8.3.6 (Password complexity)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** No minimum password length, no complexity requirements, no breach list check

---

## CWE-522: Insufficiently Protected Credentials

- **Description:** The application transmits or stores authentication credentials using insecure methods that could allow credential interception or recovery.
- **Severity:** High
- **OWASP:** A04:2021 Insecure Design / A07:2021 Identification and Authentication Failures
- **NIST:** IA-5 (Authenticator Management), SC-8 (Transmission Confidentiality)
- **PCI DSS:** Req 8.3.2 (Protect credentials during transmission)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** Password sent via GET parameters, credentials stored in browser local storage

---

## CWE-532: Insertion of Sensitive Information into Log File

- **Description:** The application writes sensitive information (passwords, tokens, PII) into log files, potentially exposing it to unauthorized actors with log access.
- **Severity:** Medium
- **OWASP:** A09:2021 Security Logging and Monitoring Failures
- **NIST:** AU-3 (Content of Audit Records), SI-11 (Error Handling)
- **PCI DSS:** Req 10.3 (Protect audit logs)
- **ISO 27001:** A.8.15 (Logging)
- **SANS Top 25:** No
- **Example:** `logger.info("User login: " + username + " password: " + password)`

---

## CWE-611: Improper Restriction of XML External Entity Reference (XXE)

- **Description:** The application processes XML input that can contain references to external entities, allowing attackers to read files, perform SSRF, or cause denial of service.
- **Severity:** High
- **OWASP:** A03:2021 Injection / A05:2021 Security Misconfiguration
- **NIST:** SI-10 (Information Input Validation), CM-6 (Configuration Settings)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#4)
- **Example:** XML parser processing `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>`

---

## CWE-613: Insufficient Session Expiration

- **Description:** The application does not sufficiently expire sessions, allowing attackers to use stolen or leaked session tokens for extended periods.
- **Severity:** Medium
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** AC-12 (Session Termination), SC-23 (Session Authenticity)
- **PCI DSS:** Req 8.2.8 (Session timeout)
- **ISO 27001:** A.8.5 (Secure authentication)
- **SANS Top 25:** No
- **Example:** JWT tokens with no expiration claim or sessions lasting indefinitely

---

## CWE-639: Authorization Bypass Through User-Controlled Key (IDOR)

- **Description:** The application uses a user-controlled key (such as a numeric ID) to access resources, without verifying that the user is authorized to access the referenced resource.
- **Severity:** High
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement)
- **PCI DSS:** Req 7.2 (Restrict access to system components)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** Yes (#4 under authorization)
- **Example:** `GET /api/users/123/profile` accessible by changing `123` to any other user ID

---

## CWE-798: Use of Hard-coded Credentials

- **Description:** The application contains hard-coded credentials (usernames, passwords, API keys, tokens) used for authentication to external services or internal components.
- **Severity:** Critical
- **OWASP:** A07:2021 Identification and Authentication Failures
- **NIST:** IA-5 (Authenticator Management), SC-12 (Cryptographic Key Establishment)
- **PCI DSS:** Req 2.2.2 (Vendor default accounts), Req 8.3.6
- **ISO 27001:** A.8.5 (Secure authentication), A.8.24 (Use of cryptography)
- **SANS Top 25:** Yes (#18)
- **Example:** `API_KEY = "sk-1234567890abcdef"` or `DATABASE_PASSWORD = "production_pass"`

---

## CWE-862: Missing Authorization

- **Description:** The application does not perform an authorization check when an actor attempts to access a resource or perform an action.
- **Severity:** High
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **PCI DSS:** Req 7.2 (Restrict access to system components)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** Yes (#11)
- **Example:** Admin endpoint with no middleware checking user role

---

## CWE-863: Incorrect Authorization

- **Description:** The application performs an authorization check but does so incorrectly, allowing actors to access resources they should not be able to reach.
- **Severity:** High
- **OWASP:** A01:2021 Broken Access Control
- **NIST:** AC-3 (Access Enforcement)
- **PCI DSS:** Req 7.2 (Restrict access to system components)
- **ISO 27001:** A.8.3 (Information access restriction)
- **SANS Top 25:** Yes (#15)
- **Example:** Role check uses OR instead of AND, or compares role names case-insensitively without normalization

---

## CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes (Mass Assignment)

- **Description:** The application receives input that defines object attributes, and sets them without properly filtering which attributes can be modified, allowing attackers to set privileged fields.
- **Severity:** High
- **OWASP:** A08:2021 Software and Data Integrity Failures
- **NIST:** AC-3 (Access Enforcement), SI-10 (Information Input Validation)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** No
- **Example:** `User.update(req.body)` allowing `{"role": "admin"}` to be set by any user

---

## CWE-917: Improper Neutralization of Special Elements Used in an Expression Language Statement

- **Description:** The application constructs expression language (EL) statements using externally-influenced input, allowing injection of arbitrary expressions.
- **Severity:** Critical
- **OWASP:** A03:2021 Injection
- **NIST:** SI-10 (Information Input Validation)
- **PCI DSS:** Req 6.2.4 (Prevent common software attacks)
- **ISO 27001:** A.8.28 (Secure coding)
- **SANS Top 25:** No
- **Example:** SSTI via `render("Hello " + userInput)` in template engines (Jinja2, Twig, Freemarker)

---

## CWE-918: Server-Side Request Forgery (SSRF)

- **Description:** The application fetches a remote resource using a user-supplied URL without validating that the URL points to an expected destination.
- **Severity:** High
- **OWASP:** A10:2021 Server-Side Request Forgery
- **NIST:** AC-3 (Access Enforcement), SC-7 (Boundary Protection)
- **PCI DSS:** Req 1.3 (Network access controls), Req 6.2.4
- **ISO 27001:** A.8.20 (Networks security), A.8.28 (Secure coding)
- **SANS Top 25:** Yes (#19)
- **Example:** `fetch(userUrl)` where userUrl is `http://169.254.169.254/latest/meta-data/`

---

## CWE-937: Using Components with Known Vulnerabilities (OWASP)

- **Description:** The application uses third-party components (libraries, frameworks) that have known, published vulnerabilities.
- **Severity:** Varies (depends on the specific CVE)
- **OWASP:** A06:2021 Vulnerable and Outdated Components
- **NIST:** CM-8 (System Component Inventory), SI-2 (Flaw Remediation), RA-5 (Vulnerability Monitoring and Scanning)
- **PCI DSS:** Req 6.3.2 (Software inventory), Req 11.3 (Vulnerability scanning)
- **ISO 27001:** A.8.8 (Management of technical vulnerabilities)
- **SANS Top 25:** No
- **Example:** Using lodash 4.17.11 which is vulnerable to prototype pollution (CVE-2019-10744)

---

## CWE-1035: Using Vulnerable Third-Party Software (OWASP)

- **Description:** The application relies on third-party software that contains known security vulnerabilities, similar to CWE-937 but broader in scope.
- **Severity:** Varies (depends on the specific CVE)
- **OWASP:** A06:2021 Vulnerable and Outdated Components
- **NIST:** CM-8 (System Component Inventory), SI-2 (Flaw Remediation)
- **PCI DSS:** Req 6.3.2 (Software inventory)
- **ISO 27001:** A.8.8 (Management of technical vulnerabilities)
- **SANS Top 25:** No
- **Example:** Running an outdated version of a web framework with known RCE vulnerabilities
