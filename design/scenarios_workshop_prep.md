# Scenarios Workshop — Prep Document

**Companion to:** `design/architecture.md` §6 (Layer 1 — Scenario Library), §3.3 (probability-weighting decision), §16.1 item 1 (scenario narrative deliverable), §2 item 2 (3–6 scenarios, locked).
**Status:** Prep for the dedicated scenarios workshop. Workshop output will be captured separately in `design/scenarios_workshop.md`.

---

## Purpose of this document

To set Tara up to walk into the workshop ready, with: (i) the framework's discipline about what counts as a good scenario, (ii) a sense of what reputable institutions are currently treating as live, (iii) a starting set of candidate themes to discriminate against (not adopt wholesale), (iv) structuring questions to drive the workshop's decisions.

The workshop itself is Tara's offline work. This document is the input.

---

## What the workshop must produce

1. **3–6 named scenarios** per §2 Locked Decision item 2. Exact count emerges from the workshop; the framework supports anything in that range. Resist locking the count before the work is done.
2. **`data/scenarios/<scenario_id>.yaml`** per scenario, populated against the §6.4 schema (id, name, version, narrative, macro time series with confidence bands, regime tags, time profile).
3. **`data/scenarios/<scenario_id>.md`** per scenario — narrative write-up per §16.1 item 1.
4. **`design/scenarios_workshop.md`** — record of themes considered (including those rejected), themes selected and why, decisions made, items deferred.

---

## What makes a scenario "good enough" for our framework

Tested against §6.2 commitments and §6.4 schema requirements.

1. **Scenarios are boundary cases, not exhaustive coverage.** Per §6.2: *"They are a chosen set of meaningfully different worlds … neither exhaustive nor strictly hierarchical."* The whole point is to span the plausible range, not to enumerate every possibility nor to weight them probabilistically. If you find yourself wanting to add a scenario to "cover" something, the test is: *does the new scenario change the shape of the future, or is it a severity-dial variation on an existing one?* Only the former earns its place.
2. **Each scenario must differ on multiple dimensions.** Per §2 item 2: *"Scenarios must differ on multiple dimensions — not simply severity dials on a single axis."* A scenario set of "mild recession / deep recession / severe recession" is one-dimensional and rejects this discipline. A scenario set that varies inflation regime, geopolitical alignment, energy intensity, and labour-market structure differently across scenarios is multidimensional and earns its place.
3. **Internal consistency.** Within a scenario, macro variables and regime tags must move in logically consistent ways (§6.6 deliverable 3). "Stagflation persists" cannot have sticky inflation and falling policy rates. Workshop time should be spent stress-testing each scenario against this discipline.
4. **Analytical purchase on IPL / CSL / WBC.** Each scenario should produce a *different* picture for at least two of the three test companies — otherwise it's not helping us separate views. A scenario that moves all three similarly is either too generic or has its discriminating action elsewhere (which then needs to be surfaced).
5. **Time profile is scenario-specific.** Per §2 item 5: forecast horizon is parametric per company-scenario combination. Some scenarios resolve in 1–3 years (e.g. a sharp shock that fades); others play out over 10+ (e.g. demographic regime, energy transition). The scenario should declare its natural horizon.
6. **A narrative a non-economist can read.** The scenario narrative is the artefact a reviewer engages with first; the YAML is the source-of-truth structure. If the narrative can't survive two minutes of explanation to a smart non-economist, the scenario isn't crisp enough.

---

## What major institutions are publishing right now

Snapshot of current scenario publications from reputable houses, as of mid-May 2026. **These are inputs to the workshop's theme-selection discussion, not the scenarios themselves.** Our scenarios should be analytically more discriminating than institutional reference/downside/severe sets — they need to span multiple dimensions, not severity dials.

### 1. IMF — World Economic Outlook, April 2026 ("Global Economy in the Shadow of War")

Three-tier scenario structure:
- **Reference forecast** — assumes the war is limited in duration and scope; disruptions fade by mid-2026. Global growth 3.1% in 2026, 3.2% in 2027; energy commodities +19%; headline inflation 4.4%.
- **Adverse scenario** — sharper energy-price rise, rising inflation expectations, tighter financial conditions. Growth 2.5%, inflation 5.4%.
- **Severe scenario** — energy supply dislocations extend into 2027; inflation expectations markedly less anchored; sharply tightened financial conditions. Growth 2%, inflation > 6%.

*What's signal-bearing for us:* the IMF has effectively replaced "baseline" language with "reference" — acknowledging the conditioning assumption that the war stays limited. The severe scenario carries a real probability mass in their view, not just stress-test colour.

