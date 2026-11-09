## 12) Styling

- **Tailwind CSS v4** is the recommended default. New Oxide engine (10x faster builds), CSS-first configuration, zero runtime cost.
- **Angular CDK** for accessible, unstyled component primitives.
- **Component-scoped styles** with `ViewEncapsulation.Emulated` (default) — styles are automatically scoped.
- Use `:host` for component-level styling.
- **styled-components / Emotion**: Not applicable in Angular. Avoid CSS-in-JS runtime approaches.
- Centralize design tokens in `shared/styles/tokens.css`.
- Co-locate component-specific styles with their component files.

```css
/* styles.css (global) — Tailwind v4 */
@import "tailwindcss";
```

```typescript
@Component({
  styles: `
    :host { display: block; }
  `,
  template: `
    <div class="flex items-center gap-4 p-4 rounded-lg bg-white shadow">
      <ng-content />
    </div>
  `
})
```
