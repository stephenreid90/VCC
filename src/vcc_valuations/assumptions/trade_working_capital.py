"""Derive a trade-working-capital intensity from the committed observation series.

The rate is never stored (D-16). It is computed here, from the raw periods in
``analyses/<company>_trade_working_capital_history.yaml``, over the window that
file declares — and only over periods whose ``demerger_status`` says they belong
to the entity being valued.

Why a separate derivation from ``working_capital_intensity_from_data``: that one
implements the statutory construction ratified under D-29/D-31 — total current
assets less cash, less total current liabilities plus current interest-bearing
debt. This one implements the company's own published measure, which is narrower
and which the company reports consistently across many periods. The two do not
agree on the same balance sheet. Neither is wrong; they are different measures,
and the point of keeping them apart is that a rate assembled from one measure's
numerator and another's denominator is exactly the defect D-50 exists to catch.

The window, the entity, the level and the method all come from the data file
rather than from this module, so changing the window is a data change with a
recorded reason and not a code change.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


class TradeWorkingCapitalError(ValueError):
    """Raised when the series cannot support the window it declares."""


@dataclass(frozen=True)
class PeriodIntensity:
    """One period's observed intensity, with everything it was struck from."""

    period: str
    label: str
    working_capital: float
    revenue: float
    revenue_period: str

    @property
    def intensity(self) -> float:
        return self.working_capital / self.revenue


@dataclass(frozen=True)
class TradeWorkingCapitalIntensity:
    """The derived rate and its declared basis (D-50)."""

    intensity: float
    periods: List[PeriodIntensity]
    entity: str
    window: str
    level: str
    method: str
    source_document: str

    @property
    def basis(self) -> Dict[str, str]:
        return {
            "entity": self.entity,
            "window": self.window,
            "level": self.level,
            "source": self.source_document,
        }

    def explain(self) -> str:
        lines = [
            f"Trade working capital intensity, {self.method}",
            f"  entity: {self.entity}",
            f"  window: {self.window}",
            f"  level:  {self.level}",
            f"  source: {self.source_document}",
        ]
        for p in self.periods:
            lines.append(
                f"  {p.label}: WC {p.working_capital} / revenue {p.revenue} "
                f"({p.revenue_period})"
            )
        return "\n".join(lines)


def _revenue_lookup(doc: Dict[str, Any]) -> Dict[str, float]:
    return {
        str(r["period"]): float(r["revenue"])
        for r in doc.get("revenue_observations", [])
    }


def _ttm(revenues: Dict[str, float], key: str) -> float:
    """A trailing-twelve-month denominator: full year, less the stale half, plus the fresh one.

    Only the one TTM construction the series declares is supported. Anything else
    is a window change and belongs in the data file, not in a special case here.
    """
    if key != "TTM_2026-03-31":
        raise TradeWorkingCapitalError(f"unsupported denominator period {key!r}")
    try:
        return revenues["FY2025"] - revenues["1H2025"] + revenues["1H2026"]
    except KeyError as exc:
        raise TradeWorkingCapitalError(
            f"TTM denominator needs FY2025, 1H2025 and 1H2026; missing {exc}"
        ) from exc


def trade_working_capital_intensity(path: Path | str) -> TradeWorkingCapitalIntensity:
    """Compute the intensity over the window the series file declares."""
    path = Path(path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))

    window = doc.get("strike_window") or {}
    if window.get("status") != "SET":
        raise TradeWorkingCapitalError(
            f"{path.name}: strike window is not set "
            f"({window.get('blocked_on', 'no reason recorded')})"
        )

    method = window["method"]
    if method != "mean_of_period_intensities":
        raise TradeWorkingCapitalError(f"unsupported method {method!r}")

    by_period = {str(o["period"]): o for o in doc["observations"]}
    revenues = _revenue_lookup(doc)

    periods: List[PeriodIntensity] = []
    for spec in window["periods"]:
        key = str(spec["period"])
        obs = by_period.get(key)
        if obs is None:
            raise TradeWorkingCapitalError(f"{key} is not in the series")
        if obs["demerger_status"] != "post":
            raise TradeWorkingCapitalError(
                f"{key} is {obs['demerger_status']}-demerger — wrong entity for this window"
            )
        den_key = str(spec["denominator_period"])
        revenue = (
            _ttm(revenues, den_key) if den_key.startswith("TTM_") else revenues[den_key]
        )
        periods.append(
            PeriodIntensity(
                period=key,
                label=obs["label"],
                working_capital=float(obs[spec["numerator"]]),
                revenue=revenue,
                revenue_period=den_key,
            )
        )

    if not periods:
        raise TradeWorkingCapitalError("the declared window selected no periods")

    mean = sum(p.intensity for p in periods) / len(periods)
    return TradeWorkingCapitalIntensity(
        intensity=mean,
        periods=periods,
        entity=window["entity"],
        window=window["window"],
        level=window["level"],
        method=method,
        source_document=doc["source"]["document"],
    )
