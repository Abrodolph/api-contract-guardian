# Bob Rules for Contract Guardian Mode

These rules apply when Bob operates in `contract-guardian` mode for API contract analysis.

## Output Requirements

### JSON Format (Critical)

- **Always** output verdict JSON matching `engine/verdict_schema.json` exactly
- **Never** add prose, explanations, or markdown code fences around the JSON
- **Never** add text before or after the JSON object
- Your entire response must be parseable as valid JSON
- The JSON must be a single object with these exact keys: `verdict`, `change_summary`, `affected_field`, `blast_radius`, `reasoning`

### Verdict Schema Structure

```json
{
  "verdict": "BREAKING | SAFE | REVIEW",
  "change_summary": "string",
  "affected_field": "string | null",
  "blast_radius": {
    "consumers": [
      {
        "name": "string",
        "call_sites": [{ "file": "string", "line": 0 }]
      }
    ],
    "total_call_sites": 0
  },
  "reasoning": "string"
}
```

## Data Gathering Rules

### Always Use MCP Tools

- **Always** call `get_openapi_spec` with `version="baseline"` first
- **Always** call `get_openapi_spec` with `version="current"` second
- **Never** guess or assume spec content — always retrieve both versions
- **Never** make up consumer data — use `get_consumer_registry` if needed

### Call Site Detection for BREAKING Changes

- **Always** call `find_call_sites(field_name)` when verdict is BREAKING
- **Always** populate `blast_radius` with the results from `find_call_sites`
- **Never** guess call sites or leave blast_radius empty for BREAKING verdicts
- Group call sites by consumer name in the output

## Blast Radius Rules (Critical)

### Structure Requirements

- `blast_radius.consumers` **must be an array of objects**, never a flat string array
- Each consumer object **must have** `name` (string) and `call_sites` (array) keys
- Each call_site object **must have** `file` (string) and `line` (number) keys
- `total_call_sites` **must equal** the sum of all call_sites across all consumers

### Examples

**BREAKING verdict with call sites:**

```json
{
  "blast_radius": {
    "consumers": [
      {
        "name": "billing-service",
        "call_sites": [
          { "file": "mock-consumers/billing-service/client.py", "line": 20 }
        ]
      },
      {
        "name": "mobile-bff",
        "call_sites": [
          { "file": "mock-consumers/mobile-bff/client.py", "line": 21 },
          { "file": "mock-consumers/mobile-bff/client.py", "line": 34 }
        ]
      }
    ],
    "total_call_sites": 3
  }
}
```

**SAFE or REVIEW verdict (no call sites needed):**

```json
{
  "blast_radius": {
    "consumers": [],
    "total_call_sites": 0
  }
}
```

**NEVER do this (wrong structure):**

```json
{
  "blast_radius": {
    "consumers": ["billing-service", "mobile-bff"], // ❌ WRONG - must be objects
    "total_call_sites": 2
  }
}
```

## Classification Rules

These rules are already baked into the `contract-guardian` mode, but are repeated here for reference:

### BREAKING (any of these)

- Response field removed or renamed
- Required request field added
- Field type changed (e.g., string → integer)
- Endpoint path changed
- HTTP method changed
- Previously optional field becomes required

### SAFE (any of these)

- Optional query parameter added
- New response field added
- New endpoint added
- New optional request field added
- Description or documentation-only change

### REVIEW (requires human judgment)

- Enum value removed
- Field changes from nullable to non-nullable
- Default value changed
- Type widened (e.g., integer → number)

## Workflow

1. Call `get_openapi_spec(version="baseline")`
2. Call `get_openapi_spec(version="current")`
3. Compare the two specs and identify changes
4. Classify the change using the rules above
5. If BREAKING: call `find_call_sites(field_name)` for the affected field
6. Construct the verdict JSON with proper blast_radius structure
7. Output **only** the JSON object, nothing else

## Common Mistakes to Avoid

- ❌ Adding markdown code fences around JSON
- ❌ Adding explanatory text before or after JSON
- ❌ Simplifying blast_radius.consumers to a flat array
- ❌ Leaving blast_radius null or undefined
- ❌ Guessing call sites instead of using find_call_sites
- ❌ Not calling MCP tools to get spec data
- ❌ Mismatching total_call_sites with actual count
