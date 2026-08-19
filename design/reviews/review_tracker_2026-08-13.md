# Full-project review — item tracker

Every finding from `full_project_review_2026-08-13.md` (Fable), with the triage verdict
from `triage_full_project_review_2026-08-13_opus.md`, the proposed treatment, anything
needing Stephen's input, and current status.

**Status key**

1. **DONE** — landed and committed.
2. **PLANNED** — agreed treatment, queued in a batch, no decision needed.
3. **NEEDS STEPHEN** — blocked on an owner decision.
4. **CLOSED** — no action required (verified as passing, disputed as wrong, or closed by
   owner decision).
5. **BACKLOG** — worth doing, not scheduled.

Batches refer to Part B of the triage report. Batch 1 (`675d931`) and Batch 2 (`f9e15b7`)
are complete; suite 146, ratchet 8, bases 3.073 / 30.03 / 203.83.

---

## A. Correctness bugs

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 1 | **CSL valuation-date mismatch.** Discounting anchors the valuation at 30 Jun 2026; net debt and share count are struck at 31 Dec 2025. Six months apart. Fable valued this at AUD 5-6/share; re-derived it is ±2%. | Two self-consistent repairs: (a) roll net debt forward to 30 Jun 2026, **+1.7%**; or (b) move the valuation date back to 31 Dec 2025 and add an H2-FY26 stub, **−1.9%**. (a) matches how DNL already does it. | **Q1** — which repair? | NEEDS STEPHEN |
| 2 | **Terminal-share warning existed only in the industrial engine**, so WBC (76.3%) and CSL (75.2%) — and WBC Stagflation at 84.5% — could not emit it. | Ported via a shared `fcf_engine.terminal_share_warning()`; `BankResult` gained `terminal_share_of_claim`, both gained `warnings`. Six new assertions. | — | **DONE** (Batch 1) |
| 3 | **Dead FX branch**, `translator.py:591` — both sides of the ternary return 1.0. Latent; DNL is AUD/AUD. | Raise `NotImplementedError` on the mismatch branch so the first genuine FX company fails loudly instead of silently valuing at 1.0. | — | PLANNED (Batch 6) |
| 4 | **CSL `net_interest_fy25` / `net_interest_decline` are populated but never read** by the segment engine. | Delete (correct for unlevered FCFF) or wire (if CSL moves to FCFE). Downstream of item 6 — do not touch until that is settled. | Resolved by **Q3** | NEEDS STEPHEN |
| 5a | `build_cfgs.py:697` prints "cfgs.json written", writes `cfgs_gen.json`. | Correct the message. | — | PLANNED (Batch 6) |
| 5b | `translator.py:852-857` computes a gross-margin base then unconditionally overwrites it with 0.0. | Delete the dead branch. | — | PLANNED (Batch 6) |
| 5c | `design/build_plan.html:167` still reads "Owner: Tara Reid". | Correct to Stephen. Already a known leftover in CLAUDE.md. | — | PLANNED (Batch 6) |
| 5d | `WORKING_NOTES.md:44` says "Suite 113" while the file elsewhere says 122. | **Partly disputed** — it sits inside a dated 12 Aug historical entry where 113 was true at the time. Treatment: annotate as historical rather than rewrite. | — | PLANNED (Batch 6) |

