### 🔵 GraphQL / Apollo Angular (if present)

- **Typed queries** — flag Apollo `useQuery` / `gql` calls without generated TypeScript types; use `graphql-codegen`.
- **`watchQuery` vs `query`** — flag `query()` used where the UI needs live cache updates; use `watchQuery()`.
- **Loading/error states** — flag components using Apollo without handling `loading` and `error` states in the template.
- **`fetchPolicy`** — flag missing `fetchPolicy` on queries where stale data is a concern.
- **Mutations and cache** — flag mutations not updating the Apollo cache (`update` function or `refetchQueries`) when they modify list data.
