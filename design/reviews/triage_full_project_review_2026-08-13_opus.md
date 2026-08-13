# Triage of the full-project review (13 August 2026)

Independent second-opinion triage of `full_project_review_2026-08-13.md` (reviewer:
Claude Fable 5). Triage by Claude Opus 5, deliberately a different model. **Assessment
and plan only — no code changed. Nothing executes until Stephen signs off.**

## Verification actually performed

1. `git fetch`; HEAD `92bbd2c` (one commit past the `d0cdaf7` Fable reviewed — handover
   note only, no source change).
2. Suite green: **122 passed**; SSOT ratchet **8 passed**.
3. All three engines re-run from data; all six scenarios per company reproduce exactly
   (DNL 3.5619 / 3.0730 / 2.9850 / 2.2224 / 1.1768 / 1.0194; WBC 35.7058 / 30.0304 /
   29.6987 / 27.1096 / 22.5807 / 18.6488; CSL AUD 237.29 / 203.83 / 198.68 / 174.79 /
   168.23 / 159.90).
4. `build_cfgs.py && gen_ui.py` rebuilt sandbox-side; the three embedded workbooks
   decoded and recalculated headless in LibreOffice — zero error cells, every scenario
   ties the engine to the last cent. Bases 3.073 / 30.03 / 203.83 present in all three
   HTMLs.
5. Where Fable asserted a number, I re-derived it rather than accepting it. Four of
   those re-derivations changed the answer materially — see Part C.

**Headline judgement: the review is good and mostly right.** Of 38 findings, 24 stand as
written, 7 are overstated or wrong in a way that changes the priority order, and 7 are
cosmetic. But Fable **missed the two items I would fix first** — a CSL UI that opens on
the wrong bar, and DNL's zero working-capital assumption — and it got the *direction* of
its own biggest methodology finding backwards.

---

# Part A — verdict on each finding

Format: finding — **classification** — evidence.

## A1. Correctness bugs (Fable 1-5)

1. **CSL FY26 / net-debt anchoring — CONFIRMED (real defect), but the framing and
   magnitude are wrong. NEEDS-STEPHEN.**
   The defect is real and is a *date mismatch*, not lost cash flow. `segment_engine.py:131-133`
   discounts FY27 at t=0.5, which anchors the valuation date at **30 Jun 2026**. But
   `csl.yaml:655` `net_debt: 9100` is documented in `data/financials/csl.yaml:56` as
   *"1H26 close"* = **31 Dec 2025**, and `csl.yaml:462` anchors the share count at
   **2025-12-31** too. So shares and net debt are correctly paired with each other
   (CLAUDE.md §5 convention holds) but sit six months behind the discounting date.
   Fable's claim that ~AUD 5-6/share is "silently lost" does not survive arithmetic —
   see Part C item 1. Real magnitude: **±2%**, and the sign depends on which fix you pick.

2. **Terminal-share warning missing from bank and segment engines — CONFIRMED must-fix,
   cheap.** `fcf_engine.py:43,382-388` is the only implementation. Measured this session:
   WBC MT terminal share **76.3%**, CSL MT **75.2%** — and WBC Stagflation is **84.5%**,
   the worst number in the project and the one world where the warning matters most.
   Five of DNL's six scenarios already trip it. Fable is right and slightly understates it.

3. **Dead FX branch — CONFIRMED nice-to-have.** `translator.py:591`:
   `fx_rate = 1.0 if functional_ccy == reporting_ccy else 1.0`. Both branches 1.0. Latent
   only; DNL is AUD/AUD. Should raise `NotImplementedError` on the else branch rather than
   silently return 1.0.

4. **CSL `net_interest_fy25` / `net_interest_decline` unused — CONFIRMED. NEEDS-STEPHEN
   (delete or wire).** Populated at `translator.py:764-765` from `csl.yaml:647-648`; never
   read in `SegmentEngine.run()`. For unlevered FCFF the correct answer is *delete*: interest
   does not belong in FCFF and the fields are a live invitation to double-count. But see
   finding 6 — if CSL moves to FCFE they become load-bearing, so decide 6 first.