## B. Methodology

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 6 | **CSL discounts unlevered FCFF at the cost of equity, then deducts net debt** — charges for the debt twice. Fable estimated +8-15% on EV; re-derived it is **+21.5% to +26.6%** on the per-share value, and it pushes CSL *up*, not down as the review's fix-order assumed. The largest open item in the project. | Full write-up delivered: `design/methodology/csl_discount_rate_fork.md`. Three options — ratify FCFF@Ke as a convention, build a WACC, or move to FCFE. My recommendation is build the WACC, on a **target** 12-15% D/V rather than the 21.4% spot figure, which lands the uplift nearer +12-16%. | **Q3** — which option? | NEEDS STEPHEN |
| 7 | **DNL terminal capitalises capex 7.0% against D&A 7.3%** — the asset base runs down in perpetuity while revenue grows 2.5%. Worth **−AUD 0.079/share (−2.6%)**. Fable's number checks out. | Bundle with the larger working-capital gap I found (see M1 below) as one DNL reinvestment decision. Changes the audited workbook, not just the engine. | **Q4** — see M1 | NEEDS STEPHEN |
| 8 | **Bank engine has no §15.5 CET1 constraint.** Flat 0.75 payout in every world; book equity compounds at 2.6% p.a. against AIEA at 4.35%, so the implied capital ratio falls every year and the model never notices. Stagflation NPAT falls 57.5% with payout unchanged. | Warn-only check first (retained earnings vs AIEA growth × RWA density) — zero base-tie risk. Forced payout cut under stress as a second, separate step. The CET1 and RWA data is already in `wbc.yaml:538-568`. | **Q5** — warn-only first, or go straight to the forced cut? | NEEDS STEPHEN |
| 9 | **Stub construction diverges from §7.2.** The text says pro-rate the next full year; the engine pro-rates the base year. The engine ties the audited workbook, so the text is what is wrong. | Align the methodology text to the engine. Text edit, zero regression risk. | — | PLANNED (Batch 6) |
| 10 | **CSL sits 93% above market** — §16.3 requires the structural-reason treatment. | (a) Price staleness **confirmed and broader than Fable said**: all three market prices are struck at 2026-06-15, not just CSL's. (b) Fable's claim that items 1 and 6 both push CSL down is **backwards** — item 6 pushes it up ~24%. Do the §16.3 write-up and the CSL gap panel *after* item 6 is decided. | **Q2** — refresh prices, or is 15 June a deliberate fixed valuation date? | NEEDS STEPHEN |
| 11 | **β triangulation is honoured in form, but DNL's peer dataset is flagged `"mock": True`** while the ratified β 1.10 narrative cites those peers. | Annotate the decision record to separate observed from awaited. Also found: `beta.mock` is never read by `gen_ui.py`, so the "mock data" warning is unconditional and will persist after Ben's feed lands — wire it. | — | PLANNED (Batch 6) |

## C. Data integrity

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 12 | **`csl.yaml` stores the same layer-2 judgment twice** — and it is broader than Fable's four items. Effectively the whole `normalised_baseline` scalar block mirrors `segment_fcff`, and only `segment_fcff` is read. Also duplicated beyond Fable's list: `da_pct_revenue`, `working_capital_change`, `tax_rate`, `restructuring_cash_to_come`, `terminal_ebit_margin`. | Delete the non-engine copies, keep the rationale prose beside the surviving copy. | — | PLANNED (Batch 3) |
| 12b | **The ratchet cannot see intra-YAML duplication** — check 3 scans code only. A second hole found: a value invented in *code* that exists nowhere in the register is also invisible (this is how the CSL broker literal survived). | Extend the lint with a same-file / cross-file duplicate-scalar check, plus a check for display values in code with no register source. | — | PLANNED (Batch 3) |
| 13 | **§7.5 anchor-date discipline is enforced nowhere.** This is the validator that would have caught item 1 automatically. | Warn when a company's net debt, share count and discounting date are not struck at one date. Build it alongside the item 1 repair. | Sequenced after **Q1** | PLANNED (Batch 3) |
| 14 | Layer-1/layer-2 split is clean where executed. | Independently spot-checked `resolve_normalised_baseline` and the WBC AIEA/NIM chain. Genuinely clean — agreed PASS. | — | CLOSED |

## D. Traceability

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 15 | **The Derivation layer covers the bridges but not the per-year build** — all three engines emit revenue/EBIT/FCFF with empty `inputs` dicts, so the workbooks explain more than the engines can. | Finish the set: one step per P&L line per period, `inputs` populated. Low urgency, no risk. | — | PLANNED (Batch 6) |

