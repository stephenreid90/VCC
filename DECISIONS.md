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
| D-02 | 17 Jun 2026 | **Beta by peer triangulation**, not mechanical use of measured β — 3–5 comparable peers, outliers named, franchise-mix reasoning. | FIRM in method; the DNL/WBC/CSL peer *datasets* are still mock (`beta_data.py` `mock: True`), so the selected betas rest on judgement and named peers rather than on observed peer betas. Separate the two when citing. | methodology §3.5.3 |
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
| D-30 | 21 Aug 2026 | **CSL working-capital intensity ratified at 35%** — average of the two clean post-Vifor years (FY24 34.8%, FY25 36.8% → 35.8%), rounded per D-29. FY22–FY23 excluded as Vifor-acquisition-distorted. | FIRM — **live in the engine from 23 Aug 2026** | `data/companies/csl.yaml` `normalised_baseline.working_capital_intensity` |
| D-34 | 23 Aug 2026 | **CSL Muddle Through re-pinned at USD 129.21 / AUD 195.78** (from 134.52 / 203.83), and all six CSL goldens with it. The hand-typed 10% driver was **deleted**, not corrected — a stored derived value is the defect (D-16), so `build_segment_inputs_from_data` now calls `working_capital_intensity_from_data()`. | FIRM | `tests/dcf/test_scenario_goldens.py`; oracle `tests/dcf/test_csl_workbook_tie.py` |
| D-31 | 21 Aug 2026 | **DNL working-capital intensity held at the raw 13.76%** (single FY2025 statutory observation), overriding D-29's rounding (which would give 15%) — one observation is too thin to round confidently. Revisit once the 1H26 Appendix 4D lands and a genuine two-year average can be struck. Not yet wired into the engine/workbook. | PROVISIONAL — revisit on the Appendix 4D | `data/companies/dnl.yaml` `normalised_baseline.working_capital_intensity.rounding_override` |
| D-13 | 20 Aug 2026 | **DNL reinvestment is to be fixed** — both working capital and terminal capex = D&A — accepting that this retires the audited MT oracle and requires a workbook rebuild. | FIRM — **implemented 23 Aug 2026**, sizing closed (see D-32) | `design/methodology/working_capital_treatment.md` §7.3 |
| D-32 | 23 Aug 2026 | **The terminal is struck from its components, not by capitalising the final explicit FCFF.** `terminal_reinvestment` is a declared field on `FcfEngineInputs` with no default: `normalised` rebuilds terminal FCFF with capex at the declared terminal rate and working capital at g x intensity; `capitalise_last_fcff` is the legacy form, kept only for the v6 mechanics oracle. DNL declares `normalised` / `capex_rule: equals_da`. | FIRM | same §7.3; `data/companies/dnl.yaml` `normalised_baseline.terminal_reinvestment` |
| D-33 | 23 Aug 2026 | **DNL Muddle Through re-pinned at 2.831** (from 3.073), and all six DNL goldens with it. Disorderly Climate rises 44.6% because normalising its above-D&A terminal capex releases more than the working-capital build consumes. | FIRM | `tests/dcf/test_scenario_goldens.py`; oracle `tests/dcf/test_dnl_workbook_tie.py` |
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

## Methodology — the terminal state and returns

Full reasoning and the numbers behind these: `design/methodology/horizon_and_terminal_convergence.md`.

| ID | Date | Decision | Status | Reasoning |
|---|---|---|---|---|
| D-40 | 25 Aug 2026 | **DNL's gas roll-off holds at −1.5pp**; only the phasing moves, to concentrate in the FY2028–FY2030 re-pricing window the archetype states and complete FY2032. | FIRM on magnitude; phasing to be implemented | `us_gas_contract_maturity_profile` in `dnl.yaml`; paper §8 |
| D-41 | 25 Aug 2026 | **DNL Disorderly Climate capex is an arc**: +3.0pp through Y5, decaying across Y6–Y8 to a persistent +1.0pp. Splits the matrix's reallocating growth capex from its licence-to-operate maintenance capex. | FIRM | paper §9; `industrial_explosives.yaml` matrix entries |
| D-44 | 25 Aug 2026 | **Invested capital = net PP&E + intangibles + non-cash working capital.** Goodwill excluded — a demerged business is not charged in perpetuity for capital its predecessor deployed. DNL: 3,681.1m, ROIC 10.09% against a WACC of 8.877%. The construction is disclosed in the UI. | FIRM | paper §13 |
| D-45 | 25 Aug 2026 | **Of terminal growth, terminal return and reinvestment, only two are free.** g and ROIC are pinned — g from the macro/scenario work, ROIC from the Porter/moat work — and the reinvestment requirement is derived. Terminal growth carries a declared basis (inflation, long-run industry growth, or nominal GDP); alternatives appear in the UI as disclosure, never as a user-selectable input (D-23). | FIRM | paper §13; `revenue_growth_chain` B30 already derives industry nominal growth per scenario |
| D-46 | 25 Aug 2026 | **A regulatory setting is assumed indefinite unless currently under public debate.** Recorded as an observable field with a source and a date, not as a judgement about how long a licence lasts. WBC's moat horizon is therefore perpetual, with the named threat and the finite-horizon sensitivity attached. | FIRM | paper §12, §13 |
| D-47 | 25 Aug 2026 | **A terminal excess return is dated — not capped at the cost of capital, and not exempted by archetype.** A 10–15 year moat captures only 17–25% of a perpetual one, so a dated fade lands close to a hard cap for competitive archetypes and differs materially only for the licensed one, where the assumption should be visible. | FIRM | paper §12 decay table |
| D-06 | 25 Aug 2026 | **CSL's WACC parameters stay PROVISIONAL.** Reconsidered this session and retained: marking it FIRM would drop the commitment to revisit without supplying support for the 14× through-cycle EV/EBITDA multiple. Now load-bearing twice — as the discount rate and as the benchmark the terminal return is judged against. | PROVISIONAL — revisit when peer financials land | supersedes nothing; status re-affirmed |
| D-19 | 25 Aug 2026 | **Market prices are refreshed and everything re-tested after the UI work lands**, so all eighteen goldens move once rather than repeatedly. CSL's 105.53 reference against a 200-day average of 161.95 is a known distortion in the meantime. | PROVISIONAL — sequencing set | paper §13 |

**Still PROPOSED, not ratified** (all in `design/methodology/horizon_and_terminal_convergence.md`):
D-35 horizon rule, D-36 growth fade, D-37 archetype ten-year macro paths, D-38 capex
convergence, D-39 terminal capex from the final explicit year, D-42 terminal-return
diagnostic, D-43 decay horizon derived from Porter plus moat source.
