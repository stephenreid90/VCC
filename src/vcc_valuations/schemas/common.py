"""
Shared enums and primitive types used across the schema modules.

Convention (per architecture spec section 10.2 and section 7.2):
- All ratings use a three-point ordinal: low | moderate | high.
- Matrix entries split direction (negative | neutral | positive) and
  magnitude (small | moderate | large) as two separate fields, giving
  seven distinct non-trivial movements plus a not_applicable flag.
- Confidence is "joint confidence in the direction x magnitude assignment,
  assuming the scenario plays out as defined".
"""

from enum import Enum


class Rating(str, Enum):
    """Three-point ordinal — the standard across the framework."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Direction(str, Enum):
    """Matrix entry direction. Separate from magnitude (section 10.2)."""

    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class Magnitude(str, Enum):
    """Matrix entry magnitude. Separate from direction (section 10.2)."""

    SMALL = "small"
    MODERATE = "moderate"
    LARGE = "large"


class Confidence(str, Enum):
    """Pinned meaning: joint confidence in direction x magnitude."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class LeveragePosture(str, Enum):
    """Company-level capital-structure stance (section 8.2).

    ``prudentially_strong`` is the bank-archetype posture: banks are not scored on
    net-debt/EBITDA leverage (that field is null for banks — see BalanceSheet); their
    capital-structure stance is a regulatory capital-adequacy judgement (CET1 vs the
    APRA "unquestionably strong" floor), captured here rather than the generic scale.
    """

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    PRUDENTIALLY_STRONG = "prudentially_strong"


class Durability(str, Enum):
    """Moat / franchise asset durability (section 8.2)."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ArchetypeRating(str, Enum):
    """Finer ordinal used in industry-archetype assessments (§7.4 v2 spec).

    A superset of the three-point ``Rating`` with the ``x_to_y`` gradations and
    ``very_low`` that the newer archetype files (bank, biopharma) use for force
    ratings, disruption severity and supply risk. Kept separate from ``Rating`` so
    company-positioning fields stay on the strict three-point scale.
    """

    VERY_LOW = "very_low"
    LOW = "low"
    LOW_TO_MODERATE = "low_to_moderate"
    MODERATE = "moderate"
    MODERATE_TO_HIGH = "moderate_to_high"
    HIGH = "high"


class LifecycleStage(str, Enum):
    """Industry lifecycle stage (section 7.3)."""

    EMERGING = "emerging"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINING = "declining"


class GeographyScope(str, Enum):
    """Industry geographical scope (section 7.4)."""

    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    MULTI_GEOGRAPHIC = "multi_geographic"
    DOMESTIC_AU_NZ = "domestic_au_nz"  # geography-as-identity for the AU/NZ bank archetype


class DriverRole(str, Enum):
    """Whether a driver is written by Layer 5 or computed by Layer 6 (section 9.2)."""

    PRIMARY = "primary"
    DERIVED = "derived"


class DriverScope(str, Enum):
    """Where a driver is populated (section 9.2)."""

    COMPANY = "company"
    SEGMENT = "segment"


class ValuationModel(str, Enum):
    """Which valuation engine consumes the driver (section 9.2)."""

    FCF = "fcf"
    DDM = "ddm"
    RESIDUAL_INCOME = "residual_income"


class CostPositionPlacement(str, Enum):
    """Position on cost curve (section 8.2)."""

    BOTTOM_QUARTILE = "bottom_quartile"
    SECOND = "2nd"
    THIRD = "3rd"
    TOP_QUARTILE = "top_quartile"
    NOT_APPLICABLE = "n/a"


class ConcentrationStructure(str, Enum):
    """Industry concentration structure (section 7.4)."""

    FRAGMENTED = "fragmented"
    CONSOLIDATING = "consolidating"
    OLIGOPOLY = "oligopoly"
    MONOPOLY = "monopoly"


class CycleAmplitude(str, Enum):
    """Industry cyclicality amplitude (section 7.4)."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CyclePhase(str, Enum):
    """Current cycle phase (section 7.4)."""

    TROUGH = "trough"
    EARLY = "early"
    MID = "mid"
    LATE_MID = "late_mid"
    LATE = "late"
    PEAK = "peak"


class CorporateActionKind(str, Enum):
    """Type of corporate-action overlay event (section 8.4)."""

    DEMERGER = "demerger"
    ACQUISITION = "acquisition"
    DIVESTMENT = "divestment"
    SPIN_OFF = "spin_off"


class MacroVariableType(str, Enum):
    """Whether a macro variable is a time series or a regime tag (section 6.4)."""

    TIME_SERIES = "time_series"
    REGIME = "regime"


class TimeProfileShape(str, Enum):
    """Named time profiles from the section 11.3 library."""

    IMPULSE = "impulse"
    REGIME_SHIFT = "regime_shift"
    STEP = "step"
    CYCLICAL = "cyclical"
    FRONT_LOADED = "front_loaded"
    BACK_LOADED = "back_loaded"
    LINEAR_THROUGH_HORIZON = "linear_through_horizon"
