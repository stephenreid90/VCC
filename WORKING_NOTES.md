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

## 🔴 HANDOVER — session of 25 August 2026, second sitting (read this first)

**Start with `land_vcc.cmd`.** Then `session_start.cmd`, then this block.

**State:** suite **288** (+2 opt-in `-m libreoffice`), ratchet **12**, bases unchanged
**2.831 / 30.03 / 195.78**. No engine change, no production change, nothing in `data/`
moved. One new test package.

### What happened

1. **The replica is committed and the tie is a test.** `tests/dcf/harness/replica.py`
   plus `tests/dcf/test_replica_ties_engine.py` — eighteen tests, six scenarios,
   floating-point equality against `FcfEngine`. Last session's harness was scratch and
   was thrown away, so nothing it reported could be re-checked; that is now fixed. The
   variants are one-change transforms of the tying plan: `extend`, `fade_growth`,
   `converge_capex`, `reshape_margin`, `capex_arc`, `hold_capital_intensity`, and four
   ways of striking terminal capex.
2. **Two terminal-boundary conventions pinned as tests.** The terminal's working-capital
   drag is struck one year ahead of the explicit period's — a factor of (1+g). And
   explicit flows discount mid-year while the terminal is an end-of-year Gordon value, so
   converting a terminal year into a steady-state explicit year *raises* EV by ~0.26%.
   D-35's "surplus years cost nothing" is true to a quarter of a per cent, not exactly.
3. **Item 11 was sized and it is not small.** Under the ruled build, invested capital
   falls from **108.3% of revenue today to 67.5–85.8% at Y10** (Muddle Through 72.6%),
   because capex converging to 7.3% *is* D&A — DNL adds no net fixed capital across ten
   years while revenue compounds about 50%. That thinning, not a moat, is what produces
   the terminal ROIC of 14.6%.
4. **The coherent alternative costs a third of the company.** Holding capital intensity
   flat gives Muddle Through **1.7675 against 2.6956 (−34.4%)**, Fragmentation −49.0%,
   Disorderly Climate −68.0%, and Stagflation Persists goes **negative**. Terminal ROIC
   then lands at 9.8% against a WACC of 8.877% — which is what `architecture.md` §11.4.2
   actually asks for.
5. **Reconstruction caveat.** The rebuilt harness lands within ~2% of last session's
   ruled table (Muddle Through 2.6956 against the paper's 2.7471). The residual could not
   be reconciled because the original harness no longer exists. Everything in 3 and 4 is
   from the committed harness.

### Open, needing Stephen

6. **Item 11 is unruled.** Three positions were put and none was taken: declare a Y10
   target intensity and derive the capex path; hold intensity flat; or accept the fall
   and disclose it as a stated judgement. **Nothing should be built on the ruled numbers
   until this is settled** — it moves DNL by more than every other open item combined.
7. **The evidence question underneath it was also left open:** how much of DNL's 6.155%
   nominal revenue growth is volume (needs capacity) versus price (does not). That is
   what decides 6, and it has not been surveyed.
8. **Everything else from the first sitting stands** — see the block below. D-42, the
   horizon and fade, and the UI disclosure piece are all still queued behind item 11.

---

## HANDOVER — session of 25 August 2026, first sitting (superseded, kept for context)

**Start with `land_vcc.cmd`** — the standing landing command, see "Landing a session" in
`CLAUDE.md`. Then `session_start.cmd`, then this block, then
`design/methodology/horizon_and_terminal_convergence.md`, which is where this session's
work actually lives.

**State:** suite **270** (+2 opt-in `-m libreoffice`), ratchet **12**, bases unchanged
**2.831 / 30.03 / 195.78**. No engine change this session. Nothing in `data/` moved.

### What happened

1. **Housekeeping fixed first.** The 23 August bundle had not landed — a stale
   `.git/refs/heads/incoming.lock` defeated `git branch -D` behind a `2>nul`. Locks are
   now swept recursively by `sandbox_cleanup.cmd`, and the per-session landing scripts are
   replaced by one permanent gitignored `land_vcc.cmd`. **New standing rule 3 in
   `CLAUDE.md`: Stephen does not use CMD or git directly** — one complete pasteable
   command in a copy-button widget, and the session verifies the result itself over the
   device bridge.
2. **A methodology paper, not a code change.** `horizon_and_terminal_convergence.md`,
   fifteen sections, thirteen decisions of which seven were ruled on. Every number in it
   comes from a scratch harness that reproduces `FcfEngine` to 1e-15 on all six live DNL
   scenarios.
3. **The finding that started it:** DNL's explicit period ends with the gas roll-off still
   ramping, so every scenario capitalises a margin that was falling 0.50pp a year. The
   five-year horizon was never a decision — `architecture.md` §2.5 committed to a
   per-scenario horizon and it was never built.
4. **The finding that mattered most:** the terminal return nobody had computed. Every DNL
   scenario implied a terminal ROIC of 37–80%, four to nine times WACC; CSL 61–73%. WBC,
   which declares its terminal ROE explicitly, runs a sane 1.12–1.37× Ke. `architecture.md`
   §11.4.2 already requires ROIC ≈ WACC and says it is "enforced at translation time" — it
   is not; `terminal_roic` appears once, as a driver-delta mapping.
5. **Five things are now known to be specified, populated and read by nothing:**
   `time_profile`, `fade_period_length`, the year-10 macro anchors, `terminal_roic`, and
   the §9.9 terminal-growth convention.

### Rulings Stephen made (in `DECISIONS.md`)

6. **D-44** invested capital = PP&E + intangibles + NCWC, goodwill excluded; disclosed in
   the UI. DNL ROIC 10.09% vs WACC 8.877%.
7. **D-45** pin g and ROIC, derive reinvestment. Terminal growth gets a declared basis;
   alternatives shown in the UI as disclosure, never as a knob (D-23).
8. **D-46** a regulatory setting is indefinite unless currently under debate — an
   observable with a source, not a judgement.
9. **D-47** terminal excess returns are dated, not capped and not exempt.
10. **D-40** gas roll-off holds at −1.5pp, phasing only. **D-41** Disorderly capex arc
    confirmed. **D-06** stays PROVISIONAL. **D-19** prices refresh after the UI work.

### Open, needing Stephen

11. **The inconsistency the rulings create.** D-44 puts terminal capex at 8.6–9.2% of
    revenue while the explicit path converges to 7.0%. The two are now struck on different
    reinvestment logic. **First thing to settle next session.**
12. **Seven decisions still PROPOSED:** D-35 horizon, D-36 fade, D-37 archetype ten-year
    macro, D-38 capex convergence, D-39 terminal capex source, D-42 the diagnostic, D-43
    decay horizon from Porter.
13. **The UI disclosure piece has grown** and is now the pivot: terminal return, terminal
    growth basis, invested-capital construction and the working-capital methodology all
    disclosed in one place. D-19 sequences the price refresh and the golden re-pin behind
    it.
14. **Do not ratify the twelve goldens from 23 August.** They will move again. Under the
    ruled assumptions DNL lands at 3.2366 / 2.7471 / 2.7035 / 1.9122 / 1.4378 / 0.6316 —
    four moving less than 4%, Disorderly −15.5%, Stagflation −21.6%.

### Recommended order

15. Build D-42, the diagnostic, first — compute and display terminal ROIC and ROE against
    the cost of capital, change no behaviour. Then settle item 11. Then the horizon and
    fade. Then the UI disclosure. Then re-pin all eighteen goldens once, with the workbook
    re-tie.

---

## HANDOVER — session of 23 August 2026 (superseded, kept for context)

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
