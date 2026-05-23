# DNL — Cross-scenario investment thesis

**Company:** Dyno Nobel Limited (ASX:DNL)
**Version:** 2026-Q2-v1
**Type:** Cross-scenario investment view per §16.1 item 6. Rollup synthesis across the six per-scenario impact analyses in `analyses/dnl/scenarios/`.

---

## One-paragraph thesis

Post-demerger Incitec Pivot is a pure-play industrial-explosives company with a structurally defensible position — co-leader globally, duopolist in Australia, US cost-curve advantage from long-term gas contracts — but with material exposure to cyclical mining-customer demand, energy and ammonia input costs, and a coal-customer mix that is structurally declining over the long horizon. Across our six scenarios, DNL is **negatively asymmetric** — the downside scenarios (Stagflation, Disorderly Climate, Fragmentation) compress value materially more than the upside scenario (Orderly Convergence) lifts it. The single most consequential firm-specific variable is the **US gas-contract roll-off in the 2028-2030 window**, which determines how much of DNL's structural cost advantage survives into the terminal state. Of the six scenarios, DNL's outcome is most sensitive to **Stagflation** and **Disorderly Climate** (both ~25-35% below Muddle Through); least sensitive to **AI Productivity Lag** (within ±5% of Muddle Through). The framework's value-add over conventional analyst views is the explicit treatment of: the USD functional-currency call (which most published Australian DCFs get wrong); the supplier-power-blocks-cost-pass-through dynamic under Stagflation; the bifurcated exposure under Disorderly Climate (coal-customer attrition vs transition-mineral demand); and the structural Fragmentation exposure from the US-Australia operating split.

## Where the asymmetry sits

| Scenario | Indicative value vs Muddle Through | Dominant driver |
|---|---|---|
| Orderly Convergence | +15–25% | ERP compression + modest volume/margin lift |
| Muddle Through | 0% (baseline) | Status quo extension |
| AI Productivity Lag | within ±5% | Small headwinds and tailwinds cancelling |
| Fragmentation | -20 to -30% | Supply-chain duplication costs + country risk premium |
| Disorderly Climate Crystallisation | -25 to -35% | Carbon-cost flow-through + terminal-state convergence acceleration |
| Stagflation Persists | -25 to -40% | Input-cost pass-through failure + discount rate spike |

The asymmetry is structural to DNL's cyclical-industrial profile: cyclical names compress harder under bad outcomes than they expand under good ones. This is in contrast to a quality-growth name like CSL, which would re-rate more sharply on the upside under Orderly Convergence via multiple expansion.

## Three transmission channels that distinguish DNL's scenario exposures

### 1. Input cost pass-through under sustained inflation

The §7.4 archetype's `supplier_power: moderate` rating implies that under sustained input-cost inflation, mining-customer push-back blocks full pass-through. DNL's long-term US gas contracts shield ~70% of US gas exposure through 2028, but Australian gas (no long-term contract position) and ammonia spot exposure (where contract-uncovered) flow through.

This is the binding constraint under Stagflation. It is *also* relevant under Disorderly Climate Crystallisation, where carbon-cost flow-through has a similar transmission mechanism (carbon priced through ammonia production into bulk ANFO; mining customers themselves under carbon-cost pressure resist explosives price increases).

Watchable signals:

- **Australian east-coast gas prices** (no DNL contract protection).
- **US natural gas curve through 2028-2030** (where DNL contracts roll off).
- **Mining-customer contract reset patterns** — DNL is currently 78% revenue under multi-year contract with ~4-year weighted-average maturity; contract resets at higher cost-pass-through terms would partially mitigate the pass-through failure.

### 2. Geographic / bloc-alignment exposure

DNL operates ~55% USA, ~35% Australia, ~10% RoW. Both core jurisdictions sit in the US-aligned bloc. Under Fragmentation, the US-aligned bloc is the slower-growing bloc, and DNL's cross-bloc supply-chain exposures (ammonium nitrate flows, ammonia inputs) are regulatorily sensitive. The China-aligned bloc upside doesn't accrue to DNL.

The partial offset is Australia's strategic-mineral position — BHP nickel, FMG iron ore for green steel feedstock, broader copper / lithium exposure provide demand pull from US-aligned bloc strategic-mineral supply.

Watchable signals:

- **Australia bloc-alignment trajectory** — explicit choices on rare-earths supply, semiconductor policy, defence cooperation.
- **Cross-bloc trade restrictions on ammonium nitrate** — particularly US-Canada movements which are already regulatorily sensitive.
- **Mining-customer export-market dynamics** — Australian iron ore demand from Chinese steel mills under bloc contestation.

### 3. Terminal-state exposure to coal-customer attrition

Coal-mining customers represent ~35% of DNL's customer mix (~20% thermal, ~15-20% met). The §9.7 item 9 terminal-growth-from-demographic-trajectory principle has its **climate-trajectory analogue** here — terminal growth and terminal ROIC must reflect the trajectory of coal-customer demand even when the explicit horizon doesn't fully capture the attrition.