5. **Cosmetics — all four CONFIRMED nice-to-have.**
   (a) `build_cfgs.py:697` prints `"cfgs.json written"`, writes `cfgs_gen.json`.
   (b) `translator.py:852-857` computes a gross-margin base then overwrites with `0.0`.
   (c) `design/build_plan.html:167` "Owner: Tara Reid" (already known in CLAUDE.md).
   (d) `WORKING_NOTES.md:44` "Suite 113" in the ALL-THREE-COMPLETE header; actual 122.

## A2. Methodology (Fable 6-11)

6. **CSL discounts FCFF at Ke then deducts net debt — CONFIRMED, and MUCH bigger than
   Fable says. NEEDS-STEPHEN, and it is the single largest open item in the project.**
   The inconsistency is exactly as described (`segment_engine.py:3-5`, `:147`). Fable
   estimates "perhaps +8-15% on EV". Re-derived: at D/V 21.4% (net debt USD 9,100m,
   market cap USD 33,354m) and pre-tax cost of debt 4.5-5.5%, WACC lands at **7.66-7.83%**
   vs Ke 8.75%, and CSL MT goes to **AUD 248-258 (+21.5% to +26.6%)**. That takes CSL from
   +93% above market to **+135% to +145%** above market. This is not a tidy-up; it is a
   decision that reframes the CSL story.

7. **DNL terminal capitalises capex < D&A — CONFIRMED, and Fable's number is right.**
   `fcf_engine.py:372`. Y5 capex 7.0% vs D&A 7.3% (`capex_pct[-1]=0.07`, `da_pct=0.073`).
   Setting terminal capex = D&A gives **3.0730 → 2.9938, −AUD 0.079/share (−2.6%)**.
   Fable said "~0.08, ~2.5%" — accurate. But this is the *smaller half* of DNL's
   reinvestment problem: see Part D item 1.

8. **Bank engine has no §15.5 CET1 constraint — CONFIRMED. NEEDS-STEPHEN.**
   `bank_engine.py:135` pays out a flat 0.75 in every period of every scenario. Measured:
   book equity grows 72,825 → 83,682 (+14.9% over 5.35 years ≈ 2.6% p.a.) while AIEA
   compounds at 4.35% p.a. — so the implied capital ratio **falls every year, in every
   world**, and the model never notices. Under Stagflation NPAT falls 57.5% and payout
   still holds at 75%. The data to check this is already in the repo
   (`wbc.yaml:538-547` CET1 12.42%, target 11.0-11.5%; `wbc.yaml:551-568` full RWA
   composition). Also confirmed: terminal implied payout 1−g/ROE = 66.7% vs explicit 75%
   (a genuine boundary step), and "ROE fade" is a single terminal input, not a path.
   *Separately checked and clean:* the AT1 treatment does **not** double-count — book
   equity 72,825 includes AT1, terminal ROE 10.5% is struck on total book equity (Y5
   implied 10.89% on the same base), and AT1 face is deducted once at the ordinary-equity
   line. Fable didn't raise it; I checked because it looked wrong. It isn't.

9. **Stub construction diverges from written methodology — CONFIRMED nice-to-have.**
   `fcf_engine.py:329` pro-rates the *base* year; §7.2
   (`equity_bridge_and_valuation_mechanics.md:658`) says the *next full year's forecast*.
   The engine ties the audited workbook, so the text is what is wrong. Text edit only,
   zero regression risk.

10. **CSL 93% above market — CONFIRMED as a live §16.3 obligation. NEEDS-STEPHEN.**
    (a) *Confirmed stale, and worse than Fable thought:* `csl.yaml:467` dates the price
    **2026-06-15** — two months old today. The same is true of **WBC (35.32, dated
    2026-06-15)** and DNL. CSL's 50-day MA is 115.28 and its 200-day MA 161.95 against a
    spot of 105.53, i.e. a fast-falling stock where two months is a long time.
    (b) *Fable's directional claim is backwards* — see Part C item 2.

11. **β peer triangulation honoured; DNL's evidence base is mock — CONFIRMED nice-to-have.**
    `beta_data.py:37` `"mock": True`; the workbook labels it MOCK
    (`engine_workbook.py:573`). The decision record should separate observed from awaited.
    Related dead wiring found: `beta.mock` is never read by `gen_ui.py`, so the "mock data"
    warning is unconditional and will keep showing after Ben's feed lands.

## A3. Data integrity (Fable 12-14)

