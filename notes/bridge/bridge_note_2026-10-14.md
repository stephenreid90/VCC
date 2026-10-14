# VCC VALUATIONS — bridge note for a new chat, 14 October 2026

Supersedes the note of 2 October 2026 (its five-step plan still stands; steps 1 and 2 are done).

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
   **593 passed, 1 skipped, 2 deselected**; SSOT lint 14/14; base ties **DNL 2.138, WBC 31.05,
   CSL 223.24**.
2. `CLAUDE.md`. Standing rule 4 (every number from committed code, asserted by a test) and
   standing rule 5 (land once per sitting, at the end; plumbing gets no airtime).
3. `WORKING_NOTES.md`, the HANDOVER block at the top (sitting of 14 October).
4. `DECISIONS.md` rows **D-71 to D-74**: ten-year period + convergence terminal (D-71);
   growth from scenario paths, derived g (D-72); archetype-declared derivations for every
   company (D-73); ten years and the terminal form for WBC and CSL (D-74).
5. `tests/terminal_form_baseline.json` — the 14 company x scenario pairs with no decay
   horizon. That list is the worklist for this chat.

## STATE — what the model does now

1. Every archetype declares, for each macro driver its chain reads, how each scenario gets
   its year-by-year path (`required_macro_drivers[].derivation`: `scenario_series`,
   `spread`, `transition_then_baseline`). `scripts/derive_macro_driver_paths.py` writes them
   into `data/scenarios/*.yaml` between BEGIN/END markers; `tests/test_macro_driver_paths.py`
   asserts them. No company or driver is named in code.
2. All three companies run a fixed ten-year explicit period with growth read per year from
   those paths plus a company offset. WBC's typed Y1-Y5 glides and CSL's margin uplifts hold
   their last typed value to Y10.
3. All three engines carry `terminal_form`: convergence over the declared decay horizon
   where one exists, Gordon fallback otherwise. DNL: four of six converge. WBC and CSL:
   Gordon everywhere (no decay horizon declared; CSL has no impact-matrix file at all).
4. No valuation breaches the 70% terminal-share line; all eighteen shares are pinned.

## RESULTS — read before quoting a level

| Scenario | DNL | WBC (was, 5y) | CSL AUD (was, 5y) |
|---|---:|---:|---:|
| Orderly Convergence | 2.49 | 40.27 (36.23) | 266.79 (228.32) |
| Muddle Through | 2.14 | 31.05 (30.03) | 223.24 (195.78) |
| AI Productivity Lag | 2.11 | 30.89 (29.72) | 214.98 (191.75) |
| Fragmentation | 1.58 | 27.73 (27.11) | 176.98 (162.11) |
| Disorderly Climate | 1.08 | 23.09 (22.61) | 187.16 (170.18) |
| Stagflation Persists | 1.39 | 16.26 (18.70) | 162.52 (156.87) |

Every WBC and CSL move is the horizon, not the terminal form. WBC Stagflation FALLS 13%
(five more years earning 5.2% on equity against an 8.05% Ke). CSL rises 4-17% (five more
years of 5-7% nominal growth at a held margin before a Gordon terminal — the DNL artefact of
2 Oct, now on CSL). D-60 (payout cut to hold CET1 at target) binds in every WBC scenario.

## THE PLAN FOR THIS CHAT — step 3: decay horizons as a process

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
`3920a3e` D-74 + notes · plus this bridge note.
