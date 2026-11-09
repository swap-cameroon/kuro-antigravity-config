## 11. Secure Build & Deployment

### Environment Files — NOT Secret Storage

```typescript
// environment.prod.ts — compiled into the bundle!
export const environment = {
  production: true,
  apiUrl: "https://api.example.com",
  // ❌ NEVER put secrets here — they are bundled into client code
};

// ✅ Use runtime config fetched from server for sensitive values
```

### Angular CLI Build Configuration

```json
// angular.json — production configuration
{
  "configurations": {
    "production": {
      "optimization": true,
      "sourceMap": false,
      "namedChunks": false,
      "extractLicenses": true,
      "outputHashing": "all",
      "security": {
        "autoCsp": true
      }
    }
  }
}
```

### Rules

- **Source maps**: Disable in production. If using Sentry, upload maps then delete from deployment
- **Environment files**: Never contain secrets — use runtime config from server
- **AutoCSP**: Enable for hash-based CSP protection
- **console.log**: Strip in production builds
- Known issue: `ng serve` with esbuild may inject inline source maps even when disabled (angular/angular-cli#31331)
