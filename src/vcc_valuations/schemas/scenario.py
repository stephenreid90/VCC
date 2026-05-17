"""
Layer 1 — Scenario schema (architecture spec section 6.4).

A scenario is a named container for what-if data with an analytical narrative.
The YAML files at data/scenarios/<id>.yaml are validated against the
ScenarioFile model. The accompanying data/scenarios/<id>.md is the prose
narrative deliverable per section 16.1 item 1; not validated here.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from vcc_valuations.schemas.common import MacroVariableType


class ScenarioNarrative(BaseModel):
    """Prescribed-structure narrative block (section 6.4)."""

    model_config = ConfigDict(extra="forbid")

    key_mechanism: str = Field(
        ..., description="One paragraph stating the central logic of the scenario."
    )
    distinguishing_features: str = Field(
        ..., description="How it differs from other scenarios in the library."
    )
    leading_indicators: str = Field(
        ..., description="What you'd observe if this scenario were materialising."
    )
    disconfirming_evidence: str = Field(
        ..., description="What would invalidate this scenario."
    )


class TimePhase(BaseModel):
    """One phase of a scenario's time profile (section 6.4)."""

    model_config = ConfigDict(extra="forbid")

    phase: str = Field(..., description="e.g. 'initial_shock', 'adjustment', 'new_equilibrium'.")
    year_start: int = Field(..., ge=1)
    year_end: Optional[int] = Field(
        None,
        description="None = open-ended through terminal.",
    )
    characterisation: str


class MacroTimeSeriesPoint(BaseModel):
    """A single year-value observation with optional confidence band."""

    model_config = ConfigDict(extra="forbid")

    year: int = Field(..., ge=1)
    value: float
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None


class MacroRegime(BaseModel):
    """Qualitative regime tag for a macro variable (section 6.4)."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="e.g. 'anchored', 'un_anchored', 'fragmented'.")
    description: str


class MacroVariable(BaseModel):
    """A macro variable; either quantitative time series or qualitative regime."""

    model_config = ConfigDict(extra="forbid")

    variable: str = Field(
        ..., description="e.g. 'real_gdp_growth_world', 'cpi_inflation_advanced'."
    )
    units: str = Field(..., description="e.g. 'percent_yoy', 'percent', 'regime', 'eur_per_tco2'.")
    type: MacroVariableType
    time_series: Optional[List[MacroTimeSeriesPoint]] = None
    regime: Optional[MacroRegime] = None


# Narrative-only blocks. These are intentionally string-valued in v0.1; later
# versions may introduce structured sub-models if validators need to enforce
# specific properties.


class Geopolitical(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bloc_dynamics: str
    trade_policy: str
    resource_nationalism: str


class Technology(BaseModel):
    model_config = ConfigDict(extra="forbid")

    productivity_regime: str
    disruption_vectors: List[str]


class Regulatory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    climate_policy: str
    financial_regulation: str
    healthcare_regulation: str


class CommodityAndEnergy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    oil_regime: str
    gas_regime: str
    metals_regime: str
    ag_regime: str


class DemandProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consumer: str
    industrial: str
    infrastructure: str
    healthcare: str


class FinancialConditions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_rates: str
    credit_spreads: str
    fx_regime: str
    equity_risk_premium: str


class Scenario(BaseModel):
    """A scenario per section 6.4."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Stable snake_case identifier.")
    name: str = Field(..., description="Display name.")
    version: str = Field(..., description="e.g. '2026-Q2-v1'.")
    published: date
    narrative: ScenarioNarrative
    time_profile: List[TimePhase] = Field(..., min_length=1)
    macro_variables: List[MacroVariable] = Field(..., min_length=1)
    geopolitical: Geopolitical
    technology: Technology
    regulatory: Regulatory
    commodity_and_energy: CommodityAndEnergy
    demand_profile: DemandProfile
    financial_conditions: FinancialConditions
    probability: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Optional per section 3.3; canonical output is comparative.",
    )


class ScenarioFile(BaseModel):
    """Top-level YAML wrapper: each data/scenarios/<id>.yaml has `scenario:` at root."""

    model_config = ConfigDict(extra="forbid")

    scenario: Scenario
