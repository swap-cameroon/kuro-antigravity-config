### C10 — Prevent Server-Side Request Forgery (SSRF)

*Never let user input control where your server makes requests.*

```python
# ❌ SSRF — user controls the URL
url = request.data.get('webhook_url')
response = requests.get(url)  # attacker: http://169.254.169.254/latest/meta-data/

# ✅ Allowlist-based validation
from urllib.parse import urlparse
import ipaddress

ALLOWED_DOMAINS = {'api.trusted.com', 'hooks.slack.com'}
BLOCKED_RANGES = [
    ipaddress.ip_network('169.254.0.0/16'),    # AWS metadata
    ipaddress.ip_network('10.0.0.0/8'),         # private
    ipaddress.ip_network('172.16.0.0/12'),      # private
    ipaddress.ip_network('192.168.0.0/16'),     # private
    ipaddress.ip_network('127.0.0.0/8'),        # loopback
]

def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Only HTTP(S) allowed")
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")
    # Resolve and check IP to prevent DNS rebinding
    ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
    for blocked in BLOCKED_RANGES:
        if ip in blocked:
            raise ValueError("IP range blocked")
    return url
```

**SSRF prevention rules:**
- Allowlist domains and/or IP ranges — never denylist
- Block `file://`, `gopher://`, `dict://`, `ftp://` schemes
- Resolve DNS and verify IP before making request (prevent DNS rebinding)
- Block cloud metadata endpoints: `169.254.169.254`, `metadata.google.internal`
- Set timeouts on all outbound requests
- Flag any parameter named: `url`, `uri`, `link`, `callback`, `webhook`, `redirect`, `dest`, `target`, `fetch`, `proxy`, `endpoint`
