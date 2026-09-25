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

## 🔴 HANDOVER — sitting of 24 September 2026 (read this first)

**Standing rule 5 is still in force until 16 October 2026.** Plumbing gets no airtime;
one exception below because it affects whether anything in this block survives.

**State:** suite and base ties as at the 18–22 September sitting — nothing re-run this
sitting. No engine code moved. **The mount was behind by 13 commits** (a landing from the
22 September sitting had not reached Stephen's checkout — the `device_commit_files`
overwrite bug noted in `CLAUDE.md` operational quirks). Caught up and pushed this sitting;
`origin/main` and Stephen's mount now agree. If a fresh chat reads this and finds the mount
behind again, that bug is still live and worth its own sitting to fix properly rather than
worked around again by hand.

### D-62 to D-66 and D-35 to D-37 — all ratified

Stephen ruled on all eight this sitting; recorded in `DECISIONS.md`. Two are worth flagging
because they added to or sharpened the paper's recommendation rather than just accepting it:

1. **D-63** (moat band) — ratified, plus a UI requirement: value has to be shown at more
   than one moat length (band ends and indefinite), not just the chosen default, so the
   point estimate never hides what the choice costs.
2. **D-65** (below cost of capital) — not tied to a five-forces judgement call as first
   proposed. Every scenario already carries a `time_profile` with a declared year at which
   it reaches its own equilibrium phase (Stagflation Persists: year 5). The reversion year
   is read from there. Stephen's own question — "do our ten-year models all converge by
   then?" — checked out: every scenario reaches its equilibrium phase at or before year 10
   except Fragmentation, which reaches it exactly at year 10 (not embedded in it — worth a
   line in the write-up). This means D-65 mostly stops mattering once D-35 lands, because
   the stress-to-resolution transition happens inside the explicit forecast, not the
   terminal.

Consequences of ratification, all now closed or moot rather than open: **M16** (D-45 vs
D-49 conflict — D-49 supplies capital C, nothing else declares a terminal return), the
**D-42 materiality floor** question, **where a bank's terminal-return defence lives**,
**D-53/D-55 for CSL**, the two outstanding **DNL excess-return defences**, and **M14**
(superseded by D-65's mechanism — say so explicitly in the write-up once built, rather than
letting it quietly vanish).

### What needs Stephen next

Nothing — the build order below is implementation, not a question.

### Build order (paper §12), now the active list

1. **DONE 24 Sep 2026.** Sourced fade-evidence note,
   `design/methodology/terminal_moat_fade_evidence.md`, checked all four citations against
   the actual source PDFs (all four numbers held). Recommendation: keep the band edges as
   proposed (5–10 / 10–20 / 20–30 / indefinite); the evidence argues for discipline in how
   they're used, not different numbers — the short band already sits above the population
   baseline, the medium band's floor is a coin-flip-grade claim (not a round number), and
   long/indefinite need D-43a's company-specific barrier rather than an industry's own
   track record. For Stephen to confirm alongside the next sitting's work.
