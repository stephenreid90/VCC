# VCC Valuations — Scenario-Based Equity Valuation Module
## Architecture & Design Specification

**Version:** 0.1 (Draft)
**Date:** 21 April 2026
**Status:** Working draft for mark-up and iteration
**Scope of this phase:** Layers 1–6 (the "assumptions engine"). Layers 7 (DCF) and 8 (interface) are described at a high level only and deferred to later phases.
**Review convention:** Open issues raised during section-by-section review are captured as an `X.1 Review items` subsection at the end of the relevant section. Search the document for "Review items" to surface all open issues in one pass. Items in these subsections are candidates for cross-review with Ben's data-sourcing workstream.

---

## 1. Purpose

This module provides a structured, auditable framework for valuing listed equities under multiple future-world scenarios. It decomposes the valuation task into a cascade of analytical layers, each with an explicit schema, so that scenario views, industry structure, company positioning, driver logic, and valuation assumptions can all be inspected, challenged, and updated independently.

The core design principle is that the value of a scenario-based valuation module does not live in the mechanics of the DCF — it lives in the reasoning that gets you to defensible assumptions. This specification therefore front-loads effort on layers 1–6 (scenarios → industry → positioning → drivers → linkage → assumption translation) and treats the DCF as a downstream consumer of those assumptions.

The MVP output, for each subject company in each scenario, is:

1. A clean, auditable set of forecast assumptions (revenue growth trajectory, margin path, capex intensity, working-capital behaviour, risk/discount-rate inputs, terminal-state view).
2. The explicit reasoning chain that produced those assumptions — traceable from world scenario → industry impact → company impact → driver movement → assumption value.

A future extension of the module (in layer 8) will enable users to inspect each assumption, assess whether they agree with it, and modify it to see the downstream valuation impact. The schema and layer boundaries are designed so that user-edited assumptions can be flagged as overrides and compared against the framework-derived baseline, preserving auditability.

The target user base is intentionally left undetermined at this stage. Internal analyst use is the working assumption; broader external use (client-facing or licensable) will be considered if the module proves valuable in practice. Design choices should favour generality over any specific user profile until this resolves.

---

## 2. Scope Decisions — Locked

1. **Technology stack.** Python engine (pandas, numpy, pydantic) with a web interface delivered as a **FastAPI backend** (exposing the engine as a JSON API) plus a **Vue frontend** (consuming that API). This is more initial engineering effort than a Streamlit-only approach but gives full UX flexibility for the eventual interactive assumption-inspection and modification features (§1), cleaner separation between engine and UI, and a clean path to later deploying the engine as a service (e.g., for a future client-facing tool).
2. **Scenario count.** Three to six named, qualitatively distinct scenarios. Scenarios must differ on *multiple dimensions* — not simply severity dials on a single axis. Exact count within the 3–6 range to emerge from the scenarios workshop.
3. **Scenario-to-driver linkage.** Explicit impact matrix of the form `scenario × industry archetype × driver → directional impact and magnitude bucket`, with company-level analyst overrides permitted and documented with reason codes. Two structural nuances are recognised: (a) a company may span multiple industry archetypes (e.g., IPL across industrial explosives and nitrogen fertilisers), in which case each business segment references its own archetype matrix and contributes a weighted share to the company-level assumption set; and (b) an industry archetype may have few peers in practice (e.g., specialty plasma therapeutics, where CSL is effectively the dominant player), in which case the archetype matrix may closely track the subject company. The layer structure is retained in the thin-archetype case because writing down the industry-reference view remains analytically useful and preserves the override mechanism for future peers.
4. **Test companies.** Incitec Pivot Limited (IPL), CSL Limited (CSL), Westpac Banking Corporation (WBC). All ASX-listed, spanning three genuinely different archetypes: industrial chemicals / mid-stream commodity exposure; defensive global healthcare; regulated domestic financial.
5. **Forecast horizon.** Parametric per company-scenario combination. Schema supports both 5 explicit years + terminal and 10 explicit years + terminal. Default selection deferred until scenarios are specified, on the basis that some scenarios may have multi-stage arcs that only make sense over 10 years, while others may resolve within 5.
6. **Data as data; logic as code.** Scenarios, industries, and companies are represented as YAML (easy for domain experts to edit); linkage, translation, DCF, and UI are Python (easy for engineers to refactor).
7. **Currency handling — functional currency basis.** Each company's valuation is conducted in its **functional currency** — the currency of the primary economic environment in which the entity operates and generates cash flows — not necessarily its reporting currency (though for most of our subjects the two will coincide). Determining the functional currency is an explicit early step in company positioning (see §8). For multi-segment companies operating in materially different economic environments, segment-level functional currencies may differ from the consolidated view (IPL is the likely test case: Dyno Nobel operates globally with predominantly USD-denominated contracts and input costs, while Fertilisers Australia is a domestic AUD operation with AUD gas inputs and AUD farmer customers). Cross-company comparisons in the interface convert to a common display currency (default AUD) at spot; FX is a scenario variable.
8. **Workstreams and division of labour.** The engine build documented in this specification runs in parallel to a **data-sourcing workstream** led by Ben (collaborator). Ben's workstream is responsible for sourcing, curating, and updating the underlying financial, operational, and reference data the engine consumes. The interface between the two workstreams is the set of data schemas defined in §§6–11 of this document (scenarios, industry archetypes, company positioning, driver taxonomy, driver-movement outputs, base-year company financial snapshots). The engine workstream owns the schemas and is responsible for keeping them stable, versioning them cleanly when they change, and communicating changes in advance to the data workstream. The data workstream is out of scope for this specification but its outputs must conform to these schemas.

