## 11) Forms

### Typed Reactive Forms (Production Standard)

```typescript
interface UserForm {
  name: FormControl<string>;
  email: FormControl<string>;
  address: FormGroup<{
    street: FormControl<string>;
    city: FormControl<string>;
  }>;
}

@Component({ ... })
export class UserFormComponent {
  private fb = inject(NonNullableFormBuilder);
  private defaultValues = input<UserVM | null>(null);

  form = this.fb.group<UserForm>({
    name: this.fb.control('', [Validators.required, Validators.minLength(2)]),
    email: this.fb.control('', [Validators.required, Validators.email]),
    address: this.fb.group({
      street: this.fb.control(''),
      city: this.fb.control(''),
    }),
  });

  submitted = output<UserFormValue>();

  constructor() {
    effect(() => {
      const defaults = this.defaultValues();
      if (defaults) this.form.patchValue(defaults);
    });
  }

  onSubmit() {
    if (this.form.valid) {
      this.submitted.emit(this.form.getRawValue());
    }
  }
}
```

> **Signal Forms** (experimental in Angular 21) use a single `[field]` directive and signal-based form models. Not production-ready yet — use typed Reactive Forms.