2. **DONE 24 Sep 2026.** CSL's invested-capital base is built. Opening capital from the
   FY25 balance sheet (D-44, already transcribed), rolled forward through FY26–FY31 on
   the segment engine's own capex/D&A/working-capital arrays — reused, not
   reimplemented (D-51). Lands 22,643–23,594 USDm across the six scenarios; CSL earns
   18.2%–24.9% on it against an 8.75% Ke. That is a real, high number, not the old
   D-53 defect (which was about return on NEW capital going to 61–73% because
   `capex = D&A` zeroed out net reinvestment — a different quantity, now not measured
   at all since the new terminal doesn't need it). Every disclosure in
   `terminal_option_sets.yaml` now prices for CSL. Full suite green (444 passed).
3. **DONE 25 Sep 2026, disclosure only (D-68).** Two-stage terminal built in `src/`:
   `perpetual_multiple` / `two_stage` / `implied_moat` / `implied_perpetual_return` /
   `return_on_new_capital` promoted out of the sizing script into
   `src/vcc_valuations/dcf/terminal_value.py` (D-51/standing rule 4 — `src/` is now the
   source, the script imports it). `two_stage_disclosure()` reads the moat length from
   `ExcessReturnDefence.decay_horizon` via a new `decay_horizon_from_matrix` in
   `translator.py`, takes the D-63 band midpoint, and discloses what the two-stage form
   would show ALONGSIDE each engine's own headline terminal — no golden moved, no
   headline `terminal_value`/`value_per_share` touched. Wired to Stephen's choice ("build
   the module now, assign moats later"): three of eighteen valuations have a declared
   moat length today, all DNL (Muddle Through, Orderly Convergence, AI Lag, each 10–15y),
   proving the module end-to-end; the other fifteen — all of WBC, all of CSL, and DNL's
   other three scenarios — disclose "not available" rather than a moat length nobody
   chose. DNL's three: two-stage $1.73–$1.93/sh against the engine's own $1.99–$2.33/sh,
   the expected ordering (a finite moat is worth less than an indefinite one). Committed
   set `design/methodology/terminal_disclosure_set.yaml`, regenerated by
   `scripts/size_two_stage_disclosure.py`, asserted by
   `tests/dcf/test_two_stage_disclosure.py`. Full suite green (455 passed). **Assigning
   moat lengths for the other fifteen valuations is a later, dedicated pass — not
   attempted here.**
4. D-35/D-36/D-37 engine changes: per-year revenue-growth path (fade), horizon-length
   selection, and the archetype macro-driver paths plus a new SSOT check.
   - **D-37 DONE 25 Sep 2026, schema/check only.** `required_macro_drivers` on
     `IndustryArchetype`; `industrial_explosives` declares the three scalars its chain
     reads (`global_mining_real_growth`, `dm_inflation`, `gas_price_growth`). New SSOT
     **check 14** (the paper's proposed "13" collided with D-50's already-shipped rate-
     basis check) — baselined honestly at 18/18 gaps, since these still live as flat
     per-scenario scalars in `dnl.yaml`, not year-anchored paths; no path was invented to
     close a gap the data doesn't support. WBC/CSL declare no required drivers, so the
     check is correctly vacuous for them. Full suite green (456 passed).
   - **D-35 + D-36 still pending, deliberately.** Asked Stephen how to sequence — his
     call: D-37 only tonight. D-35 (longest-scenario horizon) and D-36 (revenue-growth
     fade to g) are engine changes that move every DNL golden and only make sense done
     together (extending the horizon without the fade first is the +16.8% distortion
     §3 of the paper warns about) — left for a dedicated sitting.
5. Re-pin all goldens once, with the move explained per scenario — blocked on D-35/D-36
   above, and on the moat-length assignment pass that would let the two-stage terminal
   become the headline construction rather than a disclosure.
6. Write-up: the seven §8 disclosures in every company write-up's terminal section.

---

## HANDOVER — sitting of 18–22 September 2026 (superseded by the block above)

**Standing rule 5 is still in force until 16 October 2026** (see the block below and
`CLAUDE.md`). Plumbing gets no airtime.

**State:** suite **444**, ratchet unchanged, base ties green and **unmoved** — DNL 1.989,
WBC 30.03, CSL 195.78. No engine code moved this sitting. All work is on origin/main;
Stephen's working tree fast-forwards the next time `land_vcc.cmd` runs.

### The terminal value was stepped back from, and redesigned — PROPOSED, not built

Stephen stepped back from the component-built terminal (D-49 capital roll-forward, D-45
declared returns, D-42 reconciliation, M16) as over-engineered for something nobody can
see: *"we don't know what will happen, which is why it is in the TV."* The replacement is
written up in **`design/methodology/terminal_value.md`** — read it in full before any
terminal work. Every figure in it comes from `scripts/size_terminal_options.py` → the
committed set `design/methodology/terminal_option_sets.yaml`, asserted by
`tests/dcf/test_terminal_option_sets.py` (29 tests, including the maths identities).

The design in one paragraph: **default terminal = C + PV of N years of economic profit**,
closed form `TV = C × [m(1 − k^N) + k^N]`, m = (R − g)/(r − g), k = (1 + g)/(1 + r), on
capital C at the end of the forecast. Moat length N is a **band** from the five-forces work
(short / medium / long / indefinite), counted from the valuation date. Two levers: moat
length and excess return; **the return lever holds capital and flexes earnings** (the other
convention makes value fall as return rises). Simple TV and exit multiple stay selectable.
Every basis reports seven disclosures, led by **TV/capital** and **implied moat**.

Findings Stephen has seen, all in the paper:

1. The current DNL terminal implies a **66–72 year moat** that nobody chose; WBC's declared
   terminal ROEs imply 22–42 years and ARE an indefinite two-stage already.
2. A 15-year moat takes DNL MT 1.99 → 1.69 and WBC MT 30.03 → 25.32, about −15% each —
   five-year figures; D-35's ten-year forecast will move them.
3. Simple TV is agnostic about components (Stephen's correction, accepted: the earlier
   "least humble" framing was wrong) but still implies a return on new capital — 14.2% on
   DNL MT against 11.4% earned — and capitalises one year, which breaks mid-glide (DNL
   Disorderly: 1,925 against 4,169).
4. DNL at the 3.61 market price needs a perpetual return of about 18.5% on all capital.
5. WBC Stagflation (M14) shows up automatically as "other side of capital".

### What needs Stephen next

1. **Ratify D-62 to D-66** (paper §11). D-65 — how long a return *below* the cost of
   capital persists — is a genuine choice with large numbers attached (paper §5).
2. **D-35 to D-37 alongside** (ten-year default, growth fade, ten-year macro paths).
3. On ratification these close or become moot: **M16**, the **D-42 materiality floor**,
   **where a bank's defence lives**, **D-53/D-55 for CSL** (replaced by a CSL invested-capital
   build). M14 stays open and needs his answer.

### Build order once ruled (paper §12)

1. Sourced fade-evidence note, checked against the PDFs, fixing the band edges. The
   citations in the paper came through a summarising tool and are flagged as such.
2. CSL invested-capital base (D-44 on the FY25 balance sheet, rolled forward).
3. Terminal module in `src/`, wired into all three engines; `ExcessReturnDefence.decay_horizon`
   is the moat band and `declared_terminal_return` is the return lever — the schema exists.
4. Re-pin all goldens once, with the move explained per scenario.

---

## HANDOVER — session of 16 September 2026 (superseded by the block above)

### ⚠️ READ STANDING RULE 5 BEFORE YOU WRITE A WORD TO STEPHEN

**Asked for on 16 September 2026, in his words:** *"can we please forget about git for,
say, a month. It is consuming half of every chat and destroying my will on this
project."* He is right about the record — that sitting spent most of its exchanges on
bundles, stale locks, a vanished bundle and stop-hook noise, and almost none on
valuation. Standing rule 5 in `CLAUDE.md` is the operational form of it and is in force
until **16 October 2026**, when it is reviewed. A scheduled reminder exists for that date.

The short version, because it is the thing most likely to be ignored: **land once per
sitting, at the end; the landing is one line at the bottom of a message with no
explanation; absorb stop-hook output silently; never report a git diagnostic unless
Stephen has to decide something.** Fix plumbing quietly, record it here if it is durable,
and spend the conversation on the valuation.

---

**State:** suite **412**, ratchet **13 checks** plus the D-42 defence ratchet, base ties green. **WBC HAS MOVED:
30.03 → 30.07** under D-60, and all six WBC levels are re-pinned. DNL 1.989 and
CSL 195.78 unmoved. Two decisions ruled and implemented (D-59, D-60), the D-42
diagnostic built, sized and enforced, D-42 and D-58 ruled, two open items closed
(M12, item 8), four opened (M13, M14, M15, M16).

### The device shell came back

