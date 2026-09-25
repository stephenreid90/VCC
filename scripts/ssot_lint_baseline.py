"""Regenerate tests/ssot_lint_baseline.json (the SSOT lint ratchet).

Run deliberately, and only downward: the baseline records duplicates that
already exist. Adding to it needs a reason.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_ssot_lint import (  # noqa: E402
    BASELINE,
    BASIS_BASELINE,
    INTRA_BASELINE,
    MACRO_DRIVER_BASELINE,
    _find_duplicates,
    _intra_file_duplicates,
    _macro_driver_gaps,
    _ratio_fields_without_basis,
)

hits = sorted(_find_duplicates())
BASELINE.write_text(json.dumps(hits, indent=2) + "\n", encoding="utf-8")
print(f"recorded {len(hits)} known duplicates -> {BASELINE}")

intra = sorted(_intra_file_duplicates())
INTRA_BASELINE.write_text(json.dumps(intra, indent=2) + "\n", encoding="utf-8")
print(f"recorded {len(intra)} known intra-file duplicates -> {INTRA_BASELINE}")

basis = _ratio_fields_without_basis()
BASIS_BASELINE.write_text(json.dumps(basis, indent=2) + "\n", encoding="utf-8")
print(f"recorded {len(basis)} rates without a declared basis -> {BASIS_BASELINE}")

macro_gaps = _macro_driver_gaps()
MACRO_DRIVER_BASELINE.write_text(json.dumps(macro_gaps, indent=2) + "\n", encoding="utf-8")
print(f"recorded {len(macro_gaps)} required macro drivers without a year-10 path -> {MACRO_DRIVER_BASELINE}")
