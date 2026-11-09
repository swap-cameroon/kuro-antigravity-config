## 6) New Control Flow Syntax

The built-in control flow (stable since Angular 17) replaces `*ngIf`, `*ngFor`, `*ngSwitch`:

```html
<!-- @if / @else if / @else -->
@if (user(); as user) {
  <h1>Welcome, {{ user.name }}</h1>
} @else {
  <h1>Please log in</h1>
}

<!-- @for with track (required) -->
@for (item of items(); track item.id) {
  <app-item-card [item]="item" />
} @empty {
  <p>No items found.</p>
}

<!-- @switch -->
@switch (status()) {
  @case ('loading') { <app-spinner /> }
  @case ('error') { <app-error [message]="error()" /> }
  @case ('success') { <app-content [data]="data()" /> }
}
```

**Key advantages**
- Better type narrowing in templates.
- `track` expression is required in `@for` (performance guarantee).
- `@empty` block for empty collections.
- Contextual variables: `$index`, `$count`, `$first`, `$last`, `$even`, `$odd`.
