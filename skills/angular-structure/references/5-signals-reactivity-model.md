## 5) Signals — Reactivity Model

Angular's signals system is the foundation of modern Angular reactivity. All signal primitives are **stable** as of Angular 20+.

### Core Primitives

```typescript
// Writable signal
const count = signal(0);
count.set(5);
count.update(v => v + 1);

// Computed (read-only, memoized, lazy)
const doubled = computed(() => count() * 2);

// LinkedSignal (writable computed — resets when source changes)
const options = signal(['express', 'standard']);
const selected = linkedSignal(() => options()[0]);
selected.set(options()[1]); // manual override allowed

// Effect (side effects — runs asynchronously)
effect(() => {
  console.log('Count changed:', count());
});
```

### Signal-Based Component APIs

```typescript
@Component({
  selector: 'app-user-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>{{ name() }}</h2>
    @if (isAdmin()) { <span>Admin</span> }
  `
})
export class UserCardComponent {
  // Signal inputs (replaces @Input())
  name = input.required<string>();
  role = input<string>('viewer');

  // Computed from inputs
  isAdmin = computed(() => this.role() === 'admin');

  // Model signal (two-way binding with [(value)])
  value = model<string>('');

  // Signal outputs (replaces @Output())
  saved = output<void>();

  // Signal queries (replaces @ViewChild / @ContentChild)
  myInput = viewChild<ElementRef>('myInput');
  panels = contentChildren(PanelComponent);
}
```

**Best practices**
- Prefer `computed()` for derived values (memoized, lazy).
- Use `linkedSignal()` only when you need both reactivity AND manual writes.
- Use `effect()` sparingly — last resort for side effects (logging, analytics, external APIs).
- Use `untracked()` to read signals without creating dependencies.
