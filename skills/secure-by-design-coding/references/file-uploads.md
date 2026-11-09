### File Uploads

```typescript
// ✅ Secure file upload handling
import path from 'path';
import crypto from 'crypto';

const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

function handleUpload(file: Express.Multer.File): string {
  // Validate MIME type (check magic bytes, not just extension)
  if (!ALLOWED_TYPES.has(file.mimetype)) {
    throw new ValidationError('File type not allowed');
  }

  // Validate size
  if (file.size > MAX_SIZE) {
    throw new ValidationError('File too large');
  }

  // Generate random filename — never use user-supplied name
  const ext = path.extname(file.originalname).toLowerCase();
  const safeName = `${crypto.randomUUID()}${ext}`;

  // Store outside web root or on CDN with different domain
  const safePath = path.join(UPLOAD_DIR, safeName);

  // Verify no path traversal
  if (!safePath.startsWith(UPLOAD_DIR)) {
    throw new ValidationError('Invalid file path');
  }

  return safePath;
}
```