12. **csl.yaml duplication — CONFIRMED must-fix, and materially broader than the four
    items listed.** All four of Fable's are real (`csl.yaml:612-634` vs `:670-676`;
    `-2559` at `:514`/`:645`; `0.045` at `:520`/`:651`; `0.06` at `:531`/`:653`). I also
    found: `da_pct_revenue 0.06` (`:526`/`:652`), `working_capital_change 0.10`
    (`:535`/`:653`), `tax_rate 0.19` (`:541` and every `by_scenario` block),
    `restructuring_cash_to_come 507` (`:550`/`:656`), `terminal_ebit_margin 0.30`
    (`:558`/`:676`). In effect the **whole `normalised_baseline` scalar block mirrors
    `segment_fcff`**, and only `segment_fcff` is read (`translator.py:724`). The lint gap
    is confirmed: `test_ssot_lint.py:46` `SCAN_GLOBS` covers `src/`, `scripts/` and the
    UI generator only — no YAML-internal or cross-file scan.

13. **§7.5 anchor-date discipline enforced nowhere — CONFIRMED nice-to-have,** and it is
    the validator that would have caught finding 1 automatically. Do it *with* finding 1.

14. **Layer-1/layer-2 split clean — PASS, agreed.** Independently spot-checked
    `resolve_normalised_baseline` and the WBC AIEA/NIM industry-anchor + company-offset +
    scenario-delta rows. Genuinely clean.

## A4. Traceability (Fable 15)

15. **Derivation layer thin on the per-year build — CONFIRMED nice-to-have.**
    `fcf_engine.py:466-473`, `bank_engine.py:184-190`, `segment_engine.py:175-180` all
    emit revenue/EBIT/FCFF (or TOI/NPAT/dividend) with `{}` for `inputs`. The workbooks
    show strictly more than the engines can explain. Correct diagnosis; low urgency.

## A5. Tests (Fable 16-18)

16. **Only MT levels are pinned — CONFIRMED must-fix, cheap.**
    `test_wbc_bank.py:43-50` and `test_csl_segment.py:41-46` assert ordering only.
    `test_dnl_all_scenarios.py:57-63` does pin per-scenario *drivers* to the v4 workbook
    and `:83` pins asymmetry > 3.0×, so DNL is better protected than WBC/CSL — but no
    non-MT *level* is pinned anywhere. Pin all 18.

17. **Golden circularity correctly avoided; recalc tie is not a suite gate — CONFIRMED.**
    `tests/dcf/golden/_recalc.py` is a regeneration script, not collected by pytest
    (verified: `--collect-only` returns nothing). Fable's framing is right.

18. **Under-tested areas — PARTLY WRONG as stated.** `engine_workbook.py` with no pytest
    coverage: **true**. `FcfEngineInputs.__post_init__` validation errors untested:
    **true**. But "no test asserts the §11.4.2 warning fires" is **false** —
    `test_e2e_dnl_mt.py:103` asserts exactly that. And `EquityBridge.from_anchor` is not
    unit-tested but *is* exercised end-to-end with a pinned per-share outcome via
    `tests/dcf/golden/dnl_mt_inputs.py:67`.

## A6. Schema (Fable 19-20)

19. **FiveForces has no `model_validator`; bank block untyped — CONFIRMED.**
    `industry.py:37-57` — all four force fields Optional with no cross-field check;
    `industry.py:241` `bank_archetype: Optional[Dict[str, Any]]`; `:57`
    `rivalry_subforces: Optional[List[Dict[str, Any]]]`. Grep confirms zero
    `model_validator`/`field_validator` in the file. Fable's "validates strictly" caveat
    is fair.

20. **Silent `archetype=None` fallback — CONFIRMED nice-to-have.**
    `translator.py:173-182` returns `None` purely on file absence, so a typo'd archetype
    id degrades silently instead of raising.

## A7. UI and workbooks (Fable 21-38)

21. **PASS — agreed.** Verified: `gen_ui.py:508-516` short-circuits to `xlsxB64` for all
    three; sliders labelled approximate (`gen_ui.py:47`); `.gitignore:24-27` covers the
    generated files. "No reset-all" is **true** (`#reset` at `gen_ui.py:625` resets only
    the active scenario).
