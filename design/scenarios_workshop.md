# Scenarios Workshop — Output

**Workshop date:** 16 May 2026
**Workshop format:** Interactive walkthrough between Tara and Claude across one extended session.
**Companion to:** `design/architecture.md` §2 (locked decision on 3–6 scenarios), §3 (open decisions including narrowed probability-weighting), §6 (Layer 1 scenario library), §6.4 (scenario schema), §16.1 (narrative deliverables), `design/scenarios_workshop_prep.md` (pre-workshop document).
**Status:** Workshop closed; six scenarios selected. Scenario YAMLs and narratives drafted under `data/scenarios/`.

---

## Outcome

The workshop selected **six scenarios**, comprising one most-likely interior case plus five boundary cases on different dimensions:

| # | Scenario | Role | Time horizon |
|---|---|---|---|
| 1 | Muddle Through | Interior, most-likely | 7–10 years |
| 2 | Orderly Convergence | Upside boundary | 5–10 years |
| 3 | Stagflation Persists | Downside boundary (macro) | 5–7 years |
| 4 | Fragmentation and Resource Nationalism | Boundary (geopolitical / trade) | 10–15 years |
| 5 | Disorderly Climate Crystallisation | Boundary (climate) | 5–10 years |
| 6 | AI Productivity Lag | Boundary (technology / productivity) | 7–10 years |

Six is at the §2 ceiling — used deliberately, not by accident. The set spans inflation regime, real-rates trajectory, geopolitical alignment, climate-policy posture, technology-productivity transmission, and demographic-response capacity.

---

## Process

The workshop followed the three-phase method set out in the prep document:

1. **Phase 1 — discriminate.** Eight candidate themes from the prep document were assessed against three tests: multidimensional differentiation, discrimination on test companies (IPL / CSL / WBC), and plausibility. Three quick keeps; five dig-ins.
2. **Phase 2 — develop.** For each scenario on the shortlist, settled name, multi-dimensional differentiation summary, time horizon, headline macro story, time-profile shape, test-company implications. Six one-page sketches produced.
3. **Phase 3 — drafting.** Conversion of sketches into structured YAML (per §6.4) and narrative `.md` (per §16.1). Documented separately under `data/scenarios/`.

---

## Phase 1 outcomes — what we did with the eight candidates

| Candidate | Disposition | Reasoning |
|---|---|---|
| Orderly Convergence | Kept (renamed unchanged; reframed as boundary, not central case) | Originally drafted as the "central / baseline" but reframed mid-workshop after Tara challenged the framing. See "Framing shift" below. |
| Stagflation Persists | Kept | Materially distinct from Orderly Convergence on inflation regime, real-rates trajectory, policy posture, growth. Multi-dimensional. |
| Fragmentation and Resource Nationalism | Kept | Uniquely covers the geopolitical / trade dimension; no other scenario sits in that space. Particularly important for testing IPL's global-trade exposure and WBC's Australian-domestic-economy resilience under bloc-realignment. |
| Disorderly Climate Transition | Kept, **reframed** as "Disorderly Climate Crystallisation" | The disorderly climate path is already in motion (see "Framing shift"); this scenario re-focuses on the crystallisation event (physical-loss event, carbon-price spike, stranded-asset cascade) rather than on whether the transition becomes disorderly. |
| AI-productivity boom | Dropped | Upside-AI case is captured between Orderly Convergence (AI-productivity-driven) and Muddle Through (AI in pockets). Doesn't need its own scenario. |
| AI-investment disappointment | Kept, **renamed** as "AI Productivity Lag" | Tara pushed back on the original "Tech-Investment Unwind" framing — investment will likely continue (deficit-funded, US-led capital available); what's contested is the *productivity transmission*. Renamed to capture the Solow-productivity-paradox dynamic. |
| Financial-condition shock | Dropped as standalone | Bank-archetype credit-cycle stress is adequately covered across Stagflation (recession-driven NPLs), Disorderly Climate (stranded-asset write-downs), and AI Productivity Lag (tech-lending observation). Adding as 7th scenario violates §2; marginal value below marginal cost. Acute financial-shock can be a stress-test variant within other scenarios if needed. |
| Demographic regime | Dropped as standalone, **kept as cross-cutting** | Demographic momentum is a fact across all scenarios — population cohorts already born. Demographic *response* is country-specific and scenario-conditional and is addressed in each scenario's narrative. Per Tara's specific point: cannot be treated as a separate scenario because the underlying fact is invariant. |

