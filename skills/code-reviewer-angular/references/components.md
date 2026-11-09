### 🏗️ Components

- **`OnPush` change detection** — flag every component missing `changeDetection: ChangeDetectionStrategy.OnPush`. This is non-negotiable for performance-conscious teams.
  ```ts
  // ❌ Default change detection — scans entire tree
  @Component({ selector: 'app-user' })

  // ✅ OnPush — only updates when inputs change or signals notify
  @Component({
    selector: 'app-user',
    changeDetection: ChangeDetectionStrategy.OnPush,
  })
  ```

- **`inject()` function** — flag constructor injection in new code; use `inject()` exclusively:
  ```ts
  // ❌ Constructor injection (legacy)
  constructor(private readonly userService: UserService) {}

  // ✅ inject() function
  private readonly userService = inject(UserService);
  ```

- **Signal inputs/outputs (v17.1+)** — flag `@Input()`/`@Output()` + `EventEmitter` in new components on Angular 17+; prefer `input()`, `output()`, `model()`:
  ```ts
  // ❌ Legacy decorator inputs
  @Input({ required: true }) user!: User;
  @Output() selected = new EventEmitter<User>();

  // ✅ Signal-based
  readonly user = input.required<User>();
  readonly selected = output<User>();
  ```

- **`subscribe()` in components** — flag direct `.subscribe()` calls in component code; use `toSignal()` or `async` pipe instead:
  ```ts
  // ❌ Manual subscription — memory leak risk
  ngOnInit() {
    this.userService.getUser().subscribe(u => this.user = u);
  }

  // ✅ toSignal — auto-cleaned up
  readonly user = toSignal(this.userService.getUser());
  ```

- **`@for` track** — flag `@for` loops missing a stable `track` expression:
  ```html
  <!-- ❌ Missing track — full DOM re-render on any change -->
  @for (user of users()) {
    <app-user-card [user]="user" />
  }

  <!-- ✅ Stable key -->
  @for (user of users(); track user.id) {
    <app-user-card [user]="user" />
  }
  ```

- **Template safety** — flag `[innerHTML]` bindings without `DomSanitizer`. Flag `bypassSecurityTrustHtml()` / `bypassSecurityTrustUrl()` without documented justification — these bypass Angular's XSS protection.

- **`CommonModule` imports** — flag `CommonModule` in standalone component imports; use specific imports (`NgIf`, `NgFor`, `AsyncPipe`) or preferably the new control flow syntax instead.

- **NgModule in new features** — flag new `NgModule` creation on Angular 17+; all new code should be standalone.
