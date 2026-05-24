"""
Phase 3.5 smoke-test: end-to-end pipeline for DNL x each of the six scenarios.

Loads YAML inputs -> applies translator -> runs FCF DCF stub ->
prints a summary table. Surfaces any schema / data-shape issues
before Phase 4 expansion.

Usage:
    PYTHONPATH=src python scripts/run_smoke_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.translator import load_inputs, translate_to_assumption_set  # noqa: E402
from vcc_valuations.dcf.fcf_stub import run_fcf_dcf  # noqa: E402


SCENARIOS = [
    "muddle_through",
    "orderly_convergence",
    "stagflation_persists",
    "fragmentation",
    "disorderly_climate_crystallisation",
    "ai_productivity_lag",
]


def _fmt_aud_m(v: float) -> str:
    return f"AUD {v:,.0f}m"


def main() -> None:
    print("=" * 72)
    print("Phase 3.5 smoke-test: DNL x scenarios — FCF DCF stub")
    print("=" * 72)

    results = []
    for scenario_id in SCENARIOS:
        try:
            inputs = load_inputs(
                ROOT,
                scenario_id=scenario_id,
                archetype_id="industrial_explosives",
                company_id="dnl",
            )
        except Exception as e:
            print(f"\n[{scenario_id}] LOAD FAILED: {e}")
            continue

        aset = translate_to_assumption_set(inputs, horizon_years=5)
        result = run_fcf_dcf(aset)
        results.append(result)

        print(f"\n--- {scenario_id} ---")
        print(f"  Revenue base year: {_fmt_aud_m(aset.base_year_revenue)}")
        print(f"  Revenue year 5:    {_fmt_aud_m(result.revenue[-1])}")
        print(f"  EBIT margin y5:    {result.ebit_margin[-1]:.1%}")
        print(f"  FCF year 5:        {_fmt_aud_m(result.free_cash_flow[-1])}")
        print(f"  WACC:              {result.wacc:.2%}")
        print(f"  Terminal growth:   {result.terminal_growth:.2%}")
        print(f"  Enterprise value:  {_fmt_aud_m(result.enterprise_value)}")
        print(f"  Net debt:          {_fmt_aud_m(result.net_debt)}")
        print(f"  Equity value:      {_fmt_aud_m(result.equity_value)}")
        print(f"  Per share:         AUD {result.value_per_share:.2f}")
        print(f"  Terminal % of EV:  {result.terminal_share_of_ev:.1%}")
        if result.notes:
            print("  Notes:")
            for n in result.notes:
                print(f"    - {n}")
        print(f"  Drivers applied:   {len(aset.assumptions)}")

    # Summary table
    if results:
        print("\n" + "=" * 72)
        print("SUMMARY — Per-share values vs Muddle Through baseline")
        print("=" * 72)
        baseline = next(
            (r for r in results if r.scenario_id == "muddle_through"), None
        )
        baseline_vps = baseline.value_per_share if baseline else None

        print(f"{'Scenario':<36} {'EV (AUD m)':>14} {'Per share':>12} {'vs MT':>10}")
        print("-" * 72)
        for r in results:
            ev = f"{r.enterprise_value:,.0f}"
            vps = f"AUD {r.value_per_share:.2f}"
            if baseline_vps and r.value_per_share is not None:
                pct = (r.value_per_share - baseline_vps) / baseline_vps * 100
                vs_mt = f"{pct:+.1f}%"
            else:
                vs_mt = "—"
            print(f"{r.scenario_id:<36} {ev:>14} {vps:>12} {vs_mt:>10}")

    print("\nDone. Findings will be written to docs/phase_3_5_findings.md.")


if __name__ == "__main__":
    main()
