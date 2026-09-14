VCC VALUATIONS — bridge note for a new chat, 14 September 2026. Supersedes the 26 August note.

READ THIS FIRST, IN THIS ORDER.

1. The session's commits are NOT PUSHED. `origin/main` was last at `d0f3adf`. Stephen must run `land_vcc.cmd` from a normal cmd window before any cloud clone is made — one command, it never changes, see "Landing a session" in CLAUDE.md. Cloning before that forks the repo.
2. Then `session_start.cmd`. Then CLAUDE.md (standing rules 3 and 4), the HANDOVER block in WORKING_NOTES.md, DECISIONS.md (D-48 to D-51 are new), and `analyses/dnl_item11_four_positions.md`.
3. Do NOT assert that data, a document or a prior decision does not exist until you have surveyed the directory that would hold it. Curated .yaml files in data/ are SUMMARIES; raw statements live in data/financials/*.csv, data/financials/historical/<company>/ (PDFs — extract with pdftotext -layout) and the extracted series in analyses/dnl_capex_history.yaml.

STATE: suite 302 (+2 opt-in `pytest -m libreoffice`, both passing), ratchet 13 checks. THE DNL BASES HAVE MOVED: 2.831 → 2.390. CSL 195.78 and WBC 30.03 unchanged.

WHAT WAS DONE — the Denali operating base is restated and landed.
4. All four operating rates now come from one entity, one window, one level: explosives segments (DNAP + DNA + DNEL + corporate), FY2024–FY2025, ex individually material items, from the FY25 annual report segment note and capex table. base_ebit_margin 14.10% → 12.72%; da_pct_revenue 7.30% → 8.24%; capex path and stub 8.0%/7.0% → 9.18% flat; implied EBITDA margin 21.40% → 20.96%. Each carries a D-50 basis block.
5. Six DNL goldens moved: 3.2740 → 2.7980, 2.8307 → 2.3900, 2.7705 → 2.3506, 1.9926 → 1.5599, 1.7015 → 1.2671, 0.8061 → 0.3872. Terminal ROIC on Muddle Through 14.94% → about 12.4% (1.68× → 1.40× WACC). Terminal share 72.7% → 74.5%, so the §11.4.2 obligation still bites.
6. The generated-workbook oracle was regenerated and ties across all six scenarios; both `-m libreoffice` tests pass. The independent check survived the restatement.
7. The v6 audited oracle was deliberately NOT restated. `tests/dcf/golden/dnl_mt_inputs.py` is frozen at the v6 audit and says so in its docstring. DO NOT restate it when data moves — it is the only hand-audited oracle in the project and restating it retires it silently. The two field-by-field comparisons the restatement broke are excepted, with the reason written down.
8. The duplicate margin is gone: `normalised_baseline.ebit_margin: 0.135` deleted (D-16 — the engine read the other one).
9. Published tables are now permanently reproducible: every set in `design/methodology/horizon_variant_sets.yaml` carries an `operating_base` block freezing the rates it was struck on, so a later restatement cannot regenerate a different table under the same name. `post_restatement` is the new `current` set.

NEXT.
10. The transition-cost normalisation, as a SEPARATE declared line — never folded into the base rate. FY24 and FY25 are a business coming out of a demerger. Evidence that corporate cost falls: 1H26 explosives EBITDA margin runs about 22.3% against the FY24–FY25 average of 20.96%, and the 1H26 commentary records corporate costs down $6m. Size it, source it, declare it.
11. Implement the D-48 UI piece: move `analyses/dnl_capex_history.yaml` into `data/financials/`, have the translator DERIVE the averages rather than read a stored number (D-16), and wire the disclosure entry plus the user override.
12. D-49 is ruled but NOT implemented in the engine. The terminal still runs `capex_rule: equals_da`, which now means 8.24%. Growing the capital base at g needs the invested-capital roll-forward wired into the engine, not just the replica.

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
