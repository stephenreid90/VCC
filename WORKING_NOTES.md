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

## Current state of play (as of 12 June 2026)

**16 June 2026 (afternoon) — Peer-triangulation principle promoted to general methodology (§3.5.3).**

Following Tara's question on whether the principle should be addressed in the overall methodology, peer-triangulation is now a general discipline at **§3.5.3**, applying to both industrials and banks. The bank-specific statement at §15.2(c) was slimmed to a pointer; §15.2(b) now references §3.5.3 for the procedure. Existing §3.5.3 (User override) and successors renumbered to §3.5.4 / §3.5.5 / §3.5.6. Schema implications updated: company YAMLs MUST carry a `beta_selection_rationale` block per §3.5.3.

DNL's measured β = 0.95 (sourced from world-index AUD-MSCI) was applied without peer triangulation against Orica / MAXAM / Austin Powder. To be back-applied on the next DNL refresh — Australian-listed peer set is thin (Orica is the only ASX-listed direct peer; world-listed peer set adds Yara, ICL, Sasol-explosives flank).

Architecture spec v0.5 migration note (c) records the §3.5.3 addition and the renumbering.

---

**16 June 2026 — Beta-selection principle landed; peer EODHD feeds for CBA / NAB / ANZ / MQG ingested.**

Tara articulated a key methodological principle: measured β carries material statistical noise and should not be used mechanically. The framework should select β via reasoned peer triangulation, in the same spirit as a Five Forces decomposition — catalogue peers, identify outliers, reason about where the subject company should sit relative to peers given franchise mix, then select. The principle is general (applies to industrials at §3.5.2 too) but landed first in methodology **§15.2(c)** as part of the bank-specific cost-of-equity discipline. Both the measured and selected β are documented for transparency.

Peer feeds applied for WBC:

1. Peer beta dataset: CBA 0.80, NAB 0.72, ANZ 0.57, MQG 0.88, WBC 0.73.
2. ANZ excluded as outlier (institutional / international revenue dilution; Suncorp integration period). MQG excluded as informative-not-comparable (different archetype).
3. Comparable cluster CBA / NAB / WBC: β 0.72-0.80, midpoint 0.75.
4. **β_selected for WBC = 0.75** (cluster midpoint); measured 0.73 documented alongside. Re = 4.30% + 0.75 × 5.00% = **8.05%** (vs 7.95% under mechanical use of measured β).
5. Peer ROE / P/B / forward PE rankings validate franchise hierarchy: CBA > MQG > NAB ≈ WBC > ANZ on ROE; market valuation multiples track this exactly.

Archetype `cost_of_equity_anchor` revised to: measured peer range 0.57-0.88; comparable cluster range 0.72-0.80; anchor selected β 0.75; Re anchor 8.05%. The initial 0.85-1.00 range based on global-diversified-financials default was too high — Australian Big Four oligopoly produces meaningfully lower systematic risk than the global default.

NIM time series: Tara accepted YE basis (5 data points: FY21-FY25) over half-yearly (9 data points). Deferred to next pass — requires AIEA history not in the EODHD feed.

---

**15 June 2026 — Ben's WBC financial feed arrived; key calibrations applied.**

Ben's EODHD fundamentals export landed (`data/financials/wbc_eodhd_fundamentals_2026-06-15.csv`). Material calibrations applied to WBC YAMLs and bank archetype:

1. **Equity beta 0.73** — below initial archetype range 0.85-1.00. Cost of equity revised to Re = 4.30% + 0.73 × 5.00% = **7.95%** (vs initial archetype mid-point ~8.93%). 100bps reduction; meaningful upward pressure on Muddle Through fair value. Archetype `cost_of_equity_anchor` beta_range extended to 0.73-1.00 to accommodate.
2. **Shares outstanding 3,414.9m** verified (was 3,380m placeholder).
3. **Market reference price AUD 35.32** at feed date 15 June 2026 (was AUD 38.50 placeholder). Sell-side consensus 12-month target AUD 33.45 (~5% below current trading).
4. **Multi-year net income history** added to `bank_specifics.historical_anchors`: peak FY18 AUD 8.09bn; trough FY20 (COVID) AUD 2.29bn; FY25 AUD 6.91bn; through-cycle 5-yr average AUD 6.45bn.
5. **FY26 / FY27 consensus** captured: FY26 EPS AUD 2.06 / FY27 EPS AUD 2.18 — usable as Muddle Through market check.
6. **Book value per share AUD 21.31** (book equity ~AUD 72.8bn).

