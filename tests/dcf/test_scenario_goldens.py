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
from vcc_valuations.dcf.fcf_engine import (
    FcfEngine,
    TERMINAL_SHARE_THRESHOLD,
    terminal_share_warning,
)
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
    # Re-pinned 25 Sep 2026 for D-35/D-36 (build order item 4): the explicit
    # horizon extends 5 -> 6 years (the longest any DNL scenario's drivers take
    # to straight-line, once D-69's gas roll-off revision is folded in), revenue
    # growth fades linearly to g over the final 2 years (1 for Disorderly
    # Climate, D-70) instead of holding the chain rate flat, and the gas
    # roll-off is -2.0pp total on the D-69 phasing rather than -1.5pp. Re-pinned
    # again the same day for the D-49 terminal-capex roll-forward fix: that
    # roll-forward was compounding revenue at a flat re-derived rate rather
    # than D-36's actual per-year fade path, overstating the fixed capital base
    # and so understating the terminal capex rate. Every level moves down: an
    # extra year of margin compression from the heaviest part of the roll-off,
    # slower final-year growth from the fade, and the corrected (higher)
    # terminal capex rate, only partly offset by a sixth year of cash flow.
    # Levels before D-35/D-36: 2.3316 / 1.9895 / 2.0127 / 1.2241 / 0.9924 /
    # 0.0491. Levels after D-35/D-36 but before the D-49 fix: 2.2026 / 1.8734 /
    # 1.8981 / 1.1121 / 0.8391 / -0.0452.
    "orderly_convergence": 2.1626,
    "muddle_through": 1.8461,                      # independently audited (generated workbook, all six)
    "ai_productivity_lag": 1.8768,
    "fragmentation": 1.0860,
    "disorderly_climate_crystallisation": 0.8180,
    # Stagflation Persists crosses to slightly NEGATIVE. It was already earning
    # barely above its own cost of capital on new capital under the old 5-year
    # build (4.96% earned vs 8.877% WACC -- see terminal_return_sets.yaml); a
    # sixth year of margin compression, a fading growth rate and the corrected
    # terminal capex rate tip it under. Not a broken run: it is the honest
    # consequence of a scenario the model already had sitting right at the
    # margin.
    "stagflation_persists": -0.0661,
}

# --- WBC: bank DDM / Ke (§15), AUD per share -----------------------------------
WBC_GOLDEN = {
    # Re-pinned 16 Sep 2026 for D-60: the payout is cut to hold CET1 on the
    # operating target once the ratio reaches it. Retained equity is capitalised
    # in the terminal at (ROE - g)/(Ke - g), so a withheld dividend is worth more
    # retained than paid and every level that binds moves UP. Levels before:
    # 35.7058 / 30.0304 / 29.6987 / 27.1096 / 22.5807 / 18.6488. Fragmentation
    # and Stagflation are unchanged to the cent because they erode least and the
    # rule never binds in them -- which is the check that it is one-sided.
    # Re-pinned twice in two days, and the second one largely undid the first.
    # D-60 (16 Sep) bound the payout to the ARCHETYPE operating target of 11.50%
    # and lifted four levels. M13 (17 Sep) corrected WBC's own board target to
    # 11.25% post-dividend -- Westpac's stated figure, replacing the 11.0-11.5%
    # range the file had -- and the company target overrides the archetype anchor.
    # At 11.25% the constraint stops binding in five of six scenarios, so those
    # five return to their pre-D-60 values and only Orderly Convergence, which
    # erodes fastest, still binds. Pre-D-60: 35.7058 / 30.0304 / 29.6987 /
    # 27.1096 / 22.5807 / 18.6488.
    "orderly_convergence": 36.1619,                # binds Y4 (was Y3 at 11.50%)
    "muddle_through": 30.0304,                     # no longer binds; ties the v4 workbook again
    "ai_productivity_lag": 29.6987,                # no longer binds
    "fragmentation": 27.1096,                      # never bound
    "disorderly_climate_crystallisation": 22.5807,  # no longer binds
    "stagflation_persists": 18.6488,               # never bound
}

