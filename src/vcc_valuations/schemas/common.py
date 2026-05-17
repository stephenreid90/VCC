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
    """Company-level capital-structure stance (section 8.2)."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Durability(str, Enum):
    """Moat / franchise asset durability (section 8.2)."""

    LOW = "low"
    MODERATE = "moderate"
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
