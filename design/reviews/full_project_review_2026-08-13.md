# VCC Valuations — full-project review (13 August 2026)

Fresh-eyes critical assessment of the project to date, per the 12 Aug review brief.
Assessment only; no code changed. Reviewer: Claude (Fable 5), Cowork session.

**Verification performed before writing this report:**

1. Suite green at HEAD `d0cdaf7`: 122 passed, SSOT ratchet 8 passed.
2. All three engines re-run from data in this session: DNL six scenarios reproduce
   (OC 3.562 / MT 3.073 / AIPL 2.985 / Frag 2.222 / DClim 1.177 / Stag 1.019); WBC
   six reproduce (35.71 / 30.03 / 29.70 / 27.11 / 22.58 / 18.65); CSL six reproduce
   (MT USD 134.52 / AUD 203.83; OC 237.29 … Stag 159.90 AUD).
3. `build_cfgs.py && gen_ui.py` rebuilt cleanly; all three HTMLs carry engine bases
   (3.073 / 30.03 / 203.83) and an embedded base64 workbook.
4. The three embedded workbooks were decoded and recalculated headless in LibreOffice:
   every scenario line ties the engine output exactly (DNL 3.073/EV 7,009.2; WBC
   30.0304/ordinary equity 102,550.8; CSL 134.5216/203.8271). Workbook discipline
   checked cell-by-cell (fills, fonts, formula-vs-literal counts).

Findings are numbered continuously so you can reply by number. Each is tagged
**MUST-FIX**, **DECIDE** (owner call needed), or **NICE**.

---

## A. Correctness bugs

**1. CSL drops FY26 free cash flow entirely, with no Period-A walk and no anchor
date on net debt — potentially several AUD/share. MUST-FIX (or document).**
`segment_engine.py:131-134` sets FY26's mid-time to 0 and its PV to 0, so FY26 FCFF
(engine value USD 3,746m ≈ USD 7.8/share ≈ AUD 11.9/share) contributes nothing.
That is only correct if the valuation date is FY26-end (30 Jun 2026) *and* net debt
is measured at that same date. But `data/companies/csl.yaml:655` (`net_debt: 9100`)
carries no `as_at_date` (§7.5 anchor-date discipline not applied), and there is no
§7 Period-A walk rolling it to the valuation date — unlike DNL, where
`EquityBridge.from_anchor` (`fcf_engine.py:68-103`) does exactly this. If 9100 is
the 1H26 (31 Dec 2025) balance, roughly half a year of cash generation (~USD 1.5-2bn,
~AUD 5-6/share) is silently lost between anchor and valuation date. The DNL and WBC
builds handle timing explicitly (stub + walk); CSL is the odd one out. Confirm what
date 9100 is struck at; if Dec-2025, add the walk or restate the anchor.

**2. Terminal-share warning exists only in the industrial engine, and both of the
other two companies breach the threshold. MUST-FIX (cheap).**
`fcf_engine.py:43,382-388` warns when terminal PV > 70% of EV (§11.4.2 sensitivity
pass). The bank and segment engines have no equivalent — yet WBC's terminal is
76.3% of the total equity claim and CSL's is 75.2% of EV (both computed this
session). The two valuations that most need the §11.4.2 sensitivity pass are the
two that can't emit the warning. Port the warning to `bank_engine.py` and
`segment_engine.py`.

**3. Dead FX branch in the DNL assembler. NICE (latent bug).**
`translator.py:591`: `fx_rate = 1.0 if functional_ccy == reporting_ccy else 1.0` —
both branches are 1.0. Harmless for DNL (AUD/AUD) but the first company that reuses
this path with a genuine FX mismatch will silently get 1.0.

