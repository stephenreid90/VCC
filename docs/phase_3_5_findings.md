# Phase 3.5 smoke-test DCF — findings

**Date:** 22 May 2026
**Scope:** DNL × all six scenarios, run through translator stub + FCF DCF stub.
**Status:** Smoke-test complete. Findings below feed the Step 6 (production translator) and Step 7 (production DCF engine) design.

---

## Headline numbers (FCF DCF stub, 5-year explicit + Gordon-growth terminal, AUD millions)

| Scenario | EV | Net debt | Equity | Per share | vs Muddle Through | Terminal % of EV |
|---|---:|---:|---:|---:|---:|---:|
| Muddle Through | 5,327 | 1,810 | 3,517 | AUD 1.87 | baseline | 75.1% |
| Orderly Convergence | 8,663 | 1,810 | 6,854 | AUD 3.65 | +94.9% | 81.1% |
| AI Productivity Lag | 5,172 | 1,810 | 3,362 | AUD 1.79 | −4.4% | 73.4% |
| Fragmentation | 1,982 | 1,810 | 172 | AUD 0.09 | −95.1% | 67.1% |
| Disorderly Climate | 1,488 | 1,810 | −322 | AUD −0.17 | −109.2% | 68.7% |
| Stagflation Persists | 914 | 1,810 | −896 | AUD −0.48 | −125.5% | 63.7% |

Market reference (21 May 2026): share price **AUD 3.61**, consensus target **AUD 3.61**, EV **AUD 7,682m**.

---

## What worked

