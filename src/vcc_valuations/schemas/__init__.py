"""
Pydantic v2 schemas for the VCC valuations module.

These models are the formal expression of the YAML schemas described in
design/architecture.md sections 6.4, 7.4, 8.2, 8.4, 9.2, 10.3, 10.4, 10.5,
and 11.5. They are the single source of truth for what a valid scenario,
industry, company, driver, impact matrix entry, or assumption set looks like.

The design principle (per architecture spec section 5): the data files
(YAML under data/) carry the content; these schemas validate it. Domain
experts edit YAML without touching Python; engineers refactor logic
without re-entering domain content.

To export JSON Schemas for non-Python consumers (Ben's data workstream,
the eventual VCC dashboard renderer), run scripts/export_json_schemas.py.
"""

from vcc_valuations.schemas.common import (
    Rating,
    Direction,
    Magnitude,
    Confidence,
    LeveragePosture,
    Durability,
    LifecycleStage,
    GeographyScope,
)
from vcc_valuations.schemas.scenario import (
    Scenario,
    ScenarioFile,
    ScenarioNarrative,
    TimePhase,
    MacroVariable,
    MacroTimeSeriesPoint,
    MacroRegime,
)
from vcc_valuations.schemas.industry import (
    IndustryArchetype,
    IndustryArchetypeFile,
    FiveForces,
    Force,
    CostStructure,
    ScenarioSensitivity,
    DisruptionVector,
    Submarket,
)
from vcc_valuations.schemas.company import (
    CompanyPosition,
    CompanyPositionFile,
    Segment,
    Moat,
    CompetitivePosition,
    InnovationPosition,
    FranchiseAssets,
    BalanceSheet,
    CapitalAllocation,
    CorporateAction,
)
from vcc_valuations.schemas.driver import (
    Driver,
    DriverFile,
    DriverRange,
)
from vcc_valuations.schemas.linkage import (
    ImpactMatrix,
    ImpactMatrixEntry,
    DriverMovement,
    QuantifiedBand,
    CompanyOverride,
    DriverMovementSet,
)
from vcc_valuations.schemas.assumption import (
    AssumptionSet,
    SegmentAssumptions,
    ConsolidatedAssumptions,
    AssumptionCell,
    ReasoningTraceEntry,
)
from vcc_valuations.schemas.frameworks import (
    ComplementaryFramework,
    ComplementaryFrameworkType,
    PayorAndRegulator,
)

__all__ = [
    # common
    "Rating", "Direction", "Magnitude", "Confidence",
    "LeveragePosture", "Durability", "LifecycleStage", "GeographyScope",
    # scenario
    "Scenario", "ScenarioFile", "ScenarioNarrative", "TimePhase",
    "MacroVariable", "MacroTimeSeriesPoint", "MacroRegime",
    # industry
    "IndustryArchetype", "IndustryArchetypeFile", "FiveForces", "Force",
    "CostStructure", "ScenarioSensitivity", "DisruptionVector", "Submarket",
    # company
    "CompanyPosition", "CompanyPositionFile", "Segment", "Moat",
    "CompetitivePosition", "InnovationPosition", "FranchiseAssets",
    "BalanceSheet", "CapitalAllocation", "CorporateAction",
    # driver
    "Driver", "DriverFile", "DriverRange",
    # linkage
    "ImpactMatrix", "ImpactMatrixEntry", "DriverMovement", "QuantifiedBand",
    "CompanyOverride", "DriverMovementSet",
    # assumption
    "AssumptionSet", "SegmentAssumptions", "ConsolidatedAssumptions",
    "AssumptionCell", "ReasoningTraceEntry",
    # frameworks
    "ComplementaryFramework", "ComplementaryFrameworkType", "PayorAndRegulator",
]
