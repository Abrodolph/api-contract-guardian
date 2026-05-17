# Engine — Contract Guardian

The engine is the classification core of API Contract Guardian. It consists of three parts that work together: a custom Bob Shell mode that applies governance rules, an MCP server that provides grounded data access, and an accuracy eval harness that measures correctness across labelled spec-diff cases.

## Architecture

```
Developer / CI
      │
      ▼
Bob Shell (--chat-mode=contract-guardian)
      │  Loads rules from .bob/custom_modes.yaml
      │  Calls MCP tools — never guesses
      ▼
MCP Server (mcp-server/server.py)
  ├── get_openapi_spec()     → reads mock-api/*.json from disk
  ├── get_consumer_registry() → returns hardcoded consumer field map
  └── find_call_sites()      → scans mock-consumers/ source code
      │
      ▼
Verdict JSON (matches engine/verdict_schema.json)
```

Classification runs through Bob Shell rather than a direct API call because the custom mode bakes the full governance ruleset into the model's instruction context. This keeps classification rules version-controlled alongside the spec files and avoids duplicating prompt logic across callers.

## The `contract-guardian` Bob mode

Defined in `.bob/custom_modes.yaml`. The mode sets Bob's role to an API contract governance specialist and supplies `customInstructions` that encode the three-verdict ruleset exactly:

**BREAKING** — response field removed or renamed; required request field added; field type changed; endpoint path or HTTP method changed; optional field made required.

**SAFE** — optional parameter or field added; new endpoint added; description-only change.

**REVIEW** — enum value removed; field nullability changes; default value changes; type widens.

The mode constrains Bob to output only a JSON object matching the verdict schema — no prose, no markdown fences. For BREAKING verdicts it is required to call `find_call_sites` before emitting the result.

Activate the mode:

```bash
bob --chat-mode=contract-guardian --auth-method api-key --yolo \
  -p "Call get_openapi_spec with version='baseline', then version='current'. \
      Compare the two specs. For BREAKING changes also call find_call_sites \
      for the affected field. Output ONLY the verdict JSON, nothing else."
```

## MCP server

**File:** `mcp-server/server.py`  
**Protocol:** MCP over stdio  
**Registration:** `.bob/mcp.json`

The server exposes three tools:

### `get_openapi_spec(version: "current" | "baseline")`

Reads and returns the OpenAPI spec JSON from disk.

- `"current"` → `mock-api/openapi.json`
- `"baseline"` → `mock-api/openapi_baseline.json`

The eval harness swaps `openapi.json` per test case; the server always reads from disk, so it picks up the substituted spec automatically.

### `get_consumer_registry()`

Returns a hardcoded map of downstream consumers to the API fields they depend on:

| Consumer | Schemas consumed |
|----------|-----------------|
| `billing-service` | User: email, full_name, id · Invoice: amount, currency, user_id, id, status |
| `mobile-bff` | User: email, full_name, id, created_at |
| `analytics-worker` | User: email, id, created_at · Invoice: amount, currency, user_id, id, created_at |

### `find_call_sites(field_name: str)`

Recursively searches `mock-consumers/` for Python files and returns every line where the field is accessed via dict subscript (`data["field"]`, `item['field']`, etc.). Returns a list of `{ name, file, line }` objects, one per match, grouped by consumer directory.

## Eval harness

Measures how accurately the contract-guardian mode classifies spec changes against ground-truth labels.

**Current accuracy: 17/18 cases — 94.4%**

### Running the harness

```bash
python engine/eval/run_eval.py
```

Requires `BOBSHELL_API_KEY` in environment or a `.env` file at the repo root:

```
BOBSHELL_API_KEY=your-key-here
```

The harness prints a results table and exits with code `0` if all cases pass, `1` otherwise — safe to wire into CI.

### How it works

1. Sorts the 18 case folders under `engine/eval/cases/` alphabetically.
2. For each case, copies `current_spec.json` over `mock-api/openapi.json`.
3. Invokes Bob with `--chat-mode=contract-guardian` and captures stdout/stderr.
4. Extracts the verdict using three fallback strategies: JSON between `---output---` markers → any JSON object containing a `"verdict"` key → bare verdict word on its own line.
5. Compares extracted verdict to `expected.json`.
6. Restores `mock-api/openapi.json` from the baseline in a `finally` block — runs even on crashes.

If the harness is interrupted mid-run, restore the spec manually:

```bash
python engine/eval/restore_spec.py
```

### Case breakdown

| Verdict | Cases |
|---------|-------|
| BREAKING | 001, 004, 005, 006, 007, 008, 009 |
| SAFE | 002, 010, 011, 012, 013, 014, 015 |
| REVIEW | 003, 016, 017, 018 |

### Adding a case

1. Create `engine/eval/cases/case_NNN_short_description/`.
2. Add `current_spec.json` — a full OpenAPI spec with exactly one change applied to the baseline.
3. Add `expected.json`:
   ```json
   { "verdict": "BREAKING" }
   ```
   Valid values: `BREAKING`, `SAFE`, `REVIEW`.

Change one thing per case. Compound diffs make failures ambiguous.

## MCP server setup

Register the server in `.bob/mcp.json` (already committed):

```json
{
  "mcpServers": {
    "contract-guardian": {
      "command": "python",
      "args": ["c:/Personal/Code/api-contract-guardian/mcp-server/server.py"]
    }
  }
}
```

Install the MCP Python SDK if not already present:

```bash
pip install mcp
```

The server runs over stdio and is started automatically by Bob Shell when the `contract-guardian` mode is active.