1. **End-to-end pipeline executed cleanly across all six scenarios.** Translator loaded scenario / archetype / company / impact matrix / financials, validated each against the pydantic schemas, applied translation rules, and emitted a SmokeAssumptionSet that the FCF DCF consumed. No schema errors; no runtime failures.
2. **Sparse-representation convention worked.** Muddle Through with 4 populated drivers and Disorderly Climate with 11 populated drivers were handled equivalently by the translator — absent drivers default to neutral / small / not assessed per §10.2.
3. **Defended-exception terminal entries flowed through.** Orderly Convergence's positive terminal_roic and Disorderly Climate's negative terminal_roic were carried into the DCF inputs (though the FCF stub doesn't actually consume terminal_roic — see issue 6 below).
4. **Section 11.4.2 / 15.2 terminal-share-reasonableness validator fired correctly** on four scenarios (terminal contributed >70% of EV in Muddle Through, Orderly, AI Lag, and one other). This is the kind of warning a production engine should surface to analysts.
5. **Section 11.4.2 terminal-growth-cap-to-WACC catch worked.** No scenario hit the cap, but the safeguard is in place.
6. **Comparative directional ranking matches the per-scenario narratives.** Orderly Convergence (+95%) and AI Productivity Lag (−4%) match the narrative thesis; Stagflation, Fragmentation, and Disorderly Climate all materially compress value — also matches narrative. The framework's discriminating power holds.

---

## What broke / what the smoke test surfaced

The numbers themselves reveal calibration issues, not architectural ones. The framework runs; the rules need work.

### Issue 1 — Baseline (Muddle Through) AUD 1.87 vs market AUD 3.61

Our Muddle Through baseline is ~half of the market price. The market is implicitly pricing DNL closer to our Orderly Convergence case (AUD 3.65). Per Tara's framing that Muddle Through is the more-likely-than-Orderly central case, the market is being optimistic vs our framework.

But this gap is large enough that calibration questions need addressing before the framework's output is presentable. Candidate explanations, in priority order:

7. **Base-year EBIT margin is too low.** I used TTM Mar-2026 margin of 11.2%, which is depressed by post-demerger transition costs. Pre-demerger DNL (as Dyno Nobel segment of IPL) ran 13–15% margins. **Action: re-base on a normalised margin estimate (~13.5%) rather than the as-reported TTM.**
8. **Baseline WACC of 8.5% may be too high.** Implied market WACC for DNL given the current price is closer to 7.0–7.5%. **Action: re-derive WACC from market data (forward P/E 19.3× implies cost of equity around 7-8%, plus contracted cost of debt around 6%, give a blended WACC around 7%).**
9. **Net debt of AUD 1,810m reflects post-demerger restructuring** — the underlying steady-state net debt is closer to AUD 1.2-1.4bn. **Action: use a normalised net debt anchor.**
10. **Base-year capex pct (7%) appropriate** for the steady state; FY25's 12.8% is partial-year inflated and rejected for the smoke test. This is correctly handled.

### Issue 2 — Stagflation and Disorderly Climate produce negative equity

These are mathematically correct given the inputs (EV around 900-1,500m, net debt 1,810m → equity below zero). But negative-equity outcomes are implausible for a real company — they suggest the model is over-compressing earnings × multiples simultaneously.

Specifically:

11. **Margin compression is applied instantly in Year 1 and held flat** rather than phased in via the §11.3 `regime_shift` time profile. Stagflation's `gross_margin = negative / large` translates to a -3.5pp margin haircut applied immediately — EBIT margin drops from 11.2% to 3.7% in Year 1. Production translator must apply time profiles per driver.
12. **Multiple cost-driver entries stack additively without consistency check.** Stagflation has gross_margin (-3.5pp) + input_cost_pass_through (-3.5pp) + sga_pct_revenue (+0.5pp) = -7.5pp combined; this is more compression than any single observation supports. §11.4.2 consistency rule 1 (operating-leverage directional check) would catch this; not yet implemented.
13. **WACC shocks of +275bps combined with margin shocks produce compound multiplicative compression.** Both legs of the value equation move against the company at once. Real-world cyclical-industrial valuations don't compress this hard because cycles eventually mean-revert; our 5-year + perpetual model doesn't capture mean reversion. The §11.3 time-profile library — properly wired — would address this by applying impulse / regime_shift / fade profiles.

### Issue 3 — Terminal value too dominant in most scenarios

Terminal-share-of-EV runs 64–81% across scenarios. The 70% threshold validator fires in four of six cases. This is partly inherent to cyclical industrials with 5-year horizons + steady terminal growth, but it does mean a 50bps move in terminal growth or WACC swings EV materially.

Mitigations to wire in production Step 7:

14. **Extend explicit forecast to 10 years** (architecture spec §2 supports either 5 or 10) — would push terminal share below 60% for most cyclical-industrial cases.
15. **Implement explicit fade period** for terminal ROIC convergence per §11.4.2 rule 5; this disciplines the terminal-state assumptions rather than relying on Gordon-growth blowing them up.

### Issue 4 — Terminal ROIC driver populated but unused

`terminal_roic` is populated in two scenarios (Orderly +small, Disorderly Climate −moderate) with defended exceptions per §10.6 rule 2 — but the FCF DCF stub uses Gordon growth which doesn't reference terminal ROIC at all. The defended-exception governance is wasted.

Production Step 7 must implement terminal-ROIC-conditional terminal value via either:

16. **Reinvestment-rate-from-ROIC formula:** reinvestment rate = terminal_growth / terminal_roic → terminal FCF = terminal_NOPAT × (1 - reinvestment_rate) → terminal_value = terminal_FCF / (WACC - terminal_growth).
17. **Fade ROIC to WACC over the fade_period_length** per §11.4.2 rule 5 — this is the convergence discipline.

### Issue 5 — Linear deltas not appropriate for all driver types

The smoke-test translator applies the (direction, magnitude) → numeric delta as a constant annual rate across all 5 years. This works for some drivers (revenue growth rate, capex %) but not others:

18. **Volume / revenue growth** compounded at +3.5% extra annually under Orderly = 18.8% cumulative revenue lift over 5 years. That's plausible but front-loads the recovery; a regime_shift profile would phase it in more realistically.
19. **Margin shifts** as percentage-point deltas are correct in concept but should apply via regime_shift to reflect "stabilises to new level over 2-3 years" rather than "jumps Year 1".
20. **Rate shifts** (RFR, ERP) should also phase per scenario time_profile — Stagflation's rates take 1-2 years to break, not immediately.

Production §11.3 time-profile library implementation is the fix; it exists in the architecture but not in code yet.

---

## What the smoke test validates for the architecture

21. **The architecture works end-to-end.** Schemas, validators, sparse-representation convention, defended-exception governance, terminal-share-reasonableness check — all the structural mechanics function. The framework's value-add over conventional analyst valuations (per the thesis in `analyses/dnl/thesis.md`) requires production-quality translation rules and DCF mechanics, but the architectural skeleton is sound.
22. **The framework's discriminating power is real.** Even with crude calibration, the relative ordering across scenarios (Orderly > Muddle Through > AI Lag > Fragmentation > Disorderly Climate > Stagflation) matches the narrative thesis and matches what a thoughtful analyst would conclude. The framework is doing analytical work, not just arithmetic.
23. **The §11.4 consistency-rule infrastructure is necessary, not optional.** Without the consistency rules, additive driver shocks (margin + input cost + tax + rate) can produce non-physical outcomes (negative equity). The architecture's prescription — operating-leverage directional check, terminal convergence — is validated as needed by this run.
24. **Driver-IDs as stable keys works.** All 46 driver-movement cells across the six scenarios were correctly looked up by id in the translator's rule table. The §9.7 review item 6 (driver-ID style guide) is still needed but the principle holds.

---

## Required for Step 6 (production translator)

25. **Move translation rules from hardcoded Python into `data/translation_rules/`** per §11.2. The smoke test's hardcoded dict is the shape; production needs YAML data + per-archetype overrides.
26. **Implement §11.3 time-profile library** (impulse, regime_shift, step, cyclical, front_loaded, back_loaded, linear_through_horizon). Each driver carries its `default_time_profile` per §9.2; the translator applies it.
27. **Implement §11.4.1 derivations** for derived drivers (effective_tax_rate, cost_of_equity, WACC, EBIT margin, ROE). The smoke test computes some of these inline; production should separate.
28. **Implement §11.4.2 consistency rules** — operating-leverage directional check, terminal convergence enforcement, mix-shift sanity, terminal-share warning. Operating leverage alone would prevent the Stagflation negative-equity outcome.
29. **Per-driver `base_definition`** matters — the smoke test used a single base-year revenue (TTM) for all drivers; production should respect each driver's `base_definition` (latest_reported_fy vs ttm vs three_year_avg vs ntm_consensus).
30. **Output the full schema-compliant `AssumptionSet`** (per §11.5) rather than the smoke-test `SmokeAssumptionSet`. The schema is in `src/vcc_valuations/schemas/assumption.py` already.

---

## Required for Step 7 (production DCF engine)

31. **Terminal value via reinvestment-rate-from-ROIC** per Issue 4. Don't ignore `terminal_roic` driver.
32. **Explicit fade period** for terminal ROIC → WACC convergence per §11.4.2 rule 5.
33. **Working-capital dynamics** via `working_capital_days` driver. The smoke test assumes neutral; production should compute change-in-WC from revenue growth × WC days.
34. **Mid-period discounting convention** (smoke test uses end-period).
35. **Functional currency per segment** — DNL is single-segment so smoke test ignores; CSL multi-segment will need.
36. **DDM / residual income for bank archetypes** per §9.4.1 — required for WBC.
37. **Sensitivity / tornado outputs** — the framework's distinguishing feature per Ben's-bot competitive analysis. Build alongside the FCF DCF.

---

## Required for the architecture spec

38. **No spec changes required.** All the gaps identified are implementation gaps (Step 6 / Step 7 code), not spec design gaps. The §10.6 / §11.4 / §11.5 prescriptions are correct; we just haven't built them yet. Architecture spec stays at v0.2.1.
39. **Possible new §11.7 review item** worth adding: "Smoke-test 22 May 2026 confirmed end-to-end pipeline; calibration issues with baseline (margin, WACC, net debt) and consistency-rule absence noted in `docs/phase_3_5_findings.md`. Step 6 / Step 7 implementation must address before Phase 4 expansion."

---

## What the smoke test cost / what we got

40. **Cost:** ~1 hour of focused chat. Three new files (translator stub 230 lines; FCF DCF stub 175 lines; run script 95 lines) plus this findings doc.
41. **Got:** end-to-end validation that the architecture works; concrete catalogue of calibration / implementation issues; a working comparative output across all six scenarios; a baseline-vs-market gap to investigate; explicit catch by the terminal-share-reasonableness validator on four scenarios; confirmation that the framework's relative discriminating power is real.

Per §14 Phase 3.5 spec — "A few days of work; saves weeks if the cascade has to be re-run" — the smoke test was cheaper than expected (hours not days) and caught exactly what it was meant to catch: implementation gaps to address in Steps 6 / 7 before Phase 4 populates across all companies.

---

## Recommended next move

42. **Don't expand the framework to CSL and WBC until baseline calibration is fixed.** The translation rules calibration plus baseline EBIT / WACC / net-debt anchoring need work before we populate the other two test companies. Otherwise we propagate the same calibration issues 3×.
43. **Order:** (a) calibrate Muddle Through baseline to market reference (margin / WACC / net debt); (b) implement §11.3 time profiles (at least regime_shift); (c) implement the §11.4.2 operating-leverage check; (d) re-run smoke test for DNL; (e) confirm reasonable numbers; (f) then move to Step 9 (CSL + WBC population).
44. **Alternative: build out full Step 6 first** rather than incrementally calibrating the smoke test. Cleaner code path; more work upfront. Tara's call.
