## 9) State Management Strategy

| State type | Solution |
|---|---|
| **Simple / local** | Plain `signal()` + `computed()` inside components |
| **Medium feature state** | `signalState()` (NgRx Signals) |
| **Complex / enterprise** | **NgRx SignalStore** — shared state, side effects, plugins |
| **Legacy large codebases** | **NgRx Store** (Redux) — maintain, don't adopt fresh |

### NgRx SignalStore (Recommended)

```typescript
// features/users/data-access/users.store.ts
import { signalStore, withState, withComputed, withMethods, patchState } from '@ngrx/signals';
import { withEntities, setAllEntities } from '@ngrx/signals/entities';
import { rxMethod } from '@ngrx/signals/rxjs-interop';

type UsersState = {
  isLoading: boolean;
  filter: string;
};

export const UsersStore = signalStore(
  { providedIn: 'root' },
  withState<UsersState>({ isLoading: false, filter: '' }),
  withEntities<User>(),
  withComputed((store) => ({
    filteredUsers: computed(() =>
      store.entities().filter(u => u.name.includes(store.filter()))
    ),
  })),
  withMethods((store, usersService = inject(UsersService)) => ({
    updateFilter(filter: string) {
      patchState(store, { filter });
    },
    loadUsers: rxMethod<void>(
      pipe(
        tap(() => patchState(store, { isLoading: true })),
        switchMap(() => usersService.getAll()),
        tap(users => patchState(store, setAllEntities(users), { isLoading: false }))
      )
    ),
  }))
);
```

**Key patterns**
- One **SignalStore per feature** domain.
- Co-locate state, updaters, and effects in a single store file.
- Use `patchState()` for immutable state updates.
- Use `rxMethod()` from `@ngrx/signals/rxjs-interop` for async side effects.
- Use `{ providedIn: 'root' }` for global stores; provide at route level for scoped stores.