### 2. OECD — Economic Outlook Interim Report, March 2026 ("Testing Resilience")

Single baseline projection (global GDP growth 2.9% in 2026, 3.0% in 2027; G20 inflation 4.0% then easing to 2.7%) plus risk-factor commentary:

- **Upside factors:** technology-related investment momentum (AI-driven), lower-than-assumed tariff rates, carry-over from robust 2025.
- **Downside factors:** Strait of Hormuz disruption; energy infrastructure damage; energy-and-fertiliser supply shocks; commodity-price spike feeding through to inflation.
- **Tail risk:** prolonged Middle East export disruption causing sharper price reaction and commodity shortages; lower-than-expected AI investment returns triggering financial-market repricing.

*What's signal-bearing for us:* the AI productivity story is now framed as live and bidirectional — upside if it pays off, downside if it doesn't. The energy-shock channel runs through fertilisers explicitly, which matters for any IPL-comparable nitrogen-fertilisers exposure (not in our test set but in our archetypes).

### 3. World Bank — Global Economic Prospects, January 2026

Baseline + a downside scenario:
- **Baseline:** global growth easing to 2.6% in 2026 then 2.7% in 2027. Modestly upward-revised from June 2025.
- **Downside:** sharp equity-valuation decline + plunging risk appetite + tighter financial conditions → growth shaved 0.3 ppt.
- **Risk register:** further trade-barrier rises; financial conditions tightening amid banking-sector vulnerabilities; social unrest; more frequent / severe extreme weather.
- **Upside:** bilateral trade progress; faster tech-led investment; post-election political stability.

*What's signal-bearing for us:* the World Bank is the institution most explicitly flagging *banking-sector vulnerabilities* and *trade barriers* as live downside channels — both directly relevant to WBC and to any scenario involving fragmentation.

### 4. IEA — World Energy Outlook 2025

Three scenarios, each conditioned on a different policy assumption:
- **CPS (Current Policies Scenario)** — extrapolates current policies; effectively a "no further policy action" world. Pulled forward; the Announced Pledges Scenario (APS) is *not* in WEO 2025.
- **STEPS (Stated Policies Scenario)** — energy system follows the direction implied by adopted-or-stated policies. Trajectory consistent with ~2.5°C warming.
- **NZE (Net Zero Emissions by 2050)** — normative pathway to align energy sector with 1.5°C goal. Built on four pillars: clean-energy electrification, energy efficiency, low-emissions fuels, methane abatement.

*What's signal-bearing for us:* the IEA's dropping of APS in 2025 reflects a view that announced pledges have lost credibility as a separate trajectory — either policies actually move (STEPS converges toward APS) or they don't (STEPS holds). Useful framing: an "orderly transition" scenario should arguably anchor to STEPS rather than to NZE.

### 5. NGFS — Climate Scenarios Phase V (November 2024, with short-term scenarios added May 2025)

Long-term climate scenarios used by central banks for prudential stress-testing. Phase V's key change: an updated physical-risk damage function producing **GDP losses 2–4× higher than previously estimated** — Current Policies 5–15%, Net Zero 2050 2–7%, by 2050.

Phase V also introduced *short-term* scenarios (3–5 year horizon) for the first time, recognising that long-term climate-economy relationships don't capture the near-term transmission channels prudential stress-testers need.

*What's signal-bearing for us:* (i) physical climate risk is being revised upward materially by official institutions, which should push the climate-scenarios our framework considers toward more painful loss profiles than typical industry consensus; (ii) the short-term NGFS scenarios are a useful template for our 1–5-year scenario horizon question per §2 item 5.

### Themes the institutions collectively emphasise

Across all five sources, the dominant 2026 themes are:

1. **Geopolitical conflict and energy-shock transmission** — IMF and OECD both centre the Middle East / Strait of Hormuz disruption; energy → fertilisers → broader commodity pass-through.
2. **Trade barriers and fragmentation** — World Bank emphasises; IMF's "fragmentation" framing carries into the severe scenario.
3. **AI investment cycle — upside if it pays off, downside if it doesn't** — OECD explicit, IMF / WB implicit.
4. **Climate physical risk being revised upward** — NGFS Phase V; flow-on to credit and asset-price impacts.
5. **Banking-sector and financial-condition vulnerabilities** — World Bank flag; IMF severe scenario.
6. **Stagflation as the structural worry** — IMF severe + OECD downside; energy-inflation-expectations-financial-conditions nexus.

