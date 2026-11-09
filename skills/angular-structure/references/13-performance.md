## 13) Performance

### Zoneless Change Detection (Default in Angular 21+)

```typescript
// app.config.ts
providers: [
  provideZonelessChangeDetection(),
]
```

**Benefits**: 60% faster startup, smaller bundle (no zone.js), no more `ExpressionChangedAfterItHasBeenChecked` errors. Requires signals-based reactivity.

### Performance Checklist

- Use `@defer` for below-the-fold and heavy components (30-50% bundle reduction).
- Use `track` in `@for` with stable unique IDs (never use object references).
- Use `computed()` for derived values (memoized, lazy).
- Use `httpResource` with reactive signals (auto-cancels stale requests).
- Enable incremental hydration for SSR apps.
- Use `NgOptimizedImage` for image optimization.
- Use `ChangeDetectionStrategy.OnPush` everywhere (or go zoneless).
- Split code by **route** with `loadChildren` / `loadComponent`.
