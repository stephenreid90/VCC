# VCC Valuations — Working Notes

The **live** layer: where we are right now, what is in flight, what is parked. Kept
short on purpose. Rewritten 21 August 2026 — it had reached 2,657 lines of
chronological handovers that nobody read, which is precisely how settled questions
kept getting reopened.

## Where things live now

| File | Holds | Read when |
|---|---|---|
| `CLAUDE.md` | durable rules, standing directives, conventions | every session, first |
| `REPO_MAP.md` | what data exists and where (generated) | before concluding data is absent |
| `DECISIONS.md` | ratified decisions, one line each | **before proposing any method** |
| **`WORKING_NOTES.md`** | current state, in-flight work, parked items | every session |
| `OPEN_ITEMS.html` | everything open + which questions block it (generated) | when picking up work |
| `notes/archive/session_log_2026.md` | the full chronological record | when you need *why*, not *what* |
| `notes/bridge/` | per-session bridge notes | starting a fresh chat |

**Start every session with `session_start.cmd`** (or `python scripts/session_start.py`).
It regenerates the two maps, runs the suite and the ratchet, checks the base ties and
prints git state.

---

## 🔴 HANDOVER — session of 23 August 2026 (read this first)

**Start by running `session_start.cmd`** (or `python scripts/session_start.py`).
See "Survey before you conclude" in `CLAUDE.md`.

**State:** suite **265** (+2 opt-in `-m libreoffice`), ratchet **12**, bases **2.831 /
30.03 / 195.78** — both FCFF companies moved this session and that is the headline.
Five commits unpushed; the
cloud container can no longer push (see 13 below), so they travel as a bundle.

### What shipped

1. **DNL working capital is live.** `build_engine_inputs_from_data` now populates
   `delta_wc` / `delta_wc_stub` from `working_capital_intensity_from_data()` at the
   ratified 13.76%, applied to the change in the *annualised* revenue run-rate.
2. **The terminal was rebuilt, which mattered more than the working capital.** The
   engine capitalised the grown final-year FCFF, so the terminal inherited the explicit
   period's reinvestment rates — a working-capital build struck on 6.2% growth carried
   into a 2.5% perpetuity (about 2.5x the correct drag), and whatever capex rate year
   five happened to run. `FcfEngineInputs.terminal_reinvestment` is now a **declared**
   field with no default (`normalised` | `capitalise_last_fcff`); DNL declares
   `normalised` with `capex_rule: equals_da` (D-13, D-32). Same algebra the segment
   engine already used for CSL.
3. **A better oracle, not a retired one.** The v6 workbook cannot check any of this —
   it has no working-capital rows. `tests/dcf/golden/_recalc_dnl_workbook.py`
   recalculates the *generated* DNL workbook in LibreOffice and
   `tests/dcf/test_dnl_workbook_tie.py` pins every DCF line across all six scenarios.
   Engine and spreadsheet agree to 4e-15. That workbook regenerates from the data files,
   so unlike a hand-built oracle it cannot drift.
4. **All six DNL goldens re-pinned** (D-33), plus the UI base and the generated prose.

### The numbers, and the two that need reading

| Scenario | Was | Now | Change |
|---|---|---|---|
| Orderly Convergence | 3.5619 | 3.2740 | −8.1% |
| Muddle Through | 3.0730 | **2.8307** | −7.9% |
| AI Productivity Lag | 2.9850 | 2.7705 | −7.2% |
| Fragmentation | 2.2224 | 1.9926 | −10.3% |
| Disorderly Climate | 1.1768 | 1.7015 | **+44.6%** |
| Stagflation Persists | 1.0194 | 0.8061 | −20.9% |

