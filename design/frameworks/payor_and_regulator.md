# Payor-and-Regulator Framework

**Status:** Draft v1. Written before banking-archetype (WBC) population; expect refinement once the first archetype is populated against it.
**Companion to:** `design/architecture.md` §7.5.1 (complementary frameworks), §7.4 (industry archetype schema, `complementary_framework` block), §8.3 (archetype-specific positioning), §9.4.1 (banking driver set).

---

## Purpose

Some archetypes are not adequately described by Porter's Five Forces because the **binding constraint on profitability sits outside the industry's competitive dynamics, not inside them**. For banks, APRA and Basel III are not "forces" in Porter's sense — they're an external structural overlay: CET1 floor sets RWA intensity; deposit-insurance fee structure shapes funding mix; four-pillars policy effectively eliminates new-entrants threat. For regulated healthcare, the patient is not the buyer — the **payor** (Medicare, PBS, private insurer) is. For utilities, the **rate-setter** determines allowable returns. In each case, stuffing this content into Porter's "regulatory pressure" sub-field under-states its analytical weight.

This framework runs **alongside** Porter's Five Forces, not in place of it. Five Forces captures the competitive dynamics within the regulatory envelope; this framework captures the envelope itself. An archetype using `complementary_framework.type: payor_and_regulator` is expected to populate both.

**Initial scope.** Banking (WBC; primary test case in v0.1), insurance (general / life), regulated healthcare (pharma / hospitals / aged care), utilities (electricity, gas, water, telco). Other archetypes may adopt the framework if the binding-constraint logic applies.

---

## How to use

1. Apply only to archetypes flagged `complementary_framework.type: payor_and_regulator` in the §7.4 schema.
2. Work through each section in order. Answers populate the `complementary_framework.details` block of the archetype YAML.
3. Pair each industry-level finding with a company-level finding, same convention as the Five Forces question bank.
4. Run **after** Porter's Five Forces for the same archetype, not before — the Five Forces analysis surfaces what remains competitive, which this framework then sets in context.
5. The synthesis (Part D) maps findings into §8.3 archetype-specific positioning fields and into §11.4 derivation formulas (e.g. binding capital constraint flows into the bank DDM as required equity).

---

## Convention

- Identify each regulator and each payor **by name**, not by category. "APRA" rather than "the prudential regulator"; "Medicare" rather than "government payor".
- For each binding constraint, state the metric, the level, and the consequence of breach.
- Distinguish **regulatory tools** that constrain (capital floors, rate ceilings, licensing) from regulatory tools that **enable** (subsidies, grandfathered approvals, exclusivity grants). Both matter; they pull in different directions.
- Where there are multiple regulators or payors, name each and weight by materiality.
- Answer shape for ratings: `low | moderate | high`, with 2-3 sentences of rationale, consistent with Five Forces.

---

## Two-axis framing

The framework has two distinct dimensions, and **both must be assessed**:

1. **Regulatory dimension** — the constraint envelope set by external authority. Sources of regulation, binding constraints, regulatory regime characteristics, direction of pressure.
2. **Payor dimension** — who actually pays for the industry's output, how concentrated they are, what leverage they hold.

The relative weight of the two axes differs by archetype. Banks lean regulator (prudential dominates, depositor payor structure is constrained by deposit-insurance regime). Healthcare leans payor (third-party payors materially shape pricing, regulators set barriers but rarely price directly). Utilities lean both (rate-setter regulates the price the payor pays). Tech-platform-with-data-regulation cases lean regulator. Each archetype's `details` block must record where its weight sits.

---

## Part A: Regulatory dimension

### A.1 Primary regulators

**Industry:** Name the regulators that materially shape industry economics. For each: their mandate (prudential / conduct / antitrust / safety / pricing / market access), the legal instruments they hold (licensing, capital requirements, rate-setting, approval processes), and their effective independence from political cycles.
*Answer shape: list of named regulators with mandate + instruments + independence rating `low | moderate | high`. Banking example: APRA (prudential, capital + liquidity rules, high independence), ASIC (conduct, licensing + market integrity, high independence), RBA (monetary + payments, indirect prudential influence, very high independence).*

**Company:** Which regulators apply most materially to this specific company? Are there regulators that apply to peers but not to this company (or vice versa)?
*Answer shape: subset of industry regulator list with materiality rating per regulator, plus any divergence from peers.*

### A.2 Binding constraint(s)

**Industry:** What is the single most-binding regulatory constraint on industry profitability — the metric that, if breached, triggers material intervention? Name the metric, the level, and the consequence of breach. Banking example: CET1 ratio with APRA "unquestionably strong" floor of 10.5% (major banks); breach triggers capital remediation plan, restrictions on dividends and buybacks, and reputational damage.
*Answer shape: rating `low | moderate | high` (severity of constraint), plus the metric / level / consequence triplet. Multiple binding constraints are possible; list each.*