1. **`device_bash` works again** after being down since the Windows update of 8 September.
   Reads, writes and commits on the mount all work, and **`git push` authenticates from
   there with the PAT** — so a landing no longer needs Stephen to run anything. Two
   constraints from `CLAUDE.md` still hold and were re-tested, not assumed: the mount
   **still cannot delete** (`rm` gives "Operation not permitted"), and the cloud container
   still cannot push. Keep `land_vcc.cmd` as the fallback for when the shell drops again.
2. **`land_vcc.cmd` gained a stash-and-retry step.** A fast-forward aborts if the incoming
   commits add a file that already sits untracked on disk. That was about to happen with
   the two August bridge notes, was caught by simulating the tree before handing the
   command over, and is now handled: the script stashes untracked files and retries once,
   keeping the stash so nothing is lost. There is one such stash on Stephen's machine
   holding superseded copies of those two notes; it can be dropped.

### D-59 — the CET1 floor was wrong in kind, not just in the CCyB

3. **M12 asked the wrong question.** It asked whether the countercyclical buffer sits
   inside or outside the archetype CET1 floor. It sits inside — APS 110 sets the CCyB by
   extending the range of the capital conservation buffer. But the `components_in_total`
   carve-out that answered it was hiding a basis error: `regulatory_minimum` held the
   **total capital** minimum, Tier 1 plus Tier 2, in a field measured on CET1; and the
   conservation buffer held the **standardised** figure for banks that are all IRB.
4. **The floor is corrected to the real APRA stack** — CET1 PCR, IRB conservation buffer,
   D-SIB surcharge and CCyB, all on one basis and all four inside the declared total. The
   figure the file previously called a floor turned out to be an operating target, which
   is exactly why it looked plausible: it is close to where the majors actually run.
5. **So the floor and the target are now two fields, and the payout rule binds on the
   target.** A bank defends its board-approved operating level, not its regulatory
   minimum. The target carries its management buffer inside the level, retiring
   `cet1_management_buffer_typical` — the old pairing of a floor plus an additive buffer
   would have bound anything reading both far above where any major has run. The buffer is
   now *observed* as the gap between the two, on the D-48 principle.
6. **A validator rejects a target at or below its own floor**, which is the check that
   would have caught this on the day it was written. Four tests pin the specific numbers
   so the mixed basis cannot return, and one asserts that a genuinely carved-out buffer is
   still expressible — the shape stays legal, it just has to be meant.
7. **Nothing moved, and that is the point of doing it now.** Grep confirms nothing
   consumed `cet1_floor` — it appeared only in its own schema and test — so the correction
   was free. Item 8 is the first thing that would read it, so the error would have been
   baked into the §15.5 constraint the moment that was built.
8. **Watch for this: the SSOT ratchet is comment-blind and it caught the docstrings.**
   Writing the corrected figures into the schema prose tripped check 3 on six literals.
   The numbers belong in the archetype YAML, which is the register layer; the docstrings
   now carry the reasoning in words. Do not reach for `# ssot-allow` to get around this —
   and if you ever do, it goes at the END of the line (see the 14 September defect).

### Opened: M13, and it blocks the same thread

9. **WBC's own CET1 block is stale and internally inconsistent.** It carries an
   operating range of 11.0–11.5% with a `target_minimum` equal to the *top* of that range
   rather than its bottom, and a `management_target` above both. Westpac's own disclosure
   has moved on — the board target is a post-dividend CET1 above 11.25%, stated as
   replacing the former range, following APRA's phase-out of AT1 from 1 January 2027.
10. **Left for Stephen deliberately.** It is the level the dividend rule will bind on, so
    it wants a ruling rather than a session's reading of a PDF. The company `cet1` block
    is also **untyped** — no schema class at all — which is how the inconsistency
    survived; typing it is the natural companion change.

### Item 8 step 1 is in — the CET1 diagnostic, warn-only

11. **`src/vcc_valuations/dcf/bank_capital.py` projects the CET1 path and the engine warns
    on it.** No level moved. The ratio is anchored on WBC's *reported* CET1 and rolled
    forward on the model's own implied rates — equity growth from retained earnings over
    opening equity, RWA growth from AIEA times a density derived from reported RWA over
    the AIEA anchor. CET1 is not book equity and the data carries no bridge, so anchoring
    on the observable was the honest option: the diagnostic is exact on direction and rate
    of drift, and indicative on the level at which a threshold is crossed.
12. **It reproduces the finding.** Equity compounds at 2.5–2.8% against RWA at 4.35%, and
    CET1 erodes in *every* scenario: 97bp on Muddle Through, from 12.42% to 11.45%,
    crossing the 11.50% operating target at Y5; 165bp on Orderly Convergence, crossing at
    Y3; 71bp on Stagflation. Nothing breaches the 10.25% floor inside the explicit period,
    so this is a board event, not a regulator one.
13. **The ordering is inverted against value, and it is real.** Orderly Convergence is the
    best scenario for the share price and the worst for capital, because the same strong
    asset growth that drives the value consumes the capital; Stagflation is the worst for
    value and the best for capital, because the balance sheet barely grows. Asserted in
    `tests/test_bank_capital.py` so a change in that relationship is a conscious event, in
    the spirit of D-56.
14. **Zero base-tie risk is structural, not asserted.** Book equity is a pure accumulator
    in the §15 build — NII comes from AIEA, never from equity — so the per-period
    roll-forward sums to the closing figure the terminal value already used. Tested both
    ways: the same inputs with the capital block stripped give a bit-identical share price,
    and a bank with no capital data simply gets no warning rather than failing to build.
15. **Two ratchet traps cost time and are worth knowing.** The SSOT lint tokenises every
    number on a line and is comment-blind, so the precision digit inside an inline percent
    format spec reads as a bare decimal and trips check 3 — twice, the second time from the
    *docstring* explaining the first. Percent and basis-point formatting now goes through
    two annotated helpers in that module, and the explanation names no digits.

### D-60 is step 2, RULED and ON — WBC's levels have moved

