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

**State:** suite **209**, ratchet **9**, bases **2.831 / 30.03 / 203.83** — the DNL base
moved this session and that is the headline. Two commits unpushed.

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

### Open, needing Stephen

7. **Ratify or push back on the six re-pinned levels** (D-33), Disorderly Climate in
   particular. MT is now 21.6% below the market reference of 3.61, not 14.9%.
8. **CSL is the other half of the same job** — `build_segment_inputs_from_data` still
   reads `wc_change_pct_revenue_change: 0.10` where the derived figure is 35% (D-30).
   Estimated a day; moves the CSL workbook and the CSL goldens. The CSL segment engine
   already normalises its terminal, so only the intensity is in question.
9. **UI disclosure** of the working-capital methodology (intensity, clean years,
   rounding/override) — flagged by Stephen, scope still open.
10. CSL WACC parameters (D-06, still PROVISIONAL — the EV/EBITDA multiple has no
    independent support).
11. Q5 (WBC CET1 warn-only vs forced payout cut), Q6 (metric card 4), Q7 (tab parity)
    — all in the tracker, none blocking.

### Housekeeping from this session

12. **Pushing does not work from the cloud container any more.** The git proxy refuses
    `stephenreid90/VCC` ("not in this session's authorized repository set"); clone and
    fetch still work, push returns 403. Stephen pushes from his own cmd window.
13. **Two stale `.git` lock files** (`index.lock`, `HEAD.lock`, both zero-byte, left by
    the 21 Aug session) were moved aside on the mount so `git pull`/`push` can run.
    `sandbox_cleanup.cmd` clears the `.dead*` files.
14. `_to_delete/` in the repo root holds one scratch bundle; the mount still refuses
    `rm`, so it needs deleting from a normal cmd window.
15. The DNL UI footnote still cites `dnl_scenarios_comparison_v4` as the source of the
    per-scenario figures. Those now come from the engine; the reference is stale.

### Worth retrieving

16. **DNL 1H26 Appendix 4D half-year financial report** — would give total current
    assets/liabilities at 31 March 2026 (the model's own anchor date) and turn DNL's
    single working-capital observation into two, letting D-29's rounding protocol run
    unmodified and retiring the `rounding_override`.
17. **`data/companies/csl.md` does not exist** (DNL and WBC both have narratives).

---

## Active threads

1. **Working-capital standard — DNL done, CSL outstanding.** Definition, protocol and
   both intensities ratified; mechanism, DNL engine wiring, workbook oracle and goldens
   all shipped (23 Aug). What remains is `build_segment_inputs_from_data` for CSL: the
   hand-typed 10% against the derived 35% (D-30), worth about −4.2% on CSL. Estimated a
   day, including the CSL workbook and its goldens.
2. **CSL WACC — decided in principle (D-05), parameters proposed (D-06, Q9).**
   Implementation retires the audited MT oracle and moves all 18 goldens.
3. **Review batches 3, 5 and 6** — mechanical, no decisions needed, ~1.5 days total.
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
