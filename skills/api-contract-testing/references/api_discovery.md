# API Endpoint Discovery Reference

Comprehensive reference for discovering, enumerating, and analyzing API endpoints
across any technology stack. Use these techniques when no API specification exists
or to find undocumented endpoints that should be tested.

---

## Common API Base Paths

When probing a server for API endpoints, start with these base paths:

```
/api
/api/v1
/api/v2
/api/v3
/v1
/v2
/v3
/graphql
/rest
/rpc
/ws
/websocket
```

Probe each with a GET request. A non-404 response indicates the path exists.

---

## Endpoint Categories and Common Paths

### Admin and Management Paths

These paths often expose sensitive functionality and should always be probed:

```
/admin
/admin/
/administrator
/dashboard
/manage
/management
/internal
/debug
/debug/vars
/status
/health
/healthcheck
/health/live
/health/ready
/metrics
/monitoring
/info
/version
/build-info
```

### Framework-Specific Management Endpoints

**Spring Boot Actuator:**
```
/actuator
/actuator/health
/actuator/info
/actuator/env
/actuator/beans
/actuator/mappings
/actuator/configprops
/actuator/metrics
/actuator/loggers
/actuator/heapdump
/actuator/threaddump
/actuator/shutdown
/actuator/conditions
/actuator/httptrace
```

**Django Debug:**
```
/_debug
/__debug__/
/silk/
/django-admin/
```

**Rails:**
```
/rails/info/routes
/rails/info/properties
/rails/mailers
```

**ASP.NET:**
```
/elmah.axd
/trace.axd
/applicationdiagnostics
```

**PHP/WordPress:**
```
/phpinfo.php
/info.php
/wp-admin
/wp-json
/wp-json/wp/v2
```

### API Documentation Paths

Documentation endpoints often reveal the full API surface:

```
/api-docs
/api-docs.json
/swagger
/swagger-ui
/swagger-ui.html
/swagger-ui/index.html
/swagger.json
/swagger.yaml
/docs
/docs/api
/redoc
/openapi.json
/openapi.yaml
/openapi/v3/api-docs
/graphiql
/playground
/explorer
/api/schema
/schema
/_catalog
```

### Authentication and Session Paths

```
/login
/logout
/signin
/signout
/signup
/register
/forgot-password
/reset-password
/change-password
/oauth
/oauth/authorize
/oauth/token
/oauth/callback
/oauth2/authorize
/oauth2/token
/token
/token/refresh
/auth
/auth/login
/auth/register
/auth/verify
/auth/callback
/sso
/saml
/cas
/.well-known/openid-configuration
/.well-known/jwks.json
/connect/authorize
/connect/token
```

### Common Resource Paths

```
/users
/users/me
/users/profile
/accounts
/profiles
/settings
/config
/configuration
/preferences
/uploads
/files
/images
/media
/documents
/attachments
/downloads
/export
/import
/search
/notifications
/messages
/comments
/posts
/articles
/products
/orders
/payments
/invoices
/reports
/analytics
/logs
/audit
/events
/webhooks
/callbacks
/jobs
/tasks
/queue
```

### Hidden and Sensitive Paths

```
/.env
/.env.local
/.env.production
/.git
/.git/config
/.git/HEAD
/.gitignore
/.svn
/.hg
/.DS_Store
/server-status
/server-info
/.htaccess
/.htpasswd
/web.config
/crossdomain.xml
/robots.txt
/sitemap.xml
/favicon.ico
/console
/shell
/terminal
/backup
/backups
/dump
/database
/db
/phpmyadmin
/adminer
```

---

## HTTP Method Fuzzing

### Standard Methods to Test

For each discovered path, test all standard HTTP methods:

| Method  | Purpose                | Expected Behavior                  |
|---------|------------------------|------------------------------------|
| GET     | Read resource          | 200 OK with body                   |
| POST    | Create resource        | 201 Created with location header   |
| PUT     | Replace resource       | 200 OK or 204 No Content           |
| PATCH   | Partial update         | 200 OK with updated resource       |
| DELETE  | Remove resource        | 200 OK or 204 No Content           |
| OPTIONS | CORS preflight/info    | 200/204 with Allow header          |
| HEAD    | Headers only (no body) | Same headers as GET, no body       |
| TRACE   | Echo request back      | Should be disabled (405)           |

### Method Override Headers

Some frameworks allow method overriding via headers. Test these on POST requests:

```
X-HTTP-Method-Override: PUT
X-HTTP-Method-Override: DELETE
X-HTTP-Method-Override: PATCH
X-Method-Override: PUT
X-HTTP-Method: DELETE
```

