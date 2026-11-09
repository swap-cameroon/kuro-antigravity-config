### C4 — Address Security from the Start

*Security is a design constraint, not a feature to add later.*

**Before writing any feature, answer these questions:**

1. **What data does this touch?** Classify: public / internal / confidential / restricted
2. **Who should access this?** Define roles, permissions, and ownership rules
3. **What are the trust boundaries?** User input → validation → business logic → data layer
4. **What could go wrong?** Think through abuse cases, not just happy paths:
   - Can a user manipulate prices, quantities, or discounts?
   - Can a user skip required steps in a workflow?
   - Can a user access another user's data by changing an ID?
   - Can a user replay, reorder, or race requests?
5. **What are the compliance requirements?** PII handling, data retention, audit logging

**Threat-aware development checklist for every feature:**

```
□ Authentication required?
□ Authorization with ownership check?
□ Input validated at boundary (schema validation)?
□ Output encoded for context (HTML, JSON, URL)?
□ Sensitive data encrypted at rest and in transit?
□ Rate limiting on sensitive operations?
□ Audit logging for state-changing actions?
□ Error handling fails closed (deny on exception)?
□ No secrets in code, logs, or error responses?
□ Race conditions prevented (atomic operations)?
```
