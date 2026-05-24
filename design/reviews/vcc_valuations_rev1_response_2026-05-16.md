# Response to `vcc_valuations` rev1 design

**Document under review:** `VCC_VALUATIONS_DESIGN_REV1_2026-05-12.md` (rev 1, 12 May 2026)
**From:** Tara Reid + Claude (working pair)
**To:** Ben + collaborator
**Date:** 16 May 2026
**Companion to:** `design/architecture.md` v0.1 (frozen 7 May 2026, tagged `architecture-v0.1`), `design/frameworks/five_forces_questions.md`, `design/frameworks/payor_and_regulator.md`.

---

## Top line

Strong design. The "scenarios ARE workspaces" unification is genuinely the right keystone insight, and getting to zero new tables on this much functionality is impressive. The cross-references to the 5 May 2026 review (Concerns §A–§L) are precise, which suggests the design has been built against that review rather than around it.

Nothing here undermines our architecture — the alignment is high. The feedback below is about pinning a small number of points where the schema and our v0.1 spec haven't quite met yet, plus a handful of smaller items and two clarification questions. We have not changed any architecture content based on the design; if any of items 1–8 below result in changes to our spec, we would treat that as a v0.2 bump per the schema-versioning convention.

---

## Strengths worth acknowledging

The following load-bearing choices are good and we would not change them:

1. **The unification thesis holds.** Scenarios = workspaces is the load-bearing claim and it works once you accept that an SMSF tax-planning fork, a valuation scenario, and a structurer's pricing scenario have the same primitive structure. Same shape, different domain.
2. **Zero new tables** is a real architectural achievement on this much functionality. Two column ALTERs, ~120 seed rows, and 9 views is a defensible footprint.
3. **`Knowledge.fact` carrying both LLM-extracted and analyst-curated assertions** is elegant. The "extraction_run as analyst session" framing puts both kinds of provenance through the same plumbing.
4. **Reasoning trace as recursive CTE over `fact_relation`** is the right shape. It supports the §11.6 reasoning-trace discipline and the §13 per-tuple reasoning-trace API the dashboard chat surface needs.
5. **View-only `"Valuations"` schema** as the dispatcher contract is well-judged — it gives analysts and the dashboard ergonomic shapes while keeping the leverage in the underlying primitives. The cross-DB stitching note (views in `vcc_core` cannot natively join into `Knowledge.fact` in `vcc_memory`; the dispatcher does the composition) is a real tooling cost worth understanding, but the shape is right.
6. **Override governance via `Data.value_annotation` payloads** with `IMPACT_CELL_OVERRIDE`, `ASSUMPTION_OVERRIDE`, `BRIDGE_OVERRIDE` types lands the §10.4 governance block cleanly.
7. **YAML-as-seed-data bootstrap** is the right migration path. Our existing `data/scenarios/`, `data/industries/`, `data/companies/` content drops straight into seed rows via `vcc valuations import`.

---

## Material alignment items

Eight items where the schema and the v0.1 architecture spec have not yet met. Worth resolving before implementation begins.

### 1. Direction × magnitude — 5-way ordinal vs separate fields

The `ORDINAL_BAND` enum is `SEVERE_DOWN | MODERATE_DOWN | STABLE | MODERATE_UP | SEVERE_UP | BEYOND_SCALE` — a single six-state field. Our `architecture.md` §10.2 (worked through with the platform-side review) explicitly separates `direction` (three-way: `negative | neutral | positive`) and `magnitude` (three-way: `small | moderate | large`) as two distinct fields, giving seven distinct non-trivial movements.

That separation was a deliberate analytical choice — collapsing them back into a single five-state enum loses the leverage we built (e.g. a `positive / large` movement is structurally different from an `unspecified / large` movement, and analysts can carry different evidence for each).

Either the schema needs to carry both fields on the `Knowledge.fact` (probably as two `object_data_key_value_id`s, or one band plus one attribute), or we need to revisit our §10.2 decision. Our recommendation is the schema carries both — the analytical discipline is real.

### 2. `{min, mid, max}` ranges for assumption values

Our `architecture.md` §11.5 assumption-set schema is range-by-default — every assumption cell carries three numbers (low / central / high), per §16.1 confidence-band convention and the platform-side review point that collapsing to a single number throws away the framework's carried uncertainty.

The schema's `object_number` is a single scalar. Workable as three facts per cell, or as `min`/`max` attributes on the central fact, but the design choice needs making explicit so the dispatcher and the dashboard renderer agree on the shape.

### 3. `not_applicable` distinct from `neutral`

Our `architecture.md` §10.2 introduces this distinction explicitly. `not_applicable: true` (driver doesn't apply to archetype — e.g. NIM under industrial explosives) is different from `neutral` (driver applies but the scenario doesn't move it). Absence of a fact row implies "neutral / not explicitly assessed", per the §10.2 sparse-representation convention.

The `ORDINAL_BAND` enum has no `NOT_APPLICABLE` value. A convention is needed: extend the enum, use a separate flag column on the fact, or carry it via attribute.

### 4. Scenario regime tags alongside macro time series

Our `architecture.md` §6.4 supports two encodings for macro variables — quantified time series (when meaningful) **and** qualitative regime tags (e.g. `inflation_regime: anchored | un-anchored`).

The §2.1 mapping addresses the quantified case via `Data.time_series` but does not explicitly cover regime tags. The regime-tag case probably lands via `Instruments.detail` on the scenario or via a workspace-scoped `Reference` row, but it should be stated. Otherwise regime-encoded variables fall through the gap.

### 5. Nested structures in archetype EAV

