# Equity-bridge and valuation mechanics

**Status:** v0.1 — Phase 3.5 methodology, derived from working sessions 25 May 2026.
**Binds:** Step 6 production translator and Step 7 production DCF engine.
**Cross-references:** architecture spec §11.4.1 (derivations), §11.4.2 (consistency rules), §11.5 (AssumptionSet), §14 (Phase 3.5 spec).
**Companion artefacts:** `docs/phase_3_5_findings.md` (smoke-test calibration), `analyses/dnl/valuations/*.xlsx` (worked examples).

This document specifies the equity-valuation mechanics that sit between the impact-matrix-driven assumption set and the per-share output. It exists because the Phase 3.5 smoke-test surfaced several places where the original architecture short-cut judgements that should have been structured machinery — most importantly, growth assumed from a hardcoded scalar rather than derived from the scenario / industry / company chain, and an equity bridge that collapsed several distinct adjustments into a single net-debt line.

The methodology is presented as a set of principles + their structured implementations. Each principle carries a schema implication for Step 6.

---

## 1. Scope and applicability

This methodology applies to any FCFF-style DCF the framework runs. It is silent on residual-income / DDM mechanics required for bank archetypes — those will be a sibling document.

The unit of analysis is a **single company × single scenario** valuation. Comparative output across scenarios (per §6.2 of the architecture spec) is the framework's canonical view; this document specifies how each individual cell of that comparative grid is computed.

---

## 2. Revenue-growth derivation (scenario → industry → company)

The core principle: **a company's revenue growth path under a given scenario is computed from a chain of named layers, not from an opaque baseline parameter.** Each layer carries an explicit translation rule.

### 2.1 Scenario layer — `macro_baseline`

Each scenario YAML carries a `macro_baseline` block with the macro context the scenario implies:

```yaml
macro_baseline:
  developed_markets:
    real_gdp_growth: 0.020       # decimal, e.g. 2.0% pa
    inflation: 0.025             # decimal, gradually-normalising DM inflation
    nominal_gdp_growth: 0.045    # derived: (1+real)*(1+inflation)-1
  emerging_ex_china:
    real_gdp_growth: 0.040
    inflation: 0.040
    nominal_gdp_growth: 0.082
  china:
    real_gdp_growth: 0.040
    inflation: 0.020
    nominal_gdp_growth: 0.061
  # ... by region as relevant
```

These are the scenario's central macro views. They feed every industry archetype that consumes them.

### 2.2 Industry-archetype layer — `revenue_growth_translation`

Each archetype YAML carries a `revenue_growth_translation` block that specifies how scenario macro maps to industry volume and pricing:

```yaml
revenue_growth_translation:
  # How scenario macro maps to industry physical-volume growth
  volume_formula: |
    1.15 * scenario.global_mining_real_growth + 0.004
    # explosives volume tracks mining production with depletion uplift
  volume_inputs:
    - scenario.global_mining_real_growth  # derived from regional real GDP × commodity intensity
  
  # How industry pricing tracks input costs
  pricing_formula: |
    0.7 * scenario.developed_markets.inflation + 0.3 * scenario.gas_price_growth + 0.005
    # 70% inflation pass-through, 30% gas-cost-driven, 50bps productivity sharing
  
  # Sanity envelope (warn if computed growth outside this range)
  steady_state_revenue_growth_range: [0.03, 0.08]
```

The translation rule is **industry-specific** and **explicit in the data layer**. Different archetypes (industrial explosives vs banking vs biotech) will have completely different formulas because their economics are different.

### 2.3 Company-position layer — `revenue_growth_offsets`

Each company-position YAML carries a `revenue_growth_offsets` block that captures how the company differs from its archetype:

```yaml
revenue_growth_offsets:
  geographic_mix_adjustment:
    # company-specific weighting of regional growth rates
    weights:
      developed_markets: 0.90   # DNL: 55% US + 35% AU = 90%
      emerging_ex_china: 0.10   # DNL: 10% EMEA & LATAM
    # Output: weighted average of regional growth — applies as a multiplier
    # to industry growth rate to produce company-specific growth
  
  growth_pipeline_specific:
    # Named contracted volume ramps with their own time profiles
    - description: "DNEL Latin America ramp"
      annual_uplift_bps: 30
      time_profile: front_loaded_3_years
  
  company_vs_archetype_offset_bps: -50  # e.g., -50bps if mature-market weighting drags
```

### 2.4 Derivation

The translator computes, per year:

```
company_revenue_growth_y = 
    industry_revenue_growth_y    # from §2.2 applied to §2.1
  + company_pipeline_uplift_y    # from §2.3 growth_pipeline_specific
  + company_vs_archetype_offset  # from §2.3
```

For DNL Muddle Through specifically, the chain produces approximately **4.5% per annum nominal revenue growth** (DM real GDP 2.0% + inflation 2.5% → industry nominal ~5–6% via the explosives translation, less ~50bps for mature-market weighting, plus modest DNEL pipeline). This replaces the hardcoded 2.0% used in the original smoke-test.

### 2.5 Validator (§11.4.2 extension)

The translator emits a warning if any computed company revenue growth path falls outside the archetype's `steady_state_revenue_growth_range`. Drives an explicit analyst override or a revision of the translation rule.

---

## 3. EBIT-margin derivation

Same principle as revenue growth: base-year margin + transformation overlay + scenario-conditional deltas, each layer named and overridable.

### 3.1 Base-year margin

From the financials YAML `normalised_baseline.ebit_margin` (per the smoke-test calibration convention). Source-document referenced; rationale captured.

### 3.2 Transformation / strategic overlay (company-specific)