16. **Ruled and implemented the same day: the payout is cut to hold CET1 on the operating
    target.** The ratio drifts, and once it reaches the target the payout is reduced by
    just enough to hold it there. One-sided, so it never raises the payout above the stated
    ratio. Path-dependent, so it runs inside the engine loop. The level defended is the
    target, not the floor — no WBC scenario reaches the floor inside the explicit period,
    so binding on the floor would be a rule that never fires.
17. **It raises the valuation, and after a round of argument that is the ruled reading.**
    Retention lands in closing book equity, which the terminal capitalises at
    (ROE − g)/(Ke − g) = **1.54×** on the central case, while the forgone dividend is worth
    about 0.7× discounted from Y5. The session raised this as a possible artefact and
    Stephen's answer was that it is the retention trade itself: lower dividends now in
    exchange for higher dividends later. **He is right, and the form already says so** —
    the justified price-to-book terminal is derived from g = ROE × b, so the terminal stream
    IS the dividend the retained equity supports, growing at the rate retention funds.
18. **Checked rather than taken on trust before switching on.** The worry worth testing was
    whether retention conjures a return the model had not already assumed. It does not: the
    declared terminal ROE sits at or *below* the ROE the explicit period actually earns in
    its final year on five of the six scenarios. The sixth is a finding in its own right —
    see M14 below.
19. **WBC re-pinned.** Orderly Convergence 35.7058 → **36.3661** (binds Y3, withholds the
    most at 5,850m), Muddle Through 30.0304 → **30.0664**, AI Lag 29.6987 → **29.7217**,
    Disorderly 22.5807 → **22.5918**. Fragmentation and Stagflation are unchanged to the
    cent, because the rule never binds in them — which is the check that it is one-sided.
    `session_start.py` now expects WBC 30.07. DNL and CSL did not move.
20. **The audited workbook tie was NOT re-pinned, and that was deliberate.** The v4
    workbook has no capital constraint in it, so once D-60 was on the engine stopped
    reproducing it. Re-pinning that test onto the engine's own new answer would have
    dissolved the only independent check on the §15 mechanics into a self-comparison. The
    tie is now struck on the unconstrained path, and the constrained level is asserted
    beside it — including that closing equity less dividends forgone returns exactly the
    workbook's figure, so the size of the overlay is visible in the suite.
21. **M13 still gates the level** the rule defends, whenever WBC's own target is corrected.

### Opened: M14, and it is the largest thing found this sitting

22. **The declared terminal ROE bears no tested relationship to the ROE the model earns.**
    Measured as the final explicit year's NPAT over closing book equity, the declared rate
    is conservative on five scenarios — between 0.03pp and 3.00pp *below* earned. But on
    **Stagflation the declared 9.00% sits 4.01pp ABOVE the 4.99% the final year earns**.
    That is a perpetual recovery assumption and nothing declares it as one.
23. **It matters most exactly where it is worst.** Stagflation's terminal is **84.45% of
    the equity claim**, the highest in the project. So the downside valuation is
    five-sixths driven by a terminal that assumes ROE almost doubles from where the
    explicit period leaves it. This is a D-50-shaped defect — a rate carried without a
    declared basis — on the largest single quantity in the bank valuation.
24. **Take it with D-42**, the terminal-return diagnostic, which is still PROPOSED and is
    the same shape: print declared against earned, and require a stated reason where the
    gap exceeds a band. Building a second diagnostic beside it would be the duplication
    D-42 exists to prevent.

### The D-42 diagnostic is built and sized — and it found something bigger than M14

25. **Built before the decision was ruled, on purpose**, because its output is the evidence
    the ruling needs. `src/vcc_valuations/dcf/terminal_return.py` computes the terminal
    return on NEW capital from the growth identity `g = return x reinvestment_rate` on
    production engine output, against both benchmarks at once: the cost of capital (D-42)
    and the return the final explicit year earns (M14). Regenerated by
    `scripts/size_terminal_returns.py`, committed as
    `design/methodology/terminal_return_sets.yaml`, asserted by
    `tests/dcf/test_terminal_return_sets.py` — the standing-rule-4 pattern. Nothing moved.
26. **Both constructions were lifted, not invented.** They already existed in
    `tests/dcf/harness/replica.py` and were used by `size_horizon_variants.py`. They were
    moved onto the engine path because a published number cannot come from a harness that
    merely reproduces the engine (D-51). The replica's docstring is still the best
    explanation of the two readings.
27. **Finding 1, and the largest: CSL's terminal asserts a 61–73% return on new capital**
    against a discount rate of 8.75%. `terminal_capex_pct_revenue: 0.06` equals
    `da_pct_revenue: 0.06` exactly, so net terminal capex is **zero** and the only
    reinvestment left is working capital at g × 0.35, about 1.05% of revenue — a perpetuity
    growing at 3% while reinvesting 4% of earnings. **This is D-53 unimplemented, now with
    a number on it.** Opened as M15. Implementing D-53 should drop it into the range DNL
    occupies, and the sizing gives that implementation a target to land in.
28. **Finding 2: M14 confirmed and isolated.** WBC Stagflation is +401bp above earned; every
    other WBC scenario is conservative or flat. So it is one scenario's recovery assumption,
    not a systemic bias — which is what makes it answerable.
29. **Finding 3: DNL splits three-and-three on the cost of capital**, 4.85% to 12.13% against
    a WACC of 8.88%. That is the diagnostic discriminating rather than firing on everything,
    and is the best argument for ratifying D-42.
30. **What the diagnostic does NOT yet report:** the return on the WHOLE capital base
    (terminal NOPAT over invested capital rolled forward). `FcfEngine` carries no
    invested-capital roll-forward, so it cannot be struck from engine output today. It is
    the better of the two readings where a declared opening base exists, and D-44 already
    defines one for DNL. Wiring it is the natural next step and is named in the set's own
    `basis` field so nobody reads the reported figure as the other one.

### D-42 is RULED and enforced, and D-58 is closed by the same field

