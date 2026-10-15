"""Item (e) sizing (16 Oct 2026): WBC with the payout cut on and off, read from the engine.

Option 1b (approved): retained equity earns the cost of equity (Ke) as cash in the explicit years,
received by shareholders as extra dividends (BankInputs.retained_earns_ke, default on). The
principal stays in book equity and the terminal is unchanged. The engine computes all of it.

The "D-60 effect" is the value with the payout cut minus the value without it. Without the cut,
the bank pays dividends that breach the CET1 target, so this comparison is a simplification.

Usage:  PYTHONPATH=src python scripts/size_bank_retained_equity.py
"""

import dataclasses
from pathlib import Path

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.translator import build_bank_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ["orderly_convergence", "muddle_through", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]


def run(scenario, cut_on, retained_on=True):
    inp = build_bank_inputs_from_data(load_inputs(ROOT, scenario, "australian_major_banks", "wbc"), scenario)
    inp = dataclasses.replace(inp, constrain_payout_to_capital=cut_on, retained_earns_ke=retained_on)
    res = BankEngine().run(inp)
    return res.value_per_share, res.capital_constraint_binds_from


if __name__ == "__main__":
    print(f"{'scenario':36s} {'before':>8s} {'now':>8s} {'chg':>7s} | {'no cut':>8s} | D-60 effect {'before':>8s} {'now':>8s} | binds")
    for s in SCENARIOS:
        now, binds = run(s, True)
        before, _ = run(s, True, retained_on=False)
        nocut_now, _ = run(s, False)
        nocut_before, _ = run(s, False, retained_on=False)
        pct = 100 * (now / before - 1)  # ssot-allow: percent display, not a register value
        print(f"{s:36s} {before:8.2f} {now:8.2f} {pct:6.1f}% | {nocut_now:8.2f} | "
              f"{before - nocut_before:+17.2f} {now - nocut_now:+8.2f} | {binds}")
