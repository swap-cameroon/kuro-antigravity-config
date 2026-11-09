### 🔁 RxJS

**Rule of thumb: RxJS for async/events, Signals for state. Convert at component boundary with `toSignal()`.**

- **Unsubscribed observables** — flag `.subscribe()` without cleanup. Acceptable patterns: `takeUntilDestroyed()`, `async` pipe, `toSignal()`. Flag `ngOnDestroy` + manual `Subscription` arrays in new code — use `takeUntilDestroyed(this.destroyRef)` instead:
  ```ts
  // ❌ Manual unsubscribe boilerplate
  private sub = new Subscription();
  ngOnInit() { this.sub.add(obs$.subscribe(...)); }
  ngOnDestroy() { this.sub.unsubscribe(); }

  // ✅ takeUntilDestroyed
  obs$.pipe(takeUntilDestroyed()).subscribe(...);
  ```

- **`switchMap` for cancellable requests** — flag `mergeMap` or `concatMap` on search/autocomplete streams where only the latest result matters.

- **Error handling** — flag Observable chains missing `catchError` — unhandled errors complete the stream and break the UI.

- **`BehaviorSubject` as state** — flag `BehaviorSubject` used for state that is: (a) local to a component, (b) synchronous, (c) not shared across features. Replace with `signal()`.

- **Nested subscriptions** — flag `.subscribe()` inside another `.subscribe()` — use `switchMap`, `mergeMap`, or `combineLatest` instead.
