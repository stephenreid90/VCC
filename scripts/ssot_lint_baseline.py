"""Regenerate tests/ssot_lint_baseline.json (the SSOT lint ratchet).

Run deliberately, and only downward: the baseline records duplicates that
already exist. Adding to it needs a reason.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_ssot_lint import BASELINE, _find_duplicates  # noqa: E402

hits = sorted(_find_duplicates())
BASELINE.write_text(json.dumps(hits, indent=2) + "\n", encoding="utf-8")
print(f"recorded {len(hits)} known duplicates -> {BASELINE}")
