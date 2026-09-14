"""Every published horizon/terminal table is generated, and pinned, from its assumptions.

The 25 August paper published two tables about two per cent apart and could not say
which assumption differed, because the harness that produced the first had been
thrown away. The reconciliation is now structural rather than remembered: each table
is one entry in ``design/methodology/horizon_variant_sets.yaml`` carrying its
complete assumption block and the levels it produced, and this module regenerates
and asserts them.

A table in a document may therefore cite a set name. If an assumption in that set
moves, this test fails and the document is known to be stale -- which is the whole
point of committing the harness.
"""

from __future__ import annotations

import pytest

from scripts.size_horizon_variants import (
    load_sets,
    run_capex_intensity_rule,
    run_item_11,
    run_set,
    _current_set_name,
)

CFG = load_sets()
SET_NAMES = list(CFG["sets"])
POSITION_NAMES = [
    name for name, spec in CFG["item_11_positions"].items() if "expected" in spec
]

# Levels are published to four decimal places, so a level is reproduced when it
# rounds to the published figure. Tighter would pin floating-point noise; looser
# would let a real change through.
TOLERANCE = 5e-5


@pytest.mark.parametrize("set_name", SET_NAMES)
def test_set_reproduces_its_published_levels(set_name: str) -> None:
    spec = CFG["sets"][set_name]
    results = run_set(CFG, set_name)
    for scenario_id, expected in spec["expected"].items():
        got = results[scenario_id].value_per_share
        assert got == pytest.approx(expected, abs=TOLERANCE), (
            f"{set_name}/{scenario_id}: {got:.6f} against published {expected}"
        )


def test_exactly_one_set_is_current() -> None:
    assert _current_set_name(CFG) in CFG["sets"]


@pytest.mark.parametrize("set_name", SET_NAMES)
def test_a_superseded_set_names_what_superseded_it(set_name: str) -> None:
    spec = CFG["sets"][set_name]
    if spec["status"] == "superseded":
        assert spec["superseded_by"] in CFG["sets"]


def test_item_11_positions_reproduce() -> None:
    rows = run_item_11(CFG)
    for name in POSITION_NAMES:
        expected = CFG["item_11_positions"][name]["expected"]
        for scenario_id, level in expected.items():
            got = rows[name][scenario_id]
            assert got == pytest.approx(level, abs=TOLERANCE), (
                f"item 11/{name}/{scenario_id}: {got:.6f} against {level}"
            )


def test_the_ruled_build_is_the_outlier_among_the_item_11_positions() -> None:
    """The finding item 11 turns on, asserted rather than narrated.

    Both positions that make capital follow the business land well below the ruled
    build, in which capex converges to D&A and fixed capital is flat in nominal
    terms. The claim is asserted on the central case, where the decision is argued,
    and directionally everywhere the arc does not dominate the capex path.

    Disorderly Climate is the stated exception: its capex arc, not the convergence
    rule, sets its path, so the three positions collapse together there. That is a
    reason to argue item 11 on the other five, not a counter-example to it.
    """
    rows = run_item_11(CFG)
    central = "muddle_through"
    ruled = rows["ruled_build"][central]
    others = [rows[n][central] for n in POSITION_NAMES if n != "ruled_build"]
    assert ruled > max(others) * 1.3

    arc_scenario = "disorderly_climate_crystallisation"
    for scenario_id in CFG["scenarios"]:
        if scenario_id == arc_scenario:
            continue
        alternatives = [rows[n][scenario_id] for n in POSITION_NAMES if n != "ruled_build"]
        assert rows["ruled_build"][scenario_id] > max(alternatives), scenario_id


def test_capex_intensity_rule_variants_reproduce() -> None:
    """The observed-intensity rule, pinned at each entity and window it was sized on."""
    got = run_capex_intensity_rule(CFG)
    for name, spec in CFG["capex_intensity_rule"]["variants"].items():
        assert got[name] == pytest.approx(spec["expected"], abs=TOLERANCE), (
            f"capex intensity rule/{name}: {got[name]:.6f} against {spec['expected']}"
        )


def test_the_terminal_treatment_is_worth_more_than_the_window_choice() -> None:
    """Why the terminal half of the rule cannot be waved through.

    Striking terminal capex at depreciation rather than at the rate that grows
    the capital base hands the perpetuity the difference between the two, every
    year, forever. On the explosives window that is worth more than moving the
    whole explicit path from one entity's average to another's -- so it is the
    part of the rule that needs the argument, not the part that looks like an
    assumption change.
    """
    got = run_capex_intensity_rule(CFG)
    terminal_effect = got["explosives_two_year_equals_da"] - got["explosives_two_year_grow"]
    window_effect = got["group_five_year_grow"] - got["explosives_two_year_grow"]
    assert terminal_effect > 0
    assert window_effect > 0
    assert terminal_effect > window_effect * 0.8
