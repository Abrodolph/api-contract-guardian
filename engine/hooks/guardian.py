#!/usr/bin/env python3
"""
Contract Guardian — classification engine for the pre-commit hook and CI.

Pre-commit (default): detects whether mock-api/openapi.json is staged,
  classifies the change via Bob Shell, blocks BREAKING commits.
CI mode (CI=true):   skips staged-file check; compares openapi.json
  directly against openapi_baseline.json.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MOCK_API_DIR = REPO_ROOT / "mock-api"
CURRENT_SPEC = MOCK_API_DIR / "openapi.json"
BASELINE_SPEC = MOCK_API_DIR / "openapi_baseline.json"
MOCK_CONSUMERS_DIR = REPO_ROOT / "mock-consumers"

BOB_PATH = (
    shutil.which("bob")
    or shutil.which("bob.cmd")
    or r"C:/Users/saini/AppData/Roaming/npm/bob.cmd"
)
TIMEOUT = 120

# ── .env loader ───────────────────────────────────────────────────────────────

def _load_env() -> None:
    env_file = REPO_ROOT / ".env"
    if env_file.exists() and not os.environ.get("BOBSHELL_API_KEY"):
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("BOBSHELL_API_KEY=") and not line.startswith("#"):
                os.environ["BOBSHELL_API_KEY"] = (
                    line.split("=", 1)[1].strip().strip('"').strip("'")
                )
                break

# ── Staged-file detection ──────────────────────────────────────────────────────

def _is_ci() -> bool:
    return os.environ.get("CI", "").lower() in ("true", "1")


def _openapi_is_staged() -> bool:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    return "mock-api/openapi.json" in result.stdout.splitlines()

# ── Call-site scanner (mirrors MCP find_call_sites without the MCP layer) ─────

def _find_call_sites(field_name: str) -> list[dict]:
    pattern = re.compile(
        rf'(data|item|raw|response|u|inv|payload)\[(["\']){re.escape(field_name)}\2\]'
    )
    sites: list[dict] = []
    if not MOCK_CONSUMERS_DIR.exists():
        return sites
    for py_file in MOCK_CONSUMERS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(MOCK_CONSUMERS_DIR)
        consumer = rel.parts[0] if len(rel.parts) > 1 else "unknown"
        try:
            for lineno, line in enumerate(
                py_file.read_text(encoding="utf-8").splitlines(), 1
            ):
                if pattern.search(line):
                    sites.append(
                        {
                            "consumer": consumer,
                            "file": str(py_file.relative_to(REPO_ROOT)).replace(
                                "\\", "/"
                            ),
                            "line": lineno,
                        }
                    )
        except Exception:
            continue
    return sites


def _build_call_sites_block() -> str:
    fields = [
        "email", "name", "full_name", "created_at", "amount", "amount_cents",
        "currency", "user_id", "status", "plan", "id",
    ]
    lines: list[str] = []
    for field in fields:
        sites = _find_call_sites(field)
        if sites:
            consumers = list(dict.fromkeys(s["consumer"] for s in sites))
            locs = ", ".join(f"{s['file']}:{s['line']}" for s in sites)
            lines.append(f"  {field}: consumers={consumers}, locations=[{locs}]")
    return "\n".join(lines) if lines else "  (none found)"

# ── Verdict extraction ─────────────────────────────────────────────────────────

_VALID = {"BREAKING", "SAFE", "REVIEW"}


def _extract_verdict(raw: str) -> dict | None:
    for i, ch in enumerate(raw):
        if ch != "{":
            continue
        depth = 0
        for j in range(i, len(raw)):
            if raw[j] == "{":
                depth += 1
            elif raw[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        data = json.loads(raw[i : j + 1])
                        v = data.get("verdict", "").upper()
                        if v in _VALID:
                            data["verdict"] = v
                            return data
                    except json.JSONDecodeError:
                        pass
                    break
    return None

# ── Bob Shell invocation ───────────────────────────────────────────────────────

def _classify(baseline: str, current: str, call_sites_block: str) -> dict | None:
    prompt = (
        "You are an API contract governance specialist. "
        "Compare the BASELINE and CURRENT OpenAPI specs below and classify the change.\n\n"
        f"BASELINE SPEC:\n{baseline}\n\n"
        f"CURRENT SPEC:\n{current}\n\n"
        f"PRE-COMPUTED CALL SITES (use to populate blast_radius for BREAKING verdicts):\n"
        f"{call_sites_block}\n\n"
        "Classification rules:\n"
        "  BREAKING: response field removed/renamed, required request field added, "
        "field type changed, endpoint path changed, HTTP method changed, "
        "optional field made required\n"
        "  SAFE: new optional field/endpoint/response field added, doc-only change\n"
        "  REVIEW: enum value removed, nullability change, default value change, "
        "type widened (e.g. integer->number)\n\n"
        "Use the most severe rule (BREAKING > REVIEW > SAFE) when multiple changes exist.\n\n"
        "For BREAKING: group the PRE-COMPUTED CALL SITES by consumer name to build blast_radius.\n\n"
        "Output ONLY the following JSON with no other text, no markdown fences:\n"
        '{"verdict":"BREAKING or SAFE or REVIEW","change_summary":"one sentence",'
        '"affected_field":"field name or null",'
        '"blast_radius":{"consumers":[{"name":"consumer-name","call_sites":[{"file":"path","line":0}]}],'
        '"total_call_sites":0},"reasoning":"brief explanation"}'
    )
    try:
        result = subprocess.run(
            [
                BOB_PATH,
                "--auth-method", "api-key",
                "--yolo",
                "--hide-intermediary-output",
                "-p", prompt,
            ],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        return _extract_verdict(result.stdout + "\n" + result.stderr)
    except subprocess.TimeoutExpired:
        print("[guardian] Bob Shell timed out.", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"[guardian] Bob Shell not found at: {BOB_PATH}", file=sys.stderr)
        return None

# ── Backend POST ───────────────────────────────────────────────────────────────

def _post_verdict(verdict: dict) -> None:
    url = os.environ.get("GUARDIAN_BACKEND_URL", "").rstrip("/")
    if not url:
        return
    try:
        import urllib.request

        req = urllib.request.Request(
            f"{url}/verdict",
            data=json.dumps(verdict).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[guardian] Backend POST failed: {e}", file=sys.stderr)

# ── Output ─────────────────────────────────────────────────────────────────────

_R = "\033[31m"
_G = "\033[32m"
_A = "\033[33m"
_B = "\033[1m"
_X = "\033[0m"


def _print_verdict(verdict: dict) -> None:
    v = verdict["verdict"]
    summary = verdict.get("change_summary", "")
    blast = verdict.get("blast_radius", {})
    total = blast.get("total_call_sites", 0)
    consumers = blast.get("consumers", [])

    if v == "BREAKING":
        print(f"\n{_R}{_B}CONTRACT GUARDIAN: BREAKING CHANGE DETECTED{_X}")
        print(f"{_R}  Change : {summary}{_X}")
        if total:
            print(f"{_R}  Impact : {total} call site(s) across {len(consumers)} consumer(s){_X}")
            for c in consumers:
                n = len(c.get("call_sites", []))
                print(f"{_R}    - {c['name']}: {n} call site(s){_X}")
        print(f"{_R}  Commit BLOCKED. Resolve the breaking change before pushing.{_X}\n")
    elif v == "REVIEW":
        print(f"\n{_A}{_B}CONTRACT GUARDIAN: REVIEW REQUIRED{_X}")
        print(f"{_A}  Change : {summary}{_X}")
        print(f"{_A}  Commit allowed — please flag for API governance review.{_X}\n")
    else:
        print(f"\n{_G}{_B}CONTRACT GUARDIAN: SAFE CHANGE{_X}")
        print(f"{_G}  Change : {summary}{_X}")
        print(f"{_G}  Commit allowed.{_X}\n")

# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    _load_env()

    # Skip if not a CI run and openapi.json is not staged
    if not _is_ci() and not _openapi_is_staged():
        return 0

    if not os.environ.get("BOBSHELL_API_KEY"):
        print("[guardian] BOBSHELL_API_KEY not set — skipping.", file=sys.stderr)
        return 0

    for path, label in [(BASELINE_SPEC, "baseline"), (CURRENT_SPEC, "current")]:
        if not path.exists():
            print(f"[guardian] {label} spec not found: {path}", file=sys.stderr)
            return 0 if label == "baseline" else 1

    print("[guardian] Classifying API change via Bob Shell...", flush=True)

    baseline = BASELINE_SPEC.read_text(encoding="utf-8")
    current = CURRENT_SPEC.read_text(encoding="utf-8")
    call_sites = _build_call_sites_block()

    verdict = _classify(baseline, current, call_sites)

    if verdict is None:
        print("[guardian] Classification failed — skipping block.", file=sys.stderr)
        return 0

    _post_verdict(verdict)
    _print_verdict(verdict)

    return 1 if verdict["verdict"] == "BREAKING" else 0


if __name__ == "__main__":
    sys.exit(main())