**Company:** Where does this company sit relative to the binding constraint — at the floor, comfortably above, or below the regulatory expectation? How much management headroom does it carry?
*Answer shape: rating `low | moderate | high` (proximity to constraint), plus actual level vs floor and trend over recent reporting periods.*

### A.3 Regulatory regime

**Industry:** What is the broader policy stance shaping the industry — protective (e.g. four-pillars policy in Australian banking; airline route licensing), pro-competition (e.g. consumer data right; open banking), pro-consumer (e.g. payday-lending caps; energy-price guarantees), pro-investment (e.g. accelerated depreciation; renewable energy targets)?
*Answer shape: rating `low | moderate | high` (regime favourability to incumbents), plus narrative naming the dominant policy instruments and the rationale they embody.*

**Company:** Does this company benefit from regime-derived position more or less than industry peers — grandfathered approvals, incumbent licences, scale-based regulatory accommodation, regulator relationship quality?
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of company-specific regime advantages or exposures.*

### A.4 Regulatory dynamic — direction of pressure

**Industry:** Is regulatory pressure tightening, steady, or loosening? What known step-changes are on the horizon (Basel IV; Royal Commission follow-ups; APRA target-asset reviews; PBS reforms; energy market reforms)? What is the lag from announcement to effective implementation?
*Answer shape: direction tag (`tightening | steady | loosening`), plus list of known step-changes with effective dates and a rating `low | moderate | high` (uncertainty around timing / shape).*

**Company:** Is this company differentially exposed to the known step-changes — by business mix, geography, legacy position? Has the company invested in compliance / lobbying / regulator engagement ahead of peers?
*Answer shape: rating `low | moderate | high` (relative exposure), plus narrative.*

---

## Part B: Payor dimension

### B.1 Primary payors

**Industry:** Who actually pays for the industry's output, and through what channel? Distinguish the **payor** (writes the cheque) from the **end user** (consumes the product) where they differ. Banking example: depositors and borrowers are the end users, but depositor-side pricing is constrained by the deposit-insurance regime, and borrower-side pricing is constrained by competition for credit risk; the deposit insurance scheme is effectively a co-payor on funding cost. Healthcare example: patient is end user, payor is Medicare / PBS / private insurer.
*Answer shape: list of named payors with channel (direct payment / insurance / government scheme / rate-recovery / fee-based) and rating `low | moderate | high` (concentration of payor identity).*

**Company:** What is this company's payor mix vs the industry typical? Are there payor segments where the company is over- or under-weight?
*Answer shape: payor mix by share of revenue / EBIT, plus rating `low | moderate | high` (relative concentration vs industry).*

### B.2 Payor concentration and substitutability

**Industry:** How concentrated is the payor base? Can industry participants substitute one payor for another (e.g. multiple insurance plans, multiple government programmes), or is each payor effectively a sole counterparty for the segment they cover?
*Answer shape: rating `low | moderate | high` (payor concentration), plus quantification where available (e.g. "PBS covers ~80% of pharmaceutical spend").*

**Company:** Does this company have differentiated payor access — multiple payor relationships, payor-mix diversification, ability to walk away from any single payor?
*Answer shape: rating `low | moderate | high` (relative to industry payor diversification), plus narrative.*

### B.3 Payor leverage and pricing power

**Industry:** How much pricing power do payors hold? Can payors set, negotiate, or constrain prices, or are prices set by other mechanisms (market, regulator, formula)? Where payors set prices directly (Medicare reimbursement schedules; rate-of-return regulation; insurer contracted rates), record the price-setting mechanism and the renegotiation cadence.
*Answer shape: rating `low | moderate | high` (payor pricing power), plus narrative on the price-setting mechanism and cadence.*

**Company:** Does this company hold more or less negotiating leverage with payors than industry peers — through scale, differentiated offering, geographic position, exclusive contracts, regulatory protection?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative naming the levers.*

### B.4 Payor mix evolution

**Industry:** What is the direction of payor-mix change — shift from private to public payor (or vice versa), consolidation among payors, new payor types entering (employer self-insurance; embedded-insurance platforms; direct-to-consumer healthcare)? What is the time horizon?
*Answer shape: direction tag (`stable | shifting_to_public | shifting_to_private | consolidating | fragmenting`), plus narrative on the dominant shift and rating `low | moderate | high` (pace of shift).*

**Company:** Is this company aligned with or against the direction of payor-mix change?
*Answer shape: rating `low | moderate | high` (favourable to unfavourable alignment), plus narrative.*

---

## Part C: Interaction with competition

### C.1 Competition within the regulatory envelope

**Industry:** With the regulatory and payor envelope set, what dimensions of competition remain meaningful? Banking example: deposit pricing and lending pricing within the prudential envelope; service quality; brand; distribution reach; technology platform; cost-to-income efficiency. Healthcare example: clinical outcomes; service experience; cost efficiency vs payor reimbursement; specialty mix.
*Answer shape: list of competitive dimensions that remain inside the envelope, with rating `low | moderate | high` per dimension on its impact on relative profitability.*

