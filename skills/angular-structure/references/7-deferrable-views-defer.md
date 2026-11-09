## 7) Deferrable Views (`@defer`)

```html
@defer (on viewport; prefetch on idle) {
  <app-heavy-chart [data]="chartData()" />
} @placeholder (minimum 200ms) {
  <div class="skeleton-chart"></div>
} @loading (after 100ms; minimum 500ms) {
  <app-spinner />
} @error {
  <p>Failed to load chart component.</p>
}
```

**Available triggers**

| Trigger | Behavior |
|---|---|
| `on idle` | Browser reaches idle state (default) |
| `on immediate` | After non-deferred content renders |
| `on timer(5s)` | After specified delay |
| `on viewport` | Placeholder enters viewport |
| `on interaction` | User clicks or presses key |
| `on hover` | Mouse enters or focusin |
| `when condition` | Custom boolean expression |

**Prefetching**: `prefetch on idle` loads JavaScript before the trigger fires, so rendering is instant when triggered. Reduces initial bundle size by 30-50%.