These are themes, not scenarios. The workshop's job is to combine them into 3–6 multidimensional scenarios that span the plausible range.

---

## Candidate scenario themes for the workshop

A starting set to **discriminate against**, not adopt wholesale. The workshop should pick 3–6 that span the plausible range, differ on multiple dimensions, and give analytical purchase on IPL / CSL / WBC. Adapt names freely.

1. **Orderly convergence.** Conflict de-escalates within 12 months; energy prices normalise. Central banks land softly; inflation glides to target. Trade barriers stable; AI investment continues productively. Real rates settle slightly above pre-2022. *Anchor: IEA STEPS + IMF reference.*
2. **Stagflation persists.** Energy shock entrenches; second-round wage-price effects un-anchor inflation expectations; central banks forced to keep rates restrictive; growth slows materially. *Anchor: IMF adverse → severe; OECD downside tail.*
3. **Fragmentation and resource nationalism.** Geopolitical alignment hardens; trade barriers rise; supply chains regionalise; energy markets bifurcate; reserve diversification accelerates; capital controls in selected EMs. *Anchor: World Bank fragmentation risk; IMF severe.*
4. **Disorderly climate transition.** Climate policy whipsaws — accelerated carbon pricing in EU/US, lagging elsewhere; stranded assets concentrate in energy-intensive incumbents; supply shocks in critical-minerals and food. *Anchor: NGFS Disorderly + IEA NZE-anchored regulatory pressure.*
5. **AI-productivity boom.** AI capex and adoption deliver productivity gains; inflation surprises downward; real rates rise as demand strengthens; equity concentration in a small cohort of beneficiaries; labour-market disruption uneven. *Anchor: OECD upside; IMF tech-momentum.*
6. **AI-investment disappointment.** Capex extended but returns disappoint; financial-market repricing in tech-concentrated indices; capital recycles to value sectors; growth subdued; consequence: many of the secular-growth bets that have been priced in unwind. *Anchor: OECD downside scenario.*
7. **Financial-condition shock / banking stress.** Trigger varies (CRE, sovereign, NBFI counterparty); abrupt tightening of credit conditions; central-bank intervention. Acute but bounded. *Anchor: World Bank financial-stability risk; IMF severe.*
8. **Demographic-and-labour-supply regime.** Slower-burn theme: ageing in advanced economies, fertility decline propagating; productivity must rise to maintain GDP/capita; healthcare and aged-care expenditure rising; capital deepening required. *No institutional anchor — secular theme.*

**Notes for the workshop:**

- Scenarios 2 and 7 risk being severity-dial variants of each other (both involve tightening / stress). Test: do they differ on *non-financial* dimensions?
- Scenarios 5 and 6 are paired upside/downside of the same theme; arguably should be one scenario with a quantified-band approach, not two scenarios.
- Scenario 4 cuts across scenarios 1 and 2 (climate transition can be orderly or disorderly *under* a stagflationary macro). Consider whether climate is a dimension of every scenario rather than a standalone scenario.
- Scenario 8 may be too slow-moving for a 10-year horizon to surface; consider folding into a longer-horizon "secular" scenario or accepting it sits in background.

---

## Structuring questions for the workshop

Use these to make the workshop's decisions visible.

### A. Theme selection

1. **Multidimensional test.** For each candidate, on which dimensions does it materially differ from the *closest* other candidate? Inflation regime, geopolitical alignment, energy intensity, productivity growth, financial conditions, climate policy, labour supply. If the answer is "one dimension", the candidate is a severity dial — merge or drop.
2. **Discrimination test.** For each pair of candidates, under which would IPL's view materially differ? CSL's? WBC's? If none of the three companies' views moves between two scenarios, they're indistinguishable for our purpose — merge.
3. **Boundary test.** Does the candidate change the shape of the future, or is it interpolation between others already chosen?
4. **Plausibility test.** Is there a credible chain from today's world to the scenario? Not "is it likely" — plausibility, not probability.

### B. Count and span

5. **Why this count?** If you end at 3, you're disciplined; if you end at 6, you're rich. Above 6, the framework starts to fail (analyst time per scenario is a finite resource — §14.1 budget anchor). Below 3, you've lost the comparative-analysis benefit.
6. **Does the chosen set span the plausible range?** Plot the chosen scenarios mentally on each of the dimensions in question A.1. Are any dimensions covered by only one scenario? If so, that dimension is under-tested.

### C. Time profile per scenario

