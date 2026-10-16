"""R16-4 (16 Oct 2026): WBC NIM pass-through from the RBA cash rate, measured not typed.

Pins design/methodology/bank_nim_pass_through_set.yaml, written by
scripts/size_bank_nim_pass_through.py from data/companies/wbc.yaml (half-year NIMs) and
data/macro/rba_cash_rate.yaml. A changed input makes this fail and the set stale.
"""

from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

SET = yaml.safe_load((ROOT / "design" / "methodology" / "bank_nim_pass_through_set.yaml").read_text(encoding="utf-8"))["bank_nim_pass_through_set"]


def test_sample_is_one_cycle_of_ten_halves():
    assert SET["sample_halves"] == 10
    assert SET["observations"][0]["half"] == "1H21 (Mar 2021)"
    assert SET["observations"][-1]["half"] == "1H26 (Mar 2026)"


def test_pass_through_is_small_and_not_distinct_from_zero():
    lvl = SET["level_regression"]
    assert lvl["pass_through_bp_per_100bp"] == pytest.approx(-1.53, abs=0.01)
    assert lvl["std_error"] == pytest.approx(0.93, abs=0.01)
    ex = SET["level_regression_excluding_1h21"]
    assert ex["pass_through_bp_per_100bp"] == pytest.approx(-0.30, abs=0.01)
    assert abs(ex["pass_through_bp_per_100bp"]) < 2 * ex["std_error"]
    assert SET["change_regression"]["pass_through_bp_per_100bp"] == pytest.approx(1.59, abs=0.01)
    assert SET["cycle_check"]["implied_bp_per_100bp"] == pytest.approx(-2.12, abs=0.01)


def test_set_reproduces_from_the_script():
    import size_bank_nim_pass_through as s
    changes = s.cash_rate_changes()
    rows = s.wbc_half_year_nims()
    assert len(rows) == SET["sample_halves"]
    xs = [s.avg_cash_rate(*s.half_bounds(l), changes) for l, _ in rows]
    ys = [n * s.BPS for _, n in rows]
    slope, _, se, _ = s.ols(xs, ys)
    assert slope == pytest.approx(SET["level_regression"]["pass_through_bp_per_100bp"], abs=0.01)
    assert se == pytest.approx(SET["level_regression"]["std_error"], abs=0.01)
