# Forecast horizon, growth fade and terminal convergence

**Status, 25 Aug 2026: PROPOSED, nothing ratified.** Seven decisions are put forward
here (D-35 to D-41). None is in force; no code has moved. The numbers throughout are
sizings from a scratch harness that reproduces `FcfEngine` to 1e-15 on all six live
DNL scenarios, not engine output.

Purpose: settle how long the explicit forecast period runs, what happens to growth
inside it, and what the terminal inherits when it ends — as one repeatable rule for any
company, rather than a set of per-company defaults nobody chose.

---

## 1. The problem — the terminal is struck mid-glide

DNL's explicit period ends at year five with its primary margin driver still moving.
The three operating driver paths in `dnl.yaml` `engine_overlays.baseline` are:

| Driver | Y1 | Y2 | Y3 | Y4 | Y5 | Converged? |
|---|---|---|---|---|---|---|
| `margin_transformation` | 0.6pp | 1.8pp | 2.0pp | 2.0pp | 2.0pp | yes, by Y3 |
| `capex_pct` | 8.0% | 8.0% | 7.0% | 7.0% | 7.0% | yes, by Y3 |
| `margin_gas_rolloff` | 0.0 | 0.0 | −0.5pp | −1.0pp | −1.5pp | no — still ramping |

The gas roll-off is a straight ramp that has not finished when the terminal starts, and
it is the sole source of a −0.50pp per year margin decline at Y5 in **all six**
scenarios. The Gordon terminal then holds that final margin flat in perpetuity. Every
DNL valuation therefore capitalises a margin that was falling half a point a year and
freezes it at the moment the model happens to stop.

The `horizon_years_rationale` in the same file says five years is "long enough to carry
the margin-transformation and gas-roll-off glides to steady state". That is true of the
transformation and false of the roll-off, and the company's own archetype block says why
(§7 below).

This is not a DNL quirk. It is what happens whenever the horizon is a fixed default
rather than a consequence of when the drivers settle.

## 2. What the spec already committed to

`architecture.md` §2 item 5:

> **Forecast horizon.** Parametric per company-scenario combination. Schema supports
> both 5 explicit years + terminal and 10 explicit years + terminal. Default selection
> deferred until scenarios are specified, on the basis that some scenarios may have
> multi-stage arcs that only make sense over 10 years, while others may resolve within 5.