22. **CONFIRMED, and worse in one place.** Assumptions fills `FFF2CC`/font `1F4E78`
    (`engine_workbook.py:51-52`) — DNL 96 input cells, WBC 75, CSL 104. DNL Equity bridge
    carries exactly 14 literals (B10-B19, E11, F17-F19) — all *styled as inputs*, so they
    are deliberate, but they sit off the Assumptions sheet, which still breaches standing
    rule 1. WBC `Multiples!B3 = 35.32` confirmed — and WBC's Assumptions sheet has **no
    market-price row at all**, so there is nothing to link to (DNL and CSL both have one).
23. **FALSE as stated.** `pvsub` is `""` for DNL (`build_cfgs.py:98`) and WBC (`:173`),
    but CSL is populated: `"AUD (USD-functional model, at 0.66)"` (`:247`). The
    *suggestion* (put the gap sentence there for DNL/WBC) is still good.
24. **CONFIRMED — UI suggestion, agree with the recommendation.** `build_cfgs.py:457`,
    `:587` vs `:653`.
25. **CONFIRMED, and the root cause is in the data, not the UI.** `dnl.yaml:348` reads
    `market_reference_price: 3.61  # B110: Wall St target (share price at anchor 3.6061)`
    — the comment says outright it is the *share price*, not a broker target. The UI
    faithfully renders it as both. Fix the data label, then the UI.
26. **CONFIRMED — UI suggestion.** `gen_ui.py:596`.
27. **CONFIRMED — UI suggestion.** `#dlbtn` created only in `detailHTML` for `k==='dcf'`
    (`gen_ui.py:700`); header block `gen_ui.py:34-45` has no download control.
28. **CONFIRMED — UI suggestion,** and the topnotes are additionally dated
    **"Reid Advisory, June 2026"** in all three files.
29. **CONFIRMED — accessibility, and the count is exact.** Bars are click-only divs
    (`gen_ui.py:593-599`); zero `tabindex`/`role`/key handlers anywhere; exactly one
    `aria-label` per file (`gen_ui.py:720`); `markExplore` (`:626`) signals selection by
    `borderColor` alone (WCAG 1.4.1 failure).
30. **PARTLY TRUE.** Fixed 122px label column (`gen_ui.py:594`) and `calc(w% + 6px)`
    (`:596`) confirmed, and overflow is reachable at slider extremes. But the *per-year
    DCF workings* table **is** already wrapped (`gen_ui.py:683`); the unwrapped one is the
    year-by-year transitory-forces table (`:673`).
31. **PARTLY WRONG.** `worldOverrideNote` (`gen_ui.py:680`) **already** shows both values
    ("Value now X vs the assessed Y"). What is missing is the word *approximation*. The
    real problem is bigger and Fable missed it — see Part D item 4.
32. **Tab counts CONFIRMED** (DNL 8, WBC/CSL 6). **Cross-reference claim FALSE as
    stated:** no workbook cross-reference exists in *any* company's UI five-forces panel.
    Inside the workbooks: DNL has the "Ties Revenue growth B41" check row; WBC's five-forces
    sheet hard-codes its impact column as *text*; **CSL has no five-forces sheet at all**.
33-37. **UI suggestions — all sensible, no correctness content. Agreed as backlog.**
38. **CONFIRMED and larger than described.** Dead in practice are `VCCXLSX`
    (`gen_ui.py:68-211`), `VCCBOOK` (`:213-310`) *and* `DNLRICH` (`:312-503`) — ~435 lines,
    **~32 KB inlined into every generated HTML (13-17% of each file)**. The three
    `module.exports` at `:211`, `:310`, `:503` overwrite each other and the node tests they
    were shared with no longer exist.

---

# Part B — prioritised action plan

Nothing here executes without sign-off. Effort is my estimate of *my* working time.
"Base-tie risk" = risk to 3.073 / 30.03 / 203.83 and the 122-test suite.

## Batch 1 — lock the engine before anything moves (do first, one commit)

| # | Item | Effort | Base-tie risk | Depends on |
|---|---|---|---|---|
| 1 | Pin all 18 scenario levels as engine-owned goldens (Fable 16) | 30 min | **None** — assertions only | — |
| 2 | Port the §11.4.2 terminal-share warning to `bank_engine` and `segment_engine`, and add a test that it fires for WBC and CSL (Fable 2, and closes half of Fable 18) | 45 min | **None** — additive field | — |