Outstanding feed requests: peer comp (CBA/NAB/ANZ + Macquarie banking on same metrics) and NIM time series at half-yearly cadence — for next pass.

---

**12 June 2026 — Westpac build kicked off; bank-methodology fork landed first.**

Ben sent the WBC source pack (11 files: 1H26 financial results announcement, 1H26 IDP presentation, 1H26 key financial information xlsx, 1H26 quantitative information xlsx (Pillar 3), 1H26 risk factors, items-impacting-1H26 PDF, 1Q26 Update + IDP, December and March Pillar 3 reports, FY25 annual report). Ben's financial feed (multi-year time series, beta, peer comp) still to come — not blocking.

Before starting the WBC company build, added **methodology §15 "Bank-specific valuation conventions"** as a fork. Industrials methodology (§§2–7) unchanged; banks invoke §15 in place of §§2–4. Key conventions: cost of equity not WACC (no EV→equity bridge); NII = average interest-earning assets × NIM; credit losses are a scenario-conditional primary driver, not a residual; CET1 ratio binds dividend payout and asset growth; ROE fade to Ke for terminal. Schema additions: `bank_specifics.*` on company YAMLs, `bank_archetype.*` on industry YAMLs, `macro_baseline.credit_cycle / cash_rate_path / swap_spreads / housing_market / regulatory` on scenario YAMLs. Architecture spec bumped v0.4 → v0.5 (additive only).

WBC v1 baseline committed 12 June 2026 (commit d568262): `data/industries/australian_major_banks.{yaml,md}`, `data/companies/wbc.{yaml,md}`, `data/companies/wbc_documents.yaml`. Calibrated against 1H26 results (anchor date 31 March 2026): CET1 12.42%, NIM 1.89%, AIEA AUD 1,035bn, gross loans AUD 890bn, customer deposits AUD 745bn.

Next: per-scenario impact matrix `data/impact_matrix/by_industry/australian_major_banks.yaml`, then Muddle Through valuation workbook applying §15 conventions.

---

## Previous state of play (as of 16 May 2026)

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
- **DNL Q1-Q8 review + Five Forces spine + tax-rate consistency (9 June 2026).** Substantive day of methodology refinement. (a) Q1-Q8 review fixes: base EBIT corrected to AUD 480m (corporate already in segment guidance per slides 27-28); margin glide reconciled to FY27 exit run rate; OCF run rate AUD 500m (was AUD 290m, depressed by H1 TWC unwind); full Fertilisers separation map per slide 29 added to equity bridge (IPF Distribution +AUD 125m face, Geelong remediation -AUD 35m, Gibson Island -AUD 97m, transaction costs -AUD 11m, PH contingent +AUD 100m face); Period A buyback adjustment removed (value-neutral). (b) WACC discipline: Hamada formula confirmed; world-index basis for beta (DNL beta 0.95 vs 1.15 ASX200); RFR convention is 10Y on-the-run CGS YTM. (c) Tax discipline (methodology section 3.6 new): effective rate (FY26 22.5%) glides linearly to blended statutory (27.5%, computed from jurisdictional weights x statutory rates) over the explicit horizon. Single rate consistency principle: same blended statutory used for terminal operating tax, WACC debt-tax-shield, and Hamada re-levering. (d) Five Forces spine for Step 3 company position (methodology section 3.3 new): per-force traversal (buyer, supplier, new entrants, substitutes, rivalry) with industry rating vs company-relative + mechanism + quantified delta + where_captured. Replaces earlier catch-all 'company offset.' DNL net: -25bps (rivalry/competitive position -30, rivalry/product-mix -10, new entrants/DNEL pipeline +15). (e) Source-document ingestion discipline (methodology section 14 new): standing checklist (investor pres, half-year results, statutory accounts, continuous disclosure, transcripts, sustainability); per-company documents register; refresh cadence; handoff spec for Ben's data workstream. Headline: Muddle Through per share AUD 2.90 (v3) -> AUD 3.59 (v4 with full discipline), essentially at market AUD 3.61. Framework discriminating power now in scenario asymmetry, not in disagreement with consensus on central case. Architecture spec bumped v0.3.1 -> v0.4 (additive only).
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

- **Methodology §3.5 citations to add.** When next editing the methodology doc, add explicit citations to Damodaran's "Value of Control" fra