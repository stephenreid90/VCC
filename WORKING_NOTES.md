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

**State:** suite **270** (+2 opt-in `-m libreoffice`), ratchet **12**, bases
**2.831 / 30.03 / 195.78**. Six commits unpushed — they travel as a bundle, see 20 below.

### The headline: reinvestment went live, and twelve numbers moved

1. **DNL working capital is live** at the ratified 13.76%, applied to the change in the
   *annualised* revenue run-rate. But the bigger effect was the terminal.
2. **The terminal is now rebuilt from components, not capitalised.** The engine grew the
   final explicit FCFF, so the terminal inherited a working-capital build struck on 6.2%
   growth and ran it in a 2.5% perpetuity — about 2.5x the correct drag — plus whatever
   capex rate year five happened to carry. `FcfEngineInputs.terminal_reinvestment` is now a
   **declared** field with no default (D-32); DNL declares `normalised` /
   `capex_rule: equals_da` (D-13).
3. **CSL was a one-line rewire** — its segment engine already applied working capital the
   way §1 specifies, so only the input moved. The hand-typed 10% was **deleted rather than
   corrected**: under D-16 a stored derived value is the defect, not the number (D-34).

| | Was | Now | Change |
|---|---|---|---|
| DNL Orderly Convergence | 3.5619 | 3.2740 | −8.1% |
| **DNL Muddle Through** | 3.0730 | **2.8307** | −7.9% |
| DNL AI Productivity Lag | 2.9850 | 2.7705 | −7.2% |
| DNL Fragmentation | 2.2224 | 1.9926 | −10.3% |
| DNL Disorderly Climate | 1.1768 | 1.7015 | **+44.6%** |
| DNL Stagflation Persists | 1.0194 | 0.8061 | −20.9% |
| CSL Orderly Convergence (AUD) | 237.29 | 227.43 | −4.2% |
| **CSL Muddle Through (AUD)** | 203.83 | **195.78** | −3.9% |
| CSL AI Productivity Lag | 198.68 | 191.21 | −3.8% |
| CSL Fragmentation | 168.23 | 161.95 | −3.7% |
| CSL Disorderly Climate | 174.79 | 168.10 | −3.8% |
| CSL Stagflation Persists | 159.90 | 153.55 | −4.0% |

4. **Disorderly Climate rising 44.6% is the one worth arguing with.** Its Y5 capex is 10.0%
   of revenue against D&A of 7.3% and its terminal growth is the lowest of the six, so
   normalising reinvestment releases more than the working-capital build consumes. If a
   carbon-constrained explosives business should keep reinvesting above D&A in perpetuity,
   `capex_rule: final_explicit_year` is already implemented as the alternative.
5. **Every live valuation now breaches the 70% terminal-share threshold** (DNL 70.2–79.0%,
   WBC 73.97–84.45%, CSL 73.43–76.69%). No case in the project sits below the line, so all
   eighteen carry the §11.4.2 sensitivity obligation.
6. **Oracles rebuilt, not retired.** The v6 (DNL) and v4 (CSL) workbooks predate the change
   and cannot check it. `tests/dcf/golden/_recalc_generated_workbooks.py` now recalculates
   the *generated* workbooks in LibreOffice and pins every line across all six scenarios for
   both companies. Engine and spreadsheet agree to 4e-15. Those workbooks regenerate from
   the data files, so unlike a hand-built oracle they cannot drift.
7. **Both theses restated** on engine numbers. DNL's was two revisions stale (still v4 at
   AUD 3.59) and its central claim — that the framework agreed with consensus on the central
   case — had inverted; it now carries the per-scenario narrative standing rule 2 requires,
   which it never had. CSL's numbers and its whole §3.5.7 market-implied cross-check were
   recomputed (implied Ke 12.7%, implied terminal margin 14.8%, implied growth −3.8%).

### Batch 6 closed — all thirteen items

8. **435 lines of unreachable code deleted** (`VCCXLSX`/`VCCBOOK`/`DNLRICH`); every company
   ships a pre-built formula workbook, so the fallback was never reached. Pages 13–17%
   smaller. Superseded literals in `build_cfgs.py` went too, after a **sentinel test** proved
   them dead — planting impossible values changed `cfgs_gen.json` not at all.
9. **Two silent failures made loud**: the FX branch returned 1.0 on both sides of a ternary;
   the UI's mock-data banner printed unconditionally.
