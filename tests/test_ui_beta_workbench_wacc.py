"""The CSL beta workbench runs in WACC mode (20 Oct 2026, Stephen's ruling; implements D-84).

Pins: the workbench's conversion from cost of equity to discount rate uses the engine's own
target structure (segment_wacc_from_data on csl.yaml), so at the workbench defaults the implied
WACC equals the engine rate; nothing is typed; WBC stays in cost-of-equity mode; DNL unchanged.
"""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "ui_prototypes" / "_generator"
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(ROOT / "src"))

GEN_UI = (GEN / "gen_ui.py").read_text(encoding="utf-8")
BUILD = (GEN / "build_cfgs.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def bc():
    with contextlib.redirect_stdout(io.StringIO()):
        import build_cfgs
    return build_cfgs


def test_csl_workbench_is_in_wacc_mode(bc):
    t = bc.csl["beta"]["toDiscount"]
    assert t["mode"] == "wacc" and t["label"] == "WACC"
    assert 0.0 < t["wE"] < 1.0 and t["kdAfterTax"] > 0.0


def test_implied_wacc_at_defaults_equals_the_engine_rate(bc):
    b = bc.csl["beta"]; t = b["toDiscount"]
    re = b["rf"] + b["subject"]["selectedBeta"] * b["erp"] + b["alpha"]
    implied = t["wE"] * re + (1.0 - t["wE"]) * t["kdAfterTax"]
    engine = bc.csl["cp"]["reEngine"] * 100.0
    assert abs(implied - engine) < 0.005, (implied, engine)
    assert "%.2f" % implied == "%.2f" % engine


def test_workbench_parts_come_from_the_engine_function_not_typed(bc):
    from vcc_valuations.translator import load_inputs, resolve_normalised_baseline, segment_wacc_from_data
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    coe = resolve_normalised_baseline(inp)["cost_of_equity_build"]
    parts = segment_wacc_from_data(inp, coe["risk_free_rate"] + coe["beta"] * coe["equity_risk_premium"])
    b = bc.csl["beta"]; t = b["toDiscount"]
    assert abs(t["wE"] - (1.0 - parts["dv"])) < 1e-6
    assert abs(t["kdAfterTax"] - parts["kd"] * (1.0 - parts["tax"]) * 100.0) < 1e-4
    assert b["subject"]["tax"] == parts["tax"]
    assert abs(b["subject"]["de"] - parts["dv"] / (1.0 - parts["dv"])) < 1e-4
    assert b["subject"]["selectedBeta"] == coe["beta"]
    assert abs(b["rf"] - coe["risk_free_rate"] * 100.0) < 1e-6
    assert "segment_wacc_from_data" in BUILD and "csl[\"beta\"][\"toDiscount\"]" in BUILD


def test_wbc_stays_cost_of_equity_and_dnl_unchanged(bc):
    assert bc.wbc["beta"]["toDiscount"] == {"mode": "coe", "label": "cost of equity"}
    assert bc.dnl["beta"]["toDiscount"]["mode"] == "wacc"


def test_page_explains_the_conversion():
    assert "after-tax cost of debt." in GEN_UI and "BW.waccNote" in GEN_UI