31. **The defended exception is structural now, not prose.** `excess_return_defence` on the
    impact-matrix driver carries `moat_sources`, a `decay_horizon` (year band or
    `indefinite`, with a basis), a `named_threat` and a `sensitivity`. The engines surface
    the diagnostic on every valuation and warn; nothing adjusts (D-07). The obligation is a
    ratchet in `tests/dcf/test_terminal_defence.py`: declare a defence or be named in
    `tests/terminal_defence_baseline.json`, and the baseline may only shrink.
32. **The sizing is why the prose form could not survive.** Fifteen of eighteen valuations
    assert a terminal return above their cost of capital and exactly **one** carried a
    defence. Two DNL scenarios — including **Muddle Through, the headline valuation, at
    226bp of excess** — carry no `terminal_roic` driver at all. The WBC matrix carries none
    for any scenario though all six exceed Ke. CSL has no matrix file and its apparent
    excess is a D-53 artefact, so its six are baselined with the explicit instruction **not
    to write a defence for a defect**.
33. **Orderly Convergence is the worked example, and declaring it dropped a leg.** The prose
    defended the excess return on scale + switching_cost + resource. Under D-43a the
    resource leg is a **rent** — gas contracts, dated in the margin path under D-40 — and a
    rent that expires inside the explicit period cannot hold up a ten-to-fifteen year
    horizon. The structured block names scale and switching cost only. A ratchet test
    enforces that tie, which no schema can see: the moat lives on the company file and the
    defence on the archetype matrix.
34. **D-58 is closed by the same field.** `DecayHorizon` is the structured home the horizon
    never had. It rejects a block declaring neither a band nor indefinite, or both, and
    enforces D-58's own rule: an indefinite horizon requires `finite_horizon_sensitivity`
    beside it. All four probes were run — removing a baseline entry, baselining something
    that asserts nothing, defending on a rent, and an indefinite horizon with no
    sensitivity — and each fails as it should.
35. **Nothing moved.** No level, no tie.

### D-42 step 2 — the declared return now reconciles, and it does not

40. **D-49's roll-forward already had the answer and threw it away.** It rolled invested
    capital through the explicit period to strike the capex rate, then discarded the base.
    It now returns it whole, so the return on the **whole capital base** can be reported
    rather than only the return on new capital. That is the reading D-45 asks the moat work
    to declare, and **D-42's obligation is now judged on it**.
41. **Which reading governs is not cosmetic.** DNL Fragmentation sits **below** its WACC on
    new capital (8.73%) and **above** it on the whole base (8.92%). So it owes a defence
    under the better reading and did not under the weaker one. Pinned in a test.
42. **A defence now states the rate it defends.** `declared_terminal_return`, with a
    required basis — a rate without a stated derivation is the D-50 defect on the largest
    number in the valuation.
43. **And it does not reconcile. This is the finding.** DNL Orderly Convergence declares
    **9.13%** and the capital build produces **12.46%** — a gap of **333bp**. The declared
    figure is not invented: the matrix declares terminal_roic positive/small, and the
    project's own translation table maps positive-small on a rate driver to +25bp over the
    convergence target its rationale names. So the moat work's view is +25bp and the model
    delivers +358bp.
44. **That is M16, and it is a conflict between two ratified decisions.** D-45 and D-49 both
    nominate reinvestment as the derived quantity — D-45 from the declared return, D-49 from
    the balance sheet — and they agree only when the declared rate equals terminal earnings
    over the rolled-forward base. Nothing compared them because **`terminal_roic` was a
    driver with its own delta convention that no engine ever read**. The moat work's view was
    recorded in the matrix and discarded.
45. **Item 8 is done, and honestly.** Muddle Through and AI Lag now carry `terminal_roic`
    drivers with full defence blocks — barrier-bearing moat sources, the Five Forces horizon,
    the named threat, the sensitivity. Their direction and magnitude **record what the model
    already does** (read through the project's own translation table) and say so, with
    confidence `low`; `declared_terminal_return` is deliberately **absent**, because copying
    the engine's own answer back at it would make the reconciliation vacuous. Supplying those
    rates is Stephen's.
46. **Worth noticing on the scale:** every DNL scenario that asserts an excess return is
    asserting a **large** one by the project's own translation table (+254 to +358bp against
    a +200bp "large" band) — and the only scenario anyone ever assessed called it **small**.
47. **Nothing moved.** All of this is disclosure and declaration; no cash flow reads the
    capital base or the declared rate.

### What needs Stephen next

36. **M16 — which governs the terminal return?** The rate the moat work declares (D-45), or
    the capital base the explicit period leaves behind (D-49)? One of the two decisions needs
    amending either way, and on the central case it stands behind roughly 70% of DNL's EV.
    This is now the most consequential open question in the project.
37. **Should D-42 carry a materiality floor?** Fragmentation triggers the obligation on a
    **4bp** excess — the convergence target reached to within rounding, not a claim about a
    moat. Baselined on that ground rather than softened by a session.
38. **The two DNL declared rates** — Muddle Through and AI Lag — once M16 settles which
    direction the declaration runs in.
39. **M15 / D-53 for CSL.** Fourteen of the fifteen undeclared excess returns are baselined,
    and six of those disappear by arithmetic once D-53 lands rather than by anyone
    justifying them. Moves all six CSL levels; D-55 moves the same six, so they go together.
    This is now the largest thing outstanding.
37. **Where does a BANK's terminal-return defence live?** The §15 fork declares terminal ROE
    on the scenario overlay, not as an impact-matrix driver, so all six WBC scenarios are
    baselined for want of a home rather than for want of a reason. Structural question.
38. **M14:** is Stagflation's terminal ROE 4pp above its final earned year intended as a
    recovery, and what is its basis? The `decay_horizon.basis` field is where the answer
    goes once 37 is settled.
39. **Two DNL defences to write** — Muddle Through and AI Lag — with Orderly Convergence as
    the template. Muddle Through is the headline number, so it is the one that matters.

---

