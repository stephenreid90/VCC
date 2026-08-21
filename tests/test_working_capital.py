"""working_capital_intensity_from_data() — the load-bearing step of the working-capital
standard (design/methodology/working_capital_treatment.md §5 step 3).

Locks:
- CSL: six years of layer-1 history, clean_years = [FY2024, FY2025], averages to
  35.8%, rounds to 35% under the standing nearest-5%-protocol.
- DNL: single observation (FY2025), rounding_override applies the raw 13.76% instead
  of the rounded 15% (Stephen's direction, 21 Aug 2026 — see data/companies/dnl.yaml).
- WBC: bank-exempt BY RULE — returns None, not zero.
- Missing history / missing clean_years judgement both raise, so a fourth company
  can never silently inherit a zero (methodology §5 step 5 / §3).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.translator import load_inputs, working_capital_intensity_from_data

ROOT = Path(__file__).resolve().parents[1]


def test_csl_intensity_averages_clean_years_and_rounds_to_nearest_5pct():
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    d = working_capital_intensity_from_data(inp)
    assert d is not None
    assert d["L1"].value == pytest.approx(0.348, abs=1e-3)   # FY2024
    assert d["L2"].value == pytest.approx(0.368, abs=1e-3)   # FY2025
    assert d["AVG"].value == pytest.approx(0.358, abs=1e-3)
    assert d.result == pytest.approx(0.35, abs=1e-9)


def test_dnl_intensity_single_observation_uses_rounding_override():
    inp = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    d = working_capital_intensity_from_data(inp)
    assert d is not None
    assert d["L1"].value == pytest.approx(0.1376, abs=1e-4)
    assert d["AVG"].value == pytest.approx(0.1376, abs=1e-4)
    # override applies the raw figure, not the nearest-5% rounding (15%)
    assert d.result == pytest.approx(0.1376, abs=1e-4)


def test_wbc_is_exempt_by_rule_not_by_zero():
    inp = load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc")
    assert working_capital_intensity_from_data(inp) is None


def test_missing_history_raises_rather_than_defaulting():
    inp = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    inp["financials"] = dict(inp["financials"])
    inp["financials"].pop("working_capital_history", None)
    with pytest.raises(ValueError, match="working_capital_history"):
        working_capital_intensity_from_data(inp)


def test_missing_clean_years_judgement_raises():
    inp = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    inp["company_raw"] = dict(inp["company_raw"])
    nb = dict(inp["company_raw"]["normalised_baseline"])
    nb.pop("working_capital_intensity", None)
    inp["company_raw"]["normalised_baseline"] = nb
    with pytest.raises(ValueError, match="clean_years"):
        working_capital_intensity_from_data(inp)
