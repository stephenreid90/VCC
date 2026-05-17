"""
Layer 4 — Driver taxonomy (architecture spec section 9.2).

Drivers carry stable ids — the impact matrix (Layer 5) addresses scenarios
into industry / company assumptions through these ids, so renaming a driver
is a breaking change.
"""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vcc_valuations.schemas.common import (
    DriverRole,
    DriverScope,
    TimeProfileShape,
    ValuationModel,
)


class DriverRange(BaseModel):
    """Default min / mid / max for a driver under a given archetype (section 9.2)."""

    model_config = ConfigDict(extra="forbid")

    min: float
    mid: float
    max: float


class Driver(BaseModel):
    """A driver in the Layer 4 catalogue."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Stable snake_case id used by the impact matrix.")
    group: str = Field(
        ...,
        description=(
            "revenue | margin | capital | financial_risk | terminal | archetype_specific."
        ),
    )
    name: str
    description: str
    unit: str = Field(..., description="decimal | bps | days | currency | ratio | multiplier.")
    default_range: DriverRange = Field(
        ..., description="Set at archetype level; overridable per company."
    )
    applicable_archetypes: Union[List[str], str] = Field(
        ..., description="List of archetype ids, or 'all'."
    )
    valuation_model: List[ValuationModel]
    dcf_line_item: str
    role: DriverRole
    dependencies: List[str] = Field(
        default_factory=list,
        description="Other driver ids; required where role == derived.",
    )
    derivation_formula: Optional[str] = Field(
        None,
        description=(
            "Required where role == derived. Plain-language or expression form, e.g. "
            "'wacc = (E/V) * cost_of_equity + (D/V) * cost_of_debt_pretax * (1 - tax_rate)'."
        ),
    )
    scope: DriverScope
    scenario_sensitive: bool = Field(
        ...,
        description=(
            "Whether the impact matrix may move it. Must be False where role == derived "
            "(derived drivers are computed by Layer 6, not written by Layer 5)."
        ),
    )
    base_definition: str = Field(
        ...,
        description=(
            "latest_reported_fy | ttm | three_year_avg | ntm_consensus — used by Layer 6 "
            "(section 11.2) to anchor deltas against base-year values."
        ),
    )
    default_time_profile: str = Field(
        ...,
        description=(
            "Default time-profile name from the section 11.3 library, with parameters "
            "bundled (e.g. 'regime_shift(phase_in_years=3)')."
        ),
    )
    aggregation_method: str = Field(
        ...,
        description=(
            "revenue_weighted_avg | ebit_weighted_avg | sum | identity_if_company_scope — "
            "used by Layer 6 (section 11.2) to roll segment values to company level."
        ),
    )

    @model_validator(mode="after")
    def _enforce_derived_constraints(self) -> "Driver":
        """Derived drivers must not be scenario-sensitive and must have a formula."""
        if self.role == DriverRole.DERIVED:
            if self.scenario_sensitive:
                raise ValueError(
                    f"Driver {self.id!r} has role 'derived' so scenario_sensitive must be False."
                )
            if not self.derivation_formula:
                raise ValueError(
                    f"Driver {self.id!r} has role 'derived' so derivation_formula is required."
                )
            if not self.dependencies:
                raise ValueError(
                    f"Driver {self.id!r} has role 'derived' so dependencies must list "
                    "the primary drivers it is computed from."
                )
        return self


class DriverFile(BaseModel):
    """Top-level wrapper for data/drivers/<id>.yaml or a catalogue file."""

    model_config = ConfigDict(extra="forbid")

    drivers: List[Driver]
