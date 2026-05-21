# IPL under Stagflation Persists

**Company:** Incitec Pivot Limited (ASX:IPL)
**Scenario:** Stagflation Persists (macro-downside boundary)
**Version:** 2026-Q2-v1
**Type:** Per-scenario impact narrative per §16.1 item 4.

---

## The headline

Stagflation Persists is materially negative for IPL. The energy / ammonia cost spike triggers exactly the pass-through stress that the §7.4 archetype's `supplier_power: moderate` rating implies — Ben's-bot worked example. IPL's long-term US gas contracts insulate roughly 70% of US gas exposure through 2028, but spot ammonia exposure and Australian gas costs compress margins materially. Mining-customer capex slows under restrictive financial conditions, hitting demand. Discount rates rise sharply, compounding the earnings hit through multiple compression. Real rates at 2.5% (vs Muddle Through 1%) are a structural valuation headwind that dominates the multiple side. Of the six scenarios, Stagflation Persists is one of the two worst outcomes for IPL.

## How the impact matrix transmits

Ten drivers populated — the heaviest non-climate scenario for IPL.

- **Volume growth — negative / moderate / high confidence.** Mining-customer capex slows under restrictive financial conditions; high real rates compress new mine development; recession in advanced economies amplifies the slowdown for 1-2 years.
- **Input cost pass-through — negative / large / high confidence.** **The critical driver under Stagflation.** Sustained 40-60% above-baseline energy / ammonia price spike. Supplier power moderate (archetype-level) blocks full pass-through under sustained input inflation. Long-term US gas contracts shield ~70% of US gas exposure, but ammonia spot and Australian gas costs compress margins materially.
- **Gross margin — negative / large / high confidence.** Direct flow-through from input cost pass-through. Cost pressure exceeds contract protection; mining customers themselves under cost pressure resist explosives price increases.
- **SG&A as % revenue — positive / small / moderate.** Wage inflation and operating cost pressure feed into SG&A. AI augmentation provides some offset but overwhelmed by broader cost-base inflation.
- **Maintenance capex as % revenue — positive / small / moderate.** Deferred maintenance catches up; replacement costs inflated.
- **Working capital days — positive / small / moderate.** Customer payment cycles lengthen; inventory builds as demand softens.
- **Risk-free rate — positive / large / high.** Real rates 2-3% (vs Muddle Through 1%). Material headwind to valuation multiples.
- **Equity risk premium — positive / moderate / high.** Risk appetite contracts; cyclical industrials face higher ERP.
- **Beta — positive / small / moderate.** Higher correlation with industrial cycles during recession.
- **Terminal growth rate — negative / small / moderate.** Long-run trend growth shaded down via structural damage to capital formation; skilled-migration constraints bite earlier in the trajectory.

## IPL-specific divergence from the archetype matrix

IPL has a partial company-specific buffer that the archetype matrix doesn't fully capture:

1. **US gas contract position is the primary defence.** ~70% of US gas exposure (~55% of total revenue's gas exposure) is shielded through 2028. This is material — for the first 2-3 years of the scenario, the cost-pressure transmission to IPL's US operations is materially dampened vs an unhedged peer.
2. **Australian operations have less contract protection on the gas side** — Australian east-coast gas market is structurally tighter. Australian explosives margins compress more sharply than US margins under Stagflation.
3. **Customer-concentration risk crystallises here.** If a top-5 mining customer reduces capex sharply under recession, the contracted volume floor may not fully protect IPL's revenue — and contract renegotiations under stress tend to favour the larger party (the mining major).
4. **Coal-customer mix (~35% of customer base) under double pressure** — stagflation slows coal demand directly via slower power generation growth + recession in industrial steel use, separate from any climate dynamics.

## Transmission channels for IPL

**Revenue:** materially negative. Volume declines 5-10% over the 2-3-year recession phase, partly recovers in resolution phase. Headline revenue probably falls 8-15% peak-to-trough.

**Margin:** the dominant negative. EBIT margin compresses from ~14% baseline to 8-10% in the worst years; gross margin from 28-32% to 22-26%. The input-cost pass-through failure is the single biggest swing variable in IPL's earnings outcome.

**Capex:** broadly stable in absolute dollars (maintenance plus inflated replacement costs) but rises as % of revenue given revenue decline. Growth capex deferred.

**Working capital:** modestly higher demand on cash.

**Financial / risk drivers:** the second leg of the negative. Real rates +150bps from baseline; ERP +75-100bps; beta drift. Discount rate composition compresses multiples 25-35%.

**Terminal state:** terminal growth shaded down small (the explicit horizon captures the cycle resolution; terminal is post-resolution).

## What partially defends IPL

Worth being explicit about the structural defences:

1. **US gas-contract position** — already covered. Buys 2-3 years of relative protection on the largest cost line.
2. **Australian duopoly** — even under stress, Orica and IPL Dyno Nobel don't engage in destructive price competition because the customer base is concentrated and the contracted volumes provide visibility. Price discipline holds.
3. **On-site service infrastructure** — sticky once embedded. Customer churn slow even under cost pressure on the customer side.
4. **Long-term offtake contracts** — provide volume visibility (less so on price under renegotiation pressure). 78% of revenue under multi-year contract per `data/financials/ipl.yaml`; weighted average maturity ~4 years.

These mitigants don't make Stagflation a positive outcome — they make it less bad than a comparable peer without IPL's franchise assets.

## Indicative directional view on valuation

- **Valuation under Stagflation sits perhaps 25-40% below Muddle Through.** The compression comes from: (a) earnings decline ~25-35% in the worst years, (b) discount rate increase compressing multiples ~25-30%, (c) terminal growth shading down ~0.5pp.
- **The downside is asymmetric vs Muddle Through.** Stagflation downside (~30% from baseline) is meaningfully larger in absolute terms than Orderly Convergence upside (~20% from baseline). This is the cyclical industrial profile.
- **The scenario is also asymmetric vs other downside scenarios.** Stagflation hits IPL harder than Fragmentation (which has duplication costs but not the acute cost pass-through failure) and is comparable to Disorderly Climate (which hits via different mechanisms).
- **Strategist-friend benchmark relevance.** If Tara's strategist friend has a IPL view that already incorporates stagflation-tail outcomes, the framework's Stagflation case should align reasonably closely. If the strategist's view assumes a different cost pass-through structure or different gas-contract assumptions, the divergence-localisation discipline per §15.1 should pinpoint where the difference sits.

## What would shift IPL out of Stagflation Persists

- Energy-price spike fading without second-round transmission → IPL recovers toward Muddle Through.
- Credible central-bank action re-anchoring inflation expectations → toward Muddle Through or Orderly Convergence.
- Deeper recession with rapid disinflation → a different scenario (not in current set) — potentially even more bearish on volume but with discount-rate relief.

## Cross-references

- Scenario definition: `data/scenarios/stagflation_persists.{yaml,md}`
- IPL positioning: `data/companies/ipl.{yaml,md}`
- Impact matrix entry: `data/impact_matrix/by_industry/industrial_explosives.yaml` (matrix[2])
- Cross-scenario thesis: `analyses/ipl/thesis.md`
- Valuation note: `analyses/ipl/valuations/stagflation_persists.md` (deferred)