7. **What's the natural horizon for this scenario?** 1–3 years (acute shock that fades), 3–7 years (regime shift that plays out), 10+ years (secular trend). Don't impose a uniform horizon; some scenarios resolve fast, others slowly.
8. **What's the timing within the horizon?** Does the disruption hit Year 1 and fade, or build over Years 1–3 and persist? Tie to the §11.3 time-profile library (impulse / regime_shift / step / cyclical / front_loaded / back_loaded / linear_through_horizon).

### D. Macro variables and confidence

9. **Which macro variables move materially in this scenario, and which stay close to baseline?** Policy rates, inflation, GDP growth (per major region), currencies, energy prices, commodity prices, credit spreads, equity premia. The §6.4 schema supports both quantified time series with confidence bands *and* regime tags for qualitative variables — choose per variable.
10. **What's the confidence-band convention?** Per §6.7 item 4 and §11.7 item 8: bands are *analyst subjective range conditional on the scenario playing out as defined*. Workshop should agree the convention so bands are comparable across variables.

### E. Probability and presentation

11. **Are we assigning per-scenario probabilities?** Per the §3.3 narrowed open decision: comparative output is canonical. Optional per-scenario probability is supported for analyst-side indicative blends; the engine does not present a blended scalar as a canonical output. Workshop chooses whether to populate the optional field at all.
12. **What's the headline framing?** Per §13 default-view discipline: avoid defaulting to one scenario as "the answer"; default to a multi-scenario comparison. Workshop should agree the headline framing so it can be implemented in the dashboard tab.

### F. Versioning and refresh

13. **Version number and refresh date.** Each scenario carries a `version` and a refresh date (§6.5: 6-monthly cadence). Workshop locks the version-1 number for each scenario and the next-review date.

---

## §6.4 schema checklist — what each scenario needs

Before declaring a scenario "ready", confirm each of the following is populated in the YAML. Schema details in `design/architecture.md` §6.4.

1. `id` — stable snake_case identifier (e.g. `orderly_convergence`, `stagflation_persists`).
2. `name` — human-readable title for the narrative.
3. `version` and `last_reviewed_at` — for the staleness propagation in §10.6 / §10.7.
4. `narrative` — short structured summary in the YAML, with the longer prose in the paired `.md` file.
5. `macro_variables` — per variable, either:
   (a) `time_series` with `{year, value, confidence_low, confidence_mid, confidence_high}` per year, or
   (b) `regime_tag` with a qualitative value (e.g. `inflation_regime: anchored | un-anchored`).
6. `time_profile` — natural horizon and shape (per §11.3 library); not all scenarios need to be 5- or 10-year.
7. `probability` — optional; only if the analyst is choosing to compute a side-blend per §3.3.
8. `consistency_checked` — boolean or note confirming the internal-consistency check (§6.6 deliverable 3) has been done.

---

## Workshop logistics (suggested)

Tara to confirm or adjust; this is just a starting structure.

1. **Pre-read** — this document, §6 of `design/architecture.md`, the executive summaries of the five institutional publications.
2. **Workshop format** — two half-day sessions, ideally with one peer reviewer (Ben, the strategist friend, or another). Single long session risks fatigue and convergent thinking.
3. **Session 1: divergent.** Work through the candidate-themes list, generate new candidates, discriminate using questions A.1–A.4. Output: a shortlist of 6–8 candidates.
4. **Session 2: convergent.** Apply count / span / time-profile / macro-variable questions to the shortlist; converge to 3–6 scenarios with names, narratives, and rough macro-variable trajectories. Output: a scenario set ready for YAML drafting.
5. **Post-workshop drafting.** Tara + Claude draft the YAMLs and narratives in subsequent chat sessions. The workshop's outputs in `design/scenarios_workshop.md` are the brief for those drafting sessions.

---

## What not to do in the workshop

1. Lock the count before doing the work. The 3–6 range exists precisely so the count emerges.
2. Adopt an institutional scenario set wholesale (e.g. just take IMF reference / adverse / severe). The institutions are constrained to a single primary forecast and downside tails; our framework can and should be more multidimensional.
3. Spend time debating probabilities. The framework's canonical output is comparative (§3.3). Probability assignment is optional and analyst-side, not central.
4. Try to cover every theme. Coverage is not the goal; spanning the plausible range with internally consistent, analytically discriminating scenarios is the goal (§6.2).
5. Defer schema-checking to "later". A scenario that can't be populated against §6.4 isn't a scenario in our framework. Use the §6.4 checklist as a definition-of-done filter.