## 3. Scope Decisions — Open

1. Scenario themes — to be developed in a dedicated scenarios workshop before any engine code is written.
2. Default horizon per company — to be fixed once scenarios are specified.
3. Scenario probability weighting — whether to require explicit probabilities producing a blended expected-value output, or treat scenarios as a pure comparative framework. Both approaches have strong proponents and the choice materially affects how results are communicated. Tara to consult one or more economists before resolving. In the interim the schema supports both approaches; the MVP does not require probability assignment.
4. Stochastic overlay — deferred. Framework is deterministic by design, but schema should not preclude later addition of parameter uncertainty within scenarios.

---

## 4. Architecture Overview

The module is organised as a seven-layer cascade. Each layer consumes the outputs of the layers above and produces a structured object that the layer below consumes. Layer boundaries are defined by schemas, which means any layer can be rebuilt without breaking the others.

| # | Layer                              | Scope                                                           | Output                                     | Data or code?        |
|---|------------------------------------|-----------------------------------------------------------------|--------------------------------------------|----------------------|
| 1 | Scenario Library                   | Named future-world scenarios, company-agnostic                  | `Scenario` objects                         | Data (YAML)          |
| 2 | Industry Structure Framework       | Per-industry structure analysis                                 | `IndustryArchetype` objects                | Data (YAML)          |
| 3 | Company Positioning                | Subject company's position within its industry(ies)             | `CompanyPosition` objects                  | Data (YAML)          |
| 4 | Driver Taxonomy                    | Standardised list of value drivers and their units              | Driver schema                              | Code (constants)     |
| 5 | Linkage / Impact Matrix            | Scenario × industry × position → driver movements with overrides | `DriverMovementSet` per company × scenario | Code + matrix data   |
| 6 | Assumption Translation             | Driver movements → numerical forecast inputs                    | `AssumptionSet` per company × scenario     | Code                 |
| 7 | DCF Engine *(deferred)*            | Assumption set → valuation outputs                              | `ValuationResult` objects                  | Code                 |
| 8 | Interactive Interface *(deferred)* | Browsing, comparing, editing across layers                      | Streamlit app                              | Code                 |

The critical design principle: **the linkage layer (5) is where the intellectual work lives.** Translation to numerical assumptions (layer 6) is largely mechanical once the linkage is rigorous. If the linkage is loose, the module collapses into narrative plus hand-waved numbers regardless of how carefully layer 6 is implemented.

---

## 5. Repository Structure

```
vcc-valuations/
  design/
    architecture.md              this document
    schemas/                     formal JSON/pydantic schemas for each layer
    scenarios_workshop.md        TBD — output of scenarios workshop
  engine/
    scenarios/                   scenario loading and validation
    industry/                    industry-structure framework
    company/                     positioning analysis utilities
    linkage/                     impact-matrix application, override handling
    assumptions/                 driver → forecast-input translation
    dcf/                         phase-2 valuation engine
    utils/
  data/
    scenarios.yaml               named scenarios with macro variables
    industries/
      fertilisers_explosives.yaml
      specialty_biologics.yaml
      major_banks_au.yaml
    companies/
      ipl.yaml
      csl.yaml
      wbc.yaml
    impact_matrix/
      by_industry/               one matrix file per industry archetype
  api/                           phase-3 FastAPI backend (JSON API over the engine)
  frontend/                      phase-3 Vue frontend (consumes the API)
  tests/
  notebooks/                     exploratory analysis, calibration checks
  README.md
  pyproject.toml
```

Philosophy: scenarios, industries, and companies are **data** (YAML). Linkage, assumption translation, DCF, and interface are **code**. Domain experts can update scenarios or industry analyses without touching Python; engineers can refactor logic without re-entering domain content.

### 5.1 Review items (open — to be reviewed against Ben's data-sourcing workstream)

