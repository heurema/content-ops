---
name: content-ops-doctor
description: Validate content-ops configuration by pinging each platform's auth endpoint. Reports OK/FAIL per service. Run this after initial setup.
---

Check that all platform credentials are configured correctly.

## Steps

1. Check each environment variable and ping each platform:

   **dev.to:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -H "api-key: $DEVTO_API_KEY" \
     https://dev.to/api/users/me
   ```
   Expected: 200. If 401: DEVTO_API_KEY is invalid.

   **Hashnode:**
   ```bash
   curl -s -X POST https://gql.hashnode.com \
     -H "Authorization: $HASHNODE_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query":"{ me { id } }"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else 'FAIL')"
   ```
   Check both `HASHNODE_TOKEN` and `HASHNODE_PUBLICATION_ID` are set.

   **Twitter/X:**
   Report whether all 4 X_* vars are set. No live ping (write-only free tier).

2. Report results in a table:

   ```
   Platform    | Status | Detail
   ------------|--------|--------
   dev.to      | OK  | Authenticated as @username
   Hashnode    | OK  | Publication ID: pub123
   Twitter/X   | SET | Credentials present (not verified — write-only tier)
   ```

3. For any FAIL: link to the relevant section in `docs/setup.md`.

## Notes

- Run: "content-ops doctor" or "/content-ops-doctor"
- Reddit is intentionally not listed (deferred to v2).
