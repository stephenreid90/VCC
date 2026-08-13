"""Regression goldens: every scenario level, all three companies, all three engines.

**These are ENGINE-OWNED numbers, not workbook-owned.** Only Muddle Through is
independently audited against a hand-built workbook in ``analyses/`` — that tie lives
in ``test_dnl_mt_ratified.py``, ``test_wbc_bank.py`` and ``test_csl_segment.py`` and is
the real oracle. The five non-MT levels per company were superseded by the engine when
the ratified beta landed (DNL 3.484 -> 3.073 and the equivalents for WBC/CSL), so the
comparison workbooks no longer arbitrate them.

Their purpose here is different and narrower: they are a **change detector**. Before
this module the non-MT scenarios were asserted only by ORDERING
(``test_wbc_bank.py``, ``test_csl_segment.py``) or by DRIVERS
(``test_dnl_all_scenarios.py``), so a regression that moved every level while preserving
their order — a discount-rate change, a terminal-form change, a bridge change — passed
the suite silently while the UI and the downloadable workbooks drifted.

So: if one of these fails, that is NOT automatically a bug. It means a deliberate
methodology change has moved a headline number and the new value needs to be looked at,
signed off, and pasted in here. Update them consciously, never reflexively.

Values captured 13 August 2026 at commit ``92bbd2c`` (suite 122, ratchet 8), and
cross-checked the same day against the base64 workbooks embedded in the three scenario
interfaces, recalculated headless in LibreOffice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.dcf.fcf_engine import FcfEngine, TERMINAL_SHARE_THRESHOLD
from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.translator import (
    build_bank_inputs_from_data,
    build_engine_inputs_from_data,
    build_segment_inputs_from_data,
    load_inputs,
)

ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = [
    "orderly_convergence",
    "muddle_through",
    "ai_productivity_lag",
    "fragmentation",
    "disorderly_climate_crystallisation",
    "stagflation_persists",
]

# --- DNL: industrial FCFF / WACC, AUD per share --------------------------------
DNL_GOLDEN = {
    "orderly_convergence": 3.5619,
    "muddle_through": 3.0730,                      # independently audited (v6 workbook)
    "ai_productivity_lag": 2.9850,
    "fragmentation": 2.2224,
    "disorderly_climate_crystallisation": 1.1768,
    "stagflation_persists": 1.0194,
}

# --- WBC: bank DDM / Ke (§15), AUD per share -----------------------------------
WBC_GOLDEN = {
    "orderly_convergence": 35.7058,
    "muddle_through": 30.0304,                     # independently audited (v4 workbook)
    "ai_productivity_lag": 29.6987,
    "fragmentation": 27.1096,
    "disorderly_climate_crystallisation": 22.5807,
    "stagflation_persists": 18.6488,
}

# --- CSL: multi-segment FCFF / Ke (M3), (USD, AUD) per share -------------------
CSL_GOLDEN = {
    "orderly_convergence": (156.6054, 237.2885),
    "muddle_through": (134.5216, 203.8271),        # independently audited (v4 workbook)
    "ai_productivity_lag": (131.1245, 198.6799),
    "fragmentation": (111.0277, 168.2291),
    "disorderly_climate_crystallisation": (115.3559, 174.7872),
    "stagflation_persists": (105.5339, 159.9050),
}


def _dnl(scenario):
    inp = load_inputs(ROOT, scenario, "industrial_explosives", "dnl")
    return FcfEngine().run(build_engine_inputs_from_data(inp, scenario))


def _wbc(scenario):
    inp = load_inputs(ROOT, scenario, "australian_major_banks", "wbc")
    return BankEngine().run(build_bank_inputs_from_data(inp, scenario))


def _csl(scenario):
    inp = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    return SegmentEngine().run(build_segment_inputs_from_data(inp, scenario))


# ------------------------------------------------------------------ levels
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_dnl_scenario_level(scenario):
    assert _dnl(scenario).value_per_share == pytest.approx(DNL_GOLDEN[scenario], abs=5e-4)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_wbc_scenario_level(scenario):
    assert _wbc(scenario).value_per_share == pytest.approx(WBC_GOLDEN[scenario], abs=5e-4)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_csl_scenario_level(scenario):
    usd, aud = CSL_GOLDEN[scenario]
    r = _csl(scenario)
    assert r.value_per_share_usd == pytest.approx(usd, abs=5e-4)
    assert r.value_per_share_aud == pytest.approx(aud, abs=5e-4)


# ------------------------------------------- §11.4.2 terminal-share warning
# The threshold check now exists on all three engines (previously industrial only),
# so the two valuations that most need the sensitivity pass can finally say so.
TERMINAL_BREACH = {
    # (company, scenario) -> terminal share of EV / of the equity claim
    ("dnl", "muddle_through"): 0.7258,
    ("wbc", "muddle_through"): 0.7631,
    ("wbc", "stagflation_persists"): 0.8445,       # worst in the project
    ("csl", "muddle_through"): 0.7516,
}


@pytest.mark.parametrize("key,expected", sorted(TERMINAL_BREACH.items()))
def test_terminal_share_breaches_are_measured_and_warned(key, expected):
    company, scenario = key
    if company == "dnl":
        r = _dnl(scenario)
        share = r.terminal_share_of_ev
    elif company == "wbc":
        r = _wbc(scenario)
        share = r.terminal_share_of_claim
    else:
        r = _csl(scenario)
        share = r.terminal_share_of_ev
    assert share == pytest.approx(expected, abs=5e-4)
    assert share > TERMINAL_SHARE_THRESHOLD
    assert any("sensitivity pass" in w for w in r.warnings), (
        f"{company}/{scenario} terminal is {share:.1%} of value but no §11.4.2 "
        "warning was emitted."
    )


def test_warning_is_silent_below_the_threshold():
    """DNL Disorderly Climate sits at 69.3% — under 70%, so no warning fires.

    Guards the threshold itself: a change that made the warning unconditional would
    make every other assertion in this block vacuous.
    """
    r = _dnl("disorderly_climate_crystallisation")
    assert r.terminal_share_of_ev == pytest.approx(0.6928, abs=5e-4)
    assert r.terminal_share_of_ev < TERMINAL_SHARE_THRESHOLD
    assert not r.warnings


def test_every_scenario_reports_a_terminal_share_on_every_engine():
    """Parity: the diagnostic exists on all three engines for all six worlds."""
    for scenario in SCENARIOS:
        assert 0.0 < _dnl(scenario).terminal_share_of_ev < 1.0
        assert 0.0 < _wbc(scenario).terminal_share_of_claim < 1.0
        assert 0.0 < _csl(scenario).terminal_share_of_ev < 1.0
