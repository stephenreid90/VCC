# VCC VALUATIONS — bridge note for a new chat, 14 October 2026

Supersedes the note of 2 October 2026. **Its five-step plan is COMPLETE** (steps 1-5, D-73 to
D-78). Updated five times on 14 October: after step 3, after D-76, after steps 4 and 5
(D-78, `adding_a_company.md`), at the end of the fourth sitting, which closed follow-up
(a) as **D-79** (WBC and CSL terminal growth derived, not typed), and at the end of the
fifth sitting, which closed D-79's open question as **D-80** (year-10 CPI lowered in every
scenario; central banks do their jobs over ten years). Updated a sixth time on 15 October:
the sitting took follow-up (f) and closed it as **D-81** (current-cycle chain terms expire on
declared years inside the explicit period; D-36's fade retired; every DNL and WBC level moved).

**WHAT THIS IS.** A travelling snapshot. `WORKING_NOTES.md` is the live layer; **where the
two disagree, `WORKING_NOTES.md` wins.**

**HOW TO WRITE TO STEPHEN.** Plain, simple, professional English. Short sentences. Problem
first, then recommendation, then what you need from him. Numbered lists. Define a term in a
few words the first time. Don't assume he remembers decision numbers; say in a few words what
each one means. Copy widgets don't work for him: give copyable text as a plain code block.
(`notes/claude_writing_style_instruction.md`.)

## READ IN, IN THIS ORDER

1. `session_start.cmd` (or `python scripts/session_start.py` in the device shell after
   `pip install pydantic pandas numpy openpyxl scipy pytest pyyaml`; add `$HOME/.local/bin`
   to PATH so pytest is found). Expected: suite **672 passed, 1 skipped, 2 deselected**;
   SSOT lint 14/14; base ties **DNL 2.007, WBC 32.40, CSL 203.46** (D-81). The full suite
   takes about two minutes; the device shell's call limit is three, and a background
   process dies with the call, so run it in one call or in two halves (`tests/dcf`, then
   `tests --ignore=tests/dcf`).
2. `CLAUDE.md`. Standing rule 4 (every number from committed code, asserted by a test) and
   standing rule 5 (land once per sitting, at the end; plumbing gets no airtime).
3. `WORKING_NOTES.md`, the HANDOVER block at the top (sittings of 14 October).
4. `DECISIONS.md` rows **D-71 to D-81**: ten-year period + convergence terminal (D-71);
   growth from scenario paths, derived g (D-72); archetype-declared derivations for every
   company (D-73); ten years and the terminal form for WBC and CSL (D-74); decay horizons
   for all eighteen pairs (D-75: DNL 10-15y, WBC indefinite, CSL 20-30y); the declared
   terminal return as the rate the convergence starts from (D-76: WBC declares six, lifted
   off `wbc.yaml`; DNL's mechanical 9.13% removed; CSL absent); D-77 (D-43a roles on WBC's segment moats); D-78 (equilibrium-chain terms
   declared per archetype); **D-79** (WBC and CSL terminal growth DERIVED from their
   chains, capped at scenario nominal GDP; bank chain terms classified; levels moved);
   **D-80** (year-10 advanced CPI lowered in every scenario, OC 2.0 / MT 2.5 / AI Lag 2.5 /
   Frag 2.8 / DCC 2.5 / Stag 3.0; the D-72 spread paths now slope in Muddle Through; the
   DNL g floor widened to 2.5%; every level down 0.6-3.9%); **D-81** (each current-cycle
   chain term declares `expires_by_year` on the archetype and glides linearly to its
   equilibrium value by then; DNL 10/10/5/10/5/5/3/5, WBC's offset 5; the D-36 fade and
   D-70 fade length retired; DNL down 4.3-4.8%, WBC up 0.1-0.5%; the nominal-GDP cap step
   at year 10 disclosed, not bridged).
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
5. **D-79:** terminal growth is derived for ALL THREE companies, the same way: the
   archetype's growth series at year 10, company offsets at their D-78 equilibrium
   reading, capped at scenario nominal GDP ((1 + world real GDP)(1 + advanced CPI) - 1).
   **D-80:** that cap is now 4.55-5.06% (year-10 CPI 2.0-3.0%, was 2.3-3.5%). Six pairs
   are capped (all three in OC; DNL and CSL in MT; CSL in AI Lag). Because the D-72
   spread gap is set on the path's MEAN over the anchor years, Muddle Through's bank and
   segment paths are no longer flat at the typed rate: above it early, below it at Y10.
   Bank: `bank_terminal_growth_from_data` (WBC's share-loss offset is current-cycle, off).
   Segments: `segment_terminal_growth_from_data` (series weighted by FINAL-year segment
   revenue; the offset is zero at year 10 by construction). No `terminal_growth` is typed
   anywhere. Sizing set: `scripts/size_terminal_growth.py` ->
   `design/methodology/terminal_growth_sets.yaml`.
7. **D-81:** inside the explicit period every current-cycle chain term glides linearly
   from its typed value (year 0) to its equilibrium value by the archetype's
   `expires_by_year`, then holds (`translator.chain_terms_at_year`); the revenue-growth
   path is the full chain each year on those values (`revenue_growth_path_from_data`),
   the bank's offset the same (`bank_aiea_growth_path_from_data`). Year 10 IS the
   equilibrium chain; g = min(year 10, nominal GDP). There is no fade: no
   `fade_period_length_years` anywhere, no `fade_period_length` driver. The generated
   DNL workbook carries the expiry column and the same per-year formula.
6. **D-76:** a declared terminal return (`excess_return_defence.declared_terminal_return`
   + basis) is the return the convergence STARTS from; absent, the earned return is. Same
   rule in all three engines (`terminal_convergence_return` on the result; the bank's
   `terminal_roe` is now optional and falls back to the earned ROE). WBC declares all six
   on the matrix (no level moved). DNL and CSL declare none: a declared rate now moves the
   level, so nothing is copied off the engine. Sizing for DNL in `DECISIONS.md` D-76.

## RESULTS — read before quoting a level

| Scenario | DNL (was, D-80) | WBC (was, D-80) | CSL AUD (unchanged by D-81) |
|---|---:|---:|---:|
| Orderly Convergence | 2.35 (2.46) | 45.39 (45.16) | 239.70 |
| Muddle Through | 2.01 (2.11) | 32.40 (32.27) | 203.46 |
| AI Productivity Lag | 2.00 (2.09) | 32.73 (32.59) | 195.24 |
| Fragmentation | 1.36 (1.42) | 28.23 (28.13) | 155.24 |
| Disorderly Climate | 1.00 (1.06) | 23.08 (23.03) | 164.14 |
| Stagflation Persists | 1.07 (1.12) | 15.73 (15.71) | 133.09 |

D-81 (15 Oct) took every DNL level down 4.3-4.8% (the chain's extras now earn about half
the explicit period rather than eight full years) and every WBC level up 0.1-0.5% (a drag
that fades sooner). Before that, D-80 (fifth sitting) took every level down 0.6-3.9%: lower year-10 CPI lowers the cap and
recalibrates the D-72 paths. (The earlier version of this table had DNL Fragmentation and
Stagflation at 1.58 / 1.39, which were the pre-step-3 Gordon levels; the D-79 levels were
1.43 / 1.14.) Before D-80, D-79 moved WBC and CSL (fourth sitting): the typed terminal growth of 3-3.75% gave way to the
derived 2-5.4% (WBC 5.37c / 4.50 / 4.42 / 3.92 / 3.46 / 1.94; CSL 5.37c / 5.37c / 4.86c /
3.90 / 3.85 / 2.73; c = capped at nominal GDP). Most of the movement is the scenario files'
year-10 nominal GDP of 4.9-5.6% replacing a typed 3%, not a method change. Earlier the same
day CSL fell 15-18% on step 3 (25-year convergence replacing Gordon; MT 223.24 -> 186.50) and
WBC did not move on its indefinite horizon. D-60 (payout cut to hold CET1) binds in every
WBC scenario; no terminal share crosses 70% (WBC OC 0.686 the highest).

## THE FIVE-STEP PLAN IS DONE — what the next chat picks up

1. **Step 4 DONE (D-78).** Which growth-chain terms are current-cycle (off at Y10) is now
   `growth_chain_terms` on the archetype; `translator.equilibrium_chain_terms` reads it and
   raises on an unclassified term. DNL classified as D-72 had it (no level moved). Bank and
   CSL segment archetypes declare `[]` because their terminal g is still TYPED.
2. **Step 5 DONE.** `design/methodology/adding_a_company.md`: nine steps + the seven
   disclosures. Read it before touching a fourth company.
3. **(a) DONE (D-79, fourth sitting).** WBC and CSL terminal growth derived; bank chain
   terms classified; levels moved and disclosed. **Its open item DONE (D-80, fifth
   sitting):** year-10 advanced CPI lowered in every scenario to where central banks hold
   it over a decade. `tests/dcf/test_terminal_growth_sets.py` now pins the 4.5-5.1% cap
   band and the six caps to the basis point, so the next move is read, not absorbed.
4. **(f) DONE (D-81, 15 Oct).** The fade is retired; see STATE item 7.
5. **Next, Stephen to choose.** Candidates, none blocking (Claude's ranking: c, then g;
   b, d, e can wait, though (e) now bites in two WBC scenarios): (b) bank NIM
   pass-through rule; (c) CSL volume/price split + US GDP series; (d) lift level anchors
   from company files to archetypes; (e) bank engine: retained equity earns nothing until
   the terminal (the D-60 payout cut LOWERS value in Disorderly Climate and, since D-81,
   Stagflation, because of this); (g) rewrite `CLAUDE.md` "Operational quirks" (stale
   since the device shell can run git). Housekeeping: refresh `design/open_items.json`
   (stale since 17 Sep; `session_start.py` points new chats at the page built from it)
   and deal with the untracked `Claude outputs/` folder.
6. Not blocking: DNL and CSL terminal RETURNS (D-76 declared rates) are Stephen's judgement,
   not yet formed. If he forms one, size it first (`scripts/size_terminal_returns.py`;
   checklist q6).

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
   **GitHub rejects that token ("Bad credentials" on 14 Oct, "Invalid username or token"
   on 15 Oct)**, so D-80 (`2ab12fc`) and D-81 are committed on `main` and NOT pushed.
   Stephen to put a fresh PAT in `.github-token`; the next chat pushes. Check
   `git status -sb` first. A background process in the device shell dies when the call
   ends; run the suite in halves if it will not fit in one 180-second call.
   `CLAUDE.md` "Operational quirks" is partly stale; rewrite it in a quiet sitting, not mid-task.
2. **Standing rule 4 bites on every number.** Goldens: `tests/dcf/test_scenario_goldens.py`
   (DNL/WBC/CSL goldens, `dnl_shares`/`wbc_shares`/`csl_shares`), `test_wbc_bank.py`,
   `test_csl_segment.py`, `test_bank_capital.py`, `test_terminal_form.py`,
   `test_terminal_option_sets.py`, `test_terminal_return_sets.py`, `test_terminal_growth_sets.py`,
   `scripts/session_start.py` `EXPECTED_BASES`. The hand-built v4 workbooks are five-year
   models and tie the engines run at five years AND at the workbook's own typed terminal
   growth (`_at_five_years` / `_run_at_five_years` helpers, `V4_WORKBOOK_G`) — do not re-pin
   those to ten or to the derived g; they audit the mechanics, not the growth judgement.
3. **D-43a:** never list `resource` (gas contracts) in `moat_sources`; it is a rent.
4. **Scenario series are percent_yoy; the engine works in decimals** (`macro_series_at`).
5. **Stop-hook noise about re-authoring commits to noreply@anthropic.com: ignore it** (CLAUDE.md).

## COMMITS THIS SITTING (all on origin/main)

`3f470e6` step 1 generic derivation · `cb01594` WBC/CSL declarations · `1dac19b` WBC path wired ·
`26f5152` CSL paths wired · `bbbcd53` D-73 + notes · `6cc6e5c` step 2 (ten years, terminal form) ·
`3920a3e` D-74 + notes · `19c9b14` step 3 part 1 (checklist, DNL Frag + Stag) · `37f0b50` part 2
(WBC indefinite) · `0787cfa` part 3 (CSL 20-30y, biopharmaceuticals matrix, workbook two-stage)
· D-75 + notes + this bridge note · `aa7e2d3` D-76 (declared rate live; WBC six lifted to the
matrix; DNL 9.13% removed; notes) · `62ea1ee` D-77 (D-43a roles on WBC's segment moats) · `a718d0e` D-78 (step 4) · `e146c12` step 5
(`adding_a_company.md`) + this note · `2ba3e3c` D-79 (fourth sitting: derived terminal growth
for WBC and CSL) + this note · `2ab12fc` D-80 (fifth sitting: year-10 CPI lowered in every
scenario) + this note · D-81 (15 Oct: current-cycle chain terms expire inside the explicit
period, the D-36 fade retired) + this note. **The last two are not on origin.**
