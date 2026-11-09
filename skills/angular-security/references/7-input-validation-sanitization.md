## 7. Input Validation & Sanitization

### Requirements

- Validate all user inputs on the client (UX) AND server (security boundary)
- Use Angular Validators + schema validation (Zod) for type-safe validation
- Sanitize all user-generated HTML content
- Validate file types, sizes, and names before upload
- Never execute user input as code

### Angular Pattern

```typescript
import { Validators, FormBuilder } from "@angular/forms";
import DOMPurify from "dompurify";

// Reactive form with validation
this.form = this.fb.group({
  email: ["", [Validators.required, Validators.email]],
  age: ["", [Validators.required, Validators.min(18), Validators.max(120)]],
  username: [
    "",
    [
      Validators.required,
      Validators.minLength(3),
      Validators.maxLength(20),
      Validators.pattern(/^[a-zA-Z0-9_]+$/),
    ],
  ],
});

// Sanitize HTML (pipe)
@Pipe({ name: "safeHtml", standalone: true })
export class SafeHtmlPipe implements PipeTransform {
  private sanitizer = inject(DomSanitizer);

  transform(html: string): SafeHtml {
    const sanitized = DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ["b", "i", "em", "strong", "a"],
      ALLOWED_ATTR: ["href"],
    });
    return this.sanitizer.bypassSecurityTrustHtml(sanitized);
  }
}

// Usage in template
<div [innerHTML]="userContent | safeHtml"></div>
```
