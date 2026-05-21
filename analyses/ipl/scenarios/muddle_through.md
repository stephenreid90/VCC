# IPL under Muddle Through

**Company:** Incitec Pivot Limited (ASX:IPL)
**Scenario:** Muddle Through (interior, most-likely)
**Version:** 2026-Q2-v1
**Type:** Per-scenario impact narrative per §16.1 item 4. Companion to `data/scenarios/muddle_through.{yaml,md}`, `data/companies/ipl.{yaml,md}`, and `data/impact_matrix/by_industry/industrial_explosives.yaml`.

---

## The headline

Muddle Through is the reference scenario for IPL. The mining-customer capex cycle continues at current pace; gas and ammonia input costs stay near current levels; long-term contracts hold their value; technology mix-shift (DigiShot electronic detonators, AI-driven blast design) advances incrementally. Real rates stay structurally higher than the 2010s — a modest valuation headwind already in the baseline. No crystallisation event in any of the dimensions that would push IPL into one of the boundary scenarios. The reference point against which other scenarios are compared.

## How the impact matrix transmits

Per the industrial_explosives impact matrix entry for Muddle Through, four drivers are populated and all sit at `neutral / small / moderate-to-high confidence`. The sparse representation indicates this is precisely the scenario where the framework isn't moving anything materially — drivers sit at archetype-level base ranges.

- **Volume growth** — neutral / small. Mining-customer capex cycle continues at current pace. GDP-adjacent volume growth with modest cyclical variation. No catalyst either direction.
- **Input cost pass-through** — neutral / small. IPL's long-term US gas contracts continue to insulate ~70% of US gas exposure through 2028; Australian gas at established levels; ammonia spot exposure where contract-uncovered tracks baseline. Established pass-through dynamics with mining customers maintained.
- **Risk-free rate** — neutral / small / high confidence. Real rates settle ~1% as the baseline anchor. Already reflected in current valuation multiples.
- **Terminal growth rate** — neutral / small. Long-term mining-customer demand approximately GDP-adjacent. Demographic-adaptation trajectory in Australia and US handled at current pace; per §9.7 item 9, terminal growth assumption reflects this without dramatic compression.

## IPL-specific divergence from the archetype matrix

IPL's company-level scenario-sensitivity overrides (per `data/companies/ipl.yaml` `scenario_sensitivity_overrides_global`) are not triggered under Muddle Through — the operational carbon exposure and supply-chain concentration dimensions are background factors here, not active drivers.

The two IPL-specific positioning advantages that modulate the archetype baseline:

1. **US gas contract position** (franchise asset). Continues to deliver cost-curve advantage relative to spot-gas-exposed competitors. No erosion within Muddle Through's horizon (most contracts roll 2028-2030); the advantage decays gradually thereafter but is captured in terminal-state assumptions rather than in the explicit forecast period.
2. **Australian duopoly position.** Continues to support moderately above-archetype-average margins in the Australian segment. Orica and IPL Dyno Nobel share the addressable market without acute price competition; bulk ANFO contests at the margin but technology and service products preserve mix.

## Transmission channels for IPL

**Revenue:** broadly stable. Mining-customer capex cycle continues at current pace; modest volume growth (~1-3% per year); price/mix improvement from electronic-detonator share creep (current 18%, rising slowly). No volume crisis; no volume breakthrough.

**Margin:** stable. Gross margin holds in the 28-32% range; EBIT margin in the 13-15% range. Input cost pass-through continues to work via contracted structures. The labour-cost containment from AI augmentation provides modest tailwind on SG&A but is incremental.

**Capex:** maintenance-led. Capital intensity continues at ~6% of revenue. No major capacity additions inside horizon; Louisiana-style large-capex episodes are not in the baseline (and IPL post-demerger management has communicated capital discipline). Technology capex modest (DigiShot evolution, AI-driven services platform).

**Working capital:** stable.

**Financial / risk drivers:** real rates at the 1% baseline; equity risk premium near long-term average; cost of debt at structurally higher levels than 2010s but stable. Credit spreads tight enough to support the moderate leverage posture (net-debt/EBITDA ~1.8x baseline).

**Terminal state:** terminal ROIC approximately at WACC per the §1 / §9.3 cost-of-capital convergence principle. Fade period long (~15 years) reflecting durable but eroding moat. Terminal growth ~2% nominal in USD terms.

## Indicative directional view on valuation

Without the DCF engine (deferred to Step 7 / Phase 3.5 smoke-test), the directional view is:

- **Valuation under Muddle Through approximates the current trading range** for IPL given the scenario's status-quo-extension nature. Consensus analyst targets, which generally assume something close to Muddle Through (with slight Orderly Convergence tint), would be the relevant benchmark.
- **Asymmetry around the central estimate is modest.** Range from low to high case within Muddle Through would be perhaps ±15-20% on per-share value, driven primarily by the gas-contract roll-off timing and Australian duopoly pricing discipline.
- **Strategic-friend benchmark relevance.** This is the scenario where the framework's output should most closely align with conventional analyst valuation. Material divergence here would be the calibration alarm — either the framework is mis-specifying baseline drivers or the consensus is mis-anchored.

## What would shift IPL out of Muddle Through

Per the scenario's `disconfirming_evidence` block:

- Sustained inflation re-anchoring at target → IPL improves toward Orderly Convergence (mining capex healthier).
- Inflation un-anchoring with second-round wage dynamics → IPL deteriorates toward Stagflation Persists (cost compression, demand slowdown).
- Geopolitical / climate / financial trigger event → IPL moves to the relevant boundary scenario.

For IPL specifically, the most consequential trigger to watch is **gas-contract reset visibility** — as the 2028-2030 reset window approaches, market focus on the cost-curve roll-off intensifies regardless of broader scenario.

## Cross-references

- Scenario definition: `data/scenarios/muddle_through.{yaml,md}`
- IPL positioning: `data/companies/ipl.{yaml,md}`
- Impact matrix entry: `data/impact_matrix/by_industry/industrial_explosives.yaml` (matrix[0])
- Cross-scenario thesis: `analyses/ipl/thesis.md`
- Valuation note: `analyses/ipl/valuations/muddle_through.md` (deferred to Phase 3.5 smoke-test DCF per build plan)