# --- CSL: multi-segment FCFF / Ke (M3), (USD, AUD) per share -------------------
CSL_GOLDEN = {
    "orderly_convergence": (150.0986, 227.4294),
    "muddle_through": (129.213, 195.7835),        # independently audited (generated workbook, all six)
    "ai_productivity_lag": (126.197, 191.2137),
    "fragmentation": (106.8851, 161.9522),
    "disorderly_climate_crystallisation": (110.9456, 168.1047),
    "stagflation_persists": (101.3368, 153.5455),
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
    # DNL Muddle Through dropped OUT of breach on 25 Sep 2026 (D-35/D-36: the
    # longer horizon and the growth fade both shrink the terminal's share of
    # value) and Disorderly Climate is now the one DNL case that breaches --
    # exactly the finding horizon_and_terminal_convergence.md §10 anticipated.
    # Re-pinned again the same day for the D-49 terminal-capex roll-forward fix
    # (0.766 -> 0.7631).
    ("dnl", "disorderly_climate_crystallisation"): 0.7631,
    ("wbc", "muddle_through"): 0.7631,     # back to the pre-D-60 figure (M13)
    ("wbc", "stagflation_persists"): 0.8445,       # worst in the project; D-60 never binds here
    ("csl", "muddle_through"): 0.7538,
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
    """Guards the threshold itself: an unconditional warning would make every
    other assertion in this block vacuous.

    This used to assert against DNL Disorderly Climate, which sat at 69.3%. It
    no longer can: normalising DNL's terminal reinvestment (23 Aug 2026) lifted
    every DNL scenario above 70%, and with WBC and CSL already above it there is
    now no live valuation in the project below the threshold — which is itself
    the finding, recorded in WORKING_NOTES. The guard therefore exercises the
    pure predicate rather than waiting for a company to fall back under it.
    """
    assert terminal_share_warning(TERMINAL_SHARE_THRESHOLD - 0.01) is None
    assert terminal_share_warning(TERMINAL_SHARE_THRESHOLD) is None
    warning = terminal_share_warning(TERMINAL_SHARE_THRESHOLD + 0.01)
    assert warning is not None and "sensitivity pass" in warning


def test_terminal_shares_are_measured_case_by_case():
    """Pinned so a movement across the 70% line is read, not absorbed.

    Until 14 September 2026 all eighteen company x scenario valuations sat above
    the threshold and this test asserted exactly that. The Denali restatement
    (D-48, D-50) and the terminal capital base growing at g (D-49) put AI
    Productivity Lag at 69.3% and Stagflation Persists at 61.9%, so the blanket
    claim is no longer true and the §11.4.2 sensitivity obligation now applies
    case by case rather than universally. Measuring each share is the honest
    form of the same guard.
    """
    # Re-pinned 25 Sep 2026 for D-35/D-36: every DNL terminal share falls, since
    # the terminal's share of value shrinks once the explicit period is longer
    # and revenue growth fades rather than holding at the chain rate. Only
    # Disorderly Climate still breaches 70% (see TERMINAL_BREACH above).
    dnl_shares = {
        # Re-pinned 25 Sep 2026 (D-35/D-36, then the D-49 roll-forward fix).
        "orderly_convergence": 0.6649,
        "muddle_through": 0.6485,
        "ai_productivity_lag": 0.6418,
        "fragmentation": 0.6324,
        "disorderly_climate_crystallisation": 0.7631,
        "stagflation_persists": 0.5498,
    }
    for scenario in SCENARIOS:
        assert _dnl(scenario).terminal_share_of_ev == pytest.approx(
            dnl_shares[scenario], abs=5e-4), scenario
        # WBC and CSL are untouched by the Denali restatement and still breach.
        assert _wbc(scenario).terminal_share_of_claim > TERMINAL_SHARE_THRESHOLD, scenario
        assert _csl(scenario).terminal_share_of_ev > TERMINAL_SHARE_THRESHOLD, scenario



def test_every_scenario_reports_a_terminal_share_on_every_engine():
    """Parity: the diagnostic exists on all three engines for all six worlds."""
    for scenario in SCENARIOS:
        assert 0.0 < _dnl(scenario).terminal_share_of_ev < 1.0
        assert 0.0 < _wbc(scenario).terminal_share_of_claim < 1.0
        assert 0.0 < _csl(scenario).terminal_share_of_ev < 1.0
