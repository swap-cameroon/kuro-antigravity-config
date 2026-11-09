### 🖥️ Angular Universal / SSR

- **`isPlatformBrowser()`** — flag direct `window`, `document`, or `localStorage` access without platform check; these crash during SSR:
  ```ts
  // ❌ Crashes on server
  ngOnInit() { localStorage.setItem('key', 'value'); }

  // ✅ Platform-safe
  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('key', 'value');
    }
  }
  ```

- **`afterNextRender()` / `afterRender()`** — flag `ngAfterViewInit` used for browser-only DOM operations in SSR apps; use `afterNextRender()` (runs only in browser).

- **`TransferState`** — flag SSR apps making the same HTTP request on both server and client; use `TransferState` or `httpResource()` to cache server-fetched data.

- **Incremental hydration (v19+)** — flag large, below-the-fold components not using `@defer` with hydration triggers.

- **Event replay** — flag SSR apps on v18+ not enabling `withEventReplay()` in `provideClientHydration()` — user interactions before hydration are lost.