Under Disorderly Climate Crystallisation, the moat decays faster than the standard fade period assumes. The defended-exception treatment per §10.6 rule 2 attempts to capture this without claiming a permanent breach of cost-of-capital convergence — moat decays, but converges to cost of capital over a shortened fade period.

Watchable signals:

- **Thermal coal customer capex announcements** (winding down, repurposing for transition).
- **Met coal demand trajectory** (green-steel substitution timing).
- **Transition-mineral mining capex acceleration** (the offset).
- **Carbon-pricing trajectory in Australia and US** (where DNL's ammonia production sits).

## What the framework adds over conventional analyst views

Four things the architecture forces that consensus analyst valuations of DNL typically don't do:

1. **USD functional currency.** Per IAS 21 / AASB 121 and per the company's actual cash-flow structure. Most published Australian DCFs use AUD because it's the reporting currency. The framework's discipline puts the analysis in the currency where economic decisions are made.
2. **Supplier-power-blocks-cost-pass-through explicitly.** Per the §7.4 archetype + §10.2 impact matrix interaction, DNL's cost-pass-through under sustained inflation gets explicitly tested rather than assumed to work. Consensus DCFs typically assume input costs pass through.
3. **Coal-customer-attrition reflected in terminal state.** Per §9.7 item 9 (climate-trajectory analogue) and §10.6 defended-exception discipline, terminal ROIC reflects the customer-base trajectory rather than extrapolating current returns indefinitely. Consensus DCFs typically use a static terminal ROIC.
4. **Fragmentation as a modelled scenario, not just a risk-register item.** Per the §3 workshop output, Fragmentation has unique DNL exposure that conventional analysis typically captures only as a sensitivity, not as a modelled scenario.

## What would update the thesis

Per the §15 calibration discipline, the thesis is updated when one of the following materialises:

1. **A scenario-defining event materialises** — moves DNL into one of the boundary scenarios with structural permanence.
2. **The strategist-friend benchmark divergence localises a specific assumption gap** — per the §15.1 angle 1.(c) framing, disagreement on conclusion + divergence localisation > both being individually right.
3. **Ben's data workstream replaces the indicative base-year financials** with curated data — may shift the base-year anchor and therefore the cross-scenario absolute valuations (relative valuations less affected).
4. **A 6-month scenario refresh** (§6.5) brings revised macro / regime assumptions; downstream `DriverMovementSet` and `AssumptionSet` regenerate; this thesis updates accordingly.
5. **A material DNL-specific corporate event** (acquisition / divestment / capital-structure change) — triggers a corporate-action overlay per §8.4 and re-runs of the per-scenario analyses.

The thesis is provisional. The framework's value is in the trace and the comparative structure, not in any single point estimate.

## Strategic-friend benchmark — calibration plan

Per §15.1, the DNL benchmark from your strategist friend is the most important single calibration input. Build the **trace-comparison tooling** in step 8 of the build plan so we can compare reasoning chains side-by-side, not just headline numbers. Expected pattern:

- **If we agree on conclusion for different reasons**: framework intuition is converging with strategist intuition. Good signal.
- **If we agree on conclusion for the same reasons**: weak signal — both anchored to same starting frame.
- **If we disagree on conclusion**: the §11.6 reasoning trace localises *where* the disagreement sits — positioning vs scenario impact vs translation. More valuable than either of us being individually right.

For DNL specifically, the most likely areas of divergence:

- **Pass-through assumption under Stagflation** (we are explicit that pass-through fails; strategist may assume it works).
- **Terminal-state treatment under Disorderly Climate** (we apply defended-exception discipline forcing accelerated convergence; strategist may extrapolate current returns).
- **Functional currency** (we use USD; strategist may use AUD).
- **Transition-mineral offset speed under Disorderly Climate** (we have it as a partial-but-not-complete offset; strategist may credit it more or less).

## Cross-references

- Per-scenario narratives: `analyses/dnl/scenarios/<scenario>.md` × 6.
- Company positioning: `data/companies/dnl.{yaml,md}`.
- Industry view: `data/industries/industrial_explosives.{yaml,md}`.
- Impact matrix: `data/impact_matrix/by_industry/industrial_explosives.yaml`.
- Indicative base-year financials: `data/financials/dnl.yaml` (to be replaced by Ben's curated data).
- Architecture spec principles applied: §1 (cost-of-capital convergence), §6.2 (scenarios as boundary cases), §7.5 (Five Forces transmission), §8.4 (corporate-action overlay — currently empty for DNL), §9.7 item 9 (terminal-growth-from-demographic-trajectory), §10.2 (encoding conventions), §10.6 (defended-exception discipline), §11.4.2 (consistency checks), §15.1 (calibration angles), §16.1 (narrative deliverables).
- Per-scenario valuation notes `analyses/dnl/valuations/<scenario>.md` are deferred to Phase 3.5 smoke-test DCF per build plan; this thesis stands as the integrated view until those are produced.
