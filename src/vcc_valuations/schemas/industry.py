"""
Layer 2 — Industry archetype schema (architecture spec section 7.4).

An archetype is the typed analytical view of an industry — Five Forces,
lifecycle, cost structure, scenario sensitivities, disruption vectors,
regulatory regime, cyclicality, input dependencies, plus an optional
complementary framework where Porter does not adequately serve (section 7.5.1).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vcc_valuations.schemas.common import (
    ArchetypeRating,
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

    rating: ArchetypeRating
    rationale: str = Field(..., description="Short paragraph; sub-determinants per Porter 2008.")


class RivalrySubforce(BaseModel):
    """One named dimension of rivalry, where a single rating is too blunt.

    Typed 23 Aug 2026 (batch 3, item 19). It was ``Dict[str, Any]``, so a
    sub-force with no rating — or with the rating under a misspelt key —
    validated cleanly and then read as absent downstream.
    """

    model_config = ConfigDict(extra="forbid")

    sub_dimension: str
    rating: ArchetypeRating
    rationale: str


class FiveForces(BaseModel):
    """Porter's Five Forces, populated using the question bank in
    design/frameworks/five_forces_questions.md.

    Two naming generations coexist: the original ``new_entrants`` / ``substitutes``
    (industrial archetypes) and the §7.4-v2 ``threat_of_new_entrants`` /
    ``threat_of_substitutes`` (+ optional ``rivalry_subforces``) used by the newer
    bank and biopharma archetypes. Both are accepted; at least one form of each
    force is expected.
    """

    model_config = ConfigDict(extra="forbid")

    buyer_power: Force
    supplier_power: Force
    new_entrants: Optional[Force] = None
    substitutes: Optional[Force] = None
    threat_of_new_entrants: Optional[Force] = None
    threat_of_substitutes: Optional[Force] = None
    rivalry: Force
    rivalry_subforces: Optional[List[RivalrySubforce]] = None

    @model_validator(mode="after")
    def _each_force_present_once(self) -> "FiveForces":
        """Every force present exactly once, in one naming generation.

        Added 23 Aug 2026 (batch 3, item 19). Before this a block carrying
        neither ``new_entrants`` nor ``threat_of_new_entrants`` validated
        cleanly — five forces with three of them, and nothing said so. Worse,
        both generations could be supplied at once with contradictory ratings,
        and which one won depended on the reader.
        """
        for old_name, new_name in (
            ("new_entrants", "threat_of_new_entrants"),
            ("substitutes", "threat_of_substitutes"),
        ):
            old_v = getattr(self, old_name)
            new_v = getattr(self, new_name)
            if old_v is None and new_v is None:
                raise ValueError(
                    f"five_forces is missing the {old_name.replace('_', ' ')} force: "
                    f"supply either {old_name!r} (original naming) or {new_name!r} "
                    "(§7.4-v2 naming)."
                )
            if old_v is not None and new_v is not None:
                if old_v.rating != new_v.rating:
                    raise ValueError(
                        f"five_forces carries both {old_name!r} and {new_name!r} with "
                        f"CONTRADICTORY ratings ({old_v.rating} vs {new_v.rating}). "
                        "Keep one naming generation."
                    )
                raise ValueError(
                    f"five_forces carries both {old_name!r} and {new_name!r}. They agree, "
                    "but two names for one force is how they stop agreeing — keep one."
                )
        return self


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
    severity: ArchetypeRating
    certainty: ArchetypeRating
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
    rationale: Optional[str] = None


class InputDependencies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    critical_inputs: List[str]
    supply_risk: ArchetypeRating
    rationale: Optional[str] = None


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
    # Industrial archetypes carry the full lifecycle / concentration / cost-structure /
    # scenario-sensitivity blocks. The newer bank + biopharma archetypes (§7.4 v2) capture
    # that structure in archetype-specific blocks instead, so these are optional.
    lifecycle_stage: Optional[LifecycleStage] = None
    lifecycle_rationale: Optional[str] = None
    concentration: Optional[Concentration] = None
    cost_structure: Optional[CostStructure] = None
    scenario_sensitivity: Optional[ScenarioSensitivity] = None
    disruption_vectors: List[DisruptionVector] = []
    regulatory_regime: Optional[RegulatoryRegime] = None
    cyclicality: Cyclicality
    input_dependencies: InputDependencies
    # §7.4-v2 additions carried by the newer archetypes.
    archetype_class: Optional[str] = None
    bank_archetype: Optional[BankArchetype] = None


# ---------------------------------------------------------------- §7.4-v2 bank
# These were one ``Dict[str, Any]`` until 23 Aug 2026 (batch 3, item 19). The
# block carries the capital floor, the credit-cycle anchor and the cost-of-equity
# anchor that the bank engine's own inputs are calibrated against, so a typo in
# any key was a silent zero-or-absent rather than a validation error — which is
# the same failure mode the working-capital exemption rule exists to prevent.
class Cet1Floor(BaseModel):
    """Regulatory CET1 floor, built from its named components.

    ``components_in_total`` must name exactly which components the stated floor
    comprises, and the total is checked against those. It exists because the
    naive sum of every component is NOT always the floor — a countercyclical
    buffer can be tracked without sitting inside the headline requirement — and
    a total that silently disagrees with its own components is unreadable either
    way. Naming them turns "these do not add up" into "here is what adds up, and
    here is what is deliberately outside it".
    """

    model_config = ConfigDict(extra="forbid")

    regulatory_minimum: float
    capital_conservation_buffer: float
    countercyclical_buffer: float
    d_sib_surcharge: float = 0.0
    total_floor: float
    components_in_total: List[str]
    rationale: str

    @model_validator(mode="after")
    def _total_matches_its_declared_components(self) -> "Cet1Floor":
        allowed = {"regulatory_minimum", "capital_conservation_buffer",
                   "countercyclical_buffer", "d_sib_surcharge"}
        unknown = [c for c in self.components_in_total if c not in allowed]
        if unknown:
            raise ValueError(f"cet1_floor.components_in_total names unknown components: {unknown}")
        total = sum(getattr(self, c) for c in self.components_in_total)
        if abs(total - self.total_floor) > 1e-9:
            raise ValueError(
                f"cet1_floor.total_floor {self.total_floor} does not equal the sum of "
                f"the components it declares ({', '.join(self.components_in_total)} = "
                f"{total}). Fix the total, the components, or the declaration."
            )
        return self


class CreditCycleAnchor(BaseModel):
    """Through-cycle, peak and benign credit-loss anchors, in basis points."""

    model_config = ConfigDict(extra="forbid")

    through_cycle_loss_rate_bps: float
    peak_cycle_loss_rate_bps: float
    benign_cycle_loss_rate_bps: float
    rationale: str

    @model_validator(mode="after")
    def _ordered_benign_through_peak(self) -> "CreditCycleAnchor":
        if not (self.benign_cycle_loss_rate_bps
                <= self.through_cycle_loss_rate_bps
                <= self.peak_cycle_loss_rate_bps):
            raise ValueError(
                "credit_cycle_anchor must run benign <= through-cycle <= peak, got "
                f"{self.benign_cycle_loss_rate_bps} / "
                f"{self.through_cycle_loss_rate_bps} / {self.peak_cycle_loss_rate_bps}."
            )
        return self


class RwaDensityAnchor(BaseModel):
    """Indicative risk-weighted-asset density by exposure class."""

    model_config = ConfigDict(extra="forbid")

    housing_mortgages: float
    business_lending: float
    institutional: float
    sovereign_and_high_grade: float
    rationale: str


class PeerBeta(BaseModel):
    """One peer in the archetype's beta dataset (§3.5.3 triangulation)."""

    model_config = ConfigDict(extra="forbid")

    bank: str
    beta_measured: float
    inclusion: str
    notes: str