## E. Test quality

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 16 | **Only Muddle Through was pinned.** The other five levels per company were asserted by ordering (WBC, CSL) or drivers (DNL), so a regression moving every level while preserving order passed silently. | All 18 pinned in `tests/dcf/test_scenario_goldens.py`, flagged engine-owned not workbook-owned. Suite 122 → 146. | — | **DONE** (Batch 1) |
| 17 | **The LibreOffice recalc tie runs ad hoc**, not as a suite gate; `_recalc.py` is a regeneration script and is not collected by pytest. Fable's framing of the circularity is right. | Add an opt-in pytest marker so it can be run deliberately without making LibreOffice a hard suite dependency. | — | PLANNED (Batch 6) |
| 18 | **Under-tested areas** — `engine_workbook.py` (1,467 lines) has no coverage; `__post_init__` validation errors untested. | Add workbook-builder tests and input-validation tests. **Two of Fable's four claims are wrong:** `test_e2e_dnl_mt.py:103` *does* assert the §11.4.2 warning fires, and `EquityBridge.from_anchor` *is* exercised end-to-end with a pinned outcome. | — | PLANNED (Batch 6) |

## F. Schema

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 19 | **`FiveForces` has no `model_validator`** — a block with neither entrants nor substitutes validates, and both naming generations can be supplied with contradictory ratings. `bank_archetype` and `rivalry_subforces` are untyped `Dict[str, Any]` escape hatches. | One `model_validator` (one-of-each-force, reject dual-generation conflicts) plus a typed `BankArchetype` block. | — | PLANNED (Batch 3) |
| 20 | **`archetype=None` falls back silently on file absence**, so a typo'd archetype id degrades instead of raising. | Make the fallback conditional on an explicit `segment_level_valuation: true` marker. | — | PLANNED (Batch 3) |

## G. UI architecture and workbooks

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 21 | Standalone UI + base64 workbook architecture is sound; the "no JS engine port" decision held. One gap: no "reset all" for localStorage user scenarios. | Agreed PASS on the architecture. Add a reset-all control in Batch 5. | — | CLOSED (architecture) / PLANNED (reset-all, Batch 5) |
| 22 | **Workbook discipline honoured with exceptions.** DNL Equity bridge carries 14 literals (all styled as inputs, but off the Assumptions sheet); WBC `Multiples!B3` hard-codes the market price. | Move the DNL bridge inputs onto Assumptions. For WBC, the fix needs a step Fable missed: **WBC's Assumptions sheet has no market-price row at all**, so one must be added before `B3` can link to anything. | — | PLANNED (Batch 5) |

