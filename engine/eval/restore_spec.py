"""
Restores mock-api/openapi.json from the frozen baseline snapshot.

Use this any time the eval harness is interrupted before it can self-restore,
or whenever you want to manually reset openapi.json to the baseline state.
"""

import shutil
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent
REPO_ROOT = EVAL_DIR.parent.parent
MOCK_API_DIR = REPO_ROOT / "mock-api"
CURRENT_SPEC = MOCK_API_DIR / "openapi.json"
BASELINE_SPEC = MOCK_API_DIR / "openapi_baseline.json"


def main() -> None:
    if not BASELINE_SPEC.exists():
        print(f"Baseline not found: {BASELINE_SPEC}", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(BASELINE_SPEC, CURRENT_SPEC)
    print(f"Restored: {CURRENT_SPEC.relative_to(REPO_ROOT)}")
    print(f"  from:   {BASELINE_SPEC.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
