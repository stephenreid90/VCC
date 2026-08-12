"""Auditable derivation traces — the code-side equivalent of a workbook's
labelled derived rows.

Standing rule 1 / methodology §11: inputs are the yellow cells (they live in the
data files); everything else is a *formula*. In a spreadsheet the formula sits in
a labelled cell you can read and flex by hand. Our formulas are code, so without
help the intermediate steps are invisible — computed and thrown away. A
``Derivation`` makes them first-class again: every derived quantity is a named
:class:`DerivationStep` carrying its value, the formula that produced it, the
inputs it consumed and its provenance (the originating workbook cell), so the
whole build can be read out of the engine's own output — at least as granular as
the workbook it replaces, without the workbook sourcing anything.

This is deliberately generic (no revenue-chain specifics) so the same primitive
carries the Tax Bridge, the WACC build, the margin/gas glide and the equity
bridge as those are brought to full traceability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, Mapping, Tuple


@dataclass(frozen=True)
class DerivationStep:
    """One derived line: a labelled value, the formula, and where it came from.

    ``inputs`` maps human-readable operand names to the values actually used, so
    the step is self-describing (``formula`` reads against those names). ``cell``
    is the originating workbook cell (e.g. ``"B30"``) — provenance only, never a
    source: the value is computed here, the cell reference just says which row of
    the audited workbook this line corresponds to.
    """

    key: str
    label: str
    value: float
    formula: str
    inputs: Mapping[str, float] = field(default_factory=dict)
    cell: str = ""
    units: str = ""


@dataclass(frozen=True)
class Derivation:
    """An ordered, self-describing sequence of :class:`DerivationStep` s.

    ``result_key`` names the step that is the derivation's headline output, so
    ``.result`` returns it without the caller knowing the ordering. Steps are
    addressable by key (``derivation["B30"]`` or by ``key``) for pinning in tests
    and, later, for rendering a human-readable workings view.
    """

    name: str
    steps: Tuple[DerivationStep, ...]
    result_key: str

    def __post_init__(self) -> None:
        if self.result_key not in self._by_key():
            raise ValueError(
                f"result_key {self.result_key!r} is not among the steps "
                f"({', '.join(s.key for s in self.steps)})"
            )

    def _by_key(self) -> Dict[str, DerivationStep]:
        return {s.key: s for s in self.steps}

    def __getitem__(self, key: str) -> DerivationStep:
        return self._by_key()[key]

    def __iter__(self) -> Iterator[DerivationStep]:
        return iter(self.steps)

    def __len__(self) -> int:
        return len(self.steps)

    def get(self, key: str) -> DerivationStep | None:
        return self._by_key().get(key)

    @property
    def result(self) -> float:
        return self[self.result_key].value

    def as_rows(self) -> Tuple[dict, ...]:
        """Flat, render-ready rows (label / value / formula / cell / units)."""
        return tuple(
            {
                "key": s.key,
                "cell": s.cell,
                "label": s.label,
                "value": s.value,
                "formula": s.formula,
                "units": s.units,
            }
            for s in self.steps
        )


class DerivationBuilder:
    """Small helper to accumulate steps in order, then freeze into a Derivation."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: list[DerivationStep] = []

    def step(
        self,
        key: str,
        label: str,
        value: float,
        formula: str,
        inputs: Mapping[str, float] | None = None,
        cell: str = "",
        units: str = "",
    ) -> float:
        """Record a derived line and return its value (so callers can chain)."""
        self._steps.append(
            DerivationStep(
                key=key,
                label=label,
                value=value,
                formula=formula,
                inputs=dict(inputs or {}),
                cell=cell,
                units=units,
            )
        )
        return value

    def build(self, result_key: str) -> Derivation:
        return Derivation(name=self.name, steps=tuple(self._steps), result_key=result_key)