## H. UI/UX suggestions

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| 23 | Headline sub-caption `pvsub` unused — the punchline isn't landed in 5 seconds. | **Partly wrong** — CSL's *is* populated. Do it for DNL and WBC: engine-sourced gap sentence. | — | PLANNED (Batch 5) |
| 24 | Metric card 4 is inconsistent — asymmetry for DNL/WBC, terminal share for CSL. | Show asymmetry for all three; move terminal share into the discount-rate panel where it belongs beside the §11.4.2 warning. | **Q6** | PLANNED (Batch 5) |
| 25 | DNL's broker bar equals the market price (both 3.61) — the feed's target echoes spot. | **Closed by owner decision 13 Aug: leave DNL alone** until Ben's feed brings real coverage. | — | CLOSED |
| 26 | Bar values show only the per-share number, no "% vs MT". | Add the delta beside each bar value — already computed for the narrative. | — | PLANNED (Batch 5) |
| 27 | The download button lives only inside detail panels, so the most persuasive traceability artefact is invisible until a reviewer drills down. | Persistent "Download audited workbook" in the header, sheet count from cfg. | — | PLANNED (Batch 5) |
| 28 | No provenance chip — the topnote reads as a disclaimer rather than a feature. | One-line engine/commit/data provenance line under the header. Sell the one-source-of-truth story. | — | PLANNED (Batch 5) |
| 29 | **Bars are click-only divs; the whole file has one `aria-label`; tab selection is border-colour only** (WCAG 1.4.1 failure). The file is currently unusable by keyboard. | `role`/`tabindex`/Enter-Space/`aria-label` on bars; `aria-pressed` and a non-colour cue on tabs. | — | PLANNED (Batch 5) |
| 30 | Narrow-width overflow: fixed 122px label column, value label at `calc(w% + 6px)`. | Move the value inside the bar above ~80% width. **Partly wrong** — the DCF workings table is already wrapped; the unwrapped one is the transitory-forces table. | — | PLANNED (Batch 5) |
| 31 | Slider moves silently swap the engine value for the reduced form. | **Partly wrong** — the override note already shows both values; the missing word is "approximation". The real problem Fable missed is bigger: the DCF panel is static but captioned "straight from the production engine" (see M5). Fix the caption first. | — | PLANNED (Batch 5) |
| 32 | DNL has 8 explore tabs, WBC/CSL have 6 — reads as unfinished rather than data-blocked. | Add the missing tabs with an explicit "awaiting peer feed (Ben)" placeholder, which also advertises the dependency. Fable's five-forces cross-reference claim is **wrong as stated** — no company's UI panel has one; CSL's *workbook* has no five-forces sheet at all, which is the better finding. | **Q7** — placeholder tabs, or trim DNL to match? | NEEDS STEPHEN |
| 33 | Scenario narratives are buried one click deep. | Show the first sentence + "why it lands here" under the chart on bar selection. | — | PLANNED (Batch 5) |
| 34 | No onboarding for first-time reviewers. | Dismissible 3-step "how to read this" strip aimed at the feedback ask. | — | PLANNED (Batch 5) |
| 35 | No dedicated CSL market-gap panel. | Build it — but **after** items 6 and 10 land. Writing "why we differ" before knowing whether the gap is 93% or 140% is wasted work. | Blocked on **Q2, Q3** | NEEDS STEPHEN |
| 36 | No print/PDF stylesheet; the file prints poorly. | Worth doing if the prototype graduates. | — | BACKLOG |
| 37 | No side-by-side scenario comparison. | All the data is already in cfg. Nice-to-have. | — | BACKLOG |
| 38 | Dead store-zip XLSX writer kept for a path no company takes. | **Larger than Fable said** — `VCCXLSX`, `VCCBOOK` *and* `DNLRICH` are all dead: ~435 lines, ~32 KB inlined into every generated file (13-17% of each). The `module.exports` overwrite each other and the node tests they were shared with no longer exist. Delete all three. | — | PLANNED (Batch 6) |

---

## Items Fable missed (found during triage)

