"""D-42's obligation, as a ratchet: an excess return is declared or it is baselined.

The diagnostic in ``test_terminal_return_sets.py`` measures which valuations assert a
terminal return above their cost of capital. This is the half that obliges something
about it: each such valuation must carry a structured ``excess_return_defence`` in its
archetype impact matrix, or be named in ``tests/terminal_defence_baseline.json`` with a
reason. The baseline may only shrink, so the rule tightens as defences are written and
can never quietly loosen — the same shape as ``moat_role_baseline.json`` under D-43a and
ssot check 13 under D-50.

When this was first run, on 16 September 2026, fifteen of eighteen valuations asserted an
excess return and exactly one carried a defence — in prose, in a rationale field. That one
is now declared structurally and is the worked example; the other fourteen are baselined
for three different reasons, which are written out in the baseline file rather than left
as a bare list.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from size_terminal_returns import collect  # noqa: E402

from vcc_valuations.schemas.linkage import ImpactMatrix  # noqa: E402

BASELINE = ROOT / "tests" / "terminal_defence_baseline.json"

ARCHETYPE_OF = {
    "dnl": "industrial_explosives",
    "wbc": "australian_major_banks",
    "csl": "biopharmaceuticals",
}


def _baseline() -> set:
    return set(json.loads(BASELINE.read_text(encoding="utf-8"))["undeclared"])


def _declared_defences() -> dict:
    """(company, scenario) -> ExcessReturnDefence, for every matrix that has one."""
    out = {}
    for company, archetype in ARCHETYPE_OF.items():
        path = ROOT / "data" / "impact_matrix" / "by_industry" / f"{archetype}.yaml"
        if not path.exists():
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        matrix = ImpactMatrix.model_validate(raw.get("impact_matrix", raw))
        for entry in matrix.matrix:
            for movement in entry.drivers.values():
                if movement.excess_return_defence is not None:
                    out[(company, entry.scenario)] = movement.excess_return_defence
    return out


@pytest.fixture(scope="module")
def asserting_excess():
    """The valuations that claim a terminal return above their cost of capital.

    Judged on the GOVERNING reading — the return on the whole capital base where
    D-49's roll-forward provides one, the return on new capital otherwise. That
    choice changes the answer: DNL Fragmentation is below its WACC on new capital
    and above it on the whole base, so it owes a defence under the better reading
    and did not under the weaker one.
    """
    return [r for r in collect()
            if r.excess_on_governing_return is not None
            and r.excess_on_governing_return > 0]


def test_every_excess_return_is_declared_or_baselined(asserting_excess):
    declared = _declared_defences()
    baseline = _baseline()

    undeclared = {
        f"{r.company_id}:{r.scenario_id}"
        for r in asserting_excess
        if (r.company_id, r.scenario_id) not in declared
    }

    new = sorted(undeclared - baseline)
    assert not new, (
        "A valuation asserts a terminal return above its cost of capital with no "
        "declared defence (D-42):\n  " + "\n  ".join(new)
        + "\nAdd an excess_return_defence to the archetype impact matrix naming the "
          "moat source, the decay horizon, the threat and a sensitivity — or add the "
          "pair to terminal_defence_baseline.json with a reason."
    )

    stale = sorted(baseline - undeclared)
    assert not stale, (
        "These pairs are baselined but no longer need to be — either they now declare "
        "a defence or they no longer assert an excess return. Regenerate the baseline "
        "so it only ever tightens:\n  " + "\n  ".join(stale)
    )


def test_the_baseline_only_covers_valuations_that_actually_assert_excess(asserting_excess):
    """A baseline entry for something that does not assert an excess return is noise."""
    keys = {f"{r.company_id}:{r.scenario_id}" for r in asserting_excess}
    assert _baseline() <= keys, sorted(_baseline() - keys)


def test_the_one_declared_defence_is_complete_and_dated():
    """DNL Orderly Convergence: the worked example, and the only one today."""
    declared = _declared_defences()
    assert ("dnl", "orderly_convergence") in declared, sorted(declared)
    d = declared[("dnl", "orderly_convergence")]

    assert d.moat_sources
    assert d.named_threat.strip()
    assert d.sensitivity.strip()
    assert d.decay_horizon.basis.strip()
    assert d.decay_horizon.years_low == 10
    assert d.decay_horizon.years_high == 15
    assert not d.decay_horizon.indefinite


def test_a_defence_may_only_rest_on_barrier_bearing_moat_sources():
    """The D-43a tie the schema cannot make, because the two live in different files.

    A rent is a cash advantage with an end date and is carried in the explicit
    period; a barrier is what stops a rival taking the business and is what the
    decay horizon measures. Defending a terminal excess return on a rent-bearing
    source is precisely the confusion D-43a was written to stop — Denali's gas
    contracts expire six years out and cannot hold up a ten-to-fifteen year
    horizon.
    """
    roles = {}
    for company in ARCHETYPE_OF:
        path = ROOT / "data" / "companies" / f"{company}.yaml"
        if not path.exists():
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "moat" and isinstance(v, dict) and v.get("source_roles"):
                        yield v["source_roles"]
                    else:
                        yield from walk(v)
            elif isinstance(node, list):
                for v in node:
                    yield from walk(v)

        merged = {}
        for block in walk(doc):
            merged.update(block)
        if merged:
            roles[company] = merged

    for (company, scenario), defence in _declared_defences().items():
        company_roles = roles.get(company)
        if not company_roles:
            continue
        for source in defence.moat_sources:
            assert source in company_roles, (
                f"{company}:{scenario} defends on moat source {source!r}, which the "
                f"company file does not declare at all. Known: {sorted(company_roles)}"
            )
            assert company_roles[source] in ("barrier", "both"), (
                f"{company}:{scenario} defends a TERMINAL excess return on "
                f"{source!r}, which is declared {company_roles[source]!r}. A rent "
                f"has an end date and belongs in the explicit period; only a barrier "
                f"can hold up a decay horizon (D-43a)."
            )
