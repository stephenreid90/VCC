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
    # Pinned 16 Oct 2026 (D-87): net debt rolled to 30 Jun 2026 (D-87, decision Q1).
    pinned = {"orderly_convergence": 270.21, "muddle_through": 230.25,
              "ai_productivity_lag": 220.84, "fragmentation": 175.93,
              "disorderly_climate_crystallisation": 185.84, "stagflation_persists": 152.66}
    for s in _committed()["scenarios"]:
        assert s["aud_per_share_model"] == pinned[s["scenario"]], s["scenario"]


def test_each_scenario_carries_the_sensitivity_band():
    for s in _committed()["scenarios"]:
        # 2 fades x 4 starts, minus the model row itself (earned start at 25 years).
        assert len(s["sensitivity"]) == 7, s["scenario"]
