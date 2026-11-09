### Database Access

```python
# ✅ Always parameterized — never string concatenation
cursor.execute("SELECT * FROM users WHERE email = %s", [email])

# ✅ ORM with ownership filter
orders = Order.objects.filter(user=request.user, status='active')

# ✅ Bulk operations — not loops
User.objects.filter(id__in=user_ids).update(active=False)

# ✅ Atomic operations for race-prone logic
from django.db.models import F
Product.objects.filter(id=product_id, stock__gte=quantity).update(
    stock=F('stock') - quantity
)
```