It is carried as open at `architecture.md:113` ("default horizon per company — to be
fixed once scenarios are specified") and again at `:1238` ("needs an explicit field in
the scenario object declaring the horizon for each combination"). Neither was built.
`horizon_years: 5` sits at `normalised_baseline` level in `dnl.yaml` — one value for all
six scenarios.

So the five years was never a decision about any scenario. It is a deferral that
hardened.

## 3. Why the horizon cannot move on its own

Extending DNL to ten years with everything else held flat **raises** Muddle Through from
2.8307 to 3.3057, or +16.8%. Letting the gas roll-off complete still leaves +12.8%.

The cause is that revenue growth is a single scalar. The §11 chain (B25–B42) derives one
company nominal growth rate per scenario — 6.155% for Muddle Through — and
`FcfEngine.run` applies it as `base × (1 + g)^k` for every explicit year. At five years
that is five years at 6.155% before dropping into a 2.5% perpetuity; at ten years it is
ten. The extra five years of 6.2% compounding, rather than falling to terminal growth,
are the whole of the +16.8%.

A longer horizon without a growth fade is therefore not a neutral structural change. It
is a large upward revaluation dressed as a settings change. This is the likeliest reason
§2.5 was deferred rather than built: the horizon field is trivial and the fade is the
actual decision.

## 4. The fade rule (D-36, PROPOSED)

**Revenue growth holds at the chain-derived rate through the forecast segment, then
glides linearly to terminal growth across the fade segment, landing exactly on g in the
final explicit year.**

Landing exactly on g matters. If the final explicit year still grows above g, the
terminal takes a discontinuous step down at the boundary — which is the defect this
paper exists to remove, relocated rather than fixed. Landing on g makes the final
explicit year a genuine steady state, which §6 then relies on.

The fade is not an invention. `fade_period_length` is already a declared driver in the
impact matrix, scenario-differentiated, with the Disorderly Climate entry reading
"Faster fade to convergence under transition pressures. Moat assets decay faster under
stranded-asset and carbon-pricing dynamics." Like `time_profile`, it is schema'd,
populated and read by nothing.

The rule is general and replicable, which is its main virtue: it applies to any company
in any archetype without a per-company judgement, in the same way D-29 made the
working-capital rounding protocol general rather than CSL-specific.

**Engine change required.** `FcfEngineInputs.revenue_growth` is a `float` hard-coded
into the revenue loop. A fade needs a per-year path: one new field, one changed loop, a
length check alongside the existing `len(vec) != H` validations, and the translator
building the path from the chain rate, `fade_period_length` and `terminal_growth`.

## 5. The horizon rule (D-35, PROPOSED)

**The explicit period runs until the drivers straight-line — no relative movement in the
assumptions driving explicit cash flow — subject to a minimum of three years. A company
adopts the longest horizon any of its scenarios requires, and runs every scenario at that
length.**

Running a scenario longer than it needs costs nothing once the fade is in place: the
surplus years grow at terminal growth and reinvest at the steady-state rate, so they
reproduce what the terminal would have said. Running one shorter than it needs is the
defect in §1. Aligning the company to its longest scenario keeps the six comparable —
a scenario table where the cases carry different horizons invites the reader to compare
numbers that were struck on different terms.

## 6. Terminal capex, and why the rule choice should stop mattering (D-38, D-39, PROPOSED)

Two propositions have been argued past each other in this project. Both are half right.

**`capex = D&A` is not the steady-state condition for a growing perpetuity.** Capex and
D&A do both grow at g in the terminal — but what accumulates is their *difference*, and
setting both to the same percentage of the same revenue makes that difference zero. The
book asset base is then constant in nominal dollars forever while revenue compounds at
g, and D&A grows at g against a base that does not, so the implied depreciation rate
rises without limit. A self-consistent steady state has assets A, D&A = δA and capex =
(δ + g)A all compounding at g, with capex exceeding D&A by g × A permanently.
`capex = D&A` is exact only where g = 0.

**But the wedge is second-order, and shrinks as the horizon lengthens.** Sizing it on
DNL's net PP&E of AUD 2,365.6m at the anchor date:

| Scenario | Gap at 5 years | Gap at 10 years |
|---|---|---|
| Orderly Convergence | −11.6% | −7.2% |
| Muddle Through | −11.7% | −7.4% |
| AI Productivity Lag | −10.4% | −6.6% |
| Fragmentation | −14.4% | −9.2% |
| Disorderly Climate | −12.2% | −7.7% |
| Stagflation Persists | −35.7% | −24.3% |

Roughly a third smaller, because the terminal's share of value falls with the horizon.
There is also a genuine offset in the other direction: the 7.3% D&A rate includes
amortisation of acquired intangibles — DNL carries AUD 847.7m of them — and amortisation
needs no replacement capex. So the true wedge is smaller than g × (PP&E + intangibles),
and plausibly smaller than g × PP&E.

The practical resolution is not to pick a side but to stop encoding the choice in a rule
name.

**D-38. The baseline capex path must converge to a declared steady-state rate, and that
rate may not sit permanently below D&A.** DNL's converges to 7.0% against D&A of 7.3%,
which cannot be a steady state — a company reinvesting permanently below depreciation is
shrinking its asset base while its revenue compounds. Setting the converged rate to 7.3%
makes the practitioner's assumption explicitly; setting it to 8.6% makes the
growth-consistent one. Either is defensible. Neither should be inferred from which
terminal rule happens to be selected.

**D-39. Terminal capex is taken from the final explicit year, replacing
`capex_rule: equals_da`.** With the fade landing on g and the capex path converged, the
final explicit year *is* the steady state, so inheriting it is correct — which is exactly
what it was not at five years, when the final year carried a build struck on 6.2% growth.

The consequence is that the argument dissolves:

| Scenario | `equals_da` | `final_explicit_year` | Gap |
|---|---|---|---|
| Orderly Convergence | 3.3976 | 3.3976 | 0.0% |
| Muddle Through | 2.8822 | 2.8822 | 0.0% |
| AI Productivity Lag | 2.8083 | 2.8083 | 0.0% |
| Fragmentation | 2.0102 | 2.0102 | 0.0% |
| Disorderly Climate | 1.6601 | **1.4604** | −12.0% |
| Stagflation Persists | 0.7369 | 0.7369 | 0.0% |

Where a scenario carries no permanent reinvestment difference the two rules agree
exactly. The rule only bites where a scenario has declared that something is different
forever — and there it bites in the right direction.

Note what this does *not* revive. The terminal stays in `normalised` mode (D-32),
rebuilt from components with the working-capital drag struck at g × intensity. Only the
source of terminal capex changes. The 23 August defect — capitalising a working-capital
build struck on explicit-period growth into a slower perpetuity — cannot recur, because
the fade makes final-year growth equal to g.

## 7. Archetypes should carry ten years whether or not ten are used (D-37, PROPOSED)

The scenario layer is already built for this. `MacroVariable` carries a `time_series` of
`{year, value, confidence_low, confidence_high}`, and Muddle Through populates world real
GDP growth, US real GDP growth, advanced-economy CPI and the real policy rate at years 1,
2, 3, 5, 7 and 10.

What is missing is the industry layer. The two drivers DNL's revenue chain actually
consumes — `global_mining_real_growth` and `gas_price_growth` — exist nowhere as series.
They are single scalars in `dnl.yaml`'s `revenue_growth_chain.by_scenario`. The
`commodity_and_energy.gas_regime` block is prose. So the general macro is ten-year-ready
and the macro that drives the valuation is not.

The proposal is three parts:

1. Each archetype declares the macro drivers its revenue chain consumes, as a
   `required_macro_drivers` list on the archetype file.
2. Every scenario carries a year-anchored `time_series` for each declared driver, with
   anchors at years 1, 3, 5, 7 and 10 as a minimum, linearly interpolated between.
3. A new SSOT ratchet check (13) fails where any scenario × archetype pair lacks a driver
   path reaching year 10 — the same enforcement shape as checks 10 to 12, so that an
   absent path stays distinguishable from a passing one. Baseline it at today's state and
   tighten as paths land.

The fade and the driver paths are then a default and an override rather than
alternatives. The fade governs any driver with no declared path — general, replicable,
company-agnostic. A declared path overrides it wherever the domain knowledge exists. Once
check 13 is green the fade only ever governs the shape between anchors, and the horizon
becomes a free choice rather than a data constraint.

## 8. DNL applied — the gas roll-off (D-40, PROPOSED, PROVISIONAL)

The archetype block answers the timing question precisely.
`company_position.segments[0].archetype_specific.us_gas_contract_maturity_profile`:

> Average contract maturity 6 years remaining. Tiered roll-off through to **2032** with
> re-pricing risk concentrated in the **2028–2030** window.

The valuation date is 25 May 2026 against a September year-end, with a 0.351-year stub.
So Y1 is FY2027, Y3 FY2029, Y5 FY2031 — and the roll-off completes in **FY2032, the first
terminal year**. It finishes one year past the end of the explicit period, which is why
§1's ramp is unfinished.

The impact matrix adds that the contracts "partly insulate ~70% of US gas exposure
through 2028". Read together with the maturity profile these reconcile rather than
conflict: insulation holds to FY2028, then unwinds across FY2028–FY2032. That reading
independently supports a re-phasing — little effect in Y1, the bulk in FY2028–FY2030, a
tail to FY2032 — and the two blocks should carry one clarifying line so the next reader
does not have to reconcile them unaided.

**Magnitude is a judgement, and the existing one is undocumented.** The
`margin_gas_rolloff` array carries no `*_rationale`, unlike every other layer-2 judgement
in the file — only a workbook cell reference. Whether −1.5pp was intended as the total
effect or as five years of a continuing ramp is not recoverable from the file. Given the
archetype says the roll-off runs a year beyond where the ramp stops, continuing it at the
same −0.5pp per year to **−2.0pp** is the minimal non-inventive extension, and the more
conservative of the two readings.

It cannot be derived. Sizing the true margin loss needs gas as a share of cost, which is
not in the repository. So −2.0pp is proposed as PROVISIONAL, with a written rationale, to
be revisited when the cost breakdown lands. The choice is material: Muddle Through lands
at 3.0422 on −1.5pp against 2.9208 on −2.0pp.

Proposed cumulative path, as fractions of the total: 0.05, 0.30, 0.60, 0.85, 0.95, 1.00
at Y1–Y6, flat thereafter. That places 80% of the movement in FY2028–FY2030.

## 9. DNL applied — the Disorderly Climate capex arc (D-41, PROPOSED)

Disorderly Climate is the only DNL scenario carrying a non-zero `capex_delta_pp`, at
+3.0pp, and under D-14 it applies as a parallel shift across every explicit year. It
therefore never resolves: at ten years it would still be +3.0pp in year ten. The horizon
does not bind here; the shape of the assumption does.

The scenario's own `time_profile` contradicts that shape — crystallisation Y1–Y2,
repricing Y2–Y5, **new equilibrium from Y6** — so the flat shift carries repricing-phase
capex into a phase the scenario says has ended.

The impact matrix distinguishes two components the single delta conflates:

> `growth_capex_pct_revenue` — Transition-aligned capacity additions (green ammonia,
> transition-mineral-mining service expansion). **Offsetting compression of capex in
> coal-mining-supporting capacity.**

> `maintenance_capex_pct_revenue` — Decarbonisation capex for ammonia production (carbon
> capture, green ammonia pilots). Material spending required to maintain **licence to
> operate** under new carbon-pricing regimes.

The first is a reallocation and nets out. The second does not end when the transition
does — a licence-to-operate cost is permanent by construction.

So: **+3.0pp held through Y5, decaying across Y6–Y8 to a persistent +1.0pp, held
thereafter.** Under D-39 the terminal then inherits 7.3% + 1.0pp, and the scenario
carries its carbon burden into perpetuity rather than shedding it at the terminal
boundary.

**One channel remains unrepresented.** The matrix sets this scenario's `terminal_roic`
with a defended §10.6 exception — moat decay horizon of 10–15 years, with a sensitivity
note that halving it to 5–7 years costs a further 15–20% of terminal value. Nothing in
the build represents it. Disorderly Climate's level should not be treated as settled
while a declared, sized, long-tailed downside channel is missing from it.

## 10. What it is worth

Live five-year levels against the proposal — ten years, fade to g at Y10, capex
converged to 7.3%, gas roll-off −2.0pp re-phased, Disorderly capex arc per §9, terminal
capex from the final explicit year:

| Scenario | Live (5y) | Proposed (10y) | Change | TV% now | TV% proposed |
|---|---|---|---|---|---|
| Orderly Convergence | 3.2740 | 3.3976 | +3.8% | 74.3% | 57.1% |
| Muddle Through | 2.8307 | 2.8822 | +1.8% | 72.7% | 54.9% |
| AI Productivity Lag | 2.7705 | 2.8083 | +1.4% | 71.6% | 53.3% |
| Fragmentation | 1.9926 | 2.0102 | +0.9% | 71.8% | 53.9% |
| Disorderly Climate | 1.7015 | 1.4604 | −14.2% | 79.0% | 57.9% |
| Stagflation Persists | 0.8061 | 0.7369 | −8.6% | 70.2% | 52.6% |

Four levels move less than four per cent. The two that move are the two where the current
build was doing something indefensible: Disorderly Climate was shedding its defining
assumption at the terminal boundary, and Stagflation was capitalising the deepest
unfinished gas roll-off of the six.

**Every case falls below the 70% terminal-share threshold**, where all eighteen currently
breach it. Under D-07 that lifts the §11.4.2 sensitivity obligation from cases that carry
it today. This falls out of a horizon decision rather than being chosen, and is worth
noticing as a change in the project's posture rather than a free improvement.

## 11. What this does not decide

1. **Whether the growth-consistent terminal capex is adopted.** §6 sizes it and parks it
   as a declared approximation. D-38 gives it a home — the converged capex rate — so it
   can be revisited without touching a rule.
2. **The gas roll-off magnitude**, which is PROVISIONAL and not derivable from repository
   data.
3. **The moat-decay channel in Disorderly Climate** (§9), declared in the matrix and
   modelled nowhere.
4. **Whether WBC and CSL adopt the same horizon.** The rules in §4 to §7 are written to
   be archetype-agnostic, but neither company's driver paths have been examined for where
   they straight-line. The bank engine and the segment engine both need the same
   treatment before this can be called a project-wide standard.
5. **The workbook and golden consequences.** All eighteen goldens move, both audited
   workbooks need rebuilding and re-tying, and the `-m libreoffice` recalculation ties
   must be re-pinned. That is the accepted cost of the change, not an argument against
   it — but it is a day's work, not an afternoon's.

## 12. Proposed decisions

| ID | Decision | Status |
|---|---|---|
| D-35 | Explicit period runs until drivers straight-line, minimum three years; a company adopts the longest horizon any of its scenarios requires and runs all scenarios at that length. | PROPOSED |
| D-36 | Revenue growth fades linearly from the chain rate to terminal growth across the fade segment, landing exactly on g in the final explicit year. `fade_period_length` is declared per scenario. | PROPOSED |
| D-37 | Each archetype declares its required macro drivers; every scenario carries year-anchored paths to year 10 for each; ratchet check 13 enforces it. | PROPOSED |
| D-38 | The baseline capex path converges to a declared steady-state rate, which may not sit permanently below D&A. DNL: 7.3%. | PROPOSED |
| D-39 | Terminal capex is taken from the final explicit year, replacing `capex_rule: equals_da`. Terminal mode stays `normalised` (D-32). | PROPOSED |
| D-40 | DNL gas roll-off totals −2.0pp, re-phased to concentrate in FY2028–FY2030 and complete FY2032. | PROPOSED — PROVISIONAL on the cost breakdown |
| D-41 | DNL Disorderly Climate capex: +3.0pp through Y5, decaying across Y6–Y8 to a persistent +1.0pp. | PROPOSED |
