### 📦 NgRx

- **Tiered state rule** — flag NgRx used for purely local component state; use `signal()` instead. NgRx is for: global state, cross-feature shared data, and complex side effects.

- **NgRx Signal Store (v17+)** — flag class-based `@ngrx/store` for new features in modern Angular apps; prefer `signalStore()`:
  ```ts
  // ✅ NgRx Signal Store pattern
  export const UsersStore = signalStore(
    { providedIn: 'root' },
    withState(initialState),
    withComputed(({ users }) => ({
      activeUsers: computed(() => users().filter(u => u.active))
    })),
    withMethods((store, usersService = inject(UsersService)) => ({
      loadUsers: rxMethod<void>(
        pipe(
          switchMap(() => usersService.getAll()),
          tapResponse({
            next: users => patchState(store, { users }),
            error: console.error
          })
        )
      )
    }))
  );
  ```

- **Effects** — flag side effects (HTTP calls, routing, notifications) placed directly in reducers or components; use NgRx Effects or `withMethods` + `rxMethod`.
- **Selectors** — flag repeated `store.select()` calls for the same data; extract to reusable selectors.
- **`patchState`** — flag direct state mutation attempts; always use `patchState()` in Signal Store methods.
