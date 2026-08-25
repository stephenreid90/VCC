# Forecast horizon, growth fade and terminal convergence

**Status, 25 Aug 2026: PROPOSED, nothing ratified.** Nine decisions are put forward
here (D-35 to D-43). None is in force; no code has moved. The numbers throughout are
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

## 11. Earning the cost of capital only in the long run

The framework already carries this rule. `architecture.md` §11.4.2 consistency check 2:

> **Terminal-state convergence (cross-check with §10.6 rule 2).** Enforced at translation
> time. Terminal ROIC ≈ WACC (or terminal ROE ≈ cost of equity for banks) unless the
> matrix entry carries a §10.6-compliant defended exception (moat source named, decay
> horizon stated, named threat, sensitivity test).

It is not enforced. `terminal_roic` appears in the codebase exactly once, as a
driver-delta mapping in `translator.py:107`. No ROIC is computed anywhere in the engine
or the tests, so the check cannot fire. It joins `time_profile`, `fade_period_length` and
the year-10 macro anchors on the list of things that are specified, populated and read by
nothing.

**What the current terminals actually assume.** In a Gordon terminal, g = ROIC ×
reinvestment rate, so the reinvestment the model carries implies a return. Reading it back
out of the live five-year build:

| Scenario | g | Reinvestment rate | Implied terminal ROIC | × WACC |
|---|---|---|---|---|
| Orderly Convergence | 2.75% | 3.5% | 79.6% | 9.0× |
| Muddle Through | 2.50% | 3.2% | 76.9% | 8.7× |
| AI Productivity Lag | 2.25% | 2.8% | 79.6% | 9.0× |
| Fragmentation | 2.25% | 3.7% | 61.1% | 6.9× |
| Disorderly Climate | 1.75% | 2.9% | 61.1% | 6.9× |
| Stagflation Persists | 2.25% | 6.0% | 37.4% | 4.2× |

WACC is 8.877%. Every DNL scenario assumes the company earns between four and nine times
its cost of capital, on incremental capital, in perpetuity. Stagflation Persists — the
world in which DNL's margin collapses to 7.1% — still assumes a terminal return of 37%.

Two of the six carry a `terminal_roic` entry in the impact matrix at all
(`industrial_explosives.yaml:174` and `:623`). The other four have no defended exception
on record and are running at six to nine times WACC regardless.

**What convergence would cost.** Imposing ROIC = WACC collapses the Gordon terminal to
NOPAT ÷ WACC — growth at the cost of capital creates no value, which is the cleanest
statement of the principle:

| Scenario | Live | ROIC = WACC | Change |
|---|---|---|---|
| Orderly Convergence | 3.2740 | 2.3925 | −26.9% |
| Muddle Through | 2.8307 | 2.1344 | −24.6% |
| AI Productivity Lag | 2.7705 | 2.1634 | −21.9% |
| Fragmentation | 1.9926 | 1.5275 | −23.3% |
| Disorderly Climate | 1.7015 | 1.3467 | −20.9% |
| Stagflation Persists | 0.8061 | 0.5617 | −30.3% |

This is by some distance the largest single assumption in the DNL build — larger than the
working-capital standard, the terminal rebuild and the horizon change combined.

**It is also the same rule as §6, arrived at from the other side.** The identity is that
to grow at g, invested capital must itself grow at g — so reinvestment = g × IC, and IC
must include every pool that reinvestment feeds. Working capital is one of them: ΔWC is
part of reinvestment, so non-cash working capital is part of invested capital. It is not
an optional addition to the fixed-asset base; leaving it out would break the identity.

Working the requirement back for Muddle Through:

| | AUD m |
|---|---|
| Terminal revenue | 4,697.9 |
| Terminal NOPAT (10.58% of revenue) | 497.3 |
| Required reinvestment rate (g ÷ WACC = 2.50% ÷ 8.877%) | 28.2% |
| Required reinvestment | 140.0 |
| **Implied invested capital** (reinvestment ÷ g) | **5,601.7** |

And building the actual base up from the balance sheet:

| | AUD m |
|---|---|
| Net PP&E | 2,365.6 |
| Intangibles | 847.7 |
| Goodwill | 1,778.5 |
| Non-cash working capital (13.76% × terminal revenue) | 646.4 |
| **Total invested capital** | **5,638.2** |

The two are 0.6% apart. So requiring terminal ROIC = WACC is arithmetically the same
statement as requiring DNL to reinvest enough to grow its *whole* capital base — plant,
acquired intangibles, goodwill and working capital — at g. The reinvestment question of
§6 and the return question here are one question.

