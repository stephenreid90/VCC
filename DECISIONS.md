# DECISIONS — the ratified register

**Purpose: to stop settled questions being reopened.** One line per decision, with the
date it was made and a pointer to where the reasoning lives. This is the file to check
*before* proposing a method, not after.

**How to use it.** If a question you are about to open appears here, it is closed —
read the linked reasoning and proceed on that basis. If you believe a decision is
wrong, say so explicitly and ask Stephen to revisit it; do not quietly re-derive an
alternative. Reopening without saying so is the single largest source of drift in this
project.

**How to maintain it.** Add a row the moment Stephen ratifies something. Never delete a
row — supersede it, and leave the old one with `SUPERSEDED` and a pointer to the row
that replaced it. The history of what we used to think is part of the record.

Status values: **FIRM** (settled, do not reopen) · **PROVISIONAL** (working assumption,
flagged for revisit when named evidence arrives) · **SUPERSEDED**.

---

## Methodology — discount rates and capital

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-01 | v0.6 spec | **One discount rate per valuation.** No mixing WACC across the build; scenarios differ in cash flows, not in the rate. | FIRM | `architecture.md` §3.5 |
| D-02 | 17 Jun 2026 | **Beta by peer triangulation**, not mechanical use of measured β — 3–5 comparable peers, outliers named, franchise-mix reasoning. | FIRM | methodology §3.5.3 |
| D-03 | (spec) | **Cost of debt = risk-free rate + spread on comparably rated paper**, using an actual rating where one exists and a notional rating with stated reasoning where it does not. | FIRM | `architecture.md:788-802`; worked precedent `data/companies/dnl.yaml:549` |
| D-04 | (spec) | **Capital structure is a target ratio** (net debt/EBITDA or D/E), not a spot market weight. | FIRM | `architecture.md:791` |
| D-05 | 20 Aug 2026 | **CSL moves to FCFF discounted at a WACC**, built on a *target* capital structure rather than spot D/V. Resolves the FCFF-at-Ke inconsistency. | FIRM | `design/methodology/csl_discount_rate_fork.md` |
| D-06 | 20 Aug 2026 | **CSL WACC parameters** — notional BBB+/A−, ~100bp spread, kd 5.50%; target 1.8× ND/EBITDA at a through-cycle 14× EV/EBITDA → D/V 12.9%. | PROVISIONAL — the EV/EBITDA multiple has no independent support; revisit when peer financials land | `design/methodology/csl_cost_of_debt_and_target_structure.md` |
| D-07 | 25 Jun 2026 | **Terminal-share warning is non-blocking** (owner decision R3). Above 70% of value it triggers a §11.4.2 sensitivity pass; it never auto-suppresses or adjusts. | FIRM | `fcf_engine.py:40-43` |

## Methodology — cash flows and the bridge

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-08 | (spec) | **Share count and net debt are anchored at the last reported balance-sheet date, both to the same date.** The ongoing buyback is NOT projected forward. | FIRM | methodology §5 |
| D-09 | 20 Aug 2026 | **Working capital uses the broad definition:** (current assets − cash) − (current liabilities − interest-bearing debt). Not trade-only. | FIRM | `design/methodology/working_capital_treatment.md` |
| D-10 | 20 Aug 2026 | **Working-capital carve-outs:** all interest-bearing items *including current lease portions*; assets and liabilities held for sale; all cash. | FIRM | same, §2 |
| D-11 | 20 Aug 2026 | **Banks are exempt from working capital by rule, not by returning zero.** An absent check must stay distinguishable from a passing one. | FIRM | same, §3 |
| D-12 | 20 Aug 2026 | **Working-capital intensity is struck on the level, averaged over available years, and applied to ΔRevenue.** Never fit the marginal rate directly. | FIRM | same, §7.1 — CSL's six years give marginal rates of +78%, −40%, +31%, +1264%, −50% |
| D-29 | 21 Aug 2026 | **Working-capital intensity rounding protocol:** judge which years are "clean" (stated reason), average their level intensities, round to the nearest 5 percentage points. General, replicable rule — not CSL-specific. | FIRM | `working_capital_intensity_from_data()`, `src/vcc_valuations/translator.py`; worked in `working_capital_treatment.md` §6 |
| D-30 | 21 Aug 2026 | **CSL working-capital intensity ratified at 35%** — average of the two clean post-Vifor years (FY24 34.8%, FY25 36.8% → 35.8%), rounded per D-29. FY22–FY23 excluded as Vifor-acquisition-distorted. Not yet wired into the engine/workbook (§8 below). | FIRM (mechanism); NOT YET LIVE in the engine | `data/companies/csl.yaml` `normalised_baseline.working_capital_intensity` |
| D-31 | 21 Aug 2026 | **DNL working-capital intensity held at the raw 13.76%** (single FY2025 statutory observation), overriding D-29's rounding (which would give 15%) — one observation is too thin to round confidently. Revisit once the 1H26 Appendix 4D lands and a genuine two-year average can be struck. Not yet wired into the engine/workbook. | PROVISIONAL — revisit on the Appendix 4D | `data/companies/dnl.yaml` `normalised_baseline.working_capital_intensity.rounding_override` |
| D-13 | 20 Aug 2026 | **DNL reinvestment is to be fixed** — both working capital and terminal capex = D&A — accepting that this retires the audited MT oracle and requires a workbook rebuild. | FIRM (sizing still open) | `design/methodology/dnl_working_capital_derivation.md` |
| D-14 | 12 Aug 2026 | **Scenario margin and capex deltas apply as a parallel shift** across the explicit years. | FIRM | `tests/dcf/test_dnl_all_scenarios.py` header |

