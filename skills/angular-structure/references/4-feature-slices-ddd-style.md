## 4) Feature Slices (DDD-style)

Each feature encapsulates UI, data-access, and local state.

```
features/users/
  users.routes.ts               # lazy-loaded route config for this feature
  user-list/
    user-list.component.ts      # smart: orchestrates data + renders UI
    user-list.component.html
    user-list.component.spec.ts
  user-detail/
    user-detail.component.ts
  user-form/
    user-form.component.ts      # shared between create/edit
  data-access/
    users.service.ts            # HTTP client
    users.store.ts              # NgRx SignalStore
    users.model.ts              # DTOs & ViewModels
    users.adapter.ts            # DTO <-> VM mappings
  testing/
    builders.ts                 # test factories/mocks
```

**Rules**
- **Smart components** (pages) orchestrate state and navigation; **dumb components** render.
- **data-access/** keeps backend specifics (endpoints, DTOs) isolated; never leak raw DTOs to components.
- Reuse the **same form** component for create/edit — pass `defaultValues` via signal inputs and an `onSubmit` output.
- Cross-feature imports should go through a barrel `index.ts` if needed — prefer minimal cross-feature coupling.
