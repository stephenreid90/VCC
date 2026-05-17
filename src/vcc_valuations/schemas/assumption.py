"""
Layer 6 — Assumption translation output (architecture spec section 11.5).

The AssumptionSet is what the DCF / DDM / residual-income engine consumes.
It is driver-keyed (one entry per driver id from Layer 4), range-by-default
({min, mid, max} per cell), and archetype-tagged where the consolidated block
shape varies by valuation model (FCF vs DDM).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from vcc_valuations.schemas.common import Confidence, Direction, Magnitude, ValuationModel
from vcc_valuations.schemas.linkage import QuantifiedBand


class AssumptionCell(BaseModel):
    """One driver's assumption — a year-indexed range (min / mid / max) per section 11.5."""

    model_config = ConfigDict(extra="forbid")

    min: List[float]
    mid: List[float]
    max: List[float]
    confidence: Confidence
    time_profile: str = Field(..., description="Profile name + parameters per section 11.3.")
    base_value: float
    aggregation_method: str


class SegmentAssumptions(BaseModel):
    """Driver-keyed map of per-segment assumptions (section 11.5)."""

    model_config = ConfigDict(extra="forbid")

    segment: str
    industry_archetype: str
    weight: float = Field(..., ge=0.0, le=1.0)
    assumptions: Dict[str, AssumptionCell] = Field(
        ..., description="Driver id -> assumption cell."
    )


class ConsolidatedAssumptionsFCF(BaseModel):
    """FCF-model consolidated block (e.g. IPL, CSL)."""

    model_config = ConfigDict(extra="forbid")

    assumptions: Dict[str, AssumptionCell]


class ConsolidatedAssumptionsDDM(BaseModel):
    """DDM / residual-income consolidated block (e.g. WBC)."""

    model_config = ConfigDict(extra="forbid")

    assumptions: Dict[str, AssumptionCell]


class ConsolidatedAssumptions(BaseModel):
    """Archetype-tagged consolidated block (section 11.5)."""

    model_config = ConfigDict(extra="forbid")

    valuation_model: ValuationModel
    consolidated_assumptions_fcf: Optional[ConsolidatedAssumptionsFCF] = None
    consolidated_assumptions_ddm: Optional[ConsolidatedAssumptionsDDM] = None


class BaseYearSnapshot(BaseModel):
    """Anchor values from Ben's data workstream (section 11.5)."""

    model_config = ConfigDict(extra="allow")  # archetype-relevant lines vary

    fiscal_year: str
    revenue: float
    ebit: Optional[float] = None
    ebit_margin: Optional[float] = None
    capex: Optional[float] = None
    net_debt: Optional[float] = None


class ReasoningTraceEntry(BaseModel):
    """One entry in the end-to-end audit trace (section 11.5)."""

    model_config = ConfigDict(extra="forbid")

    segment: str = Field(..., description="Segment id or the literal 'company_level'.")
    driver: str
    scenario_narrative_excerpt: str
    industry_direction: Direction
    industry_magnitude: Magnitude
    industry_confidence: Confidence
    company_override: Optional[Dict[str, Any]] = None
    final_direction: Direction
    final_magnitude: Magnitude
    final_quantified_band: Optional[QuantifiedBand] = None
    translation_rule_applied: str
    base_definition: str
    base_value: float
    time_profile_used: str
    consistency_rules_applied: List[str] = []
    final_numerical_value: AssumptionCell
    narrative: str


class AssumptionSet(BaseModel):
    """Top-level AssumptionSet per company x scenario (section 11.5)."""

    model_config = ConfigDict(extra="forbid")

    company: str
    scenario: str
    scenario_version: str
    horizon_years: int = Field(
        ...,
        description=(
            "Parametric per section 2 — set per company x scenario combination, "
            "not a fixed 5 or 10."
        ),
    )
    functional_currency: str
    translation_rules_version: str
    generated_at: datetime
    generated_by: str
    base_year_snapshot: BaseYearSnapshot
    segment_assumptions: List[SegmentAssumptions]
    consolidated_assumptions: ConsolidatedAssumptions
    reasoning_trace: List[ReasoningTraceEntry]
