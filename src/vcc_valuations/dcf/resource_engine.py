"""
Resource (depleting-asset) FCFF engine -- the fourth engine (D-96 proposed, 20 Oct 2026).

For archetypes on the ``resource_lifecycle`` complementary framework (architecture.md
§7.5.1), first used for Evolution Mining (gold_producers). Method paper:
``design/methodology/resource_lifecycle_and_mining_drivers.md``.

Why a fourth engine. The industrial engine builds revenue as base x growth and the
terminal from a capital base that persists. A mine does neither: volume is a mine plan
that stops when the ore runs out, price is a scenario series, and the excess return is a
RENT on the ore with an end date (D-43a), not a barrier that a rival erodes. So:

    - each mine produces at its guidance rate until its declared recoverable inventory
      is exhausted (ore-driven: when the first of its metals runs out, the mine stops);
    - revenue = metal x the scenario's AUD price (USD real price x CPI index / AUD/USD),
      less any stream deliveries sold below spot;
    - costs are the guidance AISC with the by-product credit added back and the royalty
      stripped out, so copper and royalties move with their own prices, escalated by the
      scenario's CPI plus the archetype's real cost escalator;
    - the D-71 ten-year explicit period is kept. The terminal is the DEPLETION RUN-OFF:
      the present value of every cash flow after year ten until the last mine closes,
      then nothing -- replacement capital earns the cost of capital (D-97 proposed).

One WACC for every period (D-01). Mid-period discounting from the valuation date with a
fractional stub, exactly as ``fcf_engine.FcfEngine`` does. Equity bridge reuses
``fcf_engine.EquityBridge``. Nothing here names a company or a mine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from vcc_valuations.assumptions.wacc import WaccBuild
from vcc_valuations.dcf.fcf_engine import EquityBridge, terminal_share_warning

# koz x A$/oz and kt x A$/t both give A$ thousands; divide to reach A$ millions.
_THOUSANDS_PER_MILLION = 1.0e3  # ssot-allow: unit conversion, not a register value
# A guard on an unbounded loop: no producing mine on earth has sixty years of inventory
# at its current rate, and a mine that did would still be bounded by this.
_MAX_PERIODS = 60  # ssot-allow: loop guard

TERMINAL_FORM_DEPLETION = "depletion_run_off"
# Inventory left over from floating-point subtraction is not a production period.
_EXHAUSTED = 1.0e-9  # ssot-allow: numerical tolerance


@dataclass
class MineInputs:
    """One producing mine, in the company's functional currency (A$ m, koz, kt).

    Rates are full-year guidance midpoints. ``project_capex`` is per period (period 0 is
    the stub year at its FULL-year rate; the engine applies the stub fraction).
    """

    name: str
    gold_koz_pa: float
    copper_kt_pa: float
    inventory_gold_koz: float          # recoverable from the valuation date
    inventory_copper_kt: float
    aisc_aud_oz: float                 # guidance AISC, net of by-product credits
    sustaining_capex: float            # A$ m pa (inside AISC)
    mine_development: float            # A$ m pa (outside AISC)
    exploration: float                 # A$ m pa (outside AISC)
    da_aud_oz: float                   # book D&A per ounce, the tax-depreciation proxy
    project_capex: List[float] = field(default_factory=list)
    stream_delivered_fraction: float = 0.0
    stream_cash_fraction_of_spot: float = 0.0
    # A declared project uplift is carried as its own mine that starts later (the
    # resource_translator builds it from the host mine's unit cost). 0 = producing now.
    start_period: int = 0


@dataclass
class ResourceEngineInputs:
    company_id: str
    scenario_id: str
    functional_currency: str
    horizon_years: int
    stub_years: float
    mines: List[MineInputs]
    # Per-period paths, period 0 = the stub year. Length must cover every period the
    # longest-lived mine needs; the last value is held if the mine runs longer.
    gold_aud_oz: List[float]
    copper_aud_t: List[float]
    cost_index: List[float]            # 1.0 in the guidance year
    guidance_gold_aud_oz: float
    guidance_copper_aud_t: float
    royalty_rate: float
    tax_rate: float
    corporate_cost_aud_oz: float
    greenfields_exploration: float     # A$ m pa while any mine produces
    working_capital_intensity: float
    wacc: Union[WaccBuild, float]
    equity_bridge: EquityBridge
    notes: List[str] = field(default_factory=list)

    @property
    def wacc_scalar(self) -> float:
        return self.wacc.wacc if isinstance(self.wacc, WaccBuild) else float(self.wacc)


@dataclass
class ResourceDcfResult:
    company_id: str
    scenario_id: str
    horizon_years: int
    functional_currency: str
    period_labels: List[str]
    gold_koz: List[float]
    copper_kt: List[float]
    gold_aud_oz: List[float]
    copper_aud_t: List[float]
    revenue: List[float]
    royalty: List[float]
    operating_cost: List[float]
    exploration_and_corporate: List[float]
    ebitda: List[float]
    da: List[float]
    tax: List[float]
    capex: List[float]
    delta_wc: List[float]
    fcff: List[float]
    mine_last_period: Dict[str, int]
    wacc: float
    mid_times: List[float]
    discount_factors: List[float]
    pv_fcff: List[float]
    pv_explicit: float
    pv_terminal: float
    terminal_value: float              # at the end of the explicit period
    terminal_end_time: float
    terminal_form: str
    enterprise_value: float
    net_debt_at_valuation: float
    equity_bridge_adjustments_net: float
    lease_liabilities: float
    equity_value: float
    shares_outstanding: float
    value_per_share: float
    terminal_share_of_ev: float
    life_years: float                  # valuation date to the last mine's closure
    market_reference_price: Optional[float]
    discount_to_market: Optional[float]
    warnings: List[str]
    notes: List[str]


def _at(path: List[float], t: int) -> float:
    return path[t] if t < len(path) else path[-1]


class ResourceEngine:
    """Mine-by-mine depletion DCF. ``run(inputs) -> ResourceDcfResult``."""

    def run(self, inp: ResourceEngineInputs) -> ResourceDcfResult:
        H = inp.horizon_years
        f0 = inp.stub_years
        r = inp.wacc_scalar
        warnings: List[str] = []
        notes: List[str] = list(inp.notes)

        remaining = {m.name: [m.inventory_gold_koz, m.inventory_copper_kt] for m in inp.mines}
        last_period = {m.name: -1 for m in inp.mines}

        cols = {k: [] for k in ("gold", "cu", "rev", "roy", "opex", "expl", "ebitda",
                                "da", "tax", "capex", "dwc", "fcff")}
        gold_px, cu_px = [], []
        prev_rev_annual: Optional[float] = None
        t = 0
        while True:
            frac = f0 if t == 0 else 1.0
            ci = _at(inp.cost_index, t)
            pg = _at(inp.gold_aud_oz, t)
            pc = _at(inp.copper_aud_t, t)
            gold = cu = rev = opex = expl = da = capex = 0.0
            producing = False
            for m in inp.mines:
                if t < m.start_period:
                    continue
                rem_g, rem_c = remaining[m.name]
                scale = frac
                if m.gold_koz_pa > 0:
                    scale = min(scale, max(rem_g, 0.0) / m.gold_koz_pa)
                if m.copper_kt_pa > 0:
                    scale = min(scale, max(rem_c, 0.0) / m.copper_kt_pa)
                if scale <= _EXHAUSTED:
                    continue
                producing = True
                last_period[m.name] = t
                g = m.gold_koz_pa * scale
                c = m.copper_kt_pa * scale
                remaining[m.name] = [rem_g - g, rem_c - c]
                gold += g
                cu += c
                stream_haircut = m.stream_delivered_fraction * (1.0 - m.stream_cash_fraction_of_spot)
                rev += (g * pg * (1.0 - stream_haircut) + c * pc) / _THOUSANDS_PER_MILLION
                # Guidance AISC is net of the copper credit and includes royalties at the
                # guidance prices. Add the credit back and take the royalty out, so both
                # move with this scenario's prices instead.
                gross = (m.aisc_aud_oz * m.gold_koz_pa + m.copper_kt_pa * inp.guidance_copper_aud_t) / _THOUSANDS_PER_MILLION
                guidance_royalty = inp.royalty_rate * (
                    m.gold_koz_pa * inp.guidance_gold_aud_oz + m.copper_kt_pa * inp.guidance_copper_aud_t
                ) / _THOUSANDS_PER_MILLION
                opex += (gross - guidance_royalty - m.sustaining_capex) * scale * ci
                expl += m.exploration * scale * ci
                capex += (m.sustaining_capex + m.mine_development) * scale * ci
                capex += _at(m.project_capex, t) * frac * ci if t < len(m.project_capex) else 0.0
                da += m.da_aud_oz * g / _THOUSANDS_PER_MILLION
            if not producing and all(t >= m.start_period for m in inp.mines):
                break
            expl += (inp.corporate_cost_aud_oz * gold / _THOUSANDS_PER_MILLION
                     + inp.greenfields_exploration * frac) * ci
            roy = inp.royalty_rate * rev
            ebitda = rev - roy - opex - expl
            tax = inp.tax_rate * max(ebitda - da, 0.0)
            rev_annual = rev / frac
            dwc = 0.0 if prev_rev_annual is None else inp.working_capital_intensity * (rev_annual - prev_rev_annual)
            prev_rev_annual = rev_annual
            fcff = ebitda - tax - capex - dwc
            for k, v in (("gold", gold), ("cu", cu), ("rev", rev), ("roy", roy), ("opex", opex),
                         ("expl", expl), ("ebitda", ebitda), ("da", da), ("tax", tax),
                         ("capex", capex), ("dwc", dwc), ("fcff", fcff)):
                cols[k].append(v)
            gold_px.append(pg)
            cu_px.append(pc)
            t += 1
            if t >= _MAX_PERIODS:
                raise ValueError(f"{inp.company_id}: inventory not exhausted in {_MAX_PERIODS} periods.")

        # Closure: the working-capital balance unwinds when the last revenue stops.
        if prev_rev_annual is not None and cols["fcff"]:
            release = inp.working_capital_intensity * (0.0 - prev_rev_annual)
            cols["dwc"][-1] += release
            cols["fcff"][-1] -= release

        n = len(cols["fcff"])
        if n <= H:
            warnings.append(
                f"Every mine closes inside the explicit period ({n} periods <= {H}); the "
                "depletion run-off terminal is zero."
            )
        mid_times = [f0 / 2.0] + [f0 + k - 0.5 for k in range(1, n)]  # ssot-allow: mid-period convention
        dfs = [1.0 / (1.0 + r) ** mt for mt in mid_times]
        pv = [c * d for c, d in zip(cols["fcff"], dfs)]
        pv_explicit = sum(pv[: H + 1])
        pv_terminal = sum(pv[H + 1:])
        terminal_end_time = f0 + H
        terminal_value = pv_terminal * (1.0 + r) ** terminal_end_time
        ev = pv_explicit + pv_terminal
        share = pv_terminal / ev if ev else 0.0
        w = terminal_share_warning(share, "EV")
        if w:
            warnings.append(w)

        eb = inp.equity_bridge
        equity = ev - eb.net_debt_at_valuation - eb.equity_bridge_adjustments_net - eb.lease_liabilities
        vps = equity / eb.shares_outstanding
        dtm = vps / eb.market_reference_price - 1.0 if eb.market_reference_price else None
        life_years = f0 + max(last_period.values()) if max(last_period.values()) > 0 else f0

        notes.append(
            f"Single WACC {r:.4%} for the stub, {H} explicit years and the run-off (D-01)."  # ssot-allow: format spec
        )
        notes.append(
            "Terminal = depletion run-off: PV of cash flows after the explicit period to the "
            "last closure; replacement at zero NPV, no perpetuity (D-97 proposed)."
        )
        labels = ["Stub"] + [f"Y{k}" for k in range(1, n)]
        return ResourceDcfResult(
            company_id=inp.company_id, scenario_id=inp.scenario_id, horizon_years=H,
            functional_currency=inp.functional_currency, period_labels=labels,
            gold_koz=cols["gold"], copper_kt=cols["cu"], gold_aud_oz=gold_px, copper_aud_t=cu_px,
            revenue=cols["rev"], royalty=cols["roy"], operating_cost=cols["opex"],
            exploration_and_corporate=cols["expl"], ebitda=cols["ebitda"], da=cols["da"],
            tax=cols["tax"], capex=cols["capex"], delta_wc=cols["dwc"], fcff=cols["fcff"],
            mine_last_period=last_period, wacc=r, mid_times=mid_times, discount_factors=dfs,
            pv_fcff=pv, pv_explicit=pv_explicit, pv_terminal=pv_terminal,
            terminal_value=terminal_value, terminal_end_time=terminal_end_time,
            terminal_form=TERMINAL_FORM_DEPLETION, enterprise_value=ev,
            net_debt_at_valuation=eb.net_debt_at_valuation,
            equity_bridge_adjustments_net=eb.equity_bridge_adjustments_net,
            lease_liabilities=eb.lease_liabilities, equity_value=equity,
            shares_outstanding=eb.shares_outstanding, value_per_share=vps,
            terminal_share_of_ev=share, life_years=life_years,
            market_reference_price=eb.market_reference_price, discount_to_market=dtm,
            warnings=warnings, notes=notes,
        )