The following challenges were surfaced during Section 5 review but have not yet been resolved. They are flagged here for later review (including by Ben's Bot) to ensure the repository structure aligns with the data-sourcing workstream.

1. **Industry archetype files need splitting.** Current tree shows `fertilisers_explosives.yaml` as a single file, but §7.3 now treats industrial explosives and nitrogen fertilisers as two separate archetypes. Tree should split into `industrial_explosives.yaml` and `nitrogen_fertilisers.yaml`.
2. **Scenario file layout — one file vs many.** `scenarios.yaml` holds all scenarios in a single file, asymmetric with industries and companies (one file each). Given each scenario is a substantial object, one file per scenario (e.g. `data/scenarios/orderly_convergence.yaml`) would mirror the other patterns and make version-control diffs cleaner.
3. **Home for base-year financial snapshots.** Layer 6 (§11) requires company base-year financials (revenue, EBIT, capex, net debt, working capital etc.) at translation time. Options: (a) embedded in `data/companies/<co>.yaml` alongside positioning; (b) separate `data/financials/<co>.yaml`; (c) raw-source data under `data/source_data/` curated by Ben's workstream and hydrated at runtime. Tentative preference: (b). Needs alignment with Ben on how his data workstream ingests and updates these snapshots.
4. **Translation rules as data.** §11.5 open item 1 may push translation rules (direction × magnitude → bps/percentage deltas) into YAML. If resolved that way, add `data/translation_rules/` — organised by driver, by industry, or global (TBD).
5. **Outputs storage.** Current tree has no location for Layer 5 and Layer 6 outputs (`DriverMovementSet`, `AssumptionSet`). Decide whether these are computed on demand only, or cached to a top-level `output/` folder (e.g. `output/driver_movements/{company}_{scenario}.yaml`, `output/assumption_sets/{company}_{scenario}.yaml`). Caching would support audit and reproducibility and would make Layer 8 (interface) faster.
6. **Python packaging layout.** Engine folders are currently shown as flat directories. Best practice would be a `src/vcc_valuations/` package layout for cleaner imports, clean installability via `pip install -e .`, and to keep test code clearly separated from package code.

---

## 6. Layer 1 — Scenario Library

### 6.1 Purpose

A reusable catalogue of named future-world scenarios describing qualitatively different macro, geopolitical, technological, regulatory, and demand environments. Scenarios are **company-agnostic** — the same library applies to every subject company.

### 6.2 Scenarios as boundary cases

Scenarios are chosen to span the plausible range of futures along dimensions that matter for valuation. They are **boundary cases**, not probability-weighted coverage of every possible future: adding another scenario is worthwhile only if it changes the shape of the future in a way that materially affects valuation assumptions. Scenarios are therefore neither exhaustive (probabilities need not sum to 1) nor strictly hierarchical (they are not branches off a single base case); they are a chosen set of meaningfully different worlds.

### 6.3 Division of labour — scenario level vs industry level

Scenarios describe **world-level** conditions: macro, geopolitical, technology regime, regulatory environment, financial conditions, and demand environment. Industry-specific consequences (e.g., how "AI productivity boom" affects plasma-therapy R&D differently from explosives manufacturing; how physical climate risk affects a mining operation differently from a bank branch network) are captured at the **industry level** (§7), via industry attributes that determine how sensitive the industry is to each scenario dimension.

This separation keeps the scenario library reusable across industries and avoids duplicating industry-specific analysis inside every scenario. The practical implication: §7's industry-structure schema needs to capture industry attributes that mediate scenario exposure (labour intensity, physical-asset climate exposure, technology absorptive capacity, demographic sensitivity of demand, etc.), so that the Layer 5 impact matrix can translate world-level scenario dimensions into industry-specific driver movements.

### 6.4 Schema (draft)

```yaml
scenario:
  id: string                        # e.g. "orderly_convergence"
  name: string                      # display name
  version: string                   # e.g. "2026-Q2-v1"
  published: date
  narrative:                        # prescribed structure for comparability
    key_mechanism: string           # 1 paragraph — central logic of the scenario
    distinguishing_features: string # how it differs from other scenarios in the library
    leading_indicators: string      # what you'd see if this scenario were materialising
    disconfirming_evidence: string  # what would invalidate this scenario
  time_profile:                     # flexible, scenario-defined phases
    - phase: string                 # e.g. "initial_shock", "adjustment", "new_equilibrium"
      year_start: int
      year_end: int | null          # null = open-ended through terminal
      characterisation: string
  macro_variables:
    - variable: string              # e.g. real_gdp_growth_world
      units: string
      type: string                  # "time_series" | "regime"
      time_series:                  # populated when type == time_series
        - year: int
          value: float
          confidence_low: float | null
          confidence_high: float | null
      regime:                       # populated when type == regime
        label: string                # e.g. "fragmented", "bipolar", "open"
        description: string
  geopolitical:
    bloc_dynamics: string
    trade_policy: string
    resource_nationalism: string
  technology:
    productivity_regime: string
    disruption_vectors: list
  regulatory:
    climate_policy: string
    financial_regulation: string
    healthcare_regulation: string
  commodity_and_energy:
    oil_regime: string
    gas_regime: string
    metals_regime: string
    ag_regime: string
  demand_profile:
    consumer: string
    industrial: string
    infrastructure: string
    healthcare: string
  financial_conditions:
    policy_rates: string
    credit_spreads: string
    fx_regime: string
    equity_risk_premium: string
  probability: float | null         # optional; null = unweighted
```

### 6.5 Versioning and refresh cadence

The scenario library is refreshed on a **six-month cadence** to reflect evolving macro, geopolitical, and structural conditions. Each refresh bumps scenario versions (e.g. `2026-Q2-v1` → `2026-Q4-v1`), with intra-cycle amendments tracked as minor versions. Downstream objects (`DriverMovementSet`, `AssumptionSet`) carry a reference to the scenario version they were built against. When a scenario version changes, downstream objects referencing the old version are flagged as **stale** and must be regenerated. Industry analyses and company positions may also need revisiting where the scenario revisions alter the exposure landscape materially; those revisions are tracked under their own version fields.

### 6.6 Deliverables

1. Three to six populated scenarios (themes to be developed in dedicated scenarios workshop; see §3 open items).
2. Narrative (in the structured form above) plus quantified macro trajectories where feasible; regime-based encoding where a variable is structurally qualitative.
3. Internal consistency check — macro variables and regime values should move in logically consistent ways within each scenario (e.g. "stagflation persists" cannot have sticky inflation *and* falling policy rates).

### 6.7 Review items

1. **Scenario population.** Themes, count, and specific trajectories to be defined in the dedicated scenarios workshop (§3 open item 1).
2. **Probability-weighting.** Schema supports optional probability per scenario; the decision on whether to require, permit, or prohibit weighting is parked pending economist input (§3 open item 3).
3. **Industry-level scenario-sensitivity attributes.** §7 schema needs expansion to capture industry attributes that mediate scenario exposure (labour intensity, physical-asset climate exposure, technology absorptive capacity, demographic sensitivity, cyclicality amplitude etc.) — without these, the Layer 5 impact matrix cannot translate world-level scenario dimensions into industry-specific driver movements. Flagged for resolution during §7 review.
4. **Confidence-band convention.** Macro-variable time series support optional `confidence_low` / `confidence_high`. Convention for what those bands represent (analyst subjective range, forecaster-consensus range, historical regime-conditional range) to be specified.
5. **Version-staleness propagation.** Logic for flagging downstream objects as stale when a scenario version changes needs to be built into the engine. Specific rules (full regeneration required vs. diff-only, treatment of analyst overrides across versions) to be specified.

---

## 7. Layer 2 — Industry Structure Framework

### 7.1 Purpose

A standardised template for analysing the structure of an industry, independent of the subject company. Each of our three companies maps to one (or in IPL's case, two) industry archetypes. The archetype schema captures both the traditional industry-structure picture (Five Forces, concentration, cost structure, etc.) and the **scenario-sensitivity attributes** that allow the Layer 5 impact matrix to translate world-level scenario dimensions (per §6.3) into industry-specific driver movements.

### 7.2 Rating convention

All qualitative ratings in this schema use a three-point scale: **low / moderate / high**. Rationale:

1. Matches the magnitude encoding used in the Layer 5 impact matrix (small / moderate / large), so ratings translate cleanly into driver movement magnitudes without scale conversion.
2. Resists false precision — analyst judgment rarely distinguishes reliably between finer gradations on qualitative dimensions.
3. Robust against misuse — a three-point scale resists the temptation to compute averages or indices that are methodologically dubious.
4. Cheap to upgrade: if a finer scale is required later, a simple mapping (low=1, moderate=2, high=3) preserves all encoded judgments.

Where a dimension has a natural fourth bucket (e.g. capital intensity for industries like banking or mining), the schema allows `very_high` explicitly.

### 7.3 Lifecycle and disruption

The `lifecycle_stage` field captures where an archetype sits on its **returns-vs-cost-of-capital** trajectory:

1. **emerging** — Pre-commercial or early commercial. High outcome variance; returns not yet stabilised. Cost of capital often elevated due to uncertainty.
2. **growth** — Returns materially above cost of capital; market expanding. Excess returns attract entry and capital; incumbents can preserve them for a period through scale, IP, brand, or regulatory advantage.
3. **mature** — Returns converging to cost of capital as competition plays out. Market growth slowing to roughly GDP-adjacent pace. Most of the returns distribution sits near equilibrium.
4. **declining** — Returns persistently below cost of capital; secular demand contraction. Capital exits over time.

**Guiding principle: all industries eventually gravitate to a state where they can only earn their cost of capital.** Competition, substitution, and capital reallocation are the mechanisms. Growth-stage excess returns are transitory; declining-stage sub-cost-of-capital returns are transitory in the other direction. This principle is what gives long-dated DCFs their anchor.

**Innovation can reset the trajectory.** An industry that has reached "mature" can be pulled back into "growth" by a technological, regulatory, or demand-side innovation that re-opens excess-return opportunities — print media → digital publishing, utilities → renewables, vaccines → mRNA platforms, banking → digital/embedded finance. Old industries can become new again. The `disruption_vectors` list and the Five Forces analysis together capture the mechanisms of such transitions; `lifecycle_stage` captures the resulting returns state at the point in time the archetype is written.

**Disruption does not require a separate lifecycle value.** An industry being disrupted shows it through (i) rising threat of substitutes in the Five Forces analysis, (ii) rising threat of new entrants, (iii) intensifying rivalry, and (iv) specific mechanisms enumerated in `disruption_vectors` with direction (threat vs opportunity) and incumbency position. The same facts, read from the attacker's perspective, show opportunity rather than threat. Disruption is one phenomenon seen from two sides.

### 7.4 Schema (draft)

```yaml
industry_archetype:
  id: string                                  # e.g. "industrial_explosives"
  name: string
  version: string                             # track revisions; bump on material change
  geography: global | regional | national | multi_geographic
  submarkets:                                 # optional; populate when geography == multi_geographic
    - region: string                          # e.g. "US", "EU", "Asia_ex_Japan", "Australia"
      weight: float                           # revenue/EBIT share of archetype
      five_forces_overrides: {...}            # only forces that differ from parent
      regulatory_regime_overrides: {...}
      cyclicality_overrides: {...}
      notes: string
  five_forces:                                # parent-level / consolidated view
    buyer_power: {rating: low|moderate|high, rationale: string}
    supplier_power: {rating: low|moderate|high, rationale: string}
    new_entrants: {rating: low|moderate|high, rationale: string}
    substitutes: {rating: low|moderate|high, rationale: string}
    rivalry: {rating: low|moderate|high, rationale: string}
  lifecycle_stage: emerging | growth | mature | declining
  lifecycle_rationale: string                 # returns-vs-CoC framing per §7.3
  concentration:
    top_3_share: float | null
    structure: fragmented | consolidating | oligopoly | monopoly
  cost_structure:                             # the static cost-economics picture
    primary_cost_drivers: list
    operating_leverage: low | moderate | high
    capital_intensity: low | moderate | high | very_high
    fixed_vs_variable_mix: string             # e.g. "predominantly fixed", "~60/40 variable"
    labour_share_of_cost: low | moderate | high
    commodity_share_of_cost: low | moderate | high
    energy_share_of_cost: low | moderate | high
    imported_input_share: low | moderate | high
  scenario_sensitivity:                       # the responsiveness picture — mediates
                                              # scenario-to-driver transmission in Layer 5
    labour:
      intensity: low | moderate | high
      skill_mix: low | moderate | high
      wage_pass_through: low | moderate | high
      automation_potential: low | moderate | high
    physical_climate:
      asset_damage_risk: low | moderate | high
      demand_climate_sensitivity: low | moderate | high
    technology:
      absorptive_capacity: low | moderate | high
      digital_substitution_risk: low | moderate | high
    energy_transition:
      operational_carbon_exposure: low | moderate | high
      customer_transition_exposure: low | moderate | high
      stranded_asset_risk: low | moderate | high
    demographic:
      demand_age_profile: string              # e.g. "ageing drives demand", "youth-skewed"
      labour_supply_sensitivity: low | moderate | high
    trade_and_supply_chain:
      imported_input_share: low | moderate | high   # cross-reference with cost_structure
      supply_chain_concentration: low | moderate | high
    regulatory_cross_cutting:
      tax_sensitivity: low | moderate | high
      competition_policy_exposure: low | moderate | high
      data_and_digital_regulation: low | moderate | high
  disruption_vectors:
    - vector: string                          # e.g. "electronic initiation substitution"
      nature: threat | opportunity | both     # direction for the archetype
      incumbency_position: defender | attacker | neutral
      time_horizon: "0-3 years" | "3-7 years" | "7+ years"
      severity: low | moderate | high
      certainty: low | moderate | high
      description: string
  regulatory_regime:
    primary_regulators: list
    current_pressure: low | moderate | high
    known_step_changes: list
  cyclicality:
    cycle_length_years: int | null
    current_cycle_phase: trough | early | mid | late | peak
    amplitude: low | moderate | high
  input_dependencies:
    critical_inputs: list
    supply_risk: low | moderate | high
```

**Why `cost_structure` and `scenario_sensitivity` both exist.** `cost_structure` is the *static* cost-economics picture of the industry today; `scenario_sensitivity` is the *responsiveness* picture — how the industry reacts to each scenario dimension. Sometimes the two diverge. An industry with low labour share of cost can still have high wage pass-through sensitivity if the workers it does employ are scarce specialists whose wage spike cascades through supply chains. An industry with high imported-input share is not automatically one with high supply-chain concentration risk. Keeping the two blocks separate preserves the distinction.

### 7.5 Archetypes needed for our test companies

1. **Industrial explosives & ground-support services** — IPL's Dyno Nobel segment. Multi-geographic (Australia, North America, rest-of-world); industry dynamics dominated by mining-customer capex cycles, technology differentiation (electronic initiation systems), and scale in manufacturing/distribution.
2. **Nitrogen fertilisers** — IPL's Fertilisers Australia segment (until the planned demerger closes). National geography; distinct dynamics from explosives: driven by global urea/ammonia cycles, domestic gas input cost, agricultural commodity prices, and seasonal demand.
3. **Specialty biologics — plasma-derived therapies & vaccines** — CSL. Multi-geographic (US, EU, Asia); may be further sub-divided into Behring (plasma) and Seqirus (vaccines) if their scenario sensitivities diverge materially; to be tested when we populate.
4. **Major Australian banks — retail, business and institutional banking** — WBC. National geography.

**On multi-industry companies.** IPL spans two distinct archetypes with genuinely different industry structures, not merely two segments of one industry. The schema treats each segment as referencing its own archetype; the company-level assumption set is a weighted aggregate across segments, with weights from segment revenue and EBIT shares at the base year. The weights themselves may evolve across the forecast horizon under a given scenario (e.g. a demerger scenario would zero out one segment's weight after the effective date).

**On thin archetypes.** CSL's archetype (specialty plasma therapeutics) has very few peers of comparable scale and positioning. The industry-level matrix may therefore track CSL closely in practice. We retain the industry layer nonetheless for three reasons: (i) writing down the industry-reference view forces explicit articulation of "what a generic specialty-biologics firm would experience in this scenario," which is analytically useful even when only one subject consumes it; (ii) the override mechanism remains available if peers are added later; and (iii) architectural consistency across the three test companies simplifies the engine.

### 7.6 Review items

1. **Scenario-sensitivity attribute list.** The block above is comprehensive but may need pruning or additions as we populate actual archetypes. Ben's data-sourcing workstream needs to confirm data availability for each attribute; attributes that cannot be reliably sourced should either be dropped or marked analyst-judgment-only.
2. **Multi-segment handling for CSL.** Whether Behring and Seqirus are one archetype with internal segmentation or two distinct archetypes. To be tested when populating.
3. **Treatment of CSL Vifor.** Separate segment or rolled into Behring; depends on the post-acquisition reporting structure Ben can source.
4. **`imported_input_share` appears in both `cost_structure` and `scenario_sensitivity.trade_and_supply_chain`.** Intentional (static picture vs responsiveness picture per §7.4 note) but worth confirming this doesn't cause confusion in data entry. Option: rename one to make the distinction obvious.
5. **Submarket granularity and data availability.** Where multiple regions are captured, depth of regional analysis is constrained by what Ben's workstream can reliably source per region. Needs alignment.
6. **Lifecycle_rationale field is narrative.** Over time we may want to standardise the way lifecycle is evidenced (e.g. require reference to a peer-group ROIC vs WACC comparison).

---

## 8. Layer 3 — Company Positioning

### 8.1 Purpose

Captures where the subject company sits within its industry archetype(s). This is what determines whether a given industry-level impact hits the company harder, softer, or differently than the industry average.

### 8.2 Schema (draft)

```yaml
company_position:
  id: string
  name: string
  ticker: string
  reporting_currency: string
  functional_currency: string             # may differ from reporting currency
  functional_currency_rationale: string   # evidence for the determination
  segments:
    - segment: string
      industry_archetype: string          # FK to layer 2
      functional_currency: string         # may differ from parent if segment
                                          # operates in a distinct economic environment
      functional_currency_rationale: string
      revenue_share: float
      ebit_share: float
      notes: string
  market_position:
    share: float | string
    rank: int | string
    share_trend: string              # gaining | stable | losing
  moat:
    sources: list                    # scale | brand | network | switching_cost | regulatory | resource | patent
    durability: string               # weak | moderate | strong | very strong
    evidence: string
  cost_position:
    placement_on_curve: string       # bottom_quartile | 2nd | 3rd | top_quartile
    evidence: string
  capability_profile:
    strengths: list
    gaps: list
  balance_sheet:
    net_debt_ebitda: float
    leverage_posture: string         # conservative | moderate | aggressive
    liquidity: string
  capital_allocation:
    dividend_policy: string
    buyback_posture: string
    m_and_a_posture: string
    reinvestment_rate: float | null
  risk_exposures:
    commodity: list
    fx: list
    regulatory: list
    customer_concentration: string
    geographic_concentration: string
  esg_and_transition:
    carbon_intensity: string
    transition_plan: string
    stranded_asset_exposure: string
  management_and_governance:
    strategy_quality: string
    execution_track_record: string
```

### 8.3 Deliverables

1. A populated `company_position.yaml` for IPL, CSL, and WBC.
2. For each company, cross-references to the applicable industry archetype(s).
3. Reasoning notes captured in-line (YAML comments or dedicated `evidence` fields) so the positioning is defensible and auditable.

### 8.4 Open

1. How to represent multi-segment companies cleanly (applies to IPL; also relevant for CSL's Behring vs Seqirus split).
2. Treatment of CSL Vifor (the iron-therapy acquisition) — separate segment or rolled into Behring.
3. Whether to capture historical financial snapshots inside this layer, or keep that in a separate `financials.yaml` per company.

---

## 9. Layer 4 — Driver Taxonomy

### 9.1 Purpose

An exhaustive, standardised list of the value drivers that scenarios and company position jointly influence. Every driver must have: an id, description, unit, default range, and mapping to how it enters a DCF.

### 9.2 Driver groups (provisional)

**Revenue drivers**

1. Volume growth rate (by segment)
2. Price / mix effect (by segment)
3. Market size growth
4. Market share movement
5. New product / new geography contribution
6. FX translation effect

**Margin drivers**

1. Gross margin
2. SG&A as % revenue
3. R&D intensity (where relevant)
4. EBITDA margin
5. Depreciation & amortisation as % revenue
6. EBIT margin
7. Operating leverage coefficient
8. Input cost pass-through rate

**Capital drivers**

1. Maintenance capex as % revenue
2. Growth capex as % revenue
3. Working capital days (AR, AP, inventory)
4. Acquisition / divestment pipeline
5. Asset-turnover ratio
6. Lease commitments profile

**Financial & risk drivers**

1. Effective tax rate
2. Capital structure target (net-debt / EBITDA, or D/E)
3. Cost of debt (pre-tax)
4. Equity risk premium applied
5. Beta (levered / unlevered)
6. Country risk premium
7. Small-cap or company-specific risk premium
8. WACC
9. Minority interests / non-controlling share

**Terminal-state drivers**

1. Terminal growth rate
2. Terminal ROIC
3. Terminal reinvestment rate
4. Terminal margin
5. Fade period length and profile

**Bank-specific drivers (WBC)**

1. Net interest margin (NIM)
2. Loan book growth
3. Cost-to-income ratio
4. Credit loss charge / average loans
5. CET1 ratio target
6. Risk-weighted-asset intensity
7. Return on equity target

The bank driver set requires a parallel "bank DCF" approach (dividend discount or residual income) rather than a traditional FCF DCF, because traditional FCF is not meaningful for deposit-funded institutions. This should be noted in the DCF layer design when we get to it.

### 9.3 Open

1. Completeness check — is the driver list exhaustive for our three companies? CSL may need specific pipeline-value drivers; WBC may need more granular regulatory-capital drivers.
2. Units standardisation.
3. Whether to express FX as a separate driver or embed it in revenue growth and translation.

---

## 10. Layer 5 — Linkage / Impact Matrix

### 10.1 Purpose

The linkage layer is the conceptual core of the module. It encodes, for every combination of (scenario × industry archetype × driver), how the driver moves. Company positioning then modulates those industry-level impacts up or down via overrides to produce company-specific **driver movements**. The output of this layer is structural and qualitative (direction, magnitude, rationale) — translation into numerical forecast inputs happens in layer 6.

### 10.2 Impact matrix format (draft)

Stored per industry archetype, keyed by scenario × driver:

```yaml
industry: industrial_explosives
matrix:
  - scenario: orderly_convergence
    drivers:
      volume_growth:
        direction: neutral             # strong_negative | negative | neutral | positive | strong_positive
        magnitude: small               # small | moderate | large
        rationale: string
        confidence: medium             # low | medium | high
      input_cost_pass_through:
        direction: positive
        magnitude: moderate
        rationale: string
        confidence: high
      # ...
  - scenario: stagflation_persists
    drivers:
      # ...
```

### 10.3 Company override format

Each `CompanyPosition` may override industry-level impacts, with mandatory reason codes:

```yaml
overrides:
  - company: ipl
    scenario: fragmentation_resource_nationalism
    driver: input_cost_pass_through
    override_direction: strong_positive   # vs industry-level "positive"
    override_magnitude: large             # vs industry-level "moderate"
    reason: >
      IPL's long-term gas supply contracts (signed 2024) insulate its cost
      base through 2031, allowing it to capture pricing upside that
      merchant-gas competitors cannot.
    evidence_refs: [ipl_ar_2025_p48, ipl_hy26_slide_14]
```

### 10.4 Driver movement output schema

The output of layer 5 is a `DriverMovementSet` per company × scenario — structured, qualitative, not yet numerical:

```yaml
driver_movement_set:
  company: string
  scenario: string
  generated_at: datetime
  generated_by: string
  segments:
    - segment: string
      industry_archetype: string
      weight: float                         # segment's share of the company aggregate
      movements:
        - driver: string
          industry_direction: string        # from impact matrix
          industry_magnitude: string
          industry_rationale: string
          industry_confidence: string
          company_override:                 # null if none
            direction: string
            magnitude: string
            reason: string
            evidence_refs: list
          final_direction: string           # after override, if any
          final_magnitude: string
          final_confidence: string
```

### 10.5 Open

1. Granularity of the direction/magnitude encoding — whether a 5-step ordinal is sufficient, or whether we need explicit percentage-impact buckets (e.g., "−200bps to −100bps"). This choice affects layer 6 translation precision.
2. How to handle driver interactions (e.g., when two drivers move together in ways that are not independent) — at the linkage layer or the translation layer.
3. How overrides cascade when an industry-level impact is already at the extreme of the scale (e.g., a company whose position would push beyond "strong_negative").

---

## 11. Layer 6 — Assumption Translation

### 11.1 Purpose

Takes the qualitative `DriverMovementSet` from layer 5 and the company's base-year financial snapshot from Ben's data workstream, and produces a numerical `AssumptionSet`: the actual forecast inputs that a DCF (or bank DDM) will consume. This layer is deliberately mechanical — it is where direction/magnitude buckets become numbers.

### 11.2 Translation approach

1. **Translation rules** map each driver's direction × magnitude × confidence combination to a numerical delta. For example, "volume_growth + positive + moderate" for an industry-specific baseline might mean "+100 to +200 bps above long-run industry average growth." Rules may be global (applied to all industries), industry-specific (different bps ranges per archetype), or driver-specific.
2. **Base-year anchoring** applies the deltas against the company's actual base-year values (from Ben's data). Margin movements apply to reported EBIT margin; capex movements apply to three-year average capex intensity; etc.
3. **Time profile** expands each driver movement into a year-by-year trajectory. Default profile depends on the driver type: impulse drivers (e.g., one-off cost shocks) apply in year 1 and fade; regime drivers (e.g., new steady-state margin) phase in linearly over 2–4 years; cyclical drivers track an explicit cycle profile from the scenario.
4. **Segment aggregation** for multi-segment companies: translation runs per segment (each segment's drivers × its segment weight) and aggregates to company-level assumptions.

### 11.3 Assumption set output schema

```yaml
assumption_set:
  company: string
  scenario: string
  horizon_years: int                 # 5 or 10
  functional_currency: string
  generated_at: datetime
  generated_by: string
  base_year_snapshot:                # anchor: latest reported FY, from Ben's data
    revenue: float
    ebit: float
    ebit_margin: float
    capex: float
    net_debt: float
    # ...
  segment_assumptions:
    - segment: string
      revenue_growth: [y1, y2, ..., yN, terminal]
      ebit_margin: [y1, y2, ..., yN, terminal]
      capex_pct_revenue: [...]
      # ...
  consolidated_assumptions:
    wacc_components:
      risk_free_rate: float
      erp: float
      beta: float
      cost_of_debt_pretax: float
      target_leverage: float
      tax_rate: float
      wacc: float
    terminal:
      growth_rate: float
      roic: float
      reinvestment_rate: float
  reasoning_trace:                   # end-to-end audit trail
    - driver: string
      scenario_narrative_excerpt: string
      industry_direction: string
      industry_magnitude: string
      company_override: object | null
      final_direction: string
      final_magnitude: string
      translation_rule_applied: string
      final_numerical_value: float | list
      time_profile_used: string
      narrative: string
```

### 11.4 Why the reasoning trace matters

The `reasoning_trace` is what makes the module different from "pick a number and multiply." Every numerical assumption can be traced back through: numerical value → translation rule → driver movement → override (if any) → industry-level impact → scenario narrative. If any reviewer (or Tara's strategist friend on the IPL benchmark, or a client) asks "why is year-3 EBIT margin 14.5% under Scenario 3 but 17.2% under Scenario 1?", the module answers with the chain of reasoning, not just the answer. The trace spans both layers 5 and 6 — layer 5 contributes the qualitative chain; layer 6 adds the translation rule and the final number.

### 11.5 Open

1. Whether translation rules live in code (hard-coded ranges per direction × magnitude) or in data (editable YAML tables of bps/percentage mappings). Tentative: data, so analysts can recalibrate without code changes.
2. Whether direction × magnitude maps to a single central estimate or to a range (with interface allowing mid/low/high selection).
3. Treatment of driver interactions that are not independent — resolved here, in layer 5, or split.
4. Time-profile library — the set of canonical profiles (impulse, regime shift, linear fade, cycle) needs specifying.

---

## 12. Layer 7 — DCF Engine *(deferred, brief)*

Consumes an `AssumptionSet` object, returns enterprise value, equity value, and per-share value plus sensitivity tables. Distinct DCF implementation required for WBC (residual income / DDM) vs IPL and CSL (traditional unlevered FCF). To be specified in a separate document once layers 1–5 are built.

---

## 13. Layer 8 — Interactive Interface *(deferred, brief)*

Web application delivered as a **FastAPI backend** (exposing the engine as a JSON API) plus a **Vue frontend** (consuming that API). Per-layer navigation: browse/edit scenarios, browse/edit industry archetypes, view company positioning, view driver movements (layer 5 output), view and modify assumption sets (layer 6 output), compare scenarios side-by-side for one company, compare companies under one scenario. Sensitivity and tornado charts once the DCF engine (layer 7) is live. The user-facing assumption-inspection and modification capability foreshadowed in §1 lives here. To be specified in its own design document once the engine is working.

---

## 14. Phasing Plan

1. **Phase 0 — Design (now).** This document + scenarios workshop. No engine code yet.
2. **Phase 1 — Schema & data layer.** Formalise YAML schemas; populate industry archetypes, company positions, and one or two scenarios as worked examples.
3. **Phase 2 — Impact matrix population.** Populate the matrix across all scenarios × all three industries. Document reasoning. This is the intellectually heavy phase.
4. **Phase 3 — Assumption translator.** Code the translator that turns driver movements + base-year snapshot into `AssumptionSet` objects. First end-to-end run: IPL × base case.
5. **Phase 4 — Expand and calibrate.** Run all three companies across all scenarios. Compare IPL outputs to the strategist-friend benchmark. Iterate on matrix and overrides.
6. **Phase 5 — DCF engine.** Plug in traditional and bank DCF implementations.
7. **Phase 6 — Interface.** FastAPI backend + Vue frontend.

---

## 15. Calibration & Validation

1. **External benchmark.** IPL has an independent scenario-valuation exercise already completed by a strategist. Treat this as a calibration target: if our framework produces materially different conclusions, we must be able to explain why (either we disagree on positioning, we disagree on scenario impacts, or we disagree on translation to assumptions — the reasoning trace should localise the source of divergence).
2. **Internal consistency checks.** Macro variables inside a scenario must be logically consistent; impact-matrix entries should not contradict the scenario narrative; company overrides must have reason codes.
3. **Out-of-sample application.** Once the framework is stable, applying it to a company not in the test set (e.g., BHP) is the simplest test of generalisability.

---

## 16. Conventions

1. **Monetary units.** Each company's positioning and assumption set is denominated in its **functional currency** (see §2 item 7 and §8). Segment-level functional currencies are supported where a segment operates in a materially different economic environment from the parent. Cross-company comparisons in the interface convert to a common display currency (default AUD) at spot; FX is a scenario variable.
2. **Fiscal year.** All three subjects report to 30 June. "Year 1" in assumption sets means the first full forecast year after the most recent reported FY.
3. **File naming.** `snake_case` for ids and filenames; `CamelCase` for Python classes.
4. **Schema versioning.** Every schema carries a `version` field; breaking changes bump major version and require a migration note in `design/schemas/migrations.md`.

---

## 17. Immediate Next Steps

1. Mark up this document — anything to add, remove, or challenge.
2. Scenarios workshop — develop 4–5 named scenario themes with narrative and macro-variable outlines.
3. First industry archetype — populate `fertilisers_explosives.yaml` as the pilot; test that the schema holds up under real content before populating the other two.
4. First company positioning — populate `ipl.yaml` as the pilot; same logic.
5. Decide horizon default once scenario arcs are visible.