A `margin_glide_path` block on the company-position YAML captures known, scheduled margin movement that isn't scenario-conditional:

```yaml
margin_glide_path:
  # Year-by-year delta to base-year margin (bps)
  trajectory:
    - year: 1
      ebit_margin_delta_bps: +50
      rationale: "FY27: 50% of transformation residual delivered"
    - year: 2
      ebit_margin_delta_bps: +210
      rationale: "FY28: transformation complete; aligns to AUD 600m EBIT ambition"
    - year: 3
      ebit_margin_delta_bps: +260
      rationale: "FY29 onward: steady-state at completed transformation level"
  cap_at_year_5: true
```

For DNL the transformation overlay reflects the AUD 300m total EBIT uplift management has communicated, of which 65–75% is in the FY26 base year (per H1 disclosure).

### 3.2.1 Structural-headwind overlay (sister concept)

The transformation overlay captures known *tailwinds*. A symmetric `structural_headwind_overlay` block captures known *headwinds* — contract roll-offs, regulatory step-downs, customer-attrition schedules, technology-displacement timetables — that are scheduled, company-specific, and not captured by scenario-conditional margin deltas. Same shape as §3.2:

```yaml
structural_headwind_overlay:
  - id: us_gas_contract_rolloff
    description: "US long-term gas contracts roll 2028-2030; reverts to spot pricing"
    trajectory:
      - year: 3
        ebit_margin_delta_bps: -50
        rationale: "FY29: first tranche of contracts rolls off"
      - year: 4
        ebit_margin_delta_bps: -100
        rationale: "FY30: further tranche rolls off; cumulative -100bps"
      - year: 5
        ebit_margin_delta_bps: -150
        rationale: "FY31: majority at spot; cumulative -150bps"
```

Per the substack discipline (Stephen Reid + Tony Carlton, valuationmatters1.substack.com): structural headwinds that are knowable should be **built into the cash-flow path explicitly**, not deferred to terminal-state hand-waving or hidden behind discount-rate adjustments. The DNL Muddle Through worked example (analyses/dnl/valuations/dnl_muddle_through_valuation_v3.xlsx) applies the US gas-contract roll-off as a -50/-100/-150bps cumulative drag in Y3/Y4/Y5, partially offsetting the transformation overlay.

