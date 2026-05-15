# VCC Valuations — Working Notes

A living scratchpad for conversational decisions, current preoccupations, and context that doesn't naturally belong in the architecture spec. **Maintained by Tara + Claude as a bootstrap document for new chat sessions.**

---

## Bootstrap (read in this order)

1. This file.
2. `design/architecture.md` — the architecture spec (sections 1–17).
3. `design/build_plan.html` — the 12-step build plan and where we're up to.
4. Optional: `design/frameworks/` for methodology drafts in flight.

---

## Who and what

- **Owner:** Tara Reid (tara@reidadvisory.net), Reid Advisory.
- **Collaborator:** Ben — runs the parallel data-sourcing workstream. "Ben's bot" is Ben's working assistant; produced the platform-side review on 5 May 2026.
- **Project:** Scenario-based equity valuation module for listed equities.
- **Repo:** https://github.com/stephenreid90/VCC (account `stephenreid90`). Local at `C:\Users\steph\vcc-valuations`.
- **Test companies:** Incitec Pivot Limited (IPL — single-segment industrial explosives, post-demerger), CSL Limited, Westpac Banking Corporation (WBC).
- **Strategist friend** has independently completed an IPL scenario valuation; that's the calibration benchmark for step 8.

---

## Working preferences (Tara)

- Number multi-point lists (2 or more items) so she can reply by number. Single-point responses don't need numbering.
- Plain prose; minimal headers and bullets except where structurally needed.
- No emojis.
- Tara is not a developer — explain technical concepts (YAML, git, PATs, etc.) when they come up rather than assume.
- For git: Tara opens a cmd window in `C:\Users\steph\vcc-valuations` and runs commands there.

---

## Current state of play (as of 16 May 2026)

- Architecture spec **v0.1 frozen** (`design/architecture.md`), tagged in git as `architecture-v0.1`. Sections 1–17 reviewed and updated. Ben's-bot platform-side review (5 May 2026) absorbed; Group 1 changes committed.
- Build plan wall chart at `design/build_plan.html` (currently v3).
- **Step 1** (close out design hardening): **done.** Editorial sweep applied (engine/... paths updated to src/vcc_valuations/...; `imported_input_share` renamed to `_static` / `_responsiveness` to disambiguate). v0.1 freeze and git tag in place.
- **Step 2** (Draft analytical methodology): **done.**
  - `design/frameworks/five_forces_questions.md` — all five forces, Porter-2008-aligned. Paired industry/company questions per sub-determinant; synthesis sections map to schema fields.
  - `design/frameworks/payor_and_regulator.md` — v1 draft. Two-axis (regulatory + payor) framework for archetypes Porter doesn't adequately describe. WBC will be the first archetype populated against it (Step 9).
- **Next: Step 3** — Scenarios workshop. Workshop itself happens away from chat; Claude's role is workshop prep (themes, structuring questions, "what makes a good scenario") and YAML drafting after the workshop.

---

## Conversationally-decided things worth holding in working memory

- IPL is post-demerger single-segment industrial explosives. Working assumption pending Ben's data workstream confirmation when populating `data/companies/ipl.yaml`.
- UI is **embedded in the existing VCC dashboard** (not standalone FastAPI + Vue). Locked Decision §2.1 was re-decided after Ben's-bot review.
- Industry archetype location **parked** — stays in `vcc-valuations` for now; may relocate to a platform-level repo when other archetype consumers (NAB / ANZ / CBA VCCs) materialise.
- Time budget for step 5 (populate IPL): provisional **3-week** working anchor pre-narrative-deliverables; bumped to roughly **4 weeks** (320–800 chat-min) once narrative deliverables were added in v3 of the build plan.
- Complementary-framework approach: **defined enum** (`payor_and_regulator | network_effect | resource_lifecycle | none`) chosen but **open-to-revisit** after first non-Porter archetype (banking / WBC) is populated.
- Probability-weighting of scenarios: **comparative output is canonical**; mode (a) blended expected value is *not* supported under §6.2 boundary-cases commitment. Optional per-scenario probability supported only for analyst-side indicative blends.
- Narrative deliverables: six per company (scenario, industry view, company positioning, scenario impact, valuation note, thesis) — see §16.1.