Rationale: item 1 is the safety net for everything after it. Doing it first means every
later change is provably level-preserving or provably not. Item 2 is additive and free.

## Batch 2 — UI credibility bugs, all cheap, all embarrassing if Ben sees them first

| # | Item | Effort | Base-tie risk | Depends on |
|---|---|---|---|---|
| 3 | **CSL page opens on the broker bar** — `build_cfgs.py:245` `activeIdx:1` selects "Average broker" (136.00), not Muddle Through (203.83). Set to 2, or better, derive the index from `kind=='live'` for all three (Part D item 2) | 15 min | None | — |
| 4 | **CSL broker 136.0 is invented in code** and matches neither data source (`csl.yaml:471` = 138.58 AUD; `financials/csl.yaml:63` = USD 96.75 → AUD 146.60). Pick one, source it from YAML, reconcile the two YAML values (Part D item 3) | 30 min | None | Stephen picks the number |
| 5 | **DNL "broker" bar equals market** because `dnl.yaml:348` is the share price mislabelled as a Wall St target. Relabel the data; drop the DNL broker bar until a real consensus lands (Fable 25) | 20 min | None | — |
| 6 | **DNL slider default is rounded** — `build_cfgs.py:458` sets `def=8.88` vs `cp.re0=0.088772`, so all six DNL bars render an amber "per-scenario discount-rate override" chip that directly contradicts the single-WACC standing rule, and DNL loads at 3.0719 not 3.073 (Part D item 4) | 20 min | None (display only) | — |
| 7 | **Escape user scenario names** before `innerHTML` (`gen_ui.py:594`, `:622`); an `esc()` helper already exists at `:647` (Part D item 8) | 10 min | None | — |
| 8 | Refresh the three topnote dates off "June 2026"; fix `delScenario` `activeIdx` drift (`gen_ui.py:631`) | 15 min | None | — |

## Batch 3 — SSOT and validation hygiene

| # | Item | Effort | Base-tie risk | Depends on |
|---|---|---|---|---|
| 9 | De-duplicate `csl.yaml`: delete the mirrored `normalised_baseline` scalars, keep the rationale prose beside the surviving `segment_fcff` copy (Fable 12, expanded) | 1 h | Low — engine reads `segment_fcff` only; batch-1 goldens catch any slip | Item 1 |
| 10 | Extend the ratchet with a **check 4**: same-file and cross-file duplicate-scalar detection across `data/**/*.yaml` (Fable 12) | 1.5 h | None | Item 9 |
| 11 | `§7.5` anchor-date validator: warn when a company's net debt, share count and discounting date are not struck at one date (Fable 13) — this is the check that would have caught finding 1 | 1.5 h | None (warn-only) | Decision on item 13 |
| 12 | `FiveForces` `model_validator` (one-of-each-force, reject dual-generation conflicts) + typed `BankArchetype` block (Fable 19); make `archetype=None` conditional on an explicit `segment_level_valuation: true` marker (Fable 20) | 2 h | None | — |

## Batch 4 — methodology decisions (Stephen's call; nothing coded until each is decided)

| # | Decision | Value impact (re-derived this session) |
|---|---|---|
| 13 | **CSL valuation-date anchoring.** Either (a) roll net debt/shares forward to 30 Jun 2026 → **c. +AUD 3.4/share (+1.7%)**, or (b) move the valuation date back to 31 Dec 2025 and add an H2-FY26 stub → **−AUD 3.82/share (−1.9%)**. Both defensible; (a) is closer to how DNL does it (`fcf_engine.py:68-103` Period-A walk). | ±2% |
| 14 | **CSL FCFF at Ke vs FCFF at WACC** (Fable 6). Ratify the conservative convention in writing, or build a CSL WACC. Building it takes CSL to **AUD 248-258, +21.5% to +26.6%**, i.e. +135-145% above market. | **+24%** |
| 15 | **DNL reinvestment**: terminal capex = D&A (−0.079) *and* non-zero working capital (−0.14 to −0.27) — Part D item 1. Together **−AUD 0.22 to −0.35/share (−7% to −11%)**, taking DNL's discount to market from −15% to −22%. | **−9%** |
| 16 | **WBC CET1 feasibility check** (Fable 8): warn-only first (payout implied by retained earnings vs AIEA growth × RWA density), forced payout cut under stress as a second step. Warn-only has zero base-tie risk. | 0 initially |
| 17 | **CSL `net_interest_*` fields**: delete (my recommendation, if 14 stays FCFF) or wire (if 14 moves to FCFE). | 0 |
| 18 | **Market-price refresh** for all three (all dated 2026-06-15). Affects every "vs market" number on every page and the §16.3 story. | display only |

