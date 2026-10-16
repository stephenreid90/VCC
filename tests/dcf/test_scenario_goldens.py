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
    # Re-pinned 15 Oct 2026 for D-81: D-36's end-of-period fade is retired. Each
    # current-cycle chain term now glides linearly from its typed value to its
    # equilibrium value by the archetype's declared expiry year (beta, ore-grade
    # pickup and EM premium over 10 years; productivity and three Five Forces
    # offsets over 5; the DNEL pipeline uplift over 3), so the extras earn about
    # half the explicit period instead of eight full years. Every level down
    # 4.3-4.8%: OC 2.4619 -> 2.3451, MT 2.1059 -> 2.0067, AI 2.0903 -> 1.9984,
    # Frag 1.4179 -> 1.3576, DCC 1.0629 -> 0.9955, Stag 1.1204 -> 1.0724.
    # Where the nominal-GDP cap binds (OC, MT) year 10 sits above g by the cap
    # gap (OC 6.04% vs 5.06%); disclosed, not bridged (D-71).
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
    #
    # Re-pinned 2 Oct 2026 for D-71. Two things move every level. (1) The
    # explicit period is a FIXED ten years, no longer D-35's computed six: with
    # the interim flat chain rate held for eight years before D-36's fade, four
    # more years of ~6% nominal growth lift every scenario -- a data artefact
    # of the flat per-scenario scalars that D-37's year-anchored paths exist to
    # replace, disclosed as such rather than hidden. (2) The headline terminal
    # is excess-return convergence (D-62 to D-66 promoted from disclosure to
    # headline) over the declared decay horizon (12.5 years, the 10-15 band's
    # midpoint) for the four scenarios that have one, symmetric in R - WACC:
    # Muddle Through, Orderly Convergence and AI Lag converge DOWN from
    # 12.7-14.3% (a haircut against Gordon on the earned return); Disorderly
    # Climate converges UP from 8.0% against an 8.9% WACC (a lift). Fragmentation
    # and Stagflation have no declared decay horizon and fall back to Gordon,
    # ratcheted in tests/dcf/test_terminal_form.py. Levels under the ten-year
    # horizon with Gordon everywhere, for the record: 2.6050 / 2.2288 / 2.2495 /
    # 1.3844 / 0.9494 / 0.0717.
    #
    # Re-pinned again 2 Oct 2026 for D-72 (the four translation rulings). The
    # chain now reads each scenario's own year-anchored series: DM inflation is
    # the scenario CPI (3.0% on Muddle Through vs the old 2.5% anchor, +0.35pp
    # of pricing growth); mining is world real GDP plus a calibrated spread;
    # gas runs at the transition anchor until the scenario's equilibrium year,
    # then the baseline; the margin shift ramps in over the first phase and
    # PERSISTS (Fragmentation, Disorderly Climate) or REVERTS by Y10
    # (Stagflation). Terminal g is DERIVED -- the equilibrium chain at Y10,
    # capped at scenario nominal GDP: 5.27 / 5.37 (capped) / 4.67 / 4.45 /
    # 4.94 / 3.19 -- replacing the typed 2.50 / 2.75 / 2.25 / 2.25 / 1.75 / 2.25.
    # Under the convergence terminal g matters little once the excess return
    # is gone; the explicit-period paths and the margin shape are what moved
    # these. Stagflation moves most (0.07 -> 1.39): decisions 3 and 4 make it
    # cyclical, so its gas spike ends and its margin hit reverts at its own
    # resolution phase. Levels under D-71 alone: 2.2582 / 1.9422 / 1.9481 /
    # 1.3844 / 1.0302 / 0.0717.
    # Re-pinned 14 Oct 2026 for D-80 (Stephen's ruling): year-10 advanced CPI lowered
    # in every scenario to where central banks hold it over a decade (OC 2.0, MT 2.5,
    # AI Lag 2.5, Frag 2.8, DCC 2.5, Stag 3.0; were 2.3 / 3.0 / 2.8 / 3.3 / 3.0 / 3.5).
    # Two channels: the nominal-GDP cap on terminal g falls (5.37 -> 4.86 in MT) and
    # the D-72 spread paths recalibrate (a fixed gap on a now-sloping base). MT and OC
    # are both capped now. OC -1.2%, MT -1.5%, AI Lag -0.8%, Frag -1.1%, DCC -1.2%,
    # Stag -1.4%. Before: 2.4908 / 2.1382 / 2.1071 / 1.4342 / 1.0762 / 1.1361.
    "orderly_convergence": 2.3451,
    "muddle_through": 2.0067,                      # independently audited (generated workbook, all six)
    "ai_productivity_lag": 1.9984,
    # Fragmentation and Stagflation re-pinned 14 Oct 2026 (bridge note step 3):
    # both now declare a decay horizon (scale + switching_cost, 10-15y, ratified by
    # Stephen via design/frameworks/decay_horizon_checklist.md), so the headline
    # terminal is convergence over 12.5 years instead of Gordon on the earned
    # excess. Both earn ABOVE the WACC at Y10 (Frag 10.2%, Stag 11.8% vs 8.9%),
    # so competing the excess away cuts them: 1.5776 -> 1.4342, 1.3898 -> 1.1361.
    # Stagflation is again the floor's neighbour, not the floor (DCC 1.08).
    "fragmentation": 1.3576,
    "disorderly_climate_crystallisation": 0.9955,
    # Stagflation Persists crosses to slightly NEGATIVE. It was already earning
    # barely above its own cost of capital on new capital under the old 5-year
    # build (4.96% earned vs 8.877% WACC -- see terminal_return_sets.yaml); a
    # sixth year of margin compression, a fading growth rate and the corrected
    # terminal capex rate tip it under. Not a broken run: it is the honest
    # consequence of a scenario the model already had sitting right at the
    # margin. Back to slightly POSITIVE under D-71's ten-year horizon (the extra
    # years of chain growth), still Gordon pending a declared decay horizon.
    # D-72: 1.39 -- a cyclical scenario now, see the note above.
    "stagflation_persists": 1.0724,
}

