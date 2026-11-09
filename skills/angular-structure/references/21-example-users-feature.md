## 21) Example: Users Feature

### Routes
```typescript
// features/users/users.routes.ts
export const USERS_ROUTES: Routes = [
  { path: '', component: UserListComponent },
  { path: 'new', component: UserFormComponent },
  { path: ':id', component: UserDetailComponent },
  { path: ':id/edit', component: UserFormComponent },
];
```

### List Page (Smart Component)
```typescript
// features/users/user-list/user-list.component.ts
@Component({
  standalone: true,
  imports: [PageHeader, UsersTable],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="container">
      <app-page-header title="Users" subtitle="Manage accounts" />
      @if (store.isLoading()) {
        <app-spinner />
      } @else {
        <app-users-table
          [users]="store.filteredUsers()"
          (edit)="onEdit($event)"
        />
      }
    </main>
  `,
})
export class UserListComponent implements OnInit {
  protected store = inject(UsersStore);
  private router = inject(Router);

  ngOnInit() {
    this.store.loadUsers();
  }

  onEdit(user: User) {
    this.router.navigate(['/users', user.id, 'edit']);
  }
}
```

### Create / Edit with Shared Form
```html
<!-- Create -->
<main class="container">
  <app-page-header title="Add User" />
  <app-user-form (submitted)="store.createUser($event)" />
</main>

<!-- Edit -->
<main class="container">
  <app-page-header title="Edit User" />
  <app-user-form [defaultValues]="user()" (submitted)="store.updateUser(id(), $event)" />
</main>
```