Future refinement: the headwind can be made scenario-conditional where the magnitude legitimately differs across scenarios (e.g., post-roll-off gas pricing depends on the scenario's gas-price trajectory).

### 3.3 Scenario-conditional margin deltas

The existing impact-matrix mechanism (`gross_margin`, `input_cost_pass_through`, `sga_pct_revenue` drivers) layers on top of the transformation overlay. These are scenario-specific and represent industry-level effects (cost compression in Stagflation, etc.).

### 3.4 Final margin computation

```
company_ebit_margin_y = 
    base_year_normalised_margin
  + transformation_overlay_y       (from §3.2)
  + scenario_margin_deltas_y       (from impact matrix)
```

---

## 3.5 Discount-rate discipline — single WACC across scenarios

**The discount rate (WACC) is set at the valuation date and held constant
across scenarios.** This is the single most important discipline in the
methodology and was confirmed during the 28 May 2026 working session.

### 3.5.1 Rationale

Each scenario already prices its risk through the cash-flow path: Stagflation
has compressed margins and slower growth; Disorderly Climate has elevated
capex and lower terminal growth. The dispersion of cash flows across
scenarios *is* the framework's representation of risk.

If we also use a higher discount rate in a stress scenario, we are
penalising the same risk twice — once via the cash flows the scenario
describes, and again via the rate at which those cash flows are discounted.

The marginal investor's required return on capital at the valuation date is
a single number, set by today's market conditions. It does not change
conditional on which future state is realised. The CAPM beta we apply
(typically 1.0–1.3 for industrial cyclicals) already captures the
systematic risk of the entire conditional cash-flow distribution —
including the possibility of stress states. Layering scenario-conditional
ERP or Rf adjustments on top compounds that.

This was an open decision in architecture spec §12; it is resolved here in
favour of single-WACC discipline.

### 3.5.2 Practical mechanics

- One WACC is computed from the `WaccBuild` components at the valuation
  date per §2 (Rf, ERP, β, Rd_pretax, tax, market-value weights).
- The same WACC is applied to every scenario's explicit-period cash flows
  and to the terminal-value discounting.
- Impact-matrix rate-driver entries (Rf delta, ERP delta, country risk
  premium delta) are retained as scenario context — they describe the macro
  state the scenario implies — but **do not flow into the DCF discount
  rate**.
- Where macro-rate changes affect company financing economics (e.g., a
  scenario where the company's debt cost rises), the effect appears as
  **higher interest expense in the P&L of that scenario** (compressing
  NOPAT and FCF), not as a higher discount rate.

### 3.5.3 User override (sensitivity)

The DCF workbook exposes an "Applied WACC" cell. By default this cell is
formula-linked to the `WaccBuild` components. Users can override the cell
to test sensitivity to a different rate. This is an explicit, deliberate
sensitivity exercise — not a scenario-conditional flow-through. Overrides
should carry an analyst-facing comment explaining the rationale (e.g.,
"sensitivity at WACC -100bps to reflect possible re-rating").

### 3.5.4 Exception: terminal growth

Terminal growth *is* held scenario-conditional and the impact-matrix
`terminal_growth_rate` delta drivers do flow through.

Rationale: terminal growth represents a structural economic state (the
asymptotic real growth path of the economy in that scenario), which
legitimately differs across boundary scenarios. This is not a re-pricing of
risk; it is a description of the long-run economic regime the scenario
implies. Stagflation's terminal economy is structurally weaker than Orderly
Convergence's; that's a feature of the cash-flow path, not a hidden
discount-rate adjustment.

### 3.5.5 Schema implications

- Layer 4 driver catalogue retains `risk_free_rate`, `equity_risk_premium`,
  `country_risk_premium`, `beta` drivers. They appear in the impact matrix
  for scenario-context purposes.
- Step 6 production translator MUST NOT push these into the DCF discount
  rate when computing scenario-conditional value. They flow into the
  scenario narrative and (optionally) into the interest-expense line of
  the P&L, not the WACC.
- The `terminal_growth_rate` driver IS scenario-conditional and flows
  through to the terminal-value calculation per §3.5.4.

---

## 3.6 Tax-rate discipline — effective glides to blended statutory

A clean conceptual distinction matters here:

- **Effective rate**: actual tax paid / pre-tax income. Captures everything —
  geographic mix, R&D credits, timing differences, JV income treatment,
  prior-year true-ups. Volatile year-to-year.
- **Blended statutory rate**: weighted average of statutory rates across
  jurisdictions, weighted by income earned in each. Structural; captures
  only the persistent geographic-mix advantage.

### 3.6.1 Discipline

Explicit-period tax rate is the effective rate (per management guidance);
terminal-period rate is the blended statutory rate. Linear glide between
the two over the explicit horizon captures the analyst's view that
transient benefits (R&D credits, timing differences, JV effects)
compress, while the structural jurisdictional-mix advantage persists.

### 3.6.2 Blended statutory calculation

```yaml
tax_rate_blended_statutory:
  jurisdictional_weights:
    - jurisdiction: us
      revenue_weight: 0.55
      statutory_rate: 0.26   # federal 21% + state ~5%
    - jurisdiction: au
      revenue_weight: 0.35
      statutory_rate: 0.30
    - jurisdiction: other  # mix
      revenue_weight: 0.10
      statutory_rate: 0.27
  computed_blended: 0.275   # weighted sum
```

All inputs user-overridable per the structured-component principle.

### 3.6.3 Single-rate consistency principle

The same blended statutory rate is used for:

(a) Terminal operating tax (NOPAT in terminal value)
(b) Cost-of-debt tax shield in WACC (Rd × (1 − t))
(c) Hamada re-levering of beta (β_L = β_U × (1 + (1−t) × D/E))

No "marginal vs effective" split for different uses within the model. One
rate, one source, three uses. Internal consistency principle (per Tara,
29 May 2026).

### 3.6.4 DNL worked example

- Effective rate FY26 (Y1): 22.5% (per management guidance midpoint 20-25%)
- Blended statutory (Y5/terminal): 27.5%
- Glide Y1-Y5: 22.5% / 23.75% / 25.0% / 26.25% / 27.5% (linear)

The 5pp gap closes over the explicit horizon. Persistent ~2.5pp gap to
Australian statutory (30%) reflects structural US-revenue weighting.

---

## 4. Equity-bridge discipline

This is the discipline for walking from enterprise value to equity value to value-per-share. The principle: **every adjustment is explicit, has an anchor date, and flags whether it's already on the balance sheet.**

### 4.1 Net-debt definition (narrow)

We use the company's reported net-debt definition (typically interest-bearing liabilities − cash − fair value of debt-hedging derivatives). This matches how the company reports and how the company defines its leverage covenants.

Consequence: operating provisions, dividend payables, ARO commitments, and contingent obligations are *not* in net debt. They land as separate add-backs in the equity bridge.

### 4.2 Structured `equity_bridge_adjustments`

The company-position YAML carries a structured list:

```yaml
equity_bridge_adjustments:
  - id: declared_unpaid_dividend
    description: "Interim dividend declared 11 May 2026, payment July 2026"
    amount_aud_m: 87.0
    direction: subtract_from_equity     # increases net obligations
    on_balance_sheet_at_anchor: no      # anchor = 31 Mar 2026, dividend declared 11 May
    treatment: add_back_in_full
    provided_for_at_anchor_aud_m: 0
  
  - id: phosphate_hill_aro_commitment
    description: "ARO funding commitment at Phosphate Hill sale completion (~AUD 126m)"
    amount_aud_m: 126.0
    direction: subtract_from_equity
    on_balance_sheet_at_anchor: partial
    provided_for_at_anchor_aud_m: 82.0  # reclassified to "Held for Sale" per H1 disclosure
    treatment: add_back_gap_only        # = amount - provided_for = 44
    
  - id: perdaman_contingent_receivable
    description: "Up to AUD 145m subject to operational milestones; expected 2027"
    amount_aud_m: 145.0
    direction: add_to_equity            # reduces net obligations
    on_balance_sheet_at_anchor: no      # AASB 15: variable consideration constrained
    treatment: probability_weighted
    probability: 0.50
    expected_value_aud_m: 72.5
```

### 4.3 Validator (§11.4.2 extension)

The translator emits an error (not warning) if any `equity_bridge_adjustment` lacks an explicit `on_balance_sheet_at_anchor` flag. This is the "don't accidentally double-count" check.

### 4.4 Restructuring-cost consistency rule

**If the forward forecast assumes the benefit of a restructure (lower run-rate cost base, exit from a loss-making business, transformation-programme margin uplift), the equity bridge must include the cash cost of executing the restructure, less any existing provision.**

Mechanically: each `transformation_overlay` or `margin_glide_path` entry on the company-position YAML carries a paired `execution_cash_cost` field with the same provisioning treatment as §4.2.

For DNL: the AUD 90m of remaining transformation EBIT uplift (assumed in margin glide) has associated cash execution cost. Management's H1 transformation IMI run-rate is ~AUD 4m per half = ~AUD 8m annualised, declining over 2 years. Total remaining cash cost ~AUD 12m. Adjustment to equity: subtract AUD 12m (less anything already provided).

### 4.5 Bridge presentation

The DCF tab presents the bridge as a transparent walk:

```
Enterprise value (from DCF)                  XXX
less: reported net debt (at anchor)         (XXX)
less: net debt walk-forward to valuation    
        Capex paid in period                  (X)
      + Operating cash flow earned in period   X
      + Buyback completed in period            X    [value-neutral; see §5.2]
      + New dividend declared in period       (X)   [included via §4.2]
less: equity_bridge_adjustments
      Declared but unpaid dividends           (X)
      ARO commitments (less provided)         (X)
      Restructure execution cash cost         (X)
      Contingent receivables (prob-wtd)        X
= Equity value to shareholders               XXX
÷ Pro-forma diluted shares                   XXX
= Value per share                            AUD x.xx
```

---

## 5. Share-count discipline

### 5.1 Principle: latest reported, anchor-date-paired

Use the latest reported issued share count, paired with the net-debt position at the same balance-sheet date. **Do not project the buyback forward.**

### 5.2 Rationale

On-market buyback at fair value is value-neutral: paying $X for $X of equity changes neither enterprise value nor per-share value, only the ownership split. Projecting buyback completion into the share-count denominator (without correspondingly walking forward net debt by the cash spent) double-counts the benefit.

The exception is a buyback large enough to push the share price materially (rare; for a programme of <10% of market cap absorbed over 12+ months, the price impact is typically not material).

### 5.3 Practical resolution

The `share_statistics` block on the company financials YAML carries:

```yaml
share_statistics:
  shares_outstanding_at: 2026-03-31
  shares_outstanding: 1770000000       # ~1,770m at H1 anchor date
  shares_outstanding_source: "Back-solved from H1 NPAT ex IMIs / EPS ex IMIs; period-end estimate net of H1 buybacks"
```

The same `as_at` date must match the `net_debt` anchor date.

### 5.4 Schema validator (§11.4.2 extension)

Emit error if `share_statistics.shares_outstanding_at` ≠ `derived_metrics.net_debt_at`. Forces analyst to pair them.

---

## 6. Underlying-earnings handling (IMIs / one-off adjustments)

### 6.1 Principle: show both bases, give the user context

**Don't strip judgement from the framework; surface it to the user with context.** For every IMI / non-recurring item, run two parallel DCFs (statutory basis and ex-IMIs basis) and present both. For each item, give the user:

- The amount (gross and after-tax)
- The P&L line affected (above-EBIT or below-EBIT; many IMIs hit EBIT)
- Frequency context (how often this kind of item has appeared in recent years)
- A default lean (`accept_as_one_off | partial_recur | reject_as_recurring`) derived from a small taxonomy table
- A user-overridable toggle

### 6.2 Default-lean taxonomy

A reference table that maps the stated nature of an IMI to a default lean:

| Stated nature | Default lean | Rationale |
|---|---|---|
| Discontinued operations / divestment | accept_as_one_off | Genuinely structural; won't recur |
| Impairment of acquired goodwill / intangibles | accept_as_one_off | Singular write-down event |
| Litigation / legal settlement | accept_as_one_off | Discrete event |
| Acquisition integration (Year 1-2 post-deal) | accept_as_one_off | Defined-period transition |
| Acquisition integration (Year 3+) | reject_as_recurring | Should be in BAU by now |
| Restructuring / transformation (first 2 years) | accept_as_one_off | Defined programme |
| Restructuring / transformation (Year 3+) | partial_recur | Becoming BAU; flag for user |
| ARO revaluation | accept_as_one_off (first time); partial_recur (if repeated) | |
| Foreign-currency translation impact on debt | accept_as_one_off | Cash impact (not P&L impact); IMI classification debatable |

This taxonomy is the framework's judgement, set once. Application to any company is mechanical.

### 6.3 Per-company structured field

```yaml
underlying_adjustments_review:
  source_period: "H1 FY26 (6 months to 31 March 2026)"
  items:
    - id: phosphate_hill_impairment_exit
      after_tax_aud_m: 125.9
      gross_aud_m: 179.6
      p_and_l_line: above_ebit
      frequency_context: "First occurrence; tied to specific divestment"
      default_lean: accept_as_one_off
      user_override: null
    - id: ipf_distribution_settlement
      after_tax_aud_m: 11.2
      p_and_l_line: below_ebit
      frequency_context: "Tied to FY25 divestment; final settlement adjustments"
      default_lean: accept_as_one_off
      user_override: null
    - id: business_transformation_costs
      after_tax_aud_m: 3.9
      p_and_l_line: above_ebit
      frequency_context: "Appeared in FY24, FY25, FY26 H1 (3 consecutive years); fertilisers separation now complete so expected to roll off"
      default_lean: partial_recur     # borderline; show user
      user_override: null
```

### 6.4 Output panel

The DCF workbook presents:

- The full IMI register table (as above) on its own tab
- Two DCF columns: statutory-basis result and ex-IMIs-basis result
- The per-share difference between the two, so the user sees the swing
- An "applied basis" cell where the user picks the central case

For DNL the swing between statutory and ex-IMIs is dominated by Phosphate Hill (~AUD 126m after-tax in H1; annualised ~nil because the asset is sold). Excluding that gets us close to the AUD 161m ex-IMIs NPAT figure that's the legitimate forward-run-rate anchor.

---

## 7. Valuation-date mechanics

The valuation date is **explicit**, not implicit. Three distinct periods need handling:

### 7.1 Period A — Anchor date → Valuation date

The reported balance-sheet anchor is typically months stale (most recent half-year or annual). Between the anchor date and the valuation date, the company has earned cash, paid dividends, bought back stock, etc. The net-debt position at the valuation date is the anchor adjusted for these in-flight items.

```
Net debt at valuation date = Net debt at anchor date
                           − Operating cash flow earned in Period A
                           + Capex paid in Period A
                           + Buyback completed in Period A     [value-neutral; see §5.2]
                           + New dividends declared in Period A [also captured via §4.2]
                           ± Major capital events
```

Use run-rate estimates from the most recent reporting period (H1 typically) scaled by days-in-period. **Precision is +/− AUD 50m or so; document the estimate basis explicitly in the workbook.**

### 7.2 Period B — Valuation date → Year 1 start (stub)

The stub period from valuation date to the start of the first full fiscal-year forecast. For a company with a 30 September year-end and a valuation date of 25 May 2026, the stub is 128 days = 0.351 years.

**Treatment (Option X — own DCF line):**

```
PV(stub) = stub_FCF_pro_rated × 1 / (1 + WACC)^(stub_years / 2)
        # mid-stub discounting
```

Stub-period FCF is pro-rated from the next full fiscal year's forecast (e.g., 128/365 × Year-1 FCF).

This makes the stub-period cash flow visible to the reader as its own line, separate from the explicit-period forecast.

### 7.3 Period C onward — Explicit forecast with mid-period discounting

For Year N of the explicit forecast (N = 1..5), discount factor:

```
discount_factor_y_N = 1 / (1 + WACC) ^ (stub_years + N - 0.5)
```

Where the `- 0.5` is the mid-period convention (cash flow is treated as arriving at the mid-point of the year, not the end).

### 7.4 Terminal value

The Gordon-growth terminal value sits at the end of Year 5 (= start of perpetuity). Discount back at:

```
discount_factor_terminal = 1 / (1 + WACC) ^ (stub_years + N_explicit)
```

(Year 5 end-period, not mid, because terminal value is valued as a perpetuity from that point.)

### 7.5 Anchor-date discipline (schema requirement)

Per-field `as_at_date` on the small number of fields where timing actually matters:

```yaml
financials:
  income_statement_anchor:
    period: "H1 FY26 (Oct 2025 - Mar 2026)"
    as_at_date: 2026-03-31
  derived_metrics:
    net_debt: 1260.8
    net_debt_at: 2026-03-31
  share_statistics:
    shares_outstanding: 1770000000
    shares_outstanding_at: 2026-03-31

valuation:
  valuation_date: 2026-05-25
```

Validator (§11.4.2 extension): warn if income / debt / shares anchor dates are inconsistent.

---

## 8. What's parked

**Governance assessment (cost-of-equity premia for governance concerns).** Methodology TBD; see Tara's blog (valuationmatters1.substack.com) for the scepticism on ad-hoc alpha-style adjustments. Provisionally, governance flows through scenario-conditional events (probability-weighted) or beta (if structural), not through a separate company-specific risk premium. Revisit when populating a company where governance is materially in question.

**Stochastic / probability-weighted scenario overlay.** Per architecture spec §3 Open Decision.

---

## 9. Schema additions required (Step 6 implementation list)

Cross-references to existing pydantic modules under `src/vcc_valuations/schemas/`:

1. **`scenario.py`** — add `macro_baseline` block (regional real GDP, inflation, nominal GDP).
2. **`industry.py`** — add `revenue_growth_translation` block (formula + inputs + sanity range).
3. **`company.py`** — add `revenue_growth_offsets` block; add `margin_glide_path` block; add `equity_bridge_adjustments` structured list; add `underlying_adjustments_review` structured list; add per-field `as_at_date` on net_debt and shares_outstanding.
4. **`assumption.py`** — extend `AssumptionSet` to carry the computed revenue-growth path (year-by-year, with provenance to scenario / industry / company layers).
5. **`driver.py`** — add `dividend_payout_ratio` as a derived driver; add `buyback_completion` as a non-primary driver.
6. **Translator** (`src/vcc_valuations/translator.py`) — implement the §2 chain; implement the §3 margin overlay; implement the §4 bridge construction; implement the §7 period mechanics.
7. **DCF engine** (`src/vcc_valuations/dcf/`) — Phase 3.5 stub replaced with: stub-period FCF line, mid-period discounting, statutory vs ex-IMIs parallel runs, equity bridge from structured adjustments.
8. **Validators (§11.4.2)** — extend with: anchor-date consistency check, restructuring consistency check, equity-bridge-adjustment completeness check, revenue-growth-path sanity range check.

---

## 10. Worked example reference

The DNL Muddle Through workbook (`analyses/dnl/valuations/dnl_muddle_through_valuation.xlsx`) is the canonical worked example. Each principle in this document is implemented and visible in the workbook. The workbook is the integration test: if it can't be built straightforwardly from a company position YAML + scenario YAML + industry archetype YAML + this methodology, the methodology has a gap.


---

## 14. Source-document ingestion discipline

Per the discipline that emerged 29 May 2026 (after the DNL Q1–Q8 review
surfaced material content in the H1 investor presentation that was missed
in the initial calibration pass).

### 14.1 Per-company document register

Each company carries a `documents` register listing every ingested source
with title, date, ASX announcement number / URL, key insights extracted,
and status (read / unread / superseded). Lives in
`data/companies/<id>/documents.yaml` or on the company financials YAML.

### 14.2 Standing ingestion checklist

For any ASX-listed reporting company, the following document types are
read at population and at each refresh cycle:

(a) **Investor presentation** (slides) — often the most incrementally useful
beyond the announcement narrative; contains segment-level detail,
sensitivities, transformation trackers, transition cash flows.

(b) **Half-year results announcement** (Appendix 4D-paired ASX release) —
press-release-style narrative.

(c) **Statutory half-year financial report** (Appendix 4D + full HY
accounts) — precision on balance-sheet line items; statutory vs net-
working-capital presentation; notes detail.

(d) **Half-year dividend declaration** (ASX 3A.1).

(e) **Latest annual report** (Appendix 4E + statutory annual accounts).

(f) **Continuous disclosure announcements since last reporting period** —
particularly anything M&A, financing, guidance, or ratings related.

(g) **Conference call / analyst day transcripts** — Q&A often surfaces
nuance not in prepared remarks.

(h) **Sustainability / TCFD reports** — particularly relevant for climate
scenarios.

### 14.3 Major-corporate-event trigger

When a corporate-action overlay is active (demerger, acquisition, disposal,
recapitalisation, scheme), the framework requires explicit reference to
the specific announcement document(s) covering that event.

Schema validator: "If `corporate_action_overlay.active = true`, then
`documents` must include at least one entry tagged
`event_type = corporate_action`." Refuses to validate company positions
that omit known event documentation.

### 14.4 Refresh cadence

(a) Half-year-reporting companies: refresh within 2–4 weeks of each H1/H2
release.

(b) Quarterly-reporting companies: refresh quarterly.

(c) Material announcements (>5% impact on equity value): refresh on receipt.

(d) Methodology / spec changes: applied via top-down sweep (editorial pass
across all companies).

### 14.5 Source-citation discipline in deliverables

Every calibration anchor in the valuation workbook cites its document
source: title, date, specific page / slide reference. The "Sources" tab
in the worked-example workbook (DNL v4) is the pattern.

### 14.6 Handoff to data workstream

Ben's data workstream populates the documents register and key-insight
summaries per company. The valuation workstream consumes the register;
no direct web research that doesn't pass through the register.

This gives the data workstream a clear spec ("here's what to ingest per
company") and the valuation workstream a clear input ("the register is
what we read").


---

## 15. Bank-specific valuation conventions

Added 12 June 2026 as a methodology fork for ADI-regulated banking
companies. The framework's industrials-oriented core (§§2–7, §10) does
not transfer cleanly to banks: the FCFF / WACC / EV→equity bridge
mechanic does not apply, and the revenue / cost / capital structure of
a bank is materially different from an industrial corporate. This
section specifies the conventions a bank-style valuation must follow.

The fork is additive. The industrials methodology in §§2–7 is unchanged
and continues to apply for non-bank companies. Banks invoke §15 instead
of (not in addition to) §§2–4 for the operating-cash-flow build; §§5–7
(share-count discipline, IMIs, valuation-date mechanics) remain
shared discipline.

### 15.1 Scope and rationale

(a) **Applies to**: ASX-listed Australian banks regulated as ADIs under
APRA Prudential Standards (the Big Four plus regional ADIs such as
Bendigo and Bank of Queensland). Non-ADI lenders that take wholesale
funding only (e.g., Latitude, Pepper) are bank-adjacent — assess case by
case; default to industrials methodology unless the regulated-capital
discipline binds.

(b) **Why a fork**: a bank's cash flows are intermediated. The
shareholders' claim is on the residual after depositor and
debtholder claims at fair value; "enterprise value" before debt
deduction is not a meaningful intermediate quantity. Net interest
income substitutes for "revenue × margin"; regulatory capital
substitutes for the capex constraint; credit losses substitute for
the gross-margin shock under stress.

(c) **What's retained**: scenario layer (§§1, 2.1), share-count
discipline (§5), IMIs / one-off handling (§6), and valuation-date
mechanics (§7) all apply unchanged. The Five Forces spine (§3.3)
applies with a bank-specific archetype (§15.6 below).

### 15.2 Discount rate — cost of equity, not WACC

(a) **Principle**: bank valuations are conducted entirely on the
equityholder claim. The discount rate is the cost of equity (Re),
not WACC. WACC requires a clean separation of equity and debt
claims at market value; for a bank, the deposit and wholesale-debt
mix is the production input, not the financing structure.

(b) **CAPM construction**: Re = Rf + β × ERP, identical to §3.5.2
except β is sourced bank-specific. Defaults:
   - Risk-free rate: 10-year Australian Commonwealth bond yield (same
     as §3.5.2).
   - ERP: Damodaran-style mature-Australia premium (same as §3.5.2).
   - β: selected via the peer-triangulation discipline at §15.2(c) below.
     Bank-specific β must be documented in
     `data/companies/<id>.yaml/bank_specifics/cost_of_equity_build`.

(c) **Beta-selection discipline — peer triangulation, not mechanical use
of measured β.** Measured β carries material statistical noise:
window-dependent, index-choice-sensitive, regime-shift-affected. The
framework selects β via reasoned peer triangulation rather than
mechanically using the subject company's measured β. The procedure:

   1. Catalogue measured β for the subject company plus 3–5 directly
      comparable peers from the same archetype, with the measurement
      source (provider, index, window) documented.

   2. Identify outliers and document the structural reason — e.g.,
      institutional / international revenue dilution; recent corporate
      action disrupting price relationships; small free float; index
      weight effects.

   3. Reason about where the subject company's "true" β should sit
      relative to the comparable peer cluster, using business-mix
      logic similar to the Five Forces decomposition: defensive
      franchise lower, cyclical / wholesale exposure higher, mix-shifts
      toward growth lines or markets income higher, mortgage-book
      weighting lower.

   4. Select an appropriate β within the comparable-peer-implied range.
      The selection must be documented in
      `bank_specifics.cost_of_equity_build.beta_selection_rationale`
      with the peer table, identified outliers, and the comparison logic.

   5. Both the measured β for the subject company and the selected β
      are shown alongside each other for transparency. The difference
      and its rationale are made explicit.

The principle is general — it applies equally to industrials (§3.5.2).
Future industrials calibrations should be back-applied via peer-
triangulation against the industry archetype peer set rather than
relying on the subject company's measured β alone.

(d) **Single-Ke discipline**: per §3.5, the cost of equity is held
constant across scenarios for a single bank. The scenario asymmetry
is in the cash-flow path (NII, credit losses, capital actions), not
in the discount rate.

(e) **No WACC computed**: bank workbooks should not include a WACC build
sheet. The cost-of-equity build replaces it.

### 15.3 Revenue decomposition — NII + non-interest income

(a) **Net interest income (NII)** is the dominant revenue line.
Decomposed as:

  NII (year t) = Average interest-earning assets (year t) × NIM (year t)

where average interest-earning assets is the simple average of
opening and closing balances over the year, and NIM is the
period-average net interest margin (bps on average interest-earning
assets).

(b) **Volume driver**: average interest-earning assets growth is the
scenario-conditional driver, decomposed into the major segments
(housing, business, institutional, deposits/treasury) with each
mapped to its own macro driver. Housing loan growth maps to housing
turnover × system-share assumption; business lending maps to non-
mining business investment; institutional maps to wholesale credit
issuance volumes; deposits to household savings.

(c) **NIM driver**: NIM is scenario-conditional, decomposed into:
   - Asset yield: cash rate + lending margin to cost-of-funds.
   - Funding cost: weighted average of deposit rate + wholesale debt
     spread.
   - Hedge contribution: bank-specific structural-hedge income from
     replicating-portfolio strategies (material for retail-deposit-
     funded banks).
   - Mix shift: housing-vs-business segment weights moving over time.

(d) **Non-interest income** decomposed into:
   - Fee income (lending fees, account-keeping, FX, etc.).
   - Markets income (treasury trading, FX, derivatives).
   - Wealth/insurance (where applicable; mostly divested for Big Four
     except still material at some regionals).

Each non-NII line carries its own scenario translation.

### 15.4 Credit-loss / impairment expense

(a) **Principle**: credit losses are a primary scenario driver for
banks, not a residual. The credit-loss expense (% of gross loans p.a.)
is scenario-conditional and explicit in the forecast.

(b) **Through-the-cycle baseline**: each bank carries a normalised
through-the-cycle credit-loss rate (typical Big Four range 15–25bps
of gross loans). This is the Muddle Through anchor.

(c) **Stage 1-2-3 mechanics**: expected losses computed under AASB 9
on a 12-month basis (Stage 1) and lifetime basis (Stage 2-3). Source
the loss-stage composition from Pillar 3 / financial statements
(typically Tables CR1, CR3) and forecast stage migration under
scenario stress.

(d) **Scenario calibration**: credit-loss rates by scenario must
reference the housing-loan and business-loan loss-given-default
assumptions in the scenario YAML's `macro_baseline.credit_cycle`
block. A disorderly-climate scenario, for instance, runs much higher
losses on stranded-asset business exposures than Muddle Through.

(e) **Specific provisioning vs general overlay**: banks routinely
carry general-economic-overlay provisions on top of model-based
expected losses (post-COVID a permanent feature). The methodology
treats general overlay movements as IMIs (§6) unless the scenario
itself drives a structural change in the overlay.

### 15.5 Capital constraint — CET1 binds payout and growth

(a) **Principle**: a bank's dividend payout and asset growth are
constrained by its Common Equity Tier 1 (CET1) capital ratio. The
ratio must remain above a regulator-set minimum (typically 11.5%
under APRA's "unquestionably strong" framework, including a
countercyclical buffer of 1.0%, plus a domestic systemically
important bank (D-SIB) surcharge of 1.0% for the Big Four) plus
a management buffer (typically 50–150bps above the minimum).

(b) **The constraint binds two things**:
   - **Asset growth**: nominal interest-earning asset growth × risk-
     weight density × CET1 ratio = required CET1 capital generation
     per year. Banks generate CET1 from retained earnings (cash
     earnings × (1 − payout ratio)).
   - **Payout ratio**: the payout ratio is the residual after
     CET1 requirements are met. A bank running at the CET1 floor
     under stress must retain more earnings (lower payout) to
     rebuild capital.

(c) **Forecast mechanics**: each forecast year computes
   - Cash earnings (NII + non-NII − operating expenses − credit losses − tax)
   - CET1 generated = cash earnings × (1 − payout ratio target)
   - Required CET1 = ΔRWA × CET1 target ratio
   - If generated < required, payout is forced down; if generated >
     required by a buffer, the excess is returnable (buyback or special).

(d) **Pillar 3 mapping**: the RWA composition and risk weights come
from Pillar 3 KM1 / OV1 / CR4. Forecast risk-weight density (RWA /
exposure) holds flat by default; scenario-conditional risk-weight
movements (e.g., disorderly climate → higher housing risk weights
under climate-adjusted credit modelling) are captured as a separate
driver.

(e) **APRA buffer regime**: the methodology assumes the current APRA
buffer regime continues. Regulatory-change scenarios (e.g., higher
D-SIB surcharges) are explicitly modelled in the scenario layer's
`regulatory` block.

### 15.6 Five Forces — bank industry archetype

The Five Forces (§3.3) for a regulated retail-and-business banking
archetype:

(a) **Buyer power**: LOW (households, SMEs) to MODERATE (corporates).
Switching costs in transaction banking, mortgage relationships, and
business banking are high. Mortgage rate sensitivity is asymmetric:
new business is rate-competitive, back book is sticky.

(b) **Supplier power**: depositors are the primary funding "supplier"
and have switching options (term deposits vs at-call; one bank vs
another via comparator sites; broker channel). Wholesale funders
have credit-spread power but tend to be price-takers across the Big
Four.

(c) **Threat of new entrants**: LOW (regulatory licensing, capital
requirements, distribution scale). Fintech entrants are typically
narrow-product (BNPL, neobank deposits) and have not displaced the
oligopolistic core.

(d) **Threat of substitutes**: LOW to MODERATE. Non-bank mortgage
lenders (warehouse-funded) take share when bank credit constraints
bind; superannuation funds substitute for term deposits over long
horizons; fintech payments substitute for transaction-account
revenue but not the funding base.

(e) **Rivalry**: MODERATE. Oligopolistic among the Big Four; price
discipline holds in benign periods, breaks under share-loss
pressure (front-book mortgage pricing wars are the canonical
example). Regional banks and macquarie compete on margin in
specific segments.

(f) **Company-position decomposition**: each bank's position relative
to the Big-Four average is decomposed force-by-force per §3.3, with
quantified impact on volume growth, NIM, or cost-to-income. The
positions are not symmetric across the Big Four — CBA's deposit
franchise dominance, Westpac's mortgage-book scale, NAB's business
banking strength, ANZ's institutional / international footprint each
manifest differently.

### 15.7 Bank-specific equity adjustments

The §4 equity bridge collapses for banks (no EV→equity step), but
bank-specific equity-side adjustments still apply:

(a) **AT1 / Tier 1 hybrid securities** (Capital Notes etc.) — sit
above ordinary equity in the capital stack. Treated as a deduction
from book equity (and from per-share value) when computing
ordinary-equity-per-share. Distinct from sub debt (Tier 2), which
is debt at fair value and does not affect equity per share.

(b) **Deferred tax assets** — banks routinely carry material DTAs
(loss-recognition timing, expected-loss provisioning). The CET1
calculation deducts most DTAs from regulatory capital; the
accounting equity does not. Sanity-check: book equity per share
vs CET1 + DTA + intangibles per share.

(c) **Software intangibles** — capitalised software typically
deducted from CET1. Same sanity-check.

(d) **Goodwill** — fully deducted from CET1. Reduces capacity to
return capital from book equity.

(e) **Capital actions**: announced but not yet completed buybacks
treated per §5.2 (share-count discipline). Off-market buybacks
(common for Australian banks for franking-credit reasons) follow the
same treatment as on-market.

### 15.8 Terminal value — ROE fade to Ke

(a) **Convention**: terminal value for a bank uses a
Gordon-growth-on-equity formulation:

  TV_equity = Equity_T × (ROE_T − g) / (Ke − g)

where ROE_T is the through-the-cycle terminal ROE and g is the
terminal asset-growth rate.

(b) **ROE convergence**: terminal ROE should fade to a level
consistent with the bank's franchise quality. Australian Big Four
typical range 10–13% through-cycle; regional banks 8–11%. A bank
sustaining terminal ROE materially above its cost of equity must
have a defensible competitive advantage (the Big Four oligopoly
itself qualifies; rebuild has to be re-argued for each).

(c) **Payout sustainability**: terminal payout ratio = 1 − g / ROE_T.
This ties the terminal growth to retained earnings via the
sustainable-growth identity. Per §3.5.4 the terminal growth rate
itself can be scenario-conditional (different macro outlooks → 
different sustainable growth).

(d) **Capital surplus distribution**: a bank with CET1 above target
in the terminal period distributes the surplus before computing
terminal value. The terminal book equity used in TV is the
capital-target-adjusted figure, not the latest reported.

### 15.9 Schema implications

(a) **New schema fields for `data/companies/<id>.yaml` (banks):**
   - `bank_specifics.average_interest_earning_assets` (period-anchored)
   - `bank_specifics.nim_decomposition` (asset yield, funding cost,
     hedge contribution)
   - `bank_specifics.credit_loss_through_cycle` (bps p.a. of gross
     loans)
   - `bank_specifics.cet1.actual`, `bank_specifics.cet1.target_minimum`,
     `bank_specifics.cet1.management_buffer`
   - `bank_specifics.rwa_composition` (housing, business, institutional,
     other; with risk-weight density per segment)
   - `bank_specifics.at1_hybrid_outstanding` (AUD m face)
   - `bank_specifics.dta_balance`, `bank_specifics.software_intangibles`
   - `normalised_baseline.cost_of_equity_build` (replaces
     `wacc_build` for banks)

(b) **New schema fields for `data/industries/<id>.yaml` (bank archetype):**
   - `bank_archetype.regulator` (APRA / RBNZ / etc.)
   - `bank_archetype.cet1_floor` (regulatory minimum)
   - `bank_archetype.credit_cycle_anchor` (through-cycle loss rate
     for the archetype)
   - `bank_archetype.rwa_density_anchor` (per segment)

(c) **New schema fields for `data/scenarios/<id>.yaml` (banks):**
   - `macro_baseline.credit_cycle` (housing-loan LGD, business-loan
     LGD per scenario)
   - `macro_baseline.cash_rate_pat