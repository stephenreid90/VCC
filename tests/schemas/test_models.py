"""
Smoke tests for the schema models — instantiation, JSON export, basic
constraints.

These tests don't validate against real content; they exercise the model
shapes themselves. The scenario YAMLs are tested in test_scenarios.py.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.schemas import (  # noqa: E402
    AssumptionSet,
    CompanyPositionFile,
    Driver,
    DriverFile,
    DriverMovementSet,
    ImpactMatrix,
    IndustryArchetypeFile,
    ScenarioFile,
)
from vcc_valuations.schemas.common import (  # noqa: E402
    DriverRole,
    DriverScope,
    ValuationModel,
)
from vcc_valuations.schemas.driver import DriverRange  # noqa: E402
from vcc_valuations.schemas.linkage import CompanyOverride, Governance  # noqa: E402


# ---- JSON Schema export sanity ----


@pytest.mark.parametrize(
    "model_cls",
    [
        ScenarioFile,
        IndustryArchetypeFile,
        CompanyPositionFile,
        DriverFile,
        ImpactMatrix,
        CompanyOverride,
        DriverMovementSet,
        AssumptionSet,
    ],
    ids=lambda m: m.__name__,
)
def test_model_json_schema_exports(model_cls) -> None:
    """Each top-level model produces a valid JSON Schema."""
    schema = model_cls.model_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema or "$ref" in schema or "$defs" in schema


# ---- Driver validation rules (section 9.2) ----


def _make_primary_driver(**overrides) -> Driver:
    defaults = dict(
        id="revenue_growth",
        group="revenue",
        name="Revenue growth",
        description="YoY revenue growth.",
        unit="decimal",
        default_range=DriverRange(min=-0.10, mid=0.03, max=0.15),
        applicable_archetypes="all",
        valuation_model=[ValuationModel.FCF],
        dcf_line_item="revenue",
        role=DriverRole.PRIMARY,
        dependencies=[],
        derivation_formula=None,
        scope=DriverScope.SEGMENT,
        scenario_sensitive=True,
        base_definition="latest_reported_fy",
        default_time_profile="regime_shift(phase_in_years=3)",
        aggregation_method="revenue_weighted_avg",
    )
    defaults.update(overrides)
    return Driver(**defaults)


def test_primary_driver_constructs_cleanly() -> None:
    d = _make_primary_driver()
    assert d.role == DriverRole.PRIMARY
    assert d.scenario_sensitive is True


def test_derived_driver_requires_formula_and_dependencies() -> None:
    """Derived drivers must have a derivation_formula and at least one dependency."""
    with pytest.raises(ValidationError):
        _make_primary_driver(role=DriverRole.DERIVED, scenario_sensitive=False)


def test_derived_driver_cannot_be_scenario_sensitive() -> None:
    """Derived drivers are computed by Layer 6, not written by Layer 5."""
    with pytest.raises(ValidationError):
        _make_primary_driver(
            role=DriverRole.DERIVED,
            scenario_sensitive=True,
            derivation_formula="x = y * z",
            dependencies=["y", "z"],
        )


def test_derived_driver_well_formed() -> None:
    """A correctly-specified derived driver constructs cleanly."""
    d = _make_primary_driver(
        id="wacc",
        group="financial_risk",
        role=DriverRole.DERIVED,
        scenario_sensitive=False,
        derivation_formula="wacc = (E/V) * cost_of_equity + (D/V) * cost_of_debt * (1 - tax)",
        dependencies=["cost_of_equity", "cost_of_debt", "target_leverage", "tax_rate"],
    )
    assert d.role == DriverRole.DERIVED
    assert d.scenario_sensitive is False


# ---- CompanyOverride validation rules (section 10.4) ----


def _make_override(**overrides) -> CompanyOverride:
    defaults = dict(
        company="ipl",
        scenario="muddle_through",
        driver="revenue_growth",
        reason_category="contract",
        reason="Long-term gas supply contracts insulate cost base.",
        governance=Governance(created_by="analyst@reidadvisory.net", created_at=datetime.now()),
    )
    defaults.update(overrides)
    return CompanyOverride(**defaults)


def test_beyond_scale_requires_quantified_override() -> None:
    """Section 10.4: beyond_scale True requires a quantified_override band."""
    with pytest.raises(ValidationError):
        _make_override(beyond_scale=True)


def test_sign_flip_requires_two_evidence_refs() -> None:
    """Section 10.6 rule: sign_flip True requires at least two evidence refs."""
    with pytest.raises(ValidationError):
        _make_override(sign_flip=True)


def test_override_well_formed() -> None:
    """A correctly-specified override constructs cleanly."""
    o = _make_override(
        reason_category="cost_advantage",
        reason="Scale-based cost advantage realised in mining-customer book.",
    )
    assert o.reason_category == "cost_advantage"
