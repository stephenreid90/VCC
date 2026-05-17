"""
Layer 3 — Company positioning (architecture spec section 8.2) plus the
corporate-action overlay (section 8.4).

Positioning blocks live primarily at the segment level — single-segment
companies carry a single segment that holds the positioning. Corporate
actions (demerger, acquisition, divestment, spin_off) are handled via the
overlay rather than time-keying segment weights.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from vcc_valuations.schemas.common import (
    CorporateActionKind,
    CostPositionPlacement,
    Durability,
    LeveragePosture,
    Rating,
)


# ---- Per-segment positioning sub-blocks ----


class Moat(BaseModel):
    """Section 8.2 moat block."""

    model_config = ConfigDict(extra="forbid")

    sources: List[str] = Field(
        ...,
        description=(
            "Enum members from: scale | brand | network | switching_cost | "
            "regulatory | resource | patent | distribution | data."
        ),
    )
    durability: Durability
    evidence: str


class CostPositionBlock(BaseModel):
    """Mainly relevant for commodity-like industries (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    placement_on_curve: CostPositionPlacement
    evidence: str


class DifferentiationPosition(BaseModel):
    """Mainly relevant for differentiated industries (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    pricing_power: Rating
    differentiation_basis: List[str]
    evidence: str


class CompetitivePosition(BaseModel):
    """Cost position + differentiation position (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    cost_position: CostPositionBlock
    differentiation_position: DifferentiationPosition


class InnovationPosition(BaseModel):
    """Required where archetype is innovation-driven (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    rd_intensity: Optional[float] = None
    pipeline_strength: Rating
    pipeline_horizon_years: int
    evidence: str


class FranchiseAssets(BaseModel):
    """Supply-side / distribution / customer-relationship moats (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    assets: List[str]
    durability: Durability
    evidence: str


class CapabilityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strengths: List[str]
    gaps: List[str]


class CustomerConcentration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_n: int
    share_of_revenue: float = Field(..., ge=0.0, le=1.0)
    narrative: str


class GeographicRegionShare(BaseModel):
    model_config = ConfigDict(extra="forbid")

    geo: str
    share_of_revenue: float = Field(..., ge=0.0, le=1.0)


class GeographicConcentration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    regions: List[GeographicRegionShare]
    narrative: str


class RiskExposures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commodity: List[str] = []
    regulatory: List[str] = []
    customer_concentration: CustomerConcentration
    geographic_concentration: GeographicConcentration


class MarketTrend(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction: str = Field(..., description="gaining | stable | losing")
    delta_5yr_bps: int = Field(..., description="Quantified change in share, basis points.")
    narrative: str


class MarketPosition(BaseModel):
    """One entry per meaningful market (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    market: str
    unit: str = Field(..., description="revenue | volume | other")
    share: float = Field(..., ge=0.0, le=1.0)
    rank: int
    share_trend: MarketTrend


class ScenarioSensitivityOverrides(BaseModel):
    """Company-level or segment-level overrides to archetype scenario_sensitivity (section 8.2)."""

    model_config = ConfigDict(extra="allow")  # shape varies; opaque payload


# ---- Per-segment block ----


class Segment(BaseModel):
    """One operating segment (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    segment: str
    industry_archetype: str = Field(..., description="FK to Layer 2 industry archetype id.")
    functional_currency: str
    functional_currency_rationale: str
    revenue_share: float = Field(..., ge=0.0, le=1.0)
    ebit_share: float
    notes: Optional[str] = None
    market_positions: List[MarketPosition]
    moat: Moat
    competitive_position: CompetitivePosition
    innovation_position: Optional[InnovationPosition] = None
    franchise_assets: Optional[FranchiseAssets] = None
    capability_profile: CapabilityProfile
    risk_exposures: RiskExposures
    archetype_specific: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Shape varies by industry archetype; see architecture spec section 8.3 "
            "and the archetype's own schema (e.g. banking: CET1, NIM, cost-to-income)."
        ),
    )
    scenario_sensitivity_overrides: Optional[ScenarioSensitivityOverrides] = None


# ---- Company-level blocks (parent-level) ----


class BalanceSheet(BaseModel):
    """Consolidated balance-sheet posture (section 8.2)."""

    model_config = ConfigDict(extra="forbid")

    net_debt_ebitda: Optional[float] = Field(
        None,
        description="Null where archetype_specific replaces it (e.g. banks).",
    )
    leverage_posture: LeveragePosture
    liquidity: str


class CapitalAllocation(BaseModel):
    """Section 8.2."""

    model_config = ConfigDict(extra="forbid")

    dividend_policy: str
    buyback_posture: str
    m_and_a_posture: str
    reinvestment_rate: Optional[float] = Field(
        None,
        description="Definition: 5-year average capex / EBITDA (specify alternative in comment).",
    )


class ManagementAndGovernance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy_quality: Rating
    strategy_evidence: str
    execution_track_record: Rating
    execution_evidence: str


class ESGAndTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carbon_intensity: str
    transition_plan: str
    stranded_asset_exposure: str


# ---- Corporate-action overlay (section 8.4) ----


class PostEventWeight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: str
    revenue_share: float = Field(..., ge=0.0, le=1.0)
    ebit_share: float


class EvidenceRef(BaseModel):
    """Used across the schema for traceability (sections 10.3, 10.4, 8.4)."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    location: Optional[str] = None
    date_accessed: Optional[str] = None


class CorporateAction(BaseModel):
    """Discrete corporate event reshaping segment weights at an effective year (section 8.4)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    kind: CorporateActionKind
    effective_year: int = Field(..., ge=1)
    scenario_id: str = Field(..., description="Scenario id, or 'all' for cross-scenario.")
    affected_segments: List[str]
    post_event_weights: List[PostEventWeight]
    rationale: str
    evidence_refs: List[EvidenceRef] = []


# ---- Top-level CompanyPosition ----


class CompanyPosition(BaseModel):
    """Company position per section 8.2."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    ticker: str
    reporting_currency: str
    functional_currency: str
    functional_currency_rationale: str
    balance_sheet: BalanceSheet
    capital_allocation: CapitalAllocation
    management_and_governance: ManagementAndGovernance
    esg_and_transition: ESGAndTransition
    scenario_sensitivity_overrides_global: Optional[ScenarioSensitivityOverrides] = None
    segments: List[Segment] = Field(..., min_length=1)
    corporate_actions: List[CorporateAction] = []


class CompanyPositionFile(BaseModel):
    """Top-level YAML wrapper for data/companies/<id>.yaml."""

    model_config = ConfigDict(extra="forbid")

    company_position: CompanyPosition
