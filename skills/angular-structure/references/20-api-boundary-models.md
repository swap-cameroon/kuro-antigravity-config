## 20) API Boundary & Models

- Keep HTTP clients **inside each feature** under `data-access/`.
- Map **DTO <-> ViewModel** with adapters to decouple UI from backend changes.
- Handle **auth/error/trace** via functional interceptors at `app.config.ts`.
- Prefer **generated clients** from OpenAPI/GraphQL, wrapped by thin facades.

```typescript
// users.adapter.ts
export const toUserVM = (dto: UserDto): UserVM => ({
  id: dto.id,
  name: `${dto.firstName} ${dto.lastName}`,
  role: dto.role ?? 'user',
});
```
