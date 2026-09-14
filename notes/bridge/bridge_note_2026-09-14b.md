# VCC VALUATIONS — bridge note for a new chat, 14 September 2026 (second sitting)

Supersedes the note of 14 September 2026 (first sitting).

**WHAT THIS IS.** A travelling snapshot, written so the first exchange of a new chat is
not spent reconstructing context. It is NOT the system of record and it does not update
itself. `WORKING_NOTES.md` is the live layer and is maintained; this note freezes today.
**Where the two disagree, `WORKING_NOTES.md` wins** — read it, do not skim it because
this note looks complete.

## READ THIS FIRST, IN THIS ORDER. Do not start work until step 4.

1. **LAND FIRST.** Run `land_vcc.cmd` before any cloud clone is made. One command, it
   never changes. Cloning before that forks the repo.
2. **`session_start.cmd`.** It regenerates the maps, rebuilds the UI config, runs the
   suite and the ratchet, checks the base ties and prints git state. If it is not green,
   stop and read why.
3. Then, in this order: **`CLAUDE.md`** (standing rules 3 and 4 change how you work);
   **`WORKING_NOTES.md`** — the HANDOVER block at the top, which is authoritative;
   **`DECISIONS.md`** — D-52 to D-58 are new; **`REPO_MAP.md`** and **`OPEN_ITEMS.html`**
   before concluding any data or open item does not exist.
4. Only then start work.
5. Do NOT assert that data, a document or a prior decision does not exist until you have
   surveyed the directory that would hold it. Curated `.yaml` files in `data/` are
   SUMMARIES; raw statements live in `data/financials/*.csv`,
   `data/financials/historical/<company>/` (PDFs — extract with `pdftotext -layout`).

## STATE

Suite **364**, ratchet **13 checks**, base ties green and **unmoved**: DNL 1.989,
WBC 30.03, CSL 195.78. Nine decisions ruled this sitting; none of the numeric ones
implemented, which is why nothing moved.

## THE TRAP THAT COST THE MOST TIME

6. **A generator can be broken on main with the whole suite green.** The suite imports
   the engine, not the generators. `build_cfgs.py` had not parsed for a day because a
   `# ssot-allow` marker was inserted mid-line, commenting out a closing bracket. The
   base-tie check read a gitignored config nothing regenerated and reported two failures
   that had nothing to do with the engine. Both holes are closed — `session_start.py`
   now rebuilds before striking the ties, and a test parses every script under
   `scripts/` and `ui_prototypes/`.
7. **If a Denali number looks wrong, check `build_engine_inputs_from_data`, not the
   golden fixtures.** `tests/dcf/golden/dnl_mt_inputs.py` is a legacy hand-typed oracle
   reproducing the audited v6 workbook, retained on purpose. It carries
   `delta_wc=[0.0]*5`. Reading it as the live configuration wasted an exchange this
   sitting and is the mistake open item M1 itself records.
8. **Anything Stephen runs, runs on Windows.** A rebuild that passed in the container
   died on his machine because `open(path,'w')` picked cp1252 and the config contains
   arrows. A test now fails any `open()` in write mode that does not name an encoding.

## RULED THIS SITTING — DO NOT REOPEN

9. **D-52** — item 11 is position 3: capital intensity follows the business. Engine
   still runs position 1.
10. **D-53** — D-49 is a house rule, not a Denali ruling. CSL still declares terminal
    capex equal to D&A and is wrong the same way.
11. **D-54** — the Disorderly Climate carbon arc is capital inside the growing base,
    assumed to earn exactly the cost of capital, therefore value-neutral by
    construction. No revenue uplift booked for it.
12. **D-55** — capital-structure weights are spot market values for every company.
    Narrows D-04. Stephen's reasoning: a higher debt weight raises the levered beta and
    the two effects substantially offset, so precision in the weight buys less than the
    circularity costs. CSL comes off the target-ratio-and-multiple construction.
13. **D-56** — a scenario declares its company-level channels (volume, price, margin,
    capex) with a sign and a rationale; ordering is read, not asserted. Depends on D-42.
14. **D-57** — Denali's working-capital intensity stays as ratified under D-31.
15. **D-43 / D-43a** — the terminal decay horizon comes from the BARRIER, not from the
    contract. A contract confers a rent with an end date, carried in the explicit
    period; a barrier is what stops a rival taking the business. Implemented:
    `Moat.source_roles` in the schema, Denali declared, WBC and CSL baselined.
