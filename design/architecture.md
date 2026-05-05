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
    frameworks/                  analytical frameworks (methodology, not data)
      five_forces_questions.md   TBD — Porter's Five Forces question bank
                                 (industry-level + company-level)
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

### 7.5 How Five Forces feeds the rest of the framework

The Five Forces ratings captured in the §7.4 schema are not standalone descriptors; they are inputs that flow into other layers. The intended linkages:

1. **→ Lifecycle stage and ROIC durability (§7.4 `lifecycle_stage`).** A favourable Five Forces profile (low buyer power, low supplier power, high barriers to entry, low substitution risk, low rivalry) supports sustained returns above cost of capital and a longer growth / mature phase. Adverse profiles imply faster reversion to the cost-of-capital floor. The `lifecycle_rationale` field should explicitly cite the dominant Five Forces drivers.
2. **→ Default driver ranges (§9 `default_range`).** Industry archetypes carry default ranges for margin, pricing power, capital intensity, and similar drivers. These defaults should be set consistently with the Five Forces profile — concentrated industries with weak buyer power carry higher default margin ranges; high-rivalry industries carry lower margin defaults and wider pricing volatility. Without this discipline the Five Forces analysis becomes decorative.
3. **→ Scenario sensitivity (§7.4 `scenario_sensitivity`).** Force ratings condition how an industry transmits scenario shocks. Industries with strong supplier power are more exposed to commodity, energy, and wage scenarios; industries with strong buyer power transmit cost shocks back to suppliers rather than absorbing them; high-substitution industries are more exposed to technology and energy-transition scenarios. The `scenario_sensitivity` block should be calibrated with the Five Forces profile in view.
4. **→ Disruption surfacing (§7.3).** Disruption signals are detected through the `new_entrants` and `substitutes` forces rather than carried as a separate lifecycle state. A material adverse change in either force is a disruption signal that may compress lifecycle phase length and reset return economics.
5. **→ Company-level positioning (§8).** Five Forces is the industry-level view of competitive intensity. Company positioning (§8) is then *how the subject company sits inside that force pattern* — moat sources are answers to "what protects this company from each adverse force?", franchise assets are positive-side analogues, and competitive position (cost / differentiation) is the company's weapon for surviving rivalry.