**4. Unused engine inputs: CSL net interest. DECIDE.**
`SegmentInputs.net_interest_fy25` / `net_interest_decline` (`segment_engine.py:45-46`)
are populated from data (`translator.py:764`; csl.yaml `corporate.net_interest_fy25:
-409.5`) but never referenced in `run()`. For *unlevered* FCFF that is arguably
correct (interest doesn't belong in FCFF) — but then the fields shouldn't exist, and
their presence suggests either a leftover FCFE intention or a workbook line the
engine doesn't reproduce. Delete them or wire them, and note which the audited v4
workbook does.

**5. Cosmetics: (a) `build_cfgs.py:697` prints "cfgs.json written" but writes
`cfgs_gen.json`; `gen_ui.py:1081` falls back to `/tmp/cfgs.json`. (b) Dead code in
the legacy smoke translator: `translator.py:852-857` computes a gross-margin base
then unconditionally overwrites it with 0.0. (c) `design/build_plan.html:167` still
says "Owner: Tara Reid" (the known leftover). (d) `WORKING_NOTES.md:43` says "Suite
113" in the ALL-THREE-COMPLETE header while the file elsewhere says 122. All NICE.**

---

## B. Methodology concerns

**6. CSL discounts unlevered FCFF at the cost of equity, then deducts net debt.
DECIDE — this is internally inconsistent and a reviewer will flag it.**
`segment_engine.py` docstring (lines 3-5) is candid: "discount unlevered free cash
flow to the firm at the cost of equity". The consistent pairs are FCFF↔WACC or
FCFE↔Ke. FCFF at Ke *then* subtracting USD 9.1bn net debt double-charges the debt:
the discount rate already prices an all-equity claim, and the bridge then removes
debt again. The bias is conservative but not trivial: at market values CSL's D/V is
~20% (USD 9.1bn debt on a ~USD 33bn market cap), so a consistent WACC would sit
roughly 50-100bps below the 8.75% Ke — worth perhaps +8-15% on EV — and the
framework's own §3.5 discipline is "one discount rate *matched to the cash-flow
definition*". Either (a) ratify explicitly as a deliberate conservative convention
in the methodology doc (§15-style fork note for segment companies), or (b) build a
CSL WACC. Right now the justification lives only in a code docstring.

**7. DNL's terminal value capitalises an unsustainable steady state. DECIDE.**
`fcf_engine.py:368-376` grows last-year FCFF at g with terminal capex 7.0% of
revenue vs D&A 7.3% (session recalc) and no terminal ΔWC. Capex < D&A in perpetuity
means the asset base runs down while revenue grows at 2.5% — the wedge (~0.3pp of
revenue in perpetuity ≈ AUD 0.08/share discounted, ~2.5% of the 3.073) flatters DNL. The CSL engine fixes
exactly this (binding terminal margin, terminal capex = D&A, terminal ΔWC = g×wc;
`segment_engine.py:136-141`) — the code comment at `fcf_engine.py:369-371`
acknowledges the divergence. The engine correctly matches the audited workbook, so
this is a *workbook* methodology gap, not an engine bug. Recommend: back-port the
CSL terminal treatment to the DNL methodology (and workbook) or ratify the current
form with a one-line rationale.

**8. Bank engine implements §15.2/§15.3/§15.8 but not §15.5 (CET1). DECIDE.**
`bank_engine.py` has no capital constraint: payout is a constant 0.75
(`bank_engine.py:135`) with no check that retained earnings fund AIEA growth × RWA
density (§15.5(c) forecast mechanics), and no forced-payout-cut under stress — the
precise channel §15.5 says matters most in downside worlds (Stagflation NPAT falls
~57% yet payout stays 75%). Also: terminal payout implied by the TV formula is
1 − g/ROE = 66.7% vs the explicit-period 75% — a small step at the boundary; and
"ROE fade" is a single terminal ROE input (10.5% vs Y5 implied 10.89%), not a fade
path. None of this breaks the MT tie, but under stress scenarios the dividend
stream is arguably overstated. At minimum add a CET1 feasibility check that warns.

**9. Stub construction diverges from the written methodology. NICE (align text).**
§7.2 says stub FCF is "pro-rated from the next full fiscal year's forecast"
(`equity_bridge_and_valuation_mechanics.md:658`). The engine pro-rates the *base*
year: `fcf_engine.py:329` (`base_year_revenue * stub_years`, at base margin, stub
tax, stub capex). The engine matches the audited workbook, so the methodology text
is what's wrong (or the workbook is). Align one to the other.

**10. CSL sits 93% above market — §16.3 discipline applies. DECIDE.**
Model MT AUD 203.83 vs market 105.53 and broker 136 (cfgs_gen). The footnote
acknowledges the gap, but §16.3 ("when the framework central case sits above
market") requires the structural-reason treatment, and the pattern across companies
(DNL −15%, WBC −15%, CSL +93%) is exactly the asymmetry a sceptical reviewer will
probe first. Two sub-checks: (a) confirm 105.53 is the *current* price, not stale;
(b) note that findings 1 and 6 both push CSL *down* — if either resolves upward the
gap widens further. A dedicated "why we differ from the market" panel for CSL
(payor-pressure structural story vs our through-cycle plasma view) would front-run
the obvious challenge.

**11. β peer triangulation: honoured in form; DNL's evidence base is mock. DECIDE.**
The §3.5.3 discipline (peer set, outliers named, franchise reasoning) is genuinely
followed for all three (dnl.yaml:489-493 ratified 1.10; csl.yaml discards the
measured 0.094 with the right currency-mismatch reasoning; WBC uses the CBA/NAB
cluster with ANZ/MQG excluded per §15.2(b)). But DNL's peer dataset is flagged
`"mock": True` (`beta_data.py:37`) — the workbook labels it MOCK (good,
`engine_workbook.py:573`), yet the *ratified* β 1.10's triangulation narrative
cites those mock peers. The decision record should state which parts of the
triangulation rest on real observations and which await Ben's feed. The
DM-inflation basis (chain 2.5% vs scenario 3.0% CPI) is documented-deferred in
dnl.yaml — acceptable as a parked owner decision; no action beyond the existing note.

---

## C. Data integrity / single source of truth

**12. csl.yaml stores the same layer-2 judgment twice — the exact defect the SSOT
protocol targets, and the ratchet can't see it. MUST-FIX.**
Duplicates: (a) `segment_baseline` (csl.yaml:612-634) restates the MT growth paths
and margin uplifts that also live in `segment_fcff.by_scenario.muddle_through`
(csl.yaml:670-676) — same vectors, two homes; (b) `corporate_unallocated_fy25:
-2559` at csl.yaml:514 *and* csl.yaml:645; (c) `capex_pct_revenue: 0.045` at
csl.yaml:520 and :651; (d) `terminal_capex_pct_revenue: 0.06` at :531 and :653.
The engine reads only `segment_fcff`, so the other copies are silently-stale
mirrors. The ratchet misses this because check 3 scans only *code*
(`test_ssot_lint.py:46` SCAN_GLOBS) — intra-YAML and cross-block duplication isn't
linted. Fix: delete the non-engine copies (keep the rationale prose next to the
surviving copy) and extend the lint with a same-file duplicate-scalar check.

**13. Anchor-date discipline (§7.5) is enforced nowhere. NICE.**
DNL's financials carry the paired 31-Mar-2026 anchors; CSL's `segment_fcff.anchors`
carry no dates at all (see finding 1); no validator implements the §7.5 "warn if
inconsistent" check listed in §9 item 8. Worth adding when finding 1 is resolved.

**14. Layer-1/layer-2 split: clean where executed. PASS.**
The wacc/coe observed-vs-method split (`translator.resolve_normalised_baseline`,
financials `coe_observed_inputs` vs companies `coe_method`) is genuinely clean;
stored-derived values (computed_wacc, tax glide) have been correctly hunted out;
the WBC AIEA/NIM chain stores industry anchor + company offset + scenario delta as
separate rows and derives the applied NIM. Checks 1 and 2 of the lint hold. The
one structural constant in data (`aiea_y1_time_factor: 1.18`) is documented.

---

## D. Traceability

**15. The Derivation layer covers the bridges well but the per-year build thinly.
NICE.**
`per_year_derivation` on all three engines emits only revenue/EBIT/FCFF (or
TOI/NPAT/dividend) per period, with mostly empty `inputs` dicts
(`fcf_engine.py:466-473`, `bank_engine.py:184-190`, `segment_engine.py:173-180`) —
no tax, D&A, capex, ΔWC, or discount-factor steps, and the bank `derivation()`
omits the whole AIEA→NII build. The generated *workbooks* show all of those rows,
so the workbook currently explains more than the engine can. If the Derivation
objects are meant to be "the workbook rows" (the #2 design idea), finish the set:
one step per P&L line per period, inputs populated.

---

## E. Test quality

**16. The six-scenario levels are pinned nowhere — only MT. MUST-FIX (cheap).**
MT per-share is pinned to the independently-authored analyses/ workbooks for all
three companies (good, non-circular). But the five non-MT values are asserted only
by *ordering* (`test_wbc_bank.py:44-50`, `test_csl_segment.py:38-46`; DNL pins
drivers, not levels, `test_dnl_all_scenarios.py:60-68`). A regression that shifts
every non-MT level while preserving order passes the suite, and the UI/workbook
numbers drift silently. Since these levels are now engine-owned (they superseded
the stale-β comparison workbooks), pin all 18 as regression goldens with a comment
that they're engine-owned, not workbook-owned.

**17. Golden circularity: correctly avoided for MT; be precise in the claims.
PASS with caveat.** The generated (embedded) workbooks recalc-tie the engine *by
construction* — same source, so that's a consistency check, not an audit. The
independent oracle is the hand-built analyses/ workbooks, and only for MT. Nothing
wrong here, but "every one tying its audited workbook" (WORKING_NOTES) should be
read as: MT independently audited; the other five self-consistent. Also the
LibreOffice recalc tie runs only ad hoc (I re-verified it this session) — worth a
CI job or a scripted check (`tests/dcf/golden/_recalc.py` exists but isn't a
suite gate).

**18. Under-tested areas. NICE.** `engine_workbook.py` (1,467 lines, all three
workbook builders) has no pytest coverage; `EquityBridge.from_anchor` walk
arithmetic and the input-validation errors (`FcfEngineInputs.__post_init__`) are
untested; no test asserts the §11.4.2 warning fires (and finding 2 means it
can't for two engines); the reduced-form JS (`computeVals`) is checked only by
`node --check` (syntax), not by a numeric tie test against `CFG.base`.

---

## F. Archetype fork + §7.4-v2 schema

**19. The additive relaxation did weaken validation — the docstring's own rule
isn't enforced. DECIDE (small fix).**
`FiveForces` (industry.py:37-57) makes both naming generations optional and says
"at least one form of each force is expected" — but there is no `model_validator`,
and I verified empirically that a five-forces block with *neither* entrants nor
substitutes (in either naming) validates. You can also supply both generations of
the same force with contradictory ratings. And `bank_archetype: Dict[str, Any]`
(industry.py:241) plus `rivalry_subforces: List[Dict[str, Any]]` are untyped
escape hatches — the bank-specific content that motivated the v2 evolution is the
one part not actually validated. "All five archetype files validate strictly" is
true only for the typed subset. Fix: one `model_validator` enforcing
one-of-each-force and rejecting dual-generation conflicts, plus a typed
`BankArchetype` block. Otherwise the fork pattern itself (strict + additive,
branch on `archetype_class`) is sound and proved out three times.

**20. CSL loads with `archetype=None` — documented, but the fallback is silent.
NICE.** `translator.load_inputs:173-182` returns `None` when the file is absent.
Fine for CSL today (segment engine reads `normalised_baseline`), but a typo'd
archetype id for any *other* company would silently produce `archetype=None`
instead of an error. Make the None-fallback conditional on an explicit marker
(e.g. company declares `segment_level_valuation: true`) rather than file absence.

---

## G. Standalone UI + base64 workbook approach

**21. The architecture is right and the discipline held. PASS.**
Pre-computing everything engine-side and embedding the workbook keeps the static
file downstream of the one engine — the standing "no JS engine port" decision is
respected (the in-browser writer is only a fallback and the sliders are labelled
approximations). The gitignore/untrack call for the generated HTML/cfgs is correct
(100k-char base64 lines would poison diffs; source-only tracking is the right
trade). Residual risks, all acceptable for a feedback prototype: (a) the embedded
workbook goes stale the moment data changes — mitigated by rebuild-on-generate;
(b) `localStorage` user-scenarios persist per browser profile and may confuse a
reviewer who reopens a shared file after fiddling (an explicit "reset all" would
help); (c) the reduced-form slider model can produce values that contradict the
engine bars for large moves — see UI item 31.

**22. Workbook discipline in the embedded books: honoured with named exceptions.
NICE.** Assumptions sheets are uniformly yellow-fill (FFF2CC) blue-font inputs;
derived sheets are formula-linked (verified by literal-count audit). Exceptions:
DNL Equity bridge sheet carries 14 numeric literals (the §4.2 adjustments detail,
B10-B14 etc.); WBC Multiples B3 hard-codes the market price 35.32 (should link to
an Assumptions input row); the peer/mock sheets carry labelled-MOCK literals
(acceptable). Industry-baseline vs company-offset separate-row rule: verified
present in DNL Revenue growth and the WBC AIEA-NIM chain.

---

## H. UI/UX suggestions (scenario interfaces — prioritised, quick wins first)

All implementable in `build_cfgs.py` (content) / `gen_ui.py` (scaffold + JS).
Quick wins (a few lines each):

**23. Use the empty headline sub-caption to land the story in 5 seconds.** `pvsub`
is `""` for all three companies. Put the gap sentence there, engine-sourced:
"15% below market · downside skew 4.2×" (DNL). Right now the reader must scan four
metric cards and infer the punchline.

**24. Make metric 4 consistent across companies.** DNL/WBC show "Asymmetry
(down/up)", CSL shows "Terminal % of value". CSL's asymmetry is genuinely
different (upside-light, downside-clustered) — that's information, not a reason to
swap the metric. Show asymmetry for all three; move terminal-share into the
Discount-rate / build-up panel (where it belongs with the §11.4.2 warning — and
per finding 2 it *should* be displayed for WBC/CSL, both >70%).

**25. Label the dashed market line inline.** The dashed vertical in the bars chart
is explained only in a small legend below; put "market 3.61" at its top. Add the
broker marker's value likewise. Also: DNL's broker bar (3.61) exactly equals the
market price — if that's a placeholder rather than a real consensus target, drop
the bar for DNL; a broker bar identical to market reads as an error.

**26. Add "% vs MT" beside each scenario bar value** (e.g. "2.22 · −28%"). The
per-share deltas are already computed for the narrative; surfacing them on the
chart makes the spread readable without opening any panel.

**27. Persistent download button in the header.** `#dlbtn` currently exists only
inside detail panels (gen_ui.py:644,722), so the workbook — the single most
persuasive traceability artefact — is invisible until a reviewer opens a drill-down.
Put "Download audited workbook (12 sheets, all formulas)" in the top bar, with the
sheet count from cfg.

**28. One-line provenance chip under the header.** "Every number on this page is
computed by the production engine (commit d0cdaf7) from dnl.yaml; the downloadable
workbook recalculates to the same cent." The topnote gestures at this but reads as
a disclaimer, not a feature. This is the "one source of truth" story — sell it.

**29. Keyboard + screen-reader access for the scenario bars.** Bars are click-only
`div`s (drawBars, gen_ui.py:588-604): add `role="button"`, `tabindex="0"`,
Enter/Space handling, and an `aria-label` ("Fragmentation, 2.22 dollars per share,
28 per cent below Muddle Through"). The file currently has exactly one aria-label
(the close button, gen_ui.py:720). The explore tabs likewise need `aria-pressed`;
the selected-tab indication is border-colour only, which fails non-colour
perception — add a background/weight change too.

**30. Narrow-width fixes.** The 122px fixed label column plus the value label
positioned at `calc(w% + 6px)` overflows when a bar approaches 100% of scale on a
~360px screen; move the value inside the bar when w > 80%. The five metric cards
wrap fine (auto-fit minmax 150px) but check the per-year workings table for
horizontal scroll — wrap it in `overflow-x:auto`.

**31. Show the approximation delta at the point of interaction.** When sliders are
at defaults the reduced-form equals the engine (3.072 vs 3.073); when moved, the
value silently becomes a different model's output. The topnote says so, but put it
where the eyes are: when `isOverridden`, append "(approximation — engine value at
assessed inputs: 3.07)" to the override note (worldOverrideNote, gen_ui.py:680).
This protects the one-source-of-truth story you've otherwise been rigorous about.

Medium (an hour or two each):

**32. Equalise the tab set across companies.** DNL has 8 explore tabs; WBC/CSL
have 6 (no Multiples, no Summary financials). To a reviewer flipping between files
the missing tabs read as unfinished rather than data-blocked. Either add the tabs
with an explicit "awaiting peer-financials feed (Ben)" placeholder card — which
also advertises the data dependency — or trim DNL to match. Same for the
Five-forces panel: present in all three but the workbook cross-reference ("ties
Revenue B41") exists only for DNL; add the WBC (AIEA-NIM offset) and CSL
equivalents.

**33. Scenario narrative teaser beside the chart.** The strong per-scenario
narratives (standing rule 2) are buried one click deep in the World panel. On bar
selection, show the first sentence + "why it lands here" under the chart with a
"more" link into the panel. The 5-second story becomes: headline → spread →
selected-world reason.

**34. A "how to read this file" strip for first-time reviewers.** Ben and the
select others get a bare file with no onboarding. A dismissible 3-step strip
("1 pick a world · 2 open its build-up · 3 download the workbook and audit any
cell") targeted exactly at the feedback ask would raise the quality of the
feedback you get back.

**35. CSL gap panel (ties finding 10).** For CSL only, a dedicated card: model
203.83 vs market 105.53 — the three structural reasons, and what would have to be
true for the market to be right (the §16.1 interpretive discipline, rendered).
This converts the scariest number on any of the three pages into the most
persuasive panel.

Larger reworks (only if the prototype graduates):

**36. Print/PDF stylesheet** (reviewers will print it; the dark-mode variables and
flex layouts currently print poorly).

**37. Side-by-side scenario comparison** (pick two worlds, diff their assumption
rows and per-year builds — all data already in cfg).

**38. Replace the hand-rolled store-zip XLSX writer fallback** (gen_ui.py:69-211)
once WBC/CSL are permanently on embedded engine workbooks — it's ~140 lines of
OOXML plumbing kept only for the no-xlsxB64 path, which no company now takes.

---

## I. Recommended fix order

1. Finding 1 (CSL FY26/net-debt anchoring) — the only item that could move a
   headline number materially; resolve before sharing the CSL file for feedback.
2. Finding 10a (confirm CSL market price current) — same reason.
3. Finding 16 (pin the 18 scenario goldens) + finding 2 (port the terminal-share
   warning) — cheap, locks the engine before anything else changes.
4. Finding 12 (csl.yaml de-duplication + intra-file lint) — cheap, closes the SSOT
   hole while it's fresh.
5. Findings 6, 7, 8 (FCFF@Ke ratification; DNL terminal wedge; bank CET1 check) —
   owner methodology decisions; each needs only a paragraph + optionally a warning.
6. Finding 19 (FiveForces validator + typed bank block) — small schema PR.
7. UI quick wins 23-31 in one build_cfgs/gen_ui pass, then 32-35 before sending
   to Ben.
8. Housekeeping: findings 3, 4, 5, 9, 13, 15, 18, 20 as a cleanup batch.

Nothing found invalidates the headline numbers as computed: the engines do what
the workbooks do, to the cent, across all six scenarios and all three companies.
The material questions are timing/anchoring for CSL (1), one discount-rate
convention (6), and terminal-value conservatism (2, 7) — all decidable, none
structural.