**Company:** Where does this company compete most effectively within the envelope, and where does it lag?
*Answer shape: rating `low | moderate | high` (within-envelope competitive position), plus narrative on its strongest and weakest dimensions.*

### C.2 Regulatory arbitrage and asymmetries

**Industry:** Does the regulatory regime create asymmetries between participants — large vs small, incumbent vs new entrant, local vs foreign, domestic vs foreign-headquartered, low-tech vs high-tech? Examples: APRA differential capital floors for major vs non-major banks; PBS listing protections for incumbent products; renewable subsidies favouring established generators.
*Answer shape: rating `low | moderate | high` (extent of regime asymmetry), plus list of the most material asymmetries with direction.*

**Company:** Is this company a beneficiary, a victim, or neutral on each asymmetry?
*Answer shape: per-asymmetry tag (`benefits | exposed | neutral`), plus narrative.*

---

## Part D: Synthesis

After working through Parts A-C:

### D.1 Schema mapping

Record in the archetype YAML's `complementary_framework.details` block:

```yaml
complementary_framework:
  type: payor_and_regulator
  details:
    axis_weight: regulator_dominant | payor_dominant | both_material
    regulators:
      - name: string
        mandate: prudential | conduct | antitrust | safety | pricing | market_access
        instruments: list
        independence: low | moderate | high
    binding_constraints:
      - metric: string
        level: string
        consequence_of_breach: string
        severity: low | moderate | high
    regime:
      favourability_to_incumbents: low | moderate | high
      policy_stance: protective | pro_competition | pro_consumer | pro_investment | mixed
      narrative: string
    dynamic:
      direction: tightening | steady | loosening
      known_step_changes:
        - description: string
          effective_date: date | null
          uncertainty: low | moderate | high
    payors:
      - name: string
        channel: direct_payment | insurance | government_scheme | rate_recovery | fee_based
        share_of_revenue: float
    payor_concentration: low | moderate | high
    payor_pricing_power: low | moderate | high
    payor_mix_evolution:
      direction: stable | shifting_to_public | shifting_to_private | consolidating | fragmenting
      pace: low | moderate | high
      narrative: string
    competitive_envelope:
      dimensions: list
      narrative: string
    asymmetries:
      - description: string
        direction: favours_incumbents | favours_entrants | favours_specific_segment
        materiality: low | moderate | high
```

### D.2 Archetype-specific positioning fields

Where this framework is used, the archetype's `archetype_specific` positioning schema (§8.3) must include the company-side analogues of the binding constraints. For banks, this means CET1 ratio, RWA intensity, liquidity coverage ratio, NSFR, NIM, cost-to-income, NPL ratio, deposit-funding share — the §9.4.1 banking driver set. For utilities, the analogue would be allowed rate of return, capex roll-forward, regulatory asset base. For healthcare, payor-mix and reimbursement-rate trajectory.

### D.3 Default driver range implications

Per §7.5 link 2, default driver ranges should be calibrated against the framework's findings:

1. Where binding constraints are severe (e.g. CET1 floor for banks), the corresponding driver (RWA intensity, required equity) has a hard floor; default ranges should not span values that imply breach without scenario justification.
2. Where payor pricing power is high (e.g. PBS reimbursement schedules), revenue-growth and margin default ranges should be capped relative to industries with weaker payor leverage.
3. Where the regulatory regime is protective of incumbents (e.g. four-pillars policy), default lifecycle stage tilts toward `mature` with durable ROIC; default terminal-ROIC bands should reflect that.

### D.4 Scenario sensitivity implications

The archetype's `scenario_sensitivity` block (§7.4) should reflect the framework's findings. Specifically:

1. `regulatory_cross_cutting.competition_policy_exposure` — set from Part A regulatory-dynamic findings.
2. `regulatory_cross_cutting.data_and_digital_regulation` — set where the regime has explicit digital provisions (open banking, consumer data right).
3. New `payor_sensitivity` sub-block (added to `scenario_sensitivity` when this framework is used): payor-mix sensitivity to recession scenarios; payor pricing-power sensitivity to fiscal scenarios; payor-concentration sensitivity to consolidation scenarios.

### D.5 Cross-check with Porter

After completing this framework, re-run the Porter `new_entrants` and `buyer_power` assessments with the regulatory and payor findings in view:

1. **New entrants.** Regulatory licensing is a Porter barrier (§3.7 in the Five Forces bank); the framework will have surfaced its strength. Confirm the Porter rating reflects what was found here.
2. **Buyer power.** Where the payor is not the end user, Porter's buyer-power analysis must address both — the end-user buyer-power dynamic and the payor-power dynamic. They differ; an industry can have weak end-user power and strong payor power (or vice versa).

---

## Worked example pointer

The banking archetype (WBC) will be the first archetype populated against this framework, as part of Step 9 of the build plan. The completed archetype YAML and the `data/industries/major_banks_au.md` narrative will serve as the worked example for subsequent archetypes using this framework.
