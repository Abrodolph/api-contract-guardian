"""
Accuracy evaluation harness for the Contract Guardian.

For each case in engine/eval/cases/:
  1. Copies current_spec.json -> mock-api/openapi.json
  2. Runs bob in contract-guardian mode
  3. Extracts the verdict from ---output--- markers in stdout
  4. Compares against expected.json
  5. Prints a results table and overall accuracy

Restores the original openapi.json from baseline when done.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BOB_PATH = r"C:/Users/saini/AppData/Roaming/npm/bob.cmd"

# Load BOBSHELL_API_KEY from a .env file at repo root if not already in environment
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists() and not os.environ.get("BOBSHELL_API_KEY"):
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line.startswith("BOBSHELL_API_KEY=") and not _line.startswith("#"):
            os.environ["BOBSHELL_API_KEY"] = _line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not os.environ.get("BOBSHELL_API_KEY"):
    print("ERROR: BOBSHELL_API_KEY not set. Add it to a .env file at repo root:", file=sys.stderr)
    print("  echo BOBSHELL_API_KEY=your-key > .env", file=sys.stderr)
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────────

EVAL_DIR = Path(__file__).parent
CASES_DIR = EVAL_DIR / "cases"
REPO_ROOT = EVAL_DIR.parent.parent
MOCK_API_DIR = REPO_ROOT / "mock-api"
CURRENT_SPEC = MOCK_API_DIR / "openapi.json"
BASELINE_SPEC = MOCK_API_DIR / "openapi_baseline.json"
TMP_OUTPUT = EVAL_DIR / "tmp_output.txt"


# Short trigger prompt — the contract-guardian mode already has the full rules
# and output schema baked into its customInstructions.
# If --chat-mode doesn't load custom modes headlessly, swap to BOB_PROMPT_FULL below.
BOB_PROMPT = (
    "Call get_openapi_spec with version='baseline', then version='current'. "
    "Compare the two specs. For BREAKING changes also call find_call_sites for the "
    "affected field. Output ONLY the verdict JSON, nothing else."
)

# Fallback: full instructions embedded in the prompt (use if --chat-mode doesn't work)
BOB_PROMPT_FULL = (
    "You are an API contract governance specialist. "
    "Call get_openapi_spec with version=baseline then version=current. "
    "Classify the change: "
    "BREAKING=response field removed/renamed, required request field added, type changed, path/method changed; "
    "SAFE=optional field added, new endpoint/response field added, doc-only change; "
    "REVIEW=enum value removed, nullability change, default value change, type widened. "
    "For BREAKING, call find_call_sites(field_name) and populate blast_radius. "
    'Output ONLY a JSON object with keys verdict, change_summary, affected_field, blast_radius, reasoning. No other text.'
)

# Primary: --chat-mode loads the custom mode with its baked-in rules
# If Bob Shell doesn't support custom modes via --chat-mode, switch to:
#   BOB_CMD = [..., "-p", BOB_PROMPT_FULL]  (drop --chat-mode line)
BOB_CMD = [
    BOB_PATH,
    "--chat-mode=contract-guardian",
    "--auth-method", "api-key",
    "--yolo",
    "--hide-intermediary-output",
    "-p", BOB_PROMPT,
]
# ── Verdict extraction ────────────────────────────────────────────────────────

OUTPUT_MARKER = re.compile(r"---output---\s*(.*?)\s*---output---", re.DOTALL)
VALID_VERDICTS = {"BREAKING", "SAFE", "REVIEW"}


def _try_parse_verdict(text: str) -> str | None:
    try:
        data = json.loads(text)
        v = data.get("verdict", "").upper()
        return v if v in VALID_VERDICTS else None
    except (json.JSONDecodeError, AttributeError):
        return None


def extract_verdict(raw: str) -> str | None:
    """
    Try three extraction strategies in order:
      1. JSON between ---output--- markers
      2. Every '{' in output as a potential JSON start (handles nested objects)
      3. Bare verdict word on its own line
    """
    # Strategy 1: delimited block
    m = OUTPUT_MARKER.search(raw)
    if m:
        v = _try_parse_verdict(m.group(1))
        if v:
            return v

    # Strategy 2: find each '{' and try to parse outward until valid JSON
    for i, ch in enumerate(raw):
        if ch != "{":
            continue
        # Walk forward expanding the candidate until balanced braces
        depth = 0
        for j in range(i, len(raw)):
            if raw[j] == "{":
                depth += 1
            elif raw[j] == "}":
                depth -= 1
                if depth == 0:
                    v = _try_parse_verdict(raw[i : j + 1])
                    if v:
                        return v
                    break

    # Strategy 3: bare word
    for line in raw.splitlines():
        word = line.strip().upper()
        if word in VALID_VERDICTS:
            return word

    return None


# ── Case runner ───────────────────────────────────────────────────────────────

def run_case(case_dir: Path) -> dict:
    case_name = case_dir.name
    spec_file = case_dir / "current_spec.json"
    expected_file = case_dir / "expected.json"

    if not spec_file.exists():
        return {"case": case_name, "expected": "N/A", "predicted": "MISSING_SPEC", "pass": False}
    if not expected_file.exists():
        return {"case": case_name, "expected": "MISSING", "predicted": "N/A", "pass": False}

    expected = json.loads(expected_file.read_text()).get("verdict", "").upper()

    # Install the candidate spec
    shutil.copy2(spec_file, CURRENT_SPEC)

    try:
        result = subprocess.run(
            BOB_CMD,
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw = result.stdout + "\n" + result.stderr
        TMP_OUTPUT.write_text(raw, encoding="utf-8")
        predicted = extract_verdict(raw) or "PARSE_ERROR"

    except subprocess.TimeoutExpired:
        predicted = "TIMEOUT"
    except FileNotFoundError:
        predicted = "BOB_NOT_FOUND"

    passed = predicted == expected
    return {"case": case_name, "expected": expected, "predicted": predicted, "pass": passed}


# ── Formatting ────────────────────────────────────────────────────────────────

def print_table(rows: list[dict]) -> None:
    col_case = max(len(r["case"]) for r in rows)
    col_case = max(col_case, len("Case"))
    header = f"{'Case':<{col_case}}  {'Expected':<10}  {'Predicted':<12}  Result"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for r in rows:
        result_str = "PASS" if r["pass"] else f"FAIL  (got {r['predicted']})"
        print(f"{r['case']:<{col_case}}  {r['expected']:<10}  {r['predicted']:<12}  {result_str}")
    print(sep)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not CASES_DIR.exists():
        print(f"Cases directory not found: {CASES_DIR}", file=sys.stderr)
        sys.exit(1)

    case_dirs = sorted(
        d for d in CASES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )
    if not case_dirs:
        print("No cases found.", file=sys.stderr)
        sys.exit(1)

    print(f"Running {len(case_dirs)} case(s) from {CASES_DIR.relative_to(REPO_ROOT)}\n")

    rows: list[dict] = []
    try:
        for case_dir in case_dirs:
            print(f"  [{case_dir.name}] ...", end=" ", flush=True)
            row = run_case(case_dir)
            rows.append(row)
            print("PASS" if row["pass"] else f"FAIL (predicted={row['predicted']})")
    finally:
        # Always restore baseline regardless of errors
        if BASELINE_SPEC.exists():
            shutil.copy2(BASELINE_SPEC, CURRENT_SPEC)
            print("\nRestored openapi.json from baseline.")
        if TMP_OUTPUT.exists():
            TMP_OUTPUT.unlink()

    print()
    print_table(rows)
    print()

    passed = sum(r["pass"] for r in rows)
    total = len(rows)
    pct = 100.0 * passed / total if total else 0.0
    print(f"Accuracy: {passed}/{total} ({pct:.1f}%)")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
