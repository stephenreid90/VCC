"""D-06 (16 Oct 2026): CSL is discounted at a WACC on a target capital structure.

The arithmetic is checked by hand here, against the translator's own function.
"""

from pathlib import Path

import pytest

from vcc_valuations.translator import load_inputs, segment_wacc_from_data

ROOT = Path(__file__).resolve().parents[2]


def test_wacc_on_the_confirmed_target_structure():
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    ke = 0.045 + 0.85 * 0.05                      # Rf + beta x ERP = 8.75%
    p = segment_wacc_from_data(inp, ke)
    assert p["kd"] == pytest.approx(0.055)        # confirmed Q9
    assert p["tax"] == pytest.approx(0.30)
    assert p["net_debt_ebitda"] == pytest.approx(1.8)
    assert p["target_ev_ebitda"] == pytest.approx(14.0)
    assert p["dv"] == pytest.approx(1.8 / 14.0)   # 12.9%
    expected = ke * (1 - 1.8 / 14.0) + 0.055 * (1 - 0.30) * (1.8 / 14.0)
    assert p["wacc"] == pytest.approx(expected, abs=1e-12)
    assert p["wacc"] == pytest.approx(0.0812, abs=1e-9)
    assert p["wacc"] < ke                          # the debt is cheaper after tax