10. **A methodology error, not a code one:** §7.2 said the stub pro-rates the next full
    fiscal year. The engine pro-rates the base year and the engine ties the workbook, so the
    text was wrong — worth about AUD 74m of stub revenue at DNL's growth rate.
11. **Test gaps closed**: structural coverage for `engine_workbook.py`, `__post_init__`
    validation, populated per-year derivations, and a `-m libreoffice` opt-in test that
    rebuilds and recalculates both workbooks so a committed fixture cannot go stale.

### Batch 3 closed — all five items, ratchet 9 → 12

12. **Check 10 catches a judgement stored twice inside one data file.** It fired immediately
    on `beta`/`beta_selected` in all three companies — the gap check 3's own docstring
    described as invisible to it — and on DNL's `da_pct_revenue` mirror. CSL's entire
    `normalised_baseline` scalar block was a second copy of `segment_fcff`; deleted, with the
    rationale prose moved beside the surviving copy. 20 intra-file duplicates → 17 baselined.
13. **Check 11:** a mistyped archetype id raises instead of degrading into the
    segment-valuation path. CSL declares `segment_level_valuation: true`.
14. **Check 12:** `valuation_date` is stated rather than implied, and tied to both the anchor
    walk and the stub fraction. The anchor-date check's silent skip is now a named
    `NO_ANCHOR_DATES_YET` list — WBC and CSL are visibly exempt rather than invisibly so.
15. **The schema escape hatches are typed.** `FiveForces` rejects a missing force and rejects
    both naming generations at once; `BankArchetype`, `Cet1Floor`, `CreditCycleAnchor`,
    `RwaDensityAnchor`, `PeerBeta`, `BankCostOfEquityAnchor` and `RivalrySubforce` are real
    models. They found a live defect on first run — see 17.

### Open, needing Stephen

16. **Ratify or push back on the twelve re-pinned levels** (D-33, D-34). DNL Muddle Through
    is now 21.6% below the 3.61 market reference rather than 14.9%; Disorderly Climate is the
    number to argue with (4 above).
17. **M12 — the APRA CET1 floor does not reconcile.** The components sum to 12.5% against a
    stated `total_floor` of 11.5%. The block's own rationale (regionals at 10.5%, no
    surcharge) implies the countercyclical buffer sits *outside* the stated floor, which
    reconciles. The schema now requires a `components_in_total` declaration and the file
    declares the three that add to 11.5% — **nothing was renumbered.** Confirm the treatment
    or correct the total. Nothing reads `total_floor` today, so it is not blocking.
18. **UI disclosure** of the working-capital methodology (intensity, clean years, rounding or
    override). Flagged by Stephen, scope still open — the case is stronger now that twelve
    numbers have moved and the UI explains none of it.
19. **CSL WACC (D-06, still PROVISIONAL)** — the EV/EBITDA multiple has no independent
    support. It will move the CSL goldens a *second* time and needs another workbook re-tie;
    that was the accepted cost of not pinning numbers to an unsupported input.

### Housekeeping

20. **Landing the work:** run `land_session.cmd` from a normal cmd window. It clears stale
    locks, fetches from `vcc_session_2026-08-23.bundle`, fast-forwards, pushes and runs
    `sandbox_cleanup.cmd`. The cloud container cannot push and the mount cannot merge — see
    the corrected "Operational quirks" in `CLAUDE.md`, which previously said the opposite of
    the truth on both counts.
21. **The stop hook will keep asking to re-author commits** to `noreply@anthropic.com`.
    Stephen has declined; the convention is deliberate and the hook is platform
    configuration, not repo configuration. Noted in `CLAUDE.md` so this does not get
    re-litigated every session.
22. **Left open from batch 3:** 17 baselined intra-file duplicates. Several are real — WBC's
    1H26 income anchors are mirrored between `company_position` and `normalised_baseline` —
    and several are coincidence. Worth a tranche, not urgent.
23. **Still planned:** Batch 5 (18 UI items) is the only untouched review batch.

---

## Active threads

1. **Working-capital standard — COMPLETE.** Definition, protocol, both intensities,
   the mechanism, both engines, both workbook oracles and all twelve goldens shipped
   23 Aug. WBC exempt by rule. The only open piece is the UI disclosure.
2. **CSL WACC — decided in principle (D-05), parameters proposed (D-06, Q9).**
   Implementation retires the audited MT oracle and moves all 18 goldens.
3. **Review batch 5** (18 UI items) — the only untouched batch. Batches 3 and 6 closed
   23 Aug. See `OPEN_ITEMS.html`.

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