5. **Disorderly Climate rises 44.6%.** Its Y5 capex is 10.0% of revenue against D&A of
   7.3%, and its terminal growth is the lowest of the six, so normalising reinvestment
   releases far more than the working-capital build consumes. The review called the
   terminal-capex wedge uniformly flattering; on DNL it is not. **This is the one number
   worth arguing with** — if a climate-stressed world should keep reinvesting above D&A
   in perpetuity, `capex_rule` is the place to say so, and `final_explicit_year` is
   already implemented as the alternative.
6. **Every live valuation now breaches the 70% terminal-share threshold** (DNL 70.2–79.0%,
   WBC 73.97–84.45%, CSL 73.43–76.69%). There is no longer a single valuation in the
   project below the line, so all eighteen carry the §11.4.2 sensitivity obligation.
   `test_warning_is_silent_below_the_threshold` had to be rewritten against the pure
   predicate because no live case remains under it.

### CSL, done the same session

7. **CSL is wired through too** (D-34). `build_segment_inputs_from_data` now derives the
   intensity instead of reading the hand-typed 10%, which was **deleted rather than
   corrected** — under D-16 a stored derived value is the defect, not the number.
   CSL needed no engine change: its segment engine already applied working capital
   the way §1 specifies, so only the input moved. Same oracle treatment as DNL —
   `test_csl_workbook_tie.py` pins the generated CSL workbook across all six scenarios,
   and the working-capital charge now has its own row in that workbook rather than
   sitting inside the FCFF formula.

| Scenario | Was (AUD) | Now (AUD) | Change |
|---|---|---|---|
| Orderly Convergence | 237.29 | 227.43 | −4.2% |
| Muddle Through | 203.83 | **195.78** | −3.9% |
| AI Productivity Lag | 198.68 | 191.21 | −3.8% |
| Fragmentation | 168.23 | 161.95 | −3.7% |
| Disorderly Climate | 174.79 | 168.10 | −3.8% |
| Stagflation Persists | 159.90 | 153.55 | −4.0% |

8. **The working-capital standard is now complete** for all three companies —
   all five enforcement steps in `working_capital_treatment.md` §5 are in force.
   What remains of it is presentation, not mechanism.

### Both theses restated

9. **`analyses/dnl/thesis.md` and `analyses/csl/thesis.md`** now carry engine numbers.
   DNL's was two revisions behind (still on v4's AUD 3.59) and its central claim had
   inverted: it said Muddle Through sat "essentially at market (−0.5%)" and located the
   framework's contribution purely in the tails. At AUD 2.83 it is 21.6% below market, and
   the disagreement is now the more interesting half — it comes from funding the growth the
   model forecasts, not from a dimmer view of revenue or margin. DNL also had no
   per-scenario narrative section, which standing rule 2 requires; one is now written.
   CSL's numbers moved ~4% and its qualitative claims all survived, including the Seqirus
   cushion putting Disorderly Climate above Fragmentation.
10. **The §3.5.7 market-implied cross-check was recomputed**, not just re-worded: to justify
    CSL's market price the implied Ke is now 12.7% (β 1.64), terminal margin 14.8%, or
    perpetual growth −3.8%. A stressed β of 1.2 takes Muddle Through to AUD 144 and closes
    three-fifths of the gap, not half.
11. **One narrative claim did not survive checking.** A draft sentence attributed two-thirds
    of DNL's Stagflation fall to margin. Substituting the Stagflation margin overlay into
    Muddle Through and changing nothing else reproduces **96%** of it — the downside is
    almost purely a pass-through story. Corrected before it shipped, and worth remembering
    as the reason to compute rather than estimate these decompositions.

### Batch 6 closed — all 13 items

12. **Dead code removed.** `VCCXLSX` / `VCCBOOK` / `DNLRICH` (435 lines) were unreachable:
    every company ships a pre-built formula workbook as `CFG.xlsxB64`, so `vccDownload()`
    returned before it got there. Generated pages are 13–17% smaller. The superseded
    literals in `build_cfgs.py` (DNL 3.48, WBC 30.15, shares 1,884, net debt 1,512) went the
    same way, after a **sentinel test** proved them dead — planting impossible values in
    those keys changed `cfgs_gen.json` not at all.
