# UI design brief — the scenario-valuation interface (v1)

**Date:** 25 June 2026. **Author:** Stephen + Claude. **Status:** design brief for the next build.
**Reads with:** the "Interface prototypes" section of `WORKING_NOTES.md` (the locked concept and the
three prototypes in `ui_prototypes/`). This brief extends that concept into an interactive
modelling tool, captured from Stephen's 10-point brief and the design conversation of 25 June.

---

## The shift this brief makes

The current prototypes are an **illustrative viewer**: fixed scenarios, sliders that approximate.
This brief turns the interface into a **live modelling workbench** — the user defines their own
scenario, overrides any input, and expects the outputs to move correctly. A viewer can fake its
numbers; a workbench cannot. That single change drives most of the decisions below.

Two cross-cutting principles agreed with Stephen:

1. **HTML is the contract.** Keep building in self-contained HTML for now. When Stephen is happy
   with it, the prototype IS the spec — the eventual engine build just has to reproduce its
   behaviour and serve its data shapes. Design the HTML and its data files as if they define the
   build contract.
2. **Global value + per-scenario overrides is the universal input model.** Every input has a
   global/base value; a user scenario stores only the deltas it changes off Muddle Through. This
   mirrors the scenario-comparison workbooks (a shared base plus a per-scenario override column),
   so the UI model and the engine model are the same shape. Point 4 (Rf global or per-scenario) is
   just this general rule applied to one input.

---

## Workstream A — interaction and layout

1. **Detail renders below, not at the top.** When a user clicks "explore the inputs", the revealed
   detail appears below the trigger, in place — not jumping to the top of the screen. This also
   establishes the pattern: the "explore the inputs" panels become the editing surface, not just a
   reveal.

## Workstream B — user-defined scenarios (the core interactivity)

2. **"+" to add a user scenario.** Alongside the world scenarios and the Average Broker bar, a "+"
   button lets a user add their own scenario, which they name. It starts from Muddle Through
   settings, and the user changes elements as they move through the "explore the inputs" tabs. The
   new scenario appears as another bar/outcome next to the built-in ones.
3. **Per-input overrides everywhere.** On the Company-v-Industry page, add an editable **Impact**
   column so a user can change the assessment for their scenario. Apply the same override logic to
   **every** input across all "explore the inputs" tabs.
4. **Discount rate: global and per-scenario settings.** The user can change discount-rate elements
   both globally (e.g. set Rf = 4.5% across the board) and per-scenario (a different Rf for one
   scenario). Same for every discount-rate component.
5. **Assumptions list is editable.** In the assumptions view, a user can change inputs for their own
   scenario(s) — either across all scenarios (a global change) or by scenario (an override). This is
   the general global-vs-override model applied to the full input list.

**Editable-input scope — layered by impact.** A valuation has dozens of inputs but only a handful
move the answer (the "top 5 drivers"; Behring near-term growth barely moves value). Surface the
high-impact inputs up front where they are easy to find and change; tuck the long tail of low-impact
inputs behind an "advanced / show all inputs" reveal. Both available; nothing hidden from a user who
wants full control.

**Compute fidelity.** When a user overrides inputs, the outputs recompute via a **faithful
browser-side reduced-form** first — it reproduces the workbook maths for the value-material inputs —
with the real engine (build-plan steps 6+10) swapped in later. Agreed near-term approach.

**Excel download.** A user can download their scenario to Excel at any time, as a **formula
workbook** (inputs on an Assumptions sheet, everything else linked) per the workbook-discipline
standing rule — a live, traceable model they keep flexing, not a dead snapshot. This also serves as
the real save/portability mechanism until there is a backend.

**Persistence.** Browser-only (localStorage) for now. Caveat: localStorage is per-browser and
per-device and clears if the user clears browser data — fine for a prototype, not a real save; the
Excel download covers real portability in the meantime.

## Workstream C — deeper context and theory (content wiring; low compute risk)

6. **Longer world-scenario descriptions**, drawing on the full write-ups in `data/scenarios/*.md`
   rather than the current short blurbs.
7. **Richer Company-v-Industry Five Forces drill-down**: show how the *industry* fares under each of
   the five forces (the industry-level rating and impact) AND how the *subject company* sits within
   the industry, drawing more on `data/industries/`.
