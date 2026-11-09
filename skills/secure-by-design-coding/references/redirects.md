### Redirects

```typescript
// ✅ Safe redirect — relative URLs only, or strict allowlist
function safeRedirect(req: Request, res: Response) {
  const next = req.query.next as string || '/';
  const url = new URL(next, `${req.protocol}://${req.hostname}`);

  // Only allow same-origin redirects
  if (url.origin !== `${req.protocol}://${req.hostname}`) {
    return res.redirect('/');
  }
  return res.redirect(url.pathname + url.search);
}
```