## Batch 5 — UI improvements (after Batch 2, before sending to Ben)

19. Fable 23/24/26/27/28 in one `build_cfgs` + `gen_ui` pass (headline sub-caption, metric-4
    consistency, "% vs MT" on bars, persistent header download, provenance chip).
20. Fable 29/30 (keyboard + screen-reader access, narrow-width fixes) — genuinely worth
    doing; the file is currently unusable by keyboard.
21. Fable 31 reframed: the DCF panel does not respond to sliders at all while claiming it
    is "straight from the production engine" (Part D item 5). Fix the caption first, the
    behaviour second.
22. Fable 32-35 (tab parity, narrative teaser, "how to read this" strip, CSL gap panel)
    — after 14 and 18 are decided, since 35 depends on both.

## Batch 6 — housekeeping (one commit, last)

23. Fable 3 (dead FX branch → raise), 5a-d (cosmetics), 9 (align §7.2 stub text), 15
    (finish the Derivation set), 18 (workbook-builder tests, `__post_init__` tests),
    38 (delete the three dead JS writers, ~32 KB per file), plus the stale literals in
    `build_cfgs.py` source (Part D item 9) and the dead `beta.mock` flag.

**Suggested execution order: 1-2, then 3-8, then 9-12, then Stephen's 13-18, then 19-22,
then 23.** Batches 1-3 and 6 are mechanical and carry no methodology risk. Batch 4 is
where the actual thinking is.

---

# Part C — what Fable got wrong or overstated

1. **Finding 1's magnitude is roughly double the truth, and its framing invites the wrong
   fix.** Fable: FY26 FCFF is "USD 3,746m ≈ AUD 11.9/share" and "roughly half a year of
   cash generation (~USD 1.5-2bn, ~AUD 5-6/share) is silently lost". Neither number is a
   value impact. Excluding FY26 is *correct* under a 30 Jun 2026 valuation date — that
   cash is already in the FY26 balance sheet, not lost. Re-derived, the two self-consistent
   repairs give **−AUD 3.82 (−1.9%)** (pull the valuation date back to 31 Dec 2025 and add
   an H2 stub: the extra half-year of discounting on a 75%-terminal valuation costs more
   than the stub adds) or **c. +AUD 3.4 (+1.7%)** (roll net debt forward — and Fable's roll
   forgets that the walk must also subtract the interim dividend and after-tax interest,
   which is where its USD 1.5-2bn becomes about USD 1.0bn). The defect is real; it is not
   "the only item that could move a headline number materially".

2. **Finding 10 states the direction of finding 6 backwards.** Fable writes "findings 1
   and 6 both push CSL *down* — if either resolves upward the gap widens further", two
   paragraphs after correctly identifying the FCFF-at-Ke bias as *conservative*. Fixing 6
   pushes CSL **up 21.5-26.6%**, to +135-145% above market. Finding 1 is ambiguous in sign
   and worth ±2%. The review's own recommended fix order is built on this error: it puts
   finding 1 first ("the only item that could move a headline number materially") and
   finding 6 fifth, when finding 6 is roughly **twelve times** the value impact.

3. **Finding 6's magnitude is understated.** "Perhaps +8-15% on EV" — re-derived, it is
   +21.5% to +26.6% on the per-share value across a 4.5-5.5% pre-tax cost-of-debt range.
   The gap comes from the terminal: at g = 3.0%, moving Ke 8.75% → WACC 7.74% widens
   (k−g) from 5.75% to 4.74%, and the terminal is 75% of EV.

4. **Finding 18's warning claim is simply false.** "No test asserts the §11.4.2 warning
   fires" — `test_e2e_dnl_mt.py:103` does. And `EquityBridge.from_anchor` is not
   *unit*-tested but is exercised end-to-end through
   `tests/dcf/golden/dnl_mt_inputs.py:67` with a pinned per-share outcome, so the walk
   arithmetic is not unprotected.

