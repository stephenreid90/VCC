"""
Layer 5 — Linkage / impact matrix (architecture spec sections 10.3, 10.4, 10.5).

The impact matrix is the conceptual core of the framework: for every
(scenario x industry archetype x driver) it encodes how the driver moves
under that scenario. Company-level overrides modulate industry impacts.
The output is a DriverMovementSet per company x scenario.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vcc_valuations.schemas.common import Confidence, Direction, Magnitude
from vcc_valuations.schemas.company import EvidenceRef


# ---- Shared building blocks ----


class QuantifiedBand(BaseModel):
    """Optional quantified override of the ordinal direction x magnitude (section 10.2)."""

    model_config = ConfigDict(extra="forbid")

    min: float
    mid: float
    max: float


class Governance(BaseModel):
    """Per-entry / per-override governance audit (sections 10.3 and 10.4)."""

    model_config = ConfigDict(extra="forbid")

    created_by: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    last_reviewed_at: Optional[datetime] = None


# ---- Impact matrix entries (section 10.3) ----


class DriverMovement(BaseModel):
    """One cell of the impact matrix — scenario x archetype x driver."""

    model_config = ConfigDict(extra="forbid")

    direction: Direction
    magnitude: Magnitude
    confidence: Confidence
    rationale: str
    quantified_override: Optional[QuantifiedBand] = None
    not_applicable: bool = Field(
        False,
        description=(
            "True where the driver does not apply to this archetype "
            "(distinct from direction == neutral, which means 'applies but scenario "
            "doesn't move it')."
        ),
    )
    evidence_refs: List[EvidenceRef] = []
    governance: Optional[Governance] = None


class ImpactMatrixEntry(BaseModel):
    """All driver movements for one scenario under one archetype (section 10.3)."""

    model_config = ConfigDict(extra="forbid")

    scenario: str
    scenario_version: str
    drivers: Dict[str, DriverMovement] = Field(
        ...,
        description=(
            "Map from driver id (Layer 4) to its movement. "
            "Absent drivers imply direction == neutral and were not explicitly assessed "
            "(per the section 10.2 sparse-representation convention)."
        ),
    )


class ImpactMatrix(BaseModel):
    """The impact matrix for one industry archetype (section 10.3 outer wrapper)."""

    model_config = ConfigDict(extra="forbid")

    industry: str
    matrix: List[ImpactMatrixEntry] = Field(..., min_length=1)


# ---- Company overrides (section 10.4) ----


class HalfLifeTracker(BaseModel):
    """Scenario-version-tied refresh tracking (section 10.4)."""

    model_config = ConfigDict(extra="forbid")

    scenario_version_at_creation: str
    review_required_at_scenario_version: Optional[str] = None
    stale: bool = False
    requires_re_review: bool = False


class ReviewDialogue(BaseModel):
    """Optional peer-review trail capturing the challenge / response (section 10.4)."""

    model_config = ConfigDict(extra="forbid")

    challenge: str
    challenger: str
    response: str
    challenge_at: datetime


class CompanyOverride(BaseModel):
    """An override to an impact matrix entry (section 10.4)."""

    model_config = ConfigDict(extra="forbid")

    company: str
    segment: Optional[str] = Field(
        None,
        description="If None, the override applies to the whole company.",
    )
    scenario: str
    driver: str
    override_direction: Optional[Direction] = None
    override_magnitude: Optional[Magnitude] = None
    quantified_override: Optional[QuantifiedBand] = None
    sign_flip: bool = Field(
        False,
        description="True when override_direction opposes industry_direction.",
    )
    beyond_scale: bool = Field(
        False,
        description=(
            "True when ordinal cannot represent the movement; quantified_override "
            "required when this is True (section 10.4)."
        ),
    )
    reason_category: str = Field(
        ...,
        description=(
            "cost_advantage | scale | regulation | contract | management | "
            "product_mix | diversification | franchise_asset | data_workstream | other"
        ),
    )
    reason: str
    evidence_refs: List[EvidenceRef] = []
    governance: Governance
    review_dialogue: List[ReviewDialogue] = []
    half_life: Optional[HalfLifeTracker] = None

    @model_validator(mode="after")
    def _enforce_override_constraints(self) -> "CompanyOverride":
        if self.beyond_scale and self.quantified_override is None:
            raise ValueError(
                "When beyond_scale is True, a quantified_override band is required "
                "(section 10.4 beyond-scale semantics)."
            )
        if self.sign_flip and len(self.evidence_refs) < 2:
            raise ValueError(
                "When sign_flip is True, at least two evidence_refs are required "
                "(section 10.6 rule)."
            )
        return self


# ---- DriverMovementSet output (section 10.5) ----


class MovementOutput(BaseModel):
    """Per-driver movement output, including industry default and any override resolution."""

    model_config = ConfigDict(extra="forbid")

    driver: str
    industry_direction: Direction
    industry_magnitude: Magnitude
    industry_confidence: Confidence
    industry_rationale: str
    company_override: Optional[CompanyOverride] = None
    final_direction: Direction
    final_magnitude: Magnitude
    final_confidence: Confidence
    final_quantified_band: Optional[QuantifiedBand] = None


class SegmentMovementOutput(BaseModel):
    """Per-segment movement output."""

    model_config = ConfigDict(extra="forbid")

    segment: str
    industry_archetype: str
    weight: float = Field(..., ge=0.0, le=1.0)
    movements: List[MovementOutput]


class CompanyLevelMovementOutput(BaseModel):
    """Company-scope movements (tax, WACC components, terminal-state, minorities)."""

    model_config = ConfigDict(extra="forbid")

    movements: List[MovementOutput]


class DriverMovementSet(BaseModel):
    """The output of Layer 5 per company x scenario (section 10.5)."""

    model_config = ConfigDict(extra="forbid")

    company: str
    scenario: str
    scenario_version: str
    scenario_severity: str = Field(..., description="boundary | central (from section 6).")
    scenario_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    generated_at: datetime
    generated_by: str
    segments: List[SegmentMovementOutput]
    company_level: CompanyLevelMovementOutput
