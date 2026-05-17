# Contract Guardian — Demo Script

Exact commands for the two demo scenarios. Run all commands from the repo root
(`api-contract-guardian/`). Ensure `BOBSHELL_API_KEY` is set in `.env` first.

---

## Demo 1 — BREAKING change (commit blocked)

**What happens:** `email` is removed from the `User` response schema.
All three consumers read `email`, so the blast radius is 3 consumers.
The pre-commit hook fires, prints a red warning, and exits 1 — the commit is blocked.

### Step 1 — Save the current spec

```powershell
Copy-Item mock-api\openapi.json mock-api\openapi.json.demo-backup
```

### Step 2 — Apply the breaking change

Remove the `email` property from the `User` schema in `mock-api/openapi.json`.

Using Python (exact, reproducible):

```powershell
python -c "
import json
from pathlib import Path
spec = json.loads(Path('mock-api/openapi.json').read_text())
user = spec['components']['schemas']['User']
user['properties'].pop('email', None)
if 'email' in user.get('required', []):
    user['required'].remove('email')
Path('mock-api/openapi.json').write_text(json.dumps(spec, indent=2))
print('Done: email removed from User schema')
"
```

### Step 3 — Stage and attempt to commit

```powershell
git add mock-api/openapi.json
git commit -m "demo: remove email field"
```

### Expected output

```
[guardian] Classifying API change via Bob Shell...

CONTRACT GUARDIAN: BREAKING CHANGE DETECTED
  Change : Response field 'email' removed from User schema
  Impact : 3 call site(s) across 3 consumer(s)
    - billing-service: 1 call site(s)
    - mobile-bff: 1 call site(s)
    - analytics-worker: 1 call site(s)
  Commit BLOCKED. Resolve the breaking change before pushing.
```

Git exits with code 1 — the commit does not happen.

### Step 4 — Restore (after the demo)

```powershell
Copy-Item mock-api\openapi.json.demo-backup mock-api\openapi.json
git restore --staged mock-api/openapi.json
Remove-Item mock-api\openapi.json.demo-backup
```

---

## Demo 2 — SAFE change (commit proceeds)

**What happens:** an optional `phone` field is added to the `User` response schema.
Adding an optional field is non-breaking. The hook prints a green confirmation
and exits 0 — the commit goes through.

### Step 1 — Apply the safe change

```powershell
python -c "
import json
from pathlib import Path
spec = json.loads(Path('mock-api/openapi.json').read_text())
user = spec['components']['schemas']['User']
user['properties']['phone'] = {'type': 'string', 'example': '+1-555-0100'}
Path('mock-api/openapi.json').write_text(json.dumps(spec, indent=2))
print('Done: phone added to User schema (optional)')
"
```

### Step 2 — Stage and commit

```powershell
git add mock-api/openapi.json
git commit -m "feat(api): add optional phone field to User"
```

### Expected output

```
[guardian] Classifying API change via Bob Shell...

CONTRACT GUARDIAN: SAFE CHANGE
  Change : New optional field 'phone' added to User response schema
  Commit allowed.
```

Git exits 0 — the commit succeeds.

### Step 3 — Reset after demo

```powershell
git revert HEAD --no-edit
```

---

## Timing notes

- Bob Shell classification takes **20–60 seconds** depending on the model.
- Pre-warm the session: run one throwaway classification before the live demo.
- The GitHub Action shows the same verdict in the CI run log under the
  "Run Contract Guardian" step.

---

## Freeze checklist (run before going live)

- [ ] Run Demo 1 five times — confirm verdict JSON is stable run-to-run
- [ ] Run Demo 2 five times — confirm SAFE verdict and green output
- [ ] Confirm `GUARDIAN_BACKEND_URL` is set and Person B's dashboard shows the card
- [ ] Confirm Person B's Granite alert fires on the BREAKING verdict
- [ ] Record a backup video of Demo 1 in case Bob Shell is slow on demo day