5. **Finding 23 is wrong on the facts.** CSL's `pvsub` is populated
   (`build_cfgs.py:247`), not `""`. The suggestion still holds for DNL and WBC.

6. **Finding 32's cross-reference claim is wrong as stated.** No company's *UI*
   five-forces panel carries a workbook cross-reference. The DNL-only artefact is in the
   *workbook*. And the more useful version of this finding is that CSL's workbook has no
   five-forces sheet at all, which Fable didn't say.

7. **Findings 30 and 31 are each half wrong.** The per-year DCF workings table is already
   `overflow-x` wrapped (`gen_ui.py:683`); the unwrapped one is a different table (`:673`).
   `worldOverrideNote` already shows both the override value and the assessed value; the
   missing word is "approximation", not the number.

---

# Part D — material issues Fable missed

Ordered by how much they matter.

1. **DNL assumes zero working capital — in every explicit year *and* the terminal.**
   `build_engine_inputs_from_data` produces `delta_wc = [0.0]×5` and `delta_wc_stub = 0.0`,
   so `fcf_engine.py:354` books nothing. DNL grows revenue at 6.15% p.a. from 3,609 to
   4,583 (AUD m) as an industrial explosives manufacturer carrying receivables and
   inventory, and invests nothing to fund it. At CSL's own 10%-of-revenue-change
   convention this is worth **−AUD 0.271/share (−8.8%)**; at 5%, **−AUD 0.136 (−4.4%)**.
   Fable noticed "no terminal ΔWC" as a clause inside finding 7 and valued the *terminal
   capex* wedge at −0.079 — but the working-capital hole is two to three times larger and
   runs through the whole forecast. Taken together DNL's reinvestment treatment is worth
   **−7% to −11%**, which moves the discount to market from −15% to about −22%.

2. **The CSL page opens on the wrong bar — the headline reads 136.00, not 203.83.**
   `build_cfgs.py:245` sets `activeIdx:1`, but `segment_pack` orders bars
   `[upside, broker, live, downs…]` (`:423-427`), so index 1 is "Average broker".
   DNL and WBC correctly use 2 (`:94`, `:171`). On load, `selectScenario(1)`
   (`gen_ui.py:1002 → :605`) selects the broker line, greys out the sliders, and the
   "Value per share" card shows **136.00**. `activeIdx` is never recomputed after
   `csl["scenarios"] = _sp["bars"]` (`:652`). For the one company whose headline is the
   whole story, the page currently shows consensus instead. Related: `liveIdx` is dead
   config, never read by `gen_ui.py`.

3. **The CSL broker number is invented in code and contradicts both data files.**
   `build_cfgs.py:245` hard-codes `broker: 136.0`. `csl.yaml:471` says
   `sell_side_consensus_target_aud: 138.58`; `data/financials/csl.yaml:63` says
   `consensus_target_usd: 96.75` which at the model's own FX of 1.5152 is **AUD 146.60**.
   Three numbers, none agreeing — and the two YAML values are inconsistent with each other
   before the code even gets involved. The ratchet cannot catch this: it only searches for
   literals that *exist* in the YAML register, so a value invented in code is invisible to
   it. That is a second, distinct hole in check 3 alongside the intra-YAML one Fable found.

4. **DNL's discount-rate slider default is rounded, which silently violates the
   single-WACC standing rule on screen.** `build_cfgs.py:458` sets the slider default to
   `round(wacc*100, 2) = 8.88` while `cp.re0 = 0.088772`. Two consequences: DNL renders
   3.0719 at load (hidden at 2 dp, but "vs market" reads −14.91% against the engine's
   −14.88%); and the per-scenario override test at `gen_ui.py:595`
   (`Math.abs(vals.re - singleWacc) > 1e-9`) is true for **all six** DNL bars, so every one
   carries an amber "per-scenario discount-rate override — differs from the single WACC"
   chip. WBC (8.05) and CSL (8.75) round exactly and are unaffected.