# --- WBC: bank DDM / Ke (§15), AUD per share -----------------------------------
WBC_GOLDEN = {
    # Re-pinned 16 Oct 2026 for bridge item (e), option 1b: retained equity earns Ke as cash
    # in the explicit years (BankInputs.retained_earns_ke). Before: 45.3940 / 32.3984 / 32.7288 /
    # 28.2314 / 23.0786 / 15.7268. Every level rises 4-6%. The payout cut no longer lowers value.
    # Re-pinned 15 Oct 2026 for D-81: the share-loss offset (-15bp, current-cycle
    # since D-79) glides to zero by Y5 instead of running ten years and vanishing
    # at the terminal. A drag that fades sooner lifts every level 0.1-0.5%:
    # OC 45.1590 -> 45.3940, MT 32.2655 -> 32.3984, AI 32.5936 -> 32.7288,
    # Frag 28.1291 -> 28.2314, DCC 23.0347 -> 23.0786, Stag 15.7094 -> 15.7268.
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
    # Re-pinned 14 Oct 2026 (D-72 for the bank archetype): AIEA growth is now the
    # scenario's own bank_system_aiea_growth path (nominal-GDP proxy plus a gap
    # calibrated to the old flat industry anchor + scenario shift) plus WBC's
    # offset, read per year. The path's MEAN over the D-37 anchor years is the old
    # flat rate, so only the shape moved: +0.2% / 0 / +0.1% / -0.0% / +0.1% / +0.3%.
    # Muddle Through is unchanged to the cent (its world series are flat).
    # Before: 36.1619 / 30.0304 / 29.6987 / 27.1096 / 22.5807 / 18.6488.
    # Re-pinned again 14 Oct 2026 for D-71's TEN-year explicit period (Stephen's
    # ruling the same day): five more years of the typed glides held at their Y5
    # value, growth from the scenario path to Y10, D-60 now binding in every
    # scenario (MT at Y7, Stagflation at Y10). OC +11.2%, MT +3.4%, AI Lag +4.0%,
    # Frag +2.3%, DCC +2.1%, Stag -13.0% -- Stagflation FALLS because five more
    # years at a 5.2% earned ROE against an 8.05% Ke destroy value before the 9%
    # terminal ROE is capitalised. The v4 workbook still ties the engine run at its
    # own five years (test_wbc_bank.py). Five-year levels on the D-72 path:
    # 36.2265 / 30.0304 / 29.7176 / 27.1084 / 22.6051 / 18.7015.
    # Re-pinned 14 Oct 2026 for D-79 (Stephen's ruling): terminal growth is DERIVED
    # from the bank chain in equilibrium -- the bank_system_aiea_growth path at Y10
    # with WBC's share-loss offset off (D-78), capped at scenario nominal GDP -- in
    # place of the typed 3.25-3.75%. Derived g: 5.37 (capped) / 4.50 / 4.42 / 3.92 /
    # 3.46 / 1.94%. OC +16.7%, MT +6.5%, AI Lag +7.1%, Frag +3.0%, DCC +0.5%,
    # Stag -2.8% (its shrinking system is below the old typed rate). Most of the
    # movement is the typed 3.5% giving way to the 4.5-5.4% nominal world the
    # scenario files already assert, not a method change. Before: 40.2748 /
    # 31.0502 / 30.8918 / 27.7263 / 23.0864 / 16.2617.
    # Re-pinned 14 Oct 2026 for D-80: year-10 advanced CPI lowered in every scenario
    # (see DNL_GOLDEN). The bank series is real GDP + CPI plus a fixed gap, so both
    # the explicit path and the derived g move: g 5.06 (capped) / 4.14 / 4.20 / 3.56 /
    # 3.10 / 1.54%. OC -3.9%, MT -2.5%, AI Lag -1.5%, Frag -1.5%, DCC -0.7%, Stag -0.6%.
    # Before: 46.9911 / 33.0779 / 33.0905 / 28.5658 / 23.2017 / 15.7985.
    "orderly_convergence": 47.9071,                # binds Y4
    "muddle_through": 33.9332,                     # binds Y7
    "ai_productivity_lag": 34.2656,
    "fragmentation": 29.5771,
    "disorderly_climate_crystallisation": 24.3892,
    "stagflation_persists": 16.3524,
}