16. **D-58** — an indefinite horizon is admissible for any barrier, never silent: it
    requires the finite-horizon sensitivity declared beside it. Burden deliberately not
    inverted, because terminal value is most of the valuation.
17. **D-38 and D-39 retired** rather than ratified, superseded by D-48 and D-49.

## THE OUTSTANDING LIST

### Ruled but not in the engine — the numeric queue, in this order

18. **D-52, item 11 position 3.** Moves all six DNL levels. Largest change outstanding.
19. **D-54, carbon arc inside the base.** Moves Disorderly Climate only.
20. **D-53 and D-55 together.** Both move all six CSL levels, so they land as one change.
21. **D-56.** Needs D-42 ruled first for the diagnostic half.
22. **The WBC dividend rule** — lesser of the current payout and the capital-constrained
    one. Stephen asked for it; it has no D-number and needs "% of capital" defined as
    the payout holding CET1 flat given asset growth and RWA density. Record before
    building.

### Decisions still open

23. **Four PROPOSED**: D-35 horizon rule, D-36 growth fade, D-37 archetype ten-year
    macro paths, D-42 terminal-return diagnostic. D-35 and D-36 live only in the replica.
24. **Four PROVISIONAL**: D-06 CSL WACC, D-19 market prices, D-20 DNL broker bar,
    D-31 working-capital intensity (revisit done; next at the FY26 result).
25. **D-58 is ruled but not enforceable yet.** The decay horizon is prose inside
    `terminal_roic.rationale` in the impact matrix — "decay horizon = 10-15 years" is a
    sentence, not a value. Structuring it into a declared field with basis and
    sensitivity is the implementation step for D-58 and for the unratified half of D-43.
    Same defect D-50 was written about, and §12 says this one is worth 15–20% of
    terminal value.

### Correctness and methodology

26. **Item 1** — CSL's six-month valuation-date mismatch. Stephen has asked for the
    Period A roll-forward (anchor date → valuation date), which is what DNL already does.
27. **Item 8 and M12** — bank CET1 constraint missing; APRA floor does not reconcile
    (11.5% stated against components summing to 12.5%). Both feed item 22.
28. **M10** — all three market prices two months stale, sequenced behind the UI work.
29. **CSL has no stub period at all.** `segment_engine.py` does not implement Period B.
    Separate from item 26 and a bigger job.

### UI — fourteen open items

30. **Accessibility (item 29)** — keyboard-unusable, one aria-label for the file, WCAG
    1.4.1 failure on tab selection.
31. **Engine versus reduced form** — sliders silently swap in the JS approximation (31);
    the DCF panel claims engine provenance after a slider move (M5).
32. **DNL's two DCF views disagree by AUD 154m of EV** with a tautological tie check (M6).
33. **Stephen's terminal-share disclosure** — disclose it, do not rebuild the §11.4.2
    rule. Then the panel-to-translator wiring, then the capital-intensity override.
34. Plus cross-company text leak (M7), workbook literals off Assumptions (22), nine
    smaller items, two in BACKLOG.

### Blocked on Ben's feed

35. DNL FY21–FY24 mock, peer multiples mock, D-19 and D-20 both waiting.

Twenty-six open items: six needing Stephen's decision, eighteen planned, two backlog.

## HOUSE RULES

Australian English. Number any list of 2+ points so Stephen can reply by number.
**Standing rule 3** — Stephen does not use CMD or git directly: give him ONE complete
pasteable command, in a copy-button widget, every time, say what "finished" looks like,
then VERIFY THE RESULT YOURSELF rather than asking him to copy terminal output back.
**Standing rule 4** — any number that reaches a document must come from committed code,
shipped in the same change as the document citing it. Read `design/writing_style.md`
before drafting prose meant for readers.

## EDIT MECHANICS

Work in the CLOUD CONTAINER clone, not on the mount. The cloud container cannot push.
Finished work travels as `session.bundle` written to the repo root; Stephen runs
`land_vcc.cmd`, which merges it, pushes and deletes it. Both files are gitignored.
Keep domain numbers out of `.py` prose — the SSOT ratchet is comment-blind, and format
specs like `:.2%` read as the literal 0.2.

**The device shell (`device_bash`) is down** — a Windows update of 8 September prevents
the workspace mounting the folder. Files can still be READ via staging, which is enough
to verify a landing by reading `.git/refs` and a log file, but nothing can be RUN on
Stephen's machine. Have him run one pasteable command that tees output to
`.git\_session_log.txt`, then stage and read that.