## HANDOVER — session of 14 September 2026, third sitting (superseded by the block above)

**State:** suite **364**, ratchet **13 checks**, base ties green and UNMOVED —
DNL 1.989, WBC 30.03, CSL 195.78. No level moved. One defect closed, no numeric work.

### The gate was red on Stephen's machine and green in the container

1. **`session_start.cmd` reported 353 passed and 11 errors** while the same commit ran
   364 passed in the cloud container. Same 364 collected both places, so the eleven were
   Windows-only.
2. **All eleven were one fixture.** `tests/test_engine_workbook.py` has exactly eleven
   tests and every one requests the module-scoped `books` fixture, which builds all three
   workbooks. The fixture died, so the whole module errored. 353 + 11 = 364.
3. **The cause was the read half of the cp1252 class.** `engine_workbook.py` read
   `cfgs_gen.json` back with a bare `open()` at three sites. That file is UTF-8 and carries
   curly quotes, `→`, `Δ`, `β`, `≈`, `−` and en/em dashes; under cp1252 the read raises
   `UnicodeDecodeError` at byte 14439, on a closing curly quote.
4. **The guard added the sitting before could not catch it, and that is the finding.** It
   checked `open(..., 'w')` only, and only a bare `open` — not read mode, not
   `Path.read_text` / `write_text`. Writes were the direction that happened to bite first;
   reads are the more common direction and were unguarded. Half a class is not a ratchet.