13. **Two silent failures made loud.** The FX branch in `build_engine_inputs_from_data`
    returned 1.0 on both sides of a ternary, so the first genuine FX company would have been
    valued at par with nothing complaining; it now raises. And the UI's "Illustrative mock
    data" banner printed unconditionally — right by coincidence, since all three beta
    datasets are mock, and it would have kept firing once Ben's feed returned. Gated on
    `BW.mock`.
14. **A methodology error, not a code one.** §7.2 said the stub pro-rates the *next full
    fiscal year*; the engine has always pro-rated the base year, and the engine is what ties
    the audited workbook. At DNL's growth rate the text would have overstated stub revenue
    by about AUD 74m. Text corrected, correction dated.
15. **The ratchet tightened twice** — 142 known duplicates → 140, as deleted code took its
    baselined literals with it.
16. **Test gaps closed.** `engine_workbook.py` now has structural coverage (yellow inputs
    are inputs, no pasted numbers on the valuation sheet, the working-capital block present
    for DNL/CSL and absent for the bank); `__post_init__` validation is tested; the per-year
    derivations carry populated inputs instead of empty dicts; and a `-m libreoffice`
    opt-in test rebuilds both workbooks and recalculates them, so a committed oracle
    fixture cannot quietly go stale.

### Batch 3 — four of five closed

17. **The ratchet grew from 9 checks to 12.** Check 10 catches a judgement stored at two
    paths inside one data file — the hole that let CSL mirror its whole `normalised_baseline`
    scalar block over `segment_fcff` for months. It fired immediately on
    `beta` / `beta_selected` in all three companies, which is precisely the gap check 3's
    own docstring described as invisible to it. Check 11 makes the archetype fallback
    declared rather than inferred, so a mistyped archetype id raises instead of silently
    degrading into the segment path. Check 12 states the valuation date and ties it to both
    the anchor walk and the stub fraction.
18. **Silent skips made visible.** The anchor-date check used to `continue` past any company
    without anchor dates — so two of three were exempt and nothing said so. They are now on
    a named `NO_ANCHOR_DATES_YET` list with a reason each.
19. **FiveForces has a validator** — a block with three forces no longer validates, and
    supplying both naming generations fails (loudly when the ratings contradict).