8. **Fuller company-position detail**, drawing more on `data/companies/`.
9. **Discount-rate theory click-throughs.** For each element of the discount-rate build-up, a user
   can click through to practical theory, grounded in the IER appendices now preserved at
   `design/reference/discount_rate_iers/` (Realm Resources; Oil Search / Santos scheme booklet;
   Universal Coal target's statement; Woodside / BHP Petroleum). Set out the *proper* approach and
   *what we actually did* side by side — e.g. the risk-free rate should properly be a zero-coupon
   government bond; note what we used and why.

## Workstream D — cost-of-capital / beta workbench (its own module)

The most substantial and most data-dependent module. From Stephen's point 8:

- (a) **Rf** — global-or-per-scenario override (per Workstream B / point 4).
- (b) Click through to see the **beta for the subject company and each comparable**.
- (c) Click through to see **why each entity is considered comparable**.
- (d) **Add** other companies to the comparables list.
- (e) **"Find more comparables"** — start a process that surfaces further candidates *with a
  rationale* for why each could be comparable, and an option to select them for inclusion.
- (f) **Deselect** companies from the comparables set.
- (g) Note the **index** each comparable's beta is calculated against; let the user select/change it.
- (h) Click through to a **scatterplot** of the beta calculation.
- (i) Beta over **different estimation periods**, user-changeable — start with weekly data over 2
  years and monthly data over 4 years.
- (j) Let the user add an **alpha** into the discount-rate build-up.
- (k) Show **levered and unlevered betas** for the comparables; let the user select an unlevered beta
  and a gearing level (relever) if that is how they want to do it.

**Data approach (agreed):** one source, cached, shipped as a JSON data contract.
- **Source: EODHD** (Ben's pipeline; ASX-licensed; covers the global peers and indices; provides EOD
  price series plus gearing and tax for unlevering).
- **Cadence: cached snapshots, not live.** Betas over 2-4 year windows do not move day to day.
  Pre-compute the return series and betas offline and ship as static JSON the HTML loads — keeping the
  prototype self-contained and making the JSON the exact spec of what the engine must later produce.
  The scatterplot plots the stored (index-return, stock-return) pairs; the weekly/2yr vs monthly/4yr
  toggle switches between two pre-computed datasets; levered/unlevered comes from stored gearing + tax.
- **Indices, keyed to valuation currency:** ASX names (DNL, WBC) — S&P/ASX 200 plus MSCI World; USD
  names (CSL) — S&P 500 or MSCI World. Methodologically important: CSL's measured beta of 0.094 was
  unreliable because it regressed an AUD-listed price against an AUD index; letting the user pick a
  USD/global index makes the correct calculation visible and ties to the point-9 theory.

**This module is the pilot for the AI-vs-mechanical boundary** (Stephen's second workstream): the
regression and the relevering are *mechanical*; the comparable *selection and rationale*, and 8(e)
"find more comparables", are *judgment / AI*. Building it forces that decision in a tangible place.

---

## How this relates to the two planned workstreams

Stephen's plan was: build out the UI, then decide where the programming allows AI input vs is
mechanical. This brief shows the two blend: Workstreams **A** and **C** can proceed independently
(layout + content wiring). Workstreams **B** and **D** need the compute/data layer, so they surface
the engine (steps 6+10) and the AI/mechanical boundary directly. Workstream D is the natural first
place to make the boundary decision concrete.

## Open questions to resolve in the build

1. **Reduced-form fidelity** — the tolerance to which the browser calculator must match the
   workbooks for the value-material inputs.
2. **High-impact input set per company** — which inputs sit "up front" vs behind "advanced" (partly
   defined by the existing top-5-driver lists per company).
3. **Beta JSON data-contract spec** — exact fields, the two estimation windows, index options,
   gearing/tax for unlevering.
4. **Long-term delivery target** — HTML now; the locked decision was to embed in the VCC dashboard
   eventually. Point 8's data + regression needs are what will eventually push past a static file.
5. **Build sequence for the next chat** — suggested order: A (layout) + C (content) as low-risk
   starters that make the prototypes richer immediately, then B (user scenarios + reduced-form +
   Excel download), then D (beta workbench) as the flagship.

---

## Reference material preserved

- `design/reference/discount_rate_iers/` — the four IERs Stephen provided, source for the point-9
  discount-rate theory (proper approach + what we did): Realm Resources; Oil Search / Santos scheme
  booklet; Universal Coal target's statement; Woodside / BHP Petroleum.
- `ui_prototypes/` — the three current prototypes (csl / dnl / wbc) and the `_generator/`.
- `analyses/csl/valuations/csl_scenarios_comparison_v2.xlsx` — CSL now has a full six-scenario set,
  so its interface bars can be made real like DNL/WBC (the csl_ prototype still shows placeholders).