---

## External dependencies / things we're waiting on

- **Ben's data-sourcing workstream** — base-year financials per company; data feasibility confirmation per schema field; alignment on `financials.yaml` contract.
- **Scenarios workshop** (Tara to convene) — produces step 3 deliverables: 3–6 named scenarios in YAML + narrative form.
- **IPL strategist friend** — provides the calibration benchmark for step 8.
- **PAT permission** — Tara's GitHub fine-grained PAT is currently Contents: Read-only. Sandbox-side push returns 403; Tara pushes from her own cmd window. If she updates the PAT to Read-and-write, sandbox can push directly.

---

## Things we considered and rejected (don't relitigate)

- **Streamlit-only UI** — rejected for UX flexibility; subsequently re-decided to embed in VCC dashboard rather than build standalone Vue.
- **Disruption as a separate lifecycle stage** — rejected; disruption surfaces through Five Forces (entrants + substitutes).
- **Probability-weighted blended expected value as canonical output** — rejected per §6.2.
- **IPL as multi-segment** — was true pre-demerger; now single-segment.
- **Open-ended `complementary_framework` blocks** — rejected; chose defined enum for comparability discipline.
- **Confidence as a multi-axis field on impact-matrix entries** — kept as single ordinal with pinned meaning ("joint confidence in direction × magnitude assuming the scenario plays out").
- **Tax aggregation / capex→D&A / WACC computation as "consistency rules" in §11.4** — re-categorised as derivations (deterministic identities) per Ben's bot review; only operating-leverage and terminal-convergence remain as genuine consistency checks.

---

## Key conventions adopted (cross-cutting)

- All ratings use `low | moderate | high` (3-point) — *except* matrix entries: `direction` is 3-way (`negative | neutral | positive`) and `magnitude` is 3-way (`small | moderate | large`); the two are separate fields.
- Drivers are **nominal in functional currency**; FX appears at consolidation across functional currencies, not as a primary driver inside a segment DCF.
- Drivers carry `role: primary | derived`. Layer 5 only writes primary drivers; Layer 6 computes derived ones via declared `derivation_formula`.
- Narrative artefacts and structured artefacts are **paired**; structured fields win as source of truth where prose and structure disagree (per §16.1).
- File naming: `snake_case` for ids and filenames; `CamelCase` for Python classes.
- Schema versioning: every schema carries `version`; breaking changes bump major.
- Override discipline: target ≤20% of cells per company (archetype-tunable); above this, the archetype is mis-specified.

---

## Filesystem quirks worth knowing

- `C:\Users\steph\vcc-valuations` is mounted into Claude's sandbox. The mount permits file CREATE but not DELETE for `.git/*.lock` files. Workaround in sandbox: `mv .git/index.lock .git/index.lock.deadN` before retrying the git command. Tara can delete the lock files normally from her own cmd window: `del .git\HEAD.lock` and `del .git\index.lock`.
- A scratch-clone approach via `/tmp/` has been used in the sandbox for git operations when the mount approach is too painful.
- A `.github-token` file lives at the repo root and is excluded from git via `.git/info/exclude` (not `.gitignore`, which had unrelated modified state we don't want to touch).

---

## Decisions still parked / open (cross-link to architecture review items)

- **Industry archetype location** (`vcc-valuations` vs platform-level repo) — revisit when other consumers appear. (§5.1 item 8.)
- **Complementary-framework discipline** (defined enum vs hybrid) — revisit after WBC populated. (§7.7 item 9.)
- **Step 5 time budget** — revisit after IPL populated against actuals. (§14.3 item 1.)
- **Stochastic overlay** — deferred per §3 Open Decision.
- **Probability-weighting (narrowed scope)** — whether engine surfaces an analyst-computed blended scalar as a presented output. (§3 item 3.)
- **WACC scenario behaviour** — whether components actively move per scenario. Layer 4 keeps the option open; decision deferred to §12 (DCF Engine).
- **`risk_exposures.fx` placement** — parent / segment / both. (§8.6 item 4.)

---

## Recent commits (reference)

- `b387f1a` — initial architecture spec push (sections 1-17