**Which base is the live judgement, and it is not academic.** DNL's current return on
normalised base-year NOPAT of AUD 371.5m, against a WACC of 8.877%:

| Invested-capital base | IC (AUD m) | ROIC | vs WACC |
|---|---|---|---|
| Net PP&E only | 2,365.6 | 15.71% | above |
| PP&E + working capital | 2,833.4 | 13.11% | above |
| PP&E + intangibles + working capital | 3,681.1 | 10.09% | above |
| + goodwill — total invested capital | 5,459.6 | **6.81%** | **below** |

On everything shareholders' capital actually paid for, DNL earns 6.81% today against a
cost of capital of 8.877%. It is not currently earning its cost of capital. The terminal
as built assumes 76.9% — roughly eleven times what the business returns on committed
capital now.

This inverts how convergence should be read. Imposing ROIC = WACC in the terminal is not
a punitive assumption on the goodwill-inclusive base; it is an *improvement* on today,
and the company has to get better to deliver it.

Two honest qualifications. The base-year NOPAT uses the normalised 14.1% margin and the
22.5% effective rate, not reported figures. And AUD 1,778.5m of goodwill is largely
inherited from IPL-era acquisitions — there is a real argument that a demerged business
should not be charged in perpetuity for capital its predecessor deployed. Excluding
goodwill but keeping intangibles and working capital gives 10.09%, modestly above WACC,
which is a plausible reading of a genuine but narrow moat and sits comfortably with the
matrix's defended exception of scale plus the long-term gas contracts.

So the defensible range for DNL's sustainable return is something like 7% to 13% against
a WACC of 8.877% — not the 61% to 80% the six terminals currently carry. The choice of
base is worth an argument. The current position is not.

**The proposal is the diagnostic, not the verdict.** Computing terminal ROIC and surfacing
it against WACC is cheap and uncontroversial: the rule already exists and the inputs are
all present. What to do when it fires is the judgement, and §11.4.2 already frames it —
a §10.6-compliant defended exception, or convergence. A framework that can state a
company's terminal return and does not is choosing not to look.

**D-42 (PROPOSED).** Compute terminal ROIC (terminal ROE for banks) at translation time
and surface it against WACC on every valuation. Where it exceeds WACC, require a
§10.6-compliant defended exception naming the moat source, the decay horizon, the threat
and a sensitivity test — as §11.4.2 check 2 already specifies. Non-blocking in the first
instance, on the D-07 precedent: it warns and obliges, it does not silently adjust.

## 12. Where the decay horizon comes from, and why it is not second-order

If a terminal excess return must be *dated* rather than assumed away (§11), the obvious
objection is that the date is a judgement — and this project is built on removing
judgements, not adding them. It need not be. The industry analysis already carries the
raw material.

**The Five Forces ratings are already there and already ordinal.** All three archetypes
carry the same scale:

| Force | Industrial explosives | Plasma-derived therapies | Australian major banks |
|---|---|---|---|
| Threat of new entrants | low | very_low | low |
| Rivalry | high | moderate | moderate |
| Substitutes | low | low_to_moderate | low_to_moderate |
| Buyer power | high | moderate | low_to_moderate |
| Supplier power | moderate | low | moderate |

Three of these govern how fast an excess return erodes: entrant threat sets the height of
the barrier, rivalry sets how fast incumbents compete the excess away, and substitutes set
erosion from outside the industry. Buyer and supplier power set the *level* of the return,
not its durability.

**But the ratings alone cannot do the job, and it is worth being clear why.** Industrial
explosives and the Australian major banks both score `new_entrants: low`. On the ratings
alone, a gas-contract cost position and a banking licence are the same barrier. They are
not: one falls to a well-funded entrant, the other requires a political decision.

So the horizon needs a second input, and §10.6 already asks for it — the moat *source*.
Made into a taxonomy with durability tiers, ordered by what has to happen for the barrier
to fall:

1. **Statutory or licensed barrier** — removed only by a political decision (four pillars,
   an APRA licence).
2. **Network or scale advantage in a small market** — eroded by a structural shift in
   market size or technology.
3. **Cost position from an irreplicable asset** — eroded when the asset is matched or
   expires.
4. **Brand** — eroded by sustained competitive investment.
5. **Patent or contract** — expires on a stated date.

The fifth tier is the useful one, because it removes the judgement entirely: where the moat
source has a contractual or statutory expiry, **that date is the horizon**. DNL's cost
advantage is its long-term US gas contracts, and §8 of this paper establishes that they
roll off through **2032**. The decay horizon is not a view; it is in the contracts.

