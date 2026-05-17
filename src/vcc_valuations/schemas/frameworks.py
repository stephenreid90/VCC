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

from pydantic import BaseModel, ConfigDict, Field

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


class ComplementaryFramework(BaseModel):
    """Wrapper carried on an industry archetype (section 7.4 schema extension)."""

    model_config = ConfigDict(extra="forbid")

    type: ComplementaryFrameworkType
    details: Optional[Union[PayorAndRegulator, Dict[str, Any]]] = Field(
        None,
        description=(
            "Shape determined by type. For 'payor_and_regulator' use PayorAndRegulator. "
            "For 'network_effect' and 'resource_lifecycle' the details schemas are TBD; "
            "free-form Dict is permitted in v0.1 with a tightening planned per "
            "architecture spec section 7.7 review item 9."
        ),
    )
