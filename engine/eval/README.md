# Contract Guardian — Accuracy Eval Harness

Measures how often the Contract Guardian produces the correct verdict across a set of labelled spec-diff cases.

## Directory layout

```
engine/eval/
├── run_eval.py          # Main harness — loops cases, runs bob, scores results
├── restore_spec.py      # Emergency restore of mock-api/openapi.json from baseline
├── cases/
│   ├── case_001_breaking_field_removed/
│   │   ├── current_spec.json   # Modified spec (email removed from User)
│   │   └── expected.json       # {"verdict": "BREAKING"}
│   ├── case_002_safe_optional_param/
│   │   ├── current_spec.json   # Modified spec (sort_by param added to GET /users)
│   │   └── expected.json       # {"verdict": "SAFE"}
│   └── case_003_review_enum_removal/
│       ├── current_spec.json   # Modified spec ("pending" removed from Invoice.status)
│       └── expected.json       # {"verdict": "REVIEW"}
```

## Running the eval

```bash
cd engine/eval
python run_eval.py
```

Sample output:

```
Running 3 case(s) from engine/eval/cases

  [case_001_breaking_field_removed] ... PASS
  [case_002_safe_optional_param] ... PASS
  [case_003_review_enum_removal] ... PASS

Restored openapi.json from baseline.

Case                              Expected    Predicted     Result
---------------------------------------------------------------------
case_001_breaking_field_removed   BREAKING    BREAKING      PASS
case_002_safe_optional_param      SAFE        SAFE          PASS
case_003_review_enum_removal      REVIEW      REVIEW        PASS
---------------------------------------------------------------------

Accuracy: 3/3 (100.0%)
```

Exit code is `0` when all cases pass, `1` otherwise — safe to use in CI.

## How the harness works

1. Sorts case folders alphabetically under `cases/`.
2. For each case, copies `current_spec.json` over `mock-api/openapi.json`.
3. Runs `bob --auth-method api-key --mode contract-guardian -p "..."`.
4. Extracts the verdict from the output using three strategies (in order):
   - JSON between `---output---` markers
   - Any JSON object containing a `"verdict"` key
   - A bare verdict word on its own line
5. Compares the extracted verdict to `expected.json`.
6. Restores `mock-api/openapi.json` from the baseline in a `finally` block (runs even on crashes).

## If the harness is interrupted

```bash
python restore_spec.py
```

This copies `openapi_baseline.json` back to `openapi.json`. Run it any time the spec gets into an unknown state.

## Adding a new case

1. Create a new folder under `cases/` — use the naming convention `case_NNN_short_description`.
2. Add `current_spec.json` — a full OpenAPI spec with exactly the change you want to test.
   The baseline it is compared against is always `mock-api/openapi_baseline.json`.
3. Add `expected.json`:
   ```json
   {"verdict": "BREAKING"}
   ```
   Valid values: `BREAKING`, `SAFE`, `REVIEW`.

### Verdict guidelines

| Change type | Expected verdict |
|-------------|-----------------|
| Required response field removed | `BREAKING` |
| Required request field added | `BREAKING` |
| Field type changed | `BREAKING` |
| Endpoint removed | `BREAKING` |
| Optional query/header param added | `SAFE` |
| Optional response field added | `SAFE` |
| Description-only changes | `SAFE` |
| Enum value removed from response | `REVIEW` |
| Field made optional that was required | `REVIEW` |
| Status code added or removed | `REVIEW` |

### Tips for writing good cases

- Change **one thing** per case. Compound diffs make failures ambiguous.
- Use the full baseline spec as your starting point and apply the minimal diff.
- The baseline is `mock-api/openapi_baseline.json` — copy it as your starting point.
- Run `python restore_spec.py` after manually editing `openapi.json` to reset it.
