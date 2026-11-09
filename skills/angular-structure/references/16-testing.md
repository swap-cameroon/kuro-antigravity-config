## 16) Testing

| Layer | Tool | Notes |
|---|---|---|
| **Unit / Component** | **Vitest** | Default in Angular 21+ CLI. ~6x faster cold start than Jest, native ESM/TS. |
| **Component integration** | Vitest + `TestBed` | Test components with real providers, interceptors, stores. |
| **E2E** | **Playwright** | 3-5 critical flows in CI. UI Mode for time-traveling debugger. |
| **API mocking** | **MSW** or `HttpTestingController` | Intercept at the network level for realistic mocks. |

```typescript
// user-list.component.spec.ts
describe('UserListComponent', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [provideHttpClientTesting()],
      deferBlockBehavior: DeferBlockBehavior.Manual,
    });
  });

  it('should display users', async () => {
    const fixture = TestBed.createComponent(UserListComponent);
    const httpTesting = TestBed.inject(HttpTestingController);

    fixture.detectChanges();
    httpTesting.expectOne('/api/users').flush([{ id: '1', name: 'Alice' }]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Alice');
  });
});
```

- Co-locate `*.spec.ts` with source files.
- Factories/builders under `features/*/testing/` and `test/`.
- Jest is valid only for legacy projects where migration cost is prohibitive.
