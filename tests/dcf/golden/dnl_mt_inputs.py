"""
DNL x Muddle Through resolved engine inputs, transcribed from the audited
workbook Assumptions sheet (dnl_muddle_through_valuation_v6_2026-06-25.xlsx).

This is the M1 stand-in for the ``linkage/`` + ``assumptions/`` layers (M2): it
hand-resolves what that pipeline will one day emit, so the engine can be proven
against the workbook oracle now. Every scalar carries its Assumptions-sheet cell
reference. The revenue-growth chain is reproduced explicitly (industry baseline
x geographic mix + Five-Forces company offset) rather than pasted as a scalar,
so the derivation is auditable.
"""

from __future__ import annotations

from vcc_valuations.assumptions.wacc import WaccBuild
from vcc_valuations.dcf.fcf_engine import EquityBridge, FcfEngineInputs


def _revenue_growth_chain() -> float:
    """Muddle Through nominal revenue growth (Assumptions B42), from the chain.

    industry volume  = a x mining_real + b                      (B23,B19,B24)
    industry pricing = w_infl x infl + w_gas x gas + productivity (B26,B18,B27,B20,B28)
    industry nominal = (1+vol)(1+price) - 1
    geo-mix          = DM_wt + EM_wt x EM_premium               (B33,B34,B35)
    net FF offset    = rivalry + mix + entrants + other         (B37..B40)
    company nominal  = industry_nominal x geo-mix + net_offset  (B42)
    """
    vol = 1.15 * 0.025 + 0.004
    price = 0.7 * 0.025 + 0.3 * 0.02 + 0.005
    industry_nominal = (1.0 + vol) * (1.0 + price) - 1.0
    geo_mix = 0.9 + 0.1 * 1.3
    net_offset = -0.003 - 0.001 + 0.0015 + 0.0
    return industry_nominal * geo_mix + net_offset


def _equity_bridge_adjustments_net() -> float:
    """Net Fertilisers-separation adjustments (Equity Bridge B24 = SUM B14:B23)."""
    declared_dividend = 81.4                      # B90: 4.6cps x 1,770m
    ph_aro_net = 126.0 - 82.0                      # B91 - B92
    ph_inventory = 80.0                            # B94
    restructure = 12.0                             # B95
    geelong = 35.0                                 # B96
    gibson_island = 97.0                           # B97
    transaction_costs = 11.0                       # B98
    perdaman = -145.0 * 0.50                        # B99 x B100
    ipf_distribution = -125.0 * 0.85               # B102 x B103
    ph_contingent = -100.0 * 0.30                  # B105 x B106
    return (
        declared_dividend + ph_aro_net + ph_inventory + restructure
        + geelong + gibson_island + transaction_costs
        + perdaman + ipf_distribution + ph_contingent
    )


def dnl_muddle_through_inputs() -> FcfEngineInputs:
    wacc = WaccBuild(
        risk_free_rate=0.043,        # B69
        equity_risk_premium=0.05,    # B70
        beta=0.95,                   # B71
        cost_of_debt_pretax=0.06,    # B72
        tax_rate=0.275,              # Tax Bridge D8 / B60 blended statutory
        equity_market_value=6390.0,  # B73
        debt_market_value=1260.8,    # B74
    )

    bridge = EquityBridge.from_anchor(
        net_debt_anchor=1260.8,               # B74
        period_a_years=55.0 / 365.0,          # B84 / 365
        operating_cash_flow_run_rate=500.0,   # B86
        capex_run_rate=256.0,                 # B87
        equity_bridge_adjustments_net=_equity_bridge_adjustments_net(),
        lease_liabilities=194.3,              # B108 (AASB 16, Approach A)
        shares_outstanding=1770.0,            # B81
        fx_rate=1.0,                          # AUD throughout
        market_reference_price=3.61,          # B110
    )

    return FcfEngineInputs(
        company_id="dnl",
        scenario_id="muddle_through",
        functional_currency="AUD",
        horizon_years=5,                      # B78
        stub_years=0.351,                     # B6 (128 days / 365)
        base_year_revenue=3400.0,             # B9
        revenue_growth=_revenue_growth_chain(),  # B42
        base_ebit_margin=0.141,               # B10
        margin_transformation=[0.006, 0.018, 0.02, 0.02, 0.02],   # B45..B49
        margin_gas_rolloff=[0.0, 0.0, -0.005, -0.01, -0.015],     # B52..B56
        stub_tax_rate=0.225,                  # B59
        tax_rate_glide=[0.225, 0.2375, 0.25, 0.2625, 0.275],       # Tax Bridge B12..B16
        da_pct_revenue=0.073,                 # B13
        capex_pct_stub=0.08,                  # B12 (transition)
        capex_pct=[0.08, 0.08, 0.07, 0.07, 0.07],  # B12 (Y1,Y2), B11 (Y3..Y5)
        delta_wc=[0.0] * 5,                   # B14 (neutral)
        delta_wc_stub=0.0,
        # The v6 workbook books no working capital and capitalises the grown
        # final-year FCFF. That is what this oracle is FOR: it pins the engine's
        # arithmetic against the audited spreadsheet as built. The live
        # data-driven path declares "normalised" instead — see
        # data/companies/dnl.yaml normalised_baseline.terminal_reinvestment.
        terminal_reinvestment="capitalise_last_fcff",
        wacc=wacc,
        terminal_growth=0.025,                # B77
        equity_bridge=bridge,
    )