# --- CSL: multi-segment FCFF / Ke (M3), (USD, AUD) per share -------------------
CSL_GOLDEN = {
    # Re-pinned 16 Oct 2026 (D-87, decision Q1): CSL net debt rolled from the 1H26 close
    # (USD 9,100m, 31 Dec 2025) to the valuation date (30 Jun 2026) on the agreed convention:
    # part-year operating cash flow, each scenario's own FY26 capex for the half, and declared
    # dividends only (no buyback guess). Net debt 7,870 to 7,886. Values rise 1.8% to 3.9%.
    # Before (USD, AUD): OC 174.4343/264.3028, MT 148.0575/224.3367, AI 141.8495/214.9303,
    # Frag 112.2106/170.0215, DCC 118.7497/179.9295, Stag 96.8539/146.7531.
    # Re-pinned 16 Oct 2026 for D-06: discounted at the WACC (8.12%), not Ke (8.75%). Before (USD, AUD):
    # OC 158.1331 / 239.6033, MT 134.3206 / 203.5226, AI 128.8557 / 195.2421, Frag 102.3028 / 155.0093,
    # DCC 108.3302 / 164.1419, Stag 88.5616 / 134.1886.
    # Re-pinned 14 Oct 2026 (step 3, ratified by Stephen): CSL's six scenarios now
    # declare a LONG decay horizon, 20-30 years (midpoint 25), on the plasma-
    # collection network, manufacturing complexity, regulatory and patent-LCM
    # barriers (data/impact_matrix/by_industry/biopharmaceuticals.yaml). The
    # terminal is excess_return_convergence with N = 25 on the group capital base,
    # in place of Gordon: OC -17.9%, MT -16.5%, AI Lag -15.8%, Frag -15.1%,
    # DCC -15.0%, Stag -16.3%. Gordon levels before (USD, AUD): 176.0748/266.7885,
    # 147.3357/223.2431, 141.8839/214.9825, 116.8037/176.9810, 123.5242/187.1639,
    # 107.2600/162.5203. Independently reproduced by the sizing script
    # (terminal_disclosure_set.yaml) before the pin.
    # Re-pinned 14 Oct 2026 (D-72 for the segment archetypes): each segment's growth
    # is now its archetype's scenario series (nominal-GDP proxy plus a gap calibrated
    # to the typed steady state) plus the company's time-limited offset (the typed
    # path less its steady state -- Behring's J-curve). The series' MEAN over the
    # D-37 anchor years is the typed rate, so only the shape moved; the inflationary
    # scenarios front-load nominal growth and rise most: OC +0.4%, AI Lag +0.3%,
    # Frag +0.1%, DCC +1.2%, Stag +2.2%. Muddle Through unchanged to the cent.
    # Before (USD, AUD): 150.0986/227.4294, 126.197/191.2137, 106.8851/161.9522,
    # 110.9456/168.1047, 101.3368/153.5455.
    # Re-pinned again 14 Oct 2026 for D-71's TEN-year explicit period (Stephen's
    # ruling): FY27-FY36, segment growth from the archetype paths to Y10, margin
    # uplift glided to FY31 then held, Gordon terminal (no decay horizon declared
    # for CSL yet). OC +16.8%, MT +14.0%, AI Lag +12.1%, Frag +9.2%, DCC +10.0%,
    # Stag +3.6% -- the same horizon artefact DNL disclosed on 2 Oct: five more
    # years of 5-7% nominal growth at a held margin before the terminal. The
    # five-year generated workbook tie moved with it (csl_workbook_all_scenarios.json
    # regenerated); the hand-built v4 still ties the engine run at five years.
    # Five-year levels on the D-73 paths (USD, AUD): 150.6863/228.3199,
    # 129.213/195.7835, 126.5514/191.7507, 106.9922/162.1145, 112.3121/170.1754,
    # 103.5286/156.8666.
    # Re-pinned 14 Oct 2026 for D-79 (Stephen's ruling): terminal growth is DERIVED
    # -- each segment's archetype series at Y10 (the company offset is zero there by
    # construction), weighted by final-year segment revenue, capped at scenario
    # nominal GDP -- in place of the typed 2.75-3.25%. Derived g: 5.37 (capped) /
    # 5.37 (capped) / 4.86 / 3.90 / 3.85 / 2.73%. OC +11.4%, MT +12.0%, AI Lag +9.5%,
    # Frag +4.8%, DCC +4.6%, Stag -1.0%. As for WBC, the movement is the typed 3%
    # giving way to the nominal GDP the scenario files assert at Y10. Before (USD,
    # AUD): 144.5432/219.0118, 123.0844/186.4975, 119.4961/181.0605,
    # 99.1514/150.2342, 105.0520/159.1748, 89.7794/136.0337.
    # Re-pinned 14 Oct 2026 for D-80: year-10 advanced CPI lowered in every scenario
    # (see DNL_GOLDEN). Segment series are real GDP + CPI plus a fixed gap, so the
    # explicit paths and the derived g move: g 5.06c / 4.86c / 4.55c / 3.54 / 3.49 /
    # 2.33% (c = capped). AUD: OC -1.7%, MT -2.6%, AI Lag -1.5%, Frag -1.4%, DCC -1.4%,
    # Stag -1.2%. Before (USD, AUD): 160.9749/243.9092, 137.8604/208.8861,
    # 130.8477/198.2605, 103.9154/157.4527, 109.8907/166.5064, 88.9258/134.7404.
    # CSL re-pinned 15 Oct 2026 (item (c)): segment driver now US real GDP + advanced CPI
    # (approved paths). AI Lag and Disorderly Climate are unchanged: a flat offset is absorbed
    # by the calibrated gap.
    "orderly_convergence": (176.9697, 268.1445),
    "muddle_through": (150.6109, 228.2056),       # generated workbook ties (LibreOffice recalc, all six)
    "ai_productivity_lag": (144.4047, 218.802),
    "fragmentation": (114.7774, 173.9107),
    "disorderly_climate_crystallisation": (121.3099, 183.8088),
    "stagflation_persists": (99.4224, 150.6448),
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
    # Re-pinned 2 Oct 2026 (D-71): 0.7631 -> 0.7021. Then D-72 took it to 0.6980,
    # a hair UNDER the 70% line, so no DNL scenario breaches today; it is pinned
    # in dnl_shares below so the next move across the line is read, not absorbed.
    # 14 Oct 2026 (D-71 ten years for WBC and CSL): NO valuation in the project
    # breaches the 70% line any more. WBC MT 0.7631 -> 0.6109, WBC Stagflation 0.8430
    # -> 0.6926 (still the highest in the project), CSL MT 0.7538 -> 0.5738. They are
    # pinned in wbc_shares / csl_shares below so the next move across the line is
    # read, not absorbed. The dict is kept (empty) so the guard and its reasons stay.
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
    # No DNL scenario breaches 70% as of D-72 (Disorderly Climate sits at 69.8%).
    dnl_shares = {
        # Re-pinned 25 Sep 2026 (D-35/D-36, then the D-49 roll-forward fix),
        # and again 2 Oct 2026 for D-71 (ten-year horizon, convergence terminal):
        # four more explicit years and a finite convergence both pull the
        # terminal's share down everywhere but Disorderly Climate, whose
        # upward convergence lifts its terminal.
        # D-72 (same day): the derived g and the explicit paths move every share;
        # Stagflation's rises most as its explicit years recover.
        # 14 Oct 2026: Fragmentation and Stagflation converge (decay horizons
        # declared), so their terminals shrink: 0.5389 -> 0.5104, 0.6754 -> 0.6346.
        # D-80 (14 Oct 2026): lower year-10 CPI, lower g, every share down 0.3-0.6pt.
        # D-81 (15 Oct 2026): slower explicit growth as the extras glide off takes
        # every share down 0.5-1.1pt (DCC 0.6953 -> 0.6843).
        "orderly_convergence": 0.5206,
        "muddle_through": 0.5036,
        "ai_productivity_lag": 0.4930,
        "fragmentation": 0.4996,
        "disorderly_climate_crystallisation": 0.6843,
        "stagflation_persists": 0.6267,
    }
    # 14 Oct 2026: WBC and CSL moved to the ten-year explicit period (D-71) and every
    # one of their terminal shares fell below 70% -- the same mechanism as DNL on
    # 2 Oct (more explicit years, a smaller terminal). Pinned, not asserted below
    # the line, so the next crossing in either direction is a conscious event.
    # D-79 (14 Oct 2026): a higher derived g lifts every WBC terminal share (OC
    # 0.6373 -> 0.6864, Stag 0.6926 -> 0.6849 the other way); none crosses 70%.
    wbc_shares = {
        # Re-pinned 16 Oct 2026 (option 1b): the explicit value rises, so every WBC terminal share falls.
        # D-80 (14 Oct 2026): lower g takes every share down 0.2-1.3pt (OC 0.6864 -> 0.6736).
        # D-81 (15 Oct 2026): the offset glide lifts every share 0.4-0.7pt; Stagflation
        # 0.6826 -> 0.6900 is the closest to the 70% line in the project.
        "orderly_convergence": 0.6442, "muddle_through": 0.6014, "ai_productivity_lag": 0.5993,
        "fragmentation": 0.5737, "disorderly_climate_crystallisation": 0.5680,
        "stagflation_persists": 0.6673,
    }
    # CSL re-pinned 14 Oct 2026 (step 3): the 20-30 year decay horizon takes every
    # terminal share down 7-8 points. Gordon shares before: 0.5987, 0.5738, 0.5648,
    # 0.5438, 0.5445, 0.5336.
    # D-79 (14 Oct 2026): derived g lifts every CSL share 2-5 points; Stag -0.4.
    csl_shares = {
        # Re-pinned 16 Oct 2026 (D-06, WACC): the lower rate lifts every CSL terminal share.
        # D-80 (14 Oct 2026): lower g takes every share down 0.8-1.3pt.
        # CSL re-pinned 15 Oct 2026 (item (c), US driver): 0.5571 -> 0.5557, 0.5351 -> 0.5342,
        # 0.4873 -> 0.4855, 0.4466 -> 0.4568. AI Lag and Disorderly unchanged.
        "orderly_convergence": 0.5809, "muddle_through": 0.5599, "ai_productivity_lag": 0.5508,
        "fragmentation": 0.5107, "disorderly_climate_crystallisation": 0.5126,
        "stagflation_persists": 0.4815,
    }
    for scenario in SCENARIOS:
        assert _dnl(scenario).terminal_share_of_ev == pytest.approx(
            dnl_shares[scenario], abs=5e-4), scenario
        assert _wbc(scenario).terminal_share_of_claim == pytest.approx(wbc_shares[scenario], abs=5e-4), scenario
        assert _csl(scenario).terminal_share_of_ev == pytest.approx(csl_shares[scenario], abs=5e-4), scenario
        assert _wbc(scenario).terminal_share_of_claim < TERMINAL_SHARE_THRESHOLD, scenario
        assert _csl(scenario).terminal_share_of_ev < TERMINAL_SHARE_THRESHOLD, scenario



def test_every_scenario_reports_a_terminal_share_on_every_engine():
    """Parity: the diagnostic exists on all three engines for all six worlds."""
    for scenario in SCENARIOS:
        assert 0.0 < _dnl(scenario).terminal_share_of_ev < 1.0
        assert 0.0 < _wbc(scenario).terminal_share_of_claim < 1.0
        assert 0.0 < _csl(scenario).terminal_share_of_ev < 1.0
