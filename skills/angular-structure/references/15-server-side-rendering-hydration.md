## 15) Server-Side Rendering & Hydration

```typescript
// app.config.server.ts
export const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    provideServerRouteConfig([
      { path: '', renderMode: RenderMode.Server },
      { path: 'about', renderMode: RenderMode.Prerender },
    ]),
  ],
};

// app.config.ts — client hydration
providers: [
  provideClientHydration(
    withEventReplay(),
    withIncrementalHydration()
  ),
]
```

### Incremental Hydration

```html
@defer (hydrate on viewport) {
  <app-product-reviews />
}

@defer (hydrate on interaction) {
  <app-comment-form />
}

@defer (hydrate never) {
  <app-static-footer />
}
```

Hydration triggers: `on viewport`, `on interaction`, `on idle`, `on timer`, `on hover`, `when condition`, `never`.
