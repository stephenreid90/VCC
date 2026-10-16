"""The CSL reporting set (D-86) is regenerated, not hand-edited.

``design/methodology/csl_terminal_return_sets.yaml`` is written by
``scripts/size_csl_terminal_return.py``. These tests regenerate it in memory and
compare it with the committed file, and pin the facts a report relies on.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import size_csl_terminal_return as sizer  # noqa: E402

SET = ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml"


def _committed() -> dict:
    return yaml.safe_load(SET.read_text(encoding="utf-8"))


def test_committed_set_matches_a_fresh_run():
    assert _committed() == sizer.build()


def test_goodwill_comes_from_the_financials_file():
    assert _committed()["goodwill_aud_m"] == 8065.0


def test_goodwill_lowers_the_return_in_every_scenario():
    for s in _committed()["scenarios"]:
        assert s["starting_return_incl_goodwill"] < s["starting_return_ex_goodwill"], s["scenario"]


def test_goodwill_barely_moves_value():
    # The convergence terminal adds the base and lowers the return, so the two
    # largely cancel. A move beyond 3% would mean the reading has changed.
    for s in _committed()["scenarios"]:
        move = s["aud_per_share_incl_goodwill"] / s["aud_per_share_model"] - 1
        assert abs(move) < 0.03, s["scenario"]


def test_model_values_are_the_pinned_base_values():
    # Pinned 16 Oct 2026 (D-87, refined): net debt on the agreed convention, 482.13m shares at 31 Dec 2025.
    # Re-pinned 16 Oct 2026 (D-93): 20-year fade. Before: 266.33, 226.66, 217.32, 172.73, 182.56, 149.62.
    pinned = {"orderly_convergence": 246.47, "muddle_through": 211.15,
              "ai_productivity_lag": 203.32, "fragmentation": 164.23,
              "disorderly_climate_crystallisation": 173.43, "stagflation_persists": 143.71}
    for s in _committed()["scenarios"]:
        assert s["aud_per_share_model"] == pinned[s["scenario"]], s["scenario"]


def test_each_scenario_carries_the_sensitivity_band():
    for s in _committed()["scenarios"]:
        # 4 fades x 4 starts, minus the model row itself (earned start at 20 years, D-93).
        assert len(s["sensitivity"]) == 15, s["scenario"]


def test_csl_goodwill_return_agrees_with_the_general_terminal_return_set():
    # D-86a: one general function feeds both sets; they must not drift apart.
    general = yaml.safe_load(
        (ROOT / "design" / "methodology" / "terminal_return_sets.yaml").read_text(encoding="utf-8"))
    by = {r["scenario"]: r for r in general["terminal_return_sets"]["current"]["rows"]
          if r["company"] == "csl"}
    for s in _committed()["scenarios"]:
        g = by[s["scenario"]]
        assert round(g["earned_return_ex_goodwill"], 4) == s["starting_return_ex_goodwill"]
        assert round(g["earned_return_incl_goodwill"], 4) == s["starting_return_incl_goodwill"]


def test_the_sensitivity_paper_is_the_committed_set():
    # D-86b: every number in design/methodology/csl_terminal_return_sensitivity_2026-10-16.md
    # comes from this set. The paper's table is parsed and compared cell by cell.
    paper = (ROOT / "design" / "methodology"
             / "csl_terminal_return_sensitivity_2026-10-16.md").read_text(encoding="utf-8")
    names = {"Orderly convergence": "orderly_convergence", "Muddle through": "muddle_through",
             "AI productivity lag": "ai_productivity_lag", "Fragmentation": "fragmentation",
             "Disorderly climate": "disorderly_climate_crystallisation",
             "Stagflation persists": "stagflation_persists"}
    sets = {s["scenario"]: s for s in _committed()["scenarios"]}
    checked = 0
    for line in paper.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0] not in names:
            continue
        s = sets[names[cells[0]]]
        fade = float(cells[2].split()[0])
        vals = [float(c) for c in cells[3:7]]
        by = {(b["fade_years"], b["starting_return"]): b["aud_per_share"] for b in s["sensitivity"]}
        by[(s["fade_years"], "earned")] = s["aud_per_share_model"]
        assert vals == [by[(fade, k)] for k in ("earned", 0.2, 0.15, 0.12)], line
        checked += 1
    assert checked == 24  # 6 scenarios x 4 fades (D-93)
