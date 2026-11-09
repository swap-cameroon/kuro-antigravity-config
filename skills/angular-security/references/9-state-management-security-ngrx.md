## 9. State Management Security (NgRx)

### DevTools in Production

```typescript
// MUST disable in production
provideStoreDevtools({
  maxAge: 25,
  logOnly: environment.production,
  // Exclude sensitive properties even in dev
  actionSanitizer: (action) => ({
    ...action,
    payload: action.payload?.password
      ? { ...action.payload, password: "***" }
      : action.payload,
  }),
});
```

### SignalStore (@ngrx/signals)

`withDevtools()` has the same exposure concerns — apply production exclusion patterns.

### State Persistence Rules

- Libraries like `ngrx-store-localstorage` persist to localStorage — never store tokens or PII
- Encrypt sensitive data before persisting
- Clear persisted state on logout
- Implement version migration for state structure changes (prevent deserialization attacks)
