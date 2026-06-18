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
- Australian English.
- **(17 June 2026) Workbook discipline**: all Excel spreadsheets must use formulas, not Python-computed hard-coded values. Inputs go on a dedicated Assumptions sheet in yellow-shaded cells with blue text; all other cells link to Assumptions via formulas. Goal: Tara can trace, audit, and flex the model.
- **(17 June 2026) Write-up discipline**: include an intuitive narrative description in every company write-up (thesis, discussion document, briefing pack) explaining *why* each scenario produces the per-share number it does. Each scenario gets: macro story → key channels driving the outcome → why the number is what it is. Plus a mental short-cut at the end. Format: a sub-section after the scenario-table introduction, flowing prose.


## Current state of play (as of 18 June 2026 — end of long session)

**Session handoff notes.** This session has covered methodology v0.6 consolidation, DNL v5 backport, WBC v3/v4 (workbook + discussion document + scenarios comparison + standing rules), and started CSL v1 (foundation + Muddle Through workbook). If continuing in a new chat, see the "Carrying into next chat" section at the bottom of this file.

### Where everything stands

**Methodology**: v0.6 stable. Six refinements lifted from review-question pattern (peer-gap closure framing, cost-of-closure consistency P&L-vs-bridge distinction, workbook construction discipline §11, assumption-strength tagging §14.5.1, market-vs-framework gap interpretive output §16, acronym sweep discipline §16.4). Architecture spec at v0.6 with full migration note.

**Standing rules now in force** (lines 32-33 in this file):
1. **Workbook discipline** — all Excel spreadsheets use formulas; inputs on Assumptions sheet in yellow-shaded cells with blue text; output cells link via formulas
2. **Write-up discipline** — intuitive narrative per scenario in every company write-up; macro story → key channels → why the number is what it is; plus mental short-cut

**DNL (industrial — first test company)**: v5 backport complete (commit `6d060e5`).
- v0.6 framing applied: "transformation overlay" → "peer-gap closure" in thesis.md and dnl.md
- β peer-triangulation discipline applied: peer set Orica (~1.05) / Yara (~1.20) / ICL (~1.10) / Sasol excluded (~1.45) / DNL measured 0.36 unreliable; β selected 1.10 (cluster midpoint)
- Workbook v5 with new "DCF Build-up (v5)" sheet showing explicit Step 2 → Step 3 decomposition (industry growth + company offset; base margin + peer-gap closure + gas roll-off)
- v4_5forces workbook preserved as audit trail
- **Outstanding**: discussion document refresh with peer-gap closure framing (cosmetic, only worth doing if Tara re-shares with Sunil); actual EODHD pulls for ORI/YAR/ICL when Ben has time

