"""Pins for the CSL cross-scenario thesis (analyses/csl/thesis.md, v3 of 20 Oct 2026).

Standing rule 4: every number in a document comes from committed code. The thesis cites
design/methodology/csl_thesis_set.yaml, written by scripts/size_csl_thesis.py from the
segment engine. These tests assert (1) the committed set equals a fresh run, (2) the set
agrees with the market-gap set (D-92) and the terminal-return set (D-86) it repeats, and
(3) the thesis text carries the set's figures, so a change in the engine that moves a
number fails here until the thesis is restated.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import size_csl_thesis as szt  # noqa: E402

SET = yaml.safe_load(szt.SET_PATH.read_text(encoding="utf-8"))
THESIS = (ROOT / "analyses" / "csl" / "thesis.md").read_text(encoding="utf-8")
NAMES = {
    "orderly_convergence": "Orderly Convergence", "muddle_through": "Muddle Through",
    "ai_productivity_lag": "AI Productivity Lag", "fragmentation": "Fragmentation",
    "disorderly_climate_crystallisation": "Disorderly Climate", "stagflation_persists": "Stagflation Persists",
}


@pytest.fixture(scope="module")
def fresh():
    return szt.build()


def test_committed_set_equals_a_fresh_run(fresh):
    assert fresh == SET


def test_set_repeats_the_gap_and_return_sets():
    gap = yaml.safe_load(szt.GAP_SET.read_text(encoding="utf-8"))
    ret = yaml.safe_load(szt.RETURN_SET.read_text(encoding="utf-8"))
    gap_by = {s["scenario"]: s for s in gap["scenarios"]}
    ret_by = {s["scenario"]: s for s in ret["scenarios"]}
    for s in SET["scenarios"]:
        g = gap_by[s["scenario"]]; r = ret_by[s["scenario"]]
        assert s["aud_per_share"] == g["aud_per_share_model"] == r["aud_per_share_model"]
        assert s["gap_to_market"] == g["gap_to_market"]
        assert s["fade_band_aud_per_share"] == g["fade_band_aud_per_share"]
        assert abs(s["earned_starting_return"] - r["starting_return_ex_goodwill"]) < 1e-4
        assert s["aud_per_share_incl_goodwill"] == r["aud_per_share_incl_goodwill"]
    assert SET["discount_rate"] == gap["discount_rate"]
    assert SET["distribution"]["closest_to_market"] == gap["closest_to_market"]


def test_thesis_table_carries_every_scenario_value():
    for s in SET["scenarios"]:
        row = "| %s%s | %.2f | %.2f | %+.0f%% |" % (
            "**" if s["scenario"] == "muddle_through" else "", NAMES[s["scenario"]] + (" (central)**" if s["scenario"] == "muddle_through" else ""),
            s["usd_per_share"], s["aud_per_share"], s["gap_to_market"] * 100.0)
        if s["scenario"] == "muddle_through":
            row = "| **Muddle Through (central)** | **%.2f** | **%.2f** | **%+.0f%%** |" % (
                s["usd_per_share"], s["aud_per_share"], s["gap_to_market"] * 100.0)
        assert row in THESIS, row
        if s["scenario"] != "muddle_through":
            vs = "%+.1f%%" % (s["vs_central"] * 100.0)
            assert vs.replace("-", "−") in THESIS, vs
        assert "%.0f%%" % (s["terminal_share_of_ev"] * 100.0) in THESIS
        band = "| %s | %.2f | %.2f | %.2f |" % (NAMES[s["scenario"]], *[s["fade_band_aud_per_share"][k] for k in ("fade_15", "fade_20", "fade_25")])
        assert band in THESIS, band
        head = "(USD %.2f / AUD %.2f" % (s["usd_per_share"], s["aud_per_share"])
        assert head in THESIS, head


def test_thesis_narratives_carry_the_scenario_inputs():
    by = {s["scenario"]: s for s in SET["scenarios"]}
    mt = by["muddle_through"]
    assert "%.1f per cent at the end of the forecast" % (mt["earned_starting_return"] * 100.0) in THESIS
    assert "%.1f to %.1f per cent at FY36" % (mt["ebit_margin_first"] * 100.0, mt["ebit_margin_last"] * 100.0) in THESIS
    assert "+%dbps" % mt["margin_uplift_bps"]["csl_behring"] in THESIS
    assert "%.2f per cent in the central case" % (mt["terminal_growth"] * 100.0) in THESIS
    for sid, phrase in [
        ("orderly_convergence", "the earned return at year ten is %.1f per cent"),
        ("ai_productivity_lag", "the earned return is %.1f per cent"),
        ("disorderly_climate_crystallisation", "earned return %.1f per cent"),
        ("fragmentation", "earned return %.1f per cent"),
        ("stagflation_persists", "The earned return at year ten is %.1f per cent"),
    ]:
        assert phrase % (by[sid]["earned_starting_return"] * 100.0) in THESIS, sid
    assert "Terminal margin falls to %.1f per cent" % (by["stagflation_persists"]["terminal_ebit_margin"] * 100.0) in THESIS
    assert "terminal growth to %.2f per cent" % (by["stagflation_persists"]["terminal_growth"] * 100.0) in THESIS
    assert "terminal growth drops to %.2f per cent" % (by["ai_productivity_lag"]["terminal_growth"] * 100.0) in THESIS
    assert "Behring starts FY26 at %s per cent" % ("%.1f" % (by["fragmentation"]["behring_growth_first"] * 100.0)).replace("-", "−") in THESIS


def test_thesis_anchors_and_distribution_come_from_the_set():
    v = SET["valuation"]; d = SET["discount_rate"]; m = SET["market"]; x = SET["distribution"]
    mt = next(s for s in SET["scenarios"] if s["scenario"] == "muddle_through")
    assert "WACC %.2f%%" % (d["wacc"] * 100.0) in THESIS
    assert "Re %.2f%% (%.2f%% + %.2f × %.2f%%)" % (d["cost_of_equity"] * 100.0, d["risk_free_rate"] * 100.0, d["beta"], d["equity_risk_premium"] * 100.0) in THESIS
    assert "after-tax kd %.2f%% at %.1f%%" % (d["cost_of_debt_after_tax"] * 100.0, d["debt_weight"] * 100.0) in THESIS
    assert "net debt %.1f× EBITDA over EV %.0f× EBITDA" % (d["net_debt_ebitda"], d["target_ev_ebitda"]) in THESIS
    assert "USD {:,}m excluding goodwill".format(mt["invested_capital_ex_goodwill_usdm"]) in THESIS
    assert "USD {:,}m | D-87".format(mt["net_debt_usdm"]) in THESIS
    assert "USD %dm | FY26" % v["restructuring_cash_usdm"] in THESIS
    assert "%.2fm | 1H26" % v["shares_m"] in THESIS
    assert "AUD %.2f on %s" % (m["price_aud"], "15 June 2026") in THESIS and m["price_date"] == "2026-06-15"
    assert "52-week high of AUD %.2f" % m["fifty_two_week_high_aud"] in THESIS
    assert "USD %.2f (AUD %.2f)" % (m["broker_target_usd"], m["broker_target_aud"]) in THESIS
    assert "%.0f%% of the change in revenue" % (v["wc_change_pct_revenue_change"] * 100.0) in THESIS
    assert "%.1f%% / %.1f%% of revenue" % (v["capex_pct_revenue"] * 100.0, v["da_pct_revenue"] * 100.0) in THESIS
    assert "AUD %.2f; downside" % x["upside_aud"] in THESIS and "AUD %.2f; the ratio is **%.2f×**" % (x["downside_aud"], x["asymmetry_down_over_up"]) in THESIS
    assert "The lowest value in the band, AUD %.2f," % x["lowest_in_fade_band_aud"] in THESIS
    assert "Muddle Through is AUD %.2f" % mt["aud_per_share_incl_goodwill"] in THESIS
    assert "%.1f per cent and Muddle Through" % (mt["starting_return_incl_goodwill"] * 100.0) in THESIS
    assert v["terminal_form"] == "excess_return_convergence" and v["explicit_years"] == 10
    assert "%d-year fade" % x["decay_band_years"]["midpoint"] in THESIS
    assert "%d–%d years" % (x["decay_band_years"]["low"], x["decay_band_years"]["high"]) in THESIS


def test_thesis_states_the_gap_is_disclosed_not_reconciled():
    assert "disclosed, not reconciled" in THESIS and "D-92" in THESIS
    assert "8.75 per cent cost of equity" in THESIS            # named only as the superseded v2 basis
    assert "reverse-DCF figures are withdrawn" in THESIS