## Data and single source of truth

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-15 | (protocol) | **Structured fields are the source of truth** where prose and structured artefacts disagree. | FIRM | `CLAUDE.md` |
| D-16 | (protocol) | **No derived value is ever stored.** Computed quantities are recomputed by the engine, never persisted beside their own inputs. | FIRM | `design/single_source_of_truth.md` §3; enforced by `tests/test_ssot_lint.py` check 1 |
| D-17 | (protocol) | **Layer 1 is observed, layer 2 is judgement, layer 3 is derived.** Judgement never lives in a machine-refreshable feed file. | FIRM | same, checks 2–3 |
| D-18 | (protocol) | **Industry-archetype baseline and company-position offset are separate rows**, with the company figure derived rather than direct-input. | FIRM | methodology §11; standing rule 1 |
| D-19 | 20 Aug 2026 | **Market reference prices stay at the 15 June 2026 snapshot** until Ben's feed returns. Get the framework right first. | PROVISIONAL — revisit when the feed is back | this session |
| D-20 | 20 Aug 2026 | **DNL's broker bar stays as-is** despite equalling the market price; the feed's target echoes spot because coverage is thin post-demerger. | PROVISIONAL — revisit when real consensus coverage exists | review item 25 |

## Build and presentation

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-21 | (standing) | **Workbook discipline.** Excel uses formulas, never Python-computed hard-coded values. Inputs on a dedicated Assumptions sheet, yellow fill, blue text; every other cell links back. | FIRM | `CLAUDE.md` standing rule 1 |
| D-22 | (standing) | **Write-up discipline.** Every company write-up carries an intuitive narrative per scenario: macro story → key channels → why the number lands there, plus a mental short-cut. | FIRM | `CLAUDE.md` standing rule 2 |
| D-23 | (standing) | **No JS port of the engine.** The UI is downstream of the one engine; sliders are a labelled reduced-form approximation, never a second model of record. | FIRM | review item 21 |
| D-24 | (standing) | **Override discipline:** target ≤20% of cells overridden per company. Above that the archetype is mis-specified. | FIRM | `CLAUDE.md` |
| D-25 | 13 Aug 2026 | **The 18 scenario levels are engine-owned goldens, not workbook oracles.** Only Muddle Through is independently audited. A golden failing means a headline number moved and needs sign-off — not that there is a bug. | FIRM | `tests/dcf/test_scenario_goldens.py` header |

## Process

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-26 | 21 Aug 2026 | **Survey before you conclude.** Never assert that data, a document, a protocol or a prior decision does not exist without scanning the directory that would hold it. Run `scripts/repo_inventory.py` at session start. | FIRM | `CLAUDE.md` |
| D-27 | 21 Aug 2026 | **A curated `*.yaml` in `data/` is a summary, not a source.** Raw multi-year statements live in `data/financials/*.csv` and `data/financials/historical/<company>/`. | FIRM | same |
| D-28 | (standing) | **Australian English; number any list of 2+ points** so it can be answered by number. | FIRM | `CLAUDE.md` |
