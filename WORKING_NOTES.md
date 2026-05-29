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

- Architecture spec **v0.1 frozen** (`design/architecture.md`), tagged in git as `architecture-v0.1`. Sections 1–17 reviewed and updated. Ben's-bot platform-side review (5 May 2026) absorbed; Group 1 changes committed. Plus a new §9.7 review item (#9) added 16 May 2026 capturing the terminal-growth-from-demographic-trajectory principle.
- Build plan wall chart at `design/build_plan.html` (currently v3).
- Response document to Ben's `vcc_valuations` rev1 design committed at `design/reviews/vcc_valuations_rev1_response_2026-05-16.md`.
- **Step 1** (close out design hardening): **done.** Editorial sweep applied; v0.1 freeze and git tag in place.
- **Step 2** (Draft analytical methodology): **done.**
  - `design/frameworks/five_forces_questions.md` — all five forces, Porter-2008-aligned.
  - `design/frameworks/payor_and_regulator.md` — v1 draft. Two-axis (regulatory + payor) framework.
- **Step 3** (Scenarios workshop): **done.** Six scenarios selected via interactive workshop (16 May 2026): Muddle Through (interior, most-likely), Orderly Convergence (upside boundary), Stagflation Persists (macro-downside boundary), Fragmentation and Resource Nationalism (geopolitical boundary), Disorderly Climate Crystallisation (climate boundary), AI Productivity Lag (technology boundary). All six scenarios drafted into `data/scenarios/<id>.yaml` (structured per §6.4) and `data/scenarios/<id>.md` (narrative per §16.1). Workshop output at `design/scenarios_workshop.md` includes institutional comparison (IMF / OECD / World Bank / IEA / NGFS mapping).
- **Step 4** (Formalise data schemas): **done.** pydantic v2 models for all eight layer schemas live under `src/vcc_valuations/schemas/` (scenario, industry, company + corporate-action overlay, driver, linkage, assumption, frameworks, plus common enums). JSON Schema exports generated under `design/schemas/`. Round-trip tests under `tests/schemas/` validate each scenario YAML against the model — all six pass; 22/22 tests pass overall.
- **Step 5** (Populate first archetype — DNL, formerly IPL): **substantively done.** Five phases completed.
- **IPL → DNL rename (22 May 2026):** Ben's data dump revealed the company was renamed from Incitec Pivot Limited (IPL) to **Dyno Nobel Limited (DNL.AU)** in March 2025 following the demerger of the fertilisers business. ISIN AU0000390544. Two passes:
  - **First pass (commit `f21fb1e`):** Renamed company / financial / analyses files (`data/companies/dnl.{yaml,md}`, `data/financials/dnl.yaml`, `analyses/dnl/`), bulk-replaced IPL → DNL in those files' prose, replaced indicative financials with real EODHD-sourced data (FY2025 + TTM Mar 2026), refined functional-currency treatment to per-entity (parent AUD, US subsidiary USD per IAS 21 / AASB 121).
  - **Editorial sweep (commit `_pending_`):** swept IPL → DNL across `design/architecture.md` (now v0.2.1), `design/build_plan.html`, `design/frameworks/five_forces_questions.md`, `design/scenarios_workshop.md` and `..._prep.md`, `design/reviews/vcc_valuations_rev1_response_2026-05-16.md`, `data/industries/industrial_explosives.{yaml,md}`, `data/impact_matrix/by_industry/industrial_explosives.yaml`, and the six `data/scenarios/*.md` files. The single remaining "IPL" reference is the legitimate "DNL, formerly IPL" historical pointer in architecture spec §2 item 4. YAMLs still validate against pydantic schemas. Architecture spec bumped v0.2 → v0.2.1 (editorial only; no schema or analytical content changes).
  - **Phase A:** industrial_explosives archetype YAML + narrative, validates against schema. Multi-tier competitive landscape (Tier 1: Orica + Dyno + MAXAM + EPC; Tier 2: Austin Powder + AECI + Solar Industries + Sasol/BME + Yara; Tier 3: country-specific).
  - **Phase B:** IPL company position YAML + narrative + indicative base-year financials. **USD functional currency** (Ben's-bot review point). Single segment post-demerger. Five franchise assets, archetype-specific positioning block, two company-level scenario sensitivity overrides (high operational carbon, moderate supply-chain concentration).
  - **Phase C:** industrial_explosives impact matrix across all six scenarios. 46 driver movements populated; sparse per §10.2; two defended-exception terminal-state entries per §10.6 rule 2.
  - **Phase D:** six per-scenario impact narratives + cross-scenario thesis. Each scenario sketch covers IPL-specific transmission channels and divergences from archetype baseline. Thesis identifies negative asymmetry: downside scenarios compress value more than upside lifts it.
  - **Phase E (valuations):** deferred to Phase 3.5 smoke-test DCF (Step 7).
- **Phase 3.5 smoke-test DCF (24 May 2026): done, including calibration pass.** First-pass end-to-end pipeline (commit `86233ca`) confirmed the framework works: comparative directional ranking matches the per-scenario narratives; framework discriminating power is real. First-pass calibration issues (baseline AUD 1.87/share vs market AUD 3.61; two scenarios negative-equity; four trip the >70% terminal-share validator) addressed by an incremental calibration pass: normalised EBIT margin (11.2% → 13.5%), steady-state net debt (AUD 1,810m → AUD 1,300m), rigorous component-build WACC (8.5% round-number → 8.82% from Rf 4.30% + β 1.15 × ERP 5.00% with market-value weights). Calibrated Muddle Through baseline AUD 2.53/share (30% below market, down from 50% below); negative-equity outcomes disappeared; terminal-share validator still fires on 3 of 6 (structural; needs §11.4.2 rule 5 fade period in Step 7). Calibration captured in `data/financials/dnl.yaml` `normalised_baseline` block and `docs/phase_3_5_findings.md` Calibration-pass section. No architecture spec changes required.
- **Next: Step 6** — production translator informed by Phase 3.5 findings (calibrated baseline, §11.3 time profiles, §11.4.2 consistency rules), then either re-run smoke test or proceed straight to **Step 9** (populate CSL + WBC) once the engine is solid.

---

## Conversationally-decided things worth holding in working memory

- IPL is post-demerger single-segment industrial explosives. Working assumption pending Ben's data workstream confirmation when populating `data/companies/ipl.yaml`.
- UI is **embedded in the existing VCC dashboard** (not standalone FastAPI + Vue). Locked Decision §2.1 was re-decided after Ben's-bot review.
- Industry archetype location **parked** — stays in `vcc-valuations` for now; may relocate to a platform-level repo when other archetype consumers (NAB / ANZ / CBA VCCs) materialise.
- Time budget for step 5 (populate IPL): provisional **3-week** working anchor pre-narrative-deliverables; bumped to roughly **4 weeks** (320–800 chat-min) once narrative deliverables were added in v3 of the build plan.
- Complementary-framework approach: **defined enum** (`payor_and_regulator | network_effect | resource_lifecycle | none`) chosen but **open-to-revisit** after first non-Porter archetype (banking / WBC) is populated.
- Probability-weighting of scenarios: **comparative output is canonical**; mode (a) blended expected value is *not* supported under §6.2 boundary-cases commitment. Optional per-scenario probability supported only for analyst-side indicative blends. Scenarios workshop chose not to populate the probability field in YAMLs at this stage.
- Narrative deliverables: six per company (scenario, industry view, company positioning, scenario impact, valuation note, thesis) — see §16.1.
- **Workshop refinement on §6.2 framing:** scenarios are boundary cases except for the most-likely interior (Muddle Through). The set spans the plausible range; it doesn't aim for exhaustive coverage. (§6.2 with workshop refinement.)
- **US powerhouse as cross-cutting assumption.** Tara's view — the US economy is structurally stronger than consensus credits. Handled implicitly in each scenario's narrative rather than as a structured regime tag.
- **Climate posture and demographic response also cross-cutting**, addressed in each scenario's narrative, not as structured regime tags. Tara's preference.
- **Terminal-growth-from-demographic-trajectory.** Scenario × company × geography-conditional. Even when the 2040s skilled-migration cliff sits beyond the explicit forecast horizon, terminal growth must reflect the demographic-adaptation trajectory. Captured as §9.7 review item 9 in architecture spec (added 16 May 2026).
- **AI Productivity Lag insight (workshop):** AI doesn't need to deliver economy-wide TFP gains to be useful for labour substitution. Rents capture asymmetric — platform owners win; labour-cost containment in white-collar work is the working channel. China's bipedal-robotics is uniquely advantaged in physical-substitution domains.
- **Gas-contract roll-off overlay added (29 May 2026).** Tara flagged that the US gas-contract roll-off (2028-2030 window) was narrative-only and the margin glide path actually moved the wrong way (transformation drove margins up through FY31 — exactly when the gas-cost advantage erodes). Resolution: added a structural-headwind overlay to the margin glide of -50/-100/-150bps cumulative in Y3/Y4/Y5, partially offsetting the transformation tailwind. Methodology §3.2.1 captures the concept (sister to transformation overlay). Applied flat across scenarios for this iteration — future refinement could make scenario-conditional (bigger drag under high-gas scenarios like Stagflation/Disorderly Climate). Headline DNL per-share moves: MT AUD 3.22 → AUD 2.90 (vs market AUD 3.61, -20%); Orderly AUD 3.72 → AUD 3.36 (-7%); Stagflation AUD 1.12 → AUD 0.82; all scenarios drop AUD 0.31-0.36/share. Workbooks v3 in analyses/dnl/valuations/. Aligns with substack discipline of building structural risk into cash flows, not hand-waving to terminal state or adjusting WACC.
- **Reference texts and style anchors (28 May 2026).** Tara's go-to references: (a) Damodaran (Stern website, blog, books — particularly Investment Valuation, Narrative and Numbers, and the 2005 "Value of Control" paper); (b) Mercer's Business Valuation: An Integrated Theory, 3rd Edition (Mercer + Harms, 2021); (c) Clifford Ang's Applied Valuation; (d) Valuation Matters substack at valuationmatters1.substack.com (co-authored Stephen Reid + Tony Carlton). Style of thinking absorbed from KISS principle + control-premium-fallacy posts: (i) build risk and economic content into the cash flows, not into ad-hoc premia or discounts; (ii) "standard" adjustments applied rotely are suspect — case-specific mechanism is required; (iii) KISS / market efficiency / historical premia get arbitraged away; (iv) distinguish measurable from abstract (e.g. takeover premium != control premium); (v) double-counting check is the recurring red flag. The single-WACC discipline (methodology §3.5) is a direct application of (i) and (v).
- **Single-WACC discipline across scenarios (28 May 2026).** Resolution of the parked §9.7 review item 4 ("WACC scenario behaviour"). WACC is set at the valuation date and held constant across all scenarios. Rationale: each scenario already prices its risk through the cash-flow path; using a higher discount rate in a stress scenario double-counts risk. The marginal investor's required return is set by today's market conditions; it does not change conditional on which future state realises. Scenario rate-driver deltas (Rf, ERP, country risk) are retained in the impact matrix for narrative context but do NOT flow into the DCF discount rate. Terminal growth REMAINS scenario-conditional (it represents a structural economic state, not risk re-pricing). User override of WACC for sensitivity is exposed in the workbook. Captured in methodology §3.5 and architecture spec v0.3.1. Cross-scenario range compressed ~30% under single-WACC vs the earlier differential-WACC approach; asymmetry persists in cash flows alone (downside compression > upside lift). Tara's view: "feels like changing the WACC is double counting risk."
- **Equity-bridge and valuation-mechanics methodology (25 May 2026).** Following a deep methodology exchange with Tara on the DNL Muddle Through workbook, the following are now baked into the framework via `design/methodology/equity_bridge_and_valuation_mechanics.md` and architecture spec v0.3: (1) revenue growth derived from scenario macro → industry archetype → company position chain (not hardcoded scalar); (2) margin glide path as a structured company-position field; (3) narrow net-debt definition + structured equity-bridge adjustments with on-balance-sheet flag and provided-for-at-anchor tracking; (4) restructuring-cost consistency rule (assume benefit → must assume execution cost); (5) latest reported share count paired to net-debt anchor date (no buyback projection); (6) IMI handling via parallel statutory + ex-IMIs DCFs with per-item context and default-lean taxonomy, user picks central case; (7) explicit valuation date with Period A walk-forward (anchor → valuation), Period B stub line in the DCF (Option X), mid-period discounting from valuation date onward; (8) per-field as_at_date discipline on items where timing matters; (9) governance assessment parked (Tara dislikes ad-hoc alpha-style premia — refer her substack `valuationmatters1.substack.com`). Step 6 production translator + Step 7 production DCF must implement all of this. The DNL Muddle Through workbook serves as the canonical worked example.
- **Valuation inputs as transparent components, not opaque baselines (24 May 2026).** Following the Phase 3.5 smoke-test calibration pass, valuation inputs that an analyst would reasonably want to challenge or override are exposed as named, overridable component fields rather than as hidden parameters. WACC in particular is now built up component-by-component (Rf, ERP, β, Rd_pretax, tax, market-value weights) via a `WaccBuild` dataclass; the rationale for each component lives next to it in the financials YAML (`normalised_baseline.wacc_build`). This principle carries forward to the Step 7 production DCF engine and is captured in `docs/phase_3_5_findings.md` (Calibration pass section, Design principle adopted).
- **Disorderly Climate Crystallisation framing:** scenario is about the *crystallisation event*, not about whether climate transition becomes disorderly (it already is, per Tara's workshop point about money-supply / inflation / cost-of-living pressure crushing climate-policy coordination).

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

## Decisions still parked / open

- **Methodology §3.5 citations to add.** When next editing the methodology doc, add explicit citations to Damodaran's "Value of Control" framework and Stephen's substack reasoning on building risk into cash flows rather than into premia. Strengthens the §3.5 single-WACC argument by anchoring it in published work rather than pure finance-theory framing.
 (cross-link to architecture review items)

- **Industry archetype location** (`vcc-valuations` vs platform-level repo) — revisit when other consumers appear. (§5.1 item 8.)
- **Complementary-framework discipline** (defined enum vs hybrid) — revisit after WBC populated. (§7.7 item 9.)
- **Step 5 time budget** — revisit after IPL populated against actuals. (§14.3 item 1.)
- **Stochastic overlay** — deferred per §3 Open Decision.
- **Probability-weighting (narrowed scope)** — whether engine surfaces an analyst-computed blended scalar as a presented output. (§3 item 3.)
- **WACC scenario behaviour** — whether components actively move per scenario. Layer 4 keeps the option open; decision deferred to §12 (DCF Engine).
- **`risk_exposures.fx` placement** — parent / segment / both. (§8.6 item 4.)

---

## Recent commits (reference)

- `b387f1a` — initial architecture spec push (sections 1-17 first cut).
- `8df0784` — sections 7-11 worked through with Tara.
- `0b976eb` — Ben's-bot platform-side review absorbed (Group 1 changes).
- `f62d3ae` — narrative-deliverables convention added; Five Forces question bank started.
- `9f91be4` — WORKING_NOTES.md created.
- `ac4e8e7` — Five Forces question bank completed (Supplier, New Entrants, Substitutes, Rivalry).
- `4616ede` — payor-and-regulator framework v1 draft added.
- `ec462c5` — editorial sweep + v0.1 freeze (Step 1 closed out).
- `8e7a51b` — WORKING_NOTES update after Step 1 and Step 2 closed.
- `a76a9ec` — scenarios workshop prep document.
- `8cc2527` — response to Ben's `vcc_valuations` rev1 design.
- `1d3d53b` — Step 3 complete (six scenarios drafted).
- `35578ea` — Step 4 (pydantic + JSON Schema + tests).
- `e142f95` — chore: removed accidentally-committed `__pycache__` files.
- `f682363` — WORKING_NOTES Step 4 update.
- `dfd1243` — architecture v0.2 (§7.1.1 archetype-granularity principle).
- Step 5: Phase A `_` (industrial_explosives archetype), Phase B `_` (IPL position + indicative financials), Phase C `dea44c2` (IPL impact matrix), Phase D `_` (IPL per-scenario narratives + thesis). Hash placeholders updated when latest commits drop.
- `f21fb1e` — IPL → DNL first pass (renames + real EODHD financials + per-entity functional currency).
- `5d55305` — IPL → DNL editorial sweep across spec/build-plan/workshop docs/industry/matrix/scenarios (architecture v0.2 → v0.2.1).
- `86233ca` — Phase 3.5 smoke-test DCF (translator stub + FCF DCF stub + driver script + findings).
- **PENDING COMMIT — briefing pack for Ben meeting (29 May 2026).** `analyses/dnl/dnl_briefing_pack_2026-05-29.docx` + `.pdf`. 6 substantive pages + small overflow covering scenarios / Porter / DNL positioning / per-scenario impact / methodology principles. To be committed in the next push.
- **Tag:** `architecture-v0.1` points at `ec462c5`.

---

## Last updated

29 May 2026 (later) — Gas-contract roll-off overlay added to margin glide path (methodology §3.2.1). DNL workbooks rebuilt as v3: Muddle Through per share AUD 3.22 → AUD 2.90; all scenarios down ~AUD 0.31-0.36. Aligns with substack 'build structural risk into cash flows' discipline.

29 May 2026 — Reference texts and style anchors captured (Damodaran, Mercer, Ang, Valuation Matters substack). Style of thinking distilled from KISS principle + control-premium-fallacy posts. Methodology §3.5 citation follow-up parked. Briefing pack for Ben meeting drafted at `analyses/dnl/dnl_briefing_pack_2026-05-29.{docx,pdf}` (committed alongside this update).

28 May 2026 — Single-WACC discipline added (methodology §3.5; architecture spec v0.3.1). DNL scenario comparison rebuilt with constant WACC; comparison vs prior differential-WACC version captured in workbook. All six scenarios for DNL computed: Orderly Convergence AUD 3.72, Muddle Through AUD 3.22, AI Productivity Lag AUD 3.14, Fragmentation AUD 2.36, Disorderly Climate AUD 1.35, Stagflation AUD 1.12. Asymmetry persists (downside compression > upside lift) even without WACC differentials.

25 May 2026 — Equity-bridge and valuation-mechanics methodology added (`design/methodology/equity_bridge_and_valuation_mechanics.md`); architecture spec bumped to v0.3. Substantive methodology decisions captured: scenario → industry → company growth chain replaces opaque baseline; structured equity bridge with anchor-date discipline; restructuring consistency rule; latest-reported share count paired to net debt; statutory + ex-IMIs parallel DCFs; Period A walk-forward + Period B stub + mid-period discounting. DNL Muddle Through workbook rebuilt as the canonical worked example. Ready for Step 6 production translator implementation against the explicit methodology.

Previous updates:
- 22 May 2026 — Step 5 closed out + IPL → DNL rename + editorial sweep.
- 17 May 2026 — Step 4 (Formalise data schemas) closed out. All eight layer schemas as pydantic v2 models; JSON Schema exports; tests pass on all six scenario YAMLs (22/22). Ready for Step 5 (Populate first archetype — IPL).
- 16 May 2026 (later) — Step 3 closed.
- 16 May 2026 (earlier) — Step 1 and Step 2 closed.
- 7 May 2026 — initial creation as hedge against chat context-length limits.

Update this file whenever a conversational decision is made that doesn't belong in the architecture spec. Concision matters — this needs to remain skim-readable.
