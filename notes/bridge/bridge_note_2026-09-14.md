VCC VALUATIONS — bridge note for a new chat, 14 September 2026. Supersedes the 26 August note.

READ THIS FIRST, IN THIS ORDER.

1. The session's commits are NOT PUSHED. `origin/main` was last at `d0f3adf`. Stephen must run `land_vcc.cmd` from a normal cmd window before any cloud clone is made — one command, it never changes, see "Landing a session" in CLAUDE.md. Cloning before that forks the repo.
2. Then `session_start.cmd`. Then CLAUDE.md (standing rules 3 and 4), the HANDOVER block in WORKING_NOTES.md, DECISIONS.md (D-48 to D-51 are new), and `analyses/dnl_item11_four_positions.md`.
3. Do NOT assert that data, a document or a prior decision does not exist until you have surveyed the directory that would hold it. Curated .yaml files in data/ are SUMMARIES; raw statements live in data/financials/*.csv, data/financials/historical/<company>/ (PDFs — extract with pdftotext -layout) and the extracted series in analyses/dnl_capex_history.yaml.

STATE: suite 302 (+2 opt-in `pytest -m libreoffice`, both passing), ratchet 13 checks, base ties green. DNL HAS MOVED: 2.831 → 1.989. CSL 195.78 and WBC 30.03 unchanged.

WHAT LANDED.
4. The operating base is DERIVED, not stored. `data/financials/dnl.yaml` carries the raw FY2024–FY2025 explosives-segment observations (revenue, EBITDA, D&A, capex, ex individually material items); the translator derives capital intensity 9.18%, depreciation intensity 8.24%, EBITDA margin 20.96% and EBIT margin 12.72%. The company file declares a WINDOW, not a number (D-16, D-48, D-50).
5. The transition-cost normalisation is a separate declared line, +0.35pp, sized only on the corporate-cost reduction actually reported ("Corporate costs reduced by $6m", 1H26, annualised). Deliberately not the full gap to the 1H26 run-rate, which also contains JV and other income of unproven persistence. Revisit at the FY26 result.
6. D-49 is in the engine: `capex_rule: grows_capital_base_at_g`. Opening invested capital is derived per D-44 and rolled forward on the valuation's own flows; terminal capex is D&A plus g × fixed base, 9.7–10.2% by scenario against D&A of 8.24%.
7. The generated workbook carries the invested-capital roll-forward AS FORMULAS and strikes terminal capex per scenario from it, so LibreOffice checks D-49 independently. It ties across all six scenarios.
8. The UI assumptions panel discloses capital intensity, depreciation intensity, the margin and its normalisation, and the terminal capex rule — each with entity, window, level and source.
9. Levels: Orderly 3.2740→2.3316, Muddle Through 2.8307→1.9895, AI Lag 2.7705→2.0127, Fragmentation 1.9926→1.2241, Disorderly 1.7015→0.9924, Stagflation 0.8061→0.0491.

THREE THINGS THAT NEED STEPHEN.
10. AI PRODUCTIVITY LAG NOW SITS ABOVE MUDDLE THROUGH (2.0127 vs 1.9895). Consequence of D-49, not a data error: AI Lag carries +0.5pp margin and a lower terminal growth, and a lower g also means a lower perpetual reinvestment call once terminal capex is D&A + g × fixed base. The ordering assertion in test_dnl_all_scenarios.py was updated to match, with the reasoning written down. Whether the scenario narrative supports it is a judgement.
11. Not every valuation breaches the 70% terminal threshold any more — AI Lag 69.3%, Stagflation 61.9%. The blanket test is replaced by one pinning each share. The §11.4.2 obligation is now case by case.
12. The USER OVERRIDE on capital intensity is NOT built; the disclosure is. The override needs the UI panel wired to the translator first — the sliders drive a reduced-form JS approximation and putting an engine input behind one would make the UI a second model of record (D-23).

NEXT.
13. Wire the UI panel to the translator, then add the override behind it.
14. The Porter work and the margin build still disagree about the gas contracts: the moat is declared as "scale + switching_cost + resource (long-term contracts)" with a 10–15 year decay horizon, but those contracts expire by FY2032, six years from the valuation date, and D-43 says a contractual expiry sets the horizon directly.
15. Item 11 is narrowed again but still open — analyses/dnl_item11_four_positions.md and analyses/dnl_item11_capital_intensity.xlsx.
16. Then D-42 the diagnostic, and D-35/D-36 the horizon rule and fade, which are still PROPOSED and still only live in the replica.

RULINGS OF 14 SEPTEMBER — FIRM, DO NOT REOPEN.
13. D-48 — capex intensity and depreciation intensity are a PAIR struck from one window and one entity, the longest available for the entity being valued, minimum two years, entity and window disclosed. The gap between them is then observed rather than assumed. The base EBIT margin is restated to hold the measured EBITDA margin. The average is derived from a committed series and never stored (D-16); the UI discloses it and permits a user override of the derived default (allowed under D-23 — an input, not a second engine).
14. D-49 — the terminal capital base grows at g. Terminal capex = depreciation + g × fixed base. Retires `capex_rule: equals_da` for DNL, superseding that half of D-13 and superseding D-39. Worth AUD 0.34 on Muddle Through.
15. D-50 — every rate declares the basis it was struck on: a sibling `<field>_basis` with entity, window, level, source. Ratchet check 13 enforces it on the checks 3 and 10 pattern. Six rates remain baselined in `tests/ssot_basis_baseline.json` — the four DNL fields the rule came from now declare.
16. D-51 — the workbook is a presentation layer, NEVER a source. A cell reference is not provenance. The data files are the single source of truth, sourced to the accounts; the workbook is regenerated from the data and never read back into it.

WHY D-50 EXISTS, SO IT IS NOT WATERED DOWN.
17. Four defects found across three sittings were one error wearing four hats: a capex rate from the pre-demerger group compared against a depreciation rate set to match it; a 12.8% headline dividing group capex by continuing-operations revenue; a depreciation rate anchored to an assumption rather than observed; a base EBIT margin whose stated cross-check is a pre-corporate segment range while the number is applied to a revenue base that carries corporate costs. Every one was a ratio assembled from parts that did not belong together.

STILL OPEN.
18. Item 11 is narrowed, not closed. Under the restatement capital intensity still falls from 108.3% to 79.3% and terminal ROIC is still 1.40× WACC. Four positions with full evidence in `analyses/dnl_item11_four_positions.md`; the live workbook is `analyses/dnl_item11_capital_intensity.xlsx`.
19. The Porter work and the margin build disagree about the gas contracts. The impact matrix declares the moat as "scale + switching_cost + resource (long-term contracts)", decay horizon 10–15 years. Those same contracts expire by FY2032, six years from the valuation date, and D-43 says a contractual expiry sets the horizon directly. The excess return should decay at least as fast as the margin resting on it.
20. Unchanged behind that: D-42 the diagnostic, the horizon rule and fade, the UI disclosure piece (now also carrying the D-48 entity/window/rates disclosure and the user override), then the remaining golden movement (CSL, behind D-06) with a workbook re-tie.
21. STILL PROPOSED: D-35 horizon, D-36 fade, D-37 archetype ten-year macro, D-38 capex convergence (now largely superseded by D-48 — re-read before citing), D-42 diagnostic, D-43 decay horizon. D-06 stays PROVISIONAL. D-19 prices refresh after the UI work.
22. The twelve goldens from 23 August are superseded: the six DNL levels moved with the restatement and are re-pinned; the six CSL levels still move when D-06 lands.

HOUSE RULES. Australian English. Number any list of 2+ points so Stephen can reply by number. Standing rule 3 — Stephen does not use CMD or git directly: give him ONE complete pasteable command, in a copy-button widget, EVERY time, say what "finished" looks like, then VERIFY THE RESULT YOURSELF over the device bridge rather than asking him to copy terminal output back. Standing rule 4 — any number that reaches a document must come from committed code, shipped in the same change as the document citing it. Ask via AskUserQuestion if a brief is unclear. Read `design/writing_style.md` before drafting prose meant for readers.

EDIT MECHANICS. Work in the CLOUD CONTAINER clone, not on the mount — the mount cannot delete or replace a file, so git merge, git checkout -- and git branch -D all fail there. The cloud container cannot push. Finished work travels as `session.bundle` written to the repo root; Stephen runs `land_vcc.cmd`. Both are gitignored. Keep domain numbers out of .py prose — the SSOT ratchet is comment-blind, and format specs like `:.2%` read as the literal 0.2.
