---
name: API Contract Testing
description: Validates API specifications against actual endpoint behavior. Tests any HTTP API regardless of backend technology.
triggers:
  - test API contracts
  - validate API spec
  - check API specification
  - verify API behavior matches documentation
  - find undocumented endpoints
  - API contract validation
  - check for undocumented API endpoints
  - verify API responses match spec
  - API schema validation
---

# API Contract Testing

Validate that API implementations conform to their documented specifications. This skill is language-agnostic and tests any HTTP API regardless of backend technology.

## Key Principles

- **Contract-first**: The API specification is the source of truth. Any deviation between spec and implementation is a finding.
- **Non-destructive**: Prefer GET requests and read-only operations. Avoid sending requests that modify state unless explicitly instructed.
- **Language-agnostic**: Test the HTTP interface, not the source code. Works with any backend framework or language.
- **If no spec exists**: Discover endpoints from source code or a running server and report what should be documented.

## Workflow

### Step 1: Spec Discovery

Locate API specification files in the project:

- OpenAPI/Swagger: `openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json`
- GraphQL: `schema.graphql`, `*.graphql`
- RAML: `*.raml`
- API Blueprint: `*.apib`, `api-blueprint`

If no specification file is found, auto-discover endpoints by reading framework-specific route definitions:

- **Express.js**: Scan for `router.get()`, `router.post()`, `router.put()`, `router.delete()`, `app.use()`, `app.get()`, `app.post()`
- **Flask**: Scan for `@app.route()`, `@blueprint.route()`, Blueprint registrations
- **Django**: Scan `urls.py` for `path()`, `re_path()`, `url()` patterns
- **Spring Boot**: Scan for `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@RequestMapping` annotations
- **Laravel**: Scan `routes/api.php` and `routes/web.php` for `Route::get()`, `Route::post()` patterns
- **Rails**: Scan `config/routes.rb` for `resources`, `get`, `post` definitions
- **Go/Gin**: Scan for `r.GET()`, `r.POST()`, `r.PUT()`, `r.DELETE()` patterns
- **ASP.NET**: Scan for `[HttpGet]`, `[HttpPost]` attributes, `MapGet()`, `MapPost()` calls
- **FastAPI**: Scan for `@app.get()`, `@app.post()`, `@router.get()` decorators

If the server is running, use the Bash tool to probe common API base paths via curl (`/api`, `/api/v1`, `/v1`, `/graphql`, `/rest`).

### Step 2: Endpoint Inventory

Build a complete list of all documented (or discovered) endpoints. For each endpoint, record:

- **Path** and supported **HTTP methods**
- **Path parameters** and **query parameters** (names, types, required/optional)
- **Request body schema** (content type, required fields, field types)
- **Response schemas** per status code (expected fields, types, formats)
- **Authentication requirements** (which auth mechanism, which roles/scopes)
- **Expected status codes** for success and error cases

Present the inventory as a structured table or list before proceeding to validation.

### Step 3: Contract Validation

For each documented endpoint, use the Bash tool to send HTTP requests via `curl` and verify:

1. **Status codes**: Response status matches the spec (e.g., GET returns 200, POST returns 201, missing resource returns 404).
2. **Content-Type**: Response `Content-Type` header matches the spec (e.g., `application/json`).
3. **Response body schema**: Response JSON structure conforms to the documented schema -- correct field names, correct types, no missing required fields.
4. **Required fields**: All fields marked as required in the spec are present in the response.
5. **Error format**: Error responses follow the documented error schema (e.g., `{"error": "message"}` or RFC 7807 Problem Details).
6. **Data types**: Field values match expected types (strings are strings, numbers are numbers, dates match format).

Flag any deviations as contract violations.

### Step 4: Undocumented Endpoint Discovery

Probe for endpoints that are NOT in the specification:

**Common paths to test:**
- Admin/management: `/admin`, `/dashboard`, `/manage`, `/internal`, `/debug`, `/status`, `/health`, `/metrics`
- Spring Actuator: `/actuator`, `/actuator/health`, `/actuator/env`, `/actuator/beans`
- Django debug: `/_debug`, `/__debug__/`
- Documentation: `/api-docs`, `/swagger`, `/swagger-ui`, `/docs`, `/redoc`, `/openapi.json`, `/swagger.json`
- Auth: `/login`, `/logout`, `/register`, `/forgot-password`, `/reset-password`, `/oauth`, `/token`
- Sensitive: `/.env`, `/.git`, `/server-status`, `/phpinfo`, `/elmah`, `/trace`, `/console`
- GraphQL: `/graphql`, `/graphiql`

**HTTP method fuzzing:**
- For each known endpoint, try methods not documented in the spec (e.g., try PUT/DELETE/PATCH on GET-only endpoints).
- Test method override headers: `X-HTTP-Method-Override`, `X-Method-Override`, `X-HTTP-Method`.

**Parameter discovery:**
- Try common query parameters: `id`, `user_id`, `page`, `limit`, `debug`, `verbose`, `format`, `admin`, `role`.
- Check if undocumented parameters change behavior.

Report any endpoint that responds with a non-404 status as potentially undocumented.

### Step 5: Authentication Enforcement

For each endpoint marked as requiring authentication:

1. **Missing credentials**: Send request with no `Authorization` header. Expect 401 Unauthorized.
2. **Invalid credentials**: Send request with an invalid/garbage token. Expect 401 Unauthorized.
3. **Empty token**: Send `Authorization: Bearer ` (empty value). Expect 401 Unauthorized.
4. **Expired token**: If JWT-based, send a token with past `exp` claim. Expect 401 Unauthorized.

For each endpoint marked as public:

1. Verify it responds successfully without any auth headers.
2. Verify it does not accidentally require auth (returning 401 when it should be open).

Test authorization boundaries:

1. **Horizontal access**: Can user A's credentials access user B's resources?
2. **Vertical access**: Can a regular user access admin-only endpoints?
3. **Method-level**: Can a user with read access perform write operations?

Test common auth bypass patterns:

- Trailing slash variation (`/admin` vs `/admin/`)
- Case variation (`/Admin` vs `/admin`)
- Path parameter manipulation (sequential IDs)
- HTTP method switching (GET vs POST)

### Step 6: Report

Produce a structured findings report with these categories:

1. **Schema Violations**: Responses that do not match the documented schema (missing fields, wrong types, extra undocumented fields).
2. **Undocumented Endpoints**: Endpoints that respond but are not in the specification.
3. **Authentication Gaps**: Endpoints that should require auth but do not, or auth bypasses found.
4. **Excessive Data Exposure**: Response contains fields not defined in the spec (potential information leakage -- CWE-200).
5. **Missing Error Handling**: Endpoints that return unexpected status codes, stack traces, or unstructured error messages.
6. **Missing Rate Limiting**: Auth-related endpoints without rate limiting protection.

For each finding, include:

- **Endpoint**: Method and path
- **Expected behavior**: What the spec says
- **Actual behavior**: What the server returned
- **Severity**: Critical / High / Medium / Low / Informational
- **Recommendation**: How to fix the deviation

Severity guidelines:
- **Critical**: Auth bypass, sensitive data exposure, undocumented admin endpoints accessible without auth
- **High**: Schema violations that expose extra fields, missing auth on protected endpoints
- **Medium**: Wrong status codes, missing required fields in responses, undocumented but non-sensitive endpoints
- **Low**: Content-Type mismatches, inconsistent error formats
- **Informational**: Missing documentation for existing endpoints, minor schema deviations