Our `architecture.md` §7.4 archetype schema contains genuinely nested objects. `disruption_vectors[]` is a list of `{vector, nature, incumbency_position, time_horizon, severity, certainty, description}`; `scenario_sensitivity` has roughly seven sub-categories each with 2–4 fields.

The archetype examples in §2.2 show only scalar typed-EAV attributes. The nested structures can land via JSONB-in-attribute or via "child" `data_key_values` rows, but the design pattern for nested archetype content needs nailing down. Worth a worked example.

### 6. Per-segment positioning richness

Our `architecture.md` §8.2 positions per-segment blocks (`moat`, `franchise_assets`, `competitive_position`, `innovation_position`, `scenario_sensitivity_overrides`) **inside each segment**, not at the company level.

The DNL example in §2.3 only shows `revenue_share / ebit_share / functional_currency / archetype` per segment. The richer per-segment content is workable in the proposed model — additional `Reference.data_key_value_attributes` rows under each segment value — but the same stress-test applies as item 5: we should see one segment richly populated.

### 7. Confidence — enum vs numeric

Our `architecture.md` uses `low | moderate | high` (three-point ordinal, pinned meaning per §10.2 — "joint confidence in the direction × magnitude assignment, assuming the scenario plays out").

The schema uses a `numeric` confidence field (presumably 0.0–1.0). Either is fine, but the translation convention should be agreed and documented (for instance: low = 0.33, moderate = 0.67, high = 0.95; or analyst-set numeric with bucketed display).

### 8. Five Forces sub-determinant detail

Our `design/frameworks/five_forces_questions.md` (just completed; Porter-2008-aligned) has nine sub-determinants for Buyer Power alone, each with paired industry / company answers plus rationale plus evidence. Supplier Power has seven, New Entrants eight, Substitutes four, Rivalry nine.

The schema stores each force as a single rating value (with rationale presumably going to `Instruments.detail.description` or a free-text attribute). The sub-determinant-level detail either needs its own structure in the schema or lives only in the §16.1 narrative artefact (`data/industries/<archetype>.md`).

Worth deciding explicitly: is sub-determinant-level data "in the schema" (queryable, validatable) or "in the narrative" (prose-only)? Both are workable; the choice affects what the dispatcher can do programmatically.

---

## Smaller items

Five items that are easier to resolve but worth flagging.

9. **`workspace.description` must be `TEXT`**, not `VARCHAR(N)`. The scenario narrative deliverable per `architecture.md` §16.1 is potentially several pages of prose.
10. **Time-profile library and consistency checks as `Products.model` steps.** Our `architecture.md` §11.3 (seven named time profiles — `impulse`, `regime_shift`, `step`, `cyclical`, `front_loaded`, `back_loaded`, `linear_through_horizon`) and §11.4 (consistency checks — operating-leverage directional, terminal-state convergence, mix-shift, terminal-share reasonableness) are not explicitly mapped but presumably live as `Products.model` steps alongside translation rules. Worth confirming.
11. **Corporate-action overlay via `Instruments.schedule`.** §2.10 hand-waves this ("Already covered"). Our `architecture.md` §8.4 corporate-action overlay has explicit structure (`id`, `kind`, `effective_year`, `scenario_id`, `affected_segments`, `post_event_weights`, `rationale`, `evidence_refs`). Validate it fits `Instruments.schedule` cleanly; if not, the difference matters because the overlay merges our older multi-segment-time-evolution and M&A-overlay design problems into one mechanism.
12. **Layer 8 (dashboard) JSON contract is not addressed.** Presumably the §4 `"Valuations"` views are the contract surface. If so, the views should be locked before the dashboard tab is built so the contract is stable across implementation.
13. **Scenario versioning approach.** The design proposes forking via `parent_workspace_id` (a new workspace per scenario version). Our `architecture.md` §6.5 uses a `version` field on the scenario plus an explicit refresh-cadence mechanism (§6.7 review item 5; §10.7 review item 8). Both are valid; they are different. Workspace-forks-as-versions vs version-as-attribute. Worth deciding which is authoritative for our context.

---

## Open questions

14. **The "white paper" referenced.** §1 mentions *"the white paper's vision of consistency, auditability, peer comparison, scale"* and §10 references *"the white paper's relative-valuation, peer-comparison, and method-triangulation visions"*. Is there a separate document we should be reading alongside? Several concepts (relative valuation, peer comparison, method triangulation) are not yet explicit in our v0.1 spec, and they may belong if there is a broader vision document our architecture should be consistent with. Please share if so.
15. **"Stephen Reid" references.** The author refers throughout to "Stephen Reid". Our GitHub repo is `stephenreid90/VCC`. Worth understanding whether Stephen is a third party on the platform side, or whether this is a naming question worth clarifying.

---

## Suggestion for the next pass

The single most useful thing the next revision could include is **one richly populated archetype as a worked example** — `industrial_explosives.yaml` rendered in full (all five forces with rationales, lifecycle plus rationale, full `cost_structure`, full `scenario_sensitivity`, `disruption_vectors` as a list of structured records, `regulatory_regime`, `cyclicality`, `input_dependencies`) showing exactly how each piece lands in `Instruments.name` / `Instruments.detail` / nested attributes.

That single example would resolve items 5, 6, and 8 simultaneously, and surface any remaining gaps before they become implementation rework.

---

## Process note

The architecture spec is currently at v0.1 (frozen 7 May 2026, tagged `architecture-v0.1`). If any of items 1–8 result in changes to the spec, we would treat that as a v0.2 bump per the schema-versioning convention in §16 item 4, with a migration note recording what changed and why.

End of response.
