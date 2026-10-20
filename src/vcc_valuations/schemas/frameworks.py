"""
Complementary frameworks for archetypes Porter does not adequately serve
(architecture spec section 7.5.1).

Each complementary framework is enum-typed; the details payload shape varies
by framework type. The defined-enum approach was a deliberate workshop
decision (recorded in WORKING_NOTES) to enforce comparability discipline
across instances within a framework type.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vcc_valuations.schemas.common import Rating


class ComplementaryFrameworkType(str, Enum):
    """The enum that drives details-block shape (section 7.5.1)."""

    PAYOR_AND_REGULATOR = "payor_and_regulator"
    NETWORK_EFFECT = "network_effect"
    RESOURCE_LIFECYCLE = "resource_lifecycle"
    NONE = "none"


# payor_and_regulator framework — schema co-located with design/frameworks/payor_and_regulator.md.


class RegulatorMandate(str, Enum):
    PRUDENTIAL = "prudential"
    CONDUCT = "conduct"
    ANTITRUST = "antitrust"
    SAFETY = "safety"
    PRICING = "pricing"
    MARKET_ACCESS = "market_access"


class Regulator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Named regulator, e.g. 'APRA', 'ASIC'.")
    mandate: RegulatorMandate
    instruments: List[str]
    independence: Rating


class BindingConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: str
    level: str
    consequence_of_breach: str
    severity: Rating


class RegulatoryRegimeDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    favourability_to_incumbents: Rating
    policy_stance: Literal[
        "protective", "pro_competition", "pro_consumer", "pro_investment", "mixed"
    ]
    narrative: str


class StepChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    effective_date: Optional[str] = None
    uncertainty: Rating


class RegulatoryDynamic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction: Literal["tightening", "steady", "loosening"]
    known_step_changes: List[StepChange]


class PayorChannel(str, Enum):
    DIRECT_PAYMENT = "direct_payment"
    INSURANCE = "insurance"
    GOVERNMENT_SCHEME = "government_scheme"
    RATE_RECOVERY = "rate_recovery"
    FEE_BASED = "fee_based"


class Payor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    channel: PayorChannel
    share_of_revenue: float = Field(..., ge=0.0, le=1.0)


class PayorMixEvolution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction: Literal[
        "stable",
        "shifting_to_public",
        "shifting_to_private",
        "consolidating",
        "fragmenting",
    ]
    pace: Rating
    narrative: str


class CompetitiveEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimensions: List[str]
    narrative: str


class RegimeAsymmetry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    direction: Literal[
        "favours_incumbents", "favours_entrants", "favours_specific_segment"
    ]
    materiality: Rating


class PayorAndRegulator(BaseModel):
    """Details block when type == payor_and_regulator (section 7.5.1)."""

    model_config = ConfigDict(extra="forbid")

    axis_weight: Literal[
        "regulator_dominant", "payor_dominant", "both_material"
    ]
    regulators: List[Regulator]
    binding_constraints: List[BindingConstraint]
    regime: RegulatoryRegimeDetail
    dynamic: RegulatoryDynamic
    payors: List[Payor]
    payor_concentration: Rating
    payor_pricing_power: Rating
    payor_mix_evolution: PayorMixEvolution
    competitive_envelope: CompetitiveEnvelope
    asymmetries: List[RegimeAsymmetry]


# resource_lifecycle framework — schema co-located with
# design/methodology/resource_lifecycle_and_mining_drivers.md (written 20 Oct 2026 for
# the first resource archetype, gold_producers; architecture.md §7.5.1 said "schema TBD
# when first used"). It records what makes a depleting-asset archetype comparable across
# instances: what is sold and at what scenario price, how the inventory that sets mine
# life is counted, what happens after it runs out, and the jurisdictional and
# stranded-asset view. The engine reads the series names and the two bases; the rest is
# the analytical record.


class CommodityRole(str, Enum):
    PRIMARY = "primary"
    BY_PRODUCT = "by_product"


class Commodity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    role: CommodityRole
    price_series: str = Field(..., description="Scenario macro variable carrying the price path.")
    price_units: str = Field(..., description="Units of the scenario series, e.g. 'usd_per_oz_real_2026'.")
    rationale: str


class InventoryBasis(str, Enum):
    """How the producing inventory that sets mine life is counted (D-98 proposed)."""

    STATED_LIFE = "stated_life"        # the company's disclosed life-of-mine end year
    RESERVES = "reserves"              # Ore Reserves only, contained x recovery


class ReplacementTreatment(str, Enum):
    """What the valuation assumes once the declared inventory is mined (D-97 proposed)."""

    ZERO_NPV = "zero_npv"              # replacement capital earns the cost of capital


class JurisdictionRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jurisdiction: str
    rating: Rating
    rationale: str


class ResourceLifecycle(BaseModel):
    """Details block when type == resource_lifecycle (architecture.md §7.5.1)."""

    model_config = ConfigDict(extra="forbid")

    commodities: List[Commodity] = Field(..., min_length=1)
    price_basis: str = Field(..., description="How a real price series becomes nominal.")
    inflation_series: str = Field(..., description="Scenario series that inflates real prices and costs.")
    fx_series: Optional[str] = Field(None, description="Scenario series: USD per unit of the functional currency.")
    cost_metric: str = Field(..., description="The archetype's unit-cost measure, e.g. AISC.")
    cost_curve_note: str
    inventory_basis: InventoryBasis
    inventory_basis_rationale: str
    replacement: ReplacementTreatment
    replacement_rationale: str
    reserve_life_note: str
    jurisdictions: List[JurisdictionRisk] = Field(..., min_length=1)
    stranded_asset_trajectory: Rating
    stranded_asset_rationale: str


class ComplementaryFramework(BaseModel):
    """Wrapper carried on an industry archetype (section 7.4 schema extension)."""

    model_config = ConfigDict(extra="forbid")

    type: ComplementaryFrameworkType
    details: Optional[Union[PayorAndRegulator, ResourceLifecycle, Dict[str, Any]]] = Field(
        None,
        description=(
            "Shape determined by type. For 'payor_and_regulator' use PayorAndRegulator; "
            "for 'resource_lifecycle' use ResourceLifecycle (20 Oct 2026). For "
            "'network_effect' the details schema is TBD; free-form Dict is permitted in "
            "v0.1 with a tightening planned per architecture spec section 7.7 review item 9."
        ),
    )

    @model_validator(mode="after")
    def _resource_lifecycle_is_typed(self) -> "ComplementaryFramework":
        """A resource_lifecycle block must validate as ResourceLifecycle, not fall to Dict.

        The Union would otherwise accept any mapping, which is the "comment block with
        delusions of structure" §7.5.1 warns about.
        """
        if self.type == ComplementaryFrameworkType.RESOURCE_LIFECYCLE:
            if self.details is None:
                raise ValueError("resource_lifecycle requires a details block.")
            if not isinstance(self.details, ResourceLifecycle):
                self.details = ResourceLifecycle.model_validate(self.details)
        return self