| # | Issue | Proposed treatment | Needs your input? | Status |
|---|---|---|---|---|
| M1 | **DNL assumes zero working capital** in every explicit year *and* the terminal, while growing revenue 6.15% p.a. as an industrial manufacturer with receivables and inventory. Worth **−AUD 0.14 to −0.27/share (−4% to −9%)** — two to three times Fable's terminal-capex wedge. Together with item 7, DNL's reinvestment treatment is worth −7% to −11%, moving the discount to market from −15% to about −22%. | Decide whether the working-capital assumption is open for revision. Changes the audited workbook, not just the engine. | **Q4** | NEEDS STEPHEN |
| M2 | **CSL page opened on the broker bar** — headline read 136.00, not 203.83. | Opening bar now derived from `kind=='live'` for all three companies. | — | **DONE** (Batch 2) |
| M3 | **CSL broker bar was a hard-coded AUD literal at a stale FX** (136.00 = the correct USD consensus at ~1.406). | Now sourced from the register and converted at the model's own FX: 146.60. The two register consensus figures still disagree by ~6% — flagged for Ben's next refresh. | — | **DONE** (Batch 2) |
| M4 | **DNL's slider default rounding put a false "discount-rate override" chip on all six bars**, contradicting the single-rate standing rule on screen, and rendered 3.0719 instead of 3.073. | `cp.re0` and the slider default are now one number; the unrounded engine rate is kept as `cp.reEngine`. Reduced form now returns `cp.base` exactly. | — | **DONE** (Batch 2) |
| M5 | **The DCF panel is static but captioned "straight from the production engine"** — after any slider move the headline is the reduced form while the build-up still shows the engine path. | Fix the caption first, the behaviour second. This is the real version of item 31. | — | PLANNED (Batch 5) |
| M6 | **DNL's two DCF views disagree by AUD 154m of EV** (7,009 vs 6,855 — the table view omits the equity-bridge adjustment), and its "tie check" is tautological because the reconstruction is back-solved from the answer. | Reconcile the two views; make the tie check real or remove it. | — | PLANNED (Batch 5) |
| M7 | **Cross-company text leak** — CSL's β workbench says "re-lever at **DNL** gearing D/E". Present in all three generated files. | Parameterise the label. | — | PLANNED (Batch 5) |
| M8 | **Stored self-XSS via user scenario names** — from `prompt()`, unescaped into `innerHTML`, persisted in localStorage so they re-execute on every load. | `esc()` applied (the helper already existed). | — | **DONE** (Batch 2) |
| M9 | **`build_cfgs.py` source still carries superseded numbers** (DNL 3.48, WBC 30.15, shares 1884, netDebt 1512). Verified the packs overwrite all of them, so nothing renders wrong today — but a stale headline one edit from being displayed. | Delete the dead literals. | — | PLANNED (Batch 6) |
| M10 | **All three market prices are struck at 2026-06-15** — two months stale, not just CSL's. | See Q2. | **Q2** | NEEDS STEPHEN |
| M11 | **WBC's Assumptions sheet has no market-price row**, which is why `Multiples!B3` hard-codes it. | Add the row, then link. Prerequisite for item 22. | — | PLANNED (Batch 5) |
| — | *Checked because they looked wrong, and are not:* WBC AT1 treatment (no double-count); CSL FX applied only at the per-share line; single-rate discipline holds across all six scenarios in all three engines; all three embedded workbooks recalculate with zero error cells. | No action. | — | CLOSED |

---

## Open questions — consolidated

| Q | Question | Blocks |
|---|---|---|
| **Q1** | CSL valuation-date anchoring: roll net debt forward to 30 Jun 2026 (+1.7%), or move the valuation date back to 31 Dec 2025 with a stub (−1.9%)? | Items 1, 13 |
| **Q2** | Market prices are all struck 15 June 2026. Refresh them, or is that a deliberate fixed valuation date? | Items 10, 35, M10 |
| **Q3** | CSL discount rate: ratify FCFF@Ke, build a WACC (+21.5% to +26.6%), or move to FCFE? Write-up at `design/methodology/csl_discount_rate_fork.md`. | Items 4, 6, 35 |
| **Q4** | DNL reinvestment: is the zero-working-capital assumption open for revision (−4% to −9%), and do you want terminal capex set to D&A (−2.6%)? Both change the audited workbook. | Items 7, M1 |
| **Q5** | WBC CET1: warn-only check first, or go straight to a forced payout cut under stress? | Item 8 |
| **Q6** | Metric card 4: show asymmetry for all three companies and move terminal share into the discount-rate panel? | Item 24 |
| **Q7** | Tab parity: add placeholder tabs to WBC/CSL advertising the Ben dependency, or trim DNL to six? | Item 32 |

## Tally

54 tracked items.

| Status | Count |
|---|---|
| NEEDS STEPHEN | 10 |
| DONE | 6 |
| PLANNED | 33 |
| CLOSED | 3 |
| BACKLOG | 2 |

> **Read this in the browser instead.** `review_tracker_2026-08-13.html` (same folder) is
> the same content as a real rendered table — filterable by status, searchable, with the
> tally as counters at the top. This markdown version is the plain-text fallback.
