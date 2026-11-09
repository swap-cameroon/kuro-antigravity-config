### Idempotency for Critical Operations

```typescript
// ✅ Idempotency key for financial/critical operations
async function processPayment(req: Request, res: Response) {
  const idempotencyKey = req.headers['idempotency-key'] as string;
  if (!idempotencyKey) {
    return res.status(400).json({ error: 'Idempotency-Key header required' });
  }

  // Check if already processed
  const existing = await cache.get(`idempotency:${idempotencyKey}`);
  if (existing) {
    return res.status(200).json(JSON.parse(existing));
  }

  // Process and cache result
  const result = await executePayment(req.body);
  await cache.set(`idempotency:${idempotencyKey}`, JSON.stringify(result), 'EX', 86400);
  return res.status(201).json(result);
}
```