**And the horizon is not a rounding error.** The instinct — mine included — is that beyond
thirty or forty years the discounting makes the distinction academic. It does not, because
book equity is compounding at g while the discount rate is Ke, so the effective discount on
residual income is only Ke − g. For WBC that is 8.05% − 3.5% = 4.55%, and a 4.55% net
discount has a very long tail. Valuing WBC's ROE premium (10.50% against a Ke of 8.05%) as
a linear decay to Ke over N years:

| Decay horizon | Value ÷ book | Share of the perpetual moat captured |
|---|---|---|
| 5 years | 1.043 | 8.1% |
| 10 years | 1.091 | 17.0% |
| 15 years | 1.133 | 24.7% |
| 20 years | 1.170 | 31.5% |
| 30 years | 1.229 | 42.6% |
| 40 years | 1.276 | 51.3% |
| 50 years | 1.312 | 58.0% |
| 100 years | 1.412 | 76.6% |
| forever | 1.538 | 100.0% |

A forty-year moat captures barely half the value of a perpetual one. The difference is 17%
of WBC's terminal and, at a 76.3% terminal share, about 13% of the whole valuation. So
"effectively forever" is not arithmetically true at these rates — assuming a perpetual bank
moat is a live, material assumption that has to be declared and tested, not a convenience.

This cuts the other way too, and helpfully. A competitive business with a ten-to-fifteen
year decay horizon captures only 17% to 25% of a perpetual moat, which sits far closer to a
hard cap at the cost of capital than to perpetuity. For DNL and CSL the argument between
"cap at WACC" and "fade over the Porter-implied horizon" is a modest one. It is only for
the licensed archetype that the choice is expensive — which is precisely where the
judgement should be visible.

**D-43 (PROPOSED).** The terminal excess-return decay horizon is derived, not judged: from
the archetype's Five Forces ratings for entrants, rivalry and substitutes, combined with a
declared `moat_source` drawn from the tiered taxonomy above. Where the source carries a
contractual or statutory expiry, that date is the horizon. A perpetual horizon is
admissible only for a tier-1 statutory barrier, must name the threat that would end it, and
must be sensitivity-tested against a finite horizon — because §12's table shows the
assumption is worth 15% to 20% of terminal value, not a rounding.

## 13. What this does not decide

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
5. **Whether terminal ROIC is forced to converge** (§11). D-42 proposes computing and
   surfacing it, which is the cheap and uncontroversial half. Whether an unsupported
   6–9x WACC terminal return is corrected, defended or left standing is the single
   largest open assumption in the build.
6. **The workbook and golden consequences.** All eighteen goldens move, both audited
   workbooks need rebuilding and re-tying, and the `-m libreoffice` recalculation ties
   must be re-pinned. That is the accepted cost of the change, not an argument against
   it — but it is a day's work, not an afternoon's.

## 14. Proposed decisions

| ID | Decision | Status |
|---|---|---|
| D-35 | Explicit period runs until drivers straight-line, minimum three years; a company adopts the longest horizon any of its scenarios requires and runs all scenarios at that length. | PROPOSED |
| D-36 | Revenue growth fades linearly from the chain rate to terminal growth across the fade segment, landing exactly on g in the final explicit year. `fade_period_length` is declared per scenario. | PROPOSED |
| D-37 | Each archetype declares its required macro drivers; every scenario carries year-anchored paths to year 10 for each; ratchet check 13 enforces it. | PROPOSED |
| D-38 | The baseline capex path converges to a declared steady-state rate, which may not sit permanently below D&A. DNL: 7.3%. | PROPOSED |
| D-39 | Terminal capex is taken from the final explicit year, replacing `capex_rule: equals_da`. Terminal mode stays `normalised` (D-32). | PROPOSED |
| D-40 | DNL gas roll-off totals −2.0pp, re-phased to concentrate in FY2028–FY2030 and complete FY2032. | PROPOSED — PROVISIONAL on the cost breakdown |
| D-41 | DNL Disorderly Climate capex: +3.0pp through Y5, decaying across Y6–Y8 to a persistent +1.0pp. | PROPOSED |
| D-42 | Terminal ROIC (ROE for banks) is computed at translation time and surfaced against WACC; an excess requires a §10.6-compliant defended exception. Non-blocking, per the D-07 precedent. | PROPOSED |
| D-43 | The decay horizon for a terminal excess return is derived from the Five Forces ratings plus a declared tiered `moat_source`, not judged. A contractual or statutory expiry sets the horizon directly. Perpetual is admissible only for a statutory barrier, with a named threat and a finite-horizon sensitivity. | PROPOSED |