20. **Still open from batch 3:** the typed `BankArchetype` block (item 19's other half), and
    17 baselined intra-file duplicates. Several of those are real — WBC's 1H26 income
    anchors are mirrored between `company_position` and `normalised_baseline` — and several
    are coincidence. Worth a tranche, not urgent.

### Open, needing Stephen

12. **Ratify or push back on the twelve re-pinned levels** (D-33 for DNL, D-34 for CSL).
   DNL Muddle Through is now 21.6% below the 3.61 market reference rather than 14.9%;
   Disorderly Climate is the one number worth arguing with (see 5 above).
13. **UI disclosure** of the working-capital methodology (intensity, clean years,
   rounding/override) — flagged by Stephen, scope still open.
14. **CSL WACC (D-06, still PROVISIONAL)** — the EV/EBITDA multiple has no independent
    support. Note this will move the CSL goldens a *second* time and needs another
    workbook re-tie; that was the accepted cost of not pinning numbers to an
    unsupported input.
15. Q5 (WBC CET1 warn-only vs forced payout cut), Q6 (metric card 4), Q7 (tab parity)
    — all in the tracker, none blocking. Batch 3 (5 schema/validator items) and Batch 5
    (18 UI items) remain planned; **Batch 6 is closed**.

### Housekeeping from this session

16. **Pushing does not work from the cloud container any more.** The git proxy refuses
    `stephenreid90/VCC` ("not in this session's authorized repository set"); clone and
    fetch still work, push returns 403. Stephen pushes from his own cmd window.
17. **Two stale `.git` lock files** (`index.lock`, `HEAD.lock`, both zero-byte, left by
    the 21 Aug session) were moved aside on the mount so `git pull`/`push` can run.
    `sandbox_cleanup.cmd` clears the `.dead*` files.
18. `_to_delete/` in the repo root holds one scratch bundle; the mount still refuses
    `rm`, so it needs deleting from a normal cmd window.
19. The DNL UI footnote still cites `dnl_scenarios_comparison_v4` as the source of the
    per-scenario figures. Those now come from the engine; the reference is stale.

### Worth retrieving

20. **DNL 1H26 Appendix 4D half-year financial report** — would give total current
    assets/liabilities at 31 March 2026 (the model's own anchor date) and turn DNL's
    single working-capital observation into two, letting D-29's rounding protocol run
    unmodified and retiring the `rounding_override`.
21. **`data/companies/csl.md` does not exist** (DNL and WBC both have narratives).

---

## Active threads

1. **Working-capital standard — COMPLETE.** Definition, protocol, both intensities,
   the mechanism, both engines, both workbook oracles and all twelve goldens shipped
   23 Aug. WBC exempt by rule. The only open piece is the UI disclosure.
2. **CSL WACC — decided in principle (D-05), parameters proposed (D-06, Q9).**
   Implementation retires the audited MT oracle and moves all 18 goldens.
3. **Review batches 3 and 5** — mechanical, no decisions needed. Batch 6 closed 23 Aug.
   See `OPEN_ITEMS.html`.

## Parked, with the reason

4. **Market-price refresh** — parked until Ben's feed returns (D-19). Affects every
   "vs market" figure, the §16.3 CSL gap story and nothing structural.
5. **DNL broker bar** — parked until real consensus coverage exists (D-20).
6. **Peer comparability metrics and the peer multiples grid for WBC/CSL** — blocked on
   the `det` and `mfin` slots in `beta_data.py`, which are populated for DNL only.
7. **CSL EV/EBITDA multiple** used to convert the target capital structure — the one
   input in the CSL WACC with no independent support. Revisit when peer financials land.

## Known gaps in the data

8. **DNL 1H26 Appendix 4D half-year financial report** — would give total current
   assets/liabilities at 31 March 2026, the model's own anchor date.
9. **`data/companies/csl.md`** does not exist; DNL and WBC both have narratives.
   Surfaced by `repo_inventory.py` on its first run.
10. **DNL/IPL EODHD export** — still the outstanding feed item. No longer blocks
    working capital (the statutory accounts cover it) but does block peer financials
    and the FY21–FY24 summary statements, which remain mock in the UI.

## Volatile notes

11. A strategist friend has independently completed an IPL/DNL scenario valuation —
    the calibration benchmark for build-plan step 8.
12. Industry-archetype location is parked in `vcc-valuations`; may move to a
    platform-level repo if other archetype consumers (NAB/ANZ/CBA) materialise.
13. The complementary-framework enum
    (`payor_and_regulator | network_effect | resource_lifecycle | none`) is chosen but
    open to revisit now that the bank archetype is populated.

## Housekeeping

14. Sandbox commits can orphan `.git/*.lock.dead*` files and `*.bak` backups. Run
    `sandbox_cleanup.cmd` from a normal cmd window. **Deletion is NOT permitted in the
    Cowork mount** (`rm` returns "Operation not permitted", verified 23 Aug 2026 — the
    earlier note here saying otherwise was wrong). A session can only `mv` files aside;
    clearing them needs Stephen's own cmd window.
15. The GitHub PAT lives at `.github-token` (gitignored, untracked — verified 21 Aug
    2026), but **the cloud container can no longer push**: the git proxy allows clone
    and fetch and refuses push with "not in this session's authorized repository set"
    (403, verified 23 Aug 2026). Stephen pushes from his own cmd window. For the record,
    the command that used to work:
    `git push "https://x-access-token:$(cat .github-token)@github.com/stephenreid90/VCC.git" main`
