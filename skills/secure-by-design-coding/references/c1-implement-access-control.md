### C1 — Implement Access Control

*Every resource access must be authorized. Authentication ≠ authorization.*

**Principles:**
- **Deny by default** — no access unless explicitly granted
- **Centralize access control** — one verification layer, not scattered checks
- **Force every request through verification** — use middleware/filters/decorators as Policy Enforcement Points
- **Least privilege** — minimum permissions for minimum duration
- **Never hard-code roles** — use permission-based checks, not role string comparisons

**Patterns to always apply:**

```python
# ❌ Hard-coded role check — fragile, unauditable
if user.role == "admin":
    delete_account(account_id)

# ✅ Permission-based check — flexible, auditable
if user.has_permission("accounts:delete"):
    delete_account(account_id)
```

```python
# ❌ Authentication without authorization — user is logged in but may not own this
def get_order(request, order_id):
    return Order.objects.get(id=order_id)

# ✅ Ownership enforced at the query level
def get_order(request, order_id):
    return get_object_or_404(Order, id=order_id, user=request.user)
```

```typescript
// ❌ No access control middleware
router.delete('/users/:id', deleteUser);

// ✅ Layered: authN → authZ → ownership
router.delete('/users/:id',
  authenticate,
  authorize('users:delete'),
  verifyOwnership('user'),
  deleteUser
);
```

**When writing any endpoint, always include:**
1. Authentication check (who is this?)
2. Authorization check (are they allowed this action?)
3. Ownership/scope check (do they own this specific resource?)
4. Tenant isolation (in multi-tenant systems — every query filters by tenant)

**Multi-tenancy rule:** Every database query in a multi-tenant system MUST include
a tenant filter. No exceptions. Cache keys, file paths, background jobs, and
search indexes must also be tenant-scoped.
