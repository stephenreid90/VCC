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

## 🔴 HANDOVER — session of 21 August 2026 (read this first)

**Start by running `python scripts/repo_inventory.py` and reading `REPO_MAP.md`.**
See "Survey before you conclude" in `CLAUDE.md`.

**State:** suite **152**, ratchet **9**, bases unchanged **3.073 / 30.03 / 203.83**
(unaffected — see below). Pushed to `origin/main`; the device-mounted repo needs a
plain `git pull` to catch up (device_bash has no network, so pushes happen from a
temporary cloud-container clone, not the mount — see "Sandbox architecture,
clarified" below).

### What shipped

1. **Working-capital mechanism implemented and tested** (`working_capital_intensity_
   from_data()`, `src/vcc_valuations/translator.py`), per `design/methodology/
   working_capital_treatment.md` §5 step 3. 5 new tests in
   `tests/test_working_capital.py`; a 9th SSOT ratchet check enforcing every
   non-exempt company carries the data + judgement.
2. **Layer-1 data filed:** `working_capital_history` (6 years) added to
   `data/financials/csl.yaml` — sourced from `csl_eodhd_fundamentals_2026-06-15.csv`
   and cross-checked against the methodology paper's §6.1 table (exact match on all
   six years). DNL's single FY2025 observation restated from the existing
   `balance_sheet` block into the same shape.
3. **Layer-2 judgement ratified and filed** (D-29/D-30/D-31 in `DECISIONS.md`):
   - **CSL: 35%.** `clean_years: [FY2024, FY2025]` → average 35.8% → rounds to 35%
     under the new standing protocol (average of clean years, round to nearest 5pp
     — D-29, general and replicable, not CSL-specific).
   - **DNL: 13.76%**, held at the raw figure via a named `rounding_override` rather
     than the protocol's 15% — one observation is too thin to round with confidence.
     Revisit once the 1H26 Appendix 4D lands (still not in the archive — see below).
   - **WBC:** confirmed exempt by the existing `industry_type: bank` field; no data
     change needed, just a comment pointing at it.
4. **NOT done, deliberately:** the mechanism is not wired into `build_engine_inputs_
   from_data` (DNL) or `build_segment_inputs_from_data` (CSL) — those still read the
   old hand-typed zero / 10%. Doing that plus rebuilding both audited workbooks
   (formulas, not Python constants) and re-tying all 18 goldens is the next block of
   work (est. half a day DNL, a day CSL — unchanged from the prior handover). Stephen
   chose to scope this session to the mechanism + data + ratification rather than
   rush the engine/workbook rebuild ("do not let the engine become self-certifying").
5. **Flagged, not built:** Stephen wants the working-capital methodology (intensity,
   clean-years judgement, rounding/override) disclosed in the UI. Scope TBD, likely
   alongside the engine wiring above.

### Sandbox architecture, clarified this session

6. **`device_bash` (the Cowork desktop bridge / mounted Windows repo) has NO network
   access** — confirmed by a failed `git fetch` (403 from proxy). CLAUDE.md's note
   that "sandbox-side git push works directly from Cowork" refers to the **cloud
   container's own Bash tool**, which clones the repo fresh each session via the PAT
   (`.github-token`, staged in from the device) and has full network access. That is
   where suite/ratchet/UI-build/commit/push actually happen now.
7. **Practical effect:** after a cloud-container session pushes, the device-mounted
   repo at `C:\Users\steph\vcc-valuations` is behind until Stephen runs `git pull`
   from his own (non-sandboxed) cmd window — same as the existing "Stephen pushes
   from his own cmd window" pattern, just `pull` instead of `push`. No lock-file or
   `sandbox_cleanup.cmd` cleanup was needed this session (the cloud-container clone
   is separate and disposed of at session end).

### Decisions Stephen made this session (do not reopen)

8. **Working-capital rounding protocol (D-29):** average of judged clean years,
   round to nearest 5pp, as the general rule for every company.
9. **CSL working-capital intensity ratified at 35%** (D-30).
10. **DNL working-capital intensity held at raw 13.76%**, not rounded, pending a
    second observation (D-31).

### Open, needing Stephen

11. **Scope the engine-wiring + workbook rebuild** (item 4 above) — continue now in
    a follow-up session, or park. Retires an audited MT oracle for both companies and
    moves all 18 pinned goldens; needs deliberate workbook re-tie, not a quick edit.
12. **UI disclosure** for the working-capital methodology (item 5) — scope and
    placement.
13. CSL WACC parameters (D-06, still PROVISIONAL — the EV/EBITDA multiple has no
    independent support).
14. Q5 (WBC CET1 warn-only vs forced payout cut), Q6 (metric card 4), Q7 (tab parity)
    — all in the tracker, none blocking.

### Worth retrieving

15. **DNL 1H26 Appendix 4D half-year financial report.** Checked this session:
    `dnl_1h26_results_announcement_2026.pdf` (which IS in the archive) has a 31 March
    2026 balance sheet on page 11, but in management's NET presentation (Group TWC,
    Net PP&E, Net debt — Total Assets 5,863.3m), not the statutory GROSS format with
    separate Total current assets / Total current liabilities the broad-measure
    formula needs. The full statutory half-year financial report is still not filed.
16. **`data/companies/csl.md` does not exist** (DNL and WBC both have narratives).

---

## Active threads

1. **Working-capital standard — specified, not implemented.**
   `design/methodology/working_capital_treatment.md` is complete. Five enforcement
   steps; step 3 (a `working_capital_intensity_from_data()` in the translator) is the
   load-bearing one. Blocked only on Stephen confirming the two intensities (Q4, Q8).
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
    `sandbox_cleanup.cmd` from a normal cmd window. File deletion is now permitted in
    the Cowork mount, so a session can usually clear these itself.
15. The GitHub PAT lives at `.github-token` (gitignored, untracked — verified 21 Aug
    2026). Sandbox-side push:
    `git push "https://x-access-token:$(cat .github-token)@github.com/stephenreid90/VCC.git" main`
