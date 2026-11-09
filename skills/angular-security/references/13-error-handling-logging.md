## 13. Error Handling & Logging

```typescript
import * as Sentry from "@sentry/angular";

// Global error handler
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  handleError(error: Error) {
    Sentry.captureException(error);
    // Don't log sensitive data
    console.error("Application error:", error.message);
  }
}

// Register
(provideAppInitializer(() => {
  Sentry.init({
    dsn: environment.sentryDsn,
    beforeSend(event) {
      if (event.user) delete event.user.email;
      return event;
    },
  });
}),
  { provide: ErrorHandler, useClass: GlobalErrorHandler });
```

### Rules

- Implement global error handler
- Display user-friendly messages — never expose stack traces
- Log to monitoring service (Sentry) — never log tokens, passwords, or PII
- Strip console.log in production
