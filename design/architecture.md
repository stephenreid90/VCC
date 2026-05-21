# VCC Valuations — Scenario-Based Equity Valuation Module
## Architecture & Design Specification

**Version:** 0.2
**Date:** 21 April 2026 (drafted); 7 May 2026 (Ben's-bot review + Group 1 changes; editorial sweep; v0.1 freeze); 17 May 2026 (v0.2: archetype-granularity principle added at §7.1.1).
**Status:** v0.2. Section-by-section review with Tara complete; Ben's-bot platform-side review (5 May 2026) incorporated; archetype-granularity principle added 17 May 2026. Subsequent material changes will bump version with a migration note.
**Migration from v0.1 → v0.2:** Additive change only. New §7.1.1 "Defining archetype granularity" added; no schema changes; no breaking changes to existing content. Existing v0.1 archetype YAMLs remain valid.
**Scope of this phase:** Layers 1–6 (the "assumptions engine"). Layers 7 (DCF) and 8 (interface) are described at a high level only and deferred to later phases.
**Review convention:** Open issues raised during section-by-section review are captured as an `X.N Review items` subsection at the end of the relevant section. Search the document for "Review items" to surface all open issues in one pass. Items in these subsections are candidates for cross-review with Ben's data-sourcing workstream.

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

1. **Technology stack.** Python engine (pandas, numpy, pydantic) exposing a JSON API. The user interface is **embedded in the existing VCC dashboard** — the engine returns rich structured `AssumptionSet` JSON, the dashboard's existing module loader (`v2.html` shell + `static/js/v2/` modules) renders it as a Valuations tab on each per-company VCC. This avoids building a second frontend, gives single UX / single auth / single ops surface, and aligns with the platform principle "server returns rich structured output; UI is one renderer, agent is another." (Earlier draft locked FastAPI + Vue as a standalone module; that decision was revisited following platform-side review and the VCC-dashboard-embed approach adopted instead.)
2. **Scenario count.** Three to six named, qualitatively distinct scenarios. Scenarios must differ on *multiple dimensions* — not simply severity dials on a single axis. Exact count within the 3–6 range to emerge from the scenarios workshop.
3. **Scenario-to-driver linkage.** Explicit impact matrix of the form `scenario × industry archetype × driver → directional impact and magnitude bucket`, with company-level analyst overrides permitted and documented with reason codes. Two structural nuances are recognised: (a) a company may span multiple industry archetypes, in which case each business segment references its own archetype matrix and contributes a weighted share to the company-level assumption set; and (b) an industry archetype may have few peers in practice (e.g., specialty plasma therapeutics, where CSL is effectively the dominant player), in which case the archetype matrix may closely track the subject company. The layer structure is retained in the thin-archetype case because writing down the industry-reference view remains analytically useful and preserves the override mechanism for future peers. (IPL formerly spanned two distinct archetypes — industrial explosives and nitrogen fertilisers — and was the original illustrative case for multi-segment treatment. Following the demerger of the fertilisers business, IPL trades as a single-segment industrial-explosives company. The multi-segment treatment in the schema remains relevant for CSL and any future test company spanning multiple archetypes; the corporate-action overlay (§8) handles the demerger / acquisition / divestment case generally.)
4. **Test companies.** Incitec Pivot Limited (IPL), CSL Limited (CSL), Westpac Banking Corporation (WBC). All ASX-listed, spanning three genuinely different archetypes: industrial chemicals / mid-stream commodity exposure; defensive global healthcare; regulated domestic financial.
5. **Forecast horizon.** Parametric per company-scenario combination. Schema supports both 5 explicit years + terminal and 10 explicit years + terminal. Default selection deferred until scenarios are specified, on the basis that some scenarios may have multi-stage arcs that only make sense over 10 years, while others may resolve within 5.
6. **Data as data; logic as code.** Scenarios, industries, and companies are represented as YAML (easy for domain experts to edit); linkage, translation, DCF, and UI are Python (easy for engineers to refactor).
7. **Currency handling — functional currency basis.** Each company's valuation is conducted in its **functional currency** — the currency of the primary economic environment in which the entity operates and generates cash flows — not necessarily its reporting currency (though for most of our subjects the two will coincide). Determining the functional currency is an explicit early step in company positioning (see §8). For multi-segment companies operating in materially different economic environments, segment-level functional currencies may differ from the consolidated view (IPL is the likely test case: Dyno Nobel operates globally with predominantly USD-denominated contracts and input costs, while Fertilisers Australia is a domestic AUD operation with AUD gas inputs and AUD farmer customers). Cross-company comparisons in the interface convert to a common display currency (default AUD) at spot; FX is a scenario variable.
8. **Workstreams and division of labour.** The engine build documented in this specification runs in parallel to a **data-sourcing workstream** led by Ben (collaborator). Ben's workstream is responsible for sourcing, curating, and updating the underlying financial, operational, and reference data the engine consumes. The interface between the two workstreams is the set of data schemas defined in §§6–11 of this document (scenarios, industry archetypes, company positioning, driver taxonomy, driver-movement outputs, base-year company financial snapshots). The engine workstream owns the schemas and is responsible for keeping them stable, versioning them cleanly when they change, and communicating changes in advance to the data workstream. The data workstream is out of scope for this specification but its outputs must conform to these schemas.

## 3. Scope Decisions — Open

1. Scenario themes — to be developed in a dedicated scenarios workshop before any engine code is written.
2. Default horizon per company — to be fixed once scenarios are specified.
3. Scenario probability weighting — *narrowed*. The §6.2 commitment to scenarios as boundary cases (chosen to span plausible variation, not to be exhaustive or mutually exclusive) is incompatible with a probability-weighted blended expected-value output mode (which would require exhaustive, weakly mutually exclusive coverage). Comparative output is therefore canonical. The remaining open question is narrower: whether to allow analysts to compute their own indicative blended scalar as a side-calculation using optional per-scenario probabilities. The schema supports the optional probability field; whether the engine surfaces a blended scalar as a presented output (rather than analyst-computed) is the call to make. Tara still to consult economists if useful, but mode (a) blended expected value is *not* a supported canonical output mode.
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
      payor_and_regulator.md     TBD — complementary framework for banks /
                                 financial-services / regulated industries
                                 (see §7.X)
  src/
    vcc_valuations/              installable Python package (pip install -e .)
      scenarios/                 scenario loading and validation
      industry/                  industry-structure framework
      company/                   positioning analysis utilities
      linkage/                   impact-matrix application, override handling
      assumptions/               driver → forecast-input translation
                                 (incl. time_profiles.py and consistency_rules.py)
      dcf/                       phase-2 valuation engine
      api/                       JSON API exposing engine to VCC dashboard
      cli/                       vcc-valuation subcommand entry points
      utils/
  data/
    scenarios/                   one file per scenario
      orderly_convergence.yaml
      stagflation_persists.yaml
      # ...
    industries/                  one file per archetype
      industrial_explosives.yaml
      nitrogen_fertilisers.yaml
      specialty_biologics.yaml
      major_banks_au.yaml
    companies/
      ipl.yaml
      csl.yaml
      wbc.yaml
    financials/                  curated base-year snapshots only
      ipl.yaml                   # small, engine-consumable; raw data lives
                                 # in market-ingest's Postgres, curated into
                                 # this file by Ben's data workstream
      csl.yaml
      wbc.yaml
    translation_rules/           direction × magnitude → numeric band mappings
    impact_matrix/
      by_industry/               one matrix file per industry archetype
  output/                        cached layer outputs (audit + reproducibility)
    driver_movements/            one file per company × scenario
    assumption_sets/             one file per company × scenario
  tests/
  notebooks/                     exploratory analysis, calibration checks
  README.md
  pyproject.toml
```

Philosophy: scenarios, industries, and companies are **data** (YAML). Linkage, assumption translation, DCF, and API are **code**. Domain experts can update scenarios or industry analyses without touching Python; engineers can refactor logic without re-entering domain content. The UI layer sits in the broader VCC platform, not in this repository — see §13.

### 5.1 Review items

Items 1–6 below were surfaced during the original Section 5 review and have all been *resolved* in the tree above following Ben's-bot platform-side review (5 May 2026). They are retained here as a record. Remaining open items (numbered 7+) are still active.

1. **Industry archetype files split into single-archetype files.** Resolved: `industrial_explosives.yaml`, `nitrogen_fertilisers.yaml` (separate); `specialty_biologics.yaml`; `major_banks_au.yaml`.
2. **Scenario file layout — one file per scenario.** Resolved: `data/scenarios/<scenario_id>.yaml`. Mirrors industries and companies; cleaner version-control diffs.
3. **Home for base-year financial snapshots — option (c) adopted.** Raw source data ingested by Ben's data workstream into `market-ingest`'s Postgres (which already ingests EODHD fundamentals with revenue / EBIT / capex / net debt / working-capital lines). A thin `data/financials/<co>.yaml` carries only the curated base-year snapshot the engine consumes. The engine never reaches into raw data; it consumes the curated snapshot. Keeps the engine deterministic against committed YAML while letting the data layer evolve.
4. **Translation rules as data.** Resolved: `data/translation_rules/` (per §11.2).
5. **Outputs storage.** Resolved: `output/{driver_movements,assumption_sets}/` cached for audit and reproducibility, and to make the dashboard renderer instant.
6. **Python packaging layout.** Resolved: `src/vcc_valuations/` package layout.

**Active items:**

7. **Data-sourcing workstream contract.** The valuation module's `data/financials/<co>.yaml` schema and the contract by which Ben's `market-ingest` workstream populates it need to be written down explicitly and version-pinned. Specifically: what fields, in what units, from what source records, with what update cadence. Sits at the boundary between this spec and the data workstream's own.
8. **Industry archetype location — strategic decision parked.** Industry archetypes (`major_banks_au`, `specialty_biologics` etc.) are currently colocated with the valuation module. Once other consumers of archetypes appear in the platform — additional bank VCCs (NAB / ANZ / CBA), the structurer, etc. — these may be better hosted as a platform-level artefact (sibling `vcc-reference-data/` repo, or under `vcc-platform/data/reference/`). The same applies to scenarios. Decision deferred until at least one additional consumer materialises; revisit at that point. For v0.1 they live in `vcc-valuations`.
9. **Tree-vs-imports drift.** *Resolved* in the v0.1 editorial sweep — all imports-style references in the document now use the `src/vcc_valuations/` package path.

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
4. **Narrative deliverable** (per §16.1 item 1): `data/scenarios/<scenario_id>.md` per scenario — prose write-up describing the future-world. Produced in the scenarios workshop alongside the structured YAML.

### 6.7 Review items

1. **Scenario population.** Themes, count, and specific trajectories to be defined in the dedicated scenarios workshop (§3 open item 1).
2. **Probability-weighting.** Schema supports optional probability per scenario; the decision on whether to require, permit, or prohibit weighting is parked pending economist input (§3 open item 3).
3. **Industry-level scenario-sensitivity attributes.** §7 schema needs expansion to capture industry attributes that mediate scenario exposure (labour intensity, physical-asset climate exposure, technology absorptive capacity, demographic sensitivity, cyclicality amplitude etc.) — without these, the Layer 5 impact matrix cannot translate world-level scenario dimensions into industry-specific driver movements. Flagged for resolution during §7 review.
4. **Confidence-band convention.** Macro-variable time series support optional `confidence_low` / `confidence_high`. Convention for what those bands represent (analyst subjective range, forecaster-consensus range, historical regime-conditional range) to be specified.
5. **Version-staleness propagation.** Logic for flagging downstream objects as stale when a scenario version changes needs to be built into the engine. Specific rules (full regeneration required vs. diff-only, treatment of analyst overrides across versions) to be specified.

---

## 7. Layer 2 — Industry Structure Framework

### 7.1 Purpose

A standardised template for analysing the structure of an industry, independent of the subject company. Each test company maps to one or more industry archetypes via per-segment FKs (§8.2). The archetype schema captures both the traditional industry-structure picture (Five Forces, concentration, cost structure, etc.) and the **scenario-sensitivity attributes** that allow the Layer 5 impact matrix to translate world-level scenario dimensions (per §6.3) into industry-specific driver movements.

### 7.1.1 Defining archetype granularity

How fine-grained should the archetype taxonomy be? Too coarse (e.g. "banking" globally) misses material variation in drivers and regulatory regimes. Too fine (e.g. "Australian variable-rate retail mortgages") collapses toward one-archetype-per-company and loses the comparative analytical leverage that the industry layer exists to provide.

**The driver-set principle.** An industry archetype is the level at which the relevant set of value drivers, their default ranges, and their scenario sensitivities are meaningfully similar across the companies / segments grouped under it. Five tests, all of which should hold:

1. **Driver-set similarity.** The set of *relevant drivers* is similar across instances of the archetype. A bank archetype has NIM, CET1, credit-loss charge, cost-to-income; a mining archetype has volume, realised price, cost-curve placement. They cannot share an archetype.
2. **Default-range consistency.** The *default ranges* (§9.2 `default_range`) for shared drivers can be set with reasonable consistency across instances. Advanced-economy retail-banking NIM defaults differ structurally from emerging-market banking NIM defaults; they should be different archetypes.
3. **Scenario-sensitivity coherence.** Scenarios transmit similarly across instances. Metallurgical coal and thermal coal respond differently to climate-policy scenarios (thermal is transition-exposed; met is partially insulated via steel demand); they shouldn't share an archetype.
4. **Five Forces coherence.** The Five Forces analysis yields similar results. Australian supermarkets (Coles + Woolworths duopoly) have very different rivalry intensity from US fragmented grocery; different archetype.
5. **Regulatory / macro-policy similarity.** The regulatory regime, monetary policy environment, accounting framework, and competitive structure are similar enough across instances. Australian banks vs European universal banks vs Chinese state banks each fail this test against each other; they are distinct archetypes.

If any of these tests fails materially, the archetype is too broad and should be subdivided. Conversely, archetypes with only one company in the test set ("thin archetypes") are explicitly fine — see §7.6 last paragraph.

**Three handling mechanisms in the schema.** When variation between companies / segments / regions matters, choose the right mechanism:

6. **Distinct archetypes** when the five-test principle indicates material divergence on drivers, default ranges, scenario sensitivity, Five Forces, or regulatory regime. Examples: metallurgical coal vs thermal coal vs domestic-thermal-coal-AU; supermarkets-AU vs supermarkets-US; major-banks-AU vs us-regional-banks.
7. **Submarkets within an archetype** (§7.4 `submarkets[]`) when the product and drivers are similar but regional exposure varies meaningfully. Force ratings can be overridden per submarket; default ranges stay archetype-level. Example: industrial explosives with Australia / North America / RoW submarkets.
8. **Multi-segment within a company** (§8.2 `segments[]`) when a company spans archetypes. Each segment FK-references its own archetype; per-segment positioning lives at the company level. Examples: CSL spanning specialty plasma therapeutics + vaccines + potential Vifor segment; a diversified conglomerate spanning multiple unrelated archetypes; an oil major spanning upstream + downstream + chemicals.

**Geographic specificity as a special case.** Geographic-and-regulatory specificity is built into archetype *identity* (the `id` field) when the regime materially shifts drivers. `major_banks_au` rather than `banks`. `australian_supermarkets` rather than `supermarkets`. `chinese_property_developers` rather than `property_developers`. The default test: if companies in the geography face a meaningfully different regulator, monetary policy regime, accounting framework, or competitive structure from the rest of the world, geography is part of archetype identity.

**Worked examples.** Test the principle against ambiguous cases by walking through the five tests, not by intuition. Three worked examples for the v0.1 spec:

9. **Coal sub-sectors.** Metallurgical coal vs thermal coal: test 3 (scenario sensitivity to climate policy) fails — distinct archetypes. Within thermal coal, domestic-AU vs seaborne: test 1 (driver set) and test 3 (scenario sensitivity) both partially fail — Australian domestic thermal coal is heavily contracted on long-term offtake terms; seaborne is spot-volatile and more exposed to carbon-border-adjustment mechanisms. My lean: distinct archetypes (`thermal_coal_seaborne`, `thermal_coal_domestic_au`) rather than submarkets — but the call can be revisited when a coal company enters the test set.
10. **Banking sub-segments within Australia.** Retail + business + institutional within Australian banking share the archetype's driver set (NIM, credit-loss charge, cost-to-income, CET1, RWA intensity); what differs is the *exposure mix* per segment (institutional has wholesale-funding exposure; retail has mortgage-book physical-risk exposure; business has SME credit-cycle exposure). Test 1 passes; tests 2-5 are within tolerance. My lean: **one archetype, with per-segment positioning at the company level capturing the mix differences**. WBC stays single-segment for v0.1 unless segment-level driver divergence justifies otherwise during populating.
11. **Retail sub-sectors.** Grocery vs apparel vs electronics vs DIY: test 1 (driver-set) and test 3 (scenario-sensitivity) both fail across these — gross margin levels differ structurally; demand-cyclicality differs structurally. Distinct archetypes per sub-sector. A company spanning multiple (e.g. Wesfarmers spanning Bunnings + Kmart + Officeworks + chemicals) is multi-segment.

**As the test set grows.** The archetype taxonomy expands by adding new archetypes that meet the principle, not by stretching existing archetypes to fit new companies. When a candidate company doesn't fit cleanly under any existing archetype, the question is which test fails, and the archetype that meets the principle gets defined.

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
  complementary_framework:                    # optional secondary frame (see §7.5.1)
    type: payor_and_regulator | network_effect | resource_lifecycle | none
    details: object                           # shape determined by type;
                                              # schema co-located with the relevant
                                              # framework definition under
                                              # design/frameworks/<type>.md
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
    imported_input_share_static: low | moderate | high   # static share of cost base
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
      imported_input_share_responsiveness: low | moderate | high   # responsiveness; see cost_structure for static share
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

#### 7.5.1 Complementary frameworks for archetypes Porter does not fully serve

Porter's Five Forces is the dominant frame, but it strains in two recognisable cases:

1. **Heavily regulated archetypes** (banks, insurers, utilities, parts of healthcare) where the binding constraint on returns is a prudential regulator or payor regime, not the five competitive forces. APRA, Basel III, the deposit-insurance regime, and the four-pillars policy aren't *forces* in Porter's sense — they're an external structural overlay that constrains every metric on the bank archetype: CET1 floor sets RWA intensity; deposit-insurance fee structure shapes funding mix; four-pillars policy effectively eliminates new-entrants threat. Stuffing this into "regulatory pressure" inside Five Forces under-states its analytical weight.
2. **Platform / network industries** (digital marketplaces, embedded-finance platforms) where network-effect strength and multi-homing cost capture dimensions Porter does not. Not in the v0.1 test set but worth not painting into a corner.

To handle these without abandoning Five Forces, each archetype carries an optional `complementary_framework` field. The field is **enum-typed**, not free-form: each value points at a defined schema co-located with the framework's methodology document (parallel to the Five Forces question bank).

Initial enum:

1. **`payor_and_regulator`** — for banks, insurers, utilities, regulated healthcare. Captures: primary payors / regulators by name; binding capital or solvency constraint; regulatory regime (e.g. Basel tier, deposit-insurance scheme, four-pillars or equivalent policy); known step-change events on the regulatory horizon. Schema lives at `design/frameworks/payor_and_regulator.md`. Required for the banking archetype (WBC) in v0.1.
2. **`network_effect`** — for tech platforms (when they enter the test set). Captures: network strength, multi-homing cost, side-balance, take-rate sustainability. Schema TBD when first used.
3. **`resource_lifecycle`** — for primary-resource industries (mining, oil-and-gas, rare earths). Captures: reserve life, replacement rate, jurisdictional risk, stranded-asset trajectory. Schema TBD when first used.
4. **`none`** — explicit declaration that Porter alone is sufficient for this archetype.

Adding a new framework type requires defining its schema first. This is a feature: it forces the analyst to write down what comparability across instances of that framework type means, before any archetype claims to use it. Without defined schemas, the field becomes a comment block with delusions of structure — two banks would populate differently-shaped payor-and-prudential blocks, and the comparability discipline that makes Five Forces useful does not carry over.

The complementary framework feeds the same downstream consumers as Five Forces (default driver ranges, scenario sensitivity, disruption surfacing, company positioning). For an archetype using both, the two frames are complementary, not redundant — Five Forces captures the competitive dynamics that exist within the regulatory envelope; the complementary framework captures the envelope itself.

The defined-enum-vs-open-ended question is marked open-to-revisit (§7.7) and should be re-examined after the first non-Porter archetype (banking) is populated, to confirm the discipline is paying for its cost.

### 7.6 Archetypes needed for our test companies

1. **Industrial explosives & ground-support services** — IPL (post-demerger; single-segment industrial explosives). Multi-geographic (Australia, North America, rest-of-world); industry dynamics dominated by mining-customer capex cycles, technology differentiation (electronic initiation systems), and scale in manufacturing / distribution.
2. **Specialty biologics — plasma-derived therapies & vaccines** — CSL. Multi-geographic (US, EU, Asia); may be further sub-divided into Behring (plasma) and Seqirus (vaccines) if their scenario sensitivities diverge materially; to be tested when we populate.
3. **Major Australian banks — retail, business and institutional banking** — WBC. National geography. Uses `complementary_framework: payor_and_regulator` per §7.5.1.
4. **Nitrogen fertilisers** — *kept defined* but no longer required for any v0.1 test company. IPL formerly held this segment; following the demerger, the demerged fertilisers entity is not in the v0.1 test set. Archetype retained because (i) it's a clean illustrative example for the spec, and (ii) it remains available if a fertiliser-segment company is added later.

**On multi-industry companies.** IPL formerly spanned industrial explosives and nitrogen fertilisers as two distinct archetypes with genuinely different industry structures, not merely two segments of one industry. Following the demerger, IPL is single-segment. The multi-segment treatment in the schema remains the right design — CSL is a current case (Behring + Seqirus + Vifor candidate), and any future test company spanning multiple archetypes will use the same mechanism. The corporate-action overlay (§8.4) handles discrete events (demerger / acquisition / divestment) that reshape segment weights at a defined effective year.

**On thin archetypes.** CSL's archetype (specialty plasma therapeutics) has very few peers of comparable scale and positioning. The industry-level matrix may therefore track CSL closely in practice. We retain the industry layer nonetheless for three reasons: (i) writing down the industry-reference view forces explicit articulation of "what a generic specialty-biologics firm would experience in this scenario," which is analytically useful even when only one subject consumes it; (ii) the override mechanism remains available if peers are added later; and (iii) architectural consistency across the three test companies simplifies the engine.

**Narrative deliverable** (per §16.1 item 2): `data/industries/<archetype_id>.md` per archetype — prose Five Forces analysis plus lifecycle / ROIC durability framing plus complementary framework where used. Reused across all companies in the archetype. Produced during archetype population.

### 7.7 Review items

1. **Scenario-sensitivity attribute list.** The block above is comprehensive but may need pruning or additions as we populate actual archetypes. Ben's data-sourcing workstream needs to confirm data availability for each attribute (cross-checked against what `market-ingest` and external sources can populate); attributes that cannot be reliably sourced should either be dropped or marked analyst-judgment-only so the engine does not treat unset as "low".
2. **Multi-segment handling for CSL.** Whether Behring and Seqirus are one archetype with internal segmentation or two distinct archetypes. To be tested when populating.
3. **Treatment of CSL Vifor.** Separate segment or rolled into Behring; depends on the post-acquisition reporting structure Ben can source.
4. **`imported_input_share` rename to disambiguate.** *Resolved* in the v0.1 editorial sweep. `cost_structure.imported_input_share` renamed to `cost_structure.imported_input_share_static`; `scenario_sensitivity.trade_and_supply_chain.imported_input_share` renamed to `scenario_sensitivity.trade_and_supply_chain.imported_input_share_responsiveness`. The two fields are now lexically distinct, eliminating the data-entry ambiguity.
5. **Submarket granularity and data availability.** Where multiple regions are captured, depth of regional analysis is constrained by what Ben's workstream can reliably source per region. Needs alignment.
6. **Lifecycle_rationale field is narrative.** Over time we may want to standardise the way lifecycle is evidenced (e.g. require reference to a peer-group ROIC vs WACC comparison).
7. **Five Forces question bank to be developed.** Build out `design/frameworks/five_forces_questions.md` with two parallel question sets per force (industry-level and company-level). Sub-questions per force based on Porter's determinants. Iterate as we apply it to IPL / CSL / WBC; first cut to be drafted before populating the first archetype so the analysis is structured from the start.
8. **Default driver ranges to be calibrated against Five Forces.** When Layer 4 default ranges are populated for each archetype, cross-check that the ranges (margins, pricing power, capital intensity) are consistent with the Five Forces profile per §7.5 link 2. Inconsistency should trigger a re-examination of either the ranges or the force ratings.
9. **Complementary framework approach (defined enum vs open-ended) — open to revisit.** §7.5.1 commits to a defined-enum approach with per-framework schemas (payor_and_regulator, network_effect, resource_lifecycle). This is the right discipline in principle but untested. After the banking archetype (WBC) is populated using `payor_and_regulator`, revisit: is the discipline paying for its cost, or is it forcing analysts into rigid fields they want to extend? If the latter, consider a hybrid (defined core + extension fields).
10. **Payor-and-regulator framework schema.** `design/frameworks/payor_and_regulator.md` needs to be drafted before WBC is populated. Initial schema: primary_payors / regulators by name; binding capital or solvency constraint; regulatory regime details (Basel tier, deposit-insurance scheme, four-pillars or equivalent); known step-change events on the regulatory horizon.

---

## 8. Layer 3 — Company Positioning

### 8.1 Purpose

Captures where the subject company sits within its industry archetype(s). This is what determines whether a given industry-level impact hits the company harder, softer, or differently than the industry average. Positioning blocks are held primarily at the segment level, because companies frequently span multiple industries with different competitive dynamics (CSL's Behring / Seqirus / Vifor structure is the v0.1 example; IPL formerly held a distinct fertilisers segment which has since been demerged). Single-segment companies carry a single segment that holds the positioning. Discrete corporate events that reshape segment composition over the forecast horizon (demergers, acquisitions, divestments) are handled by the corporate-action overlay in §8.4.

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

### 8.4 Corporate-action overlay (segment-weight events)

Segment weights (`revenue_share`, `ebit_share`) are scalars in the §8.2 schema. To handle a discrete corporate event that reshapes those weights at a defined point in the forecast horizon — a demerger, acquisition, or divestment — the company carries a `corporate_actions` overlay rather than time-keying segment weights directly:

```yaml
company_position:
  # ... fields per §8.2 ...
  corporate_actions:                            # optional list; empty means no
                                                # discrete events in the horizon
    - id: string                                # e.g. "ipl_fertilisers_demerger_2024"
      kind: demerger | acquisition | divestment | spin_off
      effective_year: int                       # year in the forecast horizon
                                                # (1 = first forecast year)
      scenario_id: string | "all"               # event applies under this scenario,
                                                # or under all scenarios
      affected_segments: list                   # segment ids reshaped by the event
      post_event_weights:                       # new revenue / EBIT shares
        - segment: string
          revenue_share: float
          ebit_share: float
      rationale: string
      evidence_refs: list
```

The Layer 6 translator handles the weight transition deterministically: pre-event years use the base-case segment weights from §8.2; post-event years use `post_event_weights`. The transition itself can be modelled as a step at `effective_year` or smoothed using a time profile from §11.3 (`step` for a clean cut-over, `regime_shift` for a phased separation).

This mechanism handles both the historical IPL demerger case (kept as a worked illustration even though IPL itself is now post-demerger) and the generic M&A case. Treating the demerger / acquisition / divestment cases as variants of one design problem — discrete corporate events reshaping segment weights at an `effective_year` — is the substantive merge of the older §8 multi-segment-time-evolution discussion and the older §9.7 M&A overlay item.

For acquisitions where the acquirer takes on a wholly new archetype (rather than expanding an existing segment), the schema also requires a new segment to be appended with its own archetype FK and positioning blocks; the corporate action declares the new segment in `post_event_weights`.

### 8.5 Deliverables

1. A populated `company_position.yaml` for IPL, CSL, and WBC.
2. For each segment, cross-reference to the applicable industry archetype.
3. Reasoning notes captured in-line (YAML comments or `evidence` fields) so positioning is defensible and auditable.
4. Historical financials kept in a separate `financials.yaml` per company, not in this layer.
5. **Narrative deliverable** (per §16.1 item 3): `data/companies/<company_id>.md` per company — prose write-up of moat, franchise assets, competitive position, risk exposures, archetype-specific positioning, and Five Forces company-side findings. Produced during company population.

### 8.6 Review items

1. Archetype-specific schemas for banking, mining, fertilisers, and plasma therapeutics need to be drafted as part of populating the IPL / CSL / WBC archetypes.
2. CSL Vifor: confirm whether reported as a separate operating segment in CSL disclosures. Default treatment is a separate segment within CSL.
3. Innovation-position requirement should be tagged at the industry-archetype level (Layer 2), so the engine can flag missing pipeline data for innovation-driven archetypes.
4. Need to confirm whether `risk_exposures.fx` belongs at parent level (consolidated FX exposure) or per segment, or both. Currently omitted pending decision.
5. IPL post-demerger segment structure to be confirmed by Ben's data-sourcing workstream when populating `data/companies/ipl.yaml`. Default working assumption is single-segment industrial explosives; this should be verified against IPL's most recent segment disclosures (residual stakes, pending divestments, ongoing inter-company arrangements with the demerged entity).
6. Corporate-action overlay (§8.4) needs a worked example once the first event is encountered (e.g. a CSL acquisition or, as illustration, IPL's historical demerger encoded retrospectively).

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
  role: primary | derived              # primary: written by impact matrix (Layer 5).
                                       # derived: computed by Layer 6 from dependencies;
                                       # NOT writable by Layer 5.
  dependencies: list                   # other driver ids (required where role: derived)
  derivation_formula: string           # required where role: derived. Plain-language
                                       # or expression form, e.g.
                                       # "wacc = (E/V) * cost_of_equity +
                                       #         (D/V) * cost_of_debt_pretax * (1 - tax_rate)"
  scope: company | segment             # at what level the driver is populated
  scenario_sensitive: bool             # whether the impact matrix may move it
                                       # (must be false where role: derived)
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

#### 9.4.1 Banking (DDM / residual income, not FCF)

Banks consume an entirely different driver set from FCF-modelled archetypes. Most core FCF drivers (volume / price, gross / EBIT margin, capex intensity, working capital days) are `not_applicable: true` for banks. The bank driver set is:

**Income-statement drivers (segment / business-line scope where bank is multi-line)**

1. Loan book growth (primary, scenario-sensitive)
2. Net interest margin (NIM, bps) (primary, scenario-sensitive)
3. Non-interest income growth (primary)
4. Cost-to-income ratio (primary)
5. Credit loss charge / average loans (primary, scenario-sensitive — heavily so under recession scenarios)
6. Effective tax rate (primary)
7. Net income (derived from above)
8. Return on equity (derived)
9. Return on tangible equity (derived)

**Balance-sheet and capital drivers (company-scope)**

1. CET1 ratio target (primary)
2. Risk-weighted-asset intensity (RWA / total assets) (primary)
3. RWA growth (derived from loan book growth × RWA intensity)
4. Required equity (derived from CET1 target × RWA)
5. Asset mix (mortgage / business / institutional / other shares) (primary)

**Funding drivers (company-scope)**

1. Deposit-funding share (deposits / total funding) (primary)
2. Wholesale-funding share (primary, scenario-sensitive — funding stress under banking-sector scenarios)
3. Liquidity coverage ratio (LCR) target (primary)
4. Net stable funding ratio (NSFR) target (primary)
5. Deposit franchise stickiness (primary)

**Distribution and terminal drivers (company-scope)**

1. Dividend payout ratio (primary)
2. Buyback posture (primary)
3. Terminal cost of equity (primary)
4. Terminal ROE (primary; subject to convergence principle — terminal ROE ≈ cost of equity unless defended)
5. Terminal RWA growth (primary)
6. Fade period length and profile (primary)

The bank valuation flow is conceptually: rates / scenario → NIM and loan growth → net income → ROE → equity value (via DDM or residual income), with capital ratios and funding mix as binding constraints rather than free variables. The full DDM / residual-income mechanics are specified in the DCF Engine layer (§12).

#### 9.4.2 Other archetype-specific driver sets to draft

1. **Plasma therapeutics / life sciences.** Pipeline NPV contribution, probability-weighted pipeline revenue ramp by therapy, R&D productivity (revenue per R&D dollar, defined window), patent-cliff exposure profile.
2. **Mining / commodity industrials.** Cost-curve placement-driven margin trajectory, reserve life, by-product credits, jurisdictional risk index.
3. Other archetypes (insurers, REITs, utilities) added as scope expands.

### 9.5 Deliverables

1. A populated `drivers.yaml` carrying the core driver catalogue with default schema.
2. Per-archetype driver sets co-located with archetype YAMLs (Layer 2).
3. Default ranges per archetype, calibrated against Five Forces profile.
4. Cross-walk note documenting which drivers the impact matrix (Layer 5) is permitted to move.

### 9.6 Open

1. Whether WACC moves across scenarios (i.e. whether the WACC-component drivers are actively used by the impact matrix) is a Layer 7 / DCF Engine decision. Layer 4 keeps the option open by tagging the components as `scenario_sensitive: true`; the actual choice is deferred to §12.

### 9.7 Review items

1. Archetype-specific driver sets for plasma therapeutics, mining, and fertilisers need to be drafted alongside their Layer 2 archetype definitions and Layer 3 archetype-specific positioning fields. Banking is now drafted in §9.4.1.
2. **M&A overlay merged with §8.4 corporate-action overlay.** The earlier separate "M&A overlay" item is folded into the §8.4 corporate-action overlay — the demerger / acquisition / divestment / spin-off cases are one design problem (a discrete corporate event reshaping segment weights at an `effective_year`). Acquisition deal economics (price, integration cost, synergies, financing) sit in this overlay, not in the base organic driver list.
3. Innovation-position driver requirement: where Layer 2 flags an archetype as innovation-driven, the corresponding archetype-specific driver set must include pipeline-value drivers; the engine should warn if missing.
4. WACC scenario behaviour to be revisited at §12 (DCF Engine) per §9.6 open item.
5. Default-range calibration loop: when default ranges are populated, cross-check consistency with the archetype's Five Forces profile (per §7.5 / §7.7 item 8). Inconsistency triggers re-examination of the ranges or the force ratings.
6. **Driver-ID style guide to be drafted before populating the catalogue.** Once IDs are baked into the impact matrix, renaming is a breaking change discovered exactly when the matrix is most painful to migrate. Initial style-guide topics: naming convention (snake_case), group prefixes (e.g. `rev_`, `mgn_`, `cap_`, `fin_`, `term_`, `bank_`), avoidance of vendor-specific terminology, stability guarantees once published.
7. **Derived-driver derivation formulas need to be populated** under the new §9.2 `derivation_formula` field. For each driver tagged `role: derived` (cost of equity, WACC, EBIT margin, EBITDA margin, asset turnover, operating leverage coefficient, effective tax rate, return on equity, RWA growth, required equity), write the formula plain-language or expression form. Layer 6 consumers depend on these being explicit.
8. **Driver default-range completeness check.** Validator: for each (archetype × driver), confirm `default_range` is populated. Driver missing a default range under an archetype that uses it (i.e. driver is in `applicable_archetypes` for that archetype) should fail validation.
9. **Terminal-growth assumptions reflect demographic-adaptation trajectory.** Even when a scenario's explicit forecast horizon does not reach the demographic cliff (the late-2040s / 2050s use-by date for immigration-led adaptation in advanced economies), the terminal-growth assumption must reflect the trajectory the scenario is on. Self-sufficient demographic-response capability (China via industrial robotics) supports higher terminal growth; economies renting demographic time from a shrinking global skilled-migration pool (Australia, parts of Europe) carry lower terminal-growth assumptions. Terminal growth is therefore not a single scalar per company — it's a **scenario × company × geography**-conditional value. Sit alongside the §1 / §7.3 / §11.4.2 cost-of-capital convergence discipline; surfaces under the §11.4.2 rule 4 terminal-share-reasonableness check. Convention to be implemented when terminal-growth rules are drafted; surfaced from the scenarios workshop (16 May 2026).

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
                                              # | data_workstream | other
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
      created_by: string                      # named human, the analyst writing
      created_at: datetime
      approved_by: string                     # named human, the peer reviewer
      approved_at: datetime
      last_reviewed_at: datetime
      review_dialogue:                        # optional but recommended for sign-flip
                                              # or beyond-scale overrides — captures the
                                              # reviewer-vs-author challenge / response
        - challenge: string                   # what the reviewer pushed back on
          challenger: string                  # named human
          response: string                    # why the analyst persisted (or revised)
          challenge_at: datetime
      half_life:                              # tied to scenario refresh cadence (§6.5)
        scenario_version_at_creation: string
        review_required_at_scenario_version: string  # next refresh
        stale: bool                           # true once that version is current
        requires_re_review: bool              # set true when scenario_version bumps;
                                              # rationale was scenario-version-specific
```

**Override semantics:**

1. **Partial override.** Either `override_direction` or `override_magnitude` (or just `quantified_override`) may be supplied; absent fields inherit from the industry default.
2. **Sign-flip override.** Permitted when override direction opposes industry direction; the validator must flag `sign_flip: true` and require `evidence_refs` of at least two items.
3. **Beyond-scale override.** When the analyst's view would push beyond the ordinal scale (e.g. industry already `positive / large`), the override must carry a `quantified_override` band; ordinal fields then describe the *closest* representative ordinal and `beyond_scale: true` is set.

**`reason_category: data_workstream`** — added explicitly so overrides driven by data-source-induced views (e.g. "overriding because EODHD's revenue segmentation differs from the company's primary disclosure") are auditably distinct from analyst-judgment overrides. Keeps the data-vs-judgment line clean for governance.

**Override density discipline.** Overrides should be a small fraction of cells. If more than a defined threshold of a company's matrix is overridden (target: ≤20% of cells per company; archetype-tunable), the industry archetype is mis-specified or the overrides are over-fitted. The validator emits a warning at the threshold; investigation should consider revising the archetype rather than continuing to add overrides. Otherwise the "data as data, logic as code" principle is undermined by override creep — the matrix becomes a per-company library and the archetype layer ceases to do useful work.

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

### 10.6 Consistency rules and what the matrix is permitted to write

The impact matrix is the analytical core; entries must respect cross-layer constraints. Two distinctions matter:

**Layer 5 only writes primary drivers.** Drivers tagged `role: derived` in §9.2 (cost of equity, WACC, EBIT margin, EBITDA margin, asset turnover, operating leverage coefficient, effective tax rate, return on equity, RWA growth, required equity, etc.) are computed by Layer 6 from their dependencies via the formula declared in §9.2 `derivation_formula`. The impact matrix must not write to derived drivers. This rule replaces the earlier "consistency rules" treatment of tax aggregation, capex → D&A, and WACC computation: those are deterministic derivations performed in Layer 6, not coherence checks at all. Removing redundant derived-driver cells from the matrix also reduces analyst population effort meaningfully.

**Genuine consistency rules applied to the matrix.** The engine should validate (warn or block) the following:

1. **Scenario-sensitivity consistency (cross-check with §7.4).** Matrix entries should be consistent with the industry archetype's `scenario_sensitivity` block. Example: if `scenario_sensitivity.labour.wage_pass_through` is `low`, an entry under a wage-shock scenario showing `input_cost_pass_through: positive / large` must carry explicit defence in `rationale`.
2. **Cost-of-capital convergence with defended-exception criteria (cross-check with §1 and §9.3).** Matrix entries on terminal-state drivers (terminal ROIC, terminal growth, terminal margin, fade period) must respect the convergence principle — in steady state, terminal ROIC should approximate WACC (or, for banks, terminal ROE should approximate cost of equity). Entries that imply persistent excess returns are permitted only when the entry carries a **defended exception** with all four of the following:
   (a) **Moat source** named explicitly from §8.2 `moat.sources` enum.
   (b) **Decay / half-life** specifying when the moat fully erodes under the scenario in question, in years. "Perpetual" is not permitted without an explicit external benchmark.
   (c) **Named competitive threat** that *would* erode the moat. If the analyst cannot name what would compress the excess return, the moat is lazy and the entry is treated as undefended.
   (d) **Sensitivity test** — a paired scenario value showing how the valuation moves if the moat is accepted for half the stated duration.
   Entries lacking any of (a)–(d) are treated as undefended; the validator applies convergence anyway and flags the entry. This is what makes "defended" earn its keep.
3. **Freshness.** Entries carry `scenario_version`. The engine should warn when an entry references a scenario version older than the current scenario library; entries flagged stale are candidates for re-review at the next 6-month refresh.
4. **Sign-flip evidence.** `sign_flip: true` overrides require `evidence_refs` of at least two items.

Driver interactions of the cross-driver-coherence kind (e.g. directional consistency between revenue and margin movements; mix-shift sanity at company aggregation) are enforced in Layer 6 (§11.4), not here. The matrix carries each primary-driver movement independently.

### 10.7 Review items

1. **Default direction-magnitude → numeric-band mapping per driver.** Lives in Layer 4 (driver schema). Needs to be populated per archetype as part of populating the driver catalogue. Without this mapping the hybrid encoding cannot translate to numbers in Layer 6.
2. **Validator implementation.** Consistency rules in §10.6 must be implemented as engine validation, not only stated. Includes: derived-driver write-protection, scenario-sensitivity consistency, defended-exception criteria check, freshness warning, sign-flip evidence count, and the override-density threshold from §10.4. Build alongside Layer 5 code.
3. **Reason category enum stability.** Initial enum is `cost_advantage | scale | regulation | contract | management | product_mix | diversification | franchise_asset | data_workstream | other`. To be revisited after first pass populating IPL / CSL / WBC overrides; new categories added if patterns demand.
4. **Governance roles.** `created_by` = analyst writing the override; `approved_by` = named peer reviewer (one named human, not a committee, until volume requires otherwise). The audit-trail value comes from named humans more than formal governance structure.
5. **Beyond-scale override convention** (`beyond_scale: true` plus quantified band) needs a worked example once we hit a real case in populating IPL / CSL / WBC.
6. **High-importance driver completeness check.** Convention is sparse, but a validator should warn when a driver flagged "high importance" for an archetype has no matrix entry under any scenario. Mechanism for flagging "high importance" to be defined alongside the driver catalogue.
7. **Override density threshold per archetype.** §10.4 sets a default threshold of ≤20% of cells overridden per company. Threshold should be archetype-tunable — thin-archetype cases (CSL) may legitimately sit higher. Calibrate after first pass populating.
8. **Half-life staleness propagation logic.** When a scenario YAML bumps version, the engine should mark every override referencing the old `scenario_version_at_creation` with `requires_re_review: true`, on the basis that the override's rationale was scenario-version-specific. The override itself is preserved (not deleted); reviewer chooses whether to refresh, replace, or retire it at the next 6-month cycle.

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

Library lives as code in `src/vcc_valuations/assumptions/time_profiles.py`. Per-driver defaults and per-scenario overrides live as data.

### 11.4 Derivations and consistency checks

This section was previously a single list of "consistency rules." Following platform-side review the items have been split into two categories: **derivations** (deterministic identities computed once primary drivers are translated) and **consistency checks** (genuine cross-driver coherence checks that warn or reconcile). The split matters because derivations have an answer; consistency checks have a range.

#### 11.4.1 Derivations (deterministic — Layer 6 computes; Layer 5 does not write)

Each driver tagged `role: derived` in §9.2 carries a `derivation_formula`. Layer 6 evaluates these formulas after primary drivers are translated. Each derivation writes to the reasoning trace.

1. **Effective tax rate.** Statutory rate per geography × revenue / EBIT mix → company-level effective rate. Identity, not coherence.
2. **Capex → D&A.** Asset-life-weighted depreciation roll-forward from the capex stream and base-year depreciable-asset balances. Identity.
3. **Cost of equity.** `rfr + ERP × β + country_premium + small_cap_premium` (or equivalent CAPM-with-premia form). Identity.
4. **WACC.** `(E/V) × cost_of_equity + (D/V) × cost_of_debt_pretax × (1 − tax_rate)`. Identity.
5. **EBIT margin / EBITDA margin.** Computed from gross margin and below-the-line drivers per the archetype's cost structure. Identity-with-noise; tolerance comes from cost-structure granularity rather than from disagreement between layers.
6. **Return on equity (banks).** Net income / average equity, with required equity backing out from CET1 target × RWA. Identity.
7. **RWA growth (banks).** Loan book growth × RWA intensity. Identity.

These were previously framed as "consistency rules" in §11.4 rules 2–4. They are not checks. The matrix should not write to these drivers; Layer 6 computes them.

#### 11.4.2 Consistency checks (genuine cross-driver coherence)

After derivations, the engine applies the following genuine consistency checks. Each writes to the reasoning trace.

1. **Operating-leverage directional check.** Reframed from the earlier magnitude-based rule. The earlier formulation ("revenue × fixed-cost share implies an EBIT-margin range") assumes static cost structure, smooth operating leverage, and no segment mix shift — which is too strong in practice (costs are step-function, not continuous; operating leverage interacts with capacity utilisation; mix shift between segments can reverse the implied margin sign). The check is therefore **directional only**: if revenue moves `negative / large`, EBIT margin should not move `positive / large`; if revenue moves `positive / large`, margin should not move `negative / large` without rationale. The analyst can override the directional check with an explicit rationale recorded against the consistency-check trace entry. Avoids the rule itself becoming a source of artefact.
2. **Terminal-state convergence (cross-check with §10.6 rule 2).** Enforced at translation time. Terminal ROIC ≈ WACC (or terminal ROE ≈ cost of equity for banks) unless the matrix entry carries a §10.6-compliant defended exception (moat source named, decay horizon stated, named threat, sensitivity test). Layer 6 reapplies the convergence rule using the full set of translation outputs, in case derivations have shifted WACC since the matrix was populated.
3. **Mix-shift check at company aggregation.** When per-segment movements are aggregated to company level via the §11.2 step 5 `aggregation_method`, the rule warns when revenue mix shifts materially across segments and the implied company-level margin movement diverges from a naive segment-weighted average by more than a defined threshold. Surfaces accidentally inconsistent assumptions where the analyst forgot the mix effect.
4. **Terminal-share reasonableness.** Once Layer 7 produces an EV / equity value (via §14 Phase 3.5 smoke-test or full §12 engine), if terminal value contributes more than 70% of EV the engine forces a sensitivity pass on terminal assumptions. Prevents the dominant DCF failure mode of a terminal assumption silently driving the result.

Consistency checks live as code (they're structural in form; the thresholds are calibratable).

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
3. **Consistency-check priority and ordering.** When multiple checks touch the same driver (e.g. operating-leverage directional check AND terminal convergence both touching terminal margin), priority order must be defined. Default proposal: derivations first (§11.4.1), then convergence checks, then reconciliation checks.
4. **Bank DDM consolidated shape.** The `consolidated_assumptions_ddm` driver list is now drafted in §9.4.1; needs to be co-located with the banking archetype YAML when populated.
5. **Reasoning-trace storage.** Inline in the `AssumptionSet` is the v0.1 default — single source of truth, no synchronisation problem. If file size becomes an issue with many-scenario × many-company runs, split to a side-car `audit/{company}_{scenario}.yaml` with a stable hash linking back to the `AssumptionSet`. Don't pre-optimise.
6. **Parametric horizon source.** §2 says horizon is parametric per company-scenario; needs an explicit field in the scenario object (or scenario-company application) declaring the horizon for each combination.
7. **Driver-schema fields populated per driver.** §9.2 already includes `base_definition`, `default_time_profile`, `aggregation_method`. The remaining work is to populate these fields per driver, not to add them to the schema. (Earlier draft of this review item was stale — closed.)
8. **Confidence-band convention for macro time series (cross-link to §6.7 item 4).** Macro variable time series carry `confidence_band: {min, mid, max}`. Convention adopted: bands are *analyst subjective range conditional on the scenario playing out as defined*. Empirical historical-conditional bands imply the scenario already happened; consensus bands import other forecasters' priors. Subjective-conditional is honest about what's being claimed.

**Narrative deliverable** (per §16.1 item 4): `analyses/<company>/scenarios/<scenario_id>.md` per scenario × company — prose write-up of how this scenario plays out for this company, sourced from the impact matrix entries (§10), overrides, and the resulting `AssumptionSet`. The §11.6 reasoning trace is the underlying evidence base.

---

## 12. Layer 7 — DCF Engine *(deferred, brief)*

Consumes an `AssumptionSet` object, returns enterprise value, equity value, and per-share value plus sensitivity tables. Distinct implementations required: traditional unlevered FCF DCF for IPL and CSL; residual income / DDM for WBC and any other archetype tagged `valuation_model: ddm | residual_income`. To be specified in a separate document once Layers 1–6 are built and a Phase 3.5 smoke-test (§14) has run end-to-end through one IPL × one scenario.

**Relationship to `vcc-pricing-engine`.** The platform's separate `vcc-pricing-engine` (NoCodeQL containerised; bond / swap / curve pricing via QuantLib) handles current valuations of structured products. This valuations module handles forward-looking equity DCFs under scenarios. Two complementary services on the platform: pricing is point-in-time, mark-to-market structured-product valuation; valuations is scenario-conditional forward equity valuation. They share the **scenario library at the macro layer** — interest-rate / FX / commodity scenarios feed both — which is part of the case in §5.1 item 8 for hosting the scenario library platform-side rather than valuation-internal.

**Narrative deliverables** (per §16.1 items 5 and 6):
- `analyses/<company>/valuations/<scenario_id>.md` per scenario × company — one-page valuation note: headline EV / equity value / per-share value, drivers of value, sensitivities, what would change the view.
- `analyses/<company>/thesis.md` per company (rollup) — cross-scenario investment view: overall picture across scenarios, where the asymmetry sits, what would update the view.

---

## 13. Layer 8 — Interactive Interface *(deferred, brief)*

Per §2.1, the user interface is **embedded in the existing VCC dashboard**, not built as a separate frontend. The valuation module exposes a JSON API; the dashboard's existing module loader (`v2.html` shell + `static/js/v2/` modules) renders the API output as a **Valuations tab on each per-company VCC** (CSL VCC, IPL VCC, WBC VCC). Single UX, single auth, single ops surface; the Vue frontend originally sketched here is no longer being built.

**Per-company tab capabilities:**

1. View `AssumptionSet` for the selected company × scenario, with the §11.6 reasoning trace inline and expandable per-driver.
2. Compare scenarios side-by-side for one company (default view — discourage reading any single scenario as "the answer"; per §3.3 and the §6.2 boundary-cases commitment, comparison is canonical).
3. View driver movements (Layer 5 output) and the underlying scenario × industry × override chain.
4. View / propose modifications to assumptions (the user-facing assumption-inspection and modification capability foreshadowed in §1).
5. Sensitivity and tornado charts once the DCF engine (Layer 7) is live.

**Cross-company:**

6. Compare companies under one scenario, rendered as a multi-VCC view in the dashboard.

**Reasoning-trace API surface.** The `reasoning_trace` is queryable per `(company, scenario, driver)` tuple, not only as a full-`AssumptionSet` download. This is what supports the per-company VCC chat persona (e.g. "specialty plasma equity analyst" for CSL): when a user asks *"what's your view of CSL under Scenario 3?"*, the VCC chat surface pulls the relevant trace slice and answers with the chain — scenario narrative → industry impact → company position → driver movement → assumption value → DCF output. The schema in §11.5 supports this; the API surface needs explicit per-driver retrieval endpoints.

**Default view discipline.** The headline view defaults to a multi-scenario fan chart with scenarios visually distinguished — *not* a single mid-scenario number. This is a behavioural-design choice consistent with §3.3 / §6.2: scenarios are boundary cases, and comparison is the natural action the UI should support.

**Deferred details.** The CLI and per-tab UI specs themselves live in their own design documents once the engine is working. CLI commands `vcc valuation regenerate <company> <scenario>` and `vcc valuation diff <company> <scenario_old> <scenario_new>` are scoped in §14.

---

## 14. Phasing Plan

1. **Phase 0 — Design (now).** This document + scenarios workshop. No engine code yet.
2. **Phase 1 — Schema & data layer.** Formalise YAML schemas; populate industry archetypes, company positions, and one or two scenarios as worked examples. Draft the Five Forces question bank (§7.7 item 7) and the `payor_and_regulator` framework schema (§7.7 item 10) before the relevant archetypes are populated.
3. **Phase 2 — Impact matrix population.** Populate the matrix across all scenarios × all three industries. Document reasoning. This is the intellectually heavy phase. See §14.1 below for population approach (starter templates, minimum-viable matrix, time budget).
4. **Phase 3 — Assumption translator.** Code the translator that turns driver movements + base-year snapshot into `AssumptionSet` objects. First end-to-end run: IPL × base case.
5. **Phase 3.5 — Smoke-test DCF.** Insert a minimal end-to-end run before Phase 4 expands across all scenarios. Even a 50-line traditional FCF DCF and a 50-line two-stage DDM. Run one IPL × one scenario through the full pipeline (Layers 1–7) before populating across all scenarios. Cheap insurance against schema rework — surfaces any assumption-set shape problems while the schema is still cheap to revise. Likely findings: terminal-state convergence forcing inexpressible reinvestment rates; FCF cycles requiring debt-financing assumptions Layer 6 hadn't generated; banking residual-income shape revealing a missing bank-specific driver. A few days of work; saves weeks if the cascade has to be re-run.
6. **Phase 4 — Expand and calibrate.** Run all three companies across all scenarios. Compare IPL outputs to the strategist-friend benchmark per §15. Iterate on matrix and overrides. This is also where the trace-comparison tooling for the strategist benchmark gets built (§15).
7. **Phase 5 — DCF engine.** Productionise the traditional FCF DCF and the bank DDM / residual-income engine; replace the Phase 3.5 smoke-test stubs with full implementations.
8. **Phase 6 — Interface integration.** Embed valuation output as a Valuations tab in the existing VCC dashboard per §13. Build CLI commands (§14.2). No standalone frontend.

### 14.1 Phase 2 / Phase 4 population approach

Populating the impact matrix is the intellectually heaviest part of the work and the single largest call on analyst time. To make the work tractable:

1. **Starter templates with pre-populated expected cells.** Under each scenario, pre-populate the cells where the direction is essentially given by the scenario narrative (e.g. revenue growth in a recession scenario is almost always negative for non-defensive industries; rates in a tightening scenario are positive for bank NIM). The analyst confirms / adjusts rather than writing from blank. Templates live alongside scenarios in `data/translation_rules/` and are versioned.
2. **Minimum-viable matrix per archetype.** Identify 5–10 *load-bearing* drivers per scenario per archetype — the ones that materially drive the headline assumption (revenue growth, EBIT margin, capex intensity, terminal margin for FCF; NIM, loan growth, credit-loss charge for banks). Populate these first. The long tail of drivers (asset turnover, working capital days, country premium, etc.) is populated only if the headline doesn't tell the full story or the strategist-friend comparison surfaces a gap.
3. **Five Forces question bank as the structuring tool.** The §7.7 question bank should be drafted in Phase 1 and applied as the analyst works through each archetype, so the analysis is structured rather than ad-hoc.
4. **Override discipline target.** Per §10.4, override density should sit ≤20% of cells per company. If population starts heading higher, pause and revisit the archetype.
5. **Analyst time budget — provisional 3 weeks per archetype-company pair.** Working anchor for planning purposes only. Acknowledged drivers of variation: archetype novelty (banking and other non-Porter archetypes likely sit higher; subsequent applications of an established pattern compress); data-source maturity for the archetype; segment count (multi-segment companies take longer); calibration loops with the strategist friend (IPL specifically). Budget to be **calibrated against actuals** as IPL / CSL / WBC are populated; first revisit after IPL completes. Marked open-to-revisit (§14.3).

### 14.2 Tooling for analyst workflow (Phase 4 onward)

Add to the existing platform `vcc` CLI:

1. **`vcc valuation regenerate <company> <scenario>`** — re-runs Layers 1–6 for one combination; useful when a scenario YAML or company override changes. Writes the regenerated `DriverMovementSet` and `AssumptionSet` to `output/`.
2. **`vcc valuation diff <company> <scenario_old> <scenario_new>`** — shows which `AssumptionSet` fields changed and why, by cross-referencing the `reasoning_trace`. Most useful when calibrating overrides or when Ben's data workstream updates a base-year snapshot.
3. Both sit alongside the existing `vcc fundamentals` / `vcc news` commands; no new CLI framework needed.

### 14.3 Review items

1. **Analyst time budget per archetype-company pair — open to revisit.** Initial planning anchor of 3 weeks per pair is provisional. Calibrate against actuals; first revisit after IPL completes. Track actuals broken into research / schema population / override population / calibration / review so the empirical anchor is granular enough to be useful. Reported in Phase 4 retrospective.
2. **Phase 3.5 smoke-test scope.** What counts as "good enough" for the smoke-test FCF and DDM stubs needs nailing down so the work is bounded. Proposed minimum: explicit-period free cash flow projection through the parametric horizon; Gordon-growth terminal; nominal WACC discounting; no fancy mid-period or stub-period adjustments. Same shape applies to a two-stage DDM for the bank.
3. **Starter-template authoring** — who drafts the pre-populated expected cells, and against what reference set. Likely: Tara drafts initial set as part of the scenarios workshop output; Ben's data workstream confirms data feasibility.

---

## 15. Calibration & Validation

### 15.1 Calibration angles

1. **External benchmark — strategist-friend on IPL.** IPL has an independent scenario-valuation exercise already completed by a strategist friend. Treat this as the most important single calibration input — not because the strategist is necessarily right, but because divergence between framework output and strategist output **is the diagnostic**:
   (a) If both agree on conclusion but for different reasons → framework and strategist intuition are converging, good signal.
   (b) If both agree on conclusion for the same reasons → unsurprising, weak signal.
   (c) If both disagree on conclusion → the reasoning trace localises *where* the disagreement sits (positioning vs scenario impact vs translation), which is more valuable than either being individually right.
   Build the **trace-comparison tooling early** (Phase 4): compare side-by-side the two reasoning chains, not just the headline numbers.
2. **Internal consistency checks.** Macro variables inside a scenario must be logically consistent; impact-matrix entries should not contradict the scenario narrative; company overrides must have reason codes; derived drivers must be writable only by Layer 6, not by Layer 5; defended exceptions to terminal convergence must satisfy the four §10.6 criteria.
3. **Out-of-sample application.** Once the framework is stable, applying it to a company not in the test set (e.g. BHP) is the simplest test of generalisability.

### 15.2 Calibration techniques (within each angle)

The structure of three angles is settled; the techniques inside each are:

1. **Historical scenario backtest.** Take a real past scenario shock (GFC 2008–09; COVID 2020; post-2022 inflation). Apply the framework retroactively: encode IPL's 2007 positioning, run the framework's "GFC scenario" against the 2008 base year, generate the framework's predicted margin / capex path, compare to what actually happened. If the framework systematically under- or over-estimates the magnitude of the shock, the translation rules are mis-calibrated. Cheap diagnostic for the bps mappings in `data/translation_rules/` because we know the answer.
2. **Framework-internal sensitivity analysis.** Decompose total variance in the headline output across the layers: how much is driven by scenario macro variables (Layer 1), industry archetype attributes (Layer 2), company positioning (Layer 3), driver default ranges (Layer 4), impact matrix entries (Layer 5), translation rules (Layer 6)? Whichever layer dominates is the load-bearing beam, and deserves disproportionate scrutiny. A common finding in scenario-DCF frameworks: translation rules end up dominating; if so, those bps mappings are not just plumbing — they're the framework's load-bearing beam.
3. **Terminal-share reasonableness check.** Terminal value share of total EV is a known place where DCFs go wrong (terminal often 60–90% of EV, so terminal assumption changes dominate). Validator (also referenced in §11.4.2 rule 4): if terminal contributes >70% of EV under any scenario, force a sensitivity pass on terminal assumptions and require explicit defence in the reasoning trace.

### 15.3 Review items

1. **Backtest design.** Which historical episodes, which scenario mappings, which companies (IPL is the obvious candidate; CSL through COVID is potentially informative; banks through GFC). To be planned alongside Phase 4.
2. **Sensitivity-analysis methodology.** Per-layer variance decomposition needs a defined methodology — either Sobol indices (rigorous but expensive) or one-factor-at-a-time perturbation (cheaper, less precise). Decision deferred to Phase 4 implementation.

---

## 16. Conventions

1. **Monetary units.** Each company's positioning and assumption set is denominated in its **functional currency** (see §2 item 7 and §8). Segment-level functional currencies are supported where a segment operates in a materially different economic environment from the parent. Cross-company comparisons in the interface convert to a common display currency (default AUD) at spot; FX is a scenario variable.
2. **Fiscal year.** All three subjects report to 30 June. "Year 1" in assumption sets means the first full forecast year after the most recent reported FY.
3. **File naming.** `snake_case` for ids and filenames; `CamelCase` for Python classes.
4. **Schema versioning.** Every schema carries a `version` field; breaking changes bump major version and require a migration note in `design/schemas/migrations.md`.

### 16.1 Narrative deliverables

Alongside the structured engine outputs (YAML, JSON, computed numbers), every key analytical component carries a parallel **narrative write-up** — the form an analyst or client can read in prose, not extract from fields. The structured artefacts and the narrative artefacts are two views of the same analysis; the structured ones are the source of truth for ratings, lists, and numbers, and the narrative explains them.

**Mental model.** `data/` carries inputs (structured + the prose description of the input); `analyses/` carries engine outputs made readable.

**The six narrative deliverables and where they live:**

1. **Scenario narrative** — `data/scenarios/<scenario_id>.md`. Per scenario, reused across all companies. Describes the future-world: macro variables, regime characterisation, what gets disrupted, what stays stable, time profile. Sources from §6. Produced during the scenarios workshop (step 3 of the build plan).
2. **Industry view** — `data/industries/<archetype_id>.md`. Per archetype, reused across all companies in the archetype. Five Forces narrative (industry-level), lifecycle and ROIC durability framing, complementary framework where used (§7.5.1), default driver-range commentary. Sources from §7. Produced during archetype population.
3. **Company positioning** — `data/companies/<company_id>.md`. Per company. Moat, franchise assets, competitive position, risk exposures, archetype-specific positioning, Five Forces company-side findings (where positioning diverges from the industry pattern). Sources from §8. Produced during company population.
4. **Scenario impact narrative** — `analyses/<company>/scenarios/<scenario_id>.md`. Per scenario × company, roughly 1–2 pages. "How does this scenario play out for this company." Sources from §10 (impact matrix entries + overrides) and §11 (`AssumptionSet`). The structured `DriverMovementSet` and `AssumptionSet` provide the evidence; this is the readable version.
5. **Valuation note** — `analyses/<company>/valuations/<scenario_id>.md`. Per scenario × company, roughly one page. Headline EV / equity value / per-share value, the drivers of value, sensitivities, what would change the view. Sources from §12.
6. **Cross-scenario investment view (thesis)** — `analyses/<company>/thesis.md`. Per company, rollup. The synthesis: overall picture across scenarios, where the asymmetry sits, what would update the view.

**Cross-referencing convention.** Each narrative file cites the specific YAML / JSON schema fields it draws from, so a reader can jump from prose to source. The §11.6 reasoning trace is the shared evidence base for the scenario impact narrative and the valuation note — those two narratives are essentially human-readable wrappers around their respective structured outputs.

**Source-of-truth rule.** Where prose and structured fields disagree, the structured field wins (as a definitional source). The narrative then needs updating, not the structured field. A simple validator can flag mismatches (e.g. ratings cited in prose that don't match ratings in YAML); this is overkill for v0.1 but worth flagging for later.

**Refresh cadence.** Tied to the 6-month scenario refresh (§6.5). Scenario narrative refreshes when the scenario does. Industry view, company positioning refresh when their underlying YAML changes materially. Scenario impact narrative, valuation note, and thesis re-generate when any upstream input changes (and `vcc valuation regenerate` per §14.2 is the mechanism).

**Length discipline.** Each narrative is "brief" by design — typical lengths are scenario narrative 2–4 pages, industry view 3–5 pages, company positioning 3–5 pages, scenario impact 1–2 pages, valuation note 1 page, thesis 1–2 pages. Total per company-archetype-scenario set: roughly 15–25 pages. The discipline is to write what a reader needs, not exhaustive coverage.

**Layer-section forward references.** Each layer section that has a narrative deliverable carries a one-line pointer to the relevant entry in this §16.1 list. The narrative is a layer's deliverable, even though the convention is centralised here.

---

## 17. Immediate Next Steps

1. Mark up this document — anything to add, remove, or challenge.
2. Scenarios workshop — develop 4–5 named scenario themes with narrative and macro-variable outlines.
3. First industry archetype — populate `fertilisers_explosives.yaml` as the pilot; test that the schema holds up under real content before populating the other two.
4. First company positioning — populate `ipl.yaml` as the pilot; same logic.
5. Decide horizon default once scenario arcs are visible.