Also test query parameter overrides:

```
POST /resource?_method=DELETE
POST /resource?method=PUT
```

### State-Changing GET Detection (CWE-650)

GET requests must never cause state changes. Check for patterns like:

```
GET /api/users/123/delete
GET /api/users/123?action=delete
GET /api/admin/reset
GET /api/cache/clear
GET /api/logout
```

If any of these return 200 and cause a side effect, flag as CWE-650.

---

## Parameter Discovery

### Common Query Parameters

Test these query parameters on discovered endpoints:

**Identification:**
```
id, user_id, userId, uid, account_id, accountId
```

**Pagination:**
```
page, limit, offset, per_page, perPage, size, pageSize, page_size
skip, take, cursor, after, before, start, count
```

**Sorting and Filtering:**
```
sort, order, orderBy, order_by, sortBy, sort_by
direction, dir, asc, desc
filter, where, query, q, search, keyword, term
```

**Output Control:**
```
fields, select, include, exclude, expand, embed
format, accept, pretty, verbose, debug
callback, jsonp
```

**Authentication/Authorization:**
```
token, api_key, apiKey, key, access_token, accessToken
auth, session, sid
```

**Dangerous Parameters (test for injection/bypass):**
```
admin, is_admin, isAdmin, role, permissions
debug, test, dev, staging, internal, verbose
```

### Common Request Body Fields

When testing POST/PUT/PATCH endpoints:

**User-related:**
```json
{
  "username": "test",
  "password": "test",
  "email": "test@test.com",
  "name": "Test User",
  "first_name": "Test",
  "last_name": "User",
  "phone": "1234567890",
  "role": "admin",
  "admin": true,
  "is_admin": true,
  "permissions": ["read", "write", "admin"],
  "status": "active",
  "type": "admin",
  "group": "administrators"
}
```

**Watch for mass assignment**: If sending `role`, `admin`, `is_admin`, or `permissions`
in a request body causes privilege escalation, flag as a critical finding.

### Header Parameters

Test these request headers for behavior changes:

```
Authorization: Bearer <token>
X-API-Key: <key>
X-Token: <token>
Cookie: session=<value>
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Forwarded-Host: internal.example.com
X-Original-URL: /admin
X-Rewrite-URL: /admin
Host: localhost
Referer: https://admin.example.com
Origin: https://admin.example.com
Content-Type: application/json
Accept: application/xml
X-Custom-IP-Authorization: 127.0.0.1
```

---

## Framework-Specific Route Discovery

### Express.js / Node.js

Scan source files for these patterns:

```javascript
// Route definitions
router.get('/path', handler)
router.post('/path', handler)
router.put('/path', handler)
router.delete('/path', handler)
router.patch('/path', handler)
router.all('/path', handler)

// App-level routes
app.get('/path', handler)
app.post('/path', handler)
app.use('/prefix', router)
app.use('/prefix', require('./routes/module'))

// Parameter definitions
router.param('id', handler)
req.params.id
req.query.param
req.body.field
```

Look in: `routes/`, `src/routes/`, `app.js`, `server.js`, `index.js`

### Flask / Python

```python
# Route decorators
@app.route('/path', methods=['GET', 'POST'])
@blueprint.route('/path')

# Blueprint registration
app.register_blueprint(bp, url_prefix='/api')

# Flask-RESTful
api.add_resource(Resource, '/path')

# FastAPI
@app.get('/path')
@app.post('/path')
@router.get('/path')
@router.post('/path')
app.include_router(router, prefix='/api')
```

Look in: `app.py`, `main.py`, `routes.py`, `views.py`, `api/`, `blueprints/`

### Django / Python

```python
# URL patterns
urlpatterns = [
    path('api/users/', views.UserList.as_view()),
    path('api/users/<int:pk>/', views.UserDetail.as_view()),
    re_path(r'^api/search/(?P<query>.+)/$', views.search),
]

# DRF routers
router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns += router.urls

# Include patterns
path('api/', include('app.urls')),
```

Look in: `urls.py`, `*/urls.py`, `views.py`, `*/views.py`, `viewsets.py`

### Spring Boot / Java

```java
// Controller annotations
@RestController
@RequestMapping("/api/users")
@GetMapping("/list")
@PostMapping("/create")
@PutMapping("/{id}")
@DeleteMapping("/{id}")
@PatchMapping("/{id}")

// Method parameters
@PathVariable Long id
@RequestParam String query
@RequestBody UserDto user
@RequestHeader("Authorization") String auth
```

