"""Item (e) sizing (16 Oct 2026): what option 1 does to WBC, with and without the D-60 payout cut.

Option 1 (draft in notes/bridge/bank_retained_equity_draft_2026-10-16.md): retained equity
compounds at the cost of equity (Ke) to the terminal date, and the terminal value is applied to
that compounded balance. Dividends and the explicit period are unchanged, so only the terminal
value moves. Annual compounding from each period end to the terminal date.

Usage:  PYTHONPATH=src python scripts/size_bank_retained_equity.py
"""

import dataclasses
from pathlib import Path

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.translator import build_bank_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ["orderly_convergence", "muddle_through", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]


def option1_vps(inp, res):
    """Value per share with retained equity compounding at Ke to the terminal date."""
    ke = inp.cost_of_equity
    g = inp.terminal_growth
    stub = inp.stub_years
    H = len(res.retained_by_period) - 1
    terminal_end = stub + H
    ends = [stub] + [stub + k for k in range(1, H + 1)]
    compounded = sum(r * (1.0 + ke) ** (terminal_end - e) for r, e in zip(res.retained_by_period, ends))
    new_closing = inp.book_equity + compounded
    from vcc_valuations.dcf.terminal_value import two_stage
    if res.terminal_form != "excess_return_convergence":
        raise ValueError("sizing expects the WBC convergence terminal")
    tv = two_stage(new_closing, res.terminal_roe, ke, g, res.convergence_years)
    pv_tv = tv * res.terminal_discount_factor
    claim = res.pv_explicit_dividends + pv_tv
    ordinary = claim - inp.at1_hybrid - inp.non_controlling_interests - inp.treasury_shares
    return ordinary / inp.shares_outstanding_m


def option1b_vps(inp, res):
    """Consistent variant: retained equity earns Ke as cash in the explicit years, received by
    shareholders as extra dividends (so it appears in NPAT and cash, not only in book equity).
    The principal stays in book equity and the terminal is unchanged."""
    ke = inp.cost_of_equity
    stub = inp.stub_years
    lengths = [stub] + [1.0] * (len(res.retained_by_period) - 1)
    balance = 0.0
    extra_pv = 0.0
    for p, (r, n_len, df) in enumerate(zip(res.retained_by_period, lengths, res.discount_factors)):
        extra_pv += ke * balance * n_len * df
        balance += r
    claim = res.total_equity_claim + extra_pv
    return (claim - inp.at1_hybrid - inp.non_controlling_interests - inp.treasury_shares) / inp.shares_outstanding_m


def run(scenario, cut_on):
    inp = build_bank_inputs_from_data(load_inputs(ROOT, scenario, "australian_major_banks", "wbc"), scenario)
    inp = dataclasses.replace(inp, constrain_payout_to_capital=cut_on)
    res = BankEngine().run(inp)
    return res.value_per_share, option1_vps(inp, res), res.capital_constraint_binds_from, option1b_vps(inp, res)


if __name__ == "__main__":
    print(f"{'scenario':36s} {'base':>8s} {'opt1':>8s} {'chg':>7s} | {'no-cut':>8s} {'opt1 no-cut':>11s} | D-60 effect base / opt1 | binds")
    for s in SCENARIOS:
        base, o1, binds, o1b = run(s, True)
        base_nc, o1_nc, _, o1b_nc = run(s, False)
        print(f"   1b (cash version): {o1b:8.2f} ({100*(o1b/base-1):+5.1f}%), D-60 effect {o1b-o1b_nc:+.2f}")
        cut_base = base - base_nc
        cut_o1 = o1 - o1_nc
        print(f"{s:36s} {base:8.2f} {o1:8.2f} {100*(o1/base-1):6.1f}% | {base_nc:8.2f} {o1_nc:11.2f} | "
              f"{cut_base:+7.2f} / {cut_o1:+7.2f} | {binds}")