class BankCostOfEquityAnchor(BaseModel):
    """The archetype-level Ke anchor and the peer evidence behind it.

    Ranges are ``[low, high]`` and are validated as such: a reversed pair would
    otherwise read as a range nobody could see was backwards.
    """

    model_config = ConfigDict(extra="forbid")

    risk_free_rate: float
    equity_risk_premium: float
    beta_range_measured: List[float]
    beta_range_comparable_cluster: List[float]
    beta_anchor_selected: float
    cost_of_equity_range_measured: List[float]
    cost_of_equity_range_comparable: List[float]
    cost_of_equity_anchor_selected: float
    peer_beta_dataset_2026_06_15: List[PeerBeta]
    rationale: str

    @model_validator(mode="after")
    def _ranges_are_low_then_high(self) -> "BankCostOfEquityAnchor":
        for name in ("beta_range_measured", "beta_range_comparable_cluster",
                     "cost_of_equity_range_measured", "cost_of_equity_range_comparable"):
            pair = getattr(self, name)
            if len(pair) != 2 or pair[0] > pair[1]:
                raise ValueError(f"{name} must be [low, high], got {pair}.")
        return self


class BankArchetype(BaseModel):
    """§7.4-v2 bank-specific archetype block."""

    model_config = ConfigDict(extra="forbid")

    regulator: str
    secondary_regulators: List[str] = []
    cet1_floor: Cet1Floor
    cet1_management_buffer_typical: float
    credit_cycle_anchor: CreditCycleAnchor
    rwa_density_anchor: RwaDensityAnchor
    cost_of_equity_anchor: BankCostOfEquityAnchor


class IndustryArchetypeFile(BaseModel):
    """Top-level YAML wrapper for data/industries/<id>.yaml."""

    model_config = ConfigDict(extra="forbid")

    industry_archetype: IndustryArchetype
