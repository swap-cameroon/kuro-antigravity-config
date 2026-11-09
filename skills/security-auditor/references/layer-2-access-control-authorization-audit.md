## Layer 2 — Access Control & Authorization Audit

*Dedicated to the question: "Can User A access User B's data or perform actions outside their permission list?"*

### RBAC / ABAC Verification
- Map all roles defined in the system (admin, user, moderator, owner, viewer, etc.)
- For each protected endpoint, verify:
  1. Is authentication required? (authN)
  2. Is the correct role/permission checked? (authZ)
  3. Is object-level ownership verified? (not just role, but does this user own this resource?)
- Flag endpoints with authentication but no authorization
- Flag endpoints with role check but no ownership check
- Flag `admin_required` decorators missing on admin routes
- Flag permission logic implemented in middleware that can be bypassed per-route

### Permission Checklist by Resource Operation

| Operation | Required checks |
|---|---|
| Read resource | Authenticated + owns resource OR has read permission |
| Update resource | Authenticated + owns resource OR has write permission |
| Delete resource | Authenticated + owns resource OR has delete/admin permission |
| List resources | Authenticated + scoped to own resources (not all records) |
| Admin action | Authenticated + admin/staff role + audit log |
| Cross-user action | Explicit delegation/sharing grant recorded in DB |

### Multi-Tenancy Isolation Audit
For every model/table that holds tenant-scoped data, verify:
- Every query filters by `tenant_id` / `org_id` / equivalent
- Shared resources (config, templates, assets) are correctly scoped
- API responses never include data from other tenants
- Background jobs/tasks include tenant context
- Cache keys are prefixed with tenant ID
- File storage paths include tenant ID (no shared paths)
- Search indexes are tenant-isolated

### JWT / Token Authorization Audit
- Does the token carry role/permission claims that are **also verified server-side**?
- Can the token's `sub` (subject) be swapped to impersonate another user?
- Are admin endpoints checking the token's `scope` / `permissions` claim?
- Is token revocation implemented for logout/account deactivation?
- Are refresh tokens rotated and old tokens invalidated?