5. **The DCF panel is static but claims to be live.** `dcfIntro`, `dcfRows` and
   `workingsHTML()` (`gen_ui.py:681-689`) are fixed CFG data. Move any slider and the
   headline becomes the reduced-form value while the build-up below still shows the engine
   path — under the caption "Straight from the production engine — the same per-year build
   behind the headline and the downloadable workbook" (`:688`). That caption becomes false
   at the first slider drag. This is the real version of Fable's finding 31, and it is a
   bigger threat to the one-source-of-truth story than the missing "(approximation)" label.

6. **DNL's two DCF views disagree by AUD 154m of enterprise value.** The narrative view
   shows EV 7,009 (ties the workbook); the DCF-table view computes
   `ev = per*CFG.shares + CFG.netDebt` (`gen_ui.py:942`) = **6,855**, omitting the AUD
   152m equity-bridge adjustment. One click apart, same scenario. Its "Tie check:
   reconstructed EV vs headline EV" (`:968`) is tautological — the reconstruction is
   back-solved from `ev` at `:944-946`, so Δ can never be non-zero. Near-term FCFF growth
   is also hard-coded `gr=5` for every company and scenario (`:941`).

7. **Cross-company text leak on the CSL page.** `gen_ui.py:782` hard-codes
   "re-lever at **DNL** gearing D/E" in the non-bank branch of the β workbench. WBC escapes
   it only because `beta.bank` is true; CSL renders the DNL label. The string is present in
   all three generated files.

8. **Stored self-XSS via user scenario names.** Names come from `prompt()`
   (`gen_ui.py:629`), are truncated to 40 chars but never escaped, are injected with
   `innerHTML` at `:594` and `:622`, and persist in `localStorage` (`:563`) so they
   re-execute on every load. An `esc()` helper exists at `:647` and simply is not applied.
   Low severity for a self-inflicted local file, but it is a shared artefact.

9. **`build_cfgs.py` source still carries the superseded numbers.** `:92-100` has
   `cp.base 3.48`, `re0 0.0868`, `shares 1884`, `netDebt 1512`, metric4 `4.05×` and a
   footnote reading "Calibrated central case: DNL Muddle Through AUD 3.48"; `:171-175` has
   WBC at 30.15 and `1.90×`. I verified the `*_pack` functions overwrite all of these
   before output (generated cfg reads 3.073 / 30.03 / 1770 / 1418 / 4.2× / 2.00×), so
   nothing is *currently* wrong on screen — but a stale headline number sitting in a
   source literal one edit away from being rendered is exactly the trap the SSOT protocol
   exists to prevent.

10. **All three market prices are two months stale, not just CSL's.** DNL, WBC
    (`wbc.yaml:807-809`) and CSL (`csl.yaml:466-467`) are all struck at **2026-06-15**.
    Fable raised it only for CSL.

11. **WBC's Assumptions sheet has no market-price row,** which is why `Multiples!B3`
    hard-codes 35.32 — the fix Fable proposes ("link it to an Assumptions input row")
    requires adding the row first. DNL and CSL both have one.

*Checked because they looked wrong, and are not:* the WBC AT1 treatment (no double-count —
see A2 item 8); the CSL FX application point (per-share line only, `segment_engine.py:149`);
the single-Ke/single-WACC discipline (tested and holds across all six scenarios in all
three engines); and the embedded workbooks (recalculated headless — zero error cells, every
scenario ties).

---

# Part E — questions for Stephen before anything starts

1. **Batch 4 item 14 (CSL FCFF at Ke vs WACC)** is the largest open item in the project
   at +24%. Ratify the conservative convention in the methodology doc, or build the WACC?
2. **Batch 4 item 13 (CSL anchoring)** — roll net debt forward to 30 Jun 2026 (+1.7%), or
   move the valuation date back to 31 Dec 2025 with a stub (−1.9%)?
3. **Batch 4 item 15 (DNL reinvestment)** — do you want the working-capital assumption
   revisited at all? It is −4% to −9% on 3.073 and it changes the audited workbook, not
   just the engine.
4. **Batch 2 item 4** — which CSL broker number is right: 138.58, 146.60 (from USD 96.75),
   or something current?
5. **Market-price refresh** — do you want me to source current prices for all three, or is
   the 15 June 2026 snapshot deliberate (a fixed valuation date)?
6. **Batch order** — happy with 1-2 → 3-8 → 9-12 → your calls → 19-22 → 23, or would you
   rather I take the methodology decisions first and rebuild once?
