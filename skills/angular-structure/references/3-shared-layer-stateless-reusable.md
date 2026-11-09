## 3) Shared Layer (Stateless & Reusable)

```
shared/
  ui/
    PageHeader/
    DataTable/
    EmptyState/
    Skeleton/
    Button/
    Modal/
  directives/
    click-outside.directive.ts
    autofocus.directive.ts
  pipes/
    date-format.pipe.ts
    truncate.pipe.ts
  utils/
    date.ts
    array.ts
  styles/
    tokens.css
    globals.css
```

**Rules**
- **No data fetching** or business logic here.
- Components are presentational (inputs in, outputs out).
- Keep design-system atoms/molecules here; domain widgets stay inside features.
- Prefer **Angular CDK** primitives for accessible, unstyled components.
- Use `ChangeDetectionStrategy.OnPush` on all shared components.
