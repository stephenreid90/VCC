"""
Layer 2 — Industry archetype schema (architecture spec section 7.4).

An archetype is the typed analytical view of an industry — Five Forces,
lifecycle, cost structure, scenario sensitivities, disruption vectors,
regulatory regime, cyclicality, input dependencies, plus an optional
complementary framework where Porter does not adequately serve (section 7.5.1).
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from vcc_valuations.schemas.common import (
    ConcentrationStructure,
    CycleAmplitude,
    CyclePhase,
    GeographyScope,
    LifecycleStage,
    Rating,
)
from vcc_valuations.schemas.frameworks import ComplementaryFramework


class Force(BaseModel):
    """One of Porter's five forces (section 7.4)."""

    model_config = ConfigDict(extra="forbid")

    rating: Rating
    rationale: str = Field(..., description="Short paragraph; sub-determinants per Porter 2008.")


class FiveForces(BaseModel):
    """Porter's Five Forces, populated using the question bank in
    design/frameworks/five_forces_questions.md."""

    model_config = ConfigDict(extra="forbid")

    buyer_power: Force
    supplier_power: Force
    new_entrants: Force
    substitutes: Force
    rivalry: Force


class CostStructure(BaseModel):
    """Static cost-economics picture (section 7.4)."""

    model_config = ConfigDict(extra="forbid")

    primary_cost_drivers: List[str]
    operating_leverage: Rating
    capital_intensity: Rating
    fixed_vs_variable_mix: str
    labour_share_of_cost: Rating
    commodity_share_of_cost: Rating
    energy_share_of_cost: Rating
    imported_input_share_static: Rating = Field(
        ...,
        description=(
            "Static share of cost base from imported inputs. Renamed during the "
            "v0.1 editorial sweep to disambiguate from the responsiveness field "
            "under scenario_sensitivity.trade_and_supply_chain."
        ),
    )


# scenario_sensitivity sub-blocks (section 7.4).


class LabourSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intensity: Rating
    skill_mix: Rating
    wage_pass_through: Rating
    automation_potential: Rating


class PhysicalClimateSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_damage_risk: Rating
    demand_climate_sensitivity: Rating


class TechnologySensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    absorptive_capacity: Rating
    digital_substitution_risk: Rating


class EnergyTransitionSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operational_carbon_exposure: Rating
    customer_transition_exposure: Rating
    stranded_asset_risk: Rating


class DemographicSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    demand_age_profile: str
    labour_supply_sensitivity: Rating


class TradeAndSupplyChainSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    imported_input_share_responsiveness: Rating = Field(
        ...,
        description=(
            "Responsiveness of cost / supply to imported-input disruption. "
            "Distinct from cost_structure.imported_input_share_static, which "
            "captures the static share."
        ),
    )
    supply_chain_concentration: Rating


class RegulatoryCrossCuttingSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tax_sensitivity: Rating
    competition_policy_exposure: Rating
    data_and_digital_regulation: Rating


class ScenarioSensitivity(BaseModel):
    """Responsiveness picture — mediates scenario-to-driver transmission in Layer 5."""

    model_config = ConfigDict(extra="forbid")

    labour: LabourSensitivity
    physical_climate: PhysicalClimateSensitivity
    technology: TechnologySensitivity
    energy_transition: EnergyTransitionSensitivity
    demographic: DemographicSensitivity
    trade_and_supply_chain: TradeAndSupplyChainSensitivity
    regulatory_cross_cutting: RegulatoryCrossCuttingSensitivity


class DisruptionVector(BaseModel):
    """One disruption vector. Multiple per archetype (section 7.4)."""

    model_config = ConfigDict(extra="forbid")

    vector: str
    nature: str = Field(..., description="threat | opportunity | both")
    incumbency_position: str = Field(..., description="defender | attacker | neutral")
    time_horizon: str = Field(..., description="'0-3 years' | '3-7 years' | '7+ years'")
    severity: Rating
    certainty: Rating
    description: str


class RegulatoryRegime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_regulators: List[str]
    current_pressure: Rating
    known_step_changes: List[str]


class Cyclicality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cycle_length_years: Optional[int] = None
    current_cycle_phase: CyclePhase
    amplitude: CycleAmplitude


class InputDependencies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    critical_inputs: List[str]
    supply_risk: Rating


class Concentration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_3_share: Optional[float] = Field(None, ge=0.0, le=1.0)
    structure: ConcentrationStructure


class Submarket(BaseModel):
    """For multi_geographic archetypes (section 7.4)."""

    model_config = ConfigDict(extra="forbid")

    region: str
    weight: float = Field(..., ge=0.0, le=1.0)
    notes: Optional[str] = None


class IndustryArchetype(BaseModel):
    """Industry archetype per section 7.4."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    version: str
    geography: GeographyScope
    submarkets: Optional[List[Submarket]] = None
    five_forces: FiveForces
    complementary_framework: Optional[ComplementaryFramework] = None
    lifecycle_stage: LifecycleStage
    lifecycle_rationale: str
    concentration: Concentration
    cost_structure: CostStructure
    scenario_sensitivity: ScenarioSensitivity
    disruption_vectors: List[DisruptionVector] = []
    regulatory_regime: RegulatoryRegime
    cyclicality: Cyclicality
    input_dependencies: InputDependencies


class IndustryArchetypeFile(BaseModel):
    """Top-level YAML wrapper for data/industries/<id>.yaml."""

    model_config = ConfigDict(extra="forbid")

    industry_archetype: IndustryArchetype
