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
    archetype = IndustryArchetypeFile.model_validate(
        _load(archetype_path)
    ).industry_archetype
    company_raw = _load(company_path)
    company = CompanyPositionFile.model_validate(company_raw).company_position
    matrix = ImpactMatrix.model_validate(_load(matrix_path))
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
    """Per-year engine overlays for a scenario (methodology §11).

    Returns the scenario's ``normalised_baseline.engine_overlays[scenario_id]``
    mapping (margin glides, tax glide, capex step, base margin, D&A, terminal
    growth), or ``None`` if absent. These are the per-year paths the FCFF engine
    consumes; migrating them out of the hand-typed golden stand-in is part of M2.
    """
    nb = (company_raw or {}).get("normalised_baseline") or {}
    overlays = nb.get("engine_overlays") or {}
    return overlays.get(scenario_id)


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