Look in: `*Controller.java`, `*Resource.java`, `*Endpoint.java`

### Laravel / PHP

```php
// Route definitions
Route::get('/users', [UserController::class, 'index']);
Route::post('/users', [UserController::class, 'store']);
Route::put('/users/{id}', [UserController::class, 'update']);
Route::delete('/users/{id}', [UserController::class, 'destroy']);

// Resource routes (generates CRUD)
Route::resource('users', UserController::class);
Route::apiResource('users', UserController::class);

// Route groups
Route::prefix('api')->group(function () { ... });
Route::middleware('auth')->group(function () { ... });
```

Look in: `routes/api.php`, `routes/web.php`

### Ruby on Rails

```ruby
# Resource routes
resources :users
resources :users, only: [:index, :show, :create]
resource :profile

# Individual routes
get '/search', to: 'search#index'
post '/auth/login', to: 'auth#login'

# Namespace/scope
namespace :api do
  namespace :v1 do
    resources :users
  end
end
```

Look in: `config/routes.rb`

### Go / Gin

```go
// Gin routes
r.GET("/users", listUsers)
r.POST("/users", createUser)
r.PUT("/users/:id", updateUser)
r.DELETE("/users/:id", deleteUser)

// Groups
api := r.Group("/api")
{
    api.GET("/users", listUsers)
    v1 := api.Group("/v1")
    {
        v1.GET("/items", listItems)
    }
}

// Chi router
r.Get("/users", listUsers)
r.Post("/users", createUser)
r.Route("/users/{id}", func(r chi.Router) {
    r.Get("/", getUser)
    r.Delete("/", deleteUser)
})
```

Look in: `main.go`, `routes.go`, `router.go`, `handler/`, `handlers/`

### ASP.NET / C#

```csharp
// Controller attributes
[ApiController]
[Route("api/[controller]")]
[HttpGet]
[HttpGet("{id}")]
[HttpPost]
[HttpPut("{id}")]
[HttpDelete("{id}")]

// Minimal API (ASP.NET 6+)
app.MapGet("/users", GetUsers);
app.MapPost("/users", CreateUser);
app.MapPut("/users/{id}", UpdateUser);
app.MapDelete("/users/{id}", DeleteUser);
```

Look in: `*Controller.cs`, `Program.cs`, `Startup.cs`

---

## Response Analysis

### Expected Status Codes by Method

| Scenario                        | Expected Status Code |
|---------------------------------|----------------------|
| GET success                     | 200 OK               |
| GET resource not found          | 404 Not Found        |
| POST resource created           | 201 Created          |
| POST validation error           | 400 Bad Request      |
| PUT/PATCH success               | 200 OK or 204        |
| DELETE success                  | 200 OK or 204        |
| Unauthenticated request         | 401 Unauthorized     |
| Insufficient permissions        | 403 Forbidden        |
| Method not allowed on endpoint  | 405 Method Not Allowed|
| Rate limit exceeded             | 429 Too Many Requests|
| Server error                    | 500 Internal Server Error |

### Content-Type Validation

APIs should return consistent content types:

- JSON APIs: `application/json` or `application/json; charset=utf-8`
- XML APIs: `application/xml` or `text/xml`
- GraphQL: `application/json`
- File downloads: appropriate MIME type (`application/pdf`, `image/png`, etc.)

Flag mismatches such as:
- API returning `text/html` instead of `application/json`
- Missing `Content-Type` header entirely
- Inconsistent charset declarations

### Response Body Structure Analysis

**Consistent envelope pattern** (check if the API uses one):
```json
{
  "status": "success",
  "data": { ... },
  "message": "OK"
}
```

**Pagination patterns** (check for consistency):
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

Or cursor-based:
```json
{
  "data": [...],
  "next_cursor": "abc123",
  "has_more": true
}
```

**Error response patterns** (should be consistent across all endpoints):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [
      {"field": "email", "message": "This field is required"}
    ]
  }
}
```

Or RFC 7807 Problem Details:
```json
{
  "type": "https://example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Email is required",
  "instance": "/api/users"
}
```

Flag endpoints that deviate from the established error format.

### Excessive Data Exposure Detection

Compare response fields against the spec. Flag any field present in the response
but absent from the specification:

- Password hashes in user responses
- Internal IDs or database identifiers
- Debug information or stack traces
- Server internals (versions, paths, configuration)
- Other users' data in list responses
- Sensitive fields like SSN, credit card numbers, tokens

This maps to OWASP API3:2023 -- Broken Object Property Level Authorization.
