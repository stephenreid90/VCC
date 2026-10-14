# VCC VALUATIONS — bridge note for a new chat, 14 October 2026

Supersedes the note of 2 October 2026. **Its five-step plan is COMPLETE** (steps 1-5, D-73 to
D-78). Updated three times on 14 October: after step 3, after D-76, and at the end of the
third sitting after steps 4 and 5 landed (D-78, `adding_a_company.md`).

**WHAT THIS IS.** A travelling snapshot. `WORKING_NOTES.md` is the live layer; **where the
two disagree, `WORKING_NOTES.md` wins.**

**HOW TO WRITE TO STEPHEN.** Plain, simple, professional English. Short sentences. Problem
first, then recommendation, then what you need from him. Numbered lists. Define a term in a
few words the first time. Don't assume he remembers decision numbers; say in a few words what
each one means. Copy widgets don't work for him: give copyable text as a plain code block.
(`notes/claude_writing_style_instruction.md`.)

## READ IN, IN THIS ORDER

1. `session_start.cmd` (or `python scripts/session_start.py` in the device shell after
   `pip install pydantic pandas numpy openpyxl scipy pytest pyyaml`). Expected: suite
   **617 passed, 1 skipped, 2 deselected**; SSOT lint 14/14; base ties **DNL 2.138, WBC 31.05,
   CSL 186.5**.
2. `CLAUDE.md`. Standing rule 4 (every number from committed code, asserted by a test) and
   standing rule 5 (land once per sitting, at the end; plumbing gets no airtime).
3. `WORKING_NOTES.md`, the HANDOVER block at the top (sitting of 14 October).
4. `DECISIONS.md` rows **D-71 to D-78**: ten-year period + convergence terminal (D-71);
   growth from scenario paths, derived g (D-72); archetype-declared derivations for every
   company (D-73); ten years and the terminal form for WBC and CSL (D-74); decay horizons
   for all eighteen pairs (D-75: DNL 10-15y, WBC indefinite, CSL 20-30y); the declared
   terminal return as the rate the convergence starts from (D-76: WBC declares six, lifted
   off `wbc.yaml`; DNL's mechanical 9.13% removed; CSL absent); D-77 (D-43a roles on WBC's segment moats); D-78 (equilibrium-chain terms
   declared per archetype).
