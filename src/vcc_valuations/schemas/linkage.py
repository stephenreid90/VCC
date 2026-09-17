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


class DecayHorizon(BaseModel):
    """How long an excess return is assumed to last, as a value rather than a sentence.

    D-58's implementation. Before this the horizon lived as prose inside
    ``DriverMovement.rationale`` — "decay horizon = 10-15 years" is a sentence, so
    there was nothing for a validator to read and nothing a test could hold to the
    rule, on a quantity §12 puts at 15-20% of terminal value. Dated horizons carry
    a band because that is how the evidence arrives; ``indefinite`` is admissible
    for a barrier of any kind under D-58, but never by omission.
    """

    model_config = ConfigDict(extra="forbid")

    years_low: Optional[int] = None
    years_high: Optional[int] = None
    indefinite: bool = False
    basis: str

    @model_validator(mode="after")
    def _dated_or_indefinite_but_not_neither(self) -> "DecayHorizon":
        dated = self.years_low is not None or self.years_high is not None
        if self.indefinite and dated:
            raise ValueError(
                "decay_horizon is both indefinite and dated; choose one. An "
                "indefinite horizon with a band attached reads as a hedge rather "
                "than a declaration (D-58)."
            )
        if not self.indefinite and not dated:
            raise ValueError(
                "decay_horizon declares neither a year band nor indefinite. D-58 "
                "permits indefinite for any barrier, but not by omission."
            )
        if dated:
            if self.years_low is None or self.years_high is None:
                raise ValueError("a dated decay_horizon needs both years_low and years_high.")
            if self.years_low <= 0 or self.years_high < self.years_low:
                raise ValueError(
                    f"decay_horizon band must be positive and ordered, got "
                    f"[{self.years_low}, {self.years_high}]."
                )
        return self


class ExcessReturnDefence(BaseModel):
    """The §10.6 rule 2 defended exception, structured (D-42).

    D-42 requires that where a terminal return exceeds the cost of capital, the
    valuation names four things: the moat source, the decay horizon, the threat,
    and a sensitivity test. All four were expressible in prose and one of them —
    the horizon — is a number, which is why the prose form could never be checked.

    ``moat_sources`` must name barrier-bearing sources. D-43a separated a RENT (a
    cash advantage with an end date, carried in the explicit period) from a BARRIER
    (what stops a rival taking the business, which is what the decay horizon
    measures), so defending a terminal excess return on a rent-bearing source is
    the confusion that ruling exists to prevent. The tie to ``Moat.source_roles``
    is not enforced here because the moat lives on the company file and this on the
    archetype matrix; the ratchet test is where the two are compared.
    """

    model_config = ConfigDict(extra="forbid")

    moat_sources: List[str] = Field(..., min_length=1)
    decay_horizon: DecayHorizon
    named_threat: str
    sensitivity: str
    finite_horizon_sensitivity: Optional[str] = None
    # D-42 step 2, and the reason the whole exercise exists. D-45 says the
    # terminal return is PINNED by the moat work and reinvestment is derived from
    # it; D-49 derives reinvestment from the balance sheet, which leaves the
    # return to emerge. The two are only consistent when the declared rate equals
    # terminal earnings over the rolled-forward capital base -- and nothing
    # compared them, because `terminal_roic` was a driver no engine read. Declare
    # the rate here and the diagnostic reconciles it. Optional, because a scenario
    # that has not yet formed the view should say so by absence rather than by a
    # number copied off the engine, which would make the check vacuous.
    declared_terminal_return: Optional[float] = None
    declared_terminal_return_basis: Optional[str] = None

    @model_validator(mode="after")
    def _a_declared_rate_carries_its_basis(self) -> "ExcessReturnDefence":
        if self.declared_terminal_return is not None and not (
                self.declared_terminal_return_basis or "").strip():
            raise ValueError(
                "declared_terminal_return needs declared_terminal_return_basis: a "
                "terminal return without a stated derivation is the defect D-50 "
                "was written about, on the largest number in the valuation."
            )
        return self

    @model_validator(mode="after")
    def _indefinite_horizon_declares_its_finite_sensitivity(self) -> "ExcessReturnDefence":
        """D-58: indefinite is admissible, but never silent."""
        if self.decay_horizon.indefinite and not (self.finite_horizon_sensitivity or "").strip():
            raise ValueError(
                "decay_horizon is indefinite, so D-58 requires the finite-horizon "
                "sensitivity declared beside it. Terminal value is the majority of "
                "these valuations; the most valuable assumption does not get to be "
                "the silent one."
            )
        return self


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
    # D-42. Present only on drivers that assert a terminal excess return, which in
    # practice means terminal_roic. Optional in the schema and obligatory in the
    # ratchet: tests/dcf/test_terminal_defence.py requires one wherever the
    # diagnostic measures a return above the cost of capital, or the pair named in
    # a baseline that may only shrink.
    excess_return_defence: Optional[ExcessReturnDefence] = None


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
    # Optional provenance / classification carried by some archetype matrices
    # (e.g. the bank matrix tags archetype_class and a version).
    archetype_class: Optional[str] = None
    version: Optional[str] = None


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