A standardised **Five Forces question bank** — used to interview each industry archetype and each company within it — is a planned deliverable. The question bank will live at `design/frameworks/five_forces_questions.md` and will hold two parallel question sets per force: an industry-level set (assess the force in this archetype) and a company-level set (assess the subject company's position vis-à-vis the force). Sub-questions within each force draw on Porter's determinants (e.g. for buyer power: concentration, switching costs, price sensitivity, backward-integration credibility, information transparency). Question bank to be developed and refined as we work through the IPL / CSL / WBC archetypes; see §7.7 review items.

### 7.6 Archetypes needed for our test companies

1. **Industrial explosives & ground-support services** — IPL's Dyno Nobel segment. Multi-geographic (Australia, North America, rest-of-world); industry dynamics dominated by mining-customer capex cycles, technology differentiation (electronic initiation systems), and scale in manufacturing/distribution.
2. **Nitrogen fertilisers** — IPL's Fertilisers Australia segment (until the planned demerger closes). National geography; distinct dynamics from explosives: driven by global urea/ammonia cycles, domestic gas input cost, agricultural commodity prices, and seasonal demand.
3. **Specialty biologics — plasma-derived therapies & vaccines** — CSL. Multi-geographic (US, EU, Asia); may be further sub-divided into Behring (plasma) and Seqirus (vaccines) if their scenario sensitivities diverge materially; to be tested when we populate.
4. **Major Australian banks — retail, business and institutional banking** — WBC. National geography.

**On multi-industry companies.** IPL spans two distinct archetypes with genuinely different industry structures, not merely two segments of one industry. The schema treats each segment as referencing its own archetype; the company-level assumption set is a weighted aggregate across segments, with weights from segment revenue and EBIT shares at the base year. The weights themselves may evolve across the forecast horizon under a given scenario (e.g. a demerger scenario would zero out one segment's weight after the effective date).

**On thin archetypes.** CSL's archetype (specialty plasma therapeutics) has very few peers of comparable scale and positioning. The industry-level matrix may therefore track CSL closely in practice. We retain the industry layer nonetheless for three reasons: (i) writing down the industry-reference view forces explicit articulation of "what a generic specialty-biologics firm would experience in this scenario," which is analytically useful even when only one subject consumes it; (ii) the override mechanism remains available if peers are added later; and (iii) architectural consistency across the three test companies simplifies the engine.

### 7.7 Review items

1. **Scenario-sensitivity attribute list.** The block above is comprehensive but may need pruning or additions as we populate actual archetypes. Ben's data-sourcing workstream needs to confirm data availability for each attribute; attributes that cannot be reliably sourced should either be dropped or marked analyst-judgment-only.
2. **Multi-segment handling for CSL.** Whether Behring and Seqirus are one archetype with internal segmentation or two distinct archetypes. To be tested when populating.
3. **Treatment of CSL Vifor.** Separate segment or rolled into Behring; depends on the post-acquisition reporting structure Ben can source.
4. **`imported_input_share` appears in both `cost_structure` and `scenario_sensitivity.trade_and_supply_chain`.** Intentional (static picture vs responsiveness picture per §7.4 note) but worth confirming this doesn't cause confusion in data entry. Option: rename one to make the distinction obvious.
5. **Submarket granularity and data availability.** Where multiple regions are captured, depth of regional analysis is constrained by what Ben's workstream can reliably source per region. Needs alignment.
6. **Lifecycle_rationale field is narrative.** Over time we may want to standardise the way lifecycle is evidenced (e.g. require reference to a peer-group ROIC vs WACC comparison).
7. **Five Forces question bank to be developed.** Build out `design/frameworks/five_forces_questions.md` with two parallel question sets per force (industry-level and company-level). Sub-questions per force based on Porter's determinants. Iterate as we apply it to IPL / CSL / WBC; first cut to be drafted before populating the first archetype so the analysis is structured from the start.
8. **Default driver ranges to be calibrated against Five Forces.** When Layer 4 default ranges are populated for each archetype, cross-check that the ranges (margins, pricing power, capital intensity) are consistent with the Five Forces profile per §7.5 link 2. Inconsistency should trigger a re-examination of either the ranges or the force ratings.

---

## 8. Layer 3 — Company Positioning

### 8.1 Purpose

Captures where the subject company sits within its industry archetype(s). This is what determines whether a given industry-level impact hits the company harder, softer, or differently than the industry average. Positioning blocks are held primarily at the segment level, because companies frequently span multiple industries with different competitive dynamics (e.g. IPL's Dyno Nobel explosives vs Fertilisers Australia). Single-segment companies carry a single segment that holds the positioning.

### 8.2 Schema (draft)

```yaml
company_position:
  id: string
  name: string
  ticker: string
  reporting_currency: string
  functional_currency: string                  # may differ from reporting currency
  functional_currency_rationale: string

  # ---- Consolidated, parent-level blocks ----
  balance_sheet:
    net_debt_ebitda: float | null              # null where archetype_specific
                                               # replaces this (e.g. banks)
    leverage_posture: low | moderate | high
    liquidity: string
  capital_allocation:
    dividend_policy: string
    buyback_posture: string
    m_and_a_posture: string
    reinvestment_rate: float | null            # definition: 5-yr average capex / EBITDA
                                               # (specify alternative in comment if used)
  management_and_governance:
    strategy_quality: low | moderate | high
    strategy_evidence: string
    execution_track_record: low | moderate | high
    execution_evidence: string
  esg_and_transition:
    carbon_intensity: string
    transition_plan: string
    stranded_asset_exposure: string
  scenario_sensitivity_overrides_global:       # cross-segment overrides to archetype-level
                                               # scenario_sensitivity (Layer 2). Only list
                                               # dimensions where the company materially
                                               # diverges from archetype average.
    {dimension}: {sub_dimension: rating, rationale}

  # ---- Per-segment positioning ----
  segments:
    - segment: string
      industry_archetype: string               # FK to Layer 2
      functional_currency: string              # may differ from parent if segment
                                               # operates in a distinct economic environment
      functional_currency_rationale: string
      revenue_share: float
      ebit_share: float
      notes: string

      market_positions:                        # list — one entry per meaningful market
        - market: string                       # e.g. "Australian explosives",
                                               # "Global plasma immunoglobulins"
          unit: revenue | volume | other
          share: float
          rank: int
          share_trend:
            direction: gaining | stable | losing
            delta_5yr_bps: int                 # quantified change in share, basis points
            narrative: string

      moat:
        sources: list                          # scale | brand | network | switching_cost
                                               # | regulatory | resource | patent
                                               # | distribution | data
        durability: low | moderate | high
        evidence: string

      competitive_position:
        cost_position:                         # applicable mainly to commodity-like industries
          placement_on_curve: bottom_quartile | 2nd | 3rd | top_quartile | n/a
          evidence: string
        differentiation_position:              # applicable mainly to differentiated industries
          pricing_power: low | moderate | high
          differentiation_basis: list          # brand | ip | switching_cost | network | service
          evidence: string

      innovation_position:                     # required where archetype is innovation-driven
        rd_intensity: float | null             # R&D / revenue
        pipeline_strength: low | moderate | high
        pipeline_horizon_years: int
        evidence: string

      franchise_assets:                        # supply-side / distribution /
                                               # customer-relationship moats
        assets: list                           # e.g. plasma-collection footprint,
                                               # deposit franchise, long-term mining contracts
        durability: low | moderate | high
        evidence: string

      capability_profile:
        strengths: list
        gaps: list

      risk_exposures:
        commodity: list
        regulatory: list
        customer_concentration:
          top_n: int
          share_of_revenue: float
          narrative: string
        geographic_concentration:
          regions: list                        # [{geo: string, share_of_revenue: float}]
          narrative: string

      archetype_specific:                      # shape varies by industry archetype;
                                               # see §8.3
        ...

      scenario_sensitivity_overrides:          # segment-level overrides to archetype-level
                                               # scenario_sensitivity (Layer 2)
        {dimension}: {sub_dimension: rating, rationale}
```

### 8.3 Archetype-specific positioning fields

Generic positioning blocks (cost_position, moat, balance_sheet, etc.) do not adequately describe specialist archetypes. Each industry archetype declares its own `archetype_specific` schema, populated under `segments[].archetype_specific`. The schema definitions are co-located with the corresponding Layer 2 archetype YAMLs so the structure travels with the archetype.

Initial archetype-specific schemas to draft alongside the IPL / CSL / WBC archetypes:

1. **Banking** — CET1 ratio, NIM (bps), cost-to-income, NPL ratio, funding mix (deposits / wholesale share), liquidity coverage ratio, net stable funding ratio, deposit franchise stickiness, asset mix, loan-loss provisioning posture.
2. **Mining / commodity industrials** — position on global cost curve, mine life (years), by-product credits, jurisdictional risk index, reserve replacement.
3. **Fertilisers** — ammonia / urea cost competitiveness, gas-input cost exposure, transport / logistics advantage, nitrogen-use efficiency technology.
4. **Plasma therapeutics** — collection-centre count, donor pool size, fractionation capacity, pipeline-to-portfolio ratio.

### 8.4 Deliverables

1. A populated `company_position.yaml` for IPL, CSL, and WBC.
2. For each segment, cross-reference to the applicable industry archetype.
3. Reasoning notes captured in-line (YAML comments or `evidence` fields) so positioning is defensible and auditable.
4. Historical financials kept in a separate `financials.yaml` per company, not in this layer.

### 8.5 Review items

1. Archetype-specific schemas for banking, mining, fertilisers, and plasma therapeutics need to be drafted as part of populating the IPL / CSL / WBC archetypes.
2. CSL Vifor: confirm whether reported as a separate operating segment in CSL disclosures. Default treatment is a separate segment within CSL.
3. Innovation-position requirement should be tagged at the industry-archetype level (Layer 2), so the engine can flag missing pipeline data for innovation-driven archetypes.
4. Need to confirm whether `risk_exposures.fx` belongs at parent level (consolidated FX exposure) or per segment, or both. Currently omitted pending decision.

---

## 9. Layer 4 — Driver Taxonomy

### 9.1 Purpose and conventions

An exhaustive, standardised catalogue of the value drivers that scenarios and company position jointly act on. Driver IDs are stable keys: the impact matrix (Layer 5) addresses scenarios into industry / company assumptions through these IDs, so renaming a driver is a breaking change.

Conventions:

1. **Currency:** drivers are expressed in the company's (or segment's) functional currency. FX appears at consolidation across segments operating in different functional currencies, not as a primary driver inside a single-segment DCF.
2. **Real vs nominal:** drivers are **nominal in functional currency**, with inflation embedded in nominal growth rates. The discount rate is correspondingly nominal. Real-terms modelling is not used.
3. **Units:** percentages as decimal floats (`0.085`, not `8.5%`); basis points as int (`850`); currency in functional currency; days for working capital; multipliers / ratios as floats.
4. **Primary vs derived:** scenarios act on **primary** drivers. **Derived** drivers (WACC, EBIT margin, operating leverage coefficient, etc.) are computed from their primary inputs and are not directly written by the impact matrix.
5. **Scope:** drivers are populated at company or segment level depending on their nature; multi-segment companies require segment-level drivers for almost all revenue, margin, and capital lines.
6. **Default ranges:** live with the industry archetype (Layer 2) and may be overridden at company level (Layer 3). Defaults must be calibrated against the archetype's Five Forces profile (§7.5 link 2).
7. **Valuation model:** each driver is tagged with the model(s) it serves (FCF, DDM, residual income). A bank driver does not appear in an FCF model; an FCF driver does not appear in a residual-income bank model.

### 9.2 Driver schema

```yaml
driver:
  id: string                           # stable key — used by impact matrix
  group: string                        # revenue | margin | capital | financial_risk |
                                       # terminal | archetype_specific
  name: string
  description: string
  unit: string                         # decimal | bps | days | currency | ratio | multiplier
  default_range: {min, mid, max}       # populated at archetype level; overridable per company
  applicable_archetypes: list | "all"
  valuation_model: list                # fcf | ddm | residual_income (one or more)
  dcf_line_item: string                # where it lands in the model
  role: primary | derived
  dependencies: list                   # other driver ids (required where role: derived)
  scope: company | segment             # at what level the driver is populated
  scenario_sensitive: bool             # whether the impact matrix may move it
  base_definition: string              # how the base-year value is anchored — used by
                                       # Layer 6 §11.2. Values: latest_reported_fy |
                                       # ttm | three_year_avg | ntm_consensus
  default_time_profile: string         # default profile name from the §11.3 library;
                                       # parameters bundled (e.g. "regime_shift(3)")
  aggregation_method: string           # used by Layer 6 §11.2 to roll segment values
                                       # to company level. Values: revenue_weighted_avg |
                                       # ebit_weighted_avg | sum | identity_if_company_scope
```

### 9.3 Core driver groups

These apply across most archetypes that use a traditional FCF DCF. Drivers are listed by group; primary / derived role and scenario sensitivity are noted where worth flagging.

**Revenue drivers (segment-scope unless noted)**

1. Volume growth rate
2. Price / mix effect
3. Market size growth
4. Market share movement
5. New product / new geography contribution

**Margin drivers (segment-scope unless noted)**

1. Gross margin (primary)
2. SG&A as % revenue (primary)
3. R&D intensity (primary, where relevant)
4. Depreciation & amortisation as % revenue (primary)
5. EBITDA margin (derived from above)
6. EBIT margin (derived from above)
7. Operating leverage coefficient (derived from cost-structure mix in §7.4)
8. Input cost pass-through rate (primary)

**Capital drivers (segment-scope unless noted)**

1. Maintenance capex as % revenue
2. Growth capex as % revenue
3. Working capital days (AR, AP, inventory)
4. Asset-turnover ratio (derived)
5. Lease commitments profile

M&A is **not** carried in this group. M&A and divestments are modelled as an explicit overlay outside the base (organic) DCF; see §9.7 review items.

**Financial & risk drivers (company-scope)**

1. Statutory tax rate per geography (primary, scenario-sensitive)
2. Effective tax rate (derived from statutory rates × jurisdictional mix + adjustments)
3. Capital structure target (net-debt / EBITDA, or D/E)
4. Cost of debt, pre-tax (primary)
5. Risk-free rate (primary, scenario-sensitive)
6. Equity risk premium (primary, scenario-sensitive)
7. Beta, levered / unlevered (primary)
8. Country risk premium (primary, scenario-sensitive)
9. Small-cap / company-specific risk premium (primary)
10. Cost of equity (derived from rfr + ERP × β + premia)
11. WACC (derived from cost of equity + after-tax cost of debt + capital structure)
12. Minority interests / non-controlling share

**Terminal-state drivers (company-scope)**

1. Terminal growth rate
2. Terminal ROIC
3. Terminal reinvestment rate
4. Terminal margin
5. Fade period length and profile

Terminal-state assumptions must respect the cost-of-capital convergence principle from §1: in steady state, terminal ROIC should equal WACC unless a defended exception is recorded. Otherwise scenarios can manufacture perpetual excess returns inconsistent with the lifecycle thesis.

### 9.4 Archetype-specific driver sets

Some archetypes are not adequately modelled by the core drivers above. Each such archetype declares its own driver set, co-located with the Layer 2 archetype YAML and the Layer 3 archetype-specific positioning fields (§8.3).

Initial archetype-specific driver sets to draft:

1. **Banking (DDM / residual income, not FCF).** Net interest margin (bps), loan book growth, cost-to-income ratio, credit loss charge / average loans, CET1 ratio target, risk-weighted-asset intensity, return on equity target, dividend payout ratio, deposit-funding share. The bank model is a parallel valuation engine (DDM or residual income); traditional FCF is not meaningful for deposit-funded institutions. To be specified in the DCF Engine layer (§12).
2. **Plasma therapeutics / life sciences.** Pipeline NPV contribution, probability-weighted pipeline revenue ramp by therapy, R&D productivity (revenue per R&D dollar, defined window), patent-cliff exposure profile.
3. **Mining / commodity industrials.** Cost-curve placement-driven margin trajectory, reserve life, by-product credits.
4. Other archetypes (insurers, REITs, utilities) added as scope expands.

### 9.5 Deliverables

1. A populated `drivers.yaml` carrying the core driver catalogue with default schema.
2. Per-archetype driver sets co-located with archetype YAMLs (Layer 2).
3. Default ranges per archetype, calibrated against Five Forces profile.
4. Cross-walk note documenting which drivers the impact matrix (Layer 5) is permitted to move.

### 9.6 Open

1. Whether WACC moves across scenarios (i.e. whether the WACC-component drivers are actively used by the impact matrix) is a Layer 7 / DCF Engine decision. Layer 4 keeps the option open by tagging the components as `scenario_sensitive: true`; the actual choice is deferred to §12.

### 9.7 Review items

1. Archetype-specific driver sets for banking, plasma therapeutics, mining, and fertilisers need to be drafted alongside their Layer 2 archetype definitions and Layer 3 archetype-specific positioning fields.
2. M&A overlay design (§9.3 capital drivers note): how to specify acquisition / divestment overlays cleanly, including timing, deal economics, and integration assumptions, kept outside the base organic DCF.
3. Innovation-position driver requirement: where Layer 2 flags an archetype as innovation-driven, the corresponding archetype-specific driver set must include pipeline-value drivers; the engine should warn if missing.
4. WACC scenario behaviour to be revisited at §12 (DCF Engine) per §9.6 open item.
5. Default-range calibration loop: when default ranges are populated, cross-check consistency with the archetype's Five Forces profile (per §7.5 / §7.7 item 8). Inconsistency triggers re-examination of the ranges or the force ratings.
6. Driver-ID stability: once IDs are baked into the impact matrix, renaming becomes a breaking change. Worth a short style guide (naming convention, group prefixes) before the catalogue is populated.

---

## 10. Layer 5 — Linkage / Impact Matrix

### 10.1 Purpose

The linkage layer is the conceptual core of the module. It encodes, for every combination of (scenario × industry archetype × driver), how the driver moves under that scenario. Company positioning then modulates those industry-level impacts via segment-addressable overrides to produce company-specific **driver movements**. The output of this layer is structural and qualitative (direction, magnitude, rationale, optional quantified band) — translation into numerical forecast inputs and enforcement of cross-driver consistency happen in Layer 6.

### 10.2 Encoding conventions

1. **Direction and magnitude are separate.** `direction` is sign-only (`negative | neutral | positive`); `magnitude` is size-only (`small | moderate | large`). This gives seven distinct non-trivial movements (3 negative × 3 positive, plus neutral) and is consistent with the rating convention from §7.2.
2. **Hybrid encoding (ordinal + optional quantified band).** Each driver carries a default mapping in Layer 4 from `(direction, magnitude)` → numeric band (e.g. for revenue growth: `(positive, moderate)` → `+100 to +300 bps`). Layer 6 uses this mapping to produce numbers automatically. When an analyst has higher conviction, or the movement would push beyond the ordinal scale, an entry may carry an optional `quantified_override: {min, mid, max}` field that supersedes the default mapping.
3. **Sparse representation.** Most scenario × driver cells are neutral. Convention: absent entries imply `direction: neutral` and were not explicitly assessed. Populate an entry only where direction is non-neutral or confidence is at least `moderate`. The schema validator should warn when a high-importance driver has no entry under any scenario.
4. **`not_applicable` distinct from `neutral`.** A driver that does not apply to the archetype (e.g. NIM under industrial explosives) is marked `not_applicable: true` and excluded from completeness checks. A driver that applies but is unaffected by a scenario is `direction: neutral`.
5. **`confidence` definition (single, pinned).** "Joint confidence in the direction × magnitude assignment, assuming the scenario plays out as defined." Confidence in the scenario itself lives in the scenario object (§6.4) and is not duplicated here.

### 10.3 Impact matrix format

Stored per industry archetype, keyed by scenario × driver:

```yaml
industry: industrial_explosives
matrix:
  - scenario: orderly_convergence
    scenario_version: "2026.05"
    drivers:
      input_cost_pass_through:
        direction: positive                   # negative | neutral | positive
        magnitude: moderate                   # small | moderate | large
        confidence: high                      # low | moderate | high
        rationale: string
        quantified_override: null             # or {min, mid, max} when ordinal
                                              # is insufficient
        not_applicable: false
        evidence_refs:
          - source_id: csiro_2025_emissions_curve
            location: "p.42 Table 5"
            date_accessed: "2026-04-15"
        governance:
          created_by: string
          created_at: datetime
          approved_by: string
          approved_at: datetime
          last_reviewed_at: datetime
      # additional drivers...
  - scenario: stagflation_persists
    # ...
```

Drivers not listed under a scenario are treated as `neutral / small / not assessed`.

### 10.4 Company override format

Overrides modulate industry-level impacts. Overrides are addressable to a specific segment (preferred) or, by omitting `segment`, to the whole company. Mandatory fields: `reason_category`, `reason`, `evidence_refs`, governance block.

```yaml
overrides:
  - company: ipl
    segment: dyno_nobel                       # optional — omit for company-wide
    scenario: fragmentation_resource_nationalism
    driver: input_cost_pass_through
    override_direction: positive | null       # null = inherit industry direction
    override_magnitude: large | null          # null = inherit industry magnitude
    quantified_override:                      # optional — required when override
                                              # would push beyond ordinal scale
      min: ...
      mid: ...
      max: ...
    sign_flip: false                          # true when override_direction
                                              # opposes industry_direction
    beyond_scale: false                       # true when ordinal cannot represent
                                              # the movement; quantified_override
                                              # required when this is true
    reason_category: contract                 # cost_advantage | scale | regulation
                                              # | contract | management | product_mix
                                              # | diversification | franchise_asset
                                              # | other
    reason: >
      IPL's long-term gas supply contracts (signed 2024) insulate its cost
      base through 2031, allowing it to capture pricing upside that
      merchant-gas competitors cannot.
    evidence_refs:
      - source_id: ipl_ar_2025
        location: "p.48"
        date_accessed: "2026-04-12"
      - source_id: ipl_hy26_results
        location: "slide 14"
        date_accessed: "2026-04-12"
    governance:
      created_by: string
      created_at: datetime
      approved_by: string
      approved_at: datetime
      last_reviewed_at: datetime
```

**Override semantics:**

1. **Partial override.** Either `override_direction` or `override_magnitude` (or just `quantified_override`) may be supplied; absent fields inherit from the industry default.
2. **Sign-flip override.** Permitted when override direction opposes industry direction; the validator must flag `sign_flip: true` and require `evidence_refs` of at least two items.
3. **Beyond-scale override.** When the analyst's view would push beyond the ordinal scale (e.g. industry already `positive / large`), the override must carry a `quantified_override` band; ordinal fields then describe the *closest* representative ordinal and `beyond_scale: true` is set.

### 10.5 Driver movement output schema

The output of Layer 5 is a `DriverMovementSet` per company × scenario. It carries per-segment movements (for revenue / margin / capital drivers) and a parallel company-level block (for tax, WACC components, terminal-state drivers, and minority interests).

```yaml
driver_movement_set:
  company: string
  scenario: string
  scenario_version: string
  scenario_severity: boundary | central       # from §6
  scenario_probability: float | null          # if defined
  generated_at: datetime
  generated_by: string

  segments:
    - segment: string
      industry_archetype: string
      weight: float                           # segment's share of company aggregate
      movements:
        - driver: string
          industry_direction: string
          industry_magnitude: string
          industry_confidence: string
          industry_rationale: string
          company_override:                   # null if none
            override_direction: string | null
            override_magnitude: string | null
            quantified_override: {min, mid, max} | null
            sign_flip: bool
            beyond_scale: bool
            reason_category: string
            reason: string
            evidence_refs: list
          final_direction: string
          final_magnitude: string
          final_confidence: string
          final_quantified_band: {min, mid, max} | null

  company_level:                              # tax, WACC components, terminal-state,
                                              # minority interests
    movements:
      - driver: string
        # same field set as segment-level movements
```

### 10.6 Consistency rules

The impact matrix is the analytical core; entries must respect cross-layer constraints. The engine should validate (warn or block) the following:

1. **Scenario-sensitivity consistency (cross-check with §7.4).** Matrix entries should be consistent with the industry archetype's `scenario_sensitivity` block. Example: if `scenario_sensitivity.labour.wage_pass_through` is `low`, an entry under a wage-shock scenario showing `input_cost_pass_through: positive / large` must carry explicit defence in `rationale`.
2. **Cost-of-capital convergence (cross-check with §1 and §9.3).** Matrix entries on terminal-state drivers (terminal ROIC, terminal growth, terminal margin) must respect the convergence principle — in steady state, terminal ROIC should approximate WACC. Entries that imply persistent excess returns require explicit defence in `rationale`.
3. **Driver interactions are NOT enforced at this layer.** Cross-driver coherence (e.g. revenue × margin × operating leverage; tax × geography mix) is enforced in Layer 6 (assumption translation). The impact matrix carries each driver's movement independently.
4. **Freshness.** Entries carry `scenario_version`. The engine should warn when an entry references a scenario version older than the current scenario library; entries flagged stale are candidates for re-review at the next 6-month refresh.
5. **Sign-flip evidence.** `sign_flip: true` overrides require `evidence_refs` of at least two items.

### 10.7 Review items

1. **Default direction-magnitude → numeric-band mapping per driver.** Lives in Layer 4 (driver schema). Needs to be populated per archetype as part of populating the driver catalogue. Without this mapping the hybrid encoding cannot translate to numbers in Layer 6.
2. **Validator implementation.** Consistency rules in §10.6 must be implemented as engine validation, not only stated. Build alongside Layer 5 code.
3. **Reason category enum stability.** Initial enum is `cost_advantage | scale | regulation | contract | management | product_mix | diversification | franchise_asset | other`. To be revisited after first pass populating IPL / CSL / WBC overrides; new categories added if patterns demand.
4. **Governance roles.** Definitions of `created_by` and `approved_by` — single analyst, peer review, or formal governance committee — to be settled with Ben's data workstream.
5. **Beyond-scale override convention** (`beyond_scale: true` plus quantified band) needs a worked example once we hit a real case in populating IPL / CSL / WBC.
6. **High-importance driver completeness check.** Convention is sparse, but a validator should warn when a driver flagged "high importance" for an archetype has no matrix entry under any scenario. Mechanism for flagging "high importance" to be defined alongside the driver catalogue.

---

## 11. Layer 6 — Assumption Translation

### 11.1 Purpose

Takes the qualitative `DriverMovementSet` from Layer 5 and the company's base-year financial snapshot from Ben's data workstream, and produces a numerical `AssumptionSet`: the actual forecast inputs that a DCF (FCF-based) or bank DDM / residual-income model will consume. This layer is deliberately mechanical — it is where direction/magnitude buckets become numbers and where second-order consistency between drivers is enforced.

### 11.2 Translation approach

1. **Translation rules.** Each driver's `(direction, magnitude)` maps to a numeric central band (e.g. for revenue growth: `(positive, moderate)` → +100 to +300 bps above long-run average). `confidence` widens or narrows the band around the centre but does not shift the centre. Rules live as **data** in `data/translation_rules/` — editable by analysts without code changes. Rules may be global, archetype-specific, or driver-specific.
2. **Honour quantified bands from Layer 5.** When a `DriverMovementSet` cell carries a `final_quantified_band`, translation uses that band directly and skips the ordinal lookup. Hybrid encoding (§10.2) is preserved end-to-end.
3. **Base-year anchoring.** Deltas apply against base-year values from Ben's data workstream. The "base year" is per-driver, not implicit: each driver in Layer 4 carries a `base_definition` (e.g. `latest_reported_fy | ttm | three_year_avg | ntm_consensus`) so volatile metrics aren't anchored against a single noisy point.
4. **Time profiles.** Each driver movement expands into a year-by-year trajectory using a named profile from the library in §11.3. Default profile per driver lives in Layer 4 (`default_time_profile`); may be overridden per scenario.
5. **Segment aggregation.** Each Layer 4 driver carries an `aggregation_method` (e.g. `revenue_weighted_avg | ebit_weighted_avg | sum | identity_if_company_scope`). Per-segment translations roll up to company-level using these methods.
6. **Consistency rules** (§11.4) reconcile cross-driver coherence after per-driver translation but before output.

### 11.3 Time-profile library

A small named library; each driver in Layer 4 declares a default profile, overridable per scenario.

| Profile | Parameters | Behaviour |
|---|---|---|
| `impulse` | `peak_year=1, fade_years=N` | Peak in year 1, linear fade to neutral over N years. |
| `regime_shift` | `phase_in_years=N` | Linear ramp from current to new steady state over N years. |
| `step` | `year=N` | Instantaneous shift at year N (e.g. policy change effective date). |
| `cyclical` | `period_years, phase, amplitude` | Sinusoidal cycle. |
| `front_loaded` | `years=N` | Skewed phase-in: most of the effect in the first N years. |
| `back_loaded` | `years=N` | Skewed phase-in: most of the effect in the last N years. |
| `linear_through_horizon` | — | Proportional ramp through the entire horizon. |

Library lives as code in `engine/assumptions/time_profiles.py`. Per-driver defaults and per-scenario overrides live as data.

### 11.4 Consistency rules

After per-driver translation, the engine applies a sequence of structural-identity rules to reconcile cross-driver coherence. Each rule writes to the reasoning trace so the reconciliation is auditable. Rules live as code (structural identities, not calibration).

1. **Operating leverage check.** Revenue movement combined with the archetype's fixed-cost share (from §7.4 `cost_structure`) implies an EBIT-margin range. If independent translation produces a margin movement outside that range, the rule reconciles (cap to leverage-implied range or warn).
2. **Tax aggregation.** Statutory-rate movements per geography roll up to a company-level effective rate via revenue / EBIT mix.
3. **Capex → D&A.** Capex deltas feed D&A trajectories using the archetype's typical asset life.
4. **WACC computation.** Movements in components (risk-free rate, ERP, beta, cost of debt, target leverage, tax rate) compute through to cost of equity and WACC.
5. **Terminal-state convergence.** Enforce terminal ROIC ≈ WACC unless an explicit defence is recorded in the matrix entry (cross-check with §1 and §9.3).

### 11.5 Assumption set output schema

Driver-keyed, range-by-default, archetype-tagged where needed.

```yaml
assumption_set:
  company: string
  scenario: string
  scenario_version: string
  horizon_years: int                          # parametric per §2 — set per
                                              # company-scenario combination
  functional_currency: string
  translation_rules_version: string
  generated_at: datetime
  generated_by: string

  base_year_snapshot:                         # from Ben's data workstream
    fiscal_year: string
    revenue: float
    ebit: float
    ebit_margin: float
    capex: float
    net_debt: float
    # ... archetype-relevant additional lines

  segment_assumptions:                        # driver-keyed map
    - segment: string
      industry_archetype: string
      weight: float
      assumptions:
        {driver_id}:
          min: [y1, y2, ..., yN, terminal]
          mid: [y1, y2, ..., yN, terminal]
          max: [y1, y2, ..., yN, terminal]
          confidence: low | moderate | high   # propagated from L5
          time_profile: string                # name + parameters
          base_value: float                   # from base_year_snapshot
          aggregation_method: string          # per Layer 4

  consolidated_assumptions:                   # archetype-tagged
    valuation_model: fcf | ddm | residual_income

    # if FCF model (e.g. IPL, CSL):
    consolidated_assumptions_fcf:
      assumptions:
        {driver_id}:                          # WACC components, terminal-state,
                                              # tax, minorities
          # same shape as segment assumptions

    # if DDM / residual income (e.g. WBC):
    consolidated_assumptions_ddm:
      assumptions:
        {driver_id}:                          # cost of equity, dividend payout,
                                              # target CET1, NIM trajectory,
                                              # cost-to-income, credit-loss charge
          # same shape as segment assumptions

  reasoning_trace:                            # end-to-end audit, per (segment, driver)
    - segment: string | "company_level"
      driver: string
      scenario_narrative_excerpt: string
      industry_direction: string
      industry_magnitude: string
      industry_confidence: string
      company_override: object | null
      final_direction: string
      final_magnitude: string
      final_quantified_band: {min, mid, max} | null
      translation_rule_applied: string
      base_definition: string
      base_value: float
      time_profile_used: string
      consistency_rules_applied: list         # which §11.4 rules touched this driver
      final_numerical_value: {min, mid, max}  # the trajectory range
      narrative: string
```

**Forward compatibility note.** The per-cell shape `{min, mid, max}` is the deterministic representation. If the stochastic overlay (§3 Open Decision) is later adopted, cells may extend to a distribution descriptor (e.g. `{distribution: lognormal, params: {...}}`) without breaking downstream consumers — they would consume the same `min` / `mid` / `max` projections of the distribution.

### 11.6 Why the reasoning trace matters

The `reasoning_trace` is what makes the module different from "pick a number and multiply." Every numerical assumption can be traced back through: numerical value → consistency rule (if any) → translation rule + base value → driver movement → override (if any) → industry-level impact → scenario narrative. If any reviewer (or Tara's strategist friend on the IPL benchmark, or a client) asks "why is year-3 EBIT margin 14.5% under Scenario 3 but 17.2% under Scenario 1?", the module answers with the chain of reasoning, not just the answer. The trace spans Layers 5 and 6 — Layer 5 contributes the qualitative chain; Layer 6 adds the translation rule, the consistency reconciliation, and the final number.

### 11.7 Review items

1. **Translation rules calibration.** Initial `(direction, magnitude)` → bps mappings need to be set per archetype. Sensible starting point: cross-reference against historical scenario shocks (GFC, COVID, post-2022 inflation) to ensure the bands make sense in context.
2. **Time-profile parameter defaults.** Each canonical profile needs sensible default parameters per driver type (e.g. `regime_shift(phase_in_years=3)` for margin shifts; `regime_shift(phase_in_years=5)` for capital-structure shifts). To be set when the library is implemented.
3. **Consistency-rule priority and ordering.** When multiple rules touch the same driver (e.g. operating-leverage check AND terminal convergence both touching terminal margin), priority order must be defined. Default proposal: convergence rules before reconciliation rules.
4. **Bank DDM consolidated shape.** The `consolidated_assumptions_ddm` driver list needs to be defined and co-located with the banking archetype (per §9.4).
5. **Reasoning-trace storage.** Currently inline in the `AssumptionSet`. May balloon for many-scenario / many-company runs. Worth deciding whether to keep inline (single source of truth) or split to a side-car audit log per company-scenario.
6. **Parametric horizon source.** §2 says horizon is parametric per company-scenario; needs an explicit field in the scenario object (or scenario-company application) declaring the horizon for each combination.
7. **Layer 4 driver-schema additions required.** Translation logic depends on three new fields per driver in Layer 4: `base_definition`, `default_time_profile`, `aggregation_method`. These need to be added to §9.2 schema and populated per driver.

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
