"""The terminal-return set is regenerable, and its headline findings are pinned.

D-42 (PROPOSED) and M14. The committed set in
``design/methodology/terminal_return_sets.yaml`` is the published table; this test
is the ``asserted_by`` half of the standing-rule-4 contract — regenerate from the
production engines and the committed figures must come back.

The three findings pinned below are the reason the diagnostic was worth building,
and each is pinned loosely enough to survive a data refresh but tightly enough to
fail if the underlying assumption changes.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from size_terminal_returns import as_set, collect  # noqa: E402

SET_PATH = ROOT / "design" / "methodology" / "terminal_return_sets.yaml"


@pytest.fixture(scope="module")
def rows():
    return collect()


@pytest.fixture(scope="module")
def committed():
    return yaml.safe_load(SET_PATH.read_text(encoding="utf-8"))


def test_the_committed_set_regenerates(rows, committed):
    """Standing rule 4: the published table comes back from the engines."""
    assert as_set(rows) == committed, (
        "design/methodology/terminal_return_sets.yaml is stale — "
        "run scripts/size_terminal_returns.py"
    )


def test_every_valuation_is_covered(rows):
    scenarios = sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))
    assert len(rows) == 3 * len(scenarios)
    assert {r.company_id for r in rows} == {"dnl", "wbc", "csl"}


# ------------------------------------------------------- finding 1: CSL / D-53
def test_csl_terminal_asserts_an_implausible_return_on_new_capital(rows):
    """D-53, quantified. This is the number that ruling was missing.

    CSL declares ``terminal_capex_pct_revenue`` equal to ``da_pct_revenue``, so net
    capex in the terminal is exactly zero and the only reinvestment left is
    working capital at g x intensity. A perpetuity that grows while reinvesting
    about four per cent of its earnings is asserting a return on new capital in
    the high sixties, against a discount rate under nine per cent. That is not a
    moat, it is the arithmetic of ``capex_rule: equals_da`` — which is precisely
    what D-49 retired as a house rule and D-53 ruled must apply to CSL as well.

    Pinned as a band rather than a point: the finding is the order of magnitude,
    and implementing D-53 should drop it into the range DNL now occupies.
    D-79 (14 Oct 2026): the derived terminal growth (2.7-5.4%, was typed 2.75-3.25%)
    lifts the reinvestment rate to 4-7% (it is g x working-capital intensity over
    earnings); the return on new capital stays in the sixties and seventies.
    """
    csl = [r for r in rows if r.company_id == "csl"]
    assert len(csl) == 6

    for r in csl:
        assert r.reinvestment_rate < 0.08, (r.scenario_id, r.reinvestment_rate)
        assert 0.55 < r.return_on_new_capital < 0.80, (r.scenario_id, r.return_on_new_capital)
        assert r.excess_over_cost_of_capital > 0.45, r.scenario_id
        assert any("exceeds" in w for w in r.warnings)


# ------------------------------------------------------- finding 2: WBC / M14
def test_wbc_stagflation_terminal_roe_is_a_recovery_assumption(rows):
    """M14. The one scenario where the declared rate sits above what is earned.

    On five of six the declared terminal ROE is conservative against the ROE the
    final explicit year earns. Stagflation is the exception and it is a large one,
    on the scenario whose terminal is the biggest share of value in the project.
    """
    wbc = {r.scenario_id: r for r in rows if r.company_id == "wbc"}
    stag = wbc["stagflation_persists"]

    # Ten-year figures (D-71, 14 Oct 2026); at five years they were 0.0401 / 0.0499.
    # Five more years of the Stagflation glides (CTI 51%, +50bp losses) earn 5.2% on
    # the closing equity against a declared 9%: the recovery step was 3.8pp.
    # D-91 (16 Oct 2026): with the -20bp Stagflation NIM shift retired the glides earn
    # more, so the final year earns 6.2% (was 5.2%) and the step shrinks to 2.8pp. Still a recovery assumption, still disclosed.
    assert stag.step_from_earned == pytest.approx(0.0278, abs=0.002)
    assert stag.earned_final_explicit == pytest.approx(0.0622, abs=0.002)
    assert any("recovery assumption" in w for w in stag.warnings)

    # Every other scenario is conservative or flat, which is what makes the
    # Stagflation case a finding rather than a systemic bias.
    for scenario, r in wbc.items():
        if scenario == "stagflation_persists":
            continue
        assert r.step_from_earned <= 0.01, (scenario, r.step_from_earned)
        assert not any("recovery assumption" in w for w in r.warnings), scenario


# ------------------------------------------------------- finding 3: DNL / D-42
def test_dnl_splits_on_the_cost_of_capital_which_is_what_d42_is_for(rows):
    """Five DNL scenarios assert an excess return and one does not.

    This is the diagnostic behaving as D-42 intends: the terminal return is not
    uniformly above or below the discount rate, so the warning discriminates
    rather than firing on everything. The ones that exceed it are the ones that
    owe a §10.6-compliant defended exception. Fragmentation joined the "above"
    set on 2 Oct 2026 (D-71): the fixed ten-year horizon holds the flat chain
    growth four more years and lifts its whole-base return to 9.83% against an
    8.88% WACC -- 74bp on the return-on-new-capital reading, 95bp on the whole
    base. It has no declared decay horizon, so it is baselined in
    tests/terminal_defence_baseline.json pending the five-forces pass.
    """
    dnl = {r.scenario_id: r for r in rows if r.company_id == "dnl"}
    above = {s for s, r in dnl.items() if r.excess_over_cost_of_capital > 0}
    below = set(dnl) - above

    # D-72 (same day): Stagflation joins too -- cyclical, its margin hit has
    # reverted by year 10 and it earns 11.8% on the whole base. Baselined with
    # Fragmentation in tests/terminal_defence_baseline.json.
    assert above == {"muddle_through", "ai_productivity_lag", "orderly_convergence",
                     "fragmentation", "stagflation_persists"}, above
    assert below == {"disorderly_climate_crystallisation"}, below
    for s in above:
        assert any("D-42" in w for w in dnl[s].warnings)
    for s in below:
        assert not any("exceeds" in w for w in dnl[s].warnings), s


def test_the_two_readings_no_longer_disagree_about_fragmentation(rows):
    """Which reading governs is a substantive choice, not a rounding preference --
    and as of 25 Sep 2026 (D-35/D-36) the two readings have stopped disagreeing
    anywhere in DNL, Fragmentation included.

    Before the horizon extended and revenue growth started fading to g,
    Fragmentation sat BELOW its WACC on the return on new capital and ABOVE it
    on the whole capital base: under the weaker reading it owed no defended
    exception and under the better one it did. The longer horizon and the fade
    both smooth the gap between the two readings, and Fragmentation now sits
    (slightly) below WACC on BOTH. Documented rather than silently dropped,
    because a silent change of reading would silently change who owes a
    defence -- this asserts the new state explicitly so the next change to
    disagree is caught rather than assumed away.
    """
    frag = next(r for r in rows if r.company_id == "dnl"
                and r.scenario_id == "fragmentation")
    # D-71 (2 Oct 2026): Fragmentation now sits ABOVE its WACC on both readings
    # (the ten-year horizon's extra chain growth); the two readings still agree
    # in sign, which is the point this test holds.
    assert frag.excess_over_cost_of_capital > 0, frag.excess_over_cost_of_capital
    assert frag.excess_on_governing_return > 0, frag.excess_on_governing_return
    assert frag.governing_return == frag.return_on_whole_capital
    # No DNL scenario disagrees between the two readings any more (all six agree
    # in sign); revisit this test the day one does.
    dnl_rows = [r for r in rows if r.company_id == "dnl"]
    assert all(
        (r.excess_over_cost_of_capital > 0) == (r.excess_on_governing_return > 0)
        for r in dnl_rows
    ), [r.scenario_id for r in dnl_rows]


def test_dnl_declares_no_terminal_rate_and_the_earned_return_governs(rows):
    """D-76 (14 Oct 2026): a declared rate now MOVES the level, so none is copied.

    Until 14 Oct Orderly Convergence carried 9.13%, derived mechanically from its
    own declared movement (positive-small -> +25bp over the convergence target).
    While the field was disclosure-only that was harmless and the 639bp gap
    against the capital build was the D-42 finding. Under D-76 the declared rate
    is the return the convergence STARTS from, and 9.13% against the 15.5% the
    explicit period leaves the base earning would have cut the valuation by 27%
    on a number nobody chose. So it was removed: DNL declares no rate, the earned
    return governs, and the reconciliation warning is silent until Stephen
    declares one with a basis (decay_horizon_checklist.md q6).
    """
    dnl_rows = [r for r in rows if r.company_id == "dnl"]
    assert all(r.declared_return is None for r in dnl_rows), [
        (r.scenario_id, r.declared_return) for r in dnl_rows if r.declared_return is not None]
    oc = next(r for r in dnl_rows if r.scenario_id == "orderly_convergence")
    assert oc.return_on_whole_capital == pytest.approx(0.1481, abs=5e-4)   # 0.1538 before D-81 (slower explicit growth); 0.1552 before D-80
    assert oc.declared_versus_whole_capital is None
    assert not any("declares a terminal return" in w for w in oc.warnings)


def test_wbc_declares_its_terminal_roe_on_the_matrix(rows):
    """D-76: WBC's six terminal ROEs live on the australian_major_banks matrix.

    They were lifted off wbc.yaml unchanged (OC 11.0, MT 10.5, AI Lag 10.5,
    Frag 10.0, DCC 9.0, Stag 9.0), so no level moved. The bank fork reports the
    declared rate as the return on new capital, exactly as before.
    """
    expected = {"orderly_convergence": 0.11, "muddle_through": 0.105,
                "ai_productivity_lag": 0.105, "fragmentation": 0.10,
                "disorderly_climate_crystallisation": 0.09, "stagflation_persists": 0.09}
    wbc = {r.scenario_id: r for r in rows if r.company_id == "wbc"}
    assert set(wbc) == set(expected)
    for sid, roe in expected.items():
        assert wbc[sid].return_on_new_capital == pytest.approx(roe, abs=1e-9), sid


def test_every_company_with_a_capital_base_reports_the_whole_capital_return(rows):
    """D-86: the return is general, so any company with a capital base reports it.

    DNL has the D-49 roll-forward and CSL has the segment engine's base (D-67).
    The bank has no invested-capital construction, so it reports none.
    """
    have = {r.company_id for r in rows if r.return_on_whole_capital is not None}
    assert have == {"dnl", "csl"}, have
    for r in rows:
        if r.company_id in have:
            assert r.terminal_invested_capital > 0, (r.company_id, r.scenario_id)
            assert r.earned_final_explicit is not None, (r.company_id, r.scenario_id)
            assert r.governing_return == r.return_on_whole_capital, (r.company_id, r.scenario_id)


def test_csl_governing_return_is_the_earned_whole_capital_return(rows):
    """D-86, D-85: CSL's governing return is what the capital base earns.

    The 61-73% return on new capital (the g/reinvestment identity) stays in the
    set as a diagnostic only. It does not drive value (D-85) and it no longer
    governs. The cost of capital is the WACC (D-84), not Ke.
    """
    csl = [r for r in rows if r.company_id == "csl"]
    assert len(csl) == 6
    for r in csl:
        assert r.governing_return == r.return_on_whole_capital, r.scenario_id
        assert 0.19 < r.governing_return < 0.33, (r.scenario_id, r.governing_return)
        assert r.return_on_new_capital > 0.55, r.scenario_id      # diagnostic only
        assert r.governing_return < r.return_on_new_capital / 2, r.scenario_id
        assert r.cost_of_capital_name == "WACC", r.scenario_id
        assert r.declared_return is None, r.scenario_id           # D-86: no declared rate


def test_csl_set_pins_whole_capital_governing_and_diagnostic_new_capital(committed):
    # Pinned 16 Oct 2026 (D-86). Same numbers as csl_terminal_return_sets.yaml.
    pinned = {
        "orderly_convergence": (0.312154, 0.729),
        "muddle_through": (0.275579, 0.694286),
        "ai_productivity_lag": (0.270337, 0.700071),
        "fragmentation": (0.229141, 0.644571),
        "disorderly_climate_crystallisation": (0.238145, 0.648),
        "stagflation_persists": (0.205177, 0.613286),
    }
    for s, (gov, new) in pinned.items():
        r = _row(committed, "csl", s)
        assert r["governing_return"] == gov, s
        assert r["return_on_whole_capital"] == gov, s
        assert r["return_on_new_capital"] == new, s               # diagnostic only
        assert r["terminal_invested_capital"] > 22000, s
        assert r["cost_of_capital_name"] == "WACC", s
        assert r["cost_of_capital"] == 0.0812, s                 # D-84 WACC
        assert r["declared_terminal_return"] is None, s


def test_csl_earned_return_is_the_same_number_as_the_csl_return_set(committed):
    """One source: the general sizer and the CSL sizer must agree to the CSL set's rounding."""
    csl_set = yaml.safe_load(
        (ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml").read_text(encoding="utf-8"))
    for sc in csl_set["scenarios"]:
        r = _row(committed, "csl", sc["scenario"])
        assert round(r["governing_return"], 4) == sc["starting_return_ex_goodwill"], sc["scenario"]
        assert round(r["terminal_invested_capital"]) == sc["invested_capital_ex_goodwill"], sc["scenario"]


def test_the_bank_reports_its_declared_rate_not_an_inverted_one(rows):
    """The bank terminal declares the return; the identity derives retention.

    Worth asserting because reporting an inverted return for the bank would be
    wrong in a way that looks right: the justified price-to-book form fixes ROE
    and solves for the payout, so inverting it would just return the input.
    """
    for r in (r for r in rows if r.company_id == "wbc"):
        assert r.construction == "bank_roe"
        assert r.reinvestment_rate == pytest.approx(
            r.terminal_growth / r.return_on_new_capital, rel=1e-9)


# ------------------------------------------- D-86: goodwill-inclusive disclosure
def _row(committed, company, scenario):
    for r in committed["terminal_return_sets"]["current"]["rows"]:
        if r["company"] == company and r["scenario"] == scenario:
            return r
    raise KeyError((company, scenario))


def test_goodwill_inclusive_return_is_general_and_pure():
    from vcc_valuations.dcf.terminal_return import goodwill_inclusive_return
    g = goodwill_inclusive_return(earnings=100.0, capital=400.0, goodwill=100.0)
    assert g.return_ex_goodwill == 0.25
    assert g.return_incl_goodwill == 0.20
    assert g.capital_incl_goodwill == 500.0


def test_every_company_with_a_capital_base_carries_the_disclosure(rows):
    for r in rows:
        if r.terminal_invested_capital or r.company_id == "csl":
            assert r.goodwill_return is not None, (r.company_id, r.scenario_id)
            assert r.goodwill_return.return_incl_goodwill < r.goodwill_return.return_ex_goodwill
        else:
            assert r.goodwill_return is None, (r.company_id, r.scenario_id)  # bank: no base


def test_goodwill_disclosure_is_read_from_the_financials_files(committed):
    gw = {c: yaml.safe_load((ROOT / "data" / "financials" / f"{c}.yaml").read_text(encoding="utf-8"))
          for c in ("dnl", "csl")}
    for r in committed["terminal_return_sets"]["current"]["rows"]:
        if r["company"] in gw:
            assert r["goodwill"] == float(gw[r["company"]]["balance_sheet"]["goodwill"])


def test_goodwill_inclusive_figures_are_pinned(committed):
    # Pinned 16 Oct 2026 (D-86). Disclosure only: goodwill stays out of capital and value.
    pinned = {
        ("dnl", "muddle_through"): (0.130543, 0.093421),
        ("dnl", "orderly_convergence"): (0.148098, 0.106848),
        ("csl", "muddle_through"): (0.275579, 0.205154),
        ("csl", "orderly_convergence"): (0.312154, 0.234309),
        ("csl", "stagflation_persists"): (0.205177, 0.150459),
    }
    for (c, s), (ex, incl) in pinned.items():
        r = _row(committed, c, s)
        assert r["earned_return_ex_goodwill"] == ex, (c, s)
        assert r["earned_return_incl_goodwill"] == incl, (c, s)
    # the headline (ex-goodwill) return is the same number as the whole-capital reading
    for r in committed["terminal_return_sets"]["current"]["rows"]:
        if r["company"] == "dnl":
            assert r["earned_return_ex_goodwill"] == r["return_on_whole_capital"]


def test_bank_has_no_goodwill_disclosure(committed):
    for r in committed["terminal_return_sets"]["current"]["rows"]:
        if r["company"] == "wbc":
            assert r["goodwill"] is None and r["earned_return_incl_goodwill"] is None


# ------------------------------------------- D-86: the warning quotes the governing return
def _tr(**kw):
    from vcc_valuations.dcf.terminal_return import TerminalReturn
    base = dict(company_id="x", scenario_id="s", construction="fcff_roic",
                cost_of_capital=0.09, cost_of_capital_name="WACC",
                terminal_growth=0.02, terminal_earnings=10.0, reinvestment_rate=0.5,
                return_on_new_capital=0.05)
    base.update(kw)
    return TerminalReturn(**base)


def test_warning_quotes_whole_capital_when_it_governs():
    from vcc_valuations.dcf.terminal_return import _warnings_for
    # New-capital return sits below WACC; whole-capital return (10/100) sits above it.
    t = _tr(terminal_invested_capital=100.0)
    warns = [w for w in _warnings_for(t) if "exceeds" in w]
    assert len(warns) == 1
    assert "terminal return on whole capital 10.00% exceeds WACC 9.00% by 100bp" in warns[0]


def test_warning_falls_back_to_new_capital_without_a_capital_base():
    from vcc_valuations.dcf.terminal_return import _warnings_for
    t = _tr(return_on_new_capital=0.12)
    warns = [w for w in _warnings_for(t) if "exceeds" in w]
    assert len(warns) == 1
    assert "terminal return on new capital 12.00% exceeds WACC 9.00% by 300bp" in warns[0]
    assert "whole capital" not in warns[0]
