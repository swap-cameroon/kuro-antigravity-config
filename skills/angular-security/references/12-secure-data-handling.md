## 12. Secure Data Handling

### Rules

- Never store passwords, tokens, or PII in localStorage/sessionStorage
- Store sensitive data in Angular services (memory) only
- Clear all stored data on logout
- Mask sensitive data in UI
- Never log sensitive data to console in production

### Data Masking

```typescript
const maskCreditCard = (cc: string): string => cc.replace(/\d(?=\d{4})/g, "*");
// "1234567890123456" → "************3456"

const maskEmail = (email: string): string => {
  const [local, domain] = email.split("@");
  return `${local.slice(0, 2)}***@${domain}`;
};
// "user@example.com" → "us***@example.com"
```