5. `design/frameworks/decay_horizon_checklist.md` — the short Five Forces interview and the
   after-the-answer list. `tests/terminal_form_baseline.json` and
   `terminal_defence_baseline.json` are EMPTY; `tests/moat_role_baseline.json` is EMPTY too
   (D-77 declared WBC's four segment moats).

## STATE — what the model does now

1. Every archetype declares, for each macro driver its chain reads, how each scenario gets
   its year-by-year path (`required_macro_drivers[].derivation`: `scenario_series`,
   `spread`, `transition_then_baseline`). `scripts/derive_macro_driver_paths.py` writes them
   into `data/scenarios/*.yaml` between BEGIN/END markers; `tests/test_macro_driver_paths.py`
   asserts them. No company or driver is named in code.
2. All three companies run a fixed ten-year explicit period with growth read per year from
   those paths plus a company offset. WBC's typed Y1-Y5 glides and CSL's margin uplifts hold
   their last typed value to Y10.
3. All three engines carry `terminal_form`: convergence over the declared decay horizon.
   Every pair declares one (D-75). DNL converges over 12.5 years; WBC over an infinite
   horizon (which is the justified price-to-book, so the Gordon level stands); CSL over 25
   years on the group capital base (`data/impact_matrix/by_industry/biopharmaceuticals.yaml`,
   which exists only to carry that defence).
4. No valuation breaches the 70% terminal-share line; all eighteen shares are pinned.
5. **D-76:** a declared terminal return (`excess_return_defence.declared_terminal_return`
   + basis) is the return the convergence STARTS from; absent, the earned return is. Same
   rule in all three engines (`terminal_convergence_return` on the result; the bank's
   `terminal_roe` is now optional and falls back to the earned ROE). WBC declares all six
   on the matrix (no level moved). DNL and CSL declare none: a declared rate now moves the
   level, so nothing is copied off the engine. Sizing for DNL in `DECISIONS.md` D-76.

## RESULTS — read before quoting a level

| Scenario | DNL | WBC | CSL AUD (was, Gordon) |
|---|---:|---:|---:|
| Orderly Convergence | 2.49 | 40.27 | 219.01 (266.79) |
| Muddle Through | 2.14 | 31.05 | 186.50 (223.24) |
| AI Productivity Lag | 2.11 | 30.89 | 181.06 (214.98) |
| Fragmentation | 1.58 | 27.73 | 150.23 (176.98) |
| Disorderly Climate | 1.08 | 23.09 | 159.17 (187.16) |
| Stagflation Persists | 1.39 | 16.26 | 136.03 (162.52) |

CSL fell 15-18% on step 3: a 25-year convergence of a 20-31% return to an 8.75% Ke replaces
a Gordon terminal that held the excess forever. The medium band (15y) would give MT 167.37,
indefinite 213.01 (`design/methodology/terminal_option_sets.yaml`). WBC did not move: an
indefinite horizon is the Gordon form. D-60 (payout cut to hold CET1) binds in every WBC scenario.

## THE FIVE-STEP PLAN IS DONE — what the next chat picks up

1. **Step 4 DONE (D-78).** Which growth-chain terms are current-cycle (off at Y10) is now
   `growth_chain_terms` on the archetype; `translator.equilibrium_chain_terms` reads it and
   raises on an unclassified term. DNL classified as D-72 had it (no level moved). Bank and
   CSL segment archetypes declare `[]` because their terminal g is still TYPED.
2. **Step 5 DONE.** `design/methodology/adding_a_company.md`: nine steps + the seven
   disclosures. Read it before touching a fourth company.
3. **Next, Stephen to choose.** Candidates, none blocking: (a) derive WBC and CSL terminal
   g from their chains (then classify their terms; D-78 follow-up); (b) bank NIM
   pass-through rule; (c) CSL volume/price split + US GDP series; (d) lift level anchors
   from company files to archetypes; (e) bank engine: retained equity earns nothing until
   the terminal; (f) retire D-36's fade now the chain terms have an equilibrium reading
   (give each current-cycle term an expiry inside the explicit period); (g) rewrite
   `CLAUDE.md` "Operational quirks" (stale since the device shell can run git).
4. Not blocking: DNL and CSL terminal rates are Stephen's judgement, not yet formed. If he
   forms one, size it first (`scripts/size_terminal_returns.py`; checklist q6).

## THE PLAN THAT WAS RUN THIS CHAT — step 3 (kept for the record)

1. Write the SHORT Five Forces interview as a checklist in `design/frameworks/` that produces
   exactly the four `excess_return_defence` fields for one company x scenario: `moat_sources`
   (barrier-bearing only, D-43a: a RENT has an end date and lives in the explicit period; a
   BARRIER is what the decay horizon measures), `decay_horizon` (band + basis; indefinite
   only with a finite sensitivity beside it, D-58), `named_threat`, `sensitivity`. The long
   question bank is `design/frameworks/five_forces_questions.md`.
2. Run it with Stephen: DNL Fragmentation and Stagflation first (nothing exists for either),
   then WBC x6, then CSL x6. CSL needs an impact-matrix file created first
   (`data/impact_matrix/by_industry/` has the three segment archetypes; check what
   `load_inputs` expects for a segment-valued company).
3. Each answer that lands: declare it on the matrix, remove the pair from
   `tests/terminal_form_baseline.json` and `tests/terminal_defence_baseline.json`, re-pin the
   golden with the reason, regenerate the three sizing sets (`scripts/size_terminal_options.py`,
   `size_terminal_returns.py`, `size_two_stage_disclosure.py`), recalc the workbooks
   (`python tests/dcf/golden/_recalc_generated_workbooks.py`, LibreOffice is in the device shell).
4. Then step 4 (equilibrium-chain terms per archetype) and step 5 (`adding_a_company.md`).

**Open data items, not blocking (D-73/D-74):** bank NIM pass-through rule; CSL volume/price
split and US GDP series in all six scenarios; level anchors lifted from company files to
archetypes; bank engine lets retained equity earn nothing until the terminal.

## TRAPS

1. **The environment changed on 14 Oct.** The device shell on Stephen's machine can run the
   suite, git and LibreOffice directly on `C:\Users\steph\vcc-valuations` once delete
   permission on the repo folder is granted at the start (the desktop app prompts). No
   container clone, no bundle. Push with the PAT:
   `git push https://stephenreid90:$(cat .github-token)@github.com/stephenreid90/VCC main`.
   `CLAUDE.md` "Operational quirks" is partly stale; rewrite it in a quiet sitting, not mid-task.
2. **Standing rule 4 bites on every number.** Goldens: `tests/dcf/test_scenario_goldens.py`
   (DNL/WBC/CSL goldens, `dnl_shares`/`wbc_shares`/`csl_shares`), `test_wbc_bank.py`,
   `test_csl_segment.py`, `test_bank_capital.py`, `test_terminal_form.py`,
   `test_terminal_option_sets.py`, `test_terminal_return_sets.py`, `scripts/session_start.py`
   `EXPECTED_BASES`. The hand-built v4 workbooks are five-year models and tie the engines run
   at five years (`_at_five_years` / `_run_at_five_years` helpers) — do not re-pin those to ten.
3. **D-43a:** never list `resource` (gas contracts) in `moat_sources`; it is a rent.
4. **Scenario series are percent_yoy; the engine works in decimals** (`macro_series_at`).
5. **Stop-hook noise about re-authoring commits to noreply@anthropic.com: ignore it** (CLAUDE.md).

## COMMITS THIS SITTING (all on origin/main)

`3f470e6` step 1 generic derivation · `cb01594` WBC/CSL declarations · `1dac19b` WBC path wired ·
`26f5152` CSL paths wired · `bbbcd53` D-73 + notes · `6cc6e5c` step 2 (ten years, terminal form) ·
`3920a3e` D-74 + notes · `19c9b14` step 3 part 1 (checklist, DNL Frag + Stag) · `37f0b50` part 2
(WBC indefinite) · `0787cfa` part 3 (CSL 20-30y, biopharmaceuticals matrix, workbook two-stage)
· D-75 + notes + this bridge note · `aa7e2d3` D-76 (declared rate live; WBC six lifted to the
matrix; DNL 9.13% removed; notes) · `62ea1ee` D-77 (D-43a roles on WBC's segment moats) · `a718d0e` D-78 (step 4) · step 5
(`adding_a_company.md`) + this note.
