"""``FcfEngineInputs.__post_init__`` rejects what it is supposed to reject.

Batch 6, item 18: the validation branches were untested, which is the usual way a
guard rots — it keeps compiling, nobody exercises it, and one refactor later it
guards nothing. These are cheap and they pin the contract.

The terminal-reinvestment rules matter most. ``terminal_reinvestment`` has no
default precisely so that no company can inherit ``capitalise_last_fcff`` by
accident, and the paired fields are rejected in the mode that ignores them —
passing ``working_capital_intensity`` alongside ``capitalise_last_fcff`` would
otherwise be silently discarded, which is worse than an error.
"""

from __future__ import annotations

import dataclasses

import pytest

from tests.dcf.golden.dnl_mt_inputs import dnl_muddle_through_inputs


def _inputs(**overrides):
    return dataclasses.replace(dnl_muddle_through_inputs(), **overrides)


def test_vector_lengths_must_match_the_horizon() -> None:
    for field in ("margin_transformation", "margin_gas_rolloff", "tax_rate_glide", "capex_pct"):
        base = dnl_muddle_through_inputs()
        short = list(getattr(base, field))[:-1]
        with pytest.raises(ValueError, match=f"{field} must have length"):
            _inputs(**{field: short})


def test_delta_wc_defaults_to_zeros_only_when_omitted() -> None:
    zeroed = _inputs(delta_wc=[])
    assert zeroed.delta_wc == [0.0] * zeroed.horizon_years
    with pytest.raises(ValueError, match="delta_wc must have length"):
        _inputs(delta_wc=[1.0, 2.0])


def test_terminal_reinvestment_mode_must_be_recognised() -> None:
    with pytest.raises(ValueError, match="terminal_reinvestment must be one of"):
        _inputs(terminal_reinvestment="normalized")     # US spelling, a plausible slip
    with pytest.raises(ValueError, match="terminal_reinvestment must be one of"):
        _inputs(terminal_reinvestment="")


def test_normalised_mode_requires_both_terminal_fields() -> None:
    for partial in (
        {"working_capital_intensity": 0.1376},
        {"terminal_capex_pct_revenue": 0.073},
        {},
    ):
        with pytest.raises(ValueError, match="requires both"):
            _inputs(terminal_reinvestment="normalised", **partial)


def test_legacy_mode_rejects_fields_it_would_ignore() -> None:
    """Passing them with capitalise_last_fcff must fail, not quietly do nothing."""
    with pytest.raises(ValueError, match="only read when"):
        _inputs(terminal_reinvestment="capitalise_last_fcff", working_capital_intensity=0.1376)
    with pytest.raises(ValueError, match="only read when"):
        _inputs(terminal_reinvestment="capitalise_last_fcff", terminal_capex_pct_revenue=0.073)


def test_a_valid_normalised_input_constructs() -> None:
    ok = _inputs(
        terminal_reinvestment="normalised",
        working_capital_intensity=0.1376,
        terminal_capex_pct_revenue=0.073,
    )
    assert ok.terminal_reinvestment == "normalised"
    assert ok.delta_wc == [0.0] * ok.horizon_years   # omitted, so still defaulted


def test_terminal_growth_at_or_above_the_discount_rate_is_refused() -> None:
    """Gordon is undefined there, and a negative denominator would otherwise
    produce a large negative terminal value rather than an error."""
    from vcc_valuations.dcf.fcf_engine import FcfEngine

    inp = _inputs(terminal_growth=0.5)
    with pytest.raises(ValueError, match="Gordon terminal undefined"):
        FcfEngine().run(inp)