---

## Framing shifts during the workshop

Three framing shifts were made by Tara during the workshop and are worth recording:

1. **"What IS the baseline?"** Tara's challenge that climate action has already become disorderly under continued money-supply / inflation / cost-of-living pressure broke the original Orderly Convergence framing as a "central case". The scenario was reframed as the **upside boundary** — lower-probability than Muddle Through, but a meaningful upside anchor against which other scenarios are compared. Muddle Through was added as a new interior most-likely case.
2. **Boundary cases + most-likely interior.** Refining §6.2's "scenarios as boundary cases, not exhaustive coverage" commitment. The framework can support both boundary scenarios *and* a most-likely interior case, provided the most-likely is presented as one scenario among the set, not as a privileged baseline. §3.3 narrowed decision still holds: no blended expected-value canonical output. The §13 dashboard default view remains a multi-scenario comparison.
3. **US powerhouse as cross-cutting assumption.** Tara's view that the US economy is structurally stronger than consensus credits — a powerhouse — should inform every scenario's macro narrative. Handled implicitly in each scenario's narrative rather than as a structured regime tag (Tara's preference). Reflected in each scenario's headline story.

Two further refinements emerged through Phase 2:

4. **Climate-policy posture as cross-cutting dimension.** Climate is a dimension of every scenario, not a standalone. Each scenario's narrative addresses climate posture. The dedicated climate scenario (Disorderly Climate Crystallisation) tests the *crystallisation* event, not the *disorderly trajectory* (which is baseline).
5. **Demographic response as cross-cutting dimension.** China's bipedal-robotics-plus-AI approach is uniquely well-suited; advanced economies relying on immigration face a global skilled-migration pool that is itself diminishing (the late-2040s use-by date). Each scenario addresses demographic response country-by-country. **Surfaced a new architecture review item**: terminal-growth assumptions must reflect the demographic-adaptation trajectory of the company's primary geographies even when the cliff sits beyond the explicit forecast horizon (added as §9.7 item 9).

---

## Mapping to institutional scenario sets

| Our scenario | IMF WEO April 2026 | OECD Mar 2026 | World Bank GEP Jan 2026 | IEA WEO 2025 | NGFS Phase V |
|---|---|---|---|---|---|
| Muddle Through | Between Reference and Adverse | Baseline (with downside risks live) | Baseline with risk register active | Between STEPS and Current Policies | Current Policies (drift) |
| Orderly Convergence | Reference (optimistic read) | Baseline + upside factors realised | Baseline + bilateral trade progress | STEPS (delivered) approaching APS | Net Zero 2050 (orderly) |
| Stagflation Persists | Severe scenario | Downside tail (Middle East prolonged) | Downside scenario (sharp equity decline) | n/a (climate-focused) | n/a |
| Fragmentation and Resource Nationalism | Severe + fragmentation framing | Risk register (trade barriers, geopolitical) | Primary downside risk register | Bifurcated regional pathways (implicit) | Divergent Net Zero (implicit) |
| Disorderly Climate Crystallisation | n/a (climate not in WEO baseline) | Climate risk register | Extreme weather risk | Net Zero 2050 (stressed delivery) | Disorderly transition + Phase V physical-risk update |
| AI Productivity Lag | Implicit downside risk on tech | Downside risk register (AI returns disappoint) | Risk register (tech-led investment slows) | n/a | n/a |

**Observations on the mapping:**

6. **No institution publishes a "Muddle Through" central case.** Every published forecaster either anchors to a Reference / Baseline or pursues a normative pathway (IEA NZE, NGFS Net Zero). Muddle Through sits *between* the institutional baseline and the institutional downside — closer to what professional forecasters quietly believe than to what any of them publishes. The framework's distinctive analytical move on this dimension.
7. **Stagflation Persists and Disorderly Climate map cleanly to institutional severe / disorderly scenarios** — our work on those overlaps well with what's published.
8. **Fragmentation has no clean institutional analogue.** Most institutions treat it as a risk-register item, not a modelled scenario. Our explicit treatment is more analytically ambitious than institutional baselines on the geopolitical dimension.
9. **AI Productivity Lag is similarly under-published.** OECD treats it as a downside-risk paragraph; nobody publishes a full scenario around it. Distinguishing analytical move on the technology / productivity dimension.

