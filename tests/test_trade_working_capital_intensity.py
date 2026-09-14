"""The trade-working-capital intensity, pinned, with its basis.

Pins the derived rate so a change to the observation series or the declared
window is a visible event rather than a silent drift, and checks the guards that
stop the window being widened into the wrong entity.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.assumptions.trade_working_capital import (
    TradeWorkingCapitalError,
    trade_working_capital_intensity,
)

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "analyses" / "dnl_trade_working_capital_history.yaml"


@pytest.fixture(scope="module")
def derived():
    return trade_working_capital_intensity(SERIES)


def test_the_rate_is_pinned(derived) -> None:
    assert derived.intensity == pytest.approx(0.157016, abs=5e-7)  # ssot-allow: pinned derivation


def test_each_period_is_pinned(derived) -> None:
    by_period = {p.period: p for p in derived.periods}
    assert by_period["2025-09-30"].intensity == pytest.approx(0.164093, abs=5e-7)  # ssot-allow: pinned derivation
    assert by_period["2026-03-31"].intensity == pytest.approx(0.149939, abs=5e-7)  # ssot-allow: pinned derivation


def test_the_two_periods_straddle_the_mean(derived) -> None:
    """Seasonality check: the fiscal year-end and the half-year sit either side.

    Denali's first half runs through the northern winter, so the two balance
    sheets are struck at opposite points of the cycle. If both ever landed the
    same side of the mean, the averaging argument would need re-examining.
    """
    lo, hi = sorted(p.intensity for p in derived.periods)
    assert lo < derived.intensity < hi


def test_the_basis_is_declared(derived) -> None:
    """D-50: a rate carries entity, window, level and source."""
    basis = derived.basis
    for field in ("entity", "window", "level", "source"):
        assert basis[field], f"{field} is empty"
    assert basis["source"].endswith(".pdf")


def test_every_period_in_the_window_is_the_right_entity(derived) -> None:
    assert len(derived.periods) == 2
    for p in derived.periods:
        assert p.working_capital > 0
        assert p.revenue > 0


def test_an_unset_window_refuses_rather_than_defaulting(tmp_path: Path) -> None:
    import yaml

    doc = yaml.safe_load(SERIES.read_text(encoding="utf-8"))
    doc["strike_window"] = {"status": "NOT_YET_SET", "blocked_on": "a reason"}
    p = tmp_path / "unset.yaml"
    p.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(TradeWorkingCapitalError, match="not set"):
        trade_working_capital_intensity(p)


def test_a_pre_demerger_period_is_refused(tmp_path: Path) -> None:
    """The guard that matters: the long history is the wrong company."""
    import yaml

    doc = yaml.safe_load(SERIES.read_text(encoding="utf-8"))
    doc["strike_window"]["periods"].append(
        {
            "period": "2024-09-30",
            "numerator": "trade_working_capital_published",
            "denominator_period": "FY2024",
        }
    )
    p = tmp_path / "widened.yaml"
    p.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(TradeWorkingCapitalError, match="pre-demerger"):
        trade_working_capital_intensity(p)
