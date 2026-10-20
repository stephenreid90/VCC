"""Pins for UI tracker item 35 (20 Oct 2026): the CSL market-gap panel.

The panel is built in build_cfgs.py from design/methodology/csl_market_gap_set.yaml
(written by scripts/size_csl_market_gap.py, pinned by tests/dcf/test_csl_market_gap_set.py).
These tests check that every number on the page comes from that set, that the panel
is wired to the CSL page only, and that it discloses the gap without reconciling it (D-92).
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "ui_prototypes" / "_generator"
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(ROOT / "src"))

GEN_UI = (GEN / "gen_ui.py").read_text(encoding="utf-8")
BUILD = (GEN / "build_cfgs.py").read_text(encoding="utf-8")
SET = yaml.safe_load((ROOT / "design" / "methodology" / "csl_market_gap_set.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def bc():
    with contextlib.redirect_stdout(io.StringIO()):
        import build_cfgs
    return build_cfgs


def _html(key):
    return (ROOT / "ui_prototypes" / ("%s_scenario_interface.html" % key)).read_text(encoding="utf-8")


def test_panel_reads_the_set_not_typed_values():
    assert "csl_market_gap_set.yaml" in BUILD
    assert "_GAP = _data(\"design/methodology/csl_market_gap_set.yaml\")" in BUILD
    assert "csl[\"_gap\"]" in BUILD and "csl[\"titles\"][\"gap\"]" in BUILD


def test_gen_ui_passes_the_panel_through_to_csl_only():
    assert "if '_gap' in cfg: cfg['detail']['gap']=cfg['_gap']" in GEN_UI
    assert "'_financials','_gap']" in GEN_UI


def test_every_scenario_value_on_the_panel_is_the_set_value(bc):
    gap = bc.csl["_gap"]
    for s in SET["scenarios"]:
        assert "%.2f" % s["aud_per_share_model"] in gap, s["scenario"]
        assert "%+.0f%%" % (s["gap_to_market"] * 100.0) in gap, s["scenario"]
        for k in ("fade_15", "fade_20", "fade_25"):
            assert "%.2f" % s["fade_band_aud_per_share"][k] in gap, (s["scenario"], k)
        assert "%.2f%%" % (s["terminal_growth"] * 100.0) in gap, s["scenario"]
        assert "%.2f%%" % (s["earned_starting_return"] * 100.0) in gap, s["scenario"]


def test_discount_rate_and_price_on_the_panel_come_from_the_set(bc):
    gap = bc.csl["_gap"]
    d = SET["discount_rate"]
    assert "WACC %.2f%%" % (d["wacc"] * 100.0) in gap
    assert "Cost of equity %.2f%%" % (d["cost_of_equity"] * 100.0) in gap
    assert "debt weight %.2f%%" % (d["debt_weight"] * 100.0) in gap
    price = SET["scenarios"][0]["market_price_aud"]
    assert "AUD %.2f per share, struck on %s" % (price, SET["scenarios"][0]["market_price_date"]) in gap


def test_closest_scenario_and_band_claim_follow_the_set(bc):
    gap = bc.csl["_gap"]
    closest = next(s for s in SET["scenarios"] if s["scenario"] == SET["closest_to_market"])
    assert "The closest is Stagflation persists at AUD %.2f, %.0f%% above it" % (
        closest["aud_per_share_model"], closest["gap_to_market"] * 100.0) in gap
    low = min(s["fade_band_aud_per_share"]["fade_15"] for s in SET["scenarios"])
    price = SET["scenarios"][0]["market_price_aud"]
    assert low > price
    assert "The band does not close the gap." in gap


def test_panel_discloses_the_gap_and_does_not_reconcile_it(bc):
    gap = bc.csl["_gap"]
    assert "does not reconcile the gap" in gap
    assert "propose a haircut" in gap and "refresh the price (D-92)" in gap
    assert "No reconciliation to the market is made." in gap
    assert "D-06 stays provisional" in gap


def test_csl_page_carries_the_panel_and_dnl_wbc_do_not(bc):
    h = _html("csl")
    assert json.dumps(bc.csl["_gap"])[1:-1] in h
    assert "Market gap to price" in h
    for key in ("dnl", "wbc"):
        assert "Market gap to price" not in _html(key), key
        assert "_gap" not in getattr(bc, key), key
