"""The transcribed trade-working-capital series must reconcile to itself.

`analyses/dnl_trade_working_capital_history.yaml` holds figures read off a PDF by
hand. A transcription error there would propagate silently into an intensity and
from there into every Denali level, so the series carries its own arithmetic
check: the company publishes both the components and the total, and the two must
agree in every period.

This does not make the figures right — only faithfully copied. It is the cheapest
guard that would catch a transposed digit, which is the error this kind of
extraction actually makes.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "analyses" / "dnl_trade_working_capital_history.yaml"

VALID_STATUS = {"pre", "transition", "post"}


@pytest.fixture(scope="module")
def series() -> dict:
    return yaml.safe_load(SERIES.read_text(encoding="utf-8"))


def test_series_is_present_and_sourced(series: dict) -> None:
    assert series["source"]["document"]
    assert series["source"]["units"] == "AUD m"
    assert series["definition"]["formula"]
    assert len(series["observations"]) >= 2


@pytest.mark.parametrize("idx", range(9))
def test_components_reconcile_to_published_total(series: dict, idx: int) -> None:
    o = series["observations"][idx]
    computed = o["inventories"] + o["trade_debtors"] - o["trade_creditors"]
    assert computed == pytest.approx(o["trade_working_capital_published"], abs=0.05), (
        f"{o['label']}: components give {computed}, "
        f"published total is {o['trade_working_capital_published']}"
    )


def test_every_period_declares_which_entity_it_belongs_to(series: dict) -> None:
    for o in series["observations"]:
        assert o["demerger_status"] in VALID_STATUS, o["label"]


def test_the_strike_window_declares_itself_either_way(series: dict) -> None:
    """D-50: a rate declares its basis. An unset window says what it waits on.

    A set window names entity, window, level and method, and every period it
    selects must belong to the entity being valued — the seven pre-demerger
    periods in the series are a different company and can never be drawn in.
    """
    w = series["strike_window"]
    assert w["status"] in {"NOT_YET_SET", "SET"}

    if w["status"] == "NOT_YET_SET":
        assert w["blocked_on"].strip(), "an unset window must say what it is waiting on"
        selected = [str(p) for p in w.get("eligible_periods", [])]
    else:
        for field in ("entity", "window", "level", "method"):
            assert str(w[field]).strip(), f"a set window must declare {field}"
        selected = [str(spec["period"]) for spec in w["periods"]]
        assert selected, "a set window must select at least one period"

    for p in selected:
        match = [o for o in series["observations"] if str(o["period"]) == p]
        assert match, f"period {p} is not in the series"
        assert match[0]["demerger_status"] == "post", (
            f"period {p} is not post-demerger — the entity would not match"
        )
