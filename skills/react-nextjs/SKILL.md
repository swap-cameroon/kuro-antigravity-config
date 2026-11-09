---
name: react-nextjs
description: "Build and review React and Next.js (App Router) apps: components, server vs client, data fetching, state, forms, performance, testing. Use when the chosen frontend stack is React or Next.js."
license: MIT
metadata:
  version: "1.0.0"
---

# React & Next.js

React counterpart to `angular-*` skills. Quality bar for UX/a11y is `ui-design-a11y`; security: `secure-by-design-coding` (XSS, CSRF, auth).

## Components
- Function components + hooks; small, single-purpose, composition over props explosion. TypeScript strict; props typed; no `any`.
- Derive state instead of syncing it (compute during render); `useEffect` is for synchronizing with external systems only, not for data derivation or event handling. Keys stable and unique (never array index for dynamic lists).
- Memoization (`useMemo`, `useCallback`, `React.memo`) only after profiling; prefer fixing structure. Check whether the React Compiler is enabled before hand-memoizing.

## Next.js App Router
- **Server Components by default**; add `"use client"` only for interactivity, browser APIs or client state, and push it to the leaves. Never import server-only code (secrets, DB) into client modules (`server-only` package).
- Data: fetch in Server Components (`async` component) close to where it is used; parallelize with `Promise.all`; stream with `Suspense` + `loading.tsx`; caching/revalidation explicit (`revalidate`, tags, `revalidateTag`) and verified for the installed major version (caching defaults changed across releases - read the docs for your version).
- Mutations: Server Actions or route handlers; **validate input with Zod on the server**, check authn/authz inside every action, return typed results, handle errors with `error.tsx` and `useActionState`.
- Routing: layouts for shared UI, route groups, parallel/intercepting routes only when needed, `generateMetadata` for SEO, `next/image` and `next/font`, dynamic imports for heavy client widgets.

## State & forms
Server state via TanStack Query (or RSC + revalidation); local state with `useState`/`useReducer`; global client state sparingly (Zustand/Context for truly global, split contexts to avoid rerenders). Forms: React Hook Form + Zod resolver or native form + Server Actions with progressive enhancement; accessible labels and errors.

## Performance
Measure first (React Profiler, Lighthouse, Web Vitals LCP/INP/CLS). Ship less JS: server rendering, code-splitting, tree-shakeable imports, avoid large client libs. Virtualize long lists; debounce inputs; reserve image space; avoid layout thrash.

## Security
No `dangerouslySetInnerHTML` without sanitization (DOMPurify); validate and escape URLs (`javascript:`); CSP via middleware/headers; httpOnly+SameSite cookies for sessions; CSRF protection for cookie auth; env vars: only `NEXT_PUBLIC_*` reach the browser.

## Testing
Vitest/Jest + React Testing Library (query by role/label, test behavior), MSW for network, Playwright for critical journeys + axe a11y checks, Storybook for component states.

## Review checklist
Server/client boundary minimal - no effect-driven derived state - server-side validation and authz in actions - Suspense/error boundaries present - bundle size checked - a11y checks pass - tests cover user-visible behavior.