5. **Both are now closed.** Five sites name `encoding="utf-8"` — three in
   `engine_workbook.py`, one in `gen_ui.py` (which reads the same config, so the UI build
   would have died on Stephen's machine too) and one in `scripts/estimate_emrp.py`. The
   guard is now `test_text_file_access_names_its_encoding` and covers text-mode `open`,
   `read_text` and `write_text` in both directions, exempting binary modes and treating a
   mode it cannot resolve to a constant as text.
6. **Verified by simulation, both directions.** Patching `io.open` to substitute cp1252
   wherever no encoding is named reproduces the failure exactly on the pre-fix tree — all
   three builders, identical error, byte 14439 — and all three build cleanly on the fixed
   tree. The guard was probed with five regression shapes (`open(p)`, `open(p, 'r')`,
   `read_text()`, `write_text(s)`, `io.open(p, mode=m)`), each failing it, and five
   legitimate shapes (`'rb'`, `'wb'`, `read_bytes()`, and both explicit-encoding forms),
   each passing.
7. **The previous block said suite 338; it was 364.** The bridge note had it right and the
   live layer did not, which is the wrong way round. If this number looks stale again,
   `session_start.cmd` prints the true one.

---

## HANDOVER — session of 14 September 2026, second sitting (superseded by the block above)

**State:** suite **338** (as recorded at the time; the true count was 364 — see above),
ratchet **13 checks**, base ties green and UNMOVED —
DNL 1.989, WBC 30.03, CSL 195.78. No level moved this sitting. Seven rulings were made,
two stale open items closed, one defect on main fixed, and two gate weaknesses closed.

### The defect that mattered most

1. **`build_cfgs.py` had not parsed since the previous sitting.** A `# ssot-allow: display`
   marker was inserted mid-line, commenting out the rest of the line including a closing
   bracket. Every other use of that marker in the repo sits at the end of its line; the
   lint is line-based, so that is where it belongs.
2. **Nothing caught it, and that is the real finding.** The suite imports the engine, not
   the generators, so a generator can be broken on main with the whole suite green. The
   base-tie check reads `cfgs_gen.json`, which is gitignored and which nothing regenerated,
   so it compared the ratified levels against a config built weeks earlier and reported two
   failures that had nothing to do with the engine.
3. **Both holes are now closed.** `session_start.py` runs `build_cfgs.py` before reading the
   config, so the tie is struck on current code or not struck at all. A new test parses
   every script under `scripts/` and `ui_prototypes/`.

### Rulings

4. **D-52** — item 11 is ruled as position 3: capital intensity follows the business.
   **The engine still runs position 1.** Implementation and re-pinned goldens are the
   next numeric change, and the largest one outstanding.
5. **D-53** — D-49 is a house rule, not a Denali ruling. CSL still declares terminal capex
   equal to D&A and is wrong in the same way Denali was. Not yet implemented.
6. **D-54** — the Disorderly Climate carbon arc is capital that earns a return, inside the
   growing base, assumed to earn exactly the cost of capital and therefore value-neutral by
   construction. No revenue uplift is booked for it. Not yet implemented.
7. **D-55** — capital-structure weights are spot market values for every company. Narrows
   D-04 and closes a divergence nobody had noticed: the register said target ratio and
   Denali has always used spot. Stephen's reasoning is that the gearing decision is less
   load-bearing than it looks, because a higher debt weight raises the levered beta and the
   two effects substantially offset. CSL comes off the target-and-multiple construction;
   its distorted reference price stays under D-19. Not yet implemented — this moves CSL.
8. **D-56** — a scenario declares its company-level channels and the resulting ordering is
   read rather than asserted. Occasioned by AI Lag rising above Muddle Through under D-49
   with no stated channel behind either the margin overlay or the growth setting.
9. **D-57** — Denali's working-capital intensity stays as ratified under D-31. See below.
10. **D-43 and D-43a** — RULED, and implemented the same day. A contract dates the RENT,
    not the barrier. The original clause that a contractual expiry sets the horizon directly
    does not stand. `Moat.source_roles` is in the schema with a validator that roles cover
    every source; Denali declares scale, switching-cost and regulatory as barriers and the
    resource leg — the gas contracts — as a rent, already dated in the margin path under
    D-40. The standing contradiction between a ten-to-fifteen year horizon and an FY2032
    expiry is closed in the data, not just on paper, and no number moved. WBC's four moat
    blocks and CSL's three are baselined in `tests/moat_role_baseline.json`: the list may
    only shrink, and a new block cannot be added without roles.
11. **D-38 and D-39 retired** rather than ratified, superseded by D-48 and D-49. The
    PROPOSED list is now D-35, D-36, D-37 and D-42.

### Two open items closed, both stale, and a lesson about the register

12. **Item 7** described terminal capex running below D&A — precisely what D-49 replaced the
    day before. It stayed open only because the register was not updated when D-49 landed.
13. **M1** described zero working capital in every explicit year. The engine has invested
    working capital across the stub and all five years since the working-capital standard
    landed: on Muddle Through, about 163m cumulative. The zero belongs to
    `tests/dcf/golden/dnl_mt_inputs.py`, a legacy hand-typed oracle reproducing the audited
    v6 workbook. **That fixture was misread as the live configuration in session before the
    assembler was checked** — the same error the item itself records, repeated by the
    session closing it. If a Denali number looks wrong, check
    `build_engine_inputs_from_data`, not the golden fixtures.
14. Two stale NEEDS items in one list says the register drifts when a ruling lands. Close
    items in the same change as the decision that closes them.

### The working-capital work, and why it did not land

15. The instruction was to strike the intensity over the D-48 window. **That is not
    available.** A statement of financial position is not restated for discontinued
    operations, so the FY2024 comparative is the pre-demerger group — pairing it with
    continuing-operations revenue is the entity mismatch D-50 exists to stop. D-48's window
    works for capex and depreciation only because those come from the segment note, which
    IS restated. Working capital has no segment equivalent.
16. What exists instead is a nine-period trade-working-capital series the company publishes
    itself, two periods cleanly post-demerger, now transcribed with provenance in
    `analyses/dnl_trade_working_capital_history.yaml`, with a derivation in
    `src/vcc_valuations/assumptions/trade_working_capital.py` and pinned tests. The
    denominator question resolved from the accounts: the 1H26 income statement labels its
    columns Group = Explosives + Discontinued, and the apparent second-half skew is the
    northern winter, which is an argument FOR averaging the two balance sheets.
16b. **D-58** — an indefinite moat horizon is admissible for any barrier provided the
    finite-horizon sensitivity is declared beside it. RULED but NOT ENFORCEABLE: the
    decay horizon is prose inside `terminal_roic.rationale` in the impact matrix, not a
    structured field, so there is nothing for a validator to read. Structuring it is the
    implementation step for D-58 and for the unratified half of D-43.
17. **It is derived and deliberately NOT consumed** (D-57). Once M1 turned out to be stale,
    what remained was a definitional change to a measure that already works, on two
    observations. The file is evidence held for the FY26 result. The ratified FY2025
    denominator was checked while doing this and is sound — continuing operations, confirmed
    against the segment note; it simply had no basis recorded, which is what made it look
    doubtful.

### Next, in the order the interactions demand

18. Each of these moves a base tie, so they land one at a time with goldens re-pinned once
    per step: item 11 position 3 into the engine (D-52, all six DNL levels); the carbon arc
    inside the base (D-54, Disorderly only); D-49 extended to CSL (D-53, all six CSL);
    spot weights for CSL (D-55, all six CSL — take with D-53 since both move the same
    levels); the WBC dividend rule as the lesser of the current payout and the
    capital-constrained one, which Stephen asked for and which needs "% of capital" defining
    as the payout holding CET1 flat given asset growth and RWA density.
19. **CSL is missing both period mechanisms.** Period A, the net-debt walk from anchor date
    to valuation date, is what fixes the six-month date mismatch (open item 1) and Stephen
    has asked for it. Period B, the fractional stub year, `segment_engine.py` does not have
    at all — that is a bigger job and separate.
20. Then the UI: terminal-share disclosure (Stephen's scope — disclose it, do not rebuild
    the §11.4.2 rule), then the panel-to-translator wiring, then the capital-intensity
    override behind it.
21. Then D-42 the diagnostic, which D-56 now depends on, and D-35/D-36 which still live
    only in the replica.

---

## HANDOVER — session of 14 September 2026, first sitting (superseded by the block above)

**Start with `land_vcc.cmd`.** Then `session_start.cmd`, then this block.

**State:** suite **302** (+2 opt-in `-m libreoffice`, both passing), ratchet **13 checks**,
base ties green. **DNL has moved: 2.831 → 1.989.** CSL 195.78 and WBC 30.03 unchanged.

### What landed

1. **The operating base is restated and DERIVED, not stored.** `data/financials/dnl.yaml`
   carries the raw FY2024–FY2025 segment observations — revenue, EBITDA, D&A, capex for the
   explosives segments, ex individually material items. The translator derives capital
   intensity 9.18%, depreciation intensity 8.24%, EBITDA margin 20.96% and EBIT margin 12.72%
   from them. Nothing is stored beside its own inputs (D-16); the company file declares a
   window, not a number.
2. **The transition-cost normalisation is a separate declared line**, +0.35pp, sized only on
   the corporate-cost reduction the company has actually reported ("Corporate costs reduced by
   $6m", 1H26, annualised). It is deliberately NOT the full gap between the two-year average
   and the 1H26 run-rate — that gap also contains joint-venture and other income whose
   persistence is not established. Revisit at the FY26 result.
3. **D-49 is in the engine.** `capex_rule: grows_capital_base_at_g`. Opening invested capital
   is derived per D-44 from net PP&E, intangibles and the ratified working-capital intensity,
   rolled forward on the same flows the valuation uses; terminal capex is D&A plus g times the
   fixed base — 9.7% to 10.2% of revenue by scenario, against D&A of 8.24%.
4. **The workbook carries the roll-forward as formulas.** The generated workbook has an
   invested-capital section and strikes terminal capex per scenario from it, so LibreOffice
   recalculates D-49 independently of the Python. It ties across all six scenarios.
5. **The UI discloses the lot.** The assumptions panel now carries capital intensity,
   depreciation intensity, the margin and its normalisation, and the terminal capex rule, each
   with entity, window, level and source.

### Levels

| Scenario | Was (25 Aug) | Now |
|---|---|---|
| Orderly Convergence | 3.2740 | 2.3316 |
| **Muddle Through** | **2.8307** | **1.9895** |
| AI Productivity Lag | 2.7705 | 2.0127 |
| Fragmentation | 1.9926 | 1.2241 |
| Disorderly Climate | 1.7015 | 0.9924 |
| Stagflation Persists | 0.8061 | 0.0491 |

### Three things that need Stephen

6. **AI Productivity Lag now sits ABOVE Muddle Through** — 2.0127 against 1.9895. This is a
   consequence of D-49, not a data error: AI Lag carries +0.5pp of margin and a lower terminal
   growth rate, and once terminal capex is D&A plus g times the fixed base, a lower g also
   means a lower perpetual reinvestment call. The offset is now big enough to outweigh the
   slower growth. The ordering assertion in `test_dnl_all_scenarios.py` has been updated to
   match, with the reasoning written down. **Whether the scenario narrative still supports AI
   Lag above the central case is a judgement, not an arithmetic question.**
7. **Not every valuation breaches the 70% terminal threshold any more.** AI Lag is at 69.3%
   and Stagflation at 61.9%. The blanket test is replaced by one that pins each share, so a
   movement across the line is read rather than absorbed. The §11.4.2 obligation now applies
   case by case.
8. **The user override on capital intensity is not built.** The disclosure is. The override
   needs the UI panel wired to the translator first — the sliders drive a reduced-form JS
   approximation, and putting an engine input behind one of them would make the UI a second
   model of record, which D-23 forbids. That is the next UI job, not a five-minute one.

### Next

9. Wire the UI panel to the translator, then add the capital-intensity override behind it.
10. **The Porter work and the margin build still disagree about the gas contracts.** The
    impact matrix declares the moat as "scale + switching_cost + resource (long-term
    contracts)" with a 10–15 year decay horizon; those contracts expire by FY2032, six years
    from the valuation date, and D-43 says a contractual expiry sets the horizon directly.
11. **Item 11 is narrowed again but still open** — see `analyses/dnl_item11_four_positions.md`
    and `analyses/dnl_item11_capital_intensity.xlsx`.
12. Then D-42 the diagnostic, and the horizon rule and fade (D-35, D-36), which are still
    PROPOSED and still only live in the replica.

### Ruled 14 September

13. **D-48** the intensity pair from one window and one entity — implemented.
    **D-49** the terminal capital base grows at g — implemented.
    **D-50** every rate declares its basis, ratchet check 13 — six rates still baselined.
    **D-51** the workbook is a presentation layer, never a source.
14. Why D-50 exists: four defects across three sittings were one error — a ratio assembled
    from parts that did not share an entity, a window or a level of the accounts.

---

## HANDOVER — session of 26 August 2026 (superseded, kept for context)

**Start with `land_vcc.cmd`.** Then `session_start.cmd`, then this block.

**State:** suite **297** (+2 opt-in `-m libreoffice`), ratchet **12**, bases unchanged
**2.831 / 30.03 / 195.78**. No engine change, no production change, nothing in `data/`
moved. One new script, one new declaration file, one new test module.

### The reconciliation is done, and the residual was not what anyone thought

1. **The whole difference between the two 25 August tables is the explicit capex path.**
   §13's ruled table holds the live path, which converges to 7.0%; the second sitting
   applies D-38 and converges to 7.3% by Y5. Nothing else moves between them. It is not
   the terminal-boundary conventions — those are real, they are pinned as tests, and they
   are not what separated the tables.
2. **All three published tables now regenerate from committed code**, to 0.01% on §10 and
   to 0.22% on §13. `design/methodology/horizon_variant_sets.yaml` carries each table's
   complete assumption block and the levels it produced; `scripts/size_horizon_variants.py`
   generates them; `tests/dcf/test_horizon_variant_sets.py` asserts them. Exactly one set
   is `current` and the others name what superseded them.
3. **Disorderly Climate is reconciled and it is a methodology question, not a residual.**
   §13's 1.4378 came from growing the capital base *excluding* the carbon arc and adding
   the persistent +1.0pp on top — terminal capex 9.22%. The second sitting grew the base
   *including* the arc, no premium — 8.56%. Reproduced to 0.03% and 0.00% respectively.
   §9's own reasoning, that a licence-to-operate cost is permanent by construction,
   argues for the first reading. **Unruled; put with item 11.**
4. **The reconstruction the last handover could not close is closed.** The published
   §13 Disorderly figures of 1.4378 and 1.6375 are the same construction with and without
   the +1.0pp premium; the harness gives 1.4383 and 1.6380.

### Open, needing Stephen

5. **Item 11 is still the blocker, and it is now fully sized** — see §13b of the paper.
   On the central case: ruled build 2.6956, hold intensity flat 1.7676, volume plus asset
   inflation 1.8387. The two positions that make capital follow the business land within
   4% of each other; the ruled build is a third of the company above both. The evidence
   question underneath it is **answered** — B25 volume 3.28% against B29 pricing 2.85% on
   Muddle Through, so growth is over half volume and replacement assets inflate too.
6. **The handover's 1.9551 for the volume-plus-inflation position does not reproduce.**
   That run held the chain rate flat for all ten years; struck that way the harness gives
   1.6175, not 1.9551. Struck as a fading path it gives 1.8387. Both are now declared
   positions with pinned levels. Neither changes the conclusion.
7. **Disorderly's terminal carbon treatment** (3 above) needs a ruling alongside item 11.

### Housekeeping

8. **New standing rule 4 in `CLAUDE.md`: any number that reaches a document must come
   from committed code**, and the harness that produced it ships in the same change as
   the document citing it. This is the rule whose absence cost two sittings.
9. **Everything queued behind item 11 is unchanged**: D-42 the diagnostic, the horizon and
   fade, the UI disclosure piece, then re-pin all eighteen goldens once with the workbook
   re-tie. Do not ratify the twelve goldens from 23 August.

---

## HANDOVER — session of 25 August 2026, second sitting (superseded, kept for context)

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
