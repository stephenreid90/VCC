"""
Minimal Layer-5-and-6 translator for Phase 3.5 smoke test.

Takes:
- scenario YAML (data/scenarios/<id>.yaml)
- industry archetype YAML (data/industries/<id>.yaml)
- company position YAML (data/companies/<id>.yaml)
- impact matrix YAML (data/impact_matrix/by_industry/<id>.yaml)
- base-year financials YAML (data/financials/<id>.yaml)

Produces a minimal AssumptionSet — driver-keyed map of year-by-year
trajectories — sufficient to feed a smoke-test DCF.

This is the Phase 3.5 STUB, not the Step 6 production translator.
Key simplifications:
- Translation rules hardcoded here (not in data/translation_rules/).
- Time profile applied as linear_through_horizon for all drivers.
- No derived-driver computation (just primary drivers).
- No consistency-rules check (section 11.4.2).
- No segment aggregation (DNL is single-segment so this is fine).
- Hardcoded driver groups; no lookup against Layer 4 catalogue.

Findings will inform Step 6 production translator design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from vcc_valuations.schemas import (
    CompanyPositionFile,
    ImpactMatrix,
    IndustryArchetypeFile,
    ScenarioFile,
)
from vcc_valuations.schemas.common import Direction, Magnitude, Confidence


# ----------------------------------------------------------------------
# Translation rules
#
# Direction x magnitude -> numeric delta, by driver-group type.
# Hardcoded for the smoke test; the production version belongs in
# data/translation_rules/ per section 11.2 of the architecture spec.
# ----------------------------------------------------------------------

# Volume / revenue growth deltas (% per annum, change from baseline)
VOLUME_DELTA_PCT = {
    (Direction.NEGATIVE, Magnitude.LARGE): -7.0,
    (Direction.NEGATIVE, Magnitude.MODERATE): -3.5,
    (Direction.NEGATIVE, Magnitude.SMALL): -1.5,
    (Direction.NEUTRAL, Magnitude.SMALL): 0.0,
    (Direction.NEUTRAL, Magnitude.MODERATE): 0.0,
    (Direction.NEUTRAL, Magnitude.LARGE): 0.0,
    (Direction.POSITIVE, Magnitude.SMALL): 1.5,
    (Direction.POSITIVE, Magnitude.MODERATE): 3.5,
    (Direction.POSITIVE, Magnitude.LARGE): 7.0,
}

# Margin-point deltas (percentage points of margin change)
MARGIN_DELTA_PP = {
    (Direction.NEGATIVE, Magnitude.LARGE): -3.5,
    (Direction.NEGATIVE, Magnitude.MODERATE): -1.5,
    (Direction.NEGATIVE, Magnitude.SMALL): -0.5,
    (Direction.NEUTRAL, Magnitude.SMALL): 0.0,
    (Direction.NEUTRAL, Magnitude.MODERATE): 0.0,
    (Direction.NEUTRAL, Magnitude.LARGE): 0.0,
    (Direction.POSITIVE, Magnitude.SMALL): 0.5,
    (Direction.POSITIVE, Magnitude.MODERATE): 1.5,
    (Direction.POSITIVE, Magnitude.LARGE): 3.5,
}

# Rate deltas in basis points (for risk-free rate, ERP, etc.)
RATE_DELTA_BPS = {
    (Direction.NEGATIVE, Magnitude.LARGE): -200,
    (Direction.NEGATIVE, Magnitude.MODERATE): -75,
    (Direction.NEGATIVE, Magnitude.SMALL): -25,
    (Direction.NEUTRAL, Magnitude.SMALL): 0,
    (Direction.NEUTRAL, Magnitude.MODERATE): 0,
    (Direction.NEUTRAL, Magnitude.LARGE): 0,
    (Direction.POSITIVE, Magnitude.SMALL): 25,
    (Direction.POSITIVE, Magnitude.MODERATE): 75,
    (Direction.POSITIVE, Magnitude.LARGE): 200,
}

# Map driver id -> rule table
DRIVER_RULE_TABLE = {
    "volume_growth": ("volume", VOLUME_DELTA_PCT),
    "price_mix": ("volume", VOLUME_DELTA_PCT),
    "gross_margin": ("margin", MARGIN_DELTA_PP),
    "ebit_margin": ("margin", MARGIN_DELTA_PP),
    "sga_pct_revenue": ("margin", MARGIN_DELTA_PP),
    "rd_intensity": ("margin", MARGIN_DELTA_PP),
    "input_cost_pass_through": ("margin", MARGIN_DELTA_PP),
    "maintenance_capex_pct_revenue": ("margin", MARGIN_DELTA_PP),
    "growth_capex_pct_revenue": ("margin", MARGIN_DELTA_PP),
    "working_capital_days": ("margin", MARGIN_DELTA_PP),
    "risk_free_rate": ("rate", RATE_DELTA_BPS),
    "equity_risk_premium": ("rate", RATE_DELTA_BPS),
    "beta": ("rate", RATE_DELTA_BPS),
    "country_risk_premium": ("rate", RATE_DELTA_BPS),
    "terminal_growth_rate": ("rate", RATE_DELTA_BPS),
    "terminal_roic": ("rate", RATE_DELTA_BPS),
    "fade_period_length": ("rate", RATE_DELTA_BPS),
}


# ----------------------------------------------------------------------
# Data classes for the smoke-test AssumptionSet
#
# Simplified vs the full schemas.AssumptionSet so the smoke test stays
# easy to read. Production should use the full pydantic model.
# ----------------------------------------------------------------------


@dataclass
class TrajectoryAssumption:
    driver_id: str
    base_value: float
    annual_delta: float
    annual_values: List[float] = field(default_factory=list)
    confidence: Optional[Confidence] = None
    direction: Optional[Direction] = None
    magnitude: Optional[Magnitude] = None
    rationale: Optional[str] = None
    rule_applied: Optional[str] = None


@dataclass
class SmokeAssumptionSet:
    company_id: str
    scenario_id: str
    horizon_years: int
    base_year_revenue: float
    base_year_ebit_margin: float
    base_year_capex_pct_revenue: float
    base_year_net_debt: float
    base_year_shares_outstanding: float
    base_year_tax_rate: float
    assumptions: Dict[str, TrajectoryAssumption] = field(default_factory=dict)


# ----------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_inputs(
    repo_root: Path,
    scenario_id: str,
    archetype_id: str,
    company_id: str,
) -> dict:
    """Load and validate all inputs."""
    scenario_path = repo_root / "data" / "scenarios" / f"{scenario_id}.yaml"
    archetype_path = repo_root / "data" / "industries" / f"{archetype_id}.yaml"
    company_path = repo_root / "data" / "companies" / f"{company_id}.yaml"
    matrix_path = (
        repo_root / "data" / "impact_matrix" / "by_industry" / f"{archetype_id}.yaml"
    )
    financials_path = repo_root / "data" / "financials" / f"{company_id}.yaml"

    scenario = ScenarioFile.model_validate(_load(scenario_path)).scenario
    if archetype_path.exists():
        # All archetype files — industrial, bank and biopharma — now validate against the
        # §7.4-v2 IndustryArchetypeFile (bank/biopharma carry archetype_class, the v2 five-
        # forces shape and archetype-specific blocks; industrial keeps the original shape).
        archetype = IndustryArchetypeFile.model_validate(_load(archetype_path)).industry_archetype
    else:
        # Segment-level-valuation companies (e.g. CSL) have no single consolidated archetype
        # file — archetypes are resolved per segment from the company file, and the segment-
        # FCFF engine reads normalised_baseline, so nothing needs a typed archetype here.
        archetype = None
    company_raw = _load(company_path)
    company = CompanyPositionFile.model_validate(company_raw).company_position
    matrix = ImpactMatrix.model_validate(_load(matrix_path)) if matrix_path.exists() else None
    financials = _load(financials_path)

    return {
        "scenario": scenario,
        "archetype": archetype,
        "company": company,
        "matrix": matrix,
        "financials": financials,
        "company_raw": company_raw,
    }


def resolve_normalised_baseline(inputs: dict) -> dict:
    """Join the layer-2 method/selection block with the layer-1 observed inputs.

    Layer 2 (judgement: margins, net debt, tax, the beta selection) lives in
    ``data/companies/<id>.yaml`` under ``normalised_baseline``. Layer 1 (observed
    market data: risk-free rate, measured beta, peer dataset, equity and debt
    market values) stays in ``data/financials/<id>.yaml`` under
    ``wacc_observed_inputs``. See ``design/single_source_of_truth.md`` §3.

    Returns the joined mapping in the legacy shape, so callers that expect a
    ``wacc_build`` (DNL) or ``cost_of_equity_build`` (CSL, which discounts at the
    cost of equity) sub-mapping keep working. Falls back to the pre-migration
    location for any company not yet split.
    """
    financials = inputs["financials"]
    norm = dict((inputs.get("company_raw") or {}).get("normalised_baseline") or {})
    if not norm:
        return dict(financials.get("normalised_baseline") or {})
    # WACC discipline (DNL): observed capital-structure + rate inputs joined with
    # the method/selection block into the legacy wacc_build shape.
    observed = financials.get("wacc_observed_inputs") or {}
    method = dict(norm.pop("wacc_method", None) or {})
    if observed or method:
        norm["wacc_build"] = {**observed, **method}
    # Cost-of-equity discipline (CSL): discounts FCFF at Ke, so there is no
    # capital-structure weighting. Its observed market inputs (coe_observed_inputs)
    # rejoin its method/selection block (coe_method) into cost_of_equity_build.
    coe_observed = financials.get("coe_observed_inputs") or {}
    coe_method = dict(norm.pop("coe_method", None) or {})
    if coe_observed or coe_method:
        norm["cost_of_equity_build"] = {**coe_observed, **coe_method}
    return norm


def build_wacc_from_inputs(inputs: dict, default_tax: float = 0.30):
    """Assemble a ``WaccBuild`` from the resolved layer-1 / layer-2 data.

    The single data-driven discount rate for WACC-discipline companies (DNL):
    beta and ERP come from the joined ``wacc_build`` (layer-2 selection over the
    layer-1 observed inputs), the E/V weights from the methodology-§5.3-anchored
    equity / debt market values. Returns ``None`` for cost-of-equity companies
    (banks / CSL), which carry no ``wacc_build``.
    """
    from vcc_valuations.assumptions.wacc import WaccBuild

    norm = resolve_normalised_baseline(inputs)
    wb = norm.get("wacc_build")
    if not wb:
        return None
    return WaccBuild(
        risk_free_rate=wb["risk_free_rate"],
        equity_risk_premium=wb["equity_risk_premium"],
        beta=wb["beta"],
        cost_of_debt_pretax=wb["cost_of_debt_pretax"],
        tax_rate=norm.get("tax_rate", default_tax),
        equity_market_value=wb["equity_market_value"],
        debt_market_value=wb["debt_market_value"],
    )


def tax_bridge_from_data(inputs: dict):
    """The Tax Bridge as a fully-traceable :class:`Derivation` (workbook Tax Bridge).

    From the yellow-cell inputs (effective rate, per-jurisdiction statutory rates,
    glide fractions) derives, at V6 granularity: the per-region contributions
    (D5-D7, weight x statutory where the WEIGHT comes from
    ``geographic_concentration``), the blended statutory rate (D8), and the
    per-year applied-tax glide (B12-B16, the effective rate closing the gap to
    the blended statutory over the horizon). ``None`` if no ``tax_bridge``.

    The glide and D8 were previously STORED in ``engine_overlays``; they are now
    derived here so a change to any statutory rate flows through automatically.
    """
    from vcc_valuations.derivation import DerivationBuilder

    company_raw = inputs.get("company_raw") or {}
    nb = company_raw.get("normalised_baseline") or {}
    tb = nb.get("tax_bridge")
    if not tb:
        return None

    regions = _geographic_regions(company_raw)
    rate_by_region = tb["statutory_rate_by_region"]
    b = DerivationBuilder("tax_bridge")

    contributions = []
    for i, r in enumerate(regions):
        geo = r["geo"]
        weight = r["share_of_revenue"]
        rate = rate_by_region[geo]
        contributions.append(
            b.step(
                f"D{5 + i}", f"{geo} tax contribution", weight * rate,
                "revenue_weight * statutory_rate",
                {"revenue_weight": weight, "statutory_rate": rate},
                cell=f"D{5 + i}", units="%",
            )
        )
    blended = b.step(
        "D8", "Blended statutory rate", sum(contributions),
        "sum of jurisdictional contributions",
        {f"D{5 + i}": c for i, c in enumerate(contributions)}, cell="D8", units="%",
    )

    effective = tb["effective_tax_rate"]
    for i, frac in enumerate(tb["glide_fractions"], start=1):
        b.step(
            f"B{11 + i}", f"FY{26 + i} applied tax rate (Y{i})",
            effective + (blended - effective) * frac,
            "effective + (blended - effective) * fraction",
            {"effective": effective, "blended": blended, "fraction": frac},
            cell=f"B{11 + i}", units="%",
        )
    return b.build(result_key="D8")


def wacc_build_from_data(inputs: dict):
    """The WACC build as a traceable :class:`Derivation` (workbook WACC Build).

    Thin bridge from the data-driven :class:`WaccBuild` to its full six-row
    derivation (B8/B13/B18/B19/B20/B23). ``None`` for cost-of-equity companies
    (banks / CSL) which carry no ``wacc_build``.
    """
    wacc = build_wacc_from_inputs(inputs)
    return None if wacc is None else wacc.derivation()


def equity_bridge_from_data(inputs: dict, scenario_id: str):
    """The equity bridge as a traceable :class:`Derivation` (workbook Equity Bridge).

    Assembles the engine input from data, runs the DCF for the enterprise value,
    then traces the Period-A net-debt walk (B6-B11) and the per-share bridge
    (B27-B37). The headline (B33) ties the engine's ``value_per_share``.
    """
    from vcc_valuations.dcf.fcf_engine import FcfEngine

    inp = build_engine_inputs_from_data(inputs, scenario_id)
    result = FcfEngine().run(inp)
    return inp.equity_bridge.derivation(result.enterprise_value)


def equity_bridge_adjustments_net_from_data(company_raw: dict):
    """Sum the structured ``equity_bridge_adjustments`` (methodology §4.2).

    Returns the net AUD-m figure the equity bridge subtracts from enterprise
    value: subtract-from-equity items add to the net, add-to-equity receivables
    (probability-weighted) reduce it. ``None`` if the company carries no list.

    Enforces the §4.3 validator: every adjustment MUST carry an explicit
    ``on_balance_sheet_at_anchor`` flag (raises ``ValueError`` otherwise) so a
    provision is never silently double-counted.
    """
    nb = (company_raw or {}).get("normalised_baseline") or {}
    adjustments = nb.get("equity_bridge_adjustments")
    if not adjustments:
        return None
    net = 0.0
    for a in adjustments:
        if "on_balance_sheet_at_anchor" not in a:
            raise ValueError(
                f"equity_bridge_adjustment {a.get('id', '?')!r} lacks "
                f"on_balance_sheet_at_anchor (methodology §4.3)"
            )
        treatment = a.get("treatment")
        amount = a["amount_aud_m"]
        if treatment == "add_back_in_full":
            magnitude = amount
        elif treatment == "add_back_gap_only":
            magnitude = amount - a.get("provided_for_at_anchor_aud_m", 0.0)
        elif treatment == "probability_weighted":
            magnitude = a.get("expected_value_aud_m", amount * a["probability"])
        else:
            raise ValueError(f"unknown treatment {treatment!r} for {a.get('id')}")
        sign = 1.0 if a["direction"] == "subtract_from_equity" else -1.0
        net += sign * magnitude
    return net


def engine_overlays_from_data(company_raw: dict, scenario_id: str):
    """Per-year engine overlays for a scenario (methodology §11), RESOLVED.

    ``engine_overlays`` is stored as a ``baseline`` operating build (the Muddle
    Through v6 per-year glides) plus per-scenario ``by_scenario`` deltas. This
    resolver applies the deltas as a PARALLEL SHIFT across the explicit years
    (owner decision 12 Aug 2026): ``margin_delta_pp`` is added to every explicit
    year's ``margin_transformation`` and ``capex_delta_pp`` to every explicit
    year's ``capex_pct``; ``terminal_growth`` is taken absolutely. The stub (base
    year) is left unshifted. Returns the resolved mapping with the same keys
    consumers already expect (``base_ebit_margin``, ``margin_transformation``,
    ``margin_gas_rolloff``, ``capex_pct_stub``, ``capex_pct``, ``da_pct_revenue``,
    ``terminal_growth``), or ``None`` if the scenario is absent.
    """
    nb = (company_raw or {}).get("normalised_baseline") or {}
    overlays = nb.get("engine_overlays") or {}
    base = overlays.get("baseline")
    scen = (overlays.get("by_scenario") or {}).get(scenario_id)
    if base is None or scen is None:
        return None
    margin_delta = scen.get("margin_delta_pp", 0.0)
    capex_delta = scen.get("capex_delta_pp", 0.0)
    return {
        "base_ebit_margin": base["base_ebit_margin"],
        "margin_transformation": [x + margin_delta for x in base["margin_transformation"]],
        "margin_gas_rolloff": list(base["margin_gas_rolloff"]),
        "capex_pct_stub": base["capex_pct_stub"],
        "capex_pct": [x + capex_delta for x in base["capex_pct"]],
        "da_pct_revenue": base["da_pct_revenue"],
        "terminal_growth": scen["terminal_growth"],
    }


def _geographic_regions(company_raw: dict) -> list:
    """The segment-level geographic-concentration regions (share-of-revenue).

    DNL is single-segment; returns the first segment's
    ``risk_exposures.geographic_concentration.regions`` list, or ``[]``.
    """
    cp = (company_raw or {}).get("company_position") or {}
    for seg in cp.get("segments") or []:
        gc = (seg.get("risk_exposures") or {}).get("geographic_concentration") or {}
        regions = gc.get("regions")
        if regions:
            return regions
    return []


def revenue_growth_chain_from_data(inputs: dict, scenario_id: str):
    """The §11 revenue-growth chain as a fully-traceable :class:`Derivation`.

    Reproduces the workbook Assumptions B18-B42 build at full V6 granularity:
    the yellow-cell inputs come from ``revenue_growth_chain[scenario_id]`` in the
    data; every DERIVED row is computed here and exposed as a named, formula-
    annotated step (never stored back into the data). The eight derived rows,
    with their workbook cells:

        B25 industry volume growth   = a x mining_real + b
        B29 industry pricing growth  = w_infl x DM_inflation + w_gas x gas + prod
        B30 industry nominal growth  = (1 + volume)(1 + pricing) - 1
        B33 DM weighting             = sum of developed-market revenue shares
        B34 EM weighting             = sum of the remaining revenue shares
        B36 geo-mix multiplier       = DM_weight + EM_weight x EM_premium
        B41 net company offset       = rivalry + product_mix + entrants + other
        B42 company nominal growth   = industry_nominal x geo_mix + net_offset

    B33/B34 are derived from the segment ``geographic_concentration`` (so the
    workbook's hardcoded DM/EM weighting becomes an auditable step), which is
    finer than V6. Returns ``None`` if the company carries no chain for the scenario.
    """
    from vcc_valuations.derivation import DerivationBuilder

    company_raw = inputs.get("company_raw") or {}
    nb = company_raw.get("normalised_baseline") or {}
    rgc = nb.get("revenue_growth_chain") or {}
    shared = rgc.get("shared") or {}
    scen = (rgc.get("by_scenario") or {}).get(scenario_id)
    if not shared or not scen:
        return None

    ib = shared["industry_structure"]     # scenario-invariant coefficients
    macro = scen["macro"]                 # per-scenario B18/B19/B20
    co = shared["company_offset"]         # scenario-invariant company offset
    b = DerivationBuilder(f"revenue_growth_chain[{scenario_id}]")

    a = ib["volume_coefficient_a"]
    mining = macro["global_mining_real_growth"]
    b_const = ib["volume_constant_b"]
    volume = b.step(
        "B25", "Industry volume growth", a * mining + b_const,
        "a * mining_real_growth + b",
        {"a": a, "mining_real_growth": mining, "b": b_const}, cell="B25", units="%",
    )

    w_infl = ib["pricing_weight_inflation"]
    dm_infl = macro["dm_inflation"]
    w_gas = ib["pricing_weight_gas"]
    gas = macro["gas_price_growth"]
    prod = ib["productivity_sharing"]
    pricing = b.step(
        "B29", "Industry pricing growth", w_infl * dm_infl + w_gas * gas + prod,
        "w_infl * DM_inflation + w_gas * gas_growth + productivity",
        {"w_infl": w_infl, "DM_inflation": dm_infl, "w_gas": w_gas,
         "gas_growth": gas, "productivity": prod}, cell="B29", units="%",
    )

    industry_nominal = b.step(
        "B30", "Industry nominal growth", (1.0 + volume) * (1.0 + pricing) - 1.0,
        "(1 + volume)(1 + pricing) - 1",
        {"volume": volume, "pricing": pricing}, cell="B30", units="%",
    )

    developed = set(co["developed_market_regions"])
    regions = _geographic_regions(company_raw)
    dm_weight = b.step(
        "B33", "DM weighting", sum(r["share_of_revenue"] for r in regions if r["geo"] in developed),
        "sum of developed-market revenue shares",
        {r["geo"]: r["share_of_revenue"] for r in regions if r["geo"] in developed},
        cell="B33", units="%",
    )
    em_weight = b.step(
        "B34", "EM weighting", sum(r["share_of_revenue"] for r in regions if r["geo"] not in developed),
        "sum of the remaining (emerging-market) revenue shares",
        {r["geo"]: r["share_of_revenue"] for r in regions if r["geo"] not in developed},
        cell="B34", units="%",
    )
    em_premium = co["em_growth_premium"]
    geo_mix = b.step(
        "B36", "Geographic-mix multiplier", dm_weight + em_weight * em_premium,
        "DM_weight + EM_weight * EM_premium",
        {"DM_weight": dm_weight, "EM_weight": em_weight, "EM_premium": em_premium},
        cell="B36",
    )

    ff = co["five_forces_offset"]
    net_offset = b.step(
        "B41", "Net company-position offset",
        ff["rivalry_competitive_position"] + ff["rivalry_product_mix"]
        + ff["new_entrants_pipeline_uplift"] + ff["buyer_supplier_substitutes"],
        "rivalry + product_mix + new_entrants + buyer_supplier_substitutes",
        dict(ff), cell="B41", units="%",
    )

    b.step(
        "B42", "Company nominal revenue growth", industry_nominal * geo_mix + net_offset,
        "industry_nominal * geo_mix_multiplier + net_offset",
        {"industry_nominal": industry_nominal, "geo_mix_multiplier": geo_mix,
         "net_offset": net_offset}, cell="B42", units="%",
    )

    return b.build(result_key="B42")


def revenue_growth_from_data(inputs: dict, scenario_id: str):
    """Company nominal revenue growth (workbook B42) for a scenario.

    Thin wrapper over :func:`revenue_growth_chain_from_data` returning just the
    headline scalar for the engine assembler; ``None`` if there is no chain.
    """
    chain = revenue_growth_chain_from_data(inputs, scenario_id)
    return None if chain is None else chain.result


def build_engine_inputs_from_data(inputs: dict, scenario_id: str):
    """Assemble the whole ``FcfEngineInputs`` for one company x scenario from data.

    This is the M2 payload: it composes the already-data-driven pieces
    (``build_wacc_from_inputs``, ``engine_overlays_from_data``,
    ``equity_bridge_adjustments_net_from_data``, ``revenue_growth_from_data``)
    with the migrated valuation base / timing scalars and the equity-bridge
    run-rates, so the engine input carries ZERO hand-typed constants — every
    field traces to a data file. The net-debt anchor and issued share count come
    from the §5.3-anchored ``data/financials/<id>.yaml`` (31 Mar 2026), not
    re-typed here.

    DNL (single-segment industrial, WACC discipline) only for now; segment FCFF
    (CSL / M3) is a separate assembler.
    """
    from vcc_valuations.dcf.fcf_engine import EquityBridge, FcfEngineInputs

    company = inputs["company"]
    company_raw = inputs.get("company_raw") or {}
    financials = inputs["financials"]
    nb = company_raw.get("normalised_baseline") or {}

    wacc = build_wacc_from_inputs(inputs)
    if wacc is None:
        raise ValueError(
            f"{company.id}: no data-driven WACC (build_engine_inputs_from_data "
            "handles WACC-discipline companies only; banks / CSL use Ke / M3)."
        )
    overlays = engine_overlays_from_data(company_raw, scenario_id)
    if overlays is None:
        raise ValueError(f"{company.id}: no engine_overlays for scenario {scenario_id!r}.")
    revenue_growth = revenue_growth_from_data(inputs, scenario_id)
    if revenue_growth is None:
        raise ValueError(f"{company.id}: no revenue_growth_chain for scenario {scenario_id!r}.")
    adjustments_net = equity_bridge_adjustments_net_from_data(company_raw)

    # Applied tax: effective rate (stub) + the derived effective->statutory glide.
    tax = tax_bridge_from_data(inputs)
    if tax is None:
        raise ValueError(f"{company.id}: no tax_bridge.")
    stub_tax_rate = nb["tax_bridge"]["effective_tax_rate"]
    tax_rate_glide = [tax[f"B{11 + i}"].value for i in range(1, nb["horizon_years"] + 1)]

    rr = nb["equity_bridge_run_rates"]
    net_debt_anchor = financials["derived_metrics"]["net_debt"]                 # §5.3 anchor, 31 Mar 2026
    shares_outstanding = financials["share_statistics"]["shares_outstanding"] / 1_000_000
    reporting_ccy = financials.get("reporting_currency")
    functional_ccy = (company_raw.get("company_position") or {}).get(
        "functional_currency", reporting_ccy
    )
    # Single reporting currency for DNL (AUD functional == AUD reporting); FX is
    # applied only at the per-share line and is 1.0 when the two agree.
    fx_rate = 1.0 if functional_ccy == reporting_ccy else 1.0

    bridge = EquityBridge.from_anchor(
        net_debt_anchor=net_debt_anchor,
        period_a_years=rr["period_a_days"] / 365.0,
        operating_cash_flow_run_rate=rr["operating_cash_flow_run_rate"],
        capex_run_rate=rr["capex_run_rate"],
        equity_bridge_adjustments_net=adjustments_net,
        lease_liabilities=rr["lease_liabilities"],
        shares_outstanding=shares_outstanding,
        fx_rate=fx_rate,
        market_reference_price=rr["market_reference_price"],
    )

    return FcfEngineInputs(
        company_id=company.id,
        scenario_id=scenario_id,
        functional_currency=functional_ccy,
        horizon_years=nb["horizon_years"],
        stub_years=nb["stub_years"],
        base_year_revenue=nb["base_year_revenue"],
        revenue_growth=revenue_growth,
        base_ebit_margin=overlays["base_ebit_margin"],
        margin_transformation=overlays["margin_transformation"],
        margin_gas_rolloff=overlays["margin_gas_rolloff"],
        stub_tax_rate=stub_tax_rate,
        tax_rate_glide=tax_rate_glide,
        da_pct_revenue=overlays["da_pct_revenue"],
        capex_pct_stub=overlays["capex_pct_stub"],
        capex_pct=overlays["capex_pct"],
        wacc=wacc,
        terminal_growth=overlays["terminal_growth"],
        equity_bridge=bridge,
    )


def build_bank_inputs_from_data(inputs: dict, scenario_id: str):
    """Assemble ``BankInputs`` for one bank x scenario from data (methodology §15).

    Resolves the bank operating build from ``normalised_baseline.bank_build``:
    the AIEA/NIM chain (industry anchor + company offset + per-scenario macro
    deltas), the per-year overlays (NIM / cost-to-income / credit-loss glides,
    parallel-shifted per scenario), and the terminal ROE-fade inputs. The cost of
    equity comes from the joined ``cost_of_equity_build`` (Rf + beta x ERP), held
    constant across scenarios (single-Ke discipline, §15.2(d)). Zero derived values
    are read from data; every derived quantity is computed by the engine.
    """
    from vcc_valuations.dcf.bank_engine import BankInputs

    company = inputs["company"]
    company_raw = inputs.get("company_raw") or {}
    nb = company_raw.get("normalised_baseline") or {}
    bb = nb.get("bank_build")
    if bb is None:
        raise ValueError(f"{company.id}: no bank_build block (build_bank_inputs_from_data "
                         "handles bank-archetype companies only).")

    # Cost of equity (single Ke, held across scenarios).
    coe = resolve_normalised_baseline(inputs).get("cost_of_equity_build") or {}
    rf = coe.get("risk_free_rate")
    erp = coe.get("equity_risk_premium")
    beta = coe.get("beta", coe.get("beta_selected"))
    if rf is None or erp is None or beta is None:
        raise ValueError(f"{company.id}: incomplete cost_of_equity_build (need rf, ERP, beta).")
    ke = rf + beta * erp

    timing = bb["timing"]
    chain = bb["aiea_nim_chain"]
    shared = chain["shared"]
    macro = chain["by_scenario"].get(scenario_id)
    overlays = bb["overlays"]
    base = overlays["baseline"]
    scen = overlays["by_scenario"].get(scenario_id)
    if macro is None or scen is None:
        raise ValueError(f"{company.id}: no bank scenario {scenario_id!r}.")

    # AIEA growth: industry anchor + scenario delta + company offset (Five Forces).
    aiea_growth = (shared["industry"]["aiea_growth"] + macro.get("aiea_growth_delta", 0.0)
                   + shared["company_offset"]["aiea_growth_offset"])

    # Per-year glides, parallel-shifted per scenario.
    nim_shift = macro.get("nim_delta_bps", 0) / 10000.0
    nim_applied = [x + nim_shift for x in base["nim_applied"]]
    cti_shift = scen["y5_cost_to_income"] - base["cost_to_income"][-1]
    cost_to_income = [x + cti_shift for x in base["cost_to_income"]]
    cl_shift = scen.get("credit_loss_delta_bps", 0) / 10000.0
    credit_loss_rate = [x + cl_shift for x in base["credit_loss_rate"]]

    anchors = bb["balance_sheet_anchors"]
    drivers = bb["forecast_drivers"]
    income = bb["income_anchors_1h26"]

    return BankInputs(
        company_id=company.id,
        scenario_id=scenario_id,
        stub_years=timing["stub_years"],
        horizon_years=timing["horizon_years"],
        aiea_y1_time_factor=timing["aiea_y1_time_factor"],
        aiea_anchor=anchors["aiea_1h26_average"],
        book_equity=anchors["book_equity"],
        at1_hybrid=anchors["at1_hybrid"],
        non_controlling_interests=anchors["non_controlling_interests"],
        treasury_shares=anchors["treasury_shares"],
        shares_outstanding_m=anchors["shares_outstanding_m"],
        non_interest_income_1h=income["non_interest_income"],
        aiea_growth=aiea_growth,
        non_interest_income_growth=drivers["non_interest_income_growth"],
        avg_loans_pct_aiea=drivers["avg_loans_pct_aiea"],
        effective_tax_rate=drivers["effective_tax_rate"],
        dividend_payout_ratio=drivers["dividend_payout_ratio"],
        nim_applied=nim_applied,
        cost_to_income=cost_to_income,
        credit_loss_rate=credit_loss_rate,
        cost_of_equity=ke,
        terminal_roe=scen["terminal_roe"],
        terminal_growth=scen["terminal_growth"],
    )


def build_segment_inputs_from_data(inputs: dict, scenario_id: str):
    """Assemble ``SegmentInputs`` for one segment-level company x scenario (M3).

    Segment FY25 revenue / operating-result margin are the layer-1 observed anchors in
    ``data/financials/<id>.yaml``; the layer-2 drivers (per-segment growth path + margin
    uplift, corporate build, terminal, tax) come from ``normalised_baseline.segment_fcff``.
    Ke = Rf + beta x ERP from the joined ``cost_of_equity_build`` (single rate, held across
    scenarios). Zero derived values are read from data.
    """
    from vcc_valuations.dcf.segment_engine import SegmentInputs, SegmentSpec

    company = inputs["company"]
    company_raw = inputs.get("company_raw") or {}
    nb = company_raw.get("normalised_baseline") or {}
    sf = nb.get("segment_fcff")
    financials = inputs["financials"]
    if sf is None:
        raise ValueError(f"{company.id}: no segment_fcff block (build_segment_inputs_from_data "
                         "handles segment-level-valuation companies only).")
    scen = sf["by_scenario"].get(scenario_id)
    if scen is None:
        raise ValueError(f"{company.id}: no segment scenario {scenario_id!r}.")

    coe = resolve_normalised_baseline(inputs).get("cost_of_equity_build") or {}
    rf = coe.get("risk_free_rate"); erp = coe.get("equity_risk_premium")
    beta = coe.get("beta", coe.get("beta_selected"))
    if rf is None or erp is None or beta is None:
        raise ValueError(f"{company.id}: incomplete cost_of_equity_build.")
    ke = rf + beta * erp

    horizon = sf["timing"]["horizon_years"]
    # per-segment growth path (Behring is an explicit path; the others a flat CAGR).
    def growth_path(seg_name):
        if f"{_seg_key(seg_name)}_growth" in scen:
            return list(scen[f"{_seg_key(seg_name)}_growth"])
        cagr = scen[f"{_seg_key(seg_name)}_cagr"]
        return [cagr] * (horizon + 1)

    segs = []
    for s in financials["segments"]:
        name = s["segment"]
        segs.append(SegmentSpec(
            name=name,
            fy25_revenue=s["fy25_revenue"],
            fy25_or_margin=s["fy25_or_margin"],
            growth_path=growth_path(name),
            margin_uplift_cum=scen[f"{_seg_key(name)}_margin_uplift"],
        ))

    corp = sf["corporate"]; drv = sf["drivers"]; anch = sf["anchors"]
    return SegmentInputs(
        company_id=company.id, scenario_id=scenario_id, horizon_years=horizon,
        segments=segs,
        corporate_fy25=corp["unallocated_fy25"], corporate_growth=corp["unallocated_growth"],
        net_interest_fy25=corp["net_interest_fy25"], net_interest_decline=corp["net_interest_decline"],
        capex_pct_revenue=drv["capex_pct_revenue"], da_pct_revenue=drv["da_pct_revenue"],
        wc_change_pct_revenue_change=drv["wc_change_pct_revenue_change"],
        terminal_capex_pct_revenue=drv["terminal_capex_pct_revenue"],
        terminal_ebit_margin=scen["terminal_ebit_margin"], terminal_growth=scen["terminal_growth"],
        tax_rate=scen["tax_rate"], cost_of_equity=ke,
        net_debt=anch["net_debt"], restructuring_cash_to_come=anch["restructuring_cash_to_come"],
        shares_outstanding_m=anch["shares_outstanding_m"], fx_aud_per_usd=sf["fx_aud_per_usd"],
    )


def _seg_key(segment_name: str) -> str:
    """Map a segment id (``csl_behring``) to its driver key stem (``behring``)."""
    return segment_name.split("_")[-1]


# ----------------------------------------------------------------------
# Translator
# ----------------------------------------------------------------------


def translate_to_assumption_set(
    inputs: dict, horizon_years: int = 5
) -> SmokeAssumptionSet:
    """Apply impact matrix to base-year financials -> SmokeAssumptionSet."""
    scenario = inputs["scenario"]
    company = inputs["company"]
    matrix = inputs["matrix"]
    financials = inputs["financials"]

    # Find the matrix entry for this scenario.
    matrix_entry = None
    for entry in matrix.matrix:
        if entry.scenario == scenario.id:
            matrix_entry = entry
            break
    if matrix_entry is None:
        raise ValueError(
            f"No matrix entry found for scenario {scenario.id} in archetype "
            f"{matrix.industry}."
        )

    # Extract base-year anchors from financials (units: AUD millions).
    income = financials["income_statement"]["ttm_to_2026_03_31"]
    derived = financials["derived_metrics"]
    bs_total = financials["balance_sheet"]
    share_stats = financials["share_statistics"]

    # Layer-2 judgement joined with layer-1 observed inputs; prefer these over
    # the as-reported figures. Rationale for each sits beside the value in
    # data/companies/<id>.yaml (see design/single_source_of_truth.md §3).
    norm = resolve_normalised_baseline(inputs)

    base_revenue = income["revenue"]
    base_ebit_margin = norm.get("ebit_margin", income["operating_margin"])
    base_capex_pct = norm.get("capex_pct_revenue", 0.07)
    base_net_debt = norm.get("net_debt", derived["net_debt"])
    base_shares = share_stats["shares_outstanding"] / 1_000_000  # to millions
    base_tax_rate = norm.get("tax_rate", 0.30)

    aset = SmokeAssumptionSet(
        company_id=company.id,
        scenario_id=scenario.id,
        horizon_years=horizon_years,
        base_year_revenue=base_revenue,
        base_year_ebit_margin=base_ebit_margin,
        base_year_capex_pct_revenue=base_capex_pct,
        base_year_net_debt=base_net_debt,
        base_year_shares_outstanding=base_shares,
        base_year_tax_rate=base_tax_rate,
    )

    # Apply each populated driver from the matrix.
    for driver_id, movement in matrix_entry.drivers.items():
        if movement.not_applicable:
            continue
        rule = DRIVER_RULE_TABLE.get(driver_id)
        if rule is None:
            # Driver not in our hardcoded rule table; skip for smoke test.
            continue
        rule_kind, rule_table = rule
        key = (movement.direction, movement.magnitude)
        annual_delta = rule_table.get(key, 0.0)

        if rule_kind == "volume":
            base_value = 0.0  # delta itself is the growth rate
            unit_hint = "pct_yoy"
        elif rule_kind == "margin":
            if driver_id == "gross_margin":
                base_value = 1 - income.get("gross_profit", 0) / base_revenue \
                    if "gross_profit" in income else 0.0
                # Fallback: keep at scenario delta only
            base_value = 0.0
            unit_hint = "pp"
        else:  # rate
            base_value = 0.0
            unit_hint = "bps"

        # Linear-through-horizon time profile (Phase 3.5 simplification).
        annual_values = [annual_delta] * horizon_years

        aset.assumptions[driver_id] = TrajectoryAssumption(
            driver_id=driver_id,
            base_value=base_value,
            annual_delta=annual_delta,
            annual_values=annual_values,
            confidence=movement.confidence,
            direction=movement.direction,
            magnitude=movement.magnitude,
            rationale=movement.rationale,
            rule_applied=f"{rule_kind}: ({movement.direction.value},{movement.magnitude.value}) -> {annual_delta} ({unit_hint})",
        )

    return aset
