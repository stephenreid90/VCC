"""Unit tests for the Derivation trace primitive (src/vcc_valuations/derivation.py)."""

from __future__ import annotations

import pytest

from vcc_valuations.derivation import Derivation, DerivationBuilder, DerivationStep


def _sample() -> Derivation:
    b = DerivationBuilder("sample")
    x = b.step("s1", "x", 2.0, "1 + 1", {"a": 1.0, "b": 1.0}, cell="B1")
    b.step("s2", "x squared", x * x, "x * x", {"x": x}, cell="B2", units="u")
    return b.build(result_key="s2")


def test_builder_records_steps_in_order_and_returns_values():
    b = DerivationBuilder("d")
    v = b.step("k", "label", 3.0, "1 + 2", {"a": 1.0, "b": 2.0})
    assert v == 3.0
    d = b.build(result_key="k")
    assert len(d) == 1
    assert d.result == 3.0


def test_lookup_iteration_and_result():
    d = _sample()
    assert [s.cell for s in d] == ["B1", "B2"]
    assert d["s2"].value == 4.0
    assert d.result == 4.0
    assert d.get("missing") is None


def test_as_rows_is_render_ready():
    rows = _sample().as_rows()
    assert rows[1] == {
        "key": "s2", "cell": "B2", "label": "x squared",
        "value": 4.0, "formula": "x * x", "units": "u",
    }


def test_result_key_must_exist():
    with pytest.raises(ValueError, match="result_key"):
        Derivation(name="d", steps=(DerivationStep("a", "a", 1.0, "1"),), result_key="z")
