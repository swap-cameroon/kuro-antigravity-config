### C3 — Validate All Input & Handle Exceptions

*All input is untrusted. Validate syntactically AND semantically. Fail securely.*

**Validation rules — apply on every input boundary:**

| Rule | Implementation |
|---|---|
| Validate server-side | Client-side validation is UX only — never trust it |
| Allowlist over denylist | Define what IS valid, reject everything else |
| Validate type, length, range, format | Schema validation (Zod, Joi, Pydantic, marshmallow) |
| Canonicalize before validating | Decode, normalize, then check (prevents double-encoding bypass) |
| Validate semantically | Start date < end date, quantity > 0, price matches server catalog |

**Schema validation — always use a validation library:**

```typescript
// ✅ Zod — validate at the boundary
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(254),
  name: z.string().min(1).max(100).trim(),
  age: z.number().int().min(13).max(150),
  role: z.enum(['user', 'editor']),  // never allow 'admin' from input
});

// In route handler — validate before any processing
const data = CreateUserSchema.parse(req.body);  // throws on invalid
```

```python
# ✅ Pydantic — validate at the boundary
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUser(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=150)
    role: Literal['user', 'editor']  # never allow 'admin' from input

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        return v.strip()
```

**Mass assignment prevention — always use explicit field allowlists:**

```python
# ❌ Mass assignment — attacker sends {"role": "admin", "is_staff": true}
user = User(**request.data)

# ✅ Explicit allowlist via serializer/DTO
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'age']  # role deliberately excluded
        read_only_fields = ['id', 'created_at']
```

**Exception handling — fail secure, never fail open:**

```python
# ❌ Fail-open — exception bypasses authorization
try:
    if not user.has_permission('admin'):
        raise PermissionDenied()
except Exception:
    pass  # silently continues — CRITICAL vulnerability

# ✅ Fail-closed — exception denies access
try:
    authorized = user.has_permission('admin')
except Exception:
    authorized = False  # default to DENY
    logger.error("Authorization check failed", exc_info=True)
if not authorized:
    raise PermissionDenied()
```

**Error responses — never leak internals:**

```typescript
// ❌ Leaks stack trace, DB schema, internal paths
res.status(500).json({ error: err.message, stack: err.stack });

// ✅ Safe error response with correlation ID
const errorId = crypto.randomUUID();
logger.error({ errorId, err });  // full details in logs only
res.status(500).json({
  error: 'Internal server error',
  errorId,  // user can report this for debugging
});
```
