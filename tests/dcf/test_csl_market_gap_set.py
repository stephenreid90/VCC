"""CSL's gap to market (section 16.3, D-92) is regenerated, not hand-edited.

``design/methodology/csl_market_gap_set.yaml`` is written by
``scripts/size_csl_market_gap.py``. These tests regenerate it in memory, compare
it with the committed file, pin the facts the note relies on, and check the
note's tables cell by cell.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import size_csl_market_gap as sizer  # noqa: E402

SET = ROOT / "design" / "methodology" / "csl_market_gap_set.yaml"
NOTE = ROOT / "design" / "methodology" / "csl_market_gap_note_2026-10-16.md"
RETURN_SET = ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml"
NAMES = {"Orderly convergence": "orderly_convergence", "Muddle through": "muddle_through",
         "AI productivity lag": "ai_productivity_lag", "Fragmentation": "fragmentation",
         "Disorderly climate": "disorderly_climate_crystallisation",
         "Stagflation persists": "stagflation_persists"}


def _committed() -> dict:
    return yaml.safe_load(SET.read_text(encoding="utf-8"))


def _rows(n_cells: int) -> list[list[str]]:
    out = []
    for line in NOTE.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == n_cells and cells[0] in NAMES:
            out.append(cells)
    return out


def test_committed_set_matches_a_fresh_run():
    assert _committed() == sizer.build()


def test_model_values_are_the_current_base_values():
    # MT 211.15 (D-93); the rest are the terminal-return set's model values.
    ret = yaml.safe_load(RETURN_SET.read_text(encoding="utf-8"))
    base = {s["scenario"]: s["aud_per_share_model"] for s in ret["scenarios"]}
    assert base["muddle_through"] == 211.15
    for s in _committed()["scenarios"]:
        assert s["aud_per_share_model"] == base[s["scenario"]], s["scenario"]
        assert s["fade_band_aud_per_share"]["fade_20"] == s["aud_per_share_model"]


def test_the_price_is_the_15_june_2026_price_from_csl_yaml():
    csl = yaml.safe_load((ROOT / "data" / "companies" / "csl.yaml").read_text(encoding="utf-8"))
    stats = csl["company_position"]["share_statistics"]
    assert stats["market_reference_price_aud"] == 105.53
    assert str(stats["market_reference_date"]) == "2026-06-15"
    for s in _committed()["scenarios"]:
        assert s["market_price_aud"] == 105.53
        assert s["market_price_date"] == "2026-06-15"


def test_every_gap_is_positive_and_is_value_over_price_less_one():
    for s in _committed()["scenarios"]:
        assert s["gap_to_market"] > 0, s["scenario"]
        assert s["gap_to_market"] == round(s["aud_per_share_model"] / s["market_price_aud"] - 1, 4)


def test_closest_to_market_is_the_smallest_gap():
    doc = _committed()
    smallest = min(doc["scenarios"], key=lambda s: s["gap_to_market"])
    assert doc["closest_to_market"] == smallest["scenario"]


def test_the_band_is_ordered_by_fade_length():
    for s in _committed()["scenarios"]:
        b = s["fade_band_aud_per_share"]
        assert b["fade_15"] < b["fade_20"] < b["fade_25"], s["scenario"]


def test_the_note_gap_table_is_the_committed_set():
    sets = {s["scenario"]: s for s in _committed()["scenarios"]}
    checked = 0
    for cells in _rows(3):
        s = sets[NAMES[cells[0]]]
        assert cells[1] == f"{s['aud_per_share_model']:.2f}", cells
        assert cells[2] == f"{round(s['gap_to_market'] * 100):+d}%", cells
        checked += 1
    assert checked == 6


def test_the_note_band_table_is_the_committed_set():
    sets = {s["scenario"]: s for s in _committed()["scenarios"]}
    checked = 0
    for cells in _rows(4):
        b = sets[NAMES[cells[0]]]["fade_band_aud_per_share"]
        assert cells[1:] == [f"{b[k]:.2f}" for k in ("fade_15", "fade_20", "fade_25")], cells
        checked += 1
    assert checked == 6


def test_the_note_names_the_closest_scenario_and_the_rate():
    doc = _committed()
    note = NOTE.read_text(encoding="utf-8")
    closest = next(n for n, k in NAMES.items() if k == doc["closest_to_market"])
    assert f"The closest is {closest}" in note
    assert f"WACC of {doc['discount_rate']['wacc'] * 100:.2f}%" in note
    assert "105.53" in note and doc["scenarios"][0]["market_price_date"] in note