**WBC (bank — second test company)**: v3/v4 complete (commits `c47c420`, `cfbfdd6`, `939fba3`).
- All v0.6 standing rules applied
- Methodology §15 bank fork stable
- β peer-triangulation: 0.75 selected (CBA/NAB/WBC midpoint); ANZ excluded; MQG informative-not-comparable
- Discussion v3 includes intuitive narrative per scenario (the example for the standing rule)
- Workbook v4 is formula-based per standing rule (133 valid formula cells, zero errors)
- Headline: Muddle Through AUD 30.03 vs market AUD 35.32 (−15%); Orderly AUD 35.84 essentially at market (market is implicitly pricing closer to upside)
- Asymmetry ratio 1.83× (materially less than DNL's 4.05× — bank capital-constraint payout flex + oligopolistic structure cap both sides)
- **Outstanding**: nothing critical

**CSL (industrial — third test company, IN PROGRESS)**: foundation + workbook v1 done (commits `f1f3652`, `4fa068b`).
- Documents register, 3 industry archetypes (plasma_derived_therapies, vaccines, specialty_pharmaceuticals), CSL company position YAML with 3 segments + Five Forces all built
- Workbook v1 formula-based per standing rule, segment-level forecasts (Behring + Seqirus + Vifor + corporate) aggregating to consolidated NPATA → FCFF → per share
- USD throughout; AUD translation only at per-share output line
- β selected 0.85 (peer triangulation: Grifols / Takeda / Sanofi 0.7-0.9 range); measured 0.094 from EODHD unreliable per §3.5.3
- Peer-gap closure overlay: USD 525m annual savings target by FY27; +250bps Behring margin uplift / +100bps each Seqirus, Vifor by FY31
- §4.4(b) restructuring cost USD 507m PV deducted in equity bridge
- FY25 NPATA reconciliation: computed USD 3,130m vs disclosed USD 3,219m (3% gap — sound)
- **Headline result**: Muddle Through per share USD 164.97 = AUD 249.96 vs market AUD 105.53 = **+137% premium**
- **This needs review.** Market currently 61% below 52-week high AUD 269. Framework Muddle Through implies the market reset is overdone — but the gap is striking. Per v0.6 §16, market is implicitly pricing a scenario closer to a stress case than to status quo. Sanity-checks worth running:
  1. Beta — 0.85 may be too low given CSL's 60% drawdown; β = 1.0 → Re = 9.5% → ~USD 145 / AUD 220 still well above market
  2. Peer-gap closure aggressiveness — +250bps Behring may need a more cautious Muddle Through (closer to +150bps?) with full +250bps in Orderly Convergence
  3. Beyond v1: assess whether market is pricing a "Stagflation / Disorderly Policy" scenario more like AUD 80-110
- **Outstanding for CSL v2+**: per-scenario impact matrix; scenarios comparison; thesis (with intuitive narrative per scenario per standing rule); discussion document; **decision on whether to re-anchor v2 with more cautious peer-gap closure for Muddle Through**

### Open methodology questions / decisions pending

1. **CSL peer-gap closure aggressiveness**: is +250bps Behring margin uplift correct for Muddle Through, or should it be more cautious (with full closure as Orderly Convergence)?
2. **CSL Seqirus demerger**: v1 values pre-demerger consolidated. Post-demerger value-of-stub treatment deferred to v2 sensitivity.
3. **DNL peer-triangulation refresh**: indicative β values used (Orica 1.05 / Yara 1.20 / ICL 1.10). EODHD pulls on those tickers pending from Ben.
4. **CSL peer EODHD pulls**: requested from Ben — Grifols, Takeda, Sanofi for triangulation refresh.

### Pending Ben asks (data workstream)

1. EODHD fundamentals exports for DNL peers: Orica (ASX:ORI), Yara (OSLO:YAR), ICL (NYSE:ICL)
2. EODHD fundamentals exports for CSL peers: Grifols (BME:GRF), Takeda (TSE:4502), Sanofi (Paris:SAN), GSK (LSE:GSK)
3. WBC NIM half-year-cadence history from FY22 onward (multi-year time series) — deferred from earlier
4. Macquarie Banking & Financial Services segment carve-out for bank peer set

---

## Carrying into next chat

If this chat session needs to end and you're starting a fresh one, here's how to bring the new Claude up to speed efficiently:

### Opening message for the new chat

A short message like this should be enough — the new Claude reads WORKING_NOTES (which is the bootstrap document) and gets oriented:

> "We're working on the VCC scenario-based equity valuation framework. Read WORKING_NOTES.md first — the 'Current state of play (18 June 2026)' section at the top has the latest. Methodology is at v0.6; DNL backport done; WBC v3 stable; CSL v1 workbook just built and needs sanity-check review (Muddle Through AUD 250 vs market AUD 105, +137% premium — the gap is too large; want to refine Muddle Through assumptions). Standing rules at lines 32-33 of WORKING_NOTES — formula-based workbooks, intuitive narrative per scenario. Push to git happens at cmd in `C:\Users\steph\vcc-valuations` using `git push origin main`."

### Specific tips for continuity

1. **The bootstrap pattern works.** WORKING_NOTES is the authoritative single source for state. Architecture spec is at v0.6; methodology doc is comprehensive. New Claude will pick up the framework conventions by reading those.

2. **Git pushes happen from your cmd, not from Claude.** The sandbox can stage and commit but can't reach github.com. Whenever Claude says "N commits ahead", run `git push origin main` from your terminal.

3. **Use the document discipline you've established.** When Claude proposes a new build, expect: documents register update per §14, source-document key-insights extraction, then YAML + workbook + thesis + discussion document, in that order.

4. **Standing rules are binding.** Any workbook Claude produces should be formula-based with the Assumptions sheet input pattern. Any write-up should include the intuitive per-scenario narrative. Push back if Claude forgets — both rules surfaced from your review feedback and are in WORKING_NOTES.

5. **The "framework vs market" gap is a feature.** For each company, the framework's Muddle Through may sit at market (DNL), below market (WBC), or well above market (CSL v1). Each tells a different analytical story per methodology §16. Be careful: don't reflexively re-tune assumptions to match market. The framework's job is to give a defensible base case; gaps to market are informative outputs, not calibration errors.

6. **What to do next session**: the natural priorities are (a) review CSL v1 Muddle Through assumptions — particularly Behring growth rate and peer-gap closure aggressiveness; (b) build CSL scenarios comparison once Muddle Through is finalised; (c) CSL thesis + discussion document (with intuitive narratives); (d) at some point, the DNL discussion document refresh with peer-gap closure framing if you want to re-share with Sunil.

7. **The repo has 37+ commits ahead of origin.** Push them all before you finish to ensure github mirror is current. Recovery from a lost local will then be straightforward.

---

## Current state of play (as of 12 June 2026)

**17 June 2026 (evening) — Methodology v0.6 consolidation: six review-derived refinements lifted.**

Tara asked a meta-question: from her review questions during DNL and WBC, are there methodology questions worth raising. Yes, six surfaced. All six are discipline / explicit-articulation refinements rather than analytical-substance changes; no per-share numbers move. v0.6 (additive only) lands them:

1. **§3.2 renamed to "Peer-gap closure overlay"** (from "Transformation overlay"). Reframed so the methodology view does not depend on any specific announced programme succeeding; the assumption is the closure trajectory, with a specific programme (UNITE for WBC, post-demerger glide for DNL) treated as the most credible stated mechanism. YAML field name `peer_gap_closure_overlay` (new) coexists with `margin_glide_path` (existing) for backward compatibility.

2. **§4.4 renamed to "Cost-of-closure consistency rule"** (from "Restructuring-cost consistency rule") and now distinguishes (a) P&L-absorbed (WBC's UNITE expensed through P&L, time-profile mechanic) versus (b) upfront one-off equity-bridge line (DNL's AUD 12m execution cash). Both worked examples in methodology. Auditor discipline test added.

3. **New §11 Workbook construction discipline** — Step 2 → Step 3 traceability requirement. Every workbook MUST show industry baseline AND company offset as separate rows, with the company-specific assumption derived. Replaces the implicit assumption that the analyst would mentally combine the two layers. DNL backport required (current DNL workbooks collapsed the chain).

4. **§14.5.1 Assumption-strength tagging.** Each calibration anchor tagged `[disclosed]`, `[derived]`, `[judgment]`, or `[default]`. Makes audit transparent — reviewer identifies at a glance which assumptions are hard-data-grounded.

5. **New §16 Interpretive output discipline — market-vs-framework gap.** Codifies the diagnostic the framework has been using implicitly. Where Muddle Through sits at market (DNL) the value-add is asymmetry exposure; where it doesn't (WBC), the closest-to-market scenario is the market's implied pricing, and the analyst articulates which assumptions differ.

6. **§16.4 External-facing artefact discipline — acronym sweep.** Internal workbooks may use shorthand (TTM, AIEA, NIM, CET1); external artefacts spell out all but the canonical commonly-recognised set. Standard expansions table for consistency.

Architecture spec bumped 0.5 → 0.6 with migration note covering all six refinements.

**DNL backports outstanding** (to be done on next DNL refresh):
- Rename "transformation overlay" → "peer-gap closure" in DNL company YAML, thesis, briefing pack, discussion document where appropriate
- Rebuild DNL workbook to show industry growth + company offset decomposition explicitly (similar to WBC v3 pattern)
- Apply β peer-triangulation discipline (already noted earlier)

These would constitute a "DNL v5" pass — methodology-discipline refresh, not analytical-substance change.

**Meta-observation:** Tara's review questions on the first two test companies surfaced these six refinements systematically. The hypothesis is that the third (CSL) and beyond will produce fewer refinements as the methodology hardens — but each new company should be expected to surface at least one or two before the framework is stable.

---

**17 June 2026 — WBC v3 reframe: "peer-gap closure" not "transformation"; UNITE evidence; industry+WBC growth decomposition explicit in workbook.**

Tara raised four substantive questions on the v2 WBC discussion document. Three of them surfaced methodology refinements that v3 addresses:

1. **Framing change (semantic but important).** "Transformation" implies a specific announced program. Westpac's UNITE update (26 March 2026 presentation) lists three stated outcomes of which the third is "CLOSE CTI RATIO GAP TO PEERS" — peer-gap framing is Westpac's own language. v3 reframes throughout: framework assumes WBC management will progressively close the cost-to-income / return-on-equity gap to peers; UNITE is the most credible disclosed mechanism but the framework does not depend on the specific program succeeding.

2. **Cost-to-income glide rebuild around UNITE evidence.** UNITE investment trajectory is FY24 AUD 147m → FY25 AUD 660m → FY26 AUD 850-950m → FY27-28 c.40% of total → FY29 lower. ~75% of spend expensed. Direct annual benefits disclosed AUD 190m (Mortgage Simplification 70 + One Commercial Bank 40 + One Collections 40 + One Wealth 40), plus undisclosed Digital Banker + further initiatives. Implied steady-state benefit FY30-31 ~AUD 300-400m p.a. Glide is now back-loaded: FY27-28 keep elevated UNITE spend (flat CTI), FY29-31 benefits emerge (CTI drops from 51.7% to 48.0%). Half of the gap to NAB (43%) and CBA (42%).

3. **Industry growth + WBC offset decomposition NOW EXPLICIT in workbook.** Previously workbook collapsed industry AIEA growth + WBC company offset into a single number. v3 P&L Forecast sheet shows: industry AIEA growth 4.5% (from §3 of discussion doc) less WBC company offset -15bps (Five Forces: rivalry -10bps + business-banking-rebuild -5bps) = WBC AIEA growth 4.35%. Same explicit decomposition for NIM: industry NIM 1.86% + WBC supplier-power offset +8bps (deposit franchise) = WBC NIM anchor 1.94%.

4. **(Deferred to a separate pass)** — Tara also noted the v2 model had no explicit transformation execution cost line. v3 acknowledges the UNITE spend is already in 1H26 base opex. FY27-28 maintaining UNITE spend = no additional execution overlay needed at the equity bridge level (it shows up in higher opex during those years). Methodologically this is "cost in P&L during execution years, benefits in P&L during reaping years" — consistent with §3.2 transformation overlay framing.

Workbook v3 result: AUD 30.08 per share (essentially same as v2 AUD 29.98; 10c uplift). Y1 EPS AUD 2.17 matches consensus FY27 AUD 2.18.

Documents register updated with UNITE presentation. wbc_unite_update_presentation_2026-03-26.pdf saved to data/financials/historical/wbc/.

---

**16 June 2026 (evening) — WBC NIM YE history FY22-FY25 extracted; historical results pack ingested.**

Tara provided WBC half-year and full-year results announcements covering FY22 through FY25 (plus FY23 via annual report) and MQG FY26 annual report + presentation. Saved to `data/financials/historical/{wbc,mqg}/` and registered in `wbc_documents.yaml` (wbc_historical_results_pack and mqg_fy26_results_pack).

WBC NIM YE history added to `bank_specifics.historical_anchors.nim_history_annual`:

| FY | Group NIM | AIEA avg (AUDm) | Basis |
| FY22 | 1.93% | 886,971 | Statutory (disclosed) |
| FY23 | 1.95% | 941,356 | AIEA-weighted half-year average |
| FY24 | 1.95% | 970,594 | Ex Notable Items (disclosed in FY25 comparative) |
| FY25 | 1.94% | 1,002,839 | Ex Notable Items (disclosed) |

Through-cycle anchor 1.94% (midpoint of FY22-FY25 range). Current 1H26 NIM 1.89% sits at lower end — front-book mortgage competition. Pre-2022 NIM regime materially higher (1H21 2.06%) — RBA-rate-cycle effect.

Synthesised `nim_anchors` block also added: through-cycle anchor, recent peak (1.97% 2H24), recent trough (1.88% 1H25), long-term pre-2022 baseline (2.06%), with scenario calibration commentary on how NIM should move under Muddle Through, Stagflation, Disorderly Climate.

MQG FY26 results saved for future MQG-Banking segment peer-comp work (currently excluded from peer set as "different archetype" at group level; segment carve-out from these reports addresses the "option 2" Tara discussed).

---

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
- **Gas-contract roll-off overlay added (29 May 2026).** Tara flagged that the US gas-contract roll-off (2028-2030 window) was narrative-only and the margin glide path actually moved the wrong way (transformation drove margins up through FY31 — exactly when the gas-cost advantage erodes). Resolution: added a structural-headwind overlay to the margin glide of -50