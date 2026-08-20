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

## 🔴 HANDOVER — session of 19–21 August 2026 (read this first)

**Start by running `python scripts/repo_inventory.py` and reading `REPO_MAP.md`.**
See the "Survey before you conclude" directive now in `CLAUDE.md`. This session lost
two round trips to asserting data did not exist when it did.

**State:** suite **146**, ratchet **8**, `node --check` clean, bases unchanged
**3.073 / 30.03 / 203.83**. All work pushed through `e4e862d` and the follow-on
handover commit; working tree clean.

### What shipped

1. **Batch 1 `675d931` — engine lock.** All 18 scenario levels pinned in
   `tests/dcf/test_scenario_goldens.py` (engine-owned change detectors, not workbook
   oracles). §11.4.2 terminal-share warning ported to the bank and segment engines via
   `fcf_engine.terminal_share_warning()`. Suite 122 → 146.
2. **Batch 2 `f9e15b7` — UI credibility.** Pages open on the live case (CSL was opening
   on the broker bar showing 136.00); CSL broker sourced from the register at the
   model's FX (136.00 → 146.60); `cp.re0` aligned to the slider default so the reduced
   form returns base exactly and the false override chips are gone; scenario names
   escaped; delete-index drift fixed; topnotes redated.
3. **`c7b0d7d` — review tracker.** `design/reviews/review_tracker_2026-08-13.html`,
   54 items, filterable. **Open the HTML, not the markdown.**
4. **Four methodology papers** (`97e6a3e`, `a2383ae`, `8c16b1d`): the CSL discount-rate
   fork, CSL cost of debt and target structure, DNL working-capital derivation, and
   the working-capital treatment standard.
5. **`35ea0d4` — DNL source archive filed** to `data/financials/historical/dnl/`.

### Decisions Stephen made (do not reopen)

6. **CSL discount rate:** build a WACC on a **target** capital structure, not spot D/V.
7. **DNL reinvestment:** fix both working capital and terminal capex; rebuild the
   audited workbook. *Sizing still open — see below.*
8. **Market prices:** leave at 15 June 2026. Ben's feed is down; get everything else
   right first.
9. **DNL broker bar:** leave alone until real consensus coverage exists.
10. **Working-capital definition:** the broad measure (current assets less cash, less
    current liabilities excluding interest-bearing debt) — **not** trade-only.

### Where the work stopped, and what it needs

11. **Working-capital standard is written but NOT implemented.**
    `design/methodology/working_capital_treatment.md` specifies the definition, three
    carve-outs (interest-bearing incl. **current lease portions**; held-for-sale; all
    cash), the bank exemption **by rule not by zero**, the layering, and five
    enforcement steps. Step 3 — a `working_capital_intensity_from_data()` in the
    translator — is the load-bearing one. Nothing is coded.
12. **Derived intensities:** CSL **~35%** (six years, 27.6–46.6%, clean post-Vifor
    years 34.8/36.8) against an assumed 10% — worth **−4.2%** on CSL. DNL **13.76%**
    on the broad measure against an assumed zero. Both need Stephen's sign-off on the
    final figure before implementation.
13. **CSL WACC parameters proposed, not ratified:** notional BBB+/A−, spread ~100bp off
    DNL's own 170bp AUD BBB anchor, kd 5.50%; target 1.8× ND/EBITDA converted at a
    through-cycle 14× EV/EBITDA → D/V 12.9%, WACC ≈8.2%, CSL MT ≈ AUD 228 (+12%). The
    EV/EBITDA multiple is the one input with no independent support — revisit when
    peer financials land.
14. **Both changes retire an audited Muddle Through oracle** and move all 18 goldens.
    Each needs a workbook rebuild and re-tie, not just an engine edit. Half a day for
    DNL, a day for CSL.

### Open, needing Stephen

15. Final DNL working-capital intensity (13.76% derived; the paper argues for it).
16. Final CSL working-capital intensity (~35% derived).
17. CSL WACC parameters at item 13.
18. Q5 (WBC CET1 warn-only vs forced payout cut), Q6 (metric card 4), Q7 (tab parity)
    — all in the tracker, none blocking.

### Worth retrieving

19. **DNL 1H26 Appendix 4D half-year financial report.** The archive has the results
    announcement but not the statutory half-year accounts, so total current
    assets/liabilities at **31 March 2026** — the model's own anchor date — are not
    available. Would let DNL's intensity be struck at the anchor rather than six
    months before it.
20. **`data/companies/csl.md` does not exist** (DNL and WBC both have narratives).
    Surfaced by the new inventory script on its first run.

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