---

## Indicative headline-macro comparison

Midpoints of headline ranges from the scenario sketches. Advanced-economy aggregates for inflation and real rates; global aggregate for growth. **Indicative only**; structured time series are in the YAMLs.

| Scenario | CPI inflation % | Real policy rate % | Global GDP growth % |
|---|---:|---:|---:|
| Muddle Through | 3.0 | 1.0 | 2.3 |
| Orderly Convergence | 2.3 | 0.8 | 3.2 |
| Stagflation Persists | 5.0 | 2.5 | 1.8 |
| Fragmentation | 3.5 | 1.5 | 2.0 |
| Disorderly Climate Crystallisation | 4.0 | 1.5 | 2.0 |
| AI Productivity Lag | 3.0 | 1.0 | 1.9 |

**A diagnostic finding from this comparison.** Four of the six scenarios (Muddle Through, Fragmentation, Disorderly Climate, AI Productivity Lag) cluster together on headline macro. The discrimination between them lives in **structural dimensions** — sectoral dispersion, supply-chain patterns, climate-policy posture, AI-rent distribution, terminal-state implications — not in inflation / real-rates / growth.

Implications:

10. **Macro-only comparison under-reads the scenario set.** Anyone looking at only the headline macro chart would see Stagflation and Orderly as the interesting scenarios and conclude the other four are similar. They are not; the discrimination is structural.
11. **The §13 dashboard tab must include structural comparisons**, not just macro fan charts. Worth adding climate posture, AI penetration, fragmentation intensity, US powerhouse stance, demographic-adaptation capacity as comparison dimensions in the headline view.
12. **In scenario population (Phase 3) the qualitative / regime variables matter as much as the macro time series.** Don't under-populate regime tags and narrative sections in favour of macro tables — that's where most inter-scenario differentiation lives.

---

## What was deliberately not done

13. **Probability assignment.** Per §3.3 narrowed decision, the framework supports optional per-scenario probabilities for analyst-side indicative blends but does not present a blended expected-value canonical output. Workshop chose not to populate probability fields in the YAMLs at this stage; can be added later if individual analysts find them useful for their own work.
14. **Sub-regional macro variable trajectories.** YAMLs carry advanced-economy and global aggregates. Country-level trajectories (US, China, Europe, Australia) are addressed in the narratives and will be added to structured form when scenarios are applied to companies whose valuation depends on a specific national trajectory.
15. **Stress-test variants.** Acute financial-shock and other stress-test variants within scenarios are not populated at workshop close; can be added under §10.4 as override mechanisms when specific stress-tests are needed.
16. **Sectoral dispersion data.** Each scenario has narrative on which sectors win and lose; structured sectoral data is not yet in the YAMLs. To be populated as scenarios are applied to actual archetypes in Step 5 onward.

---

## Cross-cutting principles confirmed at workshop close

17. Scenarios are boundary cases except for the most-likely interior (Muddle Through). The set spans the plausible range; it does not aim for exhaustive coverage. (§6.2 with workshop refinement.)
18. Comparative output is canonical; the dashboard default view is a multi-scenario comparison. No scenario is privileged as "the answer". (§3.3.)
19. Climate posture, US powerhouse stance, and demographic response are cross-cutting dimensions addressed in each scenario's narrative — not structured regime tags. (Tara's preference, workshop decision.)
20. Terminal-growth assumptions per company must reflect the scenario's demographic-adaptation trajectory, even when the cliff sits beyond the explicit forecast horizon. (§9.7 item 9, surfaced from this workshop.)
21. Scenario set will be reviewed at the §6.5 six-month refresh cadence; first review November 2026.

---

## Next deliverables

22. `data/scenarios/<scenario_id>.yaml` × 6 — structured per §6.4. Drafted alongside this document.
23. `data/scenarios/<scenario_id>.md` × 6 — narrative per §16.1. Drafted alongside this document.
24. Cross-check against `design/architecture.md` §6.7 (Scenario library review items) — confirm any items that the workshop resolved.

End of workshop output.
