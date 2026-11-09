### ⚡ Signals

- **`signal()` for local state** — flag `BehaviorSubject` used for component or feature-local state where `signal()` would suffice.

- **`computed()` for derived state** — flag computed values re-derived manually in multiple places; extract to `computed()`:
  ```ts
  // ❌ Manual derivation, duplicated
  get activeUsers() { return this.users().filter(u => u.active); }

  // ✅ computed — memoized, reactive
  readonly activeUsers = computed(() => this.users().filter(u => u.active));
  ```

- **`effect()` side effects** — flag `effect()` used to derive or transform state (that's `computed()`'s job). `effect()` is for side effects only (logging, localStorage, external calls).

- **`signal.asReadonly()`** — flag writable signals exposed publicly from services; expose `asReadonly()`:
  ```ts
  // ❌ Writable signal leaked — consumers can mutate
  readonly users = signal<User[]>([]);

  // ✅ Expose read-only; mutate only through service methods
  private readonly _users = signal<User[]>([]);
  readonly users = this._users.asReadonly();
  ```

- **`toSignal()` with `initialValue`** — flag `toSignal()` calls on Observables that may not emit immediately without an `initialValue` or `{ requireSync: true }` — results in `undefined` signal until first emission.

- **`linkedSignal()` (v19+)** — flag complex `computed()` + `effect()` combinations that reset a signal when another changes; `linkedSignal()` is the cleaner pattern.